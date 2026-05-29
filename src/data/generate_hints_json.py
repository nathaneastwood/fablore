"""Generate src/hints.json from the database and src/hints_supplement.json.

DB-backed entries (locations, monsters, fauna, flora) are written first.
The supplement is then merged on top: supplement fields override DB fields for
matching keys, and supplement-only keys are appended.

Run from the repository root:
    python src/data/generate_hints_json.py
"""

import json
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DB_PATH = ROOT / "src" / "data" / "fablore.db"
SUPPLEMENT_PATH = ROOT / "src" / "hints_supplement.json"
OUTPUT_PATH = ROOT / "src" / "hints.json"


def _region_map(conn: sqlite3.Connection) -> dict[str, str]:
    return {
        row[0]: row[1]
        for row in conn.execute("SELECT region_id, region_name FROM regions")
    }


def generate() -> None:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    hints: dict = {}
    regions = _region_map(conn)

    for row in conn.execute("SELECT name, notes, region_id FROM locations ORDER BY name"):
        if not row["notes"]:
            continue
        entry: dict = {"type": "location", "summary": row["notes"]}
        region = regions.get(row["region_id"], "")
        if region:
            entry["region"] = region
        hints[row["name"]] = entry

    for row in conn.execute("SELECT name, description FROM monsters ORDER BY name"):
        if not row["description"]:
            continue
        hints[row["name"]] = {"type": "monster", "summary": row["description"]}

    for row in conn.execute("SELECT name, description FROM fauna ORDER BY name"):
        if not row["description"]:
            continue
        hints[row["name"]] = {"type": "fauna", "summary": row["description"]}

    for row in conn.execute("SELECT name, description FROM flora ORDER BY name"):
        if not row["description"]:
            continue
        hints[row["name"]] = {"type": "flora", "summary": row["description"]}

    conn.close()

    supplement: dict = {}
    if SUPPLEMENT_PATH.exists():
        with SUPPLEMENT_PATH.open(encoding="utf-8") as f:
            supplement = json.load(f)

    for key, value in supplement.items():
        if key in hints and isinstance(value, dict) and isinstance(hints[key], dict):
            hints[key] = {**hints[key], **value}
        else:
            hints[key] = value

    with OUTPUT_PATH.open("w", encoding="utf-8") as f:
        json.dump(hints, f, ensure_ascii=False, indent=2)

    print(f"Wrote {len(hints)} entries to {OUTPUT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    generate()
