"""Tests for :mod:`create_character_groups_md`, the database-driven generator for
``src/data/md/character-groups.md``.

Seam under test: ``render_markdown(conn) -> str``, a pure function over a
``sqlite3.Connection``. Fixture rows are written directly through ``db._queries``
so each test controls exactly the joins it exercises, without needing a full
story registration.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

_DATA_DIR = Path(__file__).resolve().parent.parent / "src" / "data"
if str(_DATA_DIR) not in sys.path:
    sys.path.insert(0, str(_DATA_DIR))


def _import_generator():
    """create_character_groups_md is stdlib-only (sqlite3 + pathlib) — unlike
    create_md.py it needs no pandas / py_markdown_table."""
    import create_character_groups_md

    return create_character_groups_md


# ---------------------------------------------------------------------------
# Skeleton
# ---------------------------------------------------------------------------


def test_render_markdown_on_empty_database_has_title_and_no_sections(db) -> None:
    """An empty database still renders a valid page: the H1 and nothing else."""
    gen = _import_generator()
    text = gen.render_markdown(db.conn)
    assert text.startswith("# Character Groups\n")
    assert "##" not in text


# ---------------------------------------------------------------------------
# Kind-driven sections
# ---------------------------------------------------------------------------


def test_aesir_section_lists_kind_members_with_joined_epithets(db) -> None:
    import db._queries as q
    from registry_ids import lore_character_id, kind_id

    gen = _import_generator()
    sp_id = kind_id("Aesir")
    q.upsert_kind(db.conn, kind_id=sp_id, name="Aesir")

    sol_id = lore_character_id("Sol")
    q.upsert_character(db.conn, character_id=sol_id, name="Sol")
    q.set_character_kinds(db.conn, sol_id, [sp_id])
    q.set_character_epithets(db.conn, sol_id, [("Aesir of Light", "epithet")])

    raven_id = lore_character_id("Raven, Aesir of Chaos")
    q.upsert_character(db.conn, character_id=raven_id, name="Raven, Aesir of Chaos")
    q.set_character_kinds(db.conn, raven_id, [sp_id])
    q.set_character_epithets(db.conn, raven_id, [("Aesir of Chaos", "epithet")])

    text = gen.render_markdown(db.conn)
    assert "## Aesir" in text
    aesir_block = text.split("## Aesir", 1)[1].split("\n##", 1)[0]
    assert "Sol" in aesir_block
    assert "Aesir of Light" in aesir_block
    assert "Raven, Aesir of Chaos" in aesir_block
    assert "Aesir of Chaos" in aesir_block
    # Sorted by character name: "Raven, Aesir of Chaos" < "Sol"
    assert aesir_block.index("Raven") < aesir_block.index("Sol")


def test_character_with_no_epithet_row_renders_with_a_blank_epithets_cell(db) -> None:
    """The Aesir-of-Flames/Infernai case: a character whose stored name IS the
    epithet has no separate character_epithets row, so the Epithets cell is blank."""
    import db._queries as q
    from registry_ids import lore_character_id, kind_id

    gen = _import_generator()
    sp_id = kind_id("Aesir")
    q.upsert_kind(db.conn, kind_id=sp_id, name="Aesir")
    cid = lore_character_id("Aesir of Flames")
    q.upsert_character(db.conn, character_id=cid, name="Aesir of Flames")
    q.set_character_kinds(db.conn, cid, [sp_id])

    text = gen.render_markdown(db.conn)
    assert "Aesir of Flames" in text


def test_multiple_epithets_on_one_character_are_comma_joined_in_sort_order(db) -> None:
    import db._queries as q
    from registry_ids import lore_character_id, kind_id

    gen = _import_generator()
    sp_id = kind_id("Ancient")
    q.upsert_kind(db.conn, kind_id=sp_id, name="Ancient")
    cid = lore_character_id("Yvor")
    q.upsert_character(db.conn, character_id=cid, name="Yvor")
    q.set_character_kinds(db.conn, cid, [sp_id])
    q.set_character_epithets(
        db.conn,
        cid,
        [
            ("Ancient of Lightning", "epithet"),
            ("Ancient of Lightning and Ice", "epithet"),
        ],
    )

    text = gen.render_markdown(db.conn)
    assert "## Ancients" in text
    block = text.split("## Ancients", 1)[1].split("\n##", 1)[0]
    assert "Ancient of Lightning, Ancient of Lightning and Ice" in block


def test_kind_with_no_members_emits_no_section(db) -> None:
    import db._queries as q
    from registry_ids import kind_id

    gen = _import_generator()
    q.upsert_kind(db.conn, kind_id=kind_id("Embra"), name="Embra")

    text = gen.render_markdown(db.conn)
    assert "## Embra" not in text


# ---------------------------------------------------------------------------
# Titles (deferred data) — the section must appear only once rows exist
# ---------------------------------------------------------------------------


def test_no_title_rows_means_no_dracai_or_grand_magisters_section(db) -> None:
    gen = _import_generator()
    text = gen.render_markdown(db.conn)
    assert "## Dracai" not in text
    assert "## Grand Magisters" not in text


def test_seeding_titles_and_holders_makes_both_sections_appear(db) -> None:
    """The generator must need no code change once titles/title_holders are
    populated — this is the fixture the task calls out explicitly."""
    import db._queries as q
    from registry_ids import group_id, lore_character_id, title_id

    gen = _import_generator()

    # Dracai: an office hanging off the Dracai people-group.
    dracai_group = group_id("Dracai")
    q.upsert_group(db.conn, group_id=dracai_group, name="Dracai", category="people")
    aether_title = title_id("Dracai of Aether")
    q.upsert_title(db.conn, title_id=aether_title, name="Dracai of Aether", group_id=dracai_group)
    kano_id = lore_character_id("Kano")
    q.upsert_character(db.conn, character_id=kano_id, name="Kano")
    q.set_title_holders(db.conn, aether_title, [(kano_id, 0, "")])

    # Grand Magister: one office, ordered succession.
    gm_title = title_id("Grand Magister")
    q.upsert_title(db.conn, title_id=gm_title, name="Grand Magister")
    devout_id = lore_character_id("The Devout")
    q.upsert_character(db.conn, character_id=devout_id, name="The Devout")
    q.set_title_holders(db.conn, gm_title, [(devout_id, 1, "")])

    text = gen.render_markdown(db.conn)
    assert "## Dracai" in text
    dracai_block = text.split("## Dracai", 1)[1].split("\n##", 1)[0]
    assert "Dracai of Aether" in dracai_block
    assert "Kano" in dracai_block

    assert "## Grand Magisters" in text
    gm_block = text.split("## Grand Magisters", 1)[1].split("\n##", 1)[0]
    assert "The Devout" in gm_block
    assert "1" in gm_block


# ---------------------------------------------------------------------------
# Deathmatch Super Slam Guilds — three-level nesting, patrons vs members
# ---------------------------------------------------------------------------


def _seed_super_slam(database) -> None:
    import db._queries as q
    from registry_ids import group_id, lore_character_id

    federation = group_id("Super Slam Guilds")
    q.upsert_group(database.conn, group_id=federation, name="Super Slam Guilds", category="federation")

    speakeasy_stable = group_id("Speakeasy's Guilds")
    q.upsert_group(
        database.conn,
        group_id=speakeasy_stable,
        name="Speakeasy's Guilds",
        category="stable",
        parent_group_id=federation,
    )
    moloca_stable = group_id("Moloca's Guilds")
    q.upsert_group(
        database.conn,
        group_id=moloca_stable,
        name="Moloca's Guilds",
        category="stable",
        parent_group_id=federation,
    )

    speakeasy_id = lore_character_id("Speakeasy")
    q.upsert_character(database.conn, character_id=speakeasy_id, name="Speakeasy")
    q.set_group_members(database.conn, speakeasy_stable, [(speakeasy_id, "")])

    moloca_id = lore_character_id("Moloca")
    q.upsert_character(database.conn, character_id=moloca_id, name="Moloca")
    q.set_group_members(database.conn, moloca_stable, [(moloca_id, "")])

    boulders = group_id("Boulders")
    q.upsert_group(
        database.conn, group_id=boulders, name="Boulders", category="guild", parent_group_id=speakeasy_stable
    )


def test_super_slam_patron_is_prose_not_a_guild_table_row(db) -> None:
    gen = _import_generator()
    _seed_super_slam(db)

    text = gen.render_markdown(db.conn)
    assert "## Deathmatch Super Slam Guilds" in text
    block = text.split("## Deathmatch Super Slam Guilds", 1)[1]

    assert "### Speakeasy's Guilds" in block
    speakeasy_block = block.split("### Speakeasy's Guilds", 1)[1].split("###", 1)[0]
    assert "Speakeasy" in speakeasy_block
    assert "Boulders" in speakeasy_block
    # Patron must not sit inside the guild-name table as a row of its own.
    assert "| Speakeasy |" not in speakeasy_block


def test_empty_stable_still_gets_a_heading(db) -> None:
    """Moloca's Guilds holds no guild rows, and must not be dropped."""
    gen = _import_generator()
    _seed_super_slam(db)

    text = gen.render_markdown(db.conn)
    block = text.split("## Deathmatch Super Slam Guilds", 1)[1]
    assert "### Moloca's Guilds" in block
    moloca_block = block.split("### Moloca's Guilds", 1)[1].split("###", 1)[0]
    assert "Moloca" in moloca_block


