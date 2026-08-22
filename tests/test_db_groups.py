"""Tests for the groups schema (migration 8) and locations.parent_location_id.

Covers the three failure modes the design work identified as the expensive ones:
a second spelling minting a second group row, a roster silently shrinking because
membership is replace-semantic, and a parent chain that loops.
"""

from __future__ import annotations

from pathlib import Path

import pytest

import db._queries as q
from db import Database, GroupEntry, LocationEntry, NPCEntry, SpeciesEntry
from registry_ids import canonical_id, group_id, lore_character_id


def _seed_hero(database: Database, slug: str, name: str) -> str:
    cid = canonical_id(slug)
    q.upsert_hero_canonical(database.conn, canonical_id=cid, canonical_slug=slug, canonical_hero=name)
    return cid


def _location_id_for(database: Database, name: str) -> str:
    row = database.conn.execute("SELECT location_id FROM locations WHERE name = ?", [name]).fetchone()
    return row[0]


def _story(database: Database, path: str = "src/main-story/super-slam/feudmasters.md", **kw):
    return database.upsert_story(path=path, story_type="main-story", title="T", **kw)


# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------


def test_migration_creates_group_tables_and_parent_column(db: Database) -> None:
    tables = {r[0] for r in db.conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    assert {"groups", "group_npcs", "group_heroes", "story_groups"} <= tables
    cols = {r[1] for r in db.conn.execute("PRAGMA table_info(locations)")}
    assert "parent_location_id" in cols


def test_schema_version_matches_constant(db: Database) -> None:
    """A migration block that outruns CURRENT_VERSION writes a block that can never fire."""
    from db._schema import CURRENT_VERSION

    assert db.conn.execute("PRAGMA user_version").fetchone()[0] == CURRENT_VERSION


def test_optional_id_columns_accept_empty_string(db: Database) -> None:
    """The reason these columns carry no SQL REFERENCES.

    They default to '' for the many rows with no parent and no location, and ''
    can never satisfy a foreign key — so an inline REFERENCES clause makes every
    insert of an ordinary row fail. validate_data.py checks them instead.
    """
    q.upsert_group(db.conn, group_id="GR1", name="Boulders")
    row = db.conn.execute("SELECT parent_group_id, location_id FROM groups").fetchone()
    assert (row["parent_group_id"], row["location_id"]) == ("", "")


# ---------------------------------------------------------------------------
# Identity
# ---------------------------------------------------------------------------


def test_group_id_hashes_the_name_alone(db: Database) -> None:
    assert group_id("Boulders") == group_id("  Boulders  ")
    assert group_id("Boulders") != group_id("Boulder Clan")


def test_second_spelling_mints_a_second_row(db: Database) -> None:
    """The Deathmatch Arena failure, in the group table.

    This is why plans/group-canonical-names.md exists and why every name is
    written once in entries/catalogue/groups.py.
    """
    _story(db, groups=[GroupEntry("Boulders", kind="guild")])
    _story(db, groups=[GroupEntry("Boulder Clan", kind="guild")])
    names = [r["name"] for r in q.select_all_groups(db.conn)]
    assert names == ["Boulder Clan", "Boulders"]


# ---------------------------------------------------------------------------
# Mentions (R5)
# ---------------------------------------------------------------------------


def test_story_groups_link_is_replace_semantic(db: Database) -> None:
    _story(db, groups=[GroupEntry("Prowlers"), GroupEntry("Gorelords")])
    assert len(q.select_story_junction(db.conn, _story(db).story_id, "story_groups", "group_id")) == 2
    _story(db, groups=[GroupEntry("Prowlers")])
    linked = q.select_story_junction(db.conn, _story(db).story_id, "story_groups", "group_id")
    assert linked == [group_id("Prowlers")]


def test_groups_none_leaves_links_untouched(db: Database) -> None:
    _story(db, groups=[GroupEntry("Prowlers")])
    _story(db, groups=None)
    assert q.select_story_junction(db.conn, _story(db).story_id, "story_groups", "group_id") == [group_id("Prowlers")]


def test_groups_empty_list_clears_links(db: Database) -> None:
    _story(db, groups=[GroupEntry("Prowlers")])
    _story(db, groups=[])
    assert q.select_story_junction(db.conn, _story(db).story_id, "story_groups", "group_id") == []


# ---------------------------------------------------------------------------
# Membership (R1)
# ---------------------------------------------------------------------------


def test_npc_membership_is_written_from_the_group(db: Database) -> None:
    entry = GroupEntry(
        "VanGeld",
        kind="clan",
        npc_members=(NPCEntry("Tara VanGeld", species=SpeciesEntry("Dwarf")),),
        member_source="heroes-of-rathe/lyath-about.md",
    )
    _story(db, groups=[entry])
    members = q.select_group_members(db.conn, group_id("VanGeld"), "group_npcs", "character_id")
    assert members == [(lore_character_id("Tara VanGeld"), "heroes-of-rathe/lyath-about.md")]


def test_a_member_may_cite_its_own_page(db: Database) -> None:
    """The Maela shape: one roster, members attested on different pages.

    ``member_source`` is one string for the group, which is right for the eleven
    rosters read off a single page and wrong for the one assembled from separate
    attestations. A member written as an ``(npc, story_key)`` pair keeps its own.
    """
    entry = GroupEntry(
        "The Maela",
        kind="troupe",
        npc_members=(
            (NPCEntry("Maela Fairmind"), "flavour/compendium-of-rathe.md"),
            (NPCEntry("Kaysin"), "flavour/rosetta.md"),
        ),
    )
    _story(db, groups=[entry])
    assert q.select_group_members(db.conn, group_id("The Maela"), "group_npcs", "character_id") == [
        (lore_character_id("Maela Fairmind"), "flavour/compendium-of-rathe.md"),
        (lore_character_id("Kaysin"), "flavour/rosetta.md"),
    ]


def test_plain_and_paired_members_mix_in_one_roster(db: Database) -> None:
    """A pair overrides ``member_source``; a bare entry still inherits it."""
    entry = GroupEntry(
        "Gemini",
        npc_members=(NPCEntry("Minerva"), (NPCEntry("Themis"), "flavour/outsiders.md")),
        member_source="heroes-of-rathe/lyath-about.md",
    )
    _story(db, groups=[entry])
    assert q.select_group_members(db.conn, group_id("Gemini"), "group_npcs", "character_id") == [
        (lore_character_id("Minerva"), "heroes-of-rathe/lyath-about.md"),
        (lore_character_id("Themis"), "flavour/outsiders.md"),
    ]


def test_a_paired_member_is_reachable_from_the_preview(db: Database) -> None:
    """The nesting bug 2116c48e fixed must not reopen through the new pair.

    ``_reachable_entities`` walks into ``npc_members`` so an epithet on a member
    reached only through a roster is previewed. The pair wraps that member in a
    tuple, and a walk that forgot to unwrap it would silently stop previewing.
    """
    entry = GroupEntry(
        "The Maela",
        npc_members=((NPCEntry("Kaysin", epithets=("Maela Soothsayer",)), "flavour/rosetta.md"),),
    )
    _story(db, groups=[entry])
    assert q.select_npc_epithets(db.conn, lore_character_id("Kaysin")) == [("Maela Soothsayer", "epithet")]


def test_hero_membership_resolves_slugs(db: Database) -> None:
    cid = _seed_hero(db, "kayo", "Kayo")
    _story(db, groups=[GroupEntry("Prowlers", hero_members=("kayo",))])
    assert q.select_group_members(db.conn, group_id("Prowlers"), "group_heroes", "canonical_id") == [(cid, "")]


def test_unknown_hero_slug_raises(db: Database) -> None:
    with pytest.raises(ValueError):
        _story(db, groups=[GroupEntry("Prowlers", hero_members=("no-such-hero",))])


def test_membership_is_replace_semantic(db: Database) -> None:
    """A short roster drops people, which is why the dry run reports removals."""
    two = GroupEntry("Gemini", npc_members=(NPCEntry("Minerva"), NPCEntry("Themis")))
    _story(db, groups=[two])
    assert len(q.select_group_members(db.conn, group_id("Gemini"), "group_npcs", "character_id")) == 2
    _story(db, groups=[GroupEntry("Gemini", npc_members=(NPCEntry("Minerva"),))])
    assert len(q.select_group_members(db.conn, group_id("Gemini"), "group_npcs", "character_id")) == 1


def test_emptied_roster_is_a_deletion_not_a_no_op(db: Database) -> None:
    """An empty roster is still a roster, and replace-semantics must honour it.

    The write path once guarded each ``set_group_members`` call on a truthy roster,
    so emptying one left every stored member in place while the dry run went on
    announcing their removal — the preview lying in exactly the case it exists for.
    """
    _story(db, groups=[GroupEntry("Gemini", npc_members=(NPCEntry("Minerva"), NPCEntry("Themis")))])
    _story(db, groups=[GroupEntry("Gemini")])
    assert q.select_group_members(db.conn, group_id("Gemini"), "group_npcs", "character_id") == []


def test_one_roster_emptied_while_the_other_stands(db: Database, capsys) -> None:
    """The original defect's exact shape: npcs cleared, heroes kept.

    Here the old reporter did print a removal line — the sibling roster kept its
    ``continue`` from firing — while the old write path skipped the delete. Preview
    and apply now agree.
    """
    _seed_hero(db, "minerva", "Minerva")
    _story(
        db,
        groups=[GroupEntry("Gemini", npc_members=(NPCEntry("Themis"),), hero_members=("minerva",))],
    )
    capsys.readouterr()
    kept = GroupEntry("Gemini", hero_members=("minerva",))
    db.upsert_story(
        path="src/main-story/super-slam/feudmasters.md",
        story_type="main-story",
        title="T",
        groups=[kept],
        dry_run=True,
    )
    assert "1 member(s) REMOVED from group_npcs" in capsys.readouterr().out
    _story(db, groups=[kept])
    assert q.select_group_members(db.conn, group_id("Gemini"), "group_npcs", "character_id") == []
    assert len(q.select_group_members(db.conn, group_id("Gemini"), "group_heroes", "canonical_id")) == 1


def test_emptied_hero_roster_is_a_deletion_too(db: Database) -> None:
    _seed_hero(db, "ira", "Ira")
    _story(db, groups=[GroupEntry("Ikaru Clan", hero_members=("ira",))])
    assert len(q.select_group_members(db.conn, group_id("Ikaru Clan"), "group_heroes", "canonical_id")) == 1
    _story(db, groups=[GroupEntry("Ikaru Clan")])
    assert q.select_group_members(db.conn, group_id("Ikaru Clan"), "group_heroes", "canonical_id") == []


def test_dry_run_removal_line_matches_what_the_apply_does(db: Database, capsys) -> None:
    """The preview and the write must agree about an emptied roster."""
    _story(db, groups=[GroupEntry("Gemini", npc_members=(NPCEntry("Minerva"), NPCEntry("Themis")))])
    capsys.readouterr()
    db.upsert_story(
        path="src/main-story/super-slam/feudmasters.md",
        story_type="main-story",
        title="T",
        groups=[GroupEntry("Gemini")],
        dry_run=True,
    )
    assert "2 member(s) REMOVED from group_npcs" in capsys.readouterr().out
    _story(db, groups=[GroupEntry("Gemini")])
    assert q.select_group_members(db.conn, group_id("Gemini"), "group_npcs", "character_id") == []


# ---------------------------------------------------------------------------
# Hierarchy
# ---------------------------------------------------------------------------


def test_parent_group_is_upserted_before_the_child(db: Database) -> None:
    parent = GroupEntry("Boulder Clan", kind="clan")
    child = GroupEntry("Boulders", kind="guild", parent=parent)
    _story(db, groups=[child])
    row = db.conn.execute("SELECT parent_group_id FROM groups WHERE group_id = ?", [group_id("Boulders")]).fetchone()
    assert row["parent_group_id"] == group_id("Boulder Clan")


def test_group_parent_cycle_raises_rather_than_looping(db: Database) -> None:
    a = GroupEntry("A")
    b = GroupEntry("B", parent=a)
    looped = GroupEntry("A", parent=b)
    with pytest.raises(ValueError, match="Cycle"):
        _story(db, groups=[looped])


def test_group_location_link_is_stored(db: Database) -> None:
    """Teklo Industries is the one group that is genuinely also a place."""
    entry = GroupEntry(
        "Teklo Industries", kind="corporation", location=LocationEntry("Teklo Industries", region="Metrix")
    )
    _story(db, groups=[entry])
    row = db.conn.execute("SELECT location_id FROM groups").fetchone()
    assert row["location_id"]
    assert db.conn.execute("SELECT name FROM locations WHERE location_id = ?", [row["location_id"]]).fetchone()["name"]


# ---------------------------------------------------------------------------
# locations.parent_location_id (R7)
# ---------------------------------------------------------------------------


def test_location_parent_is_stored(db: Database) -> None:
    maw = LocationEntry("The Maw", region="The Pits")
    _story(db, locations=[LocationEntry("Blockhead Territory", region="The Pits", parent=maw)])
    row = db.conn.execute("SELECT parent_location_id FROM locations WHERE name = ?", ["Blockhead Territory"]).fetchone()
    assert row["parent_location_id"]


def test_location_parent_cycle_raises(db: Database) -> None:
    a = LocationEntry("A", region="Aria")
    b = LocationEntry("B", region="Aria", parent=a)
    with pytest.raises(ValueError, match="Cycle"):
        _story(db, locations=[LocationEntry("A", region="Aria", parent=b)])


def test_location_parent_preserves_on_empty(db: Database) -> None:
    """An omitted parent must not clear a curated one, as notes already behave."""
    maw = LocationEntry("The Maw", region="The Pits")
    _story(db, locations=[LocationEntry("Blockhead Territory", region="The Pits", parent=maw)])
    _story(db, locations=[LocationEntry("Blockhead Territory", region="The Pits")])
    row = db.conn.execute("SELECT parent_location_id FROM locations WHERE name = ?", ["Blockhead Territory"]).fetchone()
    assert row["parent_location_id"]


# ---------------------------------------------------------------------------
# Round trip
# ---------------------------------------------------------------------------


def test_groups_survive_the_csv_round_trip(db: Database, tmp_path: Path) -> None:
    import db._export as ex
    from db._seed import seed_from_csvs

    cid = _seed_hero(db, "kayo", "Kayo")
    parent = GroupEntry("Boulder Clan", kind="clan")
    _story(
        db,
        groups=[
            GroupEntry("Boulders", kind="guild", parent=parent),
            GroupEntry("Prowlers", kind="guild", hero_members=("kayo",), member_source="x.md"),
        ],
    )
    ex.export_registry_tables(db.conn, tmp_path)
    ex.export_story_junctions(db.conn, tmp_path)

    fresh = Database(":memory:", data_dir=tmp_path)
    q.upsert_hero_canonical(fresh.conn, canonical_id=cid, canonical_slug="kayo", canonical_hero="Kayo")
    seed_from_csvs(fresh.conn, tmp_path)

    assert [r["name"] for r in q.select_all_groups(fresh.conn)] == ["Boulder Clan", "Boulders", "Prowlers"]
    row = fresh.conn.execute("SELECT parent_group_id FROM groups WHERE group_id = ?", [group_id("Boulders")]).fetchone()
    assert row["parent_group_id"] == group_id("Boulder Clan")
    assert q.select_group_members(fresh.conn, group_id("Prowlers"), "group_heroes", "canonical_id") == [(cid, "x.md")]


def test_seeding_wires_parents_even_when_the_child_is_read_first(db: Database, tmp_path: Path) -> None:
    """The CSV is sorted by name, so a child routinely precedes its parent.

    'Boulders' sorts after 'Boulder Clan', but 'Arcane Hall' precedes 'Auric
    Keep' — setting the parent inline would then fail on a foreign key. Both
    seeders insert every row first and wire parents in a second pass.
    """
    import db._export as ex
    from db._seed import seed_from_csvs

    keep = LocationEntry("Auric Keep", region="Nebulus Rift")
    _story(db, locations=[LocationEntry("Arcane Hall", region="Nebulus Rift", parent=keep)])
    ex.export_registry_tables(db.conn, tmp_path)

    names = [r["Name"] for r in _rows(tmp_path / "csv" / "locations.csv")]
    assert names.index("Arcane Hall") < names.index("Auric Keep")

    fresh = Database(":memory:", data_dir=tmp_path)
    seed_from_csvs(fresh.conn, tmp_path)
    row = fresh.conn.execute("SELECT parent_location_id FROM locations WHERE name = 'Arcane Hall'").fetchone()
    assert row["parent_location_id"]


def _rows(path: Path) -> list[dict[str, str]]:
    from pipe_csv_io import read_pipe_csv

    _, rows = read_pipe_csv(path)
    return rows


# ---------------------------------------------------------------------------
# Dry run
# ---------------------------------------------------------------------------


def test_dry_run_reports_new_groups_and_writes_nothing(db: Database, capsys) -> None:
    db.upsert_story(
        path="src/main-story/super-slam/feudmasters.md",
        story_type="main-story",
        title="T",
        groups=[GroupEntry("Prowlers", kind="guild")],
        dry_run=True,
    )
    printed = capsys.readouterr().out
    assert "Prowlers (new group" in printed
    assert q.select_all_groups(db.conn) == []
    assert db.conn.execute("SELECT COUNT(*) FROM story_groups").fetchone()[0] == 0


def test_dry_run_flags_a_roster_that_would_shrink(db: Database, capsys) -> None:
    """The removal line is the point: membership replaces, so a short roster drops people."""
    _story(db, groups=[GroupEntry("Gemini", npc_members=(NPCEntry("Minerva"), NPCEntry("Themis")))])
    capsys.readouterr()
    db.upsert_story(
        path="src/main-story/super-slam/feudmasters.md",
        story_type="main-story",
        title="T",
        groups=[GroupEntry("Gemini", npc_members=(NPCEntry("Minerva"),))],
        dry_run=True,
    )
    assert "REMOVED from group_npcs" in capsys.readouterr().out


# ---------------------------------------------------------------------------
# set_location_parent — containment written by name, not by declaration
# ---------------------------------------------------------------------------


def test_set_location_parent_writes_the_link(db: Database) -> None:
    _story(db, locations=[LocationEntry("The Maw", region="The Pits"), LocationEntry("Sori 16", region="The Pits")])
    db.set_location_parent("Sori 16", "The Maw")
    row = db.conn.execute("SELECT parent_location_id FROM locations WHERE name = 'Sori 16'").fetchone()
    assert row["parent_location_id"]


def test_set_location_parent_does_not_need_a_declaration(db: Database) -> None:
    """The reason containment lives here and not on the catalogue entry.

    Five of the nineteen reviewed containments involve locations that no story
    declaration names, so a `parent=` on the catalogue constant would never run.
    Writing by name reaches every row that exists.
    """
    _story(db, locations=[LocationEntry("Ankomeido", region="The Pits")])
    q.upsert_location(db.conn, location_id="LOx", name="Orphan Street", region_id="")
    db.set_location_parent("Orphan Street", "Ankomeido")
    row = db.conn.execute("SELECT parent_location_id FROM locations WHERE name = 'Orphan Street'").fetchone()
    assert row["parent_location_id"]


def test_set_location_parent_rejects_a_missing_location(db: Database) -> None:
    _story(db, locations=[LocationEntry("The Maw", region="The Pits")])
    with pytest.raises(ValueError, match="Location not found"):
        db.set_location_parent("Nowhere", "The Maw")
    with pytest.raises(ValueError, match="Parent location not found"):
        db.set_location_parent("The Maw", "Nowhere")


def test_set_location_parent_rejects_self_containment(db: Database) -> None:
    _story(db, locations=[LocationEntry("The Maw", region="The Pits")])
    with pytest.raises(ValueError, match="cannot contain itself"):
        db.set_location_parent("The Maw", "The Maw")


def test_set_location_parent_rejects_a_cycle(db: Database) -> None:
    _story(
        db,
        locations=[
            LocationEntry("Ankomeido", region="The Pits"),
            LocationEntry("Sori 16", region="The Pits"),
            LocationEntry("The Leaf House", region="The Pits"),
        ],
    )
    db.set_location_parent("Sori 16", "Ankomeido")
    db.set_location_parent("The Leaf House", "Sori 16")
    with pytest.raises(ValueError, match="cycle"):
        db.set_location_parent("Ankomeido", "The Leaf House")


def test_set_location_parent_rejects_an_ambiguous_name(db: Database) -> None:
    """Two rows under one name is the Deathmatch Arena fork; refuse rather than guess."""
    _story(db, locations=[LocationEntry("The Maw", region="The Pits")])
    q.upsert_location(db.conn, location_id="LOdup1", name="Twin", region_id="")
    q.upsert_location(db.conn, location_id="LOdup2", name="Twin", region_id="RGother")
    with pytest.raises(ValueError, match="matches 2 rows"):
        db.set_location_parent("Twin", "The Maw")


# ---------------------------------------------------------------------------
# update_description("group", …) — group notes come from descriptions.py
# ---------------------------------------------------------------------------


def test_update_description_writes_group_notes(db: Database) -> None:
    """Groups take their tooltip summary the same way locations take theirs.

    D3 requires the summary to live in exactly one place. `descriptions.py` is
    that place, so the supplement entry can be deleted in the same commit without
    the tooltip going dark.
    """
    _story(db, groups=[GroupEntry("Hand of Sol", kind="order")])
    db.update_description("group", "Hand of Sol", "Solana's order of knights.")
    row = db.conn.execute("SELECT notes FROM groups WHERE name = 'Hand of Sol'").fetchone()
    assert row["notes"] == "Solana's order of knights."


def test_update_description_rejects_a_group_with_no_row(db: Database) -> None:
    """The ordering constraint, made loud.

    A group row only exists once a story declaration names it. Six catalogue
    constants have no row yet, so a note written before the re-point would
    silently never apply — this raises instead.
    """
    with pytest.raises(ValueError, match="Group not found"):
        db.update_description("group", "Ikaru Clan", "Never applied.")


def test_update_description_group_notes_reach_the_csv(db: Database) -> None:
    _story(db, groups=[GroupEntry("Wardens", kind="order")])
    db.update_description("group", "Wardens", "Keepers of the wood.")
    text = (db._data_dir / "csv" / "groups.csv").read_text(encoding="utf-8")
    assert "Keepers of the wood." in text


# ---------------------------------------------------------------------------
# lore_story_key / lore_fragment — where a group is documented (migration 9)
# ---------------------------------------------------------------------------


def test_group_carries_its_own_documentation_page(db: Database) -> None:
    """The reason groups need two columns where a location needs one.

    A location reaches its page by walking region_id to the region's
    world_of_rathe_story_key. A group has no region to walk — it is not tied to
    one place — so it carries the page itself.
    """
    _story(
        db,
        groups=[
            GroupEntry(
                "Hand of Sol",
                kind="order of knights",
                lore_story_key="world-of-rathe/solana.md",
                lore_fragment="the-hand-of-sol",
            )
        ],
    )
    row = db.conn.execute("SELECT lore_story_key, lore_fragment FROM groups WHERE name = 'Hand of Sol'").fetchone()
    assert row["lore_story_key"] == "world-of-rathe/solana.md"
    assert row["lore_fragment"] == "the-hand-of-sol"


def test_group_documentation_survives_a_declaration_that_omits_it(db: Database) -> None:
    """Curated fields are never cleared by a caller that leaves them out.

    Same rule as notes: an empty incoming value keeps what is stored, because a
    story declaration that merely mentions a group must not blank its link.
    """
    full = GroupEntry(
        "Hand of Sol",
        kind="order of knights",
        lore_story_key="world-of-rathe/solana.md",
        lore_fragment="the-hand-of-sol",
    )
    _story(db, groups=[full])
    _story(db, path="src/main-story/monarch/sworn-to-protect.md", groups=[GroupEntry("Hand of Sol")])
    row = db.conn.execute("SELECT lore_story_key, lore_fragment FROM groups WHERE name = 'Hand of Sol'").fetchone()
    assert row["lore_story_key"] == "world-of-rathe/solana.md"
    assert row["lore_fragment"] == "the-hand-of-sol"


def test_group_documentation_reaches_the_csv(db: Database) -> None:
    _story(
        db,
        groups=[GroupEntry("Gemini", lore_story_key="world-of-rathe/solana.md", lore_fragment="gemini")],
    )
    text = (db._data_dir / "csv" / "groups.csv").read_text(encoding="utf-8")
    assert "LoreStoryKey|LoreFragment" in text
    assert "world-of-rathe/solana.md|gemini" in text


# ---------------------------------------------------------------------------
# Alternate names — epithets (R4) and aliases (R6)
# ---------------------------------------------------------------------------


def test_npc_epithets_are_stored_with_their_kind(db: Database) -> None:
    entry = NPCEntry("Dr. Krest Mortimer", epithets=("'The Fixer'",), short_names=("Mortimer",))
    _story(db, characters=[entry])
    stored = q.select_npc_epithets(db.conn, lore_character_id("Dr. Krest Mortimer"))
    assert stored == [("'The Fixer'", "epithet"), ("Mortimer", "short-name")]


def test_npc_epithets_keep_declared_order(db: Database) -> None:
    """Suraya holds three, and which one a tooltip prints first is the declared one."""
    three = ("Archangel of Knowledge", "Archangel of Erudition", "Arcane Herald")
    _story(db, characters=[NPCEntry("Suraya", epithets=three)])
    stored = q.select_npc_epithets(db.conn, lore_character_id("Suraya"))
    assert [name for name, _kind in stored] == list(three)


def test_epithets_are_replace_semantic(db: Database) -> None:
    _story(db, characters=[NPCEntry("Bellona", epithets=("the Wartune Herald", "Archangel of War"))])
    _story(db, characters=[NPCEntry("Bellona", epithets=("the Wartune Herald",))])
    stored = q.select_npc_epithets(db.conn, lore_character_id("Bellona"))
    assert [name for name, _kind in stored] == ["the Wartune Herald"]


def test_emptied_epithets_are_a_deletion(db: Database) -> None:
    """Same rule the rosters follow, for the same reason — and the same past bug."""
    _story(db, characters=[NPCEntry("Bellona", epithets=("Archangel of War",))])
    _story(db, characters=[NPCEntry("Bellona")])
    assert q.select_npc_epithets(db.conn, lore_character_id("Bellona")) == []


def test_location_alias_carries_its_era(db: Database) -> None:
    entry = LocationEntry("Coralysi", aliases=(("Fedhari", "Dhani"), "Fiddler's Green"))
    _story(db, locations=[entry])
    lid = _location_id_for(db, "Coralysi")
    assert q.select_location_aliases(db.conn, lid) == [("Fedhari", "Dhani"), ("Fiddler's Green", "")]


def test_group_alias_is_stored(db: Database) -> None:
    _story(db, groups=[GroupEntry("Mendacity Media", aliases=("Mendacity",))])
    assert q.select_group_aliases(db.conn, group_id("Mendacity Media")) == ["Mendacity"]


def test_group_aliases_are_replace_semantic(db: Database) -> None:
    _story(db, groups=[GroupEntry("Mendacity Media", aliases=("Mendacity", "Voxx"))])
    _story(db, groups=[GroupEntry("Mendacity Media", aliases=("Mendacity",))])
    assert q.select_group_aliases(db.conn, group_id("Mendacity Media")) == ["Mendacity"]


def test_dry_run_reports_an_alias_it_would_remove(db: Database, capsys) -> None:
    _story(db, groups=[GroupEntry("Mendacity Media", aliases=("Mendacity",))])
    capsys.readouterr()
    db.upsert_story(
        path="src/main-story/super-slam/feudmasters.md",
        story_type="main-story",
        title="T",
        groups=[GroupEntry("Mendacity Media")],
        dry_run=True,
    )
    assert "alias 'Mendacity' REMOVED" in capsys.readouterr().out


def test_alternate_names_survive_the_csv_round_trip(db: Database, tmp_path: Path) -> None:
    _story(
        db,
        characters=[NPCEntry("Bellona", epithets=("Archangel of War",))],
        locations=[LocationEntry("Coralysi", aliases=(("Fedhari", "Dhani"),))],
        groups=[GroupEntry("Mendacity Media", aliases=("Mendacity",))],
    )
    import db._export as _export

    _export.export_all(db.conn, tmp_path)
    fresh = Database(str(tmp_path / "round-trip.db"), data_dir=tmp_path)
    assert q.select_npc_epithets(fresh.conn, lore_character_id("Bellona")) == [("Archangel of War", "epithet")]
    assert q.select_group_aliases(fresh.conn, group_id("Mendacity Media")) == ["Mendacity"]


# ---------------------------------------------------------------------------
# The preview reaches as far as the write does
# ---------------------------------------------------------------------------
#
# ``_upsert_one_group`` walks into ``parent``, ``location`` and ``npc_members``,
# and ``_upsert_locations`` walks into ``parent``. Each of those writes the
# entity's alternate names, so a preview that read only the kwargs left a nested
# change applying in silence — the same shape as the guarded roster it replaced.
# Ozrim and Maela Fairmind are reachable through a group roster and nothing else.


def test_dry_run_reports_an_epithet_on_a_group_member(db: Database, capsys) -> None:
    _story(db, groups=[GroupEntry("Rosetta", npc_members=(NPCEntry("Ozrim"),))])
    capsys.readouterr()
    db.upsert_story(
        path="src/main-story/super-slam/feudmasters.md",
        story_type="main-story",
        title="T",
        groups=[GroupEntry("Rosetta", npc_members=(NPCEntry("Ozrim", epithets=("Keeper of the Script",)),))],
        dry_run=True,
    )
    assert "Ozrim: epithet 'Keeper of the Script'" in capsys.readouterr().out


def test_dry_run_reports_an_alias_on_a_groups_location(db: Database, capsys) -> None:
    _story(db, groups=[GroupEntry("The Maela", location=LocationEntry("The Everfest Carnival"))])
    capsys.readouterr()
    db.upsert_story(
        path="src/main-story/super-slam/feudmasters.md",
        story_type="main-story",
        title="T",
        groups=[GroupEntry("The Maela", location=LocationEntry("The Everfest Carnival", aliases=("The Carnival",)))],
        dry_run=True,
    )
    assert "The Everfest Carnival: alias 'The Carnival'" in capsys.readouterr().out


def test_dry_run_reports_an_alias_on_a_parent_location(db: Database, capsys) -> None:
    _story(db, locations=[LocationEntry("Shyldverk", parent=LocationEntry("Mt. Isen", aliases=("Isen's Peak",)))])
    capsys.readouterr()
    db.upsert_story(
        path="src/main-story/super-slam/feudmasters.md",
        story_type="main-story",
        title="T",
        locations=[LocationEntry("Shyldverk", parent=LocationEntry("Mt. Isen"))],
        dry_run=True,
    )
    assert 'Mt. Isen: alias "Isen\'s Peak" REMOVED' in capsys.readouterr().out


def test_dry_run_reports_an_alias_on_a_parent_group(db: Database, capsys) -> None:
    _story(db, groups=[GroupEntry("Sayashi", parent=GroupEntry("Mendacity Media", aliases=("Mendacity",)))])
    capsys.readouterr()
    db.upsert_story(
        path="src/main-story/super-slam/feudmasters.md",
        story_type="main-story",
        title="T",
        groups=[GroupEntry("Sayashi", parent=GroupEntry("Mendacity Media"))],
        dry_run=True,
    )
    assert "Mendacity Media: alias 'Mendacity' REMOVED" in capsys.readouterr().out


def test_preview_reports_a_nested_entity_only_once(db: Database, capsys) -> None:
    """A group's location named at top level too must not print twice."""
    carnival = LocationEntry("The Everfest Carnival", aliases=("The Carnival",))
    capsys.readouterr()
    db.upsert_story(
        path="src/main-story/super-slam/feudmasters.md",
        story_type="main-story",
        title="T",
        locations=[carnival],
        groups=[GroupEntry("The Maela", location=carnival)],
        dry_run=True,
    )
    assert capsys.readouterr().out.count("The Everfest Carnival: alias 'The Carnival'") == 1


def test_preview_survives_a_parent_cycle_rather_than_looping(db: Database, capsys) -> None:
    """The write path raises on a cycle, but the preview runs first."""
    outer = GroupEntry("Prowlers")
    looped = GroupEntry("Gorelords", parent=outer)
    object.__setattr__(outer, "parent", looped)
    db.upsert_story(
        path="src/main-story/super-slam/feudmasters.md",
        story_type="main-story",
        title="T",
        groups=[looped],
        dry_run=True,
    )
    assert "DRY RUN" in capsys.readouterr().out


def test_a_roster_may_not_name_one_npc_twice(db: Database) -> None:
    """The pair made this reachable, and the two paths resolved it differently.

    ``group_npcs`` is keyed ``(group_id, character_id)`` and written with
    ``INSERT OR IGNORE``, so the write kept the first citation; the preview built
    a dict from the same roster and reported the last. Neither raised. A roster
    naming someone twice was previewed as one page and stored as another —
    the preview/write divergence 2116c48e and 034330d7 both fixed, in a new shape.
    """
    entry = GroupEntry(
        "The Maela",
        npc_members=(
            (NPCEntry("Kaysin"), "flavour/rosetta.md"),
            (NPCEntry("Kaysin"), "flavour/compendium-of-rathe.md"),
        ),
    )
    with pytest.raises(ValueError, match="twice in npc_members"):
        _story(db, groups=[entry])


def test_the_duplicate_guard_fires_on_the_preview_path_too(db: Database) -> None:
    """A dry run must fail the same way, or the guard only moves the surprise."""
    entry = GroupEntry("The Maela", npc_members=(NPCEntry("Kaysin"), NPCEntry("Kaysin")))
    with pytest.raises(ValueError, match="twice in npc_members"):
        _story(db, groups=[entry], dry_run=True)
