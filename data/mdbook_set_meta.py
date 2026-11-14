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
import re
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from mdbook_common import (  # noqa: E402
    SECTION_BY_KEY,
    arc_of,
    entity_names,
    format_date,
    iter_chapters,
    load_arcs,
    load_sets,
    run,
)
from mdbook_common import story_meta_item as _item  # noqa: E402

MARK_START = "<!-- fablore-set-meta:start -->"
MARK_END = "<!-- fablore-set-meta:end -->"

# The sections that carry a set card. The flavour hub is skipped: as a
# filename-arc page it would otherwise read as the arc "intro".
_CARD_SECTIONS = ("flavour", "digital-tiles")
_HUBS = frozenset(SECTION_BY_KEY[key].hub_page for key in _CARD_SECTIONS)


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------


def _load_meta(data_dir: Path) -> dict[str, dict]:
    """Return a map from arc slug → set metadata dict."""
    sets_by_id = load_sets(data_dir)
    set_type_by_id = entity_names(data_dir / "csv" / "set-types.csv", "SetTypeId", "SetType")

    result: dict[str, dict] = {}
    for slug, row in load_arcs(data_dir).items():
        set_id = (row.get("SetId") or "").strip()
        if set_id not in sets_by_id:
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


def _build_set_meta_html(meta: dict) -> str:
    items: list[str] = []

    set_name = meta.get("set_name", "")
    set_type = meta.get("set_type", "")
    release_date = meta.get("release_date", "")

    if set_name:
        items.append(_item("fas fa-cube", f"<strong>{html.escape(set_name)}</strong>"))

    if release_date:
        items.append(_item("fas fa-calendar", html.escape(format_date(release_date))))

    if set_type:
        items.append(_item("fas fa-tag", html.escape(set_type)))

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


def _set_slug(posix_path: str) -> str | None:
    """The arc slug whose set card a flavour or digital-tiles page carries, or ``None``.

    Digital tiles count only at ``digital-tiles/<arc>/<page>.md``, not deeper,
    where :func:`arc_of` (and the hubs and Sets index) would still find an arc.
    """
    arc = arc_of(posix_path)
    if arc is None or arc[0] not in _CARD_SECTIONS or posix_path in _HUBS:
        return None
    if arc[0] == "digital-tiles" and posix_path.count("/") != 2:
        return None
    return arc[1]


# ---------------------------------------------------------------------------
# mdBook walk
# ---------------------------------------------------------------------------


def _walk_sections(sections: list, slug_meta: dict[str, dict]) -> None:
    for ch in iter_chapters(sections):
        path = Path(ch.get("path") or "").as_posix()

        slug = _set_slug(path)
        if slug and slug in slug_meta:
            meta_html = _build_set_meta_html(slug_meta[slug])
            ch["content"] = _inject(ch.get("content") or "", meta_html, after_h1=True)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main() -> None:
    """stdin: ``(PreprocessorContext, Book)`` JSON; stdout: ``Book`` JSON only."""
    run(lambda items, src_root: _walk_sections(items, _load_meta(src_root / "data")))


if __name__ == "__main__":
    main()