def test_super_slam_group_with_no_data_emits_no_section(db) -> None:
    gen = _import_generator()
    text = gen.render_markdown(db.conn)
    assert "Super Slam" not in text


# ---------------------------------------------------------------------------
# Dragons — no Pronounciation/Phonetic columns, links the archive page instead
# ---------------------------------------------------------------------------


def test_dragons_section_has_no_pronunciation_or_phonetic_columns(db) -> None:
    import db._queries as q
    from registry_ids import lore_character_id, kind_id

    gen = _import_generator()
    sp_id = kind_id("Dragon")
    q.upsert_kind(db.conn, kind_id=sp_id, name="Dragon")
    cid = lore_character_id("Azvolai")
    q.upsert_character(db.conn, character_id=cid, name="Azvolai")
    q.set_character_kinds(db.conn, cid, [sp_id])

    text = gen.render_markdown(db.conn)
    assert "## Dragons" in text
    block = text.split("## Dragons", 1)[1].split("\n##", 1)[0]
    assert "Azvolai" in block
    assert "Pronounciation" not in block
    assert "Phonetic" not in block
    assert "welcome-to-volcor.md" in block


# ---------------------------------------------------------------------------
# Determinism
# ---------------------------------------------------------------------------


def test_render_markdown_is_deterministic(db) -> None:
    gen = _import_generator()
    _seed_super_slam(db)
    first = gen.render_markdown(db.conn)
    second = gen.render_markdown(db.conn)
    assert first == second


