#!/usr/bin/env python3
"""mdBook preprocessor: inject a story metadata card after the title of story chapters.

Reads ``stories.csv`` and, for each chapter whose path matches a ``StoryKey``,
builds a single HTML card showing authors, artists, publication date, source link,
and word count / estimated reading time.  Fields are omitted when empty.
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

from pipe_csv_io import read_pipe_csv  # noqa: E402

MARK_START = "<!-- fablore-story-meta:start -->"
MARK_END = "<!-- fablore-story-meta:end -->"

_WORDS_PER_MINUTE = 250
_MIN_WORDS_FOR_READTIME = 50
_NO_WORDCOUNT_TYPES = {"world-of-rathe", "heroes-of-rathe"}

# Inline SVG for BlueSky (Font Awesome 4 has no BlueSky icon)
_BLUESKY_SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 568 501" '
    'height="0.85em" width="0.85em" style="vertical-align:-0.1em;fill:currentColor" '
    'aria-hidden="true">'
    '<path d="M123.121 33.664C188.241 82.553 258.281 181.68 284 234.873'
    'c25.719-53.192 95.759-152.32 160.879-201.209C491.866-1.611 568-28.906 568 57.947'
    'c0 17.346-9.945 145.713-15.778 166.555-20.275 72.453-94.155 90.933-159.875 79.748'
    'C508.222 323.8 521.99 372.7 484.34 421.616c-60.732 79.094-165.296 62.47-235.296-14.534'
    'C179.044 484.086 74.48 500.71 13.748 421.616-23.902 372.7-10.134 323.8 106.532 304.25'
    '40.812 315.435-33.068 296.955-53.343 224.502-59.176 203.66-69.121 75.293-69.121 57.947'
    'c0-86.853 76.134-59.558 192.242-24.283z"/>'
    '</svg>'
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
    _fa_facebook = '<i class="fa fa-facebook" aria-hidden="true"></i>'
    _x_logo = '<span class="story-share-x-logo" aria-hidden="true">X</span>'
    _fa_whatsapp = '<i class="fa fa-whatsapp" aria-hidden="true"></i>'
    _fa_link = '<i class="fa fa-link" aria-hidden="true"></i>'
    _copy_btn = (
        '  <button class="story-share-btn story-share-copy"'
        f' type="button" aria-label="Copy link" title="Copy link">{_fa_link}</button>'
    )
    _type_attr = f' data-story-type="{html.escape(story_type)}"' if story_type else ""
    html_block = "\n".join([
        f'<div class="story-share"{_type_attr}>',
        '  <span class="story-share-label">Share</span>',
        _share_link("story-share-facebook", "Share on Facebook", _fa_facebook),
        _share_link("story-share-twitter", "Share on X", _x_logo),
        _share_link("story-share-bluesky", "Share on BlueSky", _BLUESKY_SVG),
        _share_link("story-share-whatsapp", "Share on WhatsApp", _fa_whatsapp),
        _copy_btn,
        '</div>',
    ])
    return html_block + "\n" + f"""<script>
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


def _item(icon: str, inner: str) -> str:
    return (
        f'<span class="story-meta-item">'
        f'<i class="fa {icon}" aria-hidden="true"></i>'
        f" {inner}</span>"
    )


def _build_meta_html(
    *,
    authors: str,
    artists: str,
    publication_date: str,
    source_link: str,
    word_count: int,
    show_word_count: bool = True,
    story_type: str = "",
) -> str:
    """Return the ``story-meta`` div HTML, or an empty string when nothing to show."""
    items: list[str] = []

    if authors:
        items.append(_item("fa-pencil", f"Written by <strong>{html.escape(authors)}</strong>"))

    if artists:
        items.append(_item("fa-image", f"Art by <strong>{html.escape(artists)}</strong>"))

    formatted_date = _format_date(publication_date)
    if formatted_date:
        items.append(_item("fa-calendar", html.escape(formatted_date)))

    if source_link:
        link_esc = html.escape(source_link)
        items.append(
            _item(
                "fa-external-link",
                f'<a href="{link_esc}" target="_blank" rel="noopener">Original article</a>',
            )
        )

    if show_word_count and word_count > 0:
        count_fmt = f"{word_count:,}"
        if word_count >= _MIN_WORDS_FOR_READTIME:
            minutes = max(1, round(word_count / _WORDS_PER_MINUTE))
            time_label = f"{minutes} min read"
            wc_text = f"{count_fmt} words · {time_label}"
        else:
            wc_text = f"{count_fmt} words"
        items.append(_item("fa-clock-o", wc_text))

    parts: list[str] = []
    if items:
        inner = "\n  ".join(items)
        parts.append(f'<div class="story-meta" aria-label="Story information">\n  {inner}\n</div>')
    parts.append(_build_share_html(story_type))
    return "\n".join(parts)


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
    return {
        Path(r["StoryKey"]).as_posix(): r
        for r in rows
        if (r.get("StoryKey") or "").strip()
    }


def _process_chapter(content: str, row: dict[str, str]) -> str:
    """Inject the story-meta block for one chapter."""
    # Strip any existing block before counting so injected HTML is excluded
    if MARK_START in content and MARK_END in content:
        pre, _, rest = content.partition(MARK_START)
        _, _, post = rest.partition(MARK_END)
        bare_for_count = pre + post
    else:
        bare_for_count = content
    story_type = (row.get("StoryType") or "").strip()
    word_count = _count_words(bare_for_count)
    inner = _build_meta_html(
        authors=(row.get("Authors") or "").strip(),
        artists=(row.get("Artists") or "").strip(),
        publication_date=(row.get("PublicationDate") or "").strip(),
        source_link=(row.get("SourceLink") or "").strip(),
        word_count=word_count,
        show_word_count=story_type not in _NO_WORDCOUNT_TYPES,
        story_type=story_type,
    )
    return _inject_after_heading(content, inner)


def _walk_sections(
    sections: list,
    meta_by_key: dict[str, dict[str, str]],
) -> None:
    for item in sections:
        if not isinstance(item, dict):
            continue
        if "Chapter" in item:
            ch = item["Chapter"]
            path = (ch.get("path") or "").strip()
            if path:
                row = meta_by_key.get(Path(path).as_posix())
                if row is not None:
                    ch["content"] = _process_chapter(ch.get("content") or "", row)
            _walk_sections(ch.get("sub_items") or [], meta_by_key)


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
    _walk_sections(book.get("items") or [], meta_by_key)

    json.dump(book, sys.stdout, ensure_ascii=False)


if __name__ == "__main__":
    main()
