<a name="readme-top"></a>

# Data

This folder contains the data of the characters and locations of Rathe.

This README documents how to run generators and `story.py`, and includes the full CSV schema map under [Data schemas and CSV map](#data-schemas-and-csv-map). Markdown lore under `src/` is not tabular data. Automated pytest lives in the repository root [`tests/`](../../tests/) (run from the repo root after [`requirements-dev.txt`](../../requirements-dev.txt), which includes [`requirements-data.txt`](../../requirements-data.txt) for `create_md.py` and the pre-commit markdown sync hook).

<p align="right">
(<a href="#readme-top">back to top</a>)
</p>

## Stories and junctions (`story.py`)

Use the `Story` class in `story.py` to register a markdown file in `stories.csv` and link NPCs, heroes, monsters, fauna, flora, food & drink, locations, weapons, and equipment to that story. Instantiate with the path to the story under `src/`, a `StoryType` (first folder segment, e.g. `main-story`), and a `Title`. If the `StoryKey` (path relative to `src/`) is missing from `stories.csv`, a row is added with a deterministic `StoryId`; otherwise the existing row is refreshed and junction ids for that story are loaded into `story.links`.

**`StoryKey` vs `StoryId`:** `StoryKey` is the repo-relative path to the Markdown file (handy for links and humans). `StoryId` is the stable primary key (`ST` + hash of the path). Every `story-*.csv` edge uses `StoryId` only. If you reorganize `src/`, `StoryId` stays the same only while the path string (and thus the hash input) is unchanged; moving a file implies new `StoryKey`/`StoryId` unless you migrate rows deliberately. Site preprocessors, reports, or downstream joins should key on `StoryId` and treat `StoryKey` as a derived display or URL path, not as the relational join column.

Example (from repo root, Python):

```python
from pathlib import Path
import sys
sys.path.insert(0, "src/data")
from story import Story

s = Story(
    Path("src/main-story/21-omens-of-the-third-age/omens-in-the-sky.md"),
    story_type="main-story",
    title="Omens in the Sky",
)
s.link_npc("Captain Example", species="Human", status="Alive")
s.link_hero(canonical_slug="boltyn")
s.link_monster("Puppeteer", description="…")
s.link_weapon(canonical_slug="nebula-blade")
s.validate()
```

`npcs.csv` holds `CharacterId`, `Name`, `Species`, `Status` only; `story-npcs.csv` holds edges. `link_npc` refuses playable hero names (same rules as before).

Heroes: `link_hero(canonical_slug=...)` links an existing canonical row; `add_canonical_hero(slug, display_name)` inserts into `heroes-canonical.csv` (does not run `create_heroes_csv.py`—regenerate game rows separately when card data matters).

Locations: `link_location(name, region_id="", …)` — omit both `region_id` and `region_name` when the region is unknown (empty `RegionId` on the location). Pass `region_name=` (and optional `world_of_rathe_story_key=`) to upsert `regions.csv`; pass `region_id=` alone only when that id already exists in `regions.csv`.

Weapons / equipment: `link_weapon(canonical_slug=...)` and `link_equipment(canonical_slug=...)` mirror `link_hero`: the slug must exist in `weapons-canonical.csv` / `equipment-canonical.csv` (from `create_weapons_csv.py` / `create_equipment_csv.py`). Junction rows store `CanonicalWeaponId` / `CanonicalEquipmentId`, not markdown paths. See [Heroes, weapons, and equipment: how it fits together](#heroes-weapons-and-equipment-how-it-fits-together) below.

For bulk edits you can still edit CSVs directly, then run `validate_data.py`.

Story bootstrap: `python3 src/data/create_stories_index.py` rescans configured roots under `src/` (see `STORY_ROOTS` in `create_stories_index.py`), overwrites `stories.csv`, and creates any missing `story-*.csv` files with banner + header only (it does not wipe populated junctions). A `Title` in the existing `stories.csv` is kept only when it differs from the auto filename-stem title (so manual overrides survive); otherwise titles are inferred from each file's first `#` H1 or title-cased from the filename stem.

<a name="heroes-weapons-and-equipment-how-it-fits-together"></a>

### Heroes, weapons, and equipment: how it fits together

The same three-layer idea applies to heroes, weapons, and equipment:

| Layer | What it is | Heroes | Weapons | Equipment |
|-------|----------------|--------|---------|-----------|
| Game (cards) | Rows derived from the sibling `flesh-and-blood-cards` export (`card.csv`, printings, sets). Stats, card names, which sets a card appears in. | `heroes-canonical.csv`, `heroes-game.csv`, `heroes-printings.csv` | `weapons-canonical.csv`, `weapons-game.csv`, `weapons-printings.csv` | `equipment-canonical.csv`, `equipment-game.csv`, `equipment-printings.csv` |
| Dedicated lore | Markdown under `src/` that focuses on that identity (world-building, art, prose). Not emitted from the card generators. | e.g. `src/heroes-of-rathe/` | e.g. `src/weapons/` | e.g. `src/equipment/` |
| Story appearances | Any tracked narrative `*.md` (e.g. `src/main-story/`) registered in `stories.csv`. Junction rows record “this story mentions that entity.” | `story-heroes.csv`: `StoryId` + `CanonicalId` → `heroes-canonical.csv` | `story-weapons.csv`: `StoryId` + `CanonicalWeaponId` → `weapons-canonical.csv` | `story-equipment.csv`: `StoryId` + `CanonicalEquipmentId` → `equipment-canonical.csv` |

Unified link model: `Story.link_hero`, `link_weapon`, and `link_equipment` all take a `canonical_slug` that must match a row in the corresponding canonical CSV. The junction stores the stable canonical id (`CanonicalId`, `CanonicalWeaponId`, `CanonicalEquipmentId`), which is also the foreign key used by `heroes-game.csv`, `weapons-game.csv`, and `equipment-game.csv`. Dedicated lore markdown (`heroes-of-rathe/`, `weapons/`, `equipment/`) stays separate: filenames and slugs usually align (e.g. `nebula-blade` ↔ `src/weapons/nebula-blade.md`), but the data join is always through the canonical tables.

Validation: `validate_data.py` checks that story junction ids resolve to canonical rows (and runs the usual game FK checks). For heroes it also replays `create_heroes_csv` name→slug resolution so each `heroes-game.csv` `CardName` maps to that row's `CanonicalId` (display `CanonicalHero` may still differ from the full printed title). Each `stories.csv` `StoryType` must be one of `validate_data.ALLOWED_STORY_TYPES` (top-level lore folders under `src/`). It does not assert that a matching `src/weapons/…md` file exists—keep slug and lore paths aligned by convention.

For the full table index and FK overview, see [Data schemas and CSV map](#data-schemas-and-csv-map) below.

<p align="right">
(<a href="#readme-top">back to top</a>)
</p>

## Locations

The locations file highlights the location's region; any special notes; and any sections of the Main Story they are mentioned in.

<p align="right">
(<a href="#readme-top">back to top</a>)
</p>

## Editing the Data

Any edits to the data should be made in the `.csv` file as opposed to the `.md` file. Instructions on how to create the `.md` file can be found [here](#creating-the-md-files).

<p align="right">
(<a href="#readme-top">back to top</a>)
</p>

## Creating the .md Files

`create_md.py` writes Markdown tables next to selected lore CSVs for browsing in GitHub or editors. `npcs.md`, `fauna.md`, `flora.md`, `food-and-drink.md`, `locations.md`, and `monsters.md` each match their CSV basenames. Registry columns whose names end in `Id` are left out of the markdown; `locations.md` includes `RegionName` (from `regions.csv`) instead of `RegionId`.

You can use the Python code found in `create_md.py`. Dependencies are listed in [`requirements-data.txt`](../../requirements-data.txt) at the repo root (also pulled in by [`requirements-dev.txt`](../../requirements-dev.txt) for pytest and pre-commit). Install with:

```bash
pip install -r requirements-data.txt
```

Then you can run the file from the command line to regenerate the mirror `.md` files.

```bash
python3 src/data/create_md.py
```

If you use pre-commit (see `.pre-commit-config.yaml`), the `ensure-create-md-sync` hook runs when relevant `src/data` CSVs or mirror `.md` files change: it executes `create_md.py` and blocks the commit if the regenerated files do not match what is staged. Install `requirements-dev.txt` (or at least `requirements-data.txt`) first so those packages are available.

## Creating the Heroes CSV

The heroes datasets are generated from hero pages and card data.

```bash
python3 src/data/create_heroes_csv.py
```

This script derives:

- `src/data/heroes-canonical.csv` (one row per canonical hero grouping):
  - `CanonicalId` (recomputed from `CanonicalSlug` when you run `create_heroes_csv.py`), `CanonicalSlug`, `CanonicalHero` (curated display label; often shorter than printed `CardName` on cards). `validate_data.py` ensures each `heroes-game.csv` `CardName` still resolves to the row's `CanonicalId` using the same slug/alias rules as the generator.
- `src/data/heroes-game.csv` (one row per hero card line, including adult/young):
  - Link keys: `HeroGameId` (row id, `HG` + hash), `CanonicalId` (foreign key)
  - Game fields: `CardName` (full printed hero card title from upstream data), `ClassIds`, `TalentIds`, `Health`, `Intellect`, `AbilityText`, `Types`
  - `CardName` must match the upstream card dataset ``Name`` field. If you ever inferred it from older ``Variant``-plus-canonical data, re-run ``create_heroes_csv.py`` against the official ``card.csv`` so titles stay accurate (e.g. ``Ser Boltyn``, nicknames in quotes).
  - Generated IDs are deterministic hashes from stable source identifiers (not row position), so adding new rows does not renumber existing IDs. This includes `CanonicalId` (hashed from `CanonicalSlug`).
  - Which sets a card appears in are listed only in `heroes-printings.csv` (`SetId` per printing).
  - The file is pipe-delimited (`|`). Two pipes in a row (`||`) are not stray slashes: they mark two consecutive empty columns (the delimiter between blank fields).
- `src/data/classes.csv` (class reference table, shared with weapons / equipment generators):
  - `ClassId`, `ClassName`
  - Regenerate with ``python3 src/data/create_classes_talents_csv.py`` (scans hero, weapon, and non-weapon equipment rows in ``card.csv``). Running any of ``create_heroes_csv.py``, ``create_weapons_csv.py``, or ``create_equipment_csv.py`` refreshes these files too.
- `src/data/talents.csv` (talent reference table, shared):
  - `TalentId`, `TalentName`
- `src/data/heroes-printings.csv` (one row per printing/edition):
  - `HeroGameId` (foreign key to `heroes-game.csv`)
  - `SetId`, `CardId` (set-specific printing code from upstream card data), `Rarity`

Downstream site code does not read `heroes-game.csv` today; there are no remaining references to the removed ``Variant`` column outside this README and generator comments.

## Creating the Weapons CSV

Weapon card lines (any ``Types`` token containing the word weapon, e.g. ``2H Weapon``) are extracted from the same upstream ``card.csv`` as heroes.

```bash
python3 src/data/create_weapons_csv.py
```

This script writes:

- `src/data/weapons-canonical.csv` — one row per weapon identity (hyphen slug from the full printed ``Name``)
- `src/data/weapons-game.csv` — one row per matching weapon card (`WeaponGameId`, `CanonicalWeaponId`, `Cost`, `Power`, `AbilityText`, etc.)
- Refreshes shared `classes.csv` / `talents.csv` from the full ``card.csv`` (same union as `create_classes_talents_csv.py`; ``CL`` / ``TL`` ids match `create_heroes_csv.py`).
- `src/data/weapons-printings.csv` — printings keyed by `WeaponGameId`

## Creating the Equipment CSV

Slot equipment (any ``Types`` token containing equipment but not weapon) uses the same upstream ``card.csv``. Hybrid cards such as ``Warrior, Weapon, Equipment, Sword`` are listed only in the weapons outputs.

```bash
python3 src/data/create_equipment_csv.py
```

This script writes:

- `src/data/equipment-canonical.csv` — one row per equipment identity (hyphen slug from the full printed ``Name``)
- `src/data/equipment-game.csv` — one row per qualifying equipment card (`EquipmentGameId`, `CanonicalEquipmentId`, `Cost`, `Defense`, `AbilityText`, etc.)
- Refreshes shared `classes.csv` / `talents.csv` from the full ``card.csv`` (same union as `create_classes_talents_csv.py`).
- `src/data/equipment-printings.csv` — printings keyed by `EquipmentGameId`

<a name="data-schemas-and-csv-map"></a>

## Data schemas and CSV map

The subsections below map pipe-delimited data under `src/data/`: where each table comes from, how it is produced, and how tables relate.

### Working rule: do not edit machine-owned CSVs by hand

All CSVs that carry an `# AUTO-GENERATED FILE — do not edit by hand` banner (and every `story-*.csv` junction) are owned by generators or by `story.py`. Do not change rows in an editor—your edit will be overwritten the next time someone runs the correct script or `Story` API, and you risk silent drift from card exports or lore links.

- Game tables → regenerate from the `flesh-and-blood-cards` sibling repo using the `create_*_csv.py` scripts (and `validate_data.py` after).
- Lore tables → update only through `story.py` (`Story` constructor, `Story.link_*`, `Story.remove`) or `create_stories_index.py` for a full `stories.csv` rescan.
- Editorial-only files (`character-groups.md`, `data.md`, and any free-form notes) are the exception: they are not validated as registries.

Convention: fields are pipe (`|`) delimited. Leading lines starting with `#` are comments (including the autogen banner); readers skip them via `pipe_csv_io.read_pipe_csv` (pipe files) or `tab_csv_io.read_tab_csv` (upstream tab files only).

### Two sources of truth

#### 1. Game (card) data — from `flesh-and-blood-cards`

The flesh-and-blood-cards repository (expected as a sibling directory of this repo: `../flesh-and-blood-cards/`) holds official tab-separated card and set exports (e.g. `card.csv`, `card-printing.csv`, `set.csv`, `set-printing.csv`, English `set*.csv` under `csvs/english/`).

This `fablore` repo does not author card rows by hand. Generators read those exports with `tab_csv_io.read_tab_csv`, normalize to pipe CSVs under `src/data/`, and assign stable ids. After any generator run:

```bash
python3 src/data/validate_data.py
```

| Concern | Scripts (run from repo root) | Primary outputs |
|--------|------------------------------|-------------------|
| Sets & set types | `python3 src/data/create_sets_csv.py` | `sets.csv`, `set-types.csv` |
| Shared class & talent tokens | `python3 src/data/create_classes_talents_csv.py` | `classes.csv`, `talents.csv` (from `Types` on `card.csv`) |
| Heroes (canonical + game + printings) | `python3 src/data/create_heroes_csv.py` | `heroes-canonical.csv` (canonical rows from slugs + card data), `heroes-game.csv`, `heroes-printings.csv`; also refreshes `classes.csv` / `talents.csv` |
| Weapons | `python3 src/data/create_weapons_csv.py` | `weapons-canonical.csv`, `weapons-game.csv`, `weapons-printings.csv`; also refreshes `classes.csv` / `talents.csv` |
| Equipment | `python3 src/data/create_equipment_csv.py` | `equipment-canonical.csv`, `equipment-game.csv`, `equipment-printings.csv`; also refreshes `classes.csv` / `talents.csv` |

Foreign keys (game side, simplified):

- `sets.csv` → `set-types.csv` (`SetTypeId`).
- `heroes-game.csv` → `heroes-canonical.csv` (`CanonicalId`); `heroes-printings.csv` → `heroes-game.csv` + `sets.csv`.
- `weapons-game.csv` → `weapons-canonical.csv`; `weapons-printings.csv` → `weapons-game.csv` + `sets.csv`.
- `equipment-game.csv` → `equipment-canonical.csv`; `equipment-printings.csv` → `equipment-game.csv` + `sets.csv`.
- `classes.csv` / `talents.csv` are shared token registries referenced from hero, weapon, and equipment game rows (`ClassIds`, `TalentIds`).

Heroes canonical (cross-over): `heroes-canonical.csv` is driven mainly by `create_heroes_csv.py` from card data, but new canonical rows can also be inserted with `Story.add_canonical_hero` before a card exists. Treat it like game-adjacent registry data: never hand-edit; use the script or the `Story` API, then re-run `create_heroes_csv.py` when you need game rows refreshed.

#### 2. Lore (narrative) data — generated inside `fablore`

Lore CSVs tie markdown articles under `src/` to entities (NPCs, places, creatures, etc.). They are not produced from `flesh-and-blood-cards` exports.

| Layer | Role | How it is written |
|-------|------|-------------------|
| Story spine | `stories.csv` — one row per tracked `*.md` story file (`StoryKey`, `StoryId`, `StoryType`, `Title`) | `create_stories_index.py` rescans configured roots and rewrites `stories.csv` (keeps `Title` when it is not the auto stem placeholder; otherwise first H1 or title-cased filename). Constructing `Story(...)` in `story.py` upserts one row for a single file. |
| Story ↔ entity junctions | `story-npcs.csv`, `story-heroes.csv`, `story-locations.csv`, `story-monsters.csv`, `story-fauna.csv`, `story-flora.csv`, `story-food-drink.csv`, `story-weapons.csv`, `story-equipment.csv` | Each row is `StoryId` plus a registry key (`CharacterId`, `CanonicalId`, `LocationId`, `CanonicalWeaponId`, `CanonicalEquipmentId`, etc.). `Story.link_*` appends/merges edges; `Story.remove` strips all edges for a story. `create_stories_index.py` seeds header-only junction files on first run. |
| Lore entity registries | `npcs.csv`, `monsters.csv`, `fauna.csv`, `flora.csv`, `food-and-drink.csv`, `locations.csv`, `regions.csv` | Same class of object: in-repo rows upserted by `Story.link_npc`, `link_monster`, `link_fauna`, `link_flora`, `link_food_drink`, `link_location` (NPC rows go through `npc_lore.write_npc_rows`). `regions.csv` is updated when `link_location` is called with `region_name` (locations optionally reference a region; empty `RegionId` means unknown). No `flesh-and-blood-cards` feed for regions. Banner hint: `REGENERATE_STORY_REGISTRY` in `pipe_csv_io.py`. |

Foreign keys (lore side, simplified):

- `locations.csv` → optional `regions.csv` (`RegionId` may be empty for unknown region; when set, must match a row in `regions.csv`).
- Most `story-*.csv` junctions → `stories.csv` (`StoryId`) and a matching registry id: `story-npcs` → `npcs`, `story-heroes` → `heroes-canonical` (`CanonicalId`), `story-locations` → `locations`, `story-monsters` → `monsters`, `story-fauna` → `fauna`, `story-flora` → `flora`, `story-food-drink` → `food-and-drink`, `story-weapons` → `weapons-canonical` (`CanonicalWeaponId`), `story-equipment` → `equipment-canonical` (`CanonicalEquipmentId`) (same pattern as heroes: slug via `Story.link_weapon` / `link_equipment`, junction stores canonical id; dedicated lore markdown under `src/weapons/` and `src/equipment/` is editorial, not the junction key).

### Editorial and auxiliary (not registry pipelines)

| Artifact | Purpose |
|----------|---------|
| `character-groups.md` | Human-written groupings (Aesir, Dracai, …). Not validated by `validate_data.py`. |
| `characters.csv` | Convenience / display index (heroes etc.); not wired into `validate_data.py` or `story.py` junctions in this repo. |
| `data.md` | Free-form notes. |

### Full table index (columns, keys, origins)

Pipe-delimited unless noted. Empty fields appear as consecutive `|`.

| File | Columns | Primary key | FK / notes | Origin |
|------|---------|-------------|------------|--------|
| Game |||||
| `set-types.csv` | `SetTypeId`, `SetType`, `SetTypeLayer` | `SetTypeId` (`ST` + hash) | | `create_sets_csv.py` |
| `sets.csv` | `SetId`, `SetTypeId`, `SetName`, `InitialReleaseDate` | `SetId` (game string) | `SetTypeId` → `set-types.csv` | `create_sets_csv.py` |
| `classes.csv` | `ClassId`, `ClassName` | `ClassId` (`CL` + hash) | Shared | `create_classes_talents_csv.py` + hero/weapon/equipment generators |
| `talents.csv` | `TalentId`, `TalentName` | `TalentId` (`TL` + hash) | Shared | same |
| `heroes-canonical.csv` | `CanonicalId`, `CanonicalSlug`, `CanonicalHero` | `CanonicalId` (`CN` + hash of slug) | | `create_heroes_csv.py`; optional `Story.add_canonical_hero` |
| `heroes-game.csv` | `HeroGameId`, `CardName`, `CanonicalId`, `ClassIds`, `TalentIds`, … | `HeroGameId` (`HG` + hash) | `CanonicalId` → `heroes-canonical.csv` | `create_heroes_csv.py` |
| `heroes-printings.csv` | `HeroGameId`, `SetId`, `CardId`, `Rarity` | composite | → `heroes-game.csv`, `sets.csv` | `create_heroes_csv.py` |
| `weapons-canonical.csv` | `CanonicalWeaponId`, `CanonicalSlug`, `CanonicalWeapon` | `CanonicalWeaponId` (`CW` + hash) | | `create_weapons_csv.py` |
| `weapons-game.csv` | `WeaponGameId`, `CardName`, `CanonicalWeaponId`, … | `WeaponGameId` (`WG` + hash) | → `weapons-canonical.csv` | `create_weapons_csv.py` |
| `weapons-printings.csv` | `WeaponGameId`, `SetId`, `CardId`, `Rarity` | composite | → `weapons-game.csv`, `sets.csv` | `create_weapons_csv.py` |
| `equipment-canonical.csv` | `CanonicalEquipmentId`, `CanonicalSlug`, `CanonicalEquipment` | `CanonicalEquipmentId` (`CE` + hash) | | `create_equipment_csv.py` |
| `equipment-game.csv` | `EquipmentGameId`, `CardName`, `CanonicalEquipmentId`, … | `EquipmentGameId` (`EG` + hash) | → `equipment-canonical.csv` | `create_equipment_csv.py` |
| `equipment-printings.csv` | `EquipmentGameId`, `SetId`, `CardId`, `Rarity` | composite | → `equipment-game.csv`, `sets.csv` | `create_equipment_csv.py` |
| Lore |||||
| `stories.csv` | `StoryId`, `StoryKey`, `StoryType`, `Title` | `StoryId` (`ST` + hash of `StoryKey`) | `StoryKey` = path under `src/` (navigation; not used in `story-*.csv` joins) | `create_stories_index.py` / `Story` |
| `regions.csv` | `RegionId`, `RegionName`, `WorldOfRatheStoryKey` | `RegionId` (`RG` + hash of name) | Optional story path | `Story.link_location(..., region_name=...)` upserts; historical rows ship in-repo |
| `locations.csv` | `LocationId`, `Name`, `RegionId`, `Notes` | `LocationId` (`LO` + hash) | Optional `RegionId` → `regions.csv` (empty = unknown) | `Story.link_location` |
| `npcs.csv` | `CharacterId`, `Name`, `Species`, `Status` | `CharacterId` (`LC` + hash) | Appearances → `story-npcs.csv` | `Story.link_npc` |
| `monsters.csv` | `MonsterId`, `Name`, `Description` | `MonsterId` (`MO` + hash) | → `story-monsters.csv` | `Story.link_monster` |
| `fauna.csv` | `FaunaId`, `Name`, `Description` | `FaunaId` (`FA` + hash) | → `story-fauna.csv` | `Story.link_fauna` |
| `flora.csv` | `FloraId`, `Name`, `Description` | `FloraId` (`FR` + hash) | → `story-flora.csv` | `Story.link_flora` |
| `food-and-drink.csv` | `FoodDrinkId`, `Name`, `Type` | `FoodDrinkId` (`FD` + hash) | → `story-food-drink.csv` | `Story.link_food_drink` |
| `story-npcs.csv` | `StoryId`, `CharacterId` | composite | → `stories`, `npcs` | `Story` / `create_stories_index.py` |
| `story-heroes.csv` | `StoryId`, `CanonicalId` | composite | → `stories`, `heroes-canonical` | `Story` |
| `story-locations.csv` | `StoryId`, `LocationId` | composite | → `stories`, `locations` | `Story` |
| `story-monsters.csv` | `StoryId`, `MonsterId` | composite | → `stories`, `monsters` | `Story` |
| `story-fauna.csv` | `StoryId`, `FaunaId` | composite | → `stories`, `fauna` | `Story` |
| `story-flora.csv` | `StoryId`, `FloraId` | composite | → `stories`, `flora` | `Story` |
| `story-food-drink.csv` | `StoryId`, `FoodDrinkId` | composite | → `stories`, `food-and-drink` | `Story` |
| `story-weapons.csv` | `StoryId`, `CanonicalWeaponId` | composite | → `stories`, `weapons-canonical` | `Story.link_weapon` |
| `story-equipment.csv` | `StoryId`, `CanonicalEquipmentId` | composite | → `stories`, `equipment-canonical` | `Story.link_equipment` |

### Scripts and modules (quick reference)

| Script / module | Role |
|-----------------|------|
| `create_sets_csv.py` | `sets.csv`, `set-types.csv` from sibling `flesh-and-blood-cards` set exports |
| `create_classes_talents_csv.py` | `classes.csv`, `talents.csv` from `card.csv` |
| `create_heroes_csv.py` | Hero canonical + game + printings; refreshes shared class/talent CSVs |
| `create_weapons_csv.py` | Weapon canonical + game + printings; refreshes shared class/talent CSVs |
| `create_equipment_csv.py` | Equipment canonical + game + printings; refreshes shared class/talent CSVs |
| `create_stories_index.py` | Refreshes `stories.csv` from `src/` scan (titles: keep if not stem placeholder, else first H1, else filename); seeds empty `story-*.csv` if missing |
| `story.py` | `Story` class: lore registries, junctions, `stories.csv` row upsert, `remove` |
| `registry_ids.py` | Deterministic ids (`ST`, `LC`, `MO`, `RG`, `LO`, …) |
| `npc_lore.py` | NPC row helpers; `write_npc_rows` for `npcs.csv` |
| `tab_csv_io.py` | Tab-separated reads of upstream exports |
| `pipe_csv_io.py` | Pipe read/write, `auto_gen_banner`, `REGENERATE_*` hints (`REGENERATE_STORY_JUNCTIONS`, `REGENERATE_STORY_REGISTRY`, …) |
| `game_class_talent_csv.py` | Merges shared `classes.csv` / `talents.csv` for generators |
| `card_types_extract.py` | Parses card `Types` into class vs talent names |
| `create_md.py` | Markdown tables: `npcs.md` ← `npcs.csv`; `fauna.md`, `flora.md`, `food-and-drink.md`, `locations.md`, `monsters.md` ← same-named CSVs (needs pandas / extras) |
| `validate_data.py` | Read-only checks on ids and FKs; hero `CardName` vs `CanonicalId` consistency with `create_heroes_csv` rules; `stories.csv` `StoryType` allowlist (`ALLOWED_STORY_TYPES`) |

Run `python3 src/data/validate_data.py` after any generator or after `story.py` changes to lore CSVs.

<p align="right">
(<a href="#readme-top">back to top</a>)
</p>

## Automated tests (pytest)

From the repository root, use a virtual environment (recommended on macOS/Homebrew Python), install dev dependencies, and run pytest:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
python3 -m pytest
```

This exercises pipe/tab CSV helpers, ``Types`` parsing, shared class/talent merging (with isolated temp files), hero hashing helpers, registry id helpers, and an integration check that ``validate_data.collect_alerts()`` returns no issues for the committed datasets.

Isolation: mutating tests use pytest ``tmp_path`` and ``monkeypatch``; they do not write into ``src/data/`` in the checkout. The ``validate_data`` integration test only reads the checkout.

CI / dependencies (future): there is no root ``requirements.txt`` or lockfile dedicated to "runtime" generators today. ``requirements-data.txt`` and ``requirements-dev.txt`` cover ``create_md.py``, the pre-commit markdown sync hook, and pytest. If CI later runs ``create_md.py`` (or other Python generators) outside pre-commit (for example as part of an mdbook or publish step), consider adding an explicit install target or pins so that environment matches local and pre-commit behaviour.

## Validating data

```bash
python3 src/data/validate_data.py
```

This checks required non-empty ID columns on the pipe-delimited CSVs and referential links—including hero / weapon / equipment printings (each ``*GameId`` must exist on the matching game table), canonical FKs on game rows, and story junction keys (including ``story-weapons`` / ``story-equipment`` → canonical ids). Exit status is non-zero when any check fails.

Use `Story.link_fauna` / `link_flora` / `link_food_drink` from `story.py` to maintain fauna/flora/food junctions, or edit the CSVs by hand.

## Creating the Sets CSV

Set metadata is generated independently from heroes.

```bash
python3 src/data/create_sets_csv.py
```

This script derives:

- `src/data/sets.csv`:
  - `SetId`, `SetTypeId`, `SetName`, `InitialReleaseDate`
- `src/data/set-types.csv`:
  - `SetTypeId`, `SetType`, `SetTypeLayer`

Data sources:

- Set metadata from `../flesh-and-blood-cards/csvs/english/set.csv` and `set-printing.csv`

<p align="right">
(<a href="#readme-top">back to top</a>)
</p>
