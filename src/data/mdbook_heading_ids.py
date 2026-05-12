"""Heading anchor ids compatible with mdBook 0.4 HTML output.

mdBook derives ``<hN id="…">`` from heading text using the same rules as
``mdbook::utils::id_from_content`` / ``normalize_id`` (strip markup, normalize
characters, ASCII-lowercase only for ``A``–``Z``). This module reproduces that
logic in Python so ``locations.csv`` ``LoreFragment`` values can be validated
against ``src/**/*.md`` before build.

See ``https://github.com/rust-lang/mdBook`` (v0.4.x) ``src/utils/mod.rs``:
``normalize_id``, ``id_from_content``, ``unique_id_from_content``.
"""

from __future__ import annotations

import re
from pathlib import Path

from pipe_csv_io import read_pipe_csv

_ATX_HEADING = re.compile(r"^(#{1,6})\s+(.+?)\s*(?:#+\s*)?$")
_HTML_TAGS = re.compile(r"<.*?>", re.DOTALL)
_ENTITY_REPLACEMENTS = ("&lt;", "&gt;", "&amp;", "&#39;", "&quot;")


def normalize_id(content: str) -> str:
    """Match mdBook ``normalize_id``: alnum / ``_`` / ``-`` kept, whitespace → ``-``."""
    parts: list[str] = []
    for ch in content:
        if ch.isalnum() or ch in "_-":
            if ch.isascii() and ch.isalpha() and "A" <= ch <= "Z":
                parts.append(chr(ord(ch) + 32))
            else:
                parts.append(ch)
        elif ch.isspace():
            parts.append("-")
    return "".join(parts)


def id_from_content(content: str) -> str:
    """Match mdBook ``id_from_content`` (heading line or plain title text)."""
    s = _HTML_TAGS.sub("", content)
    for sub in _ENTITY_REPLACEMENTS:
        s = s.replace(sub, "")
    trimmed = s.strip().lstrip("#").strip()
    return normalize_id(trimmed)


def unique_id_from_content(content: str, id_counter: dict[str, int]) -> str:
    """Match mdBook ``unique_id_from_content`` (duplicate headings get ``-1``, ``-2``, …)."""
    base = id_from_content(content)
    count = id_counter.get(base, 0)
    if count == 0:
        unique = base
    else:
        unique = f"{base}-{count}"
    id_counter[base] = count + 1
    return unique


def collect_heading_anchor_ids(markdown: str) -> list[str]:
    """Return heading ids in document order, as mdBook would emit them.

    Only ATX headings (``#`` …) are parsed; setext headings are ignored (same
    limitation as a line-based scan).

    Args:
        markdown: Full ``.md`` file text.

    Returns:
        List of unique anchor strings (including ``-1`` suffixes for clashes).
    """
    id_counter: dict[str, int] = {}
    ids: list[str] = []
    for line in markdown.splitlines():
        m = _ATX_HEADING.match(line.rstrip())
        if not m:
            continue
        raw_title = m.group(2).strip()
        if not raw_title:
            continue
        ids.append(unique_id_from_content(raw_title, id_counter))
    return ids


def collect_heading_anchor_ids_from_path(md_path: Path) -> list[str]:
    """Load a markdown file and return :func:`collect_heading_anchor_ids`."""
    text = md_path.read_text(encoding="utf-8")
    if text.startswith("\ufeff"):
        text = text[1:]
    return collect_heading_anchor_ids(text)


def world_lore_markdown_path(src_root: Path, regions_csv: Path, region_id: str) -> Path | None:
    """Resolve ``WorldOfRatheStoryKey`` for ``region_id`` to an absolute path under ``src_root``."""
    rid = (region_id or "").strip()
    if not rid:
        return None
    if not regions_csv.is_file():
        return None
    _fn, rows = read_pipe_csv(regions_csv)
    wk = ""
    for row in rows:
        if (row.get("RegionId") or "").strip() == rid:
            wk = (row.get("WorldOfRatheStoryKey") or "").strip()
            break
    if not wk:
        return None
    return (src_root / Path(wk)).resolve()


def format_fragment_suggestion(ids: list[str], *, limit: int = 35) -> str:
    """Return a short sorted list of ids for error messages."""
    uniq = sorted(set(ids))
    if len(uniq) <= limit:
        return ", ".join(uniq)
    head = ", ".join(uniq[:limit])
    return f"{head}, … ({len(uniq)} ids total; showing first {limit})"


def require_valid_lore_fragment(
    *,
    src_root: Path,
    regions_csv: Path,
    region_id: str,
    lore_fragment: str,
) -> None:
    """Raise ``ValueError`` if ``lore_fragment`` is not an mdBook heading id on the region page.

    Args:
        src_root: Book ``src`` root (parent of ``world-of-rathe/``).
        regions_csv: Path to ``regions.csv``.
        region_id: Location's ``RegionId`` (must be non-empty).
        lore_fragment: Normalized fragment (no ``#``); non-empty only.

    Raises:
        ValueError: When the fragment cannot be resolved to a heading on disk.
    """
    frag = (lore_fragment or "").strip().lstrip("#")
    if not frag:
        return
    rid = (region_id or "").strip()
    if not rid:
        raise ValueError(
            "LoreFragment requires a known region (set region_name= or region_id=) "
            "so the world lore file can be resolved from regions.csv."
        )
    md_path = world_lore_markdown_path(src_root, regions_csv, rid)
    if md_path is None:
        raise ValueError(
            f"LoreFragment {frag!r}: region {rid!r} has no WorldOfRatheStoryKey in regions.csv."
        )
    if not md_path.is_file():
        raise ValueError(
            f"LoreFragment {frag!r}: world lore file is missing: {md_path.relative_to(src_root)}"
        )
    ids = collect_heading_anchor_ids_from_path(md_path)
    if frag not in ids:
        rel = md_path.relative_to(src_root).as_posix()
        raise ValueError(
            f"LoreFragment {frag!r} is not a heading id in {rel}. "
            f"Valid heading ids include: {format_fragment_suggestion(ids)}"
        )
