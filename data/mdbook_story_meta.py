#!/usr/bin/env python3
"""mdBook preprocessor: inject a story card after the title of story chapters.

Reads ``stories.csv`` and, for each chapter whose path matches a ``StoryKey``,
builds one HTML card in three rows, each omitted when it has nothing to show:

* context — for main-story and short-stories chapters, the arc the story
  belongs to, its place in that arc ("Part 3 of 11") and the heroes it
  features, most-mentioned first;
* byline — authors, artists, publication date, and word count / reading time;
* links — the original article, plus a slot that ``mdbook_graph_link`` fills
  with the Lore Graph link (it runs after this preprocessor).

A hero or set information block that ``mdbook_hero_meta`` / ``mdbook_set_meta``
already placed under the title moves into the card, between the context row
and the byline, so the page has one card rather than two stacked blocks.

The card is inserted after the first H1 heading in the chapter content.

mdBook passes ``(PreprocessorContext, Book)`` as JSON on stdin; this process must
print only the modified ``Book`` JSON on stdout.  Supports ``supports <renderer>``.
"""

from __future__ import annotations

import html
import json
import re
import sys
from datetime import datetime
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from mdbook_breadcrumb import _arc_display_name, _load_arcs, _load_sets, _relative_href  # noqa: E402
from mdbook_related import resolve_hero_src_path  # noqa: E402
from pipe_csv_io import read_pipe_csv  # noqa: E402

MARK_START = "<!-- fablore-story-meta:start -->"
MARK_END = "<!-- fablore-story-meta:end -->"
# mdbook_graph_link puts its link here, so it sits in the card's links row.
GRAPH_SLOT = "<!-- fablore-graph-link:slot -->"

# The hero / set information block those preprocessors put directly under the
# title (``book.toml`` runs them first). The set block keeps its own markers.
_REFERENCE_META_RE = re.compile(
    r"\s*(?:<!-- fablore-set-meta:start -->\s*)?"
    r'(<div class="story-meta" aria-label="(?:Hero|Set) information">.*?</div>)'
    r"(?:\s*<!-- fablore-set-meta:end -->)?\s*",
    re.DOTALL,
)

# Sections whose chapters live in arc folders (``<section>/<arc>/<story>.md``).
_ARC_SECTIONS = ("main-story", "short-stories")
_ARC_HUB_FILES = {"index.md", "README.md"}
# Beyond this many heroes the context row names the most-mentioned and counts the rest.
_MAX_CARD_HEROES = 3

_WORDS_PER_MINUTE = 250
_MIN_WORDS_FOR_READTIME = 50
_NO_WORDCOUNT_TYPES = {"world-of-rathe", "heroes-of-rathe"}

# Inline SVG for BlueSky (Font Awesome 4 has no BlueSky icon)
_BLUESKY_SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 568 501" '
    'height="0.85em" width="0.85em" style="vertical-align:-0.1em;fill:currentColor" '
    'aria-hidden="true">'
    '<path d="M123.121 33.664C188.241 82.553 258.281 181.68 284 234.873'
    "c25.719-53.192 95.759-152.32 160.879-201.209C491.866-1.611 568-28.906 568 57.947"
    "c0 17.346-9.945 145.713-15.778 166.555-20.275 72.453-94.155 90.933-159.875 79.748"
    "C508.222 323.8 521.99 372.7 484.34 421.616c-60.732 79.094-165.296 62.47-235.296-14.534"
    "C179.044 484.086 74.48 500.71 13.748 421.616-23.902 372.7-10.134 323.8 106.532 304.25"
    "40.812 315.435-33.068 296.955-53.343 224.502-59.176 203.66-69.121 75.293-69.121 57.947"
    'c0-86.853 76.134-59.558 192.242-24.283z"/>'
    "</svg>"
)


