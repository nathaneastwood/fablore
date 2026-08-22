"""Tests for the ``characters=`` kwarg on ``Database.upsert_story``.

Stage 6b (migration 17) merged ``story_npcs`` and ``story_heroes`` into one
``story_characters`` table but kept two kwargs, ``heroes=`` and ``npcs=``,
writing it — which forced a "hero-owned" partition to keep the two
independent, and that partition had a hole (see the removed
``_write_story_characters`` docstring in git history). This later stage
removes the second kwarg entirely: ``characters=`` accepts a mixed list of
canonical hero slugs and :class:`NPCEntry` instances, and is a plain
replace-semantic junction parameter like every other one. This file tests the
seam that change creates: ``characters=`` replace semantics, the duplicate
guard for a person named twice in one list (the invariant that replaces the
old collapse), and ``fragments=`` key-membership validation against the one
list.

Seam: the public ``Database.upsert_story`` and what it leaves in
``story_characters`` / raises — never internals.
"""

from __future__ import annotations

import pytest

import db._queries as q
from db import Database, NPCEntry


def _seed_hero(database: Database, slug: str, name: str) -> str:
    from registry_ids import canonical_id

    cid = canonical_id(slug)
    q.upsert_hero_canonical(database.conn, canonical_id=cid, canonical_slug=slug, canonical_hero=name)
    return cid


def _character_names(database: Database) -> set[str]:
    return {
        r["name"]
        for r in database.conn.execute("SELECT c.name FROM story_characters sc JOIN characters c USING(character_id)")
    }


# ---------------------------------------------------------------------------
# characters=: plain replace semantics, mixing a slug and an NPCEntry
# ---------------------------------------------------------------------------


def test_characters_mixes_a_hero_slug_and_an_npc_entry_in_one_call(db: Database) -> None:
    _seed_hero(db, "dash", "Dash")
    db.upsert_story(
        "src/main-story/x.md",
        story_type="main-story",
        title="X",
        characters=["dash", NPCEntry("Guard Captain")],
    )
    assert _character_names(db) == {"Dash", "Guard Captain"}


def test_characters_none_leaves_existing_links_unchanged(db: Database) -> None:
    _seed_hero(db, "dash", "Dash")
    db.upsert_story(
        "src/main-story/x.md",
        story_type="main-story",
        title="X",
        characters=["dash", NPCEntry("Guard Captain")],
    )
    db.upsert_story("src/main-story/x.md", story_type="main-story", title="X", characters=None)
    assert _character_names(db) == {"Dash", "Guard Captain"}


def test_characters_empty_list_clears_every_link(db: Database) -> None:
    _seed_hero(db, "dash", "Dash")
    db.upsert_story(
        "src/main-story/x.md",
        story_type="main-story",
        title="X",
        characters=["dash", NPCEntry("Guard Captain")],
    )
    db.upsert_story("src/main-story/x.md", story_type="main-story", title="X", characters=[])
    assert _character_names(db) == set()


def test_characters_list_replaces_the_stored_set_exactly(db: Database) -> None:
    """A second declaration is not additive: dropping Dash drops his link."""
    _seed_hero(db, "dash", "Dash")
    db.upsert_story(
        "src/main-story/x.md",
        story_type="main-story",
        title="X",
        characters=["dash", NPCEntry("Guard Captain")],
    )
    db.upsert_story(
        "src/main-story/x.md",
        story_type="main-story",
        title="X",
        characters=[NPCEntry("Guard Captain")],
    )
    assert _character_names(db) == {"Guard Captain"}


# ---------------------------------------------------------------------------
# Duplicate guard: a slug and an NPCEntry (or two of either) naming one
# person in a single characters= list raises, naming both.
# ---------------------------------------------------------------------------


def test_slug_and_npc_entry_for_the_same_person_raises_naming_both(db: Database) -> None:
    """The identity spine means 'kano' the slug and NPCEntry('Kano') collide."""
    _seed_hero(db, "kano", "Kano")
    with pytest.raises(ValueError) as excinfo:
        db.upsert_story(
            "src/main-story/x.md",
            story_type="main-story",
            title="X",
            characters=["kano", NPCEntry("Kano")],
        )
    message = str(excinfo.value)
    assert "x.md" in message
    assert "hero 'kano'" in message
    assert "NPC 'Kano'" in message


def test_slug_and_npc_entry_raise_names_the_shared_character_id(db: Database) -> None:
    from registry_ids import lore_character_id

    _seed_hero(db, "kano", "Kano")
    with pytest.raises(ValueError, match=lore_character_id("Kano")):
        db.upsert_story(
            "src/main-story/x.md",
            story_type="main-story",
            title="X",
            characters=["kano", NPCEntry("Kano")],
        )


def test_same_slug_named_twice_raises(db: Database) -> None:
    _seed_hero(db, "kano", "Kano")
    with pytest.raises(ValueError):
        db.upsert_story(
            "src/main-story/x.md",
            story_type="main-story",
            title="X",
            characters=["kano", "kano"],
        )


def test_duplicate_guard_fires_before_any_write(db: Database) -> None:
    """A rejected declaration must not leave a partial story_characters write."""
    _seed_hero(db, "kano", "Kano")
    with pytest.raises(ValueError):
        db.upsert_story(
            "src/main-story/x.md",
            story_type="main-story",
            title="X",
            characters=["kano", NPCEntry("Kano"), NPCEntry("Guard Captain")],
        )
    assert db.conn.execute("SELECT COUNT(*) FROM story_characters").fetchone()[0] == 0


# ---------------------------------------------------------------------------
# fragments= key validation against the one characters= list
# ---------------------------------------------------------------------------


def test_fragments_key_matching_no_one_declared_raises(db: Database) -> None:
    _seed_hero(db, "dash", "Dash")
    with pytest.raises(ValueError, match="matches no hero slug or NPC name"):
        db.upsert_story(
            "src/main-story/x.md",
            story_type="main-story",
            title="X",
            characters=["dash"],
            fragments={"nobody": "anchor"},
        )


def test_fragments_key_matching_both_a_slug_and_an_unrelated_npc_name_raises(db: Database) -> None:
    """'phoenix' is Fenris's slug and, separately, a different NPC's display
    name — two different people, so this is ambiguity, not the duplicate-
    person guard (that fires only when the two sides resolve to one
    character_id, which a slug and its own canonical display name would, but
    a slug and an unrelated display name do not).
    """
    _seed_hero(db, "phoenix", "Fenris Blackwind")
    with pytest.raises(ValueError, match="names both a declared hero slug and a declared NPC"):
        db.upsert_story(
            "src/main-story/x.md",
            story_type="main-story",
            title="X",
            characters=["phoenix", NPCEntry("phoenix")],
            fragments={"phoenix": "anchor"},
        )
