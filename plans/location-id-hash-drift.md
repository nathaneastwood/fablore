# Location id-hash drift migration

Status: **migrated**. Written up 2026-07-08 after registering the `welcome-to-rathe`
stories surfaced a live duplicate-row bug caused by this; migration script written and
run the same day via `src/data/migrate_location_ids.py`, migrating 151 drifted rows.
`validate_data.py` now reports zero location id-hash-drift warnings.

## The problem

`src/data/csv/locations.csv` has **151 of 194 rows** (~78%, as of this writing — re-run
the check below for the current count) where the stored `LocationId` does not match
what `registry_ids.location_id(name, region_id)` computes for that row's current
name/region today.

This is not cosmetic. `db/_domain.py::_upsert_locations()` recomputes
`lid = _location_id(e.name, eff_region)` **fresh on every `upsert_story()` call** and
upserts by that computed id (`INSERT ... ON CONFLICT(location_id) DO UPDATE`). If the
freshly-computed id doesn't match the row's legacy stored id, SQLite finds no conflict
and **silently inserts a second row** for the same conceptual place instead of updating
the existing one.

This already happened live during the 2026-07-08 session: registering
`wanderings-in-the-mists.md` created a duplicate `"Mugenshi Gorge"` row and repointed
that story's link to it, purely because the location's stored id predates the current
hash formula. It was caught only by manually diffing `git status` after the fact — no
automated check existed at the time.

## Root cause (confirmed via git archaeology)

- The original `locations.csv` (commit `4693b86`, March 2023) had **no `LocationId`
  column at all** — just `Name|Region|Notes|Mentions`.
- IDs were introduced by a later "Migrate data layer to SQLite database" commit
  (`48de731` and related). Whatever script assigned the original IDs at that migration
  did **not** use the same formula as today's `registry_ids.location_id()` — confirmed by
  testing several candidate historical formulas (name-only hash, non-normalized
  composite, etc.) against sample drifted rows; none reproduce the stored id.
- Net effect: roughly 4 in 5 rows carry an id from that original migration that the
  current hash function can never reproduce. It's not corruption from recent editing —
  it has been silently wrong since the SQLite migration, just never checked until the
  2026-07-08 session added a detector.

## What's already in place (as of 2026-07-08)

- **Detection**: `validate_data.py::_check_location_id_hash_drift()`, wired into
  `collect_warnings()` (warn-only — prints `WARNING:` lines but does not fail CI, since
  the drift is large and pre-existing, not something a single commit should be blocked
  on). Run `python3 src/data/validate_data.py` for the live, current list of drifted
  rows — don't trust this doc's row count to stay accurate.
- **A companion check**: `_check_near_duplicate_names()` (also warn-only), which flags
  near-identical entity names via string similarity — a different but related failure
  mode (spelling-duplicate rows, e.g. `Ampitheatre`/`Amphitheatre`,
  `Gigadril`/`Gigadrill Elevator`, both found and fixed this session). Not the same bug
  as id drift, but the two often co-occur since both stem from the DB accumulating
  divergent rows for what should be one entity.
- **A safe delete primitive**: `Database.delete_entity(entity_type, name)` in
  `db/_domain.py` — deletes an orphaned registry row (location/monster/fauna/flora) by
  name, refusing (raises `ValueError`) if any story still references it. Added so
  cleanup no longer requires dropping to raw SQL against `fablore.db` (which the
  register-story skill explicitly prohibits — see its Notes section). This is the
  primitive a migration script should reuse for the delete-old-row step, rather than
  raw `DELETE FROM locations`.
- **Supporting queries** in `db/_queries.py`: `select_location_ids_by_name()` (returns
  every `LocationId` stored under a name — handles the case where the same name exists
  under >1 row, e.g. across regions) and `count_entity_story_links(...)` (the guard
  `delete_entity` uses to refuse deleting a still-linked row).