def _count_words(markdown: str) -> int:
    """Count prose words in markdown, stripping markup and syntax."""
    text = re.sub(r"```[\s\S]*?```", "", markdown)
    text = re.sub(r"`[^`]*`", "", text)
    text = re.sub(r"<!--[\s\S]*?-->", "", text)
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", text)
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"\[([^\]]*)\]\[[^\]]*\]", r"\1", text)
    text = re.sub(r"^#{1,6}\s+", "", text, flags=re.MULTILINE)
    text = re.sub(r"\*{1,3}|_{1,3}", "", text)
    return len(text.split())


def _format_date(date_str: str) -> str:
    """Format ``YYYY-MM-DD`` as ``D Month YYYY``.  Returns the raw string on failure."""
    s = date_str.strip()
    if not s:
        return ""
    try:
        dt = datetime.strptime(s, "%Y-%m-%d")
        return f"{dt.day} {dt.strftime('%B %Y')}"
    except ValueError:
        pass
    # Handle swapped month/day (e.g. ``2019-29-08``)
    parts = s.split("-")
    if len(parts) == 3:
        try:
            dt = datetime(int(parts[0]), int(parts[2]), int(parts[1]))
            return f"{dt.day} {dt.strftime('%B %Y')}"
        except (ValueError, IndexError):
            pass
    return s


def _share_link(cls: str, label: str, icon: str) -> str:
    return (
        f'  <a class="story-share-btn {cls}" href="#"'
        f' target="_blank" rel="noopener noreferrer"'
        f' aria-label="{label}" title="{label}">{icon}</a>'
    )


def _build_share_html(story_type: str = "") -> str:
    """Return share buttons HTML with an inline script that populates URLs at runtime."""
    _fa_facebook = '<i class="fab fa-facebook" aria-hidden="true"></i>'
    _x_logo = '<span class="story-share-x-logo" aria-hidden="true">X</span>'
    _fa_whatsapp = '<i class="fab fa-whatsapp" aria-hidden="true"></i>'
    _fa_link = '<i class="fas fa-link" aria-hidden="true"></i>'
    _copy_btn = (
        '  <button class="story-share-btn story-share-copy"'
        f' type="button" aria-label="Copy link" title="Copy link">{_fa_link}</button>'
    )
    _type_attr = f' data-story-type="{html.escape(story_type)}"' if story_type else ""
    html_block = "\n".join(
        [
            f'<div class="story-share"{_type_attr}>',
            '  <span class="story-share-label">Share</span>',
            _share_link("story-share-facebook", "Share on Facebook", _fa_facebook),
            _share_link("story-share-twitter", "Share on X", _x_logo),
            _share_link("story-share-bluesky", "Share on BlueSky", _BLUESKY_SVG),
            _share_link("story-share-whatsapp", "Share on WhatsApp", _fa_whatsapp),
            _copy_btn,
            "</div>",
        ]
    )
    return (
        html_block
        + "\n"
        + f"""<script>
(function () {{
  var u = encodeURIComponent(window.location.href);
  var t = encodeURIComponent(document.title);
  function qs(sel) {{ return document.querySelector(sel); }}
  var fb = qs('.story-share-facebook');
  if (fb) fb.href = 'https://www.facebook.com/sharer/sharer.php?u=' + u;
  var tw = qs('.story-share-twitter');
  if (tw) tw.href = 'https://twitter.com/intent/tweet?url=' + u + '&text=' + t;
  var bsky = qs('.story-share-bluesky');
  if (bsky) bsky.href = 'https://bsky.app/intent/compose?text=' + t + '%20' + u;
  var wa = qs('.story-share-whatsapp');
  if (wa) wa.href = 'https://api.whatsapp.com/send?text=' + t + '%20' + u;
  var cp = qs('.story-share-copy');
  if (cp) cp.addEventListener('click', function () {{
    navigator.clipboard.writeText(window.location.href).then(function () {{
      cp.classList.add('story-share-copied');
      setTimeout(function () {{ cp.classList.remove('story-share-copied'); }}, 2000);
    }});
  }});
}})();
</script>"""
    )


def _item(icon: str, inner: str) -> str:
    return f'<span class="story-meta-item">' f'<i class="{icon}" aria-hidden="true"></i>' f" {inner}</span>"


