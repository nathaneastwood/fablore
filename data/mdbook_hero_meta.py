#!/usr/bin/env python3
"""mdBook preprocessor: inject a hero metadata card after each hero variant heading.

For each chapter under ``heroes-of-rathe/`` this preprocessor scans all H1
headings, matches each heading text against ``CardName`` values in
``heroes-game.csv``, and injects a metadata card immediately after each match.
The card shows first set, release date, class/talent, and living legend status
for that specific hero variant.

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

# Set type IDs to exclude when finding the "first set" for a hero variant.
_EXCLUDED_SET_TYPE_IDS = {
    "TY1ac8c9771b",  # Promo
    "TY92969bb9ea",  # Prize
    "TY218948d76b",  # Token Set
}

# Lower value = preferred when release dates tie.
_SET_TYPE_PRIORITY: dict[str, int] = {
    "TY87478277a5": 0,  # Core Booster Set
    "TY858a95be59": 1,  # Expansion Booster Set
    "TY48cd9f30bc": 2,  # Supplementary Booster Set
    "TYd8e2e91515": 3,  # History Pack
    "TYae8fdcc03a": 4,  # Mastery Pack
    "TY00678b0ea7": 5,  # Welcome Deck
    "TY3634cb99aa": 6,  # Hero Deck
    "TY526cd03a42": 7,  # Blitz Deck
    "TYfcaaf6a22f": 8,  # Armory Deck
    "TY6f903c3145": 9,  # Classic Battles Deck
    "TY7fc7966b3b": 10,  # First Strike Deck
    "TY14e59cce5d": 11,  # Box Set
    "TY0143717ab6": 12,  # History Pack Blitz Deck
    "TY4dde9990af": 13,  # Demo Deck
}


def _format_date(date_str: str) -> str:
    """Format ``YYYY-MM-DD`` (or ISO datetime) as ``D Month YYYY``."""
    s = date_str.strip().split("T")[0]
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
        f'<i class="{icon}" aria-hidden="true"></i>'
        f" {inner}</span>"
    )


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------


def _load_card_meta(data_dir: Path) -> dict[str, dict]:
    """Return a map from ``CardName`` → per-variant hero metadata."""
    _, game_rows = read_pipe_csv(data_dir / "csv" / "heroes-game.csv")
    _, printings_rows = read_pipe_csv(data_dir / "csv" / "heroes-printings.csv")
    _, sets_rows = read_pipe_csv(data_dir / "csv" / "sets.csv")
    _, set_types_rows = read_pipe_csv(data_dir / "csv" / "set-types.csv")
    _, classes_rows = read_pipe_csv(data_dir / "csv" / "classes.csv")
    _, talents_rows = read_pipe_csv(data_dir / "csv" / "talents.csv")
    _, ll_rows = read_pipe_csv(data_dir / "csv" / "heroes-ll.csv")

    # --- sets ---
    set_type_id_by_set_id: dict[str, str] = {}
    set_name_by_id: dict[str, str] = {}
    set_release_by_id: dict[str, str] = {}
    for row in sets_rows:
        sid = (row.get("SetId") or "").strip()
        if sid:
            set_type_id_by_set_id[sid] = (row.get("SetTypeId") or "").strip()
            set_name_by_id[sid] = (row.get("SetName") or "").strip()
            set_release_by_id[sid] = (
                (row.get("InitialReleaseDate") or "").strip().split("T")[0]
            )

    # set-types lookup — kept for future use / debugging
    _ = {
        (row.get("SetTypeId") or "").strip(): (row.get("SetType") or "").strip()
        for row in set_types_rows
        if (row.get("SetTypeId") or "").strip()
    }

    # --- classes / talents ---
    class_name_by_id: dict[str, str] = {
        (row.get("ClassId") or "").strip(): (row.get("ClassName") or "").strip()
        for row in classes_rows
        if (row.get("ClassId") or "").strip()
    }
    talent_name_by_id: dict[str, str] = {
        (row.get("TalentId") or "").strip(): (row.get("TalentName") or "").strip()
        for row in talents_rows
        if (row.get("TalentId") or "").strip()
    }

    # --- printings per HeroGameId ---
    printings_by_game_id: dict[str, list[str]] = {}
    for row in printings_rows:
        gid = (row.get("HeroGameId") or "").strip()
        sid = (row.get("SetId") or "").strip()
        if gid and sid:
            printings_by_game_id.setdefault(gid, []).append(sid)

    # --- LL entries per CardName ---
    ll_by_card_name: dict[str, list[dict[str, str]]] = {}
    for row in ll_rows:
        card_name = (row.get("CardName") or "").strip()
        if card_name:
            ll_by_card_name.setdefault(card_name, []).append(
                {
                    "Format": (row.get("Format") or "").strip(),
                    "DateInEffect": (row.get("DateInEffect") or "").strip(),
                }
            )

    # --- build per-CardName metadata ---
    result: dict[str, dict] = {}
    for row in game_rows:
        card_name = (row.get("CardName") or "").strip()
        hero_game_id = (row.get("HeroGameId") or "").strip()
        if not card_name or not hero_game_id:
            continue

        classes = [
            class_name_by_id[cid]
            for raw in (row.get("ClassIds") or "").split(",")
            if (cid := raw.strip()) and cid in class_name_by_id
        ]
        talents = [
            talent_name_by_id[tid]
            for raw in (row.get("TalentIds") or "").split(",")
            if (tid := raw.strip()) and tid in talent_name_by_id
        ]

        best_set_id, best_date, best_priority = "", "", 9999
        for sid in printings_by_game_id.get(hero_game_id, []):
            type_id = set_type_id_by_set_id.get(sid, "")
            if type_id in _EXCLUDED_SET_TYPE_IDS:
                continue
            release = set_release_by_id.get(sid, "")
            if not release:
                continue
            priority = _SET_TYPE_PRIORITY.get(type_id, 50)
            if (
                not best_date
                or release < best_date
                or (release == best_date and priority < best_priority)
            ):
                best_date = release
                best_set_id = sid
                best_priority = priority

        result[card_name] = {
            "first_set_name": set_name_by_id.get(best_set_id, ""),
            "first_set_date": best_date,
            "classes": classes,
            "talents": talents,
            "ll": ll_by_card_name.get(card_name, []),
        }

    return result


# ---------------------------------------------------------------------------
# HTML building
# ---------------------------------------------------------------------------


def _build_hero_meta_html(meta: dict) -> str:
    items: list[str] = []

    set_name = meta.get("first_set_name", "")
    set_date = meta.get("first_set_date", "")
    if set_name:
        date_part = f" — {_format_date(set_date)}" if set_date else ""
        items.append(
            _item(
                "fas fa-cube",
                f"First released in <strong>{html.escape(set_name)}</strong>{html.escape(date_part)}",
            )
        )

    classes = meta.get("classes", [])
    talents = meta.get("talents", [])
    if classes or talents:
        labels = [html.escape(c) for c in classes] + [html.escape(t) for t in talents]
        joined = " · ".join(f"<strong>{label}</strong>" for label in labels)
        items.append(_item("fas fa-tag", joined))

    for entry in meta.get("ll", []):
        fmt = html.escape(entry.get("Format", ""))
        date_fmt = _format_date(entry.get("DateInEffect", ""))
        detail = (
            f" ({html.escape(fmt)}, {html.escape(date_fmt)})"
            if date_fmt
            else f" ({html.escape(fmt)})"
        )
        items.append(_item("fas fa-trophy", f"Living Legend{detail}"))

    if not items:
        return ""

    inner = "\n  ".join(items)
    return f'<div class="story-meta" aria-label="Hero information">\n  {inner}\n</div>'


# ---------------------------------------------------------------------------
# Heading → CardName resolution
# ---------------------------------------------------------------------------

# Explicit aliases for headings that intentionally differ from the card name
# (e.g. a comma added for display style, or a missing title prefix).
_HEADING_ALIASES: dict[str, str] = {
    "Dash, I/O": "Dash I/O",
    "Data Doll, MKII": "Data Doll MKII",
    "Dorinthea, Ironsong": "Dorinthea Ironsong",
}


def _build_lookup(
    card_meta: dict[str, dict],
) -> tuple[dict[str, dict], dict[str, dict]]:
    """Return (exact_lookup, ci_lookup) for heading → meta resolution.

    ``ci_lookup`` is keyed by ``heading.lower()`` and used as a fallback when
    an exact match fails (handles capitalisation differences like
    ``The`` vs ``the`` in subtitles).
    """
    ci: dict[str, dict] = {}
    for card_name, meta in card_meta.items():
        ci.setdefault(card_name.lower(), meta)
    return card_meta, ci


def _resolve(heading: str, exact: dict[str, dict], ci: dict[str, dict]) -> dict | None:
    # 1. exact match
    if heading in exact:
        return exact[heading]
    # 2. explicit alias
    alias = _HEADING_ALIASES.get(heading)
    if alias and alias in exact:
        return exact[alias]
    # 3. case-insensitive fallback
    return ci.get(heading.lower())


# ---------------------------------------------------------------------------
# Injection
# ---------------------------------------------------------------------------

_H1_RE = re.compile(r"^# ([^\n]+)\n", re.MULTILINE)


def _process_hero_chapter(content: str, card_meta: dict[str, dict]) -> str:
    """Inject a metadata card after each H1 heading that matches a hero CardName."""
    exact, ci = _build_lookup(card_meta)
    parts: list[str] = []
    pos = 0
    for match in _H1_RE.finditer(content):
        heading_text = match.group(1).strip()
        meta = _resolve(heading_text, exact, ci)
        parts.append(content[pos : match.end()])
        pos = match.end()
        if meta is not None:
            inner = _build_hero_meta_html(meta)
            if inner:
                parts.append("\n" + inner + "\n\n")
    parts.append(content[pos:])
    return "".join(parts)


# ---------------------------------------------------------------------------
# mdBook walk
# ---------------------------------------------------------------------------

_HERO_DIR = "heroes-of-rathe/"
_ABOUT_SUFFIX = "-about.md"


def _is_hero_about_page(path: str) -> bool:
    posix = Path(path).as_posix()
    return posix.startswith(_HERO_DIR) and posix.endswith(_ABOUT_SUFFIX)


def _walk_sections(sections: list, card_meta: dict[str, dict]) -> None:
    for item in sections:
        if not isinstance(item, dict):
            continue
        if "Chapter" in item:
            ch = item["Chapter"]
            path = (ch.get("path") or "").strip()
            if path and _is_hero_about_page(path):
                ch["content"] = _process_hero_chapter(
                    ch.get("content") or "", card_meta
                )
            _walk_sections(ch.get("sub_items") or [], card_meta)


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

    card_meta = _load_card_meta(data_dir)
    _walk_sections(book.get("items") or [], card_meta)

    json.dump(book, sys.stdout, ensure_ascii=False)


if __name__ == "__main__":
    main()
