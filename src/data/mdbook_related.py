#!/usr/bin/env python3
"""mdBook preprocessor: append a Related Lore section from story junction CSVs.

Reads ``stories.csv`` and ``story-heroes.csv`` / ``story-locations.csv`` /
``story-regions.csv`` (plus canonical registries), matches each chapter's path to
``StoryKey``, and appends HTML cards with relative ``.md`` links to hero and
world-of-rathe pages.
**No card is emitted without a resolvable target file** under ``src/`` (heroes
via ``heroes-of-rathe/``, locations and regions via ``regions.csv``
``WorldOfRatheStoryKey``). Optional ``locations.csv`` ``LoreFragment`` appends
``#id`` for deep links into that world page (mdBook heading id, e.g. ``enion``
for ``### Enion``). Cards never link to the chapter file itself (e.g. no region
cards on ``world-of-rathe/savage-lands.md`` that point back to itself). All cards
render in one ``.related-cards`` grid (heroes first, optional spacer, then
locations, optional spacer, then regions) so a small theme script can equalize
card heights across all groups.

mdBook passes ``(PreprocessorContext, Book)`` as JSON on stdin; this process must
print only the modified ``Book`` JSON on stdout. Supports ``supports <renderer>``.
"""

from __future__ import annotations

import html
import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from hero_overrides import HERO_SLUG_LORE_FILE_OVERRIDES  # noqa: E402
from pipe_csv_io import read_pipe_csv  # noqa: E402

MARK_START = "<!-- fablore-related:start -->"
MARK_END = "<!-- fablore-related:end -->"


def _same_src_markdown(chapter_src_path: str, target_src_path: str) -> bool:
    """True when ``chapter`` and ``target`` are the same ``src`` markdown path."""
    a = Path(chapter_src_path).as_posix()
    b = Path(target_src_path).as_posix()
    return bool(a) and a == b


def relative_md_href(chapter_src_path: str, target_src_path: str) -> str:
    """Return a POSIX relative URL from one ``src/`` markdown path to another.

    Args:
        chapter_src_path: Path of the current chapter relative to the book's
            ``src`` directory (e.g. ``main-story/foo/bar.md``).
        target_src_path: Target path under the same ``src`` root.

    Returns:
        Relative path suitable for a Markdown/HTML ``href`` (uses ``.md``).
    """
    return Path(
        os.path.relpath(Path(target_src_path), start=Path(chapter_src_path).parent)
    ).as_posix()


@dataclass(frozen=True)
class RelatedMaps:
    """Lookup tables built from ``src/data`` pipe CSVs."""

    story_key_to_id: dict[str, str]
    story_heroes: dict[str, frozenset[str]]
    story_locations: dict[str, frozenset[str]]
    story_regions: dict[str, frozenset[str]]
    canonical_hero: dict[str, tuple[str, str]]
    location_row: dict[str, tuple[str, str, str]]
    region_row: dict[str, tuple[str, str]]


def load_related_maps(data_dir: Path) -> RelatedMaps:
    """Load junction and registry rows needed to resolve related links.

    Args:
        data_dir: Directory containing ``stories.csv`` and junction files
            (typically ``<repo>/src/data``).

    Returns:
        Frozen lookup maps for the preprocessor run.
    """
    def rows(path: Path) -> list[dict[str, str]]:
        if not path.is_file():
            return []
        _fn, rs = read_pipe_csv(path)
        return rs

    key_to_id: dict[str, str] = {}
    for r in rows(data_dir / "stories.csv"):
        sk = (r.get("StoryKey") or "").strip()
        sid = (r.get("StoryId") or "").strip()
        if sk and sid:
            key_to_id[Path(sk).as_posix()] = sid

    sh: dict[str, set[str]] = {}
    for r in rows(data_dir / "story-heroes.csv"):
        sid = (r.get("StoryId") or "").strip()
        hid = (r.get("CanonicalId") or "").strip()
        if sid and hid:
            sh.setdefault(sid, set()).add(hid)

    sl: dict[str, set[str]] = {}
    for r in rows(data_dir / "story-locations.csv"):
        sid = (r.get("StoryId") or "").strip()
        lid = (r.get("LocationId") or "").strip()
        if sid and lid:
            sl.setdefault(sid, set()).add(lid)

    sr: dict[str, set[str]] = {}
    for r in rows(data_dir / "story-regions.csv"):
        sid = (r.get("StoryId") or "").strip()
        rid = (r.get("RegionId") or "").strip()
        if sid and rid:
            sr.setdefault(sid, set()).add(rid)

    canonical: dict[str, tuple[str, str]] = {}
    for r in rows(data_dir / "heroes-canonical.csv"):
        cid = (r.get("CanonicalId") or "").strip()
        slug = (r.get("CanonicalSlug") or "").strip()
        name = (r.get("CanonicalHero") or "").strip()
        if cid and slug:
            canonical[cid] = (slug, name or slug)

    loc: dict[str, tuple[str, str, str]] = {}
    for r in rows(data_dir / "locations.csv"):
        lid = (r.get("LocationId") or "").strip()
        name = (r.get("Name") or "").strip()
        rid = (r.get("RegionId") or "").strip()
        frag = (r.get("LoreFragment") or "").strip().lstrip("#")
        if lid and name:
            loc[lid] = (name, rid, frag)

    reg: dict[str, tuple[str, str]] = {}
    for r in rows(data_dir / "regions.csv"):
        rid = (r.get("RegionId") or "").strip()
        rname = (r.get("RegionName") or "").strip()
        wk = (r.get("WorldOfRatheStoryKey") or "").strip()
        if rid:
            reg[rid] = (rname, wk)

    return RelatedMaps(
        story_key_to_id=key_to_id,
        story_heroes={k: frozenset(v) for k, v in sh.items()},
        story_locations={k: frozenset(v) for k, v in sl.items()},
        story_regions={k: frozenset(v) for k, v in sr.items()},
        canonical_hero=canonical,
        location_row=loc,
        region_row=reg,
    )