def _build_meta_html(
    *,
    authors: str,
    artists: str,
    publication_date: str,
    source_link: str,
    word_count: int,
    show_word_count: bool = True,
    story_type: str = "",
    context_html: str = "",
    reference_html: str = "",
) -> str:
    """Return the story card HTML followed by the share sheet."""
    items: list[str] = []

    if authors:
        items.append(_item("fas fa-pencil", f"Written by <strong>{html.escape(authors)}</strong>"))

    if artists:
        items.append(_item("fas fa-image", f"Art by <strong>{html.escape(artists)}</strong>"))

    formatted_date = _format_date(publication_date)
    if formatted_date:
        items.append(_item("fas fa-calendar", html.escape(formatted_date)))

    if show_word_count and word_count > 0:
        count_fmt = f"{word_count:,}"
        if word_count >= _MIN_WORDS_FOR_READTIME:
            minutes = max(1, round(word_count / _WORDS_PER_MINUTE))
            time_label = f"{minutes} min read"
            wc_text = f"{count_fmt} words · {time_label}"
        else:
            wc_text = f"{count_fmt} words"
        items.append(_item("far fa-clock", wc_text))

    links = ""
    if source_link:
        links = (
            f'<a class="story-card-source" href="{html.escape(source_link)}" target="_blank" rel="noopener">'
            '<i class="fas fa-arrow-up-right-from-square" aria-hidden="true"></i> Original article</a>'
        )

    # No blank lines inside the card: Markdown would end the HTML block there.
    parts: list[str] = ['<div class="story-card">']
    if context_html:
        parts.append(f'<p class="story-card-context">{context_html}</p>')
    if reference_html:
        parts.append(reference_html)
    if items:
        inner = "\n  ".join(items)
        parts.append(f'<div class="story-meta" aria-label="Story information">\n  {inner}\n</div>')
    parts.append(f'<p class="story-card-links">{links}{GRAPH_SLOT}</p>')
    parts.append("</div>")
    parts.append("")
    parts.append(_build_share_html(story_type))
    return "\n".join(parts)


def _order_heroes_by_mentions(
    heroes: list[tuple[str, str | None]],
    text: str,
) -> list[tuple[str, str | None]]:
    """Most-mentioned hero first; ties keep the order of first appearance.

    A story registers every hero it names, and the one it is *about* is
    nearly always the one it names most — a better lead than registry order.
    """

    def key(hero: tuple[str, str | None]) -> tuple[int, int]:
        pattern = re.compile(rf"\b{re.escape(hero[0])}\b")
        hits = pattern.findall(text)
        first = pattern.search(text)
        return (-len(hits), first.start() if first else len(text))

    return sorted(heroes, key=key)


def _build_context_html(
    chapter_path: str,
    *,
    arc_name: str,
    position: tuple[int, int] | None,
    heroes: list[tuple[str, str | None]],
) -> str:
    """Return the context row's inner HTML: arc · part · heroes."""
    pieces: list[str] = []
    if arc_name:
        pieces.append(f'<span class="story-card-arc">{html.escape(arc_name)}</span>')
    if position and position[1] > 1:
        pieces.append(f'<span class="story-card-part">Part {position[0]} of {position[1]}</span>')
    if heroes:
        shown, rest = heroes[:_MAX_CARD_HEROES], heroes[_MAX_CARD_HEROES:]
        if len(rest) == 1:  # "+1 more" takes as much room as the name
            shown, rest = heroes, []
        names: list[str] = []
        for name, src in shown:
            esc = html.escape(name)
            names.append(
                f'<a href="{html.escape(_relative_href(chapter_path, src).removesuffix(".md") + ".html")}">{esc}</a>'
                if src
                else esc
            )
        if rest:
            others = html.escape(", ".join(n for n, _ in rest))
            names.append(f'<span class="story-card-more" title="{others}">+{len(rest)} more</span>')
        pieces.append(f'<span class="story-card-heroes">{", ".join(names)}</span>')
    return "".join(pieces)


