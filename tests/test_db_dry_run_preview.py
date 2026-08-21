"""Tests for what ``upsert_story(dry_run=True)`` actually previews.

The preview is the guard in a preview-then-commit workflow, so anything the
commit path writes has to show up here. Historically it only diffed junction
*membership* by display name, which left entity attribute writes — and the
``story_heroes.fragment`` column — invisible: a declaration could silently
clear a curated value, or fork a second registry row, and the preview would
report nothing at all.

Seam: the public ``Database.upsert_story(..., dry_run=True)`` and the report
it prints. Tests assert on that report, never on internals.
"""

from __future__ import annotations

from pathlib import Path

import db._queries as q
from db import (
    Database,
    FaunaEntry,
    GroupEntry,
    FoodDrinkEntry,
    LocationEntry,
    NPCEntry,
    NarratedVideoEntry,
    RegionEntry,
    SpeciesEntry,
)


def _seed_hero(database: Database, slug: str, name: str) -> str:
    from registry_ids import canonical_id

    cid = canonical_id(slug)
    q.upsert_hero_canonical(database.conn, canonical_id=cid, canonical_slug=slug, canonical_hero=name)
    return cid


def _preview(database: Database, capsys, **kwargs) -> str:
    """Run an upsert as a dry run and return the printed report."""
    capsys.readouterr()  # discard anything buffered from setup writes
    database.upsert_story(dry_run=True, **kwargs)
    return capsys.readouterr().out


# ---------------------------------------------------------------------------
# Hero fragments
# ---------------------------------------------------------------------------


def test_preview_reports_hero_fragment_being_cleared(db: Database, capsys) -> None:
    """Dropping hero_fragments clears the anchor column; the preview must say so.

    set_story_heroes() replaces (canonical_id, fragment) pairs wholesale, so a
    declaration listing heroes without a matching hero_fragments= blanks every
    curated anchor. Membership is unchanged, so nothing else in the report moves.
    """
    _seed_hero(db, "dash", "Dash")
    db.upsert_story(
        "src/digital-tiles/bright-lights/bright-lights.md",
        story_type="digital-tiles",
        title="Bright Lights",
        heroes=["dash"],
        hero_fragments={"dash": "dash-io"},
    )

    report = _preview(
        db,
        capsys,
        path="src/digital-tiles/bright-lights/bright-lights.md",
        story_type="digital-tiles",
        title="Bright Lights",
        heroes=["dash"],
    )

    assert "dash" in report
    assert "dash-io" in report, "the fragment being lost is not named in the preview"
    assert "clear" in report.lower()


# ---------------------------------------------------------------------------
# Changes that fork a second registry row
# ---------------------------------------------------------------------------


def test_preview_warns_when_adding_a_region_forks_a_new_location_row(db: Database, capsys) -> None:
    """location_id is a hash of name|region_id, so adding a region mints a new row.

    The membership diff compares display names, and the name is present before
    and after, so it reports nothing. Without an explicit warning the preview
    shows a no-op for a change that orphans the original row.
    """
    db.upsert_story(
        "src/main-story/welcome-to-rathe/a-rising-star.md",
        story_type="main-story",
        title="A Rising Star",
        locations=[LocationEntry("Milesian Ranges")],
    )

    report = _preview(
        db,
        capsys,
        path="src/main-story/welcome-to-rathe/a-rising-star.md",
        story_type="main-story",
        title="A Rising Star",
        locations=[LocationEntry("Milesian Ranges", region="Aria")],
    )

    assert "Milesian Ranges" in report, "the forked location is not named in the preview"
    assert "Aria" in report
    assert "NEW ROW" in report, "the preview does not warn that a second row will be created"
    assert "orphan" in report.lower()


# ---------------------------------------------------------------------------
# Entity attribute changes
# ---------------------------------------------------------------------------


def test_preview_reports_location_lore_fragment_change(db: Database, capsys) -> None:
    """Changing an existing row's lore_fragment is a write the preview must show."""
    db.upsert_story(
        "src/main-story/x.md",
        story_type="main-story",
        title="X",
        locations=[LocationEntry("Enion", region="Aria", lore_fragment="enion")],
    )

    report = _preview(
        db,
        capsys,
        path="src/main-story/x.md",
        story_type="main-story",
        title="X",
        locations=[LocationEntry("Enion", region="Aria", lore_fragment="valahai")],
    )

    assert "Enion" in report
    assert "enion" in report and "valahai" in report, "the lore_fragment change is not shown"


