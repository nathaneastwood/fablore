"""Generate a set's flavour text page from the flesh-and-blood-cards data.

The page format is the one documented in ``README.md``::

    # Set Name

    #### Card Name - (XXX000)
    Flavour text

Two rules are enforced here rather than left to the caller, because both are
invisible in the output when they go wrong:

* **The H1 is the ``SetName`` from ``src/data/csv/sets.csv``.**
  ``create_stories_index.py`` infers a story's title from its first H1, so a
  hand-typed heading propagates a typo into ``stories.csv``.
* **Reprints are excluded.** ``intro.md`` promises that "any reprints are only
  included in their original set". A card can be reprinted with *new* flavour
  text (``Autumn's Touch`` is ``ELE128`` and again ``ROS046``, with a different
  line each time), so the comparison is on the flavour text and never on the
  card name. "Original set" is resolved by release date, which is why this
  module reads ``story-arcs.csv``: a page is only suppressed by a set that came
  out *before* it, so regenerating an existing page cannot strip lines that a
  later set went on to reprint.
"""

from __future__ import annotations

import re
from pathlib import Path

import numpy as np
import pandas as pd

_FLAVOUR_DIR = Path(__file__).resolve().parent
_CSV_DIR = _FLAVOUR_DIR.parent / "data" / "csv"
_SETS_CSV = _CSV_DIR / "sets.csv"
_STORY_ARCS_CSV = _CSV_DIR / "story-arcs.csv"

# Sorts after every real release date, so a page whose set cannot be dated never
# suppresses anything — an unknown date is surfaced at review, not acted on.
_UNDATED = "9999-99-99"

# Files in this directory that are not a set's flavour page. README.md matters:
# its worked example is a fenced ``#### Card Name - (XXX000)`` block, which the
# block pattern below would otherwise read as published flavour text.
_NOT_SET_PAGES = frozenset({"README.md", "intro.md", "xx-non-set-cards.md"})

_BLOCK_RE = re.compile(r"^#### .+? - \(\w+\)\n(?P<text>.+)$", re.MULTILINE)

# Upstream prints typographic punctuation on some cards (121 rows, concentrated in
# WTR/ARC/CRU/MON/EVR/UPR); every published flavour page carries the ASCII form.
# This is the transform that makes the two agree — not a stylistic preference.
_ASCII_PUNCTUATION = str.maketrans({"‘": "'", "’": "'", "“": '"', "”": '"'})


def _to_ascii_punctuation(text: str) -> str:
    """Replace typographic quotes and ellipses with their ASCII equivalents."""
    return str(text).translate(_ASCII_PUNCTUATION).replace("…", "...")


def _normalise(text: str) -> str:
    """Key for comparing two renderings of the same line across pages."""
    return " ".join(_to_ascii_punctuation(text).split())


def _sets() -> pd.DataFrame:
    return pd.read_csv(_SETS_CSV, sep="|", comment="#", dtype=str).fillna("")


def set_name(set_id: str) -> str:
    """Return the ``SetName`` for ``set_id`` from ``sets.csv``.

    Args:
        set_id: The set ID, e.g. "OUT" for "Outsiders".

    Returns:
        The set's name as published by the game API.

    Raises:
        KeyError: If the set ID is not in ``sets.csv``. Both that file and
            ``set-types.csv`` are auto-generated — regenerate them with
            ``create_sets_csv.py`` rather than hand-adding a row.
    """
    sets = _sets()
    match = sets.loc[sets["SetId"] == set_id, "SetName"]
    if match.empty:
        raise KeyError(f"{set_id!r} is not in {_SETS_CSV.name}; regenerate it with create_sets_csv.py")
    return str(match.iloc[0])


def release_date(set_id: str) -> str:
    """Return ``set_id``'s ISO release date, or ``_UNDATED`` if it has none."""
    sets = _sets()
    match = sets.loc[sets["SetId"] == set_id, "InitialReleaseDate"]
    date = str(match.iloc[0]).split("T")[0] if not match.empty else ""
    return date or _UNDATED


def page_dates(flavour_dir: Path | str | None = None) -> dict[str, str]:
    """Return each flavour page's slug mapped to the release date of its set.

    A flavour page's slug is its filename stem, which ``story-arcs.csv`` maps to
    a ``SetId`` — the same lookup ``mdbook_set_meta.py`` uses to attach the set
    metadata card. A page with no arc row, or an arc row with no ``SetId``, falls
    back to the arc's hand-maintained ``SortDate`` and then to ``_UNDATED``.
    """
    arcs = pd.read_csv(_STORY_ARCS_CSV, sep="|", comment="#", dtype=str).fillna("")
    directory = Path(flavour_dir) if flavour_dir else _FLAVOUR_DIR

    dates: dict[str, str] = {}
    for path in sorted(directory.glob("*.md")):
        if path.name in _NOT_SET_PAGES:
            continue
        row = arcs.loc[arcs["Slug"] == path.stem]
        set_id = str(row["SetId"].iloc[0]) if not row.empty else ""
        sort_date = str(row["SortDate"].iloc[0]) if not row.empty else ""
        dates[path.stem] = release_date(set_id) if set_id else (sort_date or _UNDATED)
    return dates


