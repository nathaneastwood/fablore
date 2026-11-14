"""Shared helpers for the ``mdbook_*.py`` preprocessors.

Stdlib only, like the preprocessors themselves, so ``mdbook build`` needs
nothing installed. Holds:

* the preprocessor protocol — ``supports <renderer>``, the
  ``(PreprocessorContext, Book)`` JSON on stdin, the ``Book`` JSON on stdout —
  as :func:`run` (or :func:`read_book` / :func:`write_book`), plus the
  configured ``src`` directory (:func:`book_src_root`);
* :func:`iter_chapters`, the pre-order walk over a book's chapters;
* :func:`relative_href` between two ``src``-relative markdown paths;
* the site-section registry (:data:`SECTIONS`), :func:`chapter_path` and
  :func:`arc_of` (which arc a page is in);
* the ``story-arcs.csv`` / ``sets.csv`` lookups the breadcrumb, hub, index and
  story-card preprocessors share;
* the marker literals one preprocessor writes and another looks for.
"""

from __future__ import annotations

import json
import re
import sys
from collections.abc import Callable, Iterator
from dataclasses import dataclass
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


def replace_marked_block(content: str, start: str, end: str, inner_html: str, *, pad_after: bool = True) -> str:
    """Replace the ``start``…``end`` block in ``content``, or append one (idempotent).

    A replaced block keeps a blank line before it; ``pad_after`` also puts one
    after it, folding whatever whitespace followed. An appended block goes
    after a blank line (none when ``content`` is blank) and ends with a newline.
    """
    block = f"{start}\n{inner_html}\n{end}"
    if start in content and end in content:
        pre, _, rest = content.partition(start)
        _, _, post = rest.partition(end)
        tail = "\n\n" + post.lstrip() if pad_after else post
        return pre.rstrip() + "\n\n" + block + tail
    sep = "\n\n" if content.strip() else ""
    return content.rstrip() + sep + block + "\n"


# ---------------------------------------------------------------------------
# Paths and files
# ---------------------------------------------------------------------------


@lru_cache(maxsize=None)
def relative_href(from_src: str, to_src: str) -> str:
    """POSIX relative URL from one ``src``-relative markdown path to another (keeps ``.md``).

    Pure string work: both paths are relative to the same root, so this is
    ``os.path.relpath`` without its two ``getcwd()`` calls per pair.
    """
    from_dir = [p for p in from_src.split("/") if p not in ("", ".")][:-1]
    to_parts = [p for p in to_src.split("/") if p not in ("", ".")]
    common = 0
    while common < min(len(from_dir), len(to_parts)) and from_dir[common] == to_parts[common]:
        common += 1
    return "/".join([".."] * (len(from_dir) - common) + to_parts[common:]) or "."


def md_to_html_url(md_path: str) -> str:
    """A markdown path or ``StoryKey`` (``a/b.md``) as the rendered page URL (``a/b.html``).

    mdBook renders every ``README.md`` as ``index.html``, so ``a/README.md``
    becomes ``a/index.html``; ``a/README.html`` does not exist.
    """
    key = md_path.strip()
    if not key.endswith(".md"):
        return key
    return normalise_page_path(key)[:-3] + ".html"


def normalise_page_path(path: str) -> str:
    """A ``src``-relative markdown path in POSIX form with a ``README.md`` page as ``index.md``.

    mdBook's index preprocessor renames every ``README.md`` chapter to
    ``index.md`` before ours run, and links to it must use that name, so this
    is the one spelling a page path is compared and linked under.
    """
    posix = Path(path).as_posix() if path else ""
    head, sep, name = posix.rpartition("/")
    return f"{head}{sep}index.md" if name == "README.md" else posix


def chapter_path(ch: dict) -> str:
    """A chapter's ``src``-relative path, normalised by :func:`normalise_page_path`; ``""`` when it has none."""
    return normalise_page_path((ch.get("path") or "").strip())


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
# Site sections
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Section:
    """One top-level folder of the book and what every preprocessor needs to know about it.

    ``key`` is both the folder under ``src/`` and the ``StoryType`` its pages
    are registered with. Optional fields are ``None``/``False`` for a section
    the feature does not cover.
    """

    key: str
    #: The section's landing page, as the source file under ``src/`` (``README.md``, not ``index.md``).
    hub: str | None = None
    #: The section's name in breadcrumbs and on the Sets index; ``None`` gives its pages no breadcrumb.
    label: str | None = None
    #: One page's type on story cards (singular where ``label`` is plural); ``None`` for a
    #: reference section, whose pages are reached through the entity they describe.
    story_label: str | None = None
    #: Pages group by story arc (set): ``<key>/<arc>/<page>.md``, or see ``arcs_in_filenames``.
    has_arcs: bool = False
    #: The arc is the page's filename stem (``flavour/monarch.md``), not a folder.
    arcs_in_filenames: bool = False
    #: Story cards show a word count and reading time.
    word_count: bool = True
    #: The ``entries/`` module that registers this section's stories; ``None`` when nothing is registered.
    entries_module: str | None = None
    #: How ``mdbook_child_hub`` draws the hub's child pages; ``None`` when it does not handle the hub.
    child_cards: str | None = None
    #: Pages besides the hub that get no breadcrumb (``fnmatch`` patterns).
    no_breadcrumb: tuple[str, ...] = ()

    @property
    def prefix(self) -> str:
        """The section's path prefix, ``<key>/``."""
        return f"{self.key}/"

    @property
    def narrative(self) -> bool:
        """True when its pages are stories rather than reference pages."""
        return self.story_label is not None

    @property
    def hub_page(self) -> str | None:
        """``hub`` as a chapter path (:func:`chapter_path` form), for matching and linking."""
        return normalise_page_path(self.hub) if self.hub else None