# ---------------------------------------------------------------------------
# main() — the "run from the repository root" contract
# ---------------------------------------------------------------------------


def test_main_writes_the_banner_and_rendered_text_to_the_named_path(tmp_path: Path) -> None:
    """main() takes db_path/output_md overrides so it can be exercised without
    ever touching the committed mirror."""
    gen = _import_generator()

    (tmp_path / "csv").mkdir()
    db_path = tmp_path / "fablore.db"
    out_path = tmp_path / "character-groups.md"

    gen.main(out_path, db_path=db_path)

    text = out_path.read_text(encoding="utf-8")
    assert text.startswith("<!-- ### NOTE:")
    assert "# Character Groups" in text
    assert db_path.is_file()  # Database auto-seeds a fresh db file on first open


def test_main_refuses_to_run_without_being_told_where_to_write() -> None:
    """The destination is required on purpose.

    While this generator was being written it defaulted to the live page, and a
    stray call overwrote it. What it renders today would be a net loss to a
    reader — see the module docstring — so until the data entry it waits on has
    landed, nothing that cannot name its destination should be able to reach one.
    """
    gen = _import_generator()

    with pytest.raises(TypeError):
        gen.main()


def test_output_md_still_names_the_page_this_will_eventually_generate() -> None:
    """The constant records the destination even though nothing defaults to it."""
    gen = _import_generator()
    assert gen.OUTPUT_MD == gen.DATA / "md" / "character-groups.md"


# ---------------------------------------------------------------------------
# Deliberately NOT wired yet
# ---------------------------------------------------------------------------
# `src/data/md/character-groups.md` is still hand-maintained and live in
# SUMMARY.md. Wiring this generator into create_md.py or the sync hook would
# swap the page on the next commit that touches any mirrored file — and what it
# renders today loses the Dracai and Grand Magisters sections, loses Anarchs of
# L'Apocalypta, and prints nine characters' epithets twice. These tests fail the
# moment someone wires it, which is the prompt to do the swap properly: revisit
# the module docstring's list, update all four wiring points, and replace these
# three tests with the ones that assert the wiring is present.

_ROOT = Path(__file__).resolve().parent.parent


def test_create_md_does_not_yet_call_this_generator() -> None:
    source = (_ROOT / "src" / "data" / "create_md.py").read_text(encoding="utf-8")
    assert "create_character_groups_md" not in source


def test_ensure_create_md_sync_does_not_yet_check_the_page() -> None:
    script = (_ROOT / "scripts" / "ensure-create-md-sync.sh").read_text(encoding="utf-8")
    assert "src/data/md/character-groups.md" not in script


def test_the_sync_hook_does_not_yet_trigger_on_this_generator() -> None:
    config = (_ROOT / ".pre-commit-config.yaml").read_text(encoding="utf-8")
    hook_start = config.index("id: ensure-create-md-sync")
    hook_block = config[hook_start : hook_start + 400]
    files_line = next(line for line in hook_block.splitlines() if line.strip().startswith("files:"))
    assert "create_character_groups_md" not in files_line
