#!/usr/bin/env python3
"""mdBook preprocessor: inject a set metadata card on flavour and digital-tiles pages.

For each chapter under ``flavour/`` or ``digital-tiles/`` this preprocessor
looks up the arc slug in ``story-arcs.csv`` to find a SetId, then reads the
set name, release date, and set type from ``sets.csv`` / ``set-types.csv`` and
injects a ``<div class="story-meta">`` card.

Flavour pages have an H1 heading — the card is inserted after it.
Digital-tile pages have no H1 — the card is prepended before the content.

mdBook passes ``(PreprocessorContext, Book)`` as JSON on stdin; this process
must print only the modified ``Book`` JSON on stdout.  Supports
``supports <renderer>``.
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

MARK_START = "<!-- fablore-set-meta:start -->"
MARK_END = "<!-- fablore-set-meta:end -->"

_SKIP_FLAVOUR = frozenset({"intro"})


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------


def _load_meta(data_dir: Path) -> dict[str, dict]:
    """Return a map from arc slug → set metadata dict."""
    _, arcs_rows = read_pipe_csv(data_dir / "csv" / "story-arcs.csv")
    _, sets_rows = read_pipe_csv(data_dir / "csv" / "sets.csv")
    _, set_types_rows = read_pipe_csv(data_dir / "csv" / "set-types.csv")

    sets_by_id: dict[str, dict] = {
        (r.get("SetId") or "").strip(): r
        for r in sets_rows
        if (r.get("SetId") or "").strip()
    }
    set_type_by_id: dict[str, str] = {
        (r.get("SetTypeId") or "").strip(): (r.get("SetType") or "").strip()
        for r in set_types_rows
        if (r.get("SetTypeId") or "").strip()
    }

    result: dict[str, dict] = {}
    for row in arcs_rows:
        slug = (row.get("Slug") or "").strip()
        set_id = (row.get("SetId") or "").strip()
        if not slug:
            continue
        if not set_id or set_id not in sets_by_id:
            continue
        s = sets_by_id[set_id]
        type_id = (s.get("SetTypeId") or "").strip()
        raw_date = (s.get("InitialReleaseDate") or "").strip().split("T")[0]
        result[slug] = {
            "set_name": (s.get("SetName") or "").strip(),
            "set_type": set_type_by_id.get(type_id, ""),
            "release_date": raw_date,
        }

    return result


# ---------------------------------------------------------------------------
# HTML building
# ---------------------------------------------------------------------------


def _format_date(date_str: str) -> str:
    s = date_str.strip()
    if not s:
        return ""
    try:
        dt = datetime.strptime(s, "%Y-%m-%d")
        return f"{dt.day} {dt.strftime('%B %Y')}"
    except ValueError:
        return s


def _item(icon: str, inner: str) -> str:
    return (
        f'<span class="story-meta-item">'
        f'<i class="fa {icon}" aria-hidden="true"></i>'
        f" {inner}</span>"
    )


def _build_set_meta_html(meta: dict) -> str:
    items: list[str] = []

    set_name = meta.get("set_name", "")
    set_type = meta.get("set_type", "")
    release_date = meta.get("release_date", "")

    if set_name:
        items.append(_item("fa-cube", f"<strong>{html.escape(set_name)}</strong>"))

    if release_date:
        items.append(_item("fa-calendar", html.escape(_format_date(release_date))))

    if set_type:
        items.append(_item("fa-tag", html.escape(set_type)))

    if not items:
        return ""

    inner = "\n  ".join(items)
    return f'<div class="story-meta" aria-label="Set information">\n  {inner}\n</div>'


# ---------------------------------------------------------------------------
# Injection
# ---------------------------------------------------------------------------

_H1_RE = re.compile(r"^# [^\n]*\n", re.MULTILINE)


def _inject(content: str, meta_html: str, *, after_h1: bool) -> str:
    """Insert or replace the set-meta block in ``content``."""
    if MARK_START in content and MARK_END in content:
        pre, _, rest = content.partition(MARK_START)
        _, _, post = rest.partition(MARK_END)
        bare = pre.rstrip() + ("\n\n" if pre.strip() else "") + post.lstrip()
    else:
        bare = content

    if not meta_html.strip():
        return bare

    block = f"{MARK_START}\n{meta_html}\n{MARK_END}"

    if after_h1:
        m = _H1_RE.search(bare)
        if m:
            cut = m.end()
            return bare[:cut] + "\n" + block + "\n\n" + bare[cut:].lstrip("\n")

    return block + "\n\n" + bare


# ---------------------------------------------------------------------------
# Path classification
# ---------------------------------------------------------------------------


def _flavour_slug(posix_path: str) -> str | None:
    """Return the slug for a flavour page, or None if not a flavour page."""
    parts = posix_path.split("/")
    if len(parts) == 2 and parts[0] == "flavour":
        stem = parts[1].removesuffix(".md")
        if stem not in _SKIP_FLAVOUR:
            return stem
    return None


def _digital_tiles_slug(posix_path: str) -> str | None:
    """Return the arc slug for a digital-tiles chapter, or None."""
    parts = posix_path.split("/")
    if len(parts) == 3 and parts[0] == "digital-tiles":
        return parts[1]
    return None


# ---------------------------------------------------------------------------
# mdBook walk
# ---------------------------------------------------------------------------


def _walk_sections(sections: list, slug_meta: dict[str, dict]) -> None:
    for item in sections:
        if not isinstance(item, dict):
            continue
        if "Chapter" not in item:
            continue
        ch = item["Chapter"]
        path = Path(ch.get("path") or "").as_posix()

        flavour_slug = _flavour_slug(path)
        digital_slug = _digital_tiles_slug(path)

        if flavour_slug and flavour_slug in slug_meta:
            meta_html = _build_set_meta_html(slug_meta[flavour_slug])
            ch["content"] = _inject(ch.get("content") or "", meta_html, after_h1=True)

        elif digital_slug and digital_slug in slug_meta:
            meta_html = _build_set_meta_html(slug_meta[digital_slug])
            ch["content"] = _inject(ch.get("content") or "", meta_html, after_h1=True)

        _walk_sections(ch.get("sub_items") or [], slug_meta)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


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

    slug_meta = _load_meta(data_dir)
    _walk_sections(book.get("items") or [], slug_meta)

    json.dump(book, sys.stdout, ensure_ascii=False)


if __name__ == "__main__":
    main()
