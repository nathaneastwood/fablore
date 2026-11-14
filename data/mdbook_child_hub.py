#!/usr/bin/env python3
"""mdBook preprocessor: generate a simple child-page grid on designated hub pages.

Replaces ``<!-- fablore-child-hub:start --> … <!-- fablore-child-hub:end -->``
markers on hub pages that only need a flat grid of their direct SUMMARY.md
children (no arc/set grouping) — unlike :mod:`mdbook_sets_hub`, which handles
arc-driven hub pages.

  weapons/armed-to-the-teeth.md    → grid of weapon cards, with card art
  equipment/in-the-fires-of-the-forge.md → grid of equipment cards, with card art
  languages/intro.md               → grid of language cards, with page art
  other-characters/README.md       → grid of character cards, text only
  data/data.md                     → grid of data table cards, text only

Chapter order follows the book's SUMMARY.md order via a first-pass traversal
of the book sections JSON.
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
    SECTIONS,
    chapter_path,
    iter_chapters,
    load_sets,
    relative_href,
    replace_marked_block,
    run,
)
from pipe_csv_io import read_pipe_csv  # noqa: E402

MARK_START = "<!-- fablore-child-hub:start -->"
MARK_END = "<!-- fablore-child-hub:end -->"

# Hub pages this preprocessor handles, keyed by chapter path, with the card style for their children.
_HUB_PAGES = {s.hub_page: s.child_cards for s in SECTIONS if s.child_cards and s.hub_page}

_IMG_SRC_RE = re.compile(r'<img\b[^>]*\bsrc="([^"]+)"', re.IGNORECASE)

Chapter = dict  # {"name": str, "path": str}


# ---------------------------------------------------------------------------
# Pass 1: collect direct children of each hub page
# ---------------------------------------------------------------------------


def _collect(sections: list, hub_children: dict[str, list[Chapter]]) -> None:
    """Walk book sections; for each hub page, record its direct sub_items."""
    for ch in iter_chapters(sections):
        path = chapter_path(ch)
        if not path:
            continue
        if path not in _HUB_PAGES:
            continue
        children: list[Chapter] = []
        for sub in ch.get("sub_items") or []:
            if not isinstance(sub, dict) or "Chapter" not in sub:
                continue
            sub_ch = sub["Chapter"]
            sub_path_raw = (sub_ch.get("path") or "").strip()
            if not sub_path_raw:
                continue
            children.append(
                {
                    "name": sub_ch.get("name", ""),
                    "path": Path(sub_path_raw).as_posix(),
                }
            )
        hub_children[path] = children


# ---------------------------------------------------------------------------
# Image resolution
# ---------------------------------------------------------------------------


# Per card kind: (canonical CSV, game CSV, printings CSV, story junction CSV, canonical id field, game id field).
_KIND_FILES = {
    "weapons": (
        "weapons-canonical.csv",
        "weapons-game.csv",
        "weapons-printings.csv",
        "story-weapons.csv",
        "CanonicalWeaponId",
        "WeaponGameId",
    ),
    "equipment": (
        "equipment-canonical.csv",
        "equipment-game.csv",
        "equipment-printings.csv",
        "story-equipment.csv",
        "CanonicalEquipmentId",
        "EquipmentGameId",
    ),
}


def _load_card_image_lookup(data_dir: Path, kind: str) -> dict[str, str]:
    """Build slug → ImageURL lookup for the earliest-release printing of each card.

    Reprint sets (e.g. History Pack) can appear earlier in the upstream
    ``card-printing.csv`` row order despite releasing later, so printings are
    picked by ``sets.csv`` ``InitialReleaseDate``, not file order.

    Args:
        data_dir: ``src/data`` directory.
        kind: ``"weapons"`` or ``"equipment"``.

    Returns:
        Mapping of ``CanonicalSlug`` to a non-empty ``ImageURL``, when available.
    """
    csv_dir = data_dir / "csv"
    canonical_csv, game_csv, printings_csv, _, canonical_id_field, game_id_field = _KIND_FILES[kind]
    _, canonical_rows = read_pipe_csv(csv_dir / canonical_csv)
    _, game_rows = read_pipe_csv(csv_dir / game_csv)
    _, printings_rows = read_pipe_csv(csv_dir / printings_csv)
    release_by_set_id = {sid: (r.get("InitialReleaseDate") or "").strip() for sid, r in load_sets(data_dir).items()}

    slug_by_canonical_id = {
        row[canonical_id_field]: row["CanonicalSlug"]
        for row in canonical_rows
        if row.get(canonical_id_field) and row.get("CanonicalSlug")
    }
    canonical_id_by_game_id = {
        row[game_id_field]: row[canonical_id_field]
        for row in game_rows
        if row.get(game_id_field) and row.get(canonical_id_field)
    }

    best_release_by_slug: dict[str, str] = {}
    image_by_slug: dict[str, str] = {}
    for row in printings_rows:
        game_id = row.get(game_id_field, "")
        image_url = row.get("ImageURL", "").strip()
        if not game_id or not image_url:
            continue
        canonical_id = canonical_id_by_game_id.get(game_id)
        if not canonical_id:
            continue
        slug = slug_by_canonical_id.get(canonical_id)
        if not slug:
            continue
        release = release_by_set_id.get(row.get("SetId", ""), "")
        if not release:
            continue
        current_best = best_release_by_slug.get(slug)
        if current_best is None or release < current_best:
            best_release_by_slug[slug] = release
            image_by_slug[slug] = image_url

    return image_by_slug


def _load_story_card_images(data_dir: Path, kind: str) -> dict[str, str]:
    """Map each page's ``StoryKey`` to the art of the one card its story links to.

    The card comes from the ``story-weapons.csv`` / ``story-equipment.csv``
    junction, so a page filename that differs from the card name (e.g.
    ``talishar-lost-prince.md`` for ``talishar-the-lost-prince``) still finds
    its card. A story linked to no card, or to more than one, is left out and
    the page falls back to its own ``<img>``.

    Args:
        data_dir: ``src/data`` directory.
        kind: ``"weapons"`` or ``"equipment"``.

    Returns:
        Mapping of ``StoryKey`` to a non-empty card ``ImageURL``.
    """
    csv_dir = data_dir / "csv"
    canonical_csv, _, _, junction_csv, canonical_id_field, _ = _KIND_FILES[kind]
    image_by_slug = _load_card_image_lookup(data_dir, kind)
    _, canonical_rows = read_pipe_csv(csv_dir / canonical_csv)
    _, story_rows = read_pipe_csv(csv_dir / "stories.csv")
    _, junction_rows = read_pipe_csv(csv_dir / junction_csv)

    slug_by_canonical_id = {
        row[canonical_id_field]: row["CanonicalSlug"]
        for row in canonical_rows
        if row.get(canonical_id_field) and row.get("CanonicalSlug")
    }
    story_key_by_id = {
        row["StoryId"]: row["StoryKey"] for row in story_rows if row.get("StoryId") and row.get("StoryKey")
    }

    cards_by_story_key: dict[str, set[str]] = {}
    for row in junction_rows:
        story_key = story_key_by_id.get(row.get("StoryId", ""))
        canonical_id = row.get(canonical_id_field, "")
        if story_key and canonical_id:
            cards_by_story_key.setdefault(story_key, set()).add(canonical_id)

    image_by_story_key: dict[str, str] = {}
    for story_key, canonical_ids in cards_by_story_key.items():
        if len(canonical_ids) != 1:
            continue
        image = image_by_slug.get(slug_by_canonical_id.get(next(iter(canonical_ids)), ""), "")
        if image:
            image_by_story_key[story_key] = image
    return image_by_story_key


def _page_img_fallback(src_root: Path, child_path: str) -> str:
    """Scan the child page's raw markdown for the first ``<img src="...">``."""
    full = src_root / child_path
    if not full.is_file():
        return ""
    content = full.read_text(encoding="utf-8")
    match = _IMG_SRC_RE.search(content)
    return match.group(1) if match else ""


