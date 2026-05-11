"""Pipe-delimited CSV read/write helpers with optional auto-generation banners.

Leading lines starting with ``#`` are treated as comments and skipped when
reading. Writers used by generators emit a first-line banner instructing not to
edit the file by hand.
"""

from __future__ import annotations

import csv
from io import StringIO
from pathlib import Path

# Regenerate hints passed to :func:`auto_gen_banner` for consistent tooling UX.
REGENERATE_CREATE_HEROES = "python3 src/data/create_heroes_csv.py"
REGENERATE_CREATE_SETS = "python3 src/data/create_sets_csv.py"
REGENERATE_CREATE_STORIES_INDEX = "python3 src/data/create_stories_index.py"
REGENERATE_CREATE_WEAPONS = "python3 src/data/create_weapons_csv.py"
REGENERATE_CREATE_EQUIPMENT = "python3 src/data/create_equipment_csv.py"
REGENERATE_CLASSES_TALENTS = "python3 src/data/create_classes_talents_csv.py"
REGENERATE_STORY_CLASS = "Use the Story class in src/data/story.py."
# Lore registry CSVs upserted by ``Story.link_npc``, ``link_monster``, ``link_fauna``,
# ``link_flora``, ``link_food_drink``, ``link_location`` (and ``regions.csv`` when
# ``link_location`` is given ``region_name``); ``npc_lore.write_npc_rows`` for NPCs.
REGENERATE_STORY_REGISTRY = (
    "Use the Story class in src/data/story.py (Story.link_npc / link_monster / link_fauna / "
    "link_flora / link_food_drink / link_location — link_location upserts regions.csv "
    "when region_name is set)."
)
# Banner hint for ``story-*.csv`` junction files (written by ``story.py`` and first-run
# ``create_stories_index.ensure_junction_headers``).
REGENERATE_STORY_JUNCTIONS = (
    "Use the Story class in src/data/story.py (Story.link_* / Story.remove)."
)
REGENERATE_HEROES_CANONICAL = (
    "Story.add_canonical_hero (src/data/story.py) or python3 src/data/create_heroes_csv.py"
)


def auto_gen_banner(regenerate_command: str) -> str:
    """Return one CSV comment line (starts with ``#``).

    Args:
        regenerate_command: Short instruction such as a shell command or pointer
            to the Story API.

    Returns:
        Single line ending with newline, suitable as the first bytes of a CSV file.
    """
    return (
        "# AUTO-GENERATED FILE — do not edit by hand. "
        f"Regenerate with: {regenerate_command}\n"
    )


def strip_leading_hash_comments(text: str) -> str:
    """Remove consecutive ``#`` lines from the start of file text.

    Args:
        text: Full file contents (UTF-8).

    Returns:
        Remaining text; may be empty if only comments were present.
    """
    lines = text.splitlines()
    start = 0
    while start < len(lines) and lines[start].startswith("#"):
        start += 1
    if start >= len(lines):
        return ""
    return "\n".join(lines[start:]) + "\n"


def read_pipe_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    """Load a pipe-delimited CSV, skipping leading ``#`` comment lines.

    Args:
        path: CSV path.

    Returns:
        ``(fieldnames, rows)``. Missing files yield ``([], [])``.
    """
    if not path.is_file():
        return [], []
    raw = path.read_text(encoding="utf-8")
    body = strip_leading_hash_comments(raw)
    if not body.strip():
        return [], []
    reader = csv.DictReader(StringIO(body), delimiter="|")
    fieldnames = list(reader.fieldnames or [])
    rows = list(reader)
    return fieldnames, rows


def write_pipe_csv_autogen(
    path: Path,
    fieldnames: list[str],
    rows: list[dict[str, str]],
    *,
    regenerate_command: str,
) -> None:
    """Write a pipe-delimited CSV with an auto-generation banner line.

    Args:
        path: Destination path.
        fieldnames: Header column order.
        rows: Data rows (dicts keyed by field names).
        regenerate_command: Short regenerate instruction for the banner.
    """
    with path.open("w", newline="", encoding="utf-8") as f:
        f.write(auto_gen_banner(regenerate_command))
        writer = csv.DictWriter(
            f,
            fieldnames=fieldnames,
            delimiter="|",
            lineterminator="\n",
            extrasaction="ignore",
        )
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in fieldnames})


def write_pipe_matrix_autogen(
    path: Path,
    header_row: list[str],
    data_rows: list[list[str] | tuple[str, ...]],
    *,
    regenerate_command: str,
) -> None:
    """Write a pipe-delimited CSV (matrix rows) with an auto-generation banner.

    Args:
        path: Destination path.
        header_row: Single header row.
        data_rows: Body rows as sequences of strings.
        regenerate_command: Short regenerate instruction for the banner.
    """
    with path.open("w", newline="", encoding="utf-8") as f:
        f.write(auto_gen_banner(regenerate_command))
        writer = csv.writer(f, delimiter="|", lineterminator="\n")
        writer.writerow(header_row)
        writer.writerows(data_rows)
