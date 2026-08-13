# Data update cheatsheet

Quick reference for common edits. Full detail is in [README.md](README.md).

---

## Can I edit this file?

The same entity exists as a Python constant, a database row, a CSV row and a Markdown table row. **Only the first is an input.** Editing any of the others is silently undone the next time a script runs.

| Path | Edit it? | Why |
|---|---|---|
| `entries/<type>.py` | **yes** | declares which page links to which entities |
| `entries/catalogue/*.py` | **yes** | defines what each entity *is* — the only place |
| `descriptions.py` | **yes** | the only writer of `notes` / `description` |
| `csv/story-arcs.csv` | **yes** | hand-maintained arc → set mapping |
| `csv/hero-card-name-aliases.csv` | **yes** | hand-maintained card-name aliases |
| `csv/reviewed-name-pairs.csv` | **yes** | your rulings on flagged near-duplicate names |
| `hero_overrides.py` | **yes** | curated hero data the card export lacks |
| `md/character-groups.md`, `data.md` | **yes** | editorial notes, no CSV source |
| everything else in `csv/` | **no** | written by the DB or a generator (`# AUTO-GENERATED` banner) |
| everything else in `md/` | **no** | `python3 src/data/create_md.py` |
| `fablore.db` | **no** | gitignored runtime artefact; delete it to reset |
| `src/hints.json` | **no** | `python3 src/data/generate_hints_json.py` |

Outside this folder, `src/hints_supplement.json` is hand-written.

**Delete `fablore.db` whenever you want a clean slate** — it reseeds from the committed CSVs on next open. Note that `Database.from_csv()` does *not* fully reset it: it reseeds the registry tables but leaves stale junction rows behind. Deleting the file is the only reliable reset.

---

## Lore data (stories, NPCs, locations, etc.)

### Register or update a story

A story's declaration lives in `src/data/entries/`, one module per story type, and `data-entry.py` runs them. Declarations **reference** entities; they never construct them.

```python
db.upsert_story(
    path="src/main-story/set-name/story-slug.md",
    story_type="main-story",
    title="Story Title",
    heroes=["rhinar"],                  # canonical slug — raises on an unknown one
    npcs=[npc.SER_EXAMPLE],             # from entries/catalogue/npcs.py
    locations=[loc.THE_CITADEL],
    regions=[reg.SOLANA],
    dry_run=True,
)
```

```bash
python3 src/data/data-entry.py --only src/main-story/set-name/story-slug.md  # preview one
python3 src/data/data-entry.py                                               # preview all
```

Set `dry_run=False` on the declaration, re-run to commit, then set it back to `True`. Pages with nothing to change print nothing; `--verbose` shows them.

Entity lists use **replace semantics**: `None` = leave existing links; `[]` = clear all; `[...]` = replace with exactly this list.

### Add a new entity

Add one constant to the matching module under `entries/catalogue/`, then reference it. **Search the module first** — a near-duplicate name creates a second row, it does not reuse the first.

```python
# entries/catalogue/locations.py, under its region's banner, alphabetically
THE_CITADEL = LocationEntry("The Citadel", region="Solana", lore_fragment="the-citadel")
```

Aliases in the section modules: `npc`, `loc`, `reg`, `mon`, `fauna`, `flora`, `food`.

**Always give a location its region, and a food/drink its kind.** `LocationId` hashes name *and* region; `FoodDrinkId` hashes name *and* kind. Adding the region later does not edit the row — it mints a second one and strands the first.

Writing `LocationEntry(...)` inside a section module is a `NameError` (the classes are not imported there) and fails `tests/test_data_entry.py`.

### Lore text for tooltips

Never set `notes=` or `description=` in a declaration or the catalogue. Add a call to `descriptions.py` instead:

```python
db.update_description("location", "The Citadel", "Seat of the Order of the Light.")
```

```bash
python3 src/data/descriptions.py            # real write, no dry-run
python3 src/data/generate_hints_json.py     # refresh tooltips
```

### Near-duplicate name warnings

`validate_data.py` reports pairs of similar names, because that is how one thing becomes two rows. It never merges anything — you decide.

- **Same thing?** Repoint the declarations to one name, apply them, then `db.delete_entity("location", "<old name>")` (it refuses while anything still links the row).
- **Different things?** Add `IdA|IdB|Note` to `csv/reviewed-name-pairs.csv` and the pair stops being reported.

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

## Game data (sets, heroes, weapons, equipment)

Game data is derived from the sibling `flesh-and-blood-cards` repo (`../flesh-and-blood-cards/`).
**Never edit these CSVs by hand** — they carry an `# AUTO-GENERATED FILE` banner and will be overwritten on next regeneration.

| What changed | Script to run | Outputs |
|---|---|---|
| New set or set type | `python3 src/data/create_sets_csv.py` | `csv/sets.csv`, `csv/set-types.csv` |
| New hero / hero card | `python3 src/data/create_heroes_csv.py` | `csv/heroes-canonical.csv`, `heroes-game.csv`, `heroes-printings.csv`, `heroes-ll.csv`; also refreshes `classes.csv` / `talents.csv` |
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

## Ad-hoc `Database` calls

The `Database` API still takes the dataclasses directly. This is fine for a throwaway script; it is **not** how you register a story, because a literal here and a literal in a declaration are two definitions of one entity:

```python
import sys; sys.path.insert(0, "src/data")
from db import Database, NPCEntry, LocationEntry, NarratedVideoEntry

db = Database("src/data/fablore.db")
db.upsert_story(
    "src/main-story/set-name/story-slug.md",
    story_type="main-story",
    title="Story Title",
    heroes=["rhinar"],
    npcs=[NPCEntry("Ser Example", species="Human", status="Alive")],
    locations=[LocationEntry("The Citadel", region="Solana")],
    narrated_videos=[NarratedVideoEntry(author="LSS", source_link="https://…")],
    dry_run=True,
)
```

---

## Bulk CSV edits (escape hatch)

For bulk lore corrections that would be tedious through the declarations:

1. Edit the relevant `csv/` files directly.
2. **Edit `entries/catalogue/` to match.** The catalogue is what the next `data-entry.py` run writes, so a CSV-only change is reverted by the next apply — and if you changed a name, a location's region or a food/drink's kind, the apply creates a *second* row instead of restoring the first.
3. Delete `src/data/fablore.db`.
4. The DB reseeds from your edited CSVs on next use.
5. Run `python3 src/data/validate_data.py` to confirm no FK errors.

---

## After any change

```bash
python3 src/data/validate_data.py        # FK integrity, plus near-duplicate name warnings
python3 src/data/create_md.py            # regenerate md/ tables (needs requirements-data.txt)
python3 src/data/generate_hints_json.py  # only if descriptions or lore CSVs changed
```

**Commit with the venv active.** `ensure-create-md-sync` calls `python3` while `link-checks` calls `python`; if those resolve to different interpreters one hook passes and the other fails on the same commit.