None of this fixes the drift itself — it only detects it and gives a safe tool for the
single-row case. The batch migration (below) is still unwritten.

## Migration plan

Scope as its own isolated PR — do not bundle with story-registration work, so if
something goes wrong it's obvious what caused it.

1. **Snapshot** — back up `locations.csv` and `story-locations.csv` (and confirm via
   `grep -rn "LocationId\|location_id" src/data/csv/*.csv` that nothing else keys off
   `LocationId`) before touching anything.
2. **Compute the mapping** — for every row where stored id ≠
   `location_id(name, region_id)`, that's an `(old_id → new_id)` pair.
   `_check_location_id_hash_drift`'s logic is exactly this; a migration script should
   reuse it rather than re-deriving.
3. **Check for collisions before writing anything** — verify no two rows' *new*
   computed ids collide (i.e. two differently-tracked rows don't turn out to hash to
   the same `name|region_id` today). `registry_ids.assert_unique_ids()` exists for
   exactly this. If a collision surfaces, that's a genuine duplicate needing a human
   merge decision — stop and flag it, don't auto-resolve inside the migration.
4. **Migrate inside one SQLite transaction**: for each drifted row — insert/update
   under the new id carrying over the old row's `notes`/`lore_fragment`, repoint every
   `story_locations` row from old id → new id, delete the old id row (reuse
   `delete_entity`'s underlying queries, or extend it, rather than raw SQL). Wrap the
   whole loop in `with db.conn:` so a mid-loop failure doesn't leave a half-migrated
   state.
5. **Re-export and verify**: `db._export.export_all()` (or `create_md.py` for the
   markdown mirrors), then `python3 src/data/validate_data.py` should show **zero**
   location id-hash-drift warnings, `python3 -m pytest` should stay green (419 tests as
   of this writing), and a fresh `mdbook build` should succeed. Locations'
   `LoreFragment` deep links key off region markdown files, not `LocationId`, so should
   be unaffected — but spot-check a few location tooltip links in the built site to be
   sure.
6. **One commit** — review the *migration script* itself, not a 151-line id diff;
   line-by-line review of hash outputs adds little signal versus reviewing the script's
   logic once.

## Where to start in a fresh session

Point Claude at:

- `src/data/registry_ids.py::location_id()` — the current, correct formula.
- `src/data/validate_data.py::_check_location_id_hash_drift()` and `collect_warnings()`
  — the detector, already built; re-run it first to get current numbers.
- `src/data/db/_domain.py::Database.delete_entity()` — the safe single-row delete
  primitive to reuse/extend.
- `src/data/db/_queries.py::select_location_ids_by_name()` /
  `count_entity_story_links()` — supporting queries already added.
- This file, for the "why" and the plan.

Nothing here needs re-discovering — detection and the single-row deletion primitive
already exist. What's missing is the batch migration script itself (step 4 above),
written and run deliberately with review, not as a side effect of other work.

## Next steps

- [x] Write the batch migration script (steps 1–4 above) — `src/data/migrate_location_ids.py`
- [x] Run it in isolation, verify via steps 5–6 — 151 rows migrated, `pytest` (419 tests)
      and `mdbook build` both green, spot-checked `Ankomeido`'s `ankomeido` lore-fragment
      anchor resolves in `book/world-of-rathe/pits.html`
- [x] Confirm `validate_data.py` reports zero location id-hash-drift warnings afterward
- [ ] Consider whether `npcs`/`monsters`/`fauna`/`flora` need the same historical-drift
      audit (checked 2026-07-08: all clean, 0 drift — but re-verify if this file is
      picked up much later, in case new rows were added by a different path since)
- [ ] Separately: `validate_data.py`'s near-duplicate-name check currently flags
      `Ceremionial Chamber` vs `Ceremonial Chamber` in `locations.csv` — looks like a
      spelling typo, not id drift. Out of scope for this migration (kept isolated per
      the note below); worth a follow-up fix.