def resolve_hero_src_path(src_root: Path, canonical_slug: str) -> str | None:
    """Return ``src``-relative path to hero lore markdown if a file exists.

    Args:
        src_root: Book source directory (parent of ``heroes-of-rathe/``).
        canonical_slug: ``CanonicalSlug`` from ``heroes-canonical.csv``.

    Returns:
        Path relative to ``src_root`` using POSIX separators, or ``None``.
    """
    override = HERO_SLUG_LORE_FILE_OVERRIDES.get(canonical_slug.strip())
    if override:
        p = Path(override)
        if (src_root / p).is_file():
            return p.as_posix()
    hero_dir = src_root / "heroes-of-rathe"
    for fname in (f"{canonical_slug}-about.md", f"{canonical_slug}.md"):
        if (hero_dir / fname).is_file():
            return str(Path("heroes-of-rathe") / fname)
    return None


_CARD_GROUP_ORDER: tuple[str, ...] = ("Hero", "Location", "Region")


def _append_card_markup(
    parts: list[str], kind: str, title: str, sub: str, href: str
) -> None:
    """Append one ``related-card`` anchor to ``parts`` (mutates list)."""
    esc_title = html.escape(title)
    esc_sub = html.escape(sub) if sub else ""
    parts.append(f'<a class="related-card" href="{href}">')
    parts.append('<span class="related-card-body">')
    parts.append(f'<span class="related-card-type">{html.escape(kind)}</span>')
    parts.append(f'<span class="related-card-title">{esc_title}</span>')
    parts.append("</span>")
    if esc_sub:
        parts.append(f'<span class="related-card-sub">{esc_sub}</span>')
    parts.append("</a>")


def build_related_fragment(
    maps: RelatedMaps,
    *,
    story_id: str,
    chapter_src_path: str,
    src_root: Path,
) -> str:
    """Build HTML fragment (no surrounding markers) for related cards.

    Args:
        maps: Loaded registry maps.
        story_id: Primary key for the current chapter in ``stories.csv``.
        chapter_src_path: Chapter path relative to ``src_root``.
        src_root: Book ``src`` directory on disk.

    Returns:
        HTML string, or empty if there are no resolvable related entries.
        Every card includes a non-empty ``href``; rows without a link target are
        omitted (see module docstring). Location and hero cards whose target file
        is the same as ``chapter_src_path`` are omitted (no self-links on world
        lore pages or a hero's own about page).
    """
    hero_ids = sorted(maps.story_heroes.get(story_id, frozenset()))
    loc_ids = sorted(maps.story_locations.get(story_id, frozenset()))
    reg_ids = sorted(maps.story_regions.get(story_id, frozenset()))

    hero_cards: list[tuple[str, str, str, str]] = []
    loc_cards: list[tuple[str, str, str, str]] = []
    reg_cards: list[tuple[str, str, str, str]] = []
    # (kind_label, title, subtitle, href). Only href-populated rows become cards.

    for hid in hero_ids:
        row = maps.canonical_hero.get(hid)
        if not row:
            continue
        slug, display = row
        target = resolve_hero_src_path(src_root, slug)
        if not target:
            print(
                f"mdbook_related: skip hero {display!r} (slug={slug!r}): no lore file",
                file=sys.stderr,
            )
            continue
        if _same_src_markdown(chapter_src_path, target):
            continue
        href = html.escape(relative_md_href(chapter_src_path, target))
        hero_cards.append(("Hero", display, "", href))

    for lid in loc_ids:
        loc = maps.location_row.get(lid)
        if not loc:
            continue
        place, rid, lfrag = loc
        rname, world_key = "", ""
        if rid:
            reg = maps.region_row.get(rid)
            if reg:
                rname, world_key = reg[0], reg[1]
        subtitle = rname if rname else ""
        if not world_key:
            continue
        wk = Path(world_key).as_posix()
        if not (src_root / wk).is_file():
            print(
                f"mdbook_related: location {place!r}: omitting card (world page {wk!r} missing)",
                file=sys.stderr,
            )
            continue
        if _same_src_markdown(chapter_src_path, wk):
            continue
        rel = relative_md_href(chapter_src_path, wk)
        frag = (lfrag or "").strip().lstrip("#")
        url = f"{rel}#{frag}" if frag else rel
        href = html.escape(url)
        loc_cards.append(("Location", place, subtitle, href))

    for rid in reg_ids:
        reg = maps.region_row.get(rid)
        if not reg:
            continue
        rname, world_key = reg
        if not world_key:
            continue
        wk = Path(world_key).as_posix()
        if not (src_root / wk).is_file():
            print(
                f"mdbook_related: region {rname!r}: omitting card (world page {wk!r} missing)",
                file=sys.stderr,
            )
            continue
        if _same_src_markdown(chapter_src_path, wk):
            continue
        href = html.escape(relative_md_href(chapter_src_path, wk))
        reg_cards.append(("Region", rname, "", href))

    by_kind: dict[str, list[tuple[str, str, str, str]]] = {
        "Hero": [c for c in hero_cards if c[3]],
        "Location": [c for c in loc_cards if c[3]],
        "Region": [c for c in reg_cards if c[3]],
    }
    total = sum(len(by_kind[k]) for k in by_kind)
    if total == 0:
        return ""

    parts = [
        '<section class="related-section" aria-label="Related Lore">',
        '<h1 id="related-lore">Related Lore</h1>',
        '<div class="related-cards">',
    ]
    first_group = True
    for kind_key in _CARD_GROUP_ORDER:
        group = by_kind.get(kind_key, [])
        if not group:
            continue
        group.sort(key=lambda c: c[1].lower())
        if not first_group:
            parts.append(
                '<div class="related-cards-spacer" aria-hidden="true"></div>'
            )
        first_group = False
        for kind, title, sub, href in group:
            _append_card_markup(parts, kind, title, sub, href)
    parts.append("</div></section>")
    return "\n".join(parts)


