"""One-off migration: repoint locations.csv rows to the current id-hash formula.

Historical ``locations.csv`` rows carry a ``LocationId`` assigned by a pre-SQLite
migration script that did not use today's ``registry_ids.location_id()`` formula.
``Database._upsert_locations`` recomputes the id fresh on every ``upsert_story()``
call, so a drifted row causes a silent duplicate insert instead of an update (see
``plans/location-id-hash-drift.md`` for full context).

This script computes the drifted ``(old_id -> new_id)`` mapping (reusing
``validate_data._check_location_id_hash_drift``'s detection logic), checks for
collisions among the newly-computed ids, then migrates each drifted row inside a
single transaction: insert/update the row under its new id, repoint every
``story_locations`` link from old id to new id, and delete the old id row.

Usage::

    python3 src/data/migrate_location_ids.py --dry-run   # preview only
    python3 src/data/migrate_location_ids.py              # apply

Run from the repo root. Always dry-run first.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from pipe_csv_io import read_pipe_csv  # noqa: E402
from registry_ids import assert_unique_ids, location_id  # noqa: E402
import db._queries as q  # noqa: E402
from db._domain import Database  # noqa: E402
from db._export import export_all  # noqa: E402

DATA = _SCRIPT_DIR
DB_PATH = DATA / "fablore.db"


def compute_drift_mapping(locations_path: Path) -> list[tuple[str, str, str]]:
    """Return ``(old_id, new_id, name)`` for every drifted ``locations.csv`` row.

    Mirrors ``validate_data._check_location_id_hash_drift``'s detection logic
    exactly, but returns the mapping rather than warning strings.
    """
    _, rows = read_pipe_csv(locations_path)
    drifted: list[tuple[str, str, str]] = []
    for row in rows:
        stored = (row.get("LocationId") or "").strip()
        name = (row.get("Name") or "").strip()
        region_id = (row.get("RegionId") or "").strip()
        if not stored or not name:
            continue
        computed = location_id(name, region_id)
        if stored != computed:
            drifted.append((stored, computed, name))
    return drifted


def check_collisions(mapping: list[tuple[str, str, str]]) -> None:
    """Raise ``ValueError`` if any two drifted rows compute to the same new id.

    Reuses ``registry_ids.assert_unique_ids`` — a genuine collision means two
    differently-tracked rows now hash to the same ``name|region_id`` and need
    a human merge decision, not an automatic one.
    """
    assert_unique_ids([(new_id, name) for _old_id, new_id, name in mapping], "location")


def migrate(db: Database, mapping: list[tuple[str, str, str]]) -> None:
    """Apply the migration inside one transaction.

    For each ``(old_id, new_id, name)`` pair: carry the old row's
    ``region_id``/``notes``/``lore_fragment`` over to the new id, repoint every
    ``story_locations`` row from old id to new id, then delete the old id row.
    """
    conn = db.conn
    with conn:
        for old_id, new_id, name in mapping:
            old_row = conn.execute(
                "SELECT region_id, notes, lore_fragment FROM locations WHERE location_id = ?",
                [old_id],
            ).fetchone()
            if old_row is None:
                raise ValueError(f"Expected row for old id {old_id!r} ({name!r}) not found")

            q.upsert_location(
                conn,
                location_id=new_id,
                name=name,
                region_id=old_row["region_id"],
                notes=old_row["notes"],
                lore_fragment=old_row["lore_fragment"],
            )
            conn.execute(
                "UPDATE story_locations SET location_id = ? WHERE location_id = ?",
                [new_id, old_id],
            )
            q.delete_entity_row(conn, "locations", "location_id", old_id)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the mapping and collision check result without writing anything.",
    )
    args = parser.parse_args()

    locations_csv = DATA / "csv/locations.csv"
    mapping = compute_drift_mapping(locations_csv)

    if not mapping:
        print("No location id-hash drift detected. Nothing to do.")
        return 0

    print(f"Found {len(mapping)} drifted location row(s):")
    for old_id, new_id, name in mapping:
        print(f"  {old_id} -> {new_id}  ({name!r})")

    try:
        check_collisions(mapping)
    except ValueError as exc:
        print(f"\nCOLLISION DETECTED — stopping without writing anything:\n{exc}")
        return 1
    print("\nNo collisions among newly-computed ids.")

    if args.dry_run:
        print("\nDry run — no changes made.")
        return 0

    db = Database(DB_PATH)
    migrate(db, mapping)
    export_all(db.conn, DATA)
    print(f"\nMigrated {len(mapping)} row(s) and re-exported CSVs.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