def published_flavour_text(flavour_dir: Path | str | None = None, exclude: str = "") -> dict[str, tuple[str, str]]:
    """Return flavour text already published, mapped to where it first appeared.

    Args:
        flavour_dir: Directory of flavour pages. Defaults to this file's directory.
        exclude: Filename to skip — pass the page being regenerated, or every
            line it already carries counts as its own reprint. Matched on the
            filename alone, so a scratch copy of the page excludes it too.

    Returns:
        Normalised flavour text → ``(slug, release_date)`` of the earliest page
        carrying it.
    """
    directory = Path(flavour_dir) if flavour_dir else _FLAVOUR_DIR
    skip = _NOT_SET_PAGES | ({exclude} if exclude else set())
    dates = page_dates(directory)

    published: dict[str, tuple[str, str]] = {}
    for path in sorted(directory.glob("*.md")):
        if path.name in skip:
            continue
        origin = (path.stem, dates.get(path.stem, _UNDATED))
        for match in _BLOCK_RE.finditer(path.read_text(encoding="utf-8")):
            text = _normalise(match.group("text"))
            if text not in published or origin[1] < published[text][1]:
                published[text] = origin
    return published


def create_flavour_md(
    set_id: str,
    card_flattened_path: str,
    out_file: str,
    title: str | None = None,
    drop_reprints: bool = True,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Create the flavour text markdown file.

    Args:
        set_id: The set ID, e.g. "OUT" for "Outsiders".
        card_flattened_path: The location of the "card-flattened.json" file in the flesh-and-blood-cards repo.
        out_file: The name of the file to create (including the .md extension).
        title: The H1 for the page. Defaults to the set's ``SetName`` from ``sets.csv``.
        drop_reprints: Whether to exclude flavour text already published on an
            *earlier* set's page. Pass ``False`` only to inspect the unfiltered set.

    Returns:
        A ``(kept, dropped)`` pair of pandas DataFrames with the set_id, id, name
        and flavour text. ``dropped`` additionally carries ``reprint_of``, the
        slug of the page that published the line first — report it, don't discard
        it. Note this function has a side effect which creates the markdown file.
    """
    df = pd.read_json(card_flattened_path)
    df = df[["set_id", "id", "name", "flavor_text"]]
    # Equality, not the substring test that ``query("set_id in '...'")`` performs:
    # every set ID is three characters today, so the two agree, but a truncated or
    # concatenated argument would silently match nothing or several sets.
    df = df[df["set_id"] == set_id]
    df = df.replace("", np.nan).dropna(subset=["flavor_text"])
    df = df.assign(flavor_text=df["flavor_text"].map(_to_ascii_punctuation))
    # Sorted by id as well as name, with a stable sort, so that where several
    # printings share a line the surviving card id is the lowest rather than
    # whatever order the upstream JSON happened to arrive in.
    df = df.sort_values(["name", "id"], kind="stable")
    df = df.drop_duplicates(subset=["flavor_text"])
    df = df.reset_index(drop=True)

    dropped = df.iloc[:0].assign(reprint_of=pd.Series(dtype=str))
    if drop_reprints:
        # Keyed on the filename, not the directory, so generating into a scratch
        # directory before review still excludes the page being regenerated.
        published = published_flavour_text(exclude=Path(out_file).name)
        this_date = release_date(set_id)
        origins = df["flavor_text"].map(lambda t: published.get(_normalise(t)))
        # Only an earlier set suppresses a line. Without the date test the
        # relationship is symmetric, and regenerating a page would strip whatever
        # a *later* set reprinted from it.
        is_reprint = origins.map(lambda o: o is not None and o[1] < this_date)
        dropped = df[is_reprint].assign(reprint_of=origins[is_reprint].map(lambda o: o[0])).reset_index(drop=True)
        df = df[~is_reprint].reset_index(drop=True)

    heading = title if title is not None else set_name(set_id)
    lines = [f"# {heading}", ""]
    for _, row in df.iterrows():
        lines.append("#### " + row["name"] + " - (" + row["id"] + ")")
        lines.append(row["flavor_text"])
        lines.append("")

    # Single trailing newline — the end-of-file-fixer pre-commit hook would
    # otherwise rewrite the file underneath the commit.
    Path(out_file).write_text("\n".join(lines).rstrip("\n") + "\n", encoding="utf-8")

    return df, dropped