def inject_marked_block(content: str, inner_html: str) -> str:
    """Insert or replace the fablore-related marked block at the end of ``content``.

    Args:
        content: Original chapter markdown/HTML.
        inner_html: HTML to place between markers (may be empty to strip the block).

    Returns:
        Updated chapter content.
    """
    if MARK_START in content and MARK_END in content:
        pre, _, rest = content.partition(MARK_START)
        _, _, post = rest.partition(MARK_END)
        if inner_html.strip():
            block = f"{MARK_START}\n{inner_html}\n{MARK_END}"
        else:
            block = ""
        return pre.rstrip() + ("\n\n" if block and pre.strip() else "") + block + post
    if inner_html.strip():
        sep = "\n\n" if content.strip() else ""
        return content.rstrip() + sep + f"{MARK_START}\n{inner_html}\n{MARK_END}\n"
    return content


def story_id_for_chapter(maps: RelatedMaps, chapter_path: str | None) -> str | None:
    """Resolve ``StoryId`` from a chapter's ``path`` (``StoryKey``).

    Args:
        maps: Loaded maps including ``story_key_to_id``.
        chapter_path: ``Chapter.path`` from mdBook JSON.

    Returns:
        ``StoryId`` if the chapter is listed in ``stories.csv``, else ``None``.
    """
    if not chapter_path:
        return None
    key = Path(chapter_path).as_posix()
    return maps.story_key_to_id.get(key)


def process_chapter_content(
    content: str,
    maps: RelatedMaps,
    *,
    chapter_src_path: str,
    src_root: Path,
) -> str:
    """Append or refresh the Related section for one chapter."""
    sid = story_id_for_chapter(maps, chapter_src_path)
    if not sid:
        return inject_marked_block(content, "")
    fragment = build_related_fragment(
        maps,
        story_id=sid,
        chapter_src_path=chapter_src_path,
        src_root=src_root,
    )
    return inject_marked_block(content, fragment)


def walk_mutate_sections(
    sections: list,
    maps: RelatedMaps,
    src_root: Path,
) -> None:
    """Recursively update every chapter in ``sections`` in place."""
    for item in sections:
        if not isinstance(item, dict):
            continue
        if "Chapter" in item:
            ch = item["Chapter"]
            path = ch.get("path")
            if path and isinstance(path, str):
                ch["content"] = process_chapter_content(
                    ch.get("content") or "",
                    maps,
                    chapter_src_path=path,
                    src_root=src_root,
                )
            walk_mutate_sections(ch.get("sub_items") or [], maps, src_root)
        elif "Separator" in item or "PartTitle" in item:
            continue


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

    maps = load_related_maps(data_dir)
    walk_mutate_sections(book.get("sections") or [], maps, src_root)

    json.dump(book, sys.stdout, ensure_ascii=False)


if __name__ == "__main__":
    main()
