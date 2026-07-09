"""Generate Markdown table previews from selected pipe-delimited CSV files.

Writes ``*.md`` files under ``src/data/`` for human review (mirrors of lore
registries). Technical ``*Id`` columns are omitted from the tables. Each listed
CSV is rendered to a sibling ``*.md`` with the same basename (``npcs.md``,
``fauna.md``, ``flora.md``, etc.). Requires:

    pip install numpy pandas py-markdown-table

Run from the repository root::

    python3 src/data/create_md.py
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from py_markdown_table.markdown_table import markdown_table

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "src/data"


def _read_pipe_df(path: Path) -> pd.DataFrame:
    """Load a pipe CSV, skipping ``#`` banner lines."""
    return pd.read_csv(path, delimiter="|", comment="#").replace({np.nan: ""})


def _merge_region_names_for_locations(df: pd.DataFrame, csv_path: Path) -> pd.DataFrame:
    """Add ``RegionName`` from ``regions.csv`` when rendering ``locations.csv``."""
    if csv_path.name != "locations.csv" or "RegionId" not in df.columns:
        return df
    reg_path = csv_path.parent / "regions.csv"
    if not reg_path.is_file():
        return df
    reg = _read_pipe_df(reg_path)
    if "RegionId" not in reg.columns or "RegionName" not in reg.columns:
        return df
    merged = df.merge(reg[["RegionId", "RegionName"]], on="RegionId", how="left")
    merged["RegionName"] = merged["RegionName"].fillna("")
    return merged


def _drop_registry_id_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Remove technical primary/foreign key columns (names ending in ``Id`` or ``StoryKey``)."""
    keep = [
        c
        for c in df.columns
        if not (isinstance(c, str) and (c.endswith("Id") or c.endswith("StoryKey")))
    ]
    return df[keep]


def _reorder_locations_columns(df: pd.DataFrame, csv_path: Path) -> pd.DataFrame:
    """Prefer ``Name``, ``RegionName``, ``Notes`` column order for locations."""
    if csv_path.name != "locations.csv":
        return df
    preferred = ("Name", "RegionName", "Notes", "LoreFragment")
    head = [c for c in preferred if c in df.columns]
    tail = [c for c in df.columns if c not in head]
    return df[head + tail] if head else df


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
    file is generated from the CSV.

    When ``omit_id_columns`` is True (default), columns whose names end with
    ``Id`` (e.g. ``CharacterId``, ``RegionId``) are omitted so the table is
    human-readable. For ``locations.csv``, ``RegionName`` is merged from
    ``regions.csv`` before dropping ids.

    Args:
        csv_path: Pipe-delimited CSV under ``src/data/``.
        sort_column: Column name used for ``DataFrame.sort_values``.
        output_md: Optional destination ``.md`` path (defaults to sibling of
            ``csv_path``).
        omit_id_columns: Strip ``*Id`` columns (and enrich locations with region
            names) before rendering.

    Raises:
        ValueError: If ``sort_column`` is not present in the CSV.
        OSError: If reading or writing fails.
    """
    df = _read_pipe_df(csv_path).sort_values(sort_column)
    if omit_id_columns:
        df = _merge_region_names_for_locations(df, csv_path)
        df = _drop_registry_id_columns(df)
        df = _reorder_locations_columns(df, csv_path)
    table = (
        markdown_table(df.to_dict(orient="records"))
        .set_params(row_sep="markdown", quote=False)
        .get_markdown()
    )
    out_path = output_md if output_md is not None else csv_path.with_suffix(".md")
    banner = (
        "<!-- ### NOTE: This file should not be edited by hand. "
        "Please edit the .csv file. -->\n"
    )
    out_path.write_text(banner + table + "\n", encoding="utf-8")


def main() -> None:
    """Regenerate Markdown mirrors for lore registry CSVs under ``src/data/``.

    Emits ``npcs.md`` from ``npcs.csv`` and one ``*.md`` per other listed CSV
    matching its basename.
    """
    jobs: tuple[tuple[Path, str, Path | None], ...] = (
        (DATA / "csv" / "npcs.csv", "Name", DATA / "md" / "npcs.md"),
        (DATA / "csv" / "fauna.csv", "Name", DATA / "md" / "fauna.md"),
        (DATA / "csv" / "flora.csv", "Name", DATA / "md" / "flora.md"),
        (
            DATA / "csv" / "food-and-drink.csv",
            "Name",
            DATA / "md" / "food-and-drink.md",
        ),
        (DATA / "csv" / "locations.csv", "Name", DATA / "md" / "locations.md"),
        (DATA / "csv" / "monsters.csv", "Name", DATA / "md" / "monsters.md"),
    )
    for csv_path, sort_col, out_md in jobs:
        create_md_file(csv_path, sort_col, output_md=out_md)


if __name__ == "__main__":
    main()
