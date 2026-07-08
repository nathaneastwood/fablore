"""Generate src/hints.json from the database and src/hints_supplement.json.

DB-backed entries (locations, monsters, fauna, flora) are written first.
The supplement is then merged on top: supplement fields override DB fields for
matching keys, and supplement-only keys are appended.

Run from the repository root:
    python src/data/generate_hints_json.py
"""

import json
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DB_PATH = ROOT / "src" / "data" / "fablore.db"
SUPPLEMENT_PATH = ROOT / "src" / "hints_supplement.json"
OUTPUT_PATH = ROOT / "src" / "hints.json"


def _region_map(conn: sqlite3.Connection) -> dict[str, str]:
    return {row[0]: row[1] for row in conn.execute("SELECT region_id, region_name FROM regions")}


def _key(name: str) -> str:
    """Derive a safe hint key from a DB name: strip apostrophes."""
    return name.replace("'", "")


def _entry_with_match(name: str, base: dict) -> dict:
    """Add a 'match' field if the safe key differs from the original name."""
    key = _key(name)
    if key != name:
        return {"match": name, **base}
    return base


def merge_supplement(hints: dict, supplement: dict) -> dict:
    """Merge supplement entries into DB-generated hints.

    Three cases:
    - Exact key match: supplement fields override DB fields.
    - Match-based merge: supplement key differs from DB key but its "match"
      field resolves (via _key()) to a DB key — the DB entry is replaced by
      the camelCase supplement key with fields merged.
    - No match: supplement entry is appended as-is.
    """
    match_to_db_key: dict[str, str] = {}
    for sup_key, value in supplement.items():
        if isinstance(value, dict):
            match = value.get("match")
            if match:
                db_key = _key(match) if isinstance(match, str) else _key(match[0])
                if db_key in hints:
                    match_to_db_key[sup_key] = db_key

    result = dict(hints)
    for key, value in supplement.items():
        if key in result and isinstance(value, dict) and isinstance(result[key], dict):
            result[key] = {**result[key], **value}
        elif key in match_to_db_key and isinstance(value, dict):
            db_key = match_to_db_key[key]
            merged = {**result[db_key], **value}
            del result[db_key]
            result[key] = merged
        else:
            result[key] = value
    return result


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
        hints[_key(row["name"])] = _entry_with_match(row["name"], entry)

    for row in conn.execute("SELECT name, description FROM monsters ORDER BY name"):
        if not row["description"]:
            continue
        hints[_key(row["name"])] = _entry_with_match(row["name"], {"type": "monster", "summary": row["description"]})

    for row in conn.execute("SELECT name, description FROM fauna ORDER BY name"):
        if not row["description"]:
            continue
        hints[_key(row["name"])] = _entry_with_match(row["name"], {"type": "fauna", "summary": row["description"]})

    for row in conn.execute("SELECT name, description FROM flora ORDER BY name"):
        if not row["description"]:
            continue
        hints[_key(row["name"])] = _entry_with_match(row["name"], {"type": "flora", "summary": row["description"]})

    conn.close()

    supplement: dict = {}
    if SUPPLEMENT_PATH.exists():
        with SUPPLEMENT_PATH.open(encoding="utf-8") as f:
            supplement = json.load(f)

    hints = merge_supplement(hints, supplement)

    with OUTPUT_PATH.open("w", encoding="utf-8") as f:
        json.dump(hints, f, ensure_ascii=False, indent=2)

    print(f"Wrote {len(hints)} entries to {OUTPUT_PATH.relative_to(ROOT)}", file=sys.stderr)


if __name__ == "__main__":
    generate()
