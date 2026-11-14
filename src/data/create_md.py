"""Generate Markdown table previews from selected pipe-delimited CSV files.

Writes ``*.md`` files under ``src/data/md/`` for human review (mirrors of lore
registries). Technical ``*Id`` columns are omitted from the tables. Each listed
CSV is rendered to a ``*.md`` with the same basename (``characters.md``,
``fauna.md``, ``flora.md``, etc.). Stdlib only.

Run from the repository root::

    python3 src/data/create_md.py
"""

from __future__ import annotations

from pathlib import Path

from generator_utils import md_table, write_text_if_changed
from pipe_csv_io import read_pipe_csv

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "src/data"

_LOCATIONS_FIRST = ("Name", "RegionName", "Notes")


def _region_names(csv_path: Path) -> dict[str, str]:
    """``{RegionId: RegionName}`` from the ``regions.csv`` beside ``csv_path``."""
    _, rows = read_pipe_csv(csv_path.parent / "regions.csv")
    return {r["RegionId"]: r["RegionName"] for r in rows if "RegionId" in r and "RegionName" in r}


def _is_registry_id(column: str) -> bool:
    """Technical primary/foreign key columns (names ending in ``Id`` or ``StoryKey``)."""
    return column.endswith("Id") or column.endswith("StoryKey")


def _columns(fieldnames: list[str], csv_path: Path, *, omit_id_columns: bool) -> list[str]:
    """The rendered column order for ``csv_path``.

    For ``locations.csv`` a ``RegionName`` column is appended (when the CSV has
    ``RegionId``), ``LoreFragment`` is dropped, and ``Name``, ``RegionName``,
    ``Notes`` lead.
    """
    columns = list(fieldnames)
    if not omit_id_columns:
        return columns
    is_locations = csv_path.name == "locations.csv"
    if is_locations and "RegionId" in columns and _region_names(csv_path):
        columns.append("RegionName")
    columns = [c for c in columns if not _is_registry_id(c)]
    if is_locations:
        columns = [c for c in columns if c != "LoreFragment"]
        head = [c for c in _LOCATIONS_FIRST if c in columns]
        columns = head + [c for c in columns if c not in head]
    return columns


def create_md_file(
    csv_path: Path,
    sort_column: str,
    *,
    output_md: Path | None = None,
    omit_id_columns: bool = True,
) -> None:
    """Sort ``csv_path`` by ``sort_column`` and write a Markdown table.

    The default output is ``csv_path`` with extension replaced by ``.md``. Pass
    ``output_md`` to write a different destination. A banner comment notes the
    file is generated from the CSV. The file is left untouched when its
    contents would not change.

    When ``omit_id_columns`` is True (default), columns whose names end with
    ``Id`` or ``StoryKey`` (e.g. ``CharacterId``, ``RegionId``) are omitted so
    the table is human-readable. For ``locations.csv``, ``RegionName`` is
    looked up in ``regions.csv`` before dropping ids.

    Args:
        csv_path: Pipe-delimited CSV under ``src/data/``.
        sort_column: Column name rows are sorted by (stable, by code point).
        output_md: Optional destination ``.md`` path (defaults to sibling of
            ``csv_path``).
        omit_id_columns: Strip id columns (and enrich locations with region
            names) before rendering.

    Raises:
        ValueError: If ``sort_column`` is not present in the CSV.
        OSError: If reading or writing fails.
    """
    fieldnames, rows = read_pipe_csv(csv_path)
    if sort_column not in fieldnames:
        raise ValueError(f"{csv_path}: no {sort_column!r} column to sort by")
    rows = sorted(rows, key=lambda r: r[sort_column] or "")
    columns = _columns(fieldnames, csv_path, omit_id_columns=omit_id_columns)
    if "RegionName" in columns and "RegionName" not in fieldnames:
        regions = _region_names(csv_path)
        rows = [{**r, "RegionName": regions.get(r.get("RegionId") or "", "")} for r in rows]
    table = md_table(columns, [[r.get(c) or "" for c in columns] for r in rows])
    out_path = output_md if output_md is not None else csv_path.with_suffix(".md")
    banner = "<!-- ### NOTE: This file should not be edited by hand. Please edit the .csv file. -->\n"
    write_text_if_changed(out_path, banner + table + "\n")


def main() -> None:
    """Regenerate Markdown mirrors for lore registry CSVs under ``src/data/``.

    Emits ``characters.md`` from ``characters.csv`` and one ``*.md`` per other
    listed CSV matching its basename.
    """
    jobs: tuple[tuple[Path, str, Path | None], ...] = (
        (DATA / "csv" / "characters.csv", "Name", DATA / "md" / "characters.md"),
        (DATA / "csv" / "fauna.csv", "Name", DATA / "md" / "fauna.md"),
        (DATA / "csv" / "flora.csv", "Name", DATA / "md" / "flora.md"),
        (
            DATA / "csv" / "food-and-drink.csv",
            "Name",
            DATA / "md" / "food-and-drink.md",
        ),
        (DATA / "csv" / "locations.csv", "Name", DATA / "md" / "locations.md"),
        (DATA / "csv" / "monsters.csv", "Name", DATA / "md" / "monsters.md"),
        (DATA / "csv" / "kinds.csv", "Name", DATA / "md" / "kinds.md"),
    )
    for csv_path, sort_col, out_md in jobs:
        create_md_file(csv_path, sort_col, output_md=out_md)


if __name__ == "__main__":
    main()
