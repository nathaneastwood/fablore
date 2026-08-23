"""Tests for the titles schema (migration 13): titles, title_holders, story_titles.

Mirrors ``test_db_groups.py``. The one new hazard titles introduce that groups
never had: a holder may be named as a ``CharacterEntry`` *or* as a hero slug, and migration
12's identity spine means both can resolve to the same ``character_id`` — so a
person named once each way must be caught as a repeat, the same way
``GroupEntry.member_pairs()`` catches a repeated character.
"""

from __future__ import annotations

from pathlib import Path

import pytest

import db._queries as q
from db import Database, GroupEntry, CharacterEntry, TitleEntry
from registry_ids import canonical_id, group_id, lore_character_id, title_id


def _seed_hero(database: Database, slug: str, name: str) -> str:
    cid = canonical_id(slug)
    q.upsert_hero_canonical(database.conn, canonical_id=cid, canonical_slug=slug, canonical_hero=name)
    return cid


def _story(database: Database, path: str = "src/world-of-rathe/solana.md", **kw):
    return database.upsert_story(path=path, story_type="world-of-rathe", title="T", **kw)


# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------


def test_migration_creates_title_tables(db: Database) -> None:
    tables = {r[0] for r in db.conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    assert {"titles", "title_holders", "story_titles"} <= tables


def test_schema_version_matches_constant(db: Database) -> None:
    from db._schema import CURRENT_VERSION

    assert db.conn.execute("PRAGMA user_version").fetchone()[0] == CURRENT_VERSION


def test_group_id_column_accepts_empty_string(db: Database) -> None:
    """No SQL REFERENCES on titles.group_id — see the comment in _schema.py."""
    q.upsert_title(db.conn, title_id="TI1", name="Soothsayer")
    row = db.conn.execute("SELECT group_id FROM titles").fetchone()
    assert row["group_id"] == ""


# ---------------------------------------------------------------------------
# Identity
# ---------------------------------------------------------------------------


def test_title_id_hashes_the_name_alone(db: Database) -> None:
    assert title_id("Grand Magister") == title_id("  Grand Magister  ")
    assert title_id("Grand Magister") != title_id("Grand Magistrate")


def test_second_spelling_mints_a_second_title_row(db: Database) -> None:
    _story(db, titles=[TitleEntry("Grand Magister")])
    _story(db, titles=[TitleEntry("Grand Magistrate")])
    names = [r["name"] for r in q.select_all_titles(db.conn)]
    assert names == ["Grand Magister", "Grand Magistrate"]


# ---------------------------------------------------------------------------
# Mentions (R5)
# ---------------------------------------------------------------------------


def test_story_titles_link_is_replace_semantic(db: Database) -> None:
    _story(db, titles=[TitleEntry("Grand Magister"), TitleEntry("Soothsayer")])
    sid = _story(db).story_id
    assert len(q.select_story_junction(db.conn, sid, "story_titles", "title_id")) == 2
    _story(db, titles=[TitleEntry("Grand Magister")])
    linked = q.select_story_junction(db.conn, sid, "story_titles", "title_id")
    assert linked == [title_id("Grand Magister")]


def test_titles_none_leaves_links_untouched(db: Database) -> None:
    _story(db, titles=[TitleEntry("Grand Magister")])
    _story(db, titles=None)
    sid = _story(db).story_id
    assert q.select_story_junction(db.conn, sid, "story_titles", "title_id") == [title_id("Grand Magister")]


def test_titles_empty_list_clears_links(db: Database) -> None:
    _story(db, titles=[TitleEntry("Grand Magister")])
    _story(db, titles=[])
    sid = _story(db).story_id
    assert q.select_story_junction(db.conn, sid, "story_titles", "title_id") == []


# ---------------------------------------------------------------------------
# Holders (R3)
# ---------------------------------------------------------------------------


def test_an_entry_holder_is_written_from_the_title(db: Database) -> None:
    entry = TitleEntry(
        "Grand Magister",
        npc_holders=((CharacterEntry("Aeric"), 1, "world-of-rathe/solana.md"),),
    )
    _story(db, titles=[entry])
    holders = q.select_title_holders(db.conn, title_id("Grand Magister"))
    assert holders == [(lore_character_id("Aeric"), 1, "world-of-rathe/solana.md")]


def test_hero_holder_resolves_through_character_heroes(db: Database) -> None:
    """The point of the identity spine: a hero slug lands in the same column an entry-named character would."""
    hid = _seed_hero(db, "kano", "Kano")
    resolved_character_id = "LCmanualoverride0"
    q.upsert_character(db.conn, character_id=resolved_character_id, name="Kano")
    q.set_character_hero(db.conn, hid, resolved_character_id)

    entry = TitleEntry("Dracai of Aether", hero_holders=(("kano", 0, "heroes-of-rathe/kano-about.md"),))
    _story(db, titles=[entry])
    holders = q.select_title_holders(db.conn, title_id("Dracai of Aether"))
    assert holders == [(resolved_character_id, 0, "heroes-of-rathe/kano-about.md")]


def test_hero_holder_self_heals_character_heroes_when_missing(db: Database) -> None:
    """A hero with no character_heroes row yet still resolves cleanly."""
    hid = _seed_hero(db, "kano", "Kano")
    assert q.select_character_id_for_hero(db.conn, hid) is None

    entry = TitleEntry("Dracai of Aether", hero_holders=(("kano", 0, "x.md"),))
    _story(db, titles=[entry])

    minted = lore_character_id("Kano")
    assert q.select_character_id_for_hero(db.conn, hid) == minted
    assert q.select_title_holders(db.conn, title_id("Dracai of Aether")) == [(minted, 0, "x.md")]


def test_unknown_hero_slug_raises(db: Database) -> None:
    with pytest.raises(ValueError):
        _story(db, titles=[TitleEntry("Dracai of Aether", hero_holders=(("no-such-hero", 0, "x.md"),))])


def test_a_holder_may_not_be_named_twice_as_an_entry(db: Database) -> None:
    entry = TitleEntry(
        "Grand Magister",
        npc_holders=(
            (CharacterEntry("Aeric"), 1, "x.md"),
            (CharacterEntry("Aeric"), 2, "y.md"),
        ),
    )
    with pytest.raises(ValueError, match="Aeric"):
        _story(db, titles=[entry])


def test_a_holder_may_not_be_named_twice_as_hero_slug(db: Database) -> None:
    _seed_hero(db, "kano", "Kano")
    entry = TitleEntry(
        "Dracai of Aether",
        hero_holders=(
            ("kano", 0, "x.md"),
            ("kano", 1, "y.md"),
        ),
    )
    with pytest.raises(ValueError, match="kano"):
        _story(db, titles=[entry])


def test_the_same_person_may_not_be_named_as_both_entry_and_hero(db: Database) -> None:
    """The hazard migration 12 makes reachable: one character_id, two spellings."""
    _seed_hero(db, "kano", "Kano")
    _story(db, characters=[CharacterEntry("Kano", hero_slug="kano")])
    entry = TitleEntry(
        "Dracai of Aether",
        npc_holders=((CharacterEntry("Kano"), 0, "x.md"),),
        hero_holders=(("kano", 0, "y.md"),),
    )
    with pytest.raises(ValueError, match="Kano"):
        _story(db, titles=[entry])


def test_the_duplicate_guard_fires_on_the_preview_path_too(db: Database) -> None:
    entry = TitleEntry(
        "Grand Magister",
        npc_holders=((CharacterEntry("Aeric"), 1, "x.md"), (CharacterEntry("Aeric"), 2, "y.md")),
    )
    with pytest.raises(ValueError, match="Aeric"):
        _story(db, titles=[entry], dry_run=True)


def test_holders_are_replace_semantic(db: Database) -> None:
    two = TitleEntry(
        "Grand Magister",
        npc_holders=((CharacterEntry("Aeric"), 1, "x.md"), (CharacterEntry("Bellwyn"), 2, "x.md")),
    )
    _story(db, titles=[two])
    assert len(q.select_title_holders(db.conn, title_id("Grand Magister"))) == 2
    _story(db, titles=[TitleEntry("Grand Magister", npc_holders=((CharacterEntry("Aeric"), 1, "x.md"),))])
    assert len(q.select_title_holders(db.conn, title_id("Grand Magister"))) == 1


def test_emptied_holders_is_a_deletion_not_a_no_op(db: Database) -> None:
    _story(
        db,
        titles=[TitleEntry("Grand Magister", npc_holders=((CharacterEntry("Aeric"), 1, "x.md"),))],
    )
    _story(db, titles=[TitleEntry("Grand Magister")])
    assert q.select_title_holders(db.conn, title_id("Grand Magister")) == []


def test_ordinal_records_succession_and_is_not_unique(db: Database) -> None:
    """The Dracai shape: several holders, all ordinal 0, held concurrently."""
    entry = TitleEntry(
        "Dracai",
        npc_holders=((CharacterEntry("Aeric"), 0, "x.md"), (CharacterEntry("Bellwyn"), 0, "x.md")),
    )
    _story(db, titles=[entry])
    holders = q.select_title_holders(db.conn, title_id("Dracai"))
    assert {ordinal for _cid, ordinal, _src in holders} == {0}
    assert len(holders) == 2


def test_dry_run_removal_line_matches_what_the_apply_does(db: Database, capsys) -> None:
    _story(db, titles=[TitleEntry("Grand Magister", npc_holders=((CharacterEntry("Aeric"), 1, "x.md"),))])
    capsys.readouterr()
    db.upsert_story(
        path="src/world-of-rathe/solana.md",
        story_type="world-of-rathe",
        title="T",
        titles=[TitleEntry("Grand Magister")],
        dry_run=True,
    )
    assert "1 holder(s) REMOVED from title_holders" in capsys.readouterr().out
    _story(db, titles=[TitleEntry("Grand Magister")])
    assert q.select_title_holders(db.conn, title_id("Grand Magister")) == []


# ---------------------------------------------------------------------------
# group link
# ---------------------------------------------------------------------------


def test_title_group_link_is_stored(db: Database) -> None:
    grp = GroupEntry("Dracai Council")
    _story(db, titles=[TitleEntry("Dracai of Aether", group=grp)])
    row = db.conn.execute("SELECT group_id FROM titles WHERE name = 'Dracai of Aether'").fetchone()
    assert row["group_id"] == group_id("Dracai Council")


def test_title_group_link_preserves_on_empty(db: Database) -> None:
    grp = GroupEntry("Dracai Council")
    _story(db, titles=[TitleEntry("Dracai of Aether", group=grp)])
    _story(db, path="src/world-of-rathe/aria.md", titles=[TitleEntry("Dracai of Aether")])
    row = db.conn.execute("SELECT group_id FROM titles WHERE name = 'Dracai of Aether'").fetchone()
    assert row["group_id"] == group_id("Dracai Council")


def test_dry_run_reports_a_title_group_change(db: Database, capsys) -> None:
    _story(db, titles=[TitleEntry("Dracai of Aether")])
    capsys.readouterr()
    db.upsert_story(
        path="src/world-of-rathe/solana.md",
        story_type="world-of-rathe",
        title="T",
        titles=[TitleEntry("Dracai of Aether", group=GroupEntry("Dracai Council"))],
        dry_run=True,
    )
    assert "Dracai of Aether: group " in capsys.readouterr().out


# ---------------------------------------------------------------------------
# Round trip
# ---------------------------------------------------------------------------


def test_titles_survive_the_csv_round_trip(db: Database, tmp_path: Path) -> None:
    import db._export as ex
    from db._seed import seed_from_csvs

    hid = _seed_hero(db, "kano", "Kano")
    entry = TitleEntry(
        "Dracai of Aether",
        group=GroupEntry("Dracai Council"),
        npc_holders=((CharacterEntry("Aeric"), 1, "x.md"),),
        hero_holders=(("kano", 0, "y.md"),),
    )
    _story(db, titles=[entry])
    ex.export_registry_tables(db.conn, tmp_path)
    ex.export_story_junctions(db.conn, tmp_path)

    fresh = Database(":memory:", data_dir=tmp_path)
    q.upsert_hero_canonical(fresh.conn, canonical_id=hid, canonical_slug="kano", canonical_hero="Kano")
    seed_from_csvs(fresh.conn, tmp_path)

    assert [r["name"] for r in q.select_all_titles(fresh.conn)] == ["Dracai of Aether"]
    row = fresh.conn.execute("SELECT group_id FROM titles WHERE name = 'Dracai of Aether'").fetchone()
    assert row["group_id"] == group_id("Dracai Council")
    holders = q.select_title_holders(fresh.conn, title_id("Dracai of Aether"))
    assert len(holders) == 2


# ---------------------------------------------------------------------------
# Dry run
# ---------------------------------------------------------------------------


def test_dry_run_reports_new_titles_and_writes_nothing(db: Database, capsys) -> None:
    db.upsert_story(
        path="src/world-of-rathe/solana.md",
        story_type="world-of-rathe",
        title="T",
        titles=[TitleEntry("Grand Magister")],
        dry_run=True,
    )
    printed = capsys.readouterr().out
    assert "Grand Magister (new title" in printed
    assert q.select_all_titles(db.conn) == []
    assert db.conn.execute("SELECT COUNT(*) FROM story_titles").fetchone()[0] == 0


def test_dry_run_flags_a_holder_list_that_would_shrink(db: Database, capsys) -> None:
    entry = TitleEntry(
        "Grand Magister",
        npc_holders=((CharacterEntry("Aeric"), 1, "x.md"), (CharacterEntry("Bellwyn"), 2, "x.md")),
    )
    _story(db, titles=[entry])
    capsys.readouterr()
    db.upsert_story(
        path="src/world-of-rathe/solana.md",
        story_type="world-of-rathe",
        title="T",
        titles=[TitleEntry("Grand Magister", npc_holders=((CharacterEntry("Aeric"), 1, "x.md"),))],
        dry_run=True,
    )
    assert "REMOVED from title_holders" in capsys.readouterr().out


def test_dry_run_reports_an_epithet_on_a_title_holder(db: Database, capsys) -> None:
    """The preview reaches into npc_holders, the same way it reaches group rosters."""
    entry = TitleEntry("Grand Magister", npc_holders=((CharacterEntry("Aeric"), 1, "x.md"),))
    _story(db, titles=[entry])
    capsys.readouterr()
    db.upsert_story(
        path="src/world-of-rathe/solana.md",
        story_type="world-of-rathe",
        title="T",
        titles=[
            TitleEntry(
                "Grand Magister",
                npc_holders=((CharacterEntry("Aeric", epithets=("Keeper of the Light",)), 1, "x.md"),),
            )
        ],
        dry_run=True,
    )
    assert "Aeric: epithet 'Keeper of the Light'" in capsys.readouterr().out


def test_dry_run_reports_a_new_character_created_only_through_a_title(db: Database, capsys) -> None:
    db.upsert_story(
        path="src/world-of-rathe/solana.md",
        story_type="world-of-rathe",
        title="T",
        titles=[TitleEntry("Grand Magister", npc_holders=((CharacterEntry("Aeric"), 1, "x.md"),))],
        dry_run=True,
    )
    assert "+ Aeric" in capsys.readouterr().out


def test_dry_run_reaches_a_titles_group(db: Database, capsys) -> None:
    """A title's group is a GroupEntry — walking the title must also walk it."""
    grp = GroupEntry("Dracai Council", members=(CharacterEntry("Emissary"),), member_source="x.md")
    db.upsert_story(
        path="src/world-of-rathe/solana.md",
        story_type="world-of-rathe",
        title="T",
        titles=[TitleEntry("Dracai of Aether", group=grp)],
        dry_run=True,
    )
    assert "Dracai Council (new group" in capsys.readouterr().out


def test_preview_survives_the_dry_run_without_writing_a_hero_link(db: Database, capsys) -> None:
    """The read-only prediction path must never write character_heroes."""
    hid = _seed_hero(db, "kano", "Kano")
    db.upsert_story(
        path="src/world-of-rathe/solana.md",
        story_type="world-of-rathe",
        title="T",
        titles=[TitleEntry("Dracai of Aether", hero_holders=(("kano", 0, "x.md"),))],
        dry_run=True,
    )
    capsys.readouterr()
    assert q.select_character_id_for_hero(db.conn, hid) is None
    assert q.select_all_titles(db.conn) == []


# ---------------------------------------------------------------------------
# update_description("title", …) — title notes come from descriptions.py
# ---------------------------------------------------------------------------


def test_update_description_writes_title_notes(db: Database) -> None:
    _story(db, titles=[TitleEntry("Soothsayer")])
    db.update_description("title", "Soothsayer", "A seer who reads the future in ash and smoke.")
    row = db.conn.execute("SELECT notes FROM titles WHERE name = 'Soothsayer'").fetchone()
    assert row["notes"] == "A seer who reads the future in ash and smoke."


def test_update_description_rejects_a_title_with_no_row(db: Database) -> None:
    with pytest.raises(ValueError, match="Title not found"):
        db.update_description("title", "Soothsayer", "Never applied.")


def test_update_description_title_notes_reach_the_csv(db: Database) -> None:
    _story(db, titles=[TitleEntry("Soothsayer")])
    db.update_description("title", "Soothsayer", "A seer.")
    text = (db._data_dir / "csv" / "titles.csv").read_text(encoding="utf-8")
    assert "A seer." in text
