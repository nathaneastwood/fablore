"""Shared helpers for the ``mdbook_*.py`` preprocessors.

Stdlib only, like the preprocessors themselves, so ``mdbook build`` needs
nothing installed. Holds:

* the preprocessor protocol — ``supports <renderer>``, the
  ``(PreprocessorContext, Book)`` JSON on stdin, the ``Book`` JSON on stdout —
  as :func:`run` (or :func:`read_book` / :func:`write_book`), plus the
  configured ``src`` directory (:func:`book_src_root`);
* :func:`iter_chapters`, the pre-order walk over a book's chapters;
* :func:`relative_href` between two ``src``-relative markdown paths;
* the ``story-arcs.csv`` / ``sets.csv`` lookups the breadcrumb, hub, index and
  story-card preprocessors share;
* the marker literals one preprocessor writes and another looks for.
"""

from __future__ import annotations

import json
import os
import re
import sys
from collections.abc import Callable, Iterator
from datetime import datetime
from functools import lru_cache
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from pipe_csv_io import read_pipe_csv  # noqa: E402

# ---------------------------------------------------------------------------
# Cross-preprocessor markers
# ---------------------------------------------------------------------------

# The heading mdbook_related puts at the top of its Related Lore section;
# mdbook_story_meta and mdbook_graph_link (both run after it) look for it.
RELATED_LORE_H1 = '<h1 id="related-lore">Related Lore</h1>'

# mdbook_hero_meta closes a hero banner (which holds the H1) with this marker;
# mdbook_story_meta puts the story card after it.
HERO_BANNER_END = "<!-- fablore-hero-banner:end -->"


# ---------------------------------------------------------------------------
# Preprocessor protocol
# ---------------------------------------------------------------------------


def read_book() -> tuple[dict, dict]:
    """Answer ``supports <renderer>`` (exit 0), else return ``(ctx, book)`` from stdin."""
    if len(sys.argv) >= 3 and sys.argv[1] == "supports":
        sys.exit(0)
    ctx, book = json.load(sys.stdin)
    return ctx, book


def write_book(book: dict) -> None:
    """Print the (modified) ``Book`` JSON — the only thing a preprocessor may print on stdout."""
    json.dump(book, sys.stdout, ensure_ascii=False)


def book_src_root(ctx: dict) -> Path:
    """The book's ``src`` directory: ``[book] src`` from ``book.toml``, under the book root."""
    root = Path(ctx["root"])
    book_cfg = (ctx.get("config") or {}).get("book") or {}
    src_rel = (book_cfg.get("src") or "src").strip() or "src"
    return (root / src_rel).resolve()


def run(process: Callable[[list, Path], None]) -> None:
    """Run one preprocessor: ``process(items, src_root)`` mutates the book's items in place."""
    ctx, book = read_book()
    process(book.get("items") or [], book_src_root(ctx))
    write_book(book)


def iter_chapters(items: list) -> Iterator[dict]:
    """Every ``Chapter`` dict in ``items``, in pre-order (a chapter before its sub-items).

    Separators and part titles are skipped. A chapter's ``sub_items`` are read
    after it is yielded, so the caller may rewrite its ``content`` freely.
    """
    for item in items:
        if isinstance(item, dict) and "Chapter" in item:
            ch = item["Chapter"]
            yield ch
            yield from iter_chapters(ch.get("sub_items") or [])


# ---------------------------------------------------------------------------
# Paths and files
# ---------------------------------------------------------------------------


@lru_cache(maxsize=None)
def relative_href(from_src: str, to_src: str) -> str:
    """POSIX relative URL from one ``src``-relative markdown path to another (keeps ``.md``)."""
    return Path(os.path.relpath(Path(to_src), start=Path(from_src).parent)).as_posix()


def md_to_html_url(md_path: str) -> str:
    """A markdown path or ``StoryKey`` (``a/b.md``) as the rendered page URL (``a/b.html``).

    mdBook renders every ``README.md`` as ``index.html``, so ``a/README.md``
    becomes ``a/index.html``; ``a/README.html`` does not exist.
    """
    key = md_path.strip()
    if not key.endswith(".md"):
        return key
    head, sep, name = key.rpartition("/")
    if name == "README.md":
        name = "index.md"
    return f"{head}{sep}{name[:-3]}.html"


def read_rows(path: Path) -> list[dict[str, str]]:
    """The rows of a pipe CSV; ``[]`` when it is absent or empty."""
    return read_pipe_csv(path)[1]


