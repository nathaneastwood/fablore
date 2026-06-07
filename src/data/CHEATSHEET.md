# Data update cheatsheet

Quick reference for common edits. Full detail is in [README.md](README.md).

---

## Game data (sets, heroes, weapons, equipment)

Game data is derived from the sibling `flesh-and-blood-cards` repo (`../flesh-and-blood-cards/`).
**Never edit these CSVs by hand** — they carry an `# AUTO-GENERATED FILE` banner and will be overwritten on next regeneration.

| What changed | Script to run | Outputs |
|---|---|---|
| New set or set type | `python3 src/data/create_sets_csv.py` | `csv/sets.csv`, `csv/set-types.csv` |
| New hero / hero card | `python3 src/data/create_heroes_csv.py` | `csv/heroes-canonical.csv`, `heroes-game.csv`, `heroes-printings.csv`; also refreshes `classes.csv` / `talents.csv` |
| New weapon | `python3 src/data/create_weapons_csv.py` | `csv/weapons-canonical.csv`, `weapons-game.csv`, `weapons-printings.csv` |
| New equipment | `python3 src/data/create_equipment_csv.py` | `csv/equipment-canonical.csv`, `equipment-game.csv`, `equipment-printings.csv` |
| New class or talent | `python3 src/data/create_classes_talents_csv.py` | `csv/classes.csv`, `csv/talents.csv` |

After any of these, run:

```bash
python3 src/data/validate_data.py
```

### Adding a new set type

If `flesh-and-blood-cards` introduces a product line that `create_sets_csv.py` doesn't recognise:

1. Add a name match in `infer_set_type_label` (returns the type label, e.g. `"Silver Age Chapter Deck"`).
2. Add the label to `deck_release_types` or `booster_release_types` inside `infer_set_type_layer` as appropriate (or leave it out to fall through to `"Other"`).
3. Run `python3 src/data/create_sets_csv.py` to regenerate.

If you need to add a set type *before* the upstream data lands (e.g. to test set pages), compute the stable ID yourself and upsert it:

```python
import sys; sys.path.insert(0, "src/data")
from registry_ids import make_hash_id
from text_utils import normalize_name
# compute id
set_type_id = make_hash_id("TY", normalize_name("My New Deck"))
print(set_type_id)
```

Then add the row to `csv/set-types.csv` and upsert into the DB:

```python
import sqlite3, db._queries as q
conn = sqlite3.connect("src/data/fablore.db"); conn.row_factory = sqlite3.Row
q.upsert_set_type(conn, set_type_id="TY…", set_type="My New Deck", set_type_layer="Deck Releases")
conn.commit(); conn.close()
```

---

## Lore data (stories, NPCs, locations, etc.)

Lore tables are owned by the `Database` API. Always use it — never edit the `story-*.csv` junctions or registry CSVs by hand.

### Register or update a story

```python
import sys; sys.path.insert(0, "src/data")
from db import Database, NPCEntry, LocationEntry, NarratedVideoEntry

db = Database("src/data/fablore.db")
db.upsert_story(
    "src/main-story/set-name/story-slug.md",
    story_type="main-story",
    title="Story Title",
    heroes=["rhinar"],              # canonical slugs — see db.print_heroes()
    npcs=[NPCEntry("Ser Example", species="Human", status="Alive")],
    locations=[LocationEntry("The Citadel", region="Solana")],
    narrated_videos=[NarratedVideoEntry(author="LSS", source_link="https://…")],
)
```

Pass `dry_run=True` to preview without writing.

Entity lists use **replace semantics**: `None` = leave existing links; `[]` = clear all; `[...]` = replace with exactly this list.

### Remove a story

```python
db.remove_story("src/main-story/set-name/story-slug.md")
```

### Discovery helpers

```python
db.print_heroes()      # slug → display name
db.print_weapons()
db.print_equipment()
db.print_npcs()
db.print_locations()
db.print_regions()
```

### Re-scan all story files

```bash
python3 src/data/create_stories_index.py
```

Re-scans all lore roots under `src/`, upserts discovered stories (preserving existing titles and entity links), and parses narrated video blocks.

---

## Bulk CSV edits (escape hatch)

For bulk lore corrections that would be tedious via the API:

1. Edit the relevant `csv/` files directly.
2. Delete `src/data/fablore.db`.
3. The DB will reseed from your edited CSVs on next use.
4. Run `python3 src/data/validate_data.py` to confirm no FK errors.

---

## After any change

```bash
python3 src/data/validate_data.py   # check FK integrity
python3 src/data/create_md.py       # regenerate md/ markdown tables (needs requirements-data.txt)
```
