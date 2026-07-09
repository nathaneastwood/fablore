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
import json
import os
import re
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from card_name_slug import slugify_card_name_stem  # noqa: E402
from pipe_csv_io import read_pipe_csv  # noqa: E402

MARK_START = "<!-- fablore-child-hub:start -->"
MARK_END = "<!-- fablore-child-hub:end -->"

# Hub pages this preprocessor handles, keyed by src-relative path.
# mdBook rewrites README.md → index.md in the chapter path field, so both forms are listed.
_HUB_PAGES = {
    "weapons/armed-to-the-teeth.md": "weapons",
    "equipment/in-the-fires-of-the-forge.md": "equipment",
    "languages/intro.md": "languages",
    "other-characters/README.md": "plain",
    "other-characters/index.md": "plain",
    "data/data.md": "plain",
}

_IMG_SRC_RE = re.compile(r'<img\b[^>]*\bsrc="([^"]+)"', re.IGNORECASE)

Chapter = dict  # {"name": str, "path": str}


def _relative_href(from_src: str, to_src: str) -> str:
    return Path(os.path.relpath(Path(to_src), start=Path(from_src).parent)).as_posix()


# ---------------------------------------------------------------------------
# Pass 1: collect direct children of each hub page
# ---------------------------------------------------------------------------


def _collect(sections: list, hub_children: dict[str, list[Chapter]]) -> None:
    """Walk book sections; for each hub page, record its direct sub_items."""
    for item in sections:
        if not isinstance(item, dict) or "Chapter" not in item:
            continue
        ch = item["Chapter"]
        path_raw = (ch.get("path") or "").strip()
        sub_items = ch.get("sub_items") or []
        if path_raw:
            path = Path(path_raw).as_posix()
            if path in _HUB_PAGES:
                children: list[Chapter] = []
                for sub in sub_items:
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

        _collect(sub_items, hub_children)


# ---------------------------------------------------------------------------
# Image resolution
# ---------------------------------------------------------------------------


def _load_set_release_dates(data_dir: Path) -> dict[str, str]:
    _, sets_rows = read_pipe_csv(data_dir / "csv" / "sets.csv")
    return {
        row["SetId"]: row.get("InitialReleaseDate", "").strip()
        for row in sets_rows
        if row.get("SetId")
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
    if kind == "weapons":
        canonical_path = csv_dir / "weapons-canonical.csv"
        game_path = csv_dir / "weapons-game.csv"
        printings_path = csv_dir / "weapons-printings.csv"
        canonical_id_field = "CanonicalWeaponId"
        game_id_field = "WeaponGameId"
    else:
        canonical_path = csv_dir / "equipment-canonical.csv"
        game_path = csv_dir / "equipment-game.csv"
        printings_path = csv_dir / "equipment-printings.csv"
        canonical_id_field = "CanonicalEquipmentId"
        game_id_field = "EquipmentGameId"

    _, canonical_rows = read_pipe_csv(canonical_path)
    _, game_rows = read_pipe_csv(game_path)
    _, printings_rows = read_pipe_csv(printings_path)
    release_by_set_id = _load_set_release_dates(data_dir)

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


_ARTICLE_TOKENS = frozenset({"the", "a", "an"})


def _loose_slug_key(slug: str) -> str:
    """Collapse a slug to bare alphanumerics with article words dropped.

    Lets filename-vs-card-name mismatches resolve to the same CSV entry, e.g.
    the page ``talishar-lost-prince.md`` (card name missing "the") against
    canonical slug ``talishar-the-lost-prince``, or ``bolt-n-boots.md``
    (extra hyphen) against canonical slug ``boltn-boots``.
    """
    tokens = [
        t
        for t in re.split(r"[^a-z0-9]+", slug.lower())
        if t and t not in _ARTICLE_TOKENS
    ]
    return "".join(tokens)


def _resolve_image(child_slug: str, image_by_slug: dict[str, str]) -> str:
    image = image_by_slug.get(child_slug, "")
    if image:
        return image

    loose_key = _loose_slug_key(child_slug)
    for slug, url in image_by_slug.items():
        if _loose_slug_key(slug) == loose_key:
            return url
    return ""


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
    image_by_slug: dict[str, str],
) -> tuple[str, bool]:
    """Return ``(image_url, is_card_art)``.

    ``is_card_art`` is ``True`` for portrait card-printing images (resolved via
    CSV), which need different aspect-ratio handling than the landscape banner
    images used as a page ``<img>`` fallback.
    """
    if hub_type == "plain":
        return "", False

    if hub_type in ("weapons", "equipment"):
        stem = Path(child_path).stem
        slug = slugify_card_name_stem(stem.replace("-", " "))
        image = _resolve_image(slug, image_by_slug)
        if image:
            return image, True

    # languages hub, or weapons/equipment cards with no CSV match at all.
    return _page_img_fallback(src_root, child_path), False


# ---------------------------------------------------------------------------
# Pass 2: build HTML
# ---------------------------------------------------------------------------


def _card_grid_html(
    hub_src: str,
    src_root: Path,
    children: list[Chapter],
    hub_type: str,
    image_by_slug: dict[str, str],
) -> str:
    cards: list[str] = []
    for ch in children:
        path = ch["path"]
        name = html.escape(ch["name"] or Path(path).stem)
        href = html.escape(_relative_href(hub_src, path))
        image, is_card_art = _child_image(src_root, path, hub_type, image_by_slug)

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
    block = f"{MARK_START}\n{inner_html}\n{MARK_END}"
    if MARK_START in content and MARK_END in content:
        pre, _, rest = content.partition(MARK_START)
        _, _, post = rest.partition(MARK_END)
        return pre.rstrip() + "\n\n" + block + "\n\n" + post.lstrip()
    return content.rstrip() + "\n\n" + block + "\n"


# ---------------------------------------------------------------------------
# Main walk
# ---------------------------------------------------------------------------


def _inject_hubs(
    sections: list,
    src_root: Path,
    hub_children: dict[str, list[Chapter]],
    image_lookups: dict[str, dict[str, str]],
) -> None:
    for item in sections:
        if not isinstance(item, dict) or "Chapter" not in item:
            continue
        ch = item["Chapter"]
        path_raw = (ch.get("path") or "").strip()
        if path_raw:
            path = Path(path_raw).as_posix()
            hub_type = _HUB_PAGES.get(path)
            if hub_type:
                image_by_slug = image_lookups.get(hub_type, {})
                inner = _card_grid_html(
                    path, src_root, hub_children.get(path, []), hub_type, image_by_slug
                )
                ch["content"] = _inject_hub(ch.get("content") or "", inner)

        _inject_hubs(ch.get("sub_items") or [], src_root, hub_children, image_lookups)


def main() -> None:
    if len(sys.argv) >= 3 and sys.argv[1] == "supports":
        sys.exit(0)

    ctx, book = json.load(sys.stdin)
    root = Path(ctx["root"])
    book_cfg = (ctx.get("config") or {}).get("book") or {}
    src_rel = (book_cfg.get("src") or "src").strip() or "src"
    src_root = (root / src_rel).resolve()
    data_dir = src_root / "data"

    image_lookups = {
        "weapons": _load_card_image_lookup(data_dir, "weapons"),
        "equipment": _load_card_image_lookup(data_dir, "equipment"),
    }

    hub_children: dict[str, list[Chapter]] = {}
    _collect(book.get("items") or [], hub_children)
    _inject_hubs(book.get("items") or [], src_root, hub_children, image_lookups)

    json.dump(book, sys.stdout, ensure_ascii=False)


if __name__ == "__main__":
    main()