def test_preview_stays_silent_when_omitted_field_is_preserved(db: Database, capsys) -> None:
    """Omitting notes/lore_fragment preserves the stored value, so it is not a change.

    upsert_location() only overwrites these columns when the incoming value is
    non-empty. Reporting an omitted field as 'cleared' would be a false alarm,
    which is worse than silence: it trains the reader to ignore the section.
    """
    db.upsert_story(
        "src/main-story/y.md",
        story_type="main-story",
        title="Y",
        locations=[LocationEntry("Enion", region="Aria", lore_fragment="enion", notes="A city.")],
    )

    report = _preview(
        db,
        capsys,
        path="src/main-story/y.md",
        story_type="main-story",
        title="Y",
        locations=[LocationEntry("Enion", region="Aria")],
    )

    assert "cleared" not in report.lower(), "preserved fields must not be reported as cleared"
    assert "A city." not in report


def test_preview_reports_npc_status_change(db: Database, capsys) -> None:
    """Overwriting a curated NPC status is a write the preview must show."""
    db.upsert_story(
        "src/main-story/z.md",
        story_type="main-story",
        title="Z",
        npcs=[NPCEntry("Lord Sutcliffe", species=SpeciesEntry("Human"), status="Just a head")],
    )

    report = _preview(
        db,
        capsys,
        path="src/main-story/z.md",
        story_type="main-story",
        title="Z",
        npcs=[NPCEntry("Lord Sutcliffe", species=SpeciesEntry("Human"), status="Deceased")],
    )

    assert "Lord Sutcliffe" in report
    assert "Just a head" in report and "Deceased" in report, "the status overwrite is not shown"


def test_preview_reports_fauna_description_change(db: Database, capsys) -> None:
    """Monster/fauna/flora descriptions are entity writes too."""
    db.upsert_story(
        "src/main-story/f.md",
        story_type="main-story",
        title="F",
        fauna=[FaunaEntry("Meep", description="A tiny thief.")],
    )

    report = _preview(
        db,
        capsys,
        path="src/main-story/f.md",
        story_type="main-story",
        title="F",
        fauna=[FaunaEntry("Meep", description="A chittering pickpocket.")],
    )

    assert "Meep" in report
    assert "A chittering pickpocket." in report, "the description overwrite is not shown"


def test_preview_warns_when_changing_kind_forks_a_food_drink_row(db: Database, capsys) -> None:
    """food_drink_id hashes name|kind, so changing kind forks a row like locations do."""
    db.upsert_story(
        "src/main-story/d.md",
        story_type="main-story",
        title="D",
        food_drink=[FoodDrinkEntry("Alder Cider", kind="Food")],
    )

    report = _preview(
        db,
        capsys,
        path="src/main-story/d.md",
        story_type="main-story",
        title="D",
        food_drink=[FoodDrinkEntry("Alder Cider", kind="Drink")],
    )

    assert "Alder Cider" in report
    assert "NEW ROW" in report, "the preview does not warn that changing kind forks a row"


def test_preview_reports_region_world_key_change(db: Database, capsys) -> None:
    """A region's world_of_rathe_story_key is overwritten in place, so show it."""
    db.upsert_story(
        "src/main-story/r.md",
        story_type="main-story",
        title="R",
        regions=[RegionEntry("Aria", world_of_rathe_story_key="world-of-rathe/aria.md")],
    )

    report = _preview(
        db,
        capsys,
        path="src/main-story/r.md",
        story_type="main-story",
        title="R",
        regions=[RegionEntry("Aria", world_of_rathe_story_key="world-of-rathe/wrong.md")],
    )

    assert "Aria" in report
    assert "world-of-rathe/wrong.md" in report, "the world key overwrite is not shown"


# ---------------------------------------------------------------------------
# Narrated videos
# ---------------------------------------------------------------------------


def test_preview_reports_narrated_videos_being_replaced(db: Database, capsys) -> None:
    """set_narrated_videos() replaces the set, so a count alone hides a swap.

    Reporting '1 entries' before and after a completely different video is a
    preview that cannot distinguish a no-op from a total replacement.
    """
    db.upsert_story(
        "src/main-story/v.md",
        story_type="main-story",
        title="V",
        narrated_videos=[NarratedVideoEntry(author="St_Havock", source_link="https://youtu.be/aaa")],
    )

    report = _preview(
        db,
        capsys,
        path="src/main-story/v.md",
        story_type="main-story",
        title="V",
        narrated_videos=[NarratedVideoEntry(author="Someone Else", source_link="https://youtu.be/bbb")],
    )

    assert "St_Havock" in report, "the video being dropped is not named in the preview"
    assert "Someone Else" in report


