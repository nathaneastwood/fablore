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

# Card ids are not restricted to ``\w+``: a cycle is cited as ``EVO186/187/188``
# and ``non-set-cards.md`` cites a prototype as ``DEMO A-004``. The blank line is
# optional because that page is hand-curated and spaces its blocks out. The body
# runs to the next heading rather than the next blank line, because a verse spans
# stanzas — MST084 and ELE227 are multi-paragraph.
#
# The heading parts are line-bounded on purpose. Written with DOTALL so the body
# could span stanzas, ``.+?`` in the heading would also cross newlines, letting a
# match start at one card and run to a later card's closing paren, silently
# absorbing every block in between.
_BLOCK_RE = re.compile(r"^#### [^\n]+? - \([^)\n]+\)\n\n?(?P<text>[\s\S]+?)(?=\n#|\Z)", re.MULTILINE)

# A block whose body opens with this comment is protected — see ``keep_blocks``.
_KEEP_RE = re.compile(
    r"^#### (?P<name>[^\n]+?) - \((?P<ids>[^)\n]+)\)\n<!-- keep:[^\n]*-->\n[\s\S]+?(?=\n#|\Z)",
    re.MULTILINE,
)

# Upstream prints typographic punctuation on some cards (121 rows, concentrated in
# WTR/ARC/CRU/MON/EVR/UPR); every published flavour page carries the ASCII form.
# This is the transform that makes the two agree — not a stylistic preference.
_ASCII_PUNCTUATION = str.maketrans({"‘": "'", "’": "'", "“": '"', "”": '"'})


def _to_ascii_punctuation(text: str) -> str:
    """Replace typographic quotes and ellipses with their ASCII equivalents."""
    return str(text).translate(_ASCII_PUNCTUATION).replace("…", "...")


def _normalise(text: str) -> str:
    """Key for comparing two renderings of the same line across pages.

    Strips a leading ``keep`` comment: it is annotation, not flavour text, and
    leaving it in would stop a protected line from suppressing its own reprints.
    """
    body = re.sub(r"^\s*<!-- keep:[^\n]*-->\n", "", str(text))
    return " ".join(_to_ascii_punctuation(body).split())


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


def cite(ids: list[str]) -> str:
    """Render a card's printings as the citation shown in a heading.

    A common is printed once per pitch value, each with its own collector number
    but the same flavour text, so there is no single "the" id to quote. All of
    them are cited, sharing the set prefix::

        ["EVO186", "EVO187", "EVO188"] -> "EVO186/187/188"

    Where the printings of a cycle carry *different* lines they are separate
    entries and each cites only its own id — Everfest's ``Wax On`` is one quote
    split three ways across EVR050/051/052.
    """
    ordered = sorted(ids)
    if len(ordered) == 1:
        return ordered[0]
    prefix = re.match(r"^\D*", ordered[0]).group(0)
    tail = [i[len(prefix) :] if i.startswith(prefix) else i for i in ordered[1:]]
    return "/".join([ordered[0], *tail])


def keep_blocks(page: Path | str) -> dict[str, str]:
    """Return ``{card id: block}`` for blocks the page marks as protected.

    A block whose body opens with an HTML ``keep`` comment is reproduced verbatim
    on regeneration, whatever the upstream data says::

        #### Astral Assault - (OMN160)
        <!-- keep: card prints "Quazor"; upstream transcribes "Quazar" -->
        "In the Nebulus Rift, we have long battled ..." - Astrea Quazor

    This is the mechanism for the things upstream cannot express: a transcription
    error on its side, a card whose printed flavour it never recorded, and an
    editorial note added here. Every id cited in the heading maps to the block, so
    a kept block is still found after an id is added to a cycle.
    """
    path = Path(page)
    if not path.exists():
        return {}
    kept: dict[str, str] = {}
    for match in _KEEP_RE.finditer(path.read_text(encoding="utf-8")):
        block = match.group(0).strip()
        for cid in match.group("ids").split("/"):
            kept[cid.strip()] = block
    return kept


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
    # One row per distinct line, carrying every printing that shares it: a common
    # prints once per pitch value, and the heading cites all of them rather than
    # picking one arbitrarily. Grouped on the normalised text so that a stray
    # difference in whitespace does not split one line into two entries.
    df = df.sort_values(["name", "id"], kind="stable")
    df = (
        df.assign(_key=df["flavor_text"].map(_normalise))
        .groupby("_key", sort=False)
        .agg(
            set_id=("set_id", "first"),
            name=("name", "first"),
            flavor_text=("flavor_text", "first"),
            ids=("id", lambda s: sorted(set(s))),
        )
        .reset_index(drop=True)
    )
    df = df.assign(id=df["ids"].map(cite)).sort_values(["name", "id"], kind="stable").reset_index(drop=True)

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

    # Protected blocks win over anything derived from upstream, and a protected
    # block for a card upstream no longer carries is still published — that is the
    # only copy of a line transcribed from the physical card.
    kept = keep_blocks(out_file)
    rendered: list[tuple[str, str]] = []
    used: set[str] = set()
    for _, row in df.iterrows():
        block = next((kept[i] for i in row["ids"] if i in kept), None)
        if block is None:
            rendered.append((row["name"], "#### %s - (%s)\n%s" % (row["name"], row["id"], row["flavor_text"])))
        elif block not in used:
            # A card can carry several distinct lines against one id — ARC203's
            # couplet, FAB470's three — so more than one row may resolve to the
            # same protected block. It is published once.
            used.add(block)
            rendered.append((row["name"], block))
    for block in dict.fromkeys(kept.values()):
        if block not in used:
            rendered.append((_KEEP_RE.match(block).group("name"), block))
    rendered.sort(key=lambda r: r[0])

    heading = title if title is not None else set_name(set_id)
    body = "\n\n".join(block for _, block in rendered)
    # Single trailing newline — the end-of-file-fixer pre-commit hook would
    # otherwise rewrite the file underneath the commit.
    Path(out_file).write_text(("# %s\n\n%s" % (heading, body)).rstrip("\n") + "\n", encoding="utf-8")

    return df, dropped
