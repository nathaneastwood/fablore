"""Tests for the professions tables (migration 15) — R9.

A profession is a trade many hold independently — Braumeister, shieldbearer —
unlike a group's roster (bounded, citable) or a title's holders (one at a time,
ordered). "Who is a Braumeister" is unbounded and unsourceable, which is exactly
what a group's ``member_source`` exists to prevent, so a profession never gets
one: there is no roster, only a registry (``professions``) and a junction
(``character_professions``) that any character may join independently.

Mirrors ``test_db_species.py`` for the registry + junction shape, and borrows
the hero-resolution tests from ``test_db_titles.py`` for the one hazard a
profession introduces that species never had to: attaching to a hero with no
NPC row of its own (Kano is a hero and a Lord Wizard, with no ``NPCEntry``).
"""

from __future__ import annotations

from pathlib import Path

import pytest

import db._queries as q
from db import Database, GroupEntry, NPCEntry, ProfessionEntry
from registry_ids import canonical_id, lore_character_id, profession_id


def _seed_hero(database: Database, slug: str, name: str) -> str:
    cid = canonical_id(slug)
    q.upsert_hero_canonical(database.conn, canonical_id=cid, canonical_slug=slug, canonical_hero=name)
    return cid


def _story(database: Database, path: str = "src/main-story/super-slam/feudmasters.md", **kw):
    return database.upsert_story(path=path, story_type="main-story", title="T", **kw)


def _professions_of(database: Database, name: str) -> list[str]:
    cid = lore_character_id(name)
    return [
        r[0]
        for r in database.conn.execute(
            "SELECT p.name FROM character_professions cp JOIN professions p USING(profession_id)"
            " WHERE cp.character_id = ? ORDER BY cp.sort_order",
            [cid],
        )
    ]


# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------


