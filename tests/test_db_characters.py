"""Tests for the identity spine (migration 12): characters, character_heroes,
NPCEntry.hero_slug, the hero-name guard's new escape hatch, and the closed
status vocabulary.

heroes_canonical and npcs/characters are two registries for one person. This
stage links them without touching story_npcs/story_heroes or group_npcs/
group_heroes beyond what the npcs -> characters rename forces.
"""

from __future__ import annotations

import pytest

import db._queries as q
from db import Database, GroupEntry, NPCEntry
from registry_ids import canonical_id, lore_character_id


def _seed_hero(database: Database, slug: str, name: str) -> str:
    cid = canonical_id(slug)
    q.upsert_hero_canonical(database.conn, canonical_id=cid, canonical_slug=slug, canonical_hero=name)
    return cid


def _story(database: Database, path: str = "src/main-story/monarch/step-into-the-light.md", **kw):
    return database.upsert_story(path=path, story_type="main-story", title="T", **kw)


# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------


def test_migration_renames_npcs_to_characters_and_adds_character_heroes(db: Database) -> None:
    tables = {r[0] for r in db.conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    assert "characters" in tables
    assert "character_heroes" in tables
    assert "npcs" not in tables


def test_schema_version_is_12(db: Database) -> None:
    from db._schema import CURRENT_VERSION

    assert CURRENT_VERSION == 12
    assert db.conn.execute("PRAGMA user_version").fetchone()[0] == 12


def test_character_id_column_still_the_primary_key(db: Database) -> None:
    cols = {r[1] for r in db.conn.execute("PRAGMA table_info(characters)")}
    assert "character_id" in cols


def test_character_heroes_canonical_id_is_the_primary_key(db: Database) -> None:
    info = {r[1]: r for r in db.conn.execute("PRAGMA table_info(character_heroes)")}
    assert info["canonical_id"][5] == 1  # pk flag
    assert info["character_id"][5] == 0


# ---------------------------------------------------------------------------
# NPCEntry.hero_slug
# ---------------------------------------------------------------------------


def test_hero_slug_links_the_npc_row_to_the_hero(db: Database) -> None:
    hid = _seed_hero(db, "kox", "Fightmaster Kox")
    _story(db, npcs=[NPCEntry("Fightmaster Kox", hero_slug="kox")])
    cid = lore_character_id("Fightmaster Kox")
    row = db.conn.execute("SELECT character_id FROM character_heroes WHERE canonical_id = ?", [hid]).fetchone()
    assert row is not None
    assert row["character_id"] == cid


def test_hero_slug_preserves_on_empty(db: Database) -> None:
    """Unlike species, there is no way to *clear* a stored identity claim.

    A name that matches a hero always needs hero_slug repeated (the guard
    below raises otherwise), so the claim can never be silently dropped — the
    write path never gets the chance to clear it, because the declaration
    that would omit it is refused outright.
    """
    hid = _seed_hero(db, "kox", "Fightmaster Kox")
    _story(db, npcs=[NPCEntry("Fightmaster Kox", hero_slug="kox")])
    with pytest.raises(ValueError, match="Fightmaster Kox"):
        _story(db, path="src/main-story/monarch/other-page.md", npcs=[NPCEntry("Fightmaster Kox")])
    # The stored claim survived the refused declaration untouched.
    cid = lore_character_id("Fightmaster Kox")
    row = db.conn.execute("SELECT character_id FROM character_heroes WHERE canonical_id = ?", [hid]).fetchone()
    assert row is not None
    assert row["character_id"] == cid


def test_hero_slug_empty_is_a_no_op_for_an_ordinary_npc(db: Database) -> None:
    """The overwhelmingly common case: an NPC whose name matches no hero."""
    _story(db, npcs=[NPCEntry("Some Ordinary Guard")])
    assert db.conn.execute("SELECT COUNT(*) FROM character_heroes").fetchone()[0] == 0


def test_unknown_hero_slug_raises(db: Database) -> None:
    with pytest.raises(ValueError, match="kox"):
        _story(db, npcs=[NPCEntry("Fightmaster Kox", hero_slug="kox")])


def test_two_npcs_claiming_the_same_slug_raises(db: Database) -> None:
    _seed_hero(db, "kox", "Fightmaster Kox")
    with pytest.raises(ValueError, match="kox"):
        _story(
            db,
            npcs=[
                NPCEntry("Fightmaster Kox", hero_slug="kox"),
                NPCEntry("Some Other Name", hero_slug="kox"),
            ],
        )


# ---------------------------------------------------------------------------
# The hero-name guard
# ---------------------------------------------------------------------------


def test_npc_matching_a_hero_name_without_hero_slug_still_raises(db: Database) -> None:
    _seed_hero(db, "kox", "Fightmaster Kox")
    with pytest.raises(ValueError, match="Fightmaster Kox"):
        _story(db, npcs=[NPCEntry("Fightmaster Kox")])


def test_npc_matching_a_hero_name_with_hero_slug_is_allowed(db: Database) -> None:
    _seed_hero(db, "kox", "Fightmaster Kox")
    record = _story(db, npcs=[NPCEntry("Fightmaster Kox", hero_slug="kox")])
    assert record is not None


# ---------------------------------------------------------------------------
# Self-healing at seed time
# ---------------------------------------------------------------------------


def test_seeding_mints_a_character_row_for_every_hero(tmp_path) -> None:
    (tmp_path / "csv").mkdir()
    from pipe_csv_io import write_pipe_csv_autogen

    write_pipe_csv_autogen(
        tmp_path / "csv" / "heroes-canonical.csv",
        ["CanonicalId", "CanonicalSlug", "CanonicalHero"],
        [{"CanonicalId": canonical_id("kox"), "CanonicalSlug": "kox", "CanonicalHero": "Fightmaster Kox"}],
        regenerate_command="test",
    )
    database = Database.from_csv(tmp_path / "db.sqlite", data_dir=tmp_path)
    cid = lore_character_id("Fightmaster Kox")
    row = database.conn.execute("SELECT name, status FROM characters WHERE character_id = ?", [cid]).fetchone()
    assert row is not None
    assert row["name"] == "Fightmaster Kox"
    assert row["status"] == "Unknown"
    link = database.conn.execute(
        "SELECT 1 FROM character_heroes WHERE canonical_id = ? AND character_id = ?", [canonical_id("kox"), cid]
    ).fetchone()
    assert link is not None


def test_self_heal_never_overwrites_an_explicit_resolution(tmp_path) -> None:
    """An existing character_heroes row always wins over the self-heal."""
    (tmp_path / "csv").mkdir()
    from pipe_csv_io import write_pipe_csv_autogen

    hero_cid = canonical_id("kox")
    write_pipe_csv_autogen(
        tmp_path / "csv" / "heroes-canonical.csv",
        ["CanonicalId", "CanonicalSlug", "CanonicalHero"],
        [{"CanonicalId": hero_cid, "CanonicalSlug": "kox", "CanonicalHero": "Fightmaster Kox"}],
        regenerate_command="test",
    )
    resolved_character_id = "LCmanualoverride0"
    write_pipe_csv_autogen(
        tmp_path / "csv" / "characters.csv",
        ["CharacterId", "Name", "Status", "OtherCharactersStoryKey"],
        [
            {
                "CharacterId": resolved_character_id,
                "Name": "Fightmaster Kox",
                "Status": "Alive",
                "OtherCharactersStoryKey": "",
            }
        ],
        regenerate_command="test",
    )
    write_pipe_csv_autogen(
        tmp_path / "csv" / "character-heroes.csv",
        ["CanonicalId", "CharacterId"],
        [{"CanonicalId": hero_cid, "CharacterId": resolved_character_id}],
        regenerate_command="test",
    )
    database = Database.from_csv(tmp_path / "db.sqlite", data_dir=tmp_path)
    link = database.conn.execute(
        "SELECT character_id FROM character_heroes WHERE canonical_id = ?", [hero_cid]
    ).fetchone()
    assert link["character_id"] == resolved_character_id
    minted = lore_character_id("Fightmaster Kox")
    assert database.conn.execute("SELECT 1 FROM characters WHERE character_id = ?", [minted]).fetchone() is None


# ---------------------------------------------------------------------------
# Status: closed vocabulary
# ---------------------------------------------------------------------------


def test_status_column_lives_on_characters(db: Database) -> None:
    cols = {r[1] for r in db.conn.execute("PRAGMA table_info(characters)")}
    assert "status" in cols


# ---------------------------------------------------------------------------
# Dry-run preview reports the new relation
# ---------------------------------------------------------------------------


def test_dry_run_reports_a_hero_slug_claim(db: Database, capsys) -> None:
    _seed_hero(db, "kox", "Fightmaster Kox")
    _story(db, npcs=[NPCEntry("Fightmaster Kox", hero_slug="kox")], dry_run=True)
    out = capsys.readouterr().out
    assert "kox" in out.lower()


def test_dry_run_reports_a_hero_slug_claim_reached_only_through_a_group_roster(db: Database, capsys) -> None:
    """``_reachable_entities()`` must be walked, not just the ``npcs`` kwarg."""
    _seed_hero(db, "kox", "Fightmaster Kox")
    group = GroupEntry("Boulders", npc_members=(NPCEntry("Fightmaster Kox", hero_slug="kox"),), member_source="x.md")
    _story(db, groups=[group], dry_run=True)
    out = capsys.readouterr().out
    assert "kox" in out.lower()