def _take_reference_meta(content: str) -> tuple[str, str]:
    """Split a hero / set information block off the top of the first H1's body.

    Returns ``(block html, content without it)``; ``("", content)`` when the
    title is not directly followed by such a block.
    """
    match = re.search(r"^#{1,6}[^\n]*\n", content, flags=re.MULTILINE)
    if not match:
        return "", content
    found = _REFERENCE_META_RE.match(content, match.end())
    if not found:
        return "", content
    return found.group(1), content[: match.end()] + "\n" + content[found.end() :]


def _inject_after_heading(content: str, inner_html: str) -> str:
    """Insert or replace the story-meta block after the first H1 in ``content``."""
    if MARK_START in content and MARK_END in content:
        pre, _, rest = content.partition(MARK_START)
        _, _, post = rest.partition(MARK_END)
        bare = pre.rstrip() + ("\n\n" if pre.strip() else "") + post.lstrip()
    else:
        bare = content

    if not inner_html.strip():
        return bare

    block = f"{MARK_START}\n{inner_html}\n{MARK_END}"
    match = re.search(r"^#{1,6}[^\n]*\n", bare, flags=re.MULTILINE)
    if match:
        cut = match.end()
        return bare[:cut] + "\n" + block + "\n\n" + bare[cut:].lstrip("\n")
    return block + "\n\n" + bare


def _load_story_meta(data_dir: Path) -> dict[str, dict[str, str]]:
    """Return a map from ``StoryKey`` (POSIX path) to its ``stories.csv`` row."""
    path = data_dir / "csv" / "stories.csv"
    if not path.is_file():
        return {}
    _fn, rows = read_pipe_csv(path)
    return {Path(r["StoryKey"]).as_posix(): r for r in rows if (r.get("StoryKey") or "").strip()}


def _load_story_heroes(data_dir: Path, src_root: Path) -> dict[str, list[tuple[str, str | None]]]:
    """Return ``StoryId`` → heroes it features, as ``(name, hero page src path or None)``.

    A hero is a character with a ``character-heroes`` row, so the join runs
    story → character → canonical hero.
    """
    csv_dir = data_dir / "csv"
    paths = [csv_dir / f for f in ("story-characters.csv", "character-heroes.csv", "heroes-canonical.csv")]
    if not all(p.is_file() for p in paths):
        return {}
    _, story_chars = read_pipe_csv(paths[0])
    _, char_heroes = read_pipe_csv(paths[1])
    _, canon = read_pipe_csv(paths[2])

    hero_of_char = {r["CharacterId"]: r["CanonicalId"] for r in char_heroes}
    hero_by_id: dict[str, tuple[str, str | None]] = {
        r["CanonicalId"]: (r["CanonicalHero"], resolve_hero_src_path(src_root, r["CanonicalSlug"])) for r in canon
    }
    out: dict[str, list[tuple[str, str | None]]] = {}
    for r in story_chars:
        hero = hero_by_id.get(hero_of_char.get(r["CharacterId"], ""))
        if hero and hero not in out.setdefault(r["StoryId"], []):
            out[r["StoryId"]].append(hero)
    return out


def _arc_of(path: str) -> str | None:
    """Return the arc slug for a story chapter path, or ``None`` for anything else."""
    parts = path.split("/")
    if len(parts) == 3 and parts[0] in _ARC_SECTIONS and parts[2] not in _ARC_HUB_FILES:
        return parts[1]
    return None


def _arc_positions(sections: list) -> dict[str, tuple[int, int]]:
    """Return chapter path → ``(n, total)``: its place among its folder's stories in book order.

    Counted per folder, not per arc slug: ``main-story/outsiders`` and
    ``short-stories/outsiders`` share a slug but are separate runs of stories.
    """
    by_folder: dict[str, list[str]] = {}

    def walk(items: list) -> None:
        for item in items:
            if not isinstance(item, dict) or "Chapter" not in item:
                continue
            ch = item["Chapter"]
            path = Path((ch.get("path") or "").strip()).as_posix()
            arc = _arc_of(path)
            if arc:
                by_folder.setdefault(path.rsplit("/", 1)[0], []).append(path)
            walk(ch.get("sub_items") or [])

    walk(sections)
    return {p: (i, len(paths)) for paths in by_folder.values() for i, p in enumerate(paths, start=1)}