def test_migration_creates_the_profession_tables(db: Database) -> None:
    tables = {r[0] for r in db.conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    assert {"professions", "character_professions"} <= tables


def test_schema_version_matches_constant(db: Database) -> None:
    from db._schema import CURRENT_VERSION

    assert db.conn.execute("PRAGMA user_version").fetchone()[0] == CURRENT_VERSION


# ---------------------------------------------------------------------------
# Identity
# ---------------------------------------------------------------------------


def test_profession_id_hashes_the_name_alone(db: Database) -> None:
    assert profession_id("Braumeister") == profession_id("  Braumeister  ")
    assert profession_id("Braumeister") != profession_id("Brewmeister")


def test_second_literal_for_the_same_name_reuses_the_row(db: Database) -> None:
    _story(db, characters=[NPCEntry("Aeric", professions=ProfessionEntry("Braumeister"))])
    _story(
        db,
        path="src/world-of-rathe/aria.md",
        characters=[NPCEntry("Bellwyn", professions=ProfessionEntry("Braumeister"))],
    )
    assert db.conn.execute("SELECT COUNT(*) FROM professions WHERE name = 'Braumeister'").fetchone()[0] == 1


# ---------------------------------------------------------------------------
# Writing (NPCEntry.professions)
# ---------------------------------------------------------------------------


def test_a_profession_is_written_from_a_declaration(db: Database) -> None:
    _story(db, characters=[NPCEntry("Aeric", professions=ProfessionEntry("Braumeister"))])
    assert _professions_of(db, "Aeric") == ["Braumeister"]


def test_a_character_holds_two_professions_in_declared_order(db: Database) -> None:
    entry = NPCEntry("Aeric", professions=(ProfessionEntry("Braumeister"), ProfessionEntry("Shieldbearer")))
    _story(db, characters=[entry])
    assert _professions_of(db, "Aeric") == ["Braumeister", "Shieldbearer"]


def test_professions_is_replace_semantic(db: Database) -> None:
    entry = NPCEntry("Aeric", professions=(ProfessionEntry("Braumeister"), ProfessionEntry("Shieldbearer")))
    _story(db, characters=[entry])
    _story(db, characters=[NPCEntry("Aeric", professions=ProfessionEntry("Braumeister"))])
    assert _professions_of(db, "Aeric") == ["Braumeister"]


def test_an_omitted_profession_is_a_deletion(db: Database) -> None:
    """Like species, and unlike status: a junction states the complete set."""
    _story(db, characters=[NPCEntry("Aeric", professions=ProfessionEntry("Braumeister"))])
    _story(db, characters=[NPCEntry("Aeric")])
    assert _professions_of(db, "Aeric") == []


def test_two_characters_share_one_profession_row(db: Database) -> None:
    _story(
        db,
        characters=[
            NPCEntry("Aeric", professions=ProfessionEntry("Braumeister")),
            NPCEntry("Bellwyn", professions=ProfessionEntry("Braumeister")),
        ],
    )
    assert db.conn.execute("SELECT COUNT(*) FROM professions WHERE name = 'Braumeister'").fetchone()[0] == 1


def test_a_repeated_profession_on_one_entry_raises(db: Database) -> None:
    """The guard shape GroupEntry.member_pairs(), _resolve_title_holders and
    _resolve_kin_relatives all use: two entries naming the same profession
    would otherwise resolve differently on the write path (INSERT OR IGNORE
    keeps the first) than on a preview that diffed a dict (last wins)."""
    entry = NPCEntry("Aeric", professions=(ProfessionEntry("Braumeister"), ProfessionEntry("Braumeister")))
    with pytest.raises(ValueError, match="Braumeister"):
        _story(db, characters=[entry])


def test_the_duplicate_guard_fires_on_the_preview_path_too(db: Database) -> None:
    entry = NPCEntry("Aeric", professions=(ProfessionEntry("Braumeister"), ProfessionEntry("Braumeister")))
    with pytest.raises(ValueError, match="Braumeister"):
        _story(db, characters=[entry], dry_run=True)


def test_dry_run_reports_a_profession_on_a_group_member(db: Database, capsys) -> None:
    """Reached through a group roster and through nothing else — mirrors species."""
    _story(db, groups=[GroupEntry("Rosetta", members=(NPCEntry("Ozrim"),))])
    capsys.readouterr()
    db.upsert_story(
        path="src/main-story/super-slam/feudmasters.md",
        story_type="main-story",
        title="T",
        groups=[GroupEntry("Rosetta", members=(NPCEntry("Ozrim", professions=ProfessionEntry("Braumeister")),))],
        dry_run=True,
    )
    assert "Ozrim: profession 'Braumeister'" in capsys.readouterr().out


# ---------------------------------------------------------------------------
# Preview (NPCEntry.professions)
# ---------------------------------------------------------------------------


def test_dry_run_reports_a_profession_it_would_add(db: Database, capsys) -> None:
    _story(db, characters=[NPCEntry("Aeric")])
    capsys.readouterr()
    db.upsert_story(
        path="src/main-story/super-slam/feudmasters.md",
        story_type="main-story",
        title="T",
        characters=[NPCEntry("Aeric", professions=ProfessionEntry("Braumeister"))],
        dry_run=True,
    )
    assert "Aeric: profession 'Braumeister'" in capsys.readouterr().out


def test_dry_run_reports_a_profession_it_would_remove(db: Database, capsys) -> None:
    _story(db, characters=[NPCEntry("Aeric", professions=ProfessionEntry("Braumeister"))])
    capsys.readouterr()
    db.upsert_story(
        path="src/main-story/super-slam/feudmasters.md",
        story_type="main-story",
        title="T",
        characters=[NPCEntry("Aeric")],
        dry_run=True,
    )
    assert "Aeric: profession 'Braumeister' REMOVED" in capsys.readouterr().out


def test_dry_run_does_not_write_professions(db: Database) -> None:
    db.upsert_story(
        path="src/main-story/super-slam/feudmasters.md",
        story_type="main-story",
        title="T",
        characters=[NPCEntry("Aeric", professions=ProfessionEntry("Braumeister"))],
        dry_run=True,
    )
    assert db.conn.execute("SELECT COUNT(*) FROM professions").fetchone()[0] == 0


# ---------------------------------------------------------------------------
# Attaching to a hero (the point of this stage)
# ---------------------------------------------------------------------------
# A hero is the game-side row: a canonical slug and the cards printed for it.
# A character is the lore-side person. Species, profession, kin and titles are
# facts about the person, so they hang off `characters`, and `heroes_canonical`
# joins through `character_heroes` to read them (the user's call, 2026-08-22).
#
# So there is exactly one way to say "Kano is a Lord Wizard": give the character
# the profession. `hero_slug` — built in migration 12 to dissolve X01 — is what
# makes an NPCEntry *be* a hero's character row, and Kano has no NPCEntry only
# because nobody has written one yet.


def test_a_profession_attaches_to_a_hero_through_its_character_row(db: Database) -> None:
    """The deliverable: Kano is a hero and a Lord Wizard, and had no NPCEntry.

    The profession lands on the character row seeding already minted for the
    hero — the same id `lore_character_id` computes from the canonical hero
    name — so the hero reaches it by joining, and no hero-shaped second path
    into `character_professions` has to exist.
    """
    hid = _seed_hero(db, "kano", "Kano")
    _story(db, characters=[NPCEntry("Kano", hero_slug="kano", professions=ProfessionEntry("Lord Wizard"))])

    minted = lore_character_id("Kano")
    assert q.select_character_id_for_hero(db.conn, hid) == minted
    assert _professions_of(db, "Kano") == ["Lord Wizard"]


def test_the_hero_name_guard_still_refuses_an_undeclared_claim(db: Database) -> None:
    """Without `hero_slug`, an NPC named after a hero is still refused.

    The guard migration 12 relaxed was relaxed *only* for an entry that admits
    what it is doing. Dropping `hero_slug` here must not quietly mint a second
    person under the hero's own name.
    """
    _seed_hero(db, "kano", "Kano")
    with pytest.raises(ValueError, match="playable hero name"):
        _story(db, characters=[NPCEntry("Kano", professions=ProfessionEntry("Lord Wizard"))])


def test_a_hero_profession_self_heals_the_character_heroes_link(db: Database) -> None:
    hid = _seed_hero(db, "kano", "Kano")
    assert q.select_character_id_for_hero(db.conn, hid) is None
    _story(db, characters=[NPCEntry("Kano", hero_slug="kano", professions=ProfessionEntry("Lord Wizard"))])
    assert q.select_character_id_for_hero(db.conn, hid) is not None


def test_a_hero_profession_is_replace_semantic_like_any_other(db: Database) -> None:
    _seed_hero(db, "kano", "Kano")
    _story(
        db,
        characters=[
            NPCEntry(
                "Kano",
                hero_slug="kano",
                professions=(ProfessionEntry("Lord Wizard"), ProfessionEntry("Braumeister")),
            )
        ],
    )
    _story(
        db,
        path="src/world-of-rathe/aria.md",
        characters=[NPCEntry("Kano", hero_slug="kano", professions=ProfessionEntry("Lord Wizard"))],
    )
    assert _professions_of(db, "Kano") == ["Lord Wizard"]


def test_a_dry_run_writes_neither_the_hero_link_nor_the_profession(db: Database, capsys) -> None:
    hid = _seed_hero(db, "kano", "Kano")
    db.upsert_story(
        path="src/main-story/super-slam/feudmasters.md",
        story_type="main-story",
        title="T",
        characters=[NPCEntry("Kano", hero_slug="kano", professions=ProfessionEntry("Lord Wizard"))],
        dry_run=True,
    )
    capsys.readouterr()
    assert q.select_character_id_for_hero(db.conn, hid) is None
    assert db.conn.execute("SELECT COUNT(*) FROM professions").fetchone()[0] == 0


def test_a_dry_run_reports_the_hero_profession_it_would_add(db: Database, capsys) -> None:
    _seed_hero(db, "kano", "Kano")
    db.upsert_story(
        path="src/main-story/super-slam/feudmasters.md",
        story_type="main-story",
        title="T",
        characters=[NPCEntry("Kano", hero_slug="kano", professions=ProfessionEntry("Lord Wizard"))],
        dry_run=True,
    )
    assert "profession 'Lord Wizard'" in capsys.readouterr().out


# ---------------------------------------------------------------------------
# Round trip
# ---------------------------------------------------------------------------


def test_professions_survive_the_csv_round_trip(db: Database, tmp_path: Path) -> None:
    _story(
        db,
        characters=[
            NPCEntry("Aeric", professions=(ProfessionEntry("Braumeister"), ProfessionEntry("Shieldbearer"))),
        ],
    )
    import db._export as _export

    _export.export_all(db.conn, tmp_path)
    fresh = Database(str(tmp_path / "round-trip.db"), data_dir=tmp_path)
    assert q.select_character_professions(fresh.conn, lore_character_id("Aeric")) == [
        profession_id("Braumeister"),
        profession_id("Shieldbearer"),
    ]


# ---------------------------------------------------------------------------
# update_description("profession", …) — notes come from descriptions.py
# ---------------------------------------------------------------------------


def test_update_description_writes_profession_notes(db: Database) -> None:
    _story(db, characters=[NPCEntry("Aeric", professions=ProfessionEntry("Braumeister"))])
    db.update_description("profession", "Braumeister", "The elite of the brewer's trade.")
    row = db.conn.execute("SELECT notes FROM professions WHERE name = 'Braumeister'").fetchone()
    assert row["notes"] == "The elite of the brewer's trade."


def test_update_description_rejects_a_profession_with_no_row(db: Database) -> None:
    with pytest.raises(ValueError, match="Profession not found"):
        db.update_description("profession", "Nonesuch", "Never applied.")


# ---------------------------------------------------------------------------
# The catalogue holds no lore data yet (R9 is scaffolding; the fifteen names
# waiting are a separate pass)
# ---------------------------------------------------------------------------


def test_professions_catalogue_has_no_constants_yet() -> None:
    from entries.catalogue import professions as prof_module

    assert [n for n in dir(prof_module) if n.isupper()] == []