def _child_image(
    src_root: Path,
    child_path: str,
    hub_type: str,
    image_by_story_key: dict[str, str],
) -> tuple[str, bool]:
    """Return ``(image_url, is_card_art)``.

    ``is_card_art`` is ``True`` for portrait card-printing images (resolved via
    the story's junction link), which need different aspect-ratio handling than
    the landscape banner images used as a page ``<img>`` fallback.
    """
    if hub_type == "plain":
        return "", False

    if hub_type in ("weapons", "equipment"):
        image = image_by_story_key.get(child_path, "")
        if image:
            return image, True

    # languages hub, or weapons/equipment pages with no linked card art.
    return _page_img_fallback(src_root, child_path), False


# ---------------------------------------------------------------------------
# Pass 2: build HTML
# ---------------------------------------------------------------------------


def _card_grid_html(
    hub_src: str,
    src_root: Path,
    children: list[Chapter],
    hub_type: str,
    image_by_story_key: dict[str, str],
) -> str:
    cards: list[str] = []
    for ch in children:
        path = ch["path"]
        name = html.escape(ch["name"] or Path(path).stem)
        href = html.escape(relative_href(hub_src, path))
        image, is_card_art = _child_image(src_root, path, hub_type, image_by_story_key)

        img_html = ""
        if image:
            if is_card_art:
                css_class, dims = (
                    ' class="child-hub-card-art"',
                    'width="500" height="700"',
                )
            else:
                css_class, dims = "", 'width="600" height="337"'
            img_html = f'<img{css_class} src="{html.escape(image)}" alt="" loading="lazy" {dims}>\n  '

        cards.append(
            f'<a class="sets-hub-card" href="{href}">\n'
            f"  {img_html}"
            f'  <div class="sets-hub-card-info">\n'
            f'    <span class="sets-hub-card-name">{name}</span>\n'
            f"  </div>\n"
            f"</a>"
        )

    inner = "\n".join(cards)
    return f'<div class="sets-hub-grid">\n{inner}\n</div>'


def _inject_hub(content: str, inner_html: str) -> str:
    """Replace or insert the child-hub block (idempotent)."""
    return replace_marked_block(content, MARK_START, MARK_END, inner_html)


# ---------------------------------------------------------------------------
# Main walk
# ---------------------------------------------------------------------------


def _inject_hubs(
    sections: list,
    src_root: Path,
    hub_children: dict[str, list[Chapter]],
    image_lookups: dict[str, dict[str, str]],
) -> None:
    for ch in iter_chapters(sections):
        path = chapter_path(ch)
        if not path:
            continue
        hub_type = _HUB_PAGES.get(path)
        if hub_type:
            image_by_story_key = image_lookups.get(hub_type, {})
            inner = _card_grid_html(path, src_root, hub_children.get(path, []), hub_type, image_by_story_key)
            ch["content"] = _inject_hub(ch.get("content") or "", inner)


def _process(items: list, src_root: Path) -> None:
    data_dir = src_root / "data"
    image_lookups = {
        "weapons": _load_story_card_images(data_dir, "weapons"),
        "equipment": _load_story_card_images(data_dir, "equipment"),
    }

    hub_children: dict[str, list[Chapter]] = {}
    _collect(items, hub_children)
    _inject_hubs(items, src_root, hub_children, image_lookups)


def main() -> None:
    run(_process)


if __name__ == "__main__":
    main()
