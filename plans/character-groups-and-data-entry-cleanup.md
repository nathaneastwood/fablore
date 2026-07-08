# Character groups modeling gap + data-entry cleanup

Status: **discussion / not yet actioned**. Written up 2026-07-08 after registering
`a-rising-star.md` surfaced several pre-existing data issues.

## 1. The unsolved problem: no home for "character groups"

`src/data/md/character-groups.md` lists a real taxonomy that has never been given a
database home:

- **Cosmological tiers**: Aesir, Ancients, Embra, Dracai, Dragons, Gods, Heralds,
  Grand Magisters
- **Social/organizational groups**: factions (Rosetta, Kuraghan, Disciples of Pain,
  Runeblades, ...), Deathmatch Super Slam Guilds, and by extension things like the
  Everfest's **Maela** and **Valdur** troupes

None of these have a SQLite table. Coverage today is split across three places with
no consistent rule for which one to use:

1. **`src/hints_supplement.json`** — has working `type: "faction"` entries (11 today:
   Alshoni, Cintari, Dracai, Ezu, Hand of Sol, Kuraghan, Rosetta, Sayashi, Disciples
   of Pain, Runeblades, Church of Pain) plus `aesir` (3), `ancient` (4), `embra` (1),
   `organisation` (5), `ship` (3). This is the only place a "faction" has ever
   actually been *resolved* into something renderable (a hover tooltip).
2. **`src/data/md/character-groups.md`** — a hand-maintained reference table, not
   linked to the DB or the supplement at all. Manually kept in sync with nothing.
3. **`# TODO: group — <Name>` comments in `data-entry.py`** — the register-story
   skill's current fallback when it meets a named group it can't otherwise classify.
   These are a parking lot, not a resolution: `Disciples of Pain` and `Runeblades`
   have had TODO comments since `letters-from-the-beyond.md` was registered, and nothing
   has picked them up into the supplement yet (they happen to also already exist as
   supplement entries — the TODO and the resolution both exist, disconnected).

Additionally: two members of this taxonomy (**Maela**, **Valdur**) were registered as
DB `locations` (via `descriptions.py`), not as factions, because at the time nothing
else existed to put them in. That's arguably *correct* — they are as much "a place at
the carnival" as "a group of people" — but it means the taxonomy is inconsistently
applied: some groups are supplement factions, some are DB locations, most are neither.

### Why this matters for register-story

The skill currently tells the model: *"Identify any named groups or factions... do
NOT add these as NPCs. Instead add a `# TODO: group — <Name>` comment."* This treats
every named group as equally unresolved, when in practice:
- Some groups already have working supplement `faction` entries (skill should look
  these up and just reference them, not TODO them again).
- Some "groups" are actually already-modeled DB locations (skill should search for
  them by name across `locations`/`monsters`/`fauna`/`flora` before assuming a group
  needs new treatment).
- Only genuinely new, unresolved groups should get a TODO.

### Potential solutions (not decided — for discussion)

**Option A — Keep it supplement-only, formalize the workflow.**
No schema change. Treat `hints_supplement.json` `type: "faction"` (and `aesir`,
`ancient`, `embra`, `organisation`, `ship` etc.) as the single home for all
`character-groups.md` entries. Update the skill to:
1. Before proposing a TODO, check the supplement for an existing entry (by safe key
   or `match`).
2. If found, just reference it — no TODO needed.
3. If not found, propose adding it as a supplement entry directly (not a TODO) unless
   the user wants to defer.
Pros: cheapest, no migration, reuses working code (`generate_hints_json.py` already
merges these). Cons: factions stay outside the relational DB — no `story_factions`
join table, so you can't query "which stories mention the Rosetta" the way you can
for locations/NPCs today; `character-groups.md` remains a disconnected manual mirror.

**Option B — Add a real `factions` table (and maybe `character_groups` more broadly).**
New table(s) + `FactionEntry` dataclass + `story_factions` join table + CSV export +
`generate_hints_json.py` wiring + tests, following the exact pattern `monsters` /
`fauna` already use. Would let `upsert_story(factions=[...])` work like `monsters=`
does today, and would make `character-groups.md` generatable from the DB instead of
hand-maintained (mirroring how `create_md.py` already does this for npcs/fauna/flora/etc).
Pros: consistent with the rest of the schema, queryable, removes the manual-mirror
problem. Cons: real migration effort; also raises the question of whether Aesir/
Ancients/Embra/Dracai/Gods/Heralds need their own typed tables too, or a single
generic `character_groups(type, name, ...)` table with a `kind` column covering all
of `character-groups.md`'s categories.
Also would require deciding whether to migrate Maela/Valdur off `locations` and into
this new table — non-trivial since they're already correctly working as locations
(they have a physical presence at the Everfest, `lore_fragment` support, etc.) and any
migration risks another location/faction split-identity problem like the ones fixed
in §3 below.

**Option C — Hybrid: generic `character_groups` table, keep hints_supplement for
narrative-only entities that never need DB querying.**
Only add a table for things that benefit from relational querying/story-linking
(factions, guilds) and leave purely cosmological flavour (Aesir epithets, Dragon
pronunciation tables) in `character-groups.md` as-is, since those aren't referenced
by `upsert_story` calls today anyway.