_HERO_DIR = "heroes-of-rathe/"
_ABOUT_SUFFIX = "-about.md"


def is_hero_about_page(path: str) -> bool:
    """True for a hero page, ``heroes-of-rathe/*-about.md``."""
    posix = Path(path).as_posix()
    return posix.startswith(_HERO_DIR) and posix.endswith(_ABOUT_SUFFIX)


# ---------------------------------------------------------------------------
# Dates
# ---------------------------------------------------------------------------


def long_date(s: str) -> str | None:
    """``YYYY-MM-DD`` as ``D Month YYYY``, or ``None`` when it does not parse."""
    try:
        dt = datetime.strptime(s, "%Y-%m-%d")
    except ValueError:
        return None
    return f"{dt.day} {dt.strftime('%B %Y')}"


def format_date(date_str: str) -> str:
    """``YYYY-MM-DD`` (or an ISO datetime) as ``D Month YYYY``; the date part as given when it does not parse."""
    s = date_str.strip().split("T")[0]
    if not s:
        return ""
    return long_date(s) or s


# ---------------------------------------------------------------------------
# Small HTML pieces
# ---------------------------------------------------------------------------


def story_meta_item(icon: str, inner: str) -> str:
    """One icon-and-text entry of a ``story-meta`` information block."""
    return f'<span class="story-meta-item"><i class="{icon}" aria-hidden="true"></i> {inner}</span>'


# ---------------------------------------------------------------------------
# Arcs and sets (story-arcs.csv, sets.csv)
# ---------------------------------------------------------------------------


def load_arcs(data_dir: Path) -> dict[str, dict[str, str]]:
    """``story-arcs.csv`` rows keyed by arc ``Slug``."""
    return {r["Slug"]: r for r in read_rows(data_dir / "csv" / "story-arcs.csv") if r.get("Slug")}


def load_sets(data_dir: Path) -> dict[str, dict[str, str]]:
    """``sets.csv`` rows keyed by ``SetId``."""
    return {r["SetId"]: r for r in read_rows(data_dir / "csv" / "sets.csv") if r.get("SetId")}


def arc_display_name(slug: str, arcs: dict, sets: dict) -> str:
    """``DisplayName``, else the set's ``SetName``, else the slug prettified."""
    arc = arcs.get(slug, {})
    if arc.get("DisplayName"):
        return arc["DisplayName"]
    set_id = arc.get("SetId", "")
    if set_id and set_id in sets:
        return sets[set_id]["SetName"]
    # Fallback: prettify slug ("02-arcane-rising" → "Arcane Rising")
    name = re.sub(r"^\d+-", "", slug)
    return name.replace("-", " ").title()


def arc_raw_date(slug: str, arcs: dict, sets: dict) -> str:
    """Release date for an arc, as a raw ISO string.

    Prefers the upstream ``sets.csv`` date, falling back to the hand-maintained
    ``SortDate`` in ``story-arcs.csv``. Announced-but-unreleased sets have no
    upstream row yet (``create_sets_csv.py`` only sees what the game API
    publishes), so ``SortDate`` is how they carry a date until they do.
    """
    arc = arcs.get(slug, {})
    set_id = arc.get("SetId", "")
    upstream = sets.get(set_id, {}).get("InitialReleaseDate", "") if set_id else ""
    return upstream or arc.get("SortDate", "") or ""


def arc_release_date(slug: str, arcs: dict, sets: dict, *, sort_date_fallback: bool) -> str:
    """An arc's release date for display (``D Month YYYY``), or ``""``.

    With ``sort_date_fallback`` an arc with no upstream date shows its
    ``SortDate`` (the Sets index); without, it shows no date (the set hubs).
    """
    if sort_date_fallback:
        raw = arc_raw_date(slug, arcs, sets)
    else:
        set_id = arcs.get(slug, {}).get("SetId", "")
        raw = sets[set_id].get("InitialReleaseDate", "") if set_id and set_id in sets else ""
    if not raw:
        return ""
    return long_date(raw.split("T")[0]) or raw


def arc_image(slug: str, arcs: dict) -> str:
    return (arcs.get(slug) or {}).get("ImageLink", "")


def arc_id(slug: str) -> str:
    """Derive an HTML anchor ID from an arc slug."""
    name = re.sub(r"^\d+-", "", slug)
    return re.sub(r"[^a-z0-9-]", "-", name.lower()).strip("-")