# Ordered as story types are listed to readers (Browse filters, graph inspector).
SECTIONS: tuple[Section, ...] = (
    Section(
        "main-story",
        hub="main-story/the-land-of-rathe.md",
        label="Main Story",
        story_label="Main Story",
        has_arcs=True,
        entries_module="main_story",
        no_breadcrumb=("main-story/README.md",),
    ),
    Section(
        "short-stories",
        hub="short-stories/README.md",
        label="Short Stories",
        story_label="Short Story",
        has_arcs=True,
        entries_module="short_stories",
    ),
    Section(
        "summaries",
        hub="summaries/README.md",
        label="Main Story Summaries",
        story_label="Summary",
        entries_module="summaries",
    ),
    Section(
        "world-of-rathe",
        hub="world-of-rathe/rathe.md",
        label="World of Rathe",
        story_label="World of Rathe",
        word_count=False,
        entries_module="world_of_rathe",
    ),
    Section(
        "flavour",
        hub="flavour/intro.md",
        label="Flavour Text",
        story_label="Flavour Text",
        has_arcs=True,
        arcs_in_filenames=True,
        entries_module="flavour",
    ),
    Section(
        "digital-tiles",
        hub="digital-tiles/README.md",
        label="Digital Tiles",
        story_label="Digital Tile",
        has_arcs=True,
        entries_module="digital_tiles",
    ),
    Section("spoilers", hub="spoilers/README.md", story_label="Spoiler"),
    Section("languages", hub="languages/intro.md", label="Languages", story_label="Language", child_cards="languages"),
    Section("sets", hub="sets/README.md", story_label="Set"),
    Section(
        "heroes-of-rathe",
        hub="heroes-of-rathe/heroes-of-rathe.md",
        label="Heroes of Rathe",
        word_count=False,
        entries_module="heroes",
        # Hero pages open with a full-width banner; a trail above it only crowds it.
        no_breadcrumb=(
            "heroes-of-rathe/professions-of-rathe.md",
            "heroes-of-rathe/other.md",
            "heroes-of-rathe/*-about.md",
        ),
    ),
    Section(
        "other-characters",
        hub="other-characters/README.md",
        label="Other Characters",
        entries_module="other_characters",
        child_cards="plain",
    ),
    Section(
        "weapons",
        hub="weapons/armed-to-the-teeth.md",
        label="Weapons",
        entries_module="weapons",
        child_cards="weapons",
    ),
    Section(
        "equipment",
        hub="equipment/in-the-fires-of-the-forge.md",
        label="Equipment",
        entries_module="equipment",
        child_cards="equipment",
    ),
    Section("archive", entries_module="archive"),
    Section("data", hub="data/data.md", child_cards="plain"),
)

SECTION_BY_KEY: dict[str, Section] = {s.key: s for s in SECTIONS}


def arc_of(path: str) -> tuple[str, str] | None:
    """``(section key, arc slug)`` for a page in an arc section, else ``None``.

    In a folder-per-arc section the arc is the folder one level down
    (``main-story/monarch/x.md`` at any depth, the arc folder's own
    ``index.md`` included). Under ``arcs_in_filenames`` (flavour) the arc is
    the filename stem of a direct child (``flavour/monarch.md``).

    This is the structural answer only: a section hub such as
    ``flavour/intro.md`` reads as an arc too, and nothing checks the slug
    against ``story-arcs.csv``. Callers filter for hubs, depth and sections.
    """
    parts = normalise_page_path(path).split("/")
    section = SECTION_BY_KEY.get(parts[0])
    if section is None or not section.has_arcs:
        return None
    if section.arcs_in_filenames:
        return (section.key, parts[1].removesuffix(".md")) if len(parts) == 2 else None
    return (section.key, parts[1]) if len(parts) >= 3 else None


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