No recommendation is being made here — flagged for a decision before any schema work
starts.

## 2. Two-writers-one-column problem: `data-entry.py` vs `descriptions.py`

Confirmed via `git log` (commit `6cc300d`, *"DB description preservation and
update_description API"*): `descriptions.py` was deliberately created as **the single
place to maintain all entity descriptions and location notes**, with inline
`notes=`/`description=` values *moved out of* `data-entry.py` at the time. The
intended split:

- **`data-entry.py`** — registers a story and which entities it **links to**
  (`heroes=`, `npcs=`, `locations=`, etc. — the relationships).
- **`descriptions.py`** — the **only** place that sets the actual lore text
  (`db.update_description(entity_type, name, description)`) for monsters, fauna,
  flora, and location notes.

Both scripts write into the exact same DB columns (`locations.notes`,
`monsters.description`, `fauna.description`, `flora.description`), so if this split
isn't documented and consistently followed, the same entity can silently end up
described in two places, or worse, registered as two different entities.

**Straggler found:** `data-entry.py`'s `letters-from-the-beyond.md` call (added
2026-07-07, one day before `descriptions.py` was created 2026-07-08) still has two
inline values that were never migrated:
- `LocationEntry("The Shadow Crypts", ..., notes="Dim halls within the Demonastery...")`
- `MonsterEntry("Shadowrealm Walker", description="Huge stilt-legged predators...")`

These should move to `descriptions.py` and be dropped from `data-entry.py`, per the
established convention. (Also see §3 — the Shadow Crypts entry is entangled with a
duplicate-row bug, not just a misplaced description.)

## 3. Duplicate rows found in the live DB

Neither of these was caused by anything in this conversation — both pre-exist. Found
via a sweep for locations sharing the same `(lore_fragment, region_id)`.

### 3a. `"Legendarium"` vs `"Bravo's Legendarium"`

Two rows, same region (Aria), same `lore_fragment="the-everfest-carnival"`:

| location_id | name | notes | linked stories |
|---|---|---|---|
| `LO7cc652d28f` | Legendarium | *(empty)* | `a-rising-star.md` (1 link) |
| `LO8da24ef60f` | Bravo's Legendarium | "Part of the Everfest Carnival." | **none** (orphan) |

`Bravo's Legendarium` has zero story links today — it's dead data, most likely a
row created by an earlier version of `data-entry.py` (before it was renamed to just
"Legendarium") that `descriptions.py` then added notes to (its `update_description`
requires the row to already exist, so this row predates `descriptions.py`).

**Proposed fix:** move the notes text onto the live row (`Legendarium`), then delete
the orphaned `Bravo's Legendarium` row and its `descriptions.py` entry.

### 3b. `"The Shadow Crypts"` appears as two rows

Same name, same region (Demonastery), same `lore_fragment="the-shadow-crypts"`, but
two different `location_id`s (which are a deterministic hash of `name|region_id` —
so two different IDs for identical inputs implies the region's `region_id` value was
different at the time of each insert, e.g. before vs. after the Demonastery region
was formally created):

| location_id | notes | linked stories |
|---|---|---|
| `LOc627b5aaa2` | *(empty)* | `world-of-rathe/demonastery.md`, `archive/world-of-rathe/demonastery/the-shadow.md`, `flavour/dynasty.md` (3 links — this is the "real" one) |
| `LO2853f69ca8` | "Dim halls within the Demonastery where a black mold..." | `letters-from-the-beyond.md` only (1 link — the straggler from §2) |

**Proposed fix:** move the notes text onto the older, more-linked row
(`LOc627b5aaa2`), repoint `letters-from-the-beyond.md`'s `story_locations` row to it,
then delete `LO2853f69ca8`.

## 4. Register-story skill gap that let this happen

The skill (`.claude/skills/register-story/SKILL.md`) currently checks DB coverage
*per entity name as typed in the new story*, via exact `WHERE name = ?` lookups
(Step 8b). It never had a step that says "before treating an entity as new, check
whether a *similarly named* entity already exists under a different display name"
(e.g. "Legendarium" vs "Bravo's Legendarium" — a human would probably have caught
this by eye, but the skill's literal-name-match approach won't). This should be
folded into the skill update in §6 below: when composing `LocationEntry`/
`MonsterEntry`/etc., search `db.list_locations()` etc. for fuzzy/substring matches on
the entity name, not just exact matches, and flag possible duplicates as ambiguous.

## Next steps (not yet actioned — pending decision on §1)

- [ ] Decide between Option A/B/C for character groups (§1)
- [ ] Move the two `letters-from-the-beyond.md` stragglers from `data-entry.py` into
      `descriptions.py` (§2)
- [ ] Merge the Legendarium duplicate (§3a)
- [ ] Merge the Shadow Crypts duplicate (§3b)
- [ ] Add a documentation header to both `data-entry.py` and `descriptions.py`
      cross-linking each other and stating the split
- [ ] Update the register-story skill: near-duplicate detection, and correct handling
      of groups depending on which option is chosen for §1