def _process_chapter(
    content: str,
    row: dict[str, str],
    *,
    chapter_path: str = "",
    arc_name: str = "",
    position: tuple[int, int] | None = None,
    heroes: list[tuple[str, str | None]] | None = None,
) -> str:
    """Inject the story card for one chapter."""
    # Strip any existing block before counting so injected HTML is excluded
    if MARK_START in content and MARK_END in content:
        pre, _, rest = content.partition(MARK_START)
        _, _, post = rest.partition(MARK_END)
        bare_for_count = pre + post
    else:
        bare_for_count = content
    reference_html, content = _take_reference_meta(content)
    story_type = (row.get("StoryType") or "").strip()
    word_count = _count_words(bare_for_count)
    context_html = _build_context_html(
        chapter_path,
        arc_name=arc_name,
        position=position,
        heroes=_order_heroes_by_mentions(heroes or [], bare_for_count),
    )
    inner = _build_meta_html(
        authors=(row.get("Authors") or "").strip(),
        artists=(row.get("Artists") or "").strip(),
        publication_date=(row.get("PublicationDate") or "").strip(),
        source_link=(row.get("SourceLink") or "").strip(),
        word_count=word_count,
        show_word_count=story_type not in _NO_WORDCOUNT_TYPES,
        story_type=story_type,
        context_html=context_html,
        reference_html=reference_html,
    )
    return _inject_after_heading(content, inner)


def _walk_sections(
    sections: list,
    meta_by_key: dict[str, dict[str, str]],
    *,
    arc_names: dict[str, str] | None = None,
    positions: dict[str, tuple[int, int]] | None = None,
    heroes_by_story: dict[str, list[tuple[str, str | None]]] | None = None,
) -> None:
    for item in sections:
        if not isinstance(item, dict):
            continue
        if "Chapter" in item:
            ch = item["Chapter"]
            path = Path((ch.get("path") or "").strip()).as_posix()
            row = meta_by_key.get(path) if path != "." else None
            if row is not None:
                arc = _arc_of(path)
                # Only arc chapters get a context row; hero, equipment and other
                # reference pages keep the byline and links alone.
                ch["content"] = _process_chapter(
                    ch.get("content") or "",
                    row,
                    chapter_path=path,
                    arc_name=(arc_names or {}).get(arc, "") if arc else "",
                    position=(positions or {}).get(path) if arc else None,
                    heroes=(heroes_by_story or {}).get(row.get("StoryId", ""), []) if arc else [],
                )
            _walk_sections(
                ch.get("sub_items") or [],
                meta_by_key,
                arc_names=arc_names,
                positions=positions,
                heroes_by_story=heroes_by_story,
            )


def main() -> None:
    """stdin: ``(PreprocessorContext, Book)`` JSON; stdout: ``Book`` JSON only."""
    if len(sys.argv) >= 3 and sys.argv[1] == "supports":
        sys.exit(0)

    ctx, book = json.load(sys.stdin)
    root = Path(ctx["root"])
    book_cfg = (ctx.get("config") or {}).get("book") or {}
    src_rel = (book_cfg.get("src") or "src").strip() or "src"
    src_root = (root / src_rel).resolve()
    data_dir = src_root / "data"

    meta_by_key = _load_story_meta(data_dir)
    items = book.get("items") or []
    positions = _arc_positions(items)
    arcs, sets = _load_arcs(data_dir), _load_sets(data_dir)
    arc_names = {arc: _arc_display_name(arc, arcs, sets) for arc in {p.split("/")[1] for p in positions}}
    _walk_sections(
        items,
        meta_by_key,
        arc_names=arc_names,
        positions=positions,
        heroes_by_story=_load_story_heroes(data_dir, src_root),
    )

    json.dump(book, sys.stdout, ensure_ascii=False)


if __name__ == "__main__":
    main()