def test_preview_reports_group_lore_story_key_change(db: Database, capsys) -> None:
    """A group gaining its documentation page is a write, so it must be shown.

    Only ``kind`` was compared until 2026-08-20. ``upsert_group`` writes
    ``lore_story_key`` and ``lore_fragment`` from plain strings on the entry, so
    The Maela could gain both, change the DB, and print nothing.
    """
    db.upsert_story(
        "src/main-story/x.md",
        story_type="main-story",
        title="X",
        groups=[GroupEntry("The Maela", kind="troupe")],
    )

    report = _preview(
        db,
        capsys,
        path="src/main-story/x.md",
        story_type="main-story",
        title="X",
        groups=[
            GroupEntry(
                "The Maela",
                kind="troupe",
                lore_story_key="world-of-rathe/aria.md",
                lore_fragment="the-everfest-carnival",
            )
        ],
    )

    assert "world-of-rathe/aria.md" in report, "the lore_story_key change is not shown"
    assert "the-everfest-carnival" in report, "the lore_fragment change is not shown"


def test_preview_reports_a_membership_changing_its_source(db: Database, capsys) -> None:
    """The citation is a stored column, so re-sourcing a membership is a write.

    The roster diff compared id sets, which are identical when only the cited
    page moves — so the per-member source could have landed unannounced, exactly
    the gap the emptied-roster bug had.
    """
    db.upsert_story(
        "src/main-story/x.md",
        story_type="main-story",
        title="X",
        groups=[
            GroupEntry(
                "The Maela",
                npc_members=(NPCEntry("Kaysin"),),
                member_source="flavour/compendium-of-rathe.md",
            )
        ],
    )

    report = _preview(
        db,
        capsys,
        path="src/main-story/x.md",
        story_type="main-story",
        title="X",
        groups=[GroupEntry("The Maela", npc_members=((NPCEntry("Kaysin"), "flavour/rosetta.md"),))],
    )

    assert "flavour/rosetta.md" in report, "the new citation is not shown"
    assert "flavour/compendium-of-rathe.md" in report, "the old citation is not shown"


def test_preview_stays_silent_when_a_membership_keeps_its_source(db: Database, capsys) -> None:
    """The source diff must not fire on an unchanged roster."""
    entry = GroupEntry(
        "The Maela",
        npc_members=((NPCEntry("Kaysin"), "flavour/rosetta.md"),),
    )
    db.upsert_story("src/main-story/x.md", story_type="main-story", title="X", groups=[entry])

    report = _preview(db, capsys, path="src/main-story/x.md", story_type="main-story", title="X", groups=[entry])

    assert "source" not in report, "an unchanged citation was reported as a change"


def test_preview_reports_a_group_reached_only_as_a_parent(db: Database, capsys) -> None:
    """A parent group is a write, so its creation and roster must be shown.

    ``_show_group_changes`` iterated the ``groups`` kwarg until 2026-08-21, while
    ``_show_alternate_name_changes`` walked the reachable chain. So a group named
    only as another group's ``parent`` had its row created, its roster written and
    its scalars set in silence, and the one thing that *did* print about it was an
    alias. Stage 5's Super Slam hierarchy would have created four stable rows,
    twelve parent links and three patron memberships behind one alias line.
    """
    stable = GroupEntry(
        "Speakeasy's Guilds",
        kind="stable",
        npc_members=(NPCEntry("Speakeasy"),),
        member_source="main-story/super-slam/feudmasters.md",
    )
    report = _preview(
        db,
        capsys,
        path="src/main-story/x.md",
        story_type="main-story",
        title="X",
        groups=[GroupEntry("Mythmakers", kind="guild", parent=stable)],
    )

    assert "Speakeasy's Guilds" in report, "the parent group is not previewed at all"
    assert "new group" in report
    assert "1 members" in report, "the parent's roster is not previewed"


def test_preview_reports_a_group_changing_parent(db: Database, capsys) -> None:
    """`parent_group_id` is a stored column, so re-parenting a group is a write.

    It was left unpreviewed alongside `location_id` on the reasoning that both
    "need resolving rather than reading". Only the location does: `_group_id` is a
    pure hash, so a parent resolves without touching the database.
    """
    db.upsert_story(
        "src/main-story/x.md",
        story_type="main-story",
        title="X",
        groups=[GroupEntry("Heavy Metals", kind="guild")],
    )

    report = _preview(
        db,
        capsys,
        path="src/main-story/x.md",
        story_type="main-story",
        title="X",
        groups=[GroupEntry("Heavy Metals", kind="guild", parent=GroupEntry("Batbiter's Guilds", kind="stable"))],
    )

    assert "Heavy Metals" in report and "parent" in report, "the parent change is not shown"
    assert "Batbiter's Guilds" in report, "the new parent is not named"
    assert "GR" not in report.split("parent")[1][:40], "the parent is rendered as a raw id, not a name"
