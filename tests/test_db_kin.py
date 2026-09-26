"""Tests for the kinship schema (migration 14): character_kin.

Mirrors ``test_db_titles.py``. The hazard titles introduced carries over
unchanged — a relative may be named as a ``CharacterEntry`` *or* as a hero slug, and both
can resolve to the same ``character_id`` (migration 12's identity spine) — but
``character_kin`` adds one of its own: only the *stated* direction is ever
written. "Lyath's father is Bloodworth" is one row; "Bloodworth's child is
Lyath" is never stored, only derived at read time, so the two halves cannot
come to disagree with each other.
"""

from __future__ import annotations

import pytest

import db._queries as q
from db import Database, GroupEntry, CharacterEntry
from registry_ids import canonical_id, lore_character_id


def _seed_hero(database: Database, slug: str, name: str) -> str:
    cid = canonical_id(slug)
    q.upsert_hero_canonical(database.conn, canonical_id=cid, canonical_slug=slug, canonical_hero=name)
    return cid


def _story(database: Database, path: str = "src/world-of-rathe/solana.md", **kw):
    return database.upsert_story(path=path, story_type="world-of-rathe", title="T", **kw)


# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------


def test_migration_creates_character_kin_table(db: Database) -> None:
    tables = {r[0] for r in db.conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    assert "character_kin" in tables


def test_schema_version_matches_constant(db: Database) -> None:
    from db._schema import CURRENT_VERSION

    assert db.conn.execute("PRAGMA user_version").fetchone()[0] == CURRENT_VERSION


def test_character_kin_has_no_id_column(db: Database) -> None:
    """A junction, like group_characters — no kin_id is minted for it."""
    cols = {r[1] for r in db.conn.execute("PRAGMA table_info(character_kin)")}
    assert cols == {"character_id", "relative_id", "relation", "story_key", "qualifier"}


def test_character_kin_primary_key_rejects_a_repeated_row(db: Database) -> None:
    q.upsert_character(db.conn, character_id="LC1", name="Lyath")
    q.upsert_character(db.conn, character_id="LC2", name="Bloodworth")
    db.conn.execute(
        "INSERT INTO character_kin (character_id, relative_id, relation) VALUES (?,?,?)",
        ("LC1", "LC2", "father"),
    )
    with pytest.raises(Exception):
        db.conn.execute(
            "INSERT INTO character_kin (character_id, relative_id, relation) VALUES (?,?,?)",
            ("LC1", "LC2", "father"),
        )


def test_character_kin_relative_id_has_a_foreign_key(db: Database) -> None:
    q.upsert_character(db.conn, character_id="LC1", name="Lyath")
    with pytest.raises(Exception):
        db.conn.execute(
            "INSERT INTO character_kin (character_id, relative_id, relation) VALUES (?,?,?)",
            ("LC1", "LCnonexistent0", "father"),
        )


# ---------------------------------------------------------------------------
# Declaration (R8)
# ---------------------------------------------------------------------------


def test_a_relative_is_written_from_a_single_stated_fact(db: Database) -> None:
    entry = CharacterEntry("Lyath", kin=((CharacterEntry("Bloodworth Goldmane"), "father"),))
    _story(db, characters=[entry])
    rows = q.select_character_kin(db.conn, lore_character_id("Lyath"))
    assert rows == [(lore_character_id("Bloodworth Goldmane"), "father", "", "blood")]


def test_the_inverse_is_not_also_written(db: Database) -> None:
    """Storing "Lyath's father is Bloodworth" must not also write "Bloodworth's
    child is Lyath" — see the table comment in ``_schema.py`` for why."""
    entry = CharacterEntry("Lyath", kin=((CharacterEntry("Bloodworth Goldmane"), "father"),))
    _story(db, characters=[entry])
    assert q.select_character_kin(db.conn, lore_character_id("Bloodworth Goldmane")) == []


def test_hero_relative_resolves_through_character_heroes(db: Database) -> None:
    """The point of the identity spine: a hero slug lands in the same column an entry-named character would."""
    hid = _seed_hero(db, "victor", "Victor")
    resolved_character_id = "LCmanualoverride0"
    q.upsert_character(db.conn, character_id=resolved_character_id, name="Victor")
    q.set_character_hero(db.conn, hid, resolved_character_id)

    entry = CharacterEntry("Lyath", kin=(("victor", "sibling"),))
    _story(db, characters=[entry])
    rows = q.select_character_kin(db.conn, lore_character_id("Lyath"))
    assert rows == [(resolved_character_id, "sibling", "", "blood")]


def test_hero_relative_self_heals_character_heroes_when_missing(db: Database) -> None:
    """A hero with no character_heroes row yet still resolves cleanly."""
    hid = _seed_hero(db, "victor", "Victor")
    assert q.select_character_id_for_hero(db.conn, hid) is None

    entry = CharacterEntry("Lyath", kin=(("victor", "sibling"),))
    _story(db, characters=[entry])

    minted = lore_character_id("Victor")
    assert q.select_character_id_for_hero(db.conn, hid) == minted
    assert q.select_character_kin(db.conn, lore_character_id("Lyath")) == [(minted, "sibling", "", "blood")]


def test_unknown_hero_slug_raises(db: Database) -> None:
    with pytest.raises(ValueError):
        _story(db, characters=[CharacterEntry("Lyath", kin=(("no-such-hero", "sibling"),))])


def test_kin_carries_an_optional_citation(db: Database) -> None:
    entry = CharacterEntry(
        "Lyath",
        kin=((CharacterEntry("Bloodworth Goldmane"), "father", "heroes-of-rathe/lyath-about.md"),),
    )
    _story(db, characters=[entry])
    rows = q.select_character_kin(db.conn, lore_character_id("Lyath"))
    assert rows == [(lore_character_id("Bloodworth Goldmane"), "father", "heroes-of-rathe/lyath-about.md", "blood")]


def test_a_relative_creates_its_own_character_row(db: Database) -> None:
    """The relative must get a row of its own of its own, not just an id in character_kin."""
    entry = CharacterEntry("Lyath", kin=((CharacterEntry("Bloodworth Goldmane"), "father"),))
    _story(db, characters=[entry])
    row = db.conn.execute(
        "SELECT name FROM characters WHERE character_id = ?",
        [lore_character_id("Bloodworth Goldmane")],
    ).fetchone()
    assert row["name"] == "Bloodworth Goldmane"


def test_mutual_kin_references_do_not_recurse_forever(db: Database) -> None:
    """Two people naming each other as kin — siblings, spouses — is normal
    domain data, not a cycle error; it must terminate, not raise."""
    lyath = CharacterEntry("Lyath")
    victor = CharacterEntry("Victor", kin=((lyath, "sibling"),))
    lyath_with_kin = CharacterEntry("Lyath", kin=((victor, "sibling"),))
    _story(db, characters=[lyath_with_kin])
    assert q.select_character_kin(db.conn, lore_character_id("Lyath")) == [
        (lore_character_id("Victor"), "sibling", "", "blood")
    ]
    assert q.select_character_kin(db.conn, lore_character_id("Victor")) == [
        (lore_character_id("Lyath"), "sibling", "", "blood")
    ]


# ---------------------------------------------------------------------------
# Guards
# ---------------------------------------------------------------------------


def test_a_relative_may_not_be_named_twice_with_the_same_relation(db: Database) -> None:
    entry = CharacterEntry(
        "Lyath",
        kin=(
            (CharacterEntry("Bloodworth Goldmane"), "father"),
            (CharacterEntry("Bloodworth Goldmane"), "father"),
        ),
    )
    with pytest.raises(ValueError, match="Bloodworth Goldmane"):
        _story(db, characters=[entry])


def test_the_same_person_may_not_be_named_as_both_entry_and_hero_slug(db: Database) -> None:
    """The hazard migration 12 makes reachable: one character_id, two spellings."""
    _seed_hero(db, "victor", "Victor")
    _story(db, characters=[CharacterEntry("Victor", hero_slug="victor")])
    entry = CharacterEntry(
        "Lyath",
        kin=(
            (CharacterEntry("Victor"), "sibling"),
            ("victor", "sibling"),
        ),
    )
    with pytest.raises(ValueError, match="Victor"):
        _story(db, characters=[entry])


def test_the_duplicate_guard_fires_on_the_preview_path_too(db: Database) -> None:
    entry = CharacterEntry(
        "Lyath",
        kin=(
            (CharacterEntry("Bloodworth Goldmane"), "father"),
            (CharacterEntry("Bloodworth Goldmane"), "father"),
        ),
    )
    with pytest.raises(ValueError, match="Bloodworth Goldmane"):
        _story(db, characters=[entry], dry_run=True)


def test_a_character_cannot_be_their_own_relative(db: Database) -> None:
    entry = CharacterEntry("Lyath", kin=((CharacterEntry("Lyath"), "sibling"),))
    with pytest.raises(ValueError, match="Lyath"):
        _story(db, characters=[entry])


def test_self_relative_guard_fires_via_a_hero_slug_prediction(db: Database) -> None:
    """No character_heroes row exists yet, but the slug still predicts the id
    self-healing would mint — lore_character_id of the hero's own name — so
    the self-relative guard fires without ever writing a row."""
    _seed_hero(db, "lyath", "Lyath")
    entry = CharacterEntry("Lyath", kin=(("lyath", "sibling"),))
    with pytest.raises(ValueError, match="Lyath"):
        _story(db, characters=[entry])


def test_self_relative_guard_fires_on_the_preview_path_too(db: Database) -> None:
    entry = CharacterEntry("Lyath", kin=((CharacterEntry("Lyath"), "sibling"),))
    with pytest.raises(ValueError, match="Lyath"):
        _story(db, characters=[entry], dry_run=True)


# ---------------------------------------------------------------------------
# Replace semantics
# ---------------------------------------------------------------------------


def test_kin_is_replace_semantic(db: Database) -> None:
    two = CharacterEntry(
        "Lyath",
        kin=((CharacterEntry("Bloodworth Goldmane"), "father"), (CharacterEntry("Tara VanGeld"), "mother")),
    )
    _story(db, characters=[two])
    assert len(q.select_character_kin(db.conn, lore_character_id("Lyath"))) == 2
    _story(db, characters=[CharacterEntry("Lyath", kin=((CharacterEntry("Bloodworth Goldmane"), "father"),))])
    assert len(q.select_character_kin(db.conn, lore_character_id("Lyath"))) == 1


def test_emptied_kin_is_a_deletion_not_a_no_op(db: Database) -> None:
    _story(db, characters=[CharacterEntry("Lyath", kin=((CharacterEntry("Bloodworth Goldmane"), "father"),))])
    _story(db, characters=[CharacterEntry("Lyath")])
    assert q.select_character_kin(db.conn, lore_character_id("Lyath")) == []


def test_dry_run_removal_line_matches_what_the_apply_does(db: Database, capsys) -> None:
    _story(db, characters=[CharacterEntry("Lyath", kin=((CharacterEntry("Bloodworth Goldmane"), "father"),))])
    capsys.readouterr()
    db.upsert_story(
        path="src/world-of-rathe/solana.md",
        story_type="world-of-rathe",
        title="T",
        characters=[CharacterEntry("Lyath")],
        dry_run=True,
    )
    assert "REMOVED" in capsys.readouterr().out
    _story(db, characters=[CharacterEntry("Lyath")])
    assert q.select_character_kin(db.conn, lore_character_id("Lyath")) == []


def test_dry_run_reports_a_new_kin_fact(db: Database, capsys) -> None:
    capsys.readouterr()
    db.upsert_story(
        path="src/world-of-rathe/solana.md",
        story_type="world-of-rathe",
        title="T",
        characters=[CharacterEntry("Lyath", kin=((CharacterEntry("Bloodworth Goldmane"), "father"),))],
        dry_run=True,
    )
    out = capsys.readouterr().out
    assert "father" in out and "Bloodworth Goldmane" in out
    # Nothing written
    assert q.select_character_kin(db.conn, lore_character_id("Lyath")) == []


def test_dry_run_reaches_a_kin_fact_declared_only_through_a_group_roster(db: Database, capsys) -> None:
    """A kin fact declared on a character reached only through a group roster must
    not be invisible — the same hazard commit 433d5015 fixed for four other
    functions that walked the ``npcs`` kwarg instead of the reachable set."""
    grp = GroupEntry(
        "House Goldmane",
        members=(CharacterEntry("Lyath", kin=((CharacterEntry("Bloodworth Goldmane"), "father"),)),),
        member_source="heroes-of-rathe/lyath-about.md",
    )
    capsys.readouterr()
    db.upsert_story(
        path="src/world-of-rathe/solana.md",
        story_type="world-of-rathe",
        title="T",
        groups=[grp],
        dry_run=True,
    )
    out = capsys.readouterr().out
    assert "father" in out and "Bloodworth Goldmane" in out


# ---------------------------------------------------------------------------
# Query layer: derived inverse
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "relation,expected_inverse",
    [
        ("father", "child"),
        ("mother", "child"),
        ("parent", "child"),
        ("child", "parent"),
        ("sibling", "sibling"),
        ("spouse", "spouse"),
        ("grandparent", "grandchild"),
        ("grandchild", "grandparent"),
        ("aunt-or-uncle", "niece-or-nephew"),
        ("niece-or-nephew", "aunt-or-uncle"),
        ("cousin", "cousin"),
    ],
)
def test_kin_inverse_map(relation: str, expected_inverse: str) -> None:
    assert q.KIN_INVERSE[relation] == expected_inverse


def test_both_directions_query_derives_the_inverse(db: Database) -> None:
    entry = CharacterEntry("Lyath", kin=((CharacterEntry("Bloodworth Goldmane"), "father"),))
    _story(db, characters=[entry])
    lyath_id = lore_character_id("Lyath")
    bloodworth_id = lore_character_id("Bloodworth Goldmane")

    assert q.select_character_kin_both_directions(db.conn, lyath_id) == [(bloodworth_id, "father", "", "blood")]
    assert q.select_character_kin_both_directions(db.conn, bloodworth_id) == [(lyath_id, "child", "", "blood")]


def test_both_directions_query_combines_stated_and_derived(db: Database) -> None:
    """A person with a stated fact of their own plus an inverse derived from
    someone else's — both halves must appear, correctly labelled."""
    _story(
        db,
        characters=[
            CharacterEntry("Lyath", kin=((CharacterEntry("Bloodworth Goldmane"), "father"),)),
            CharacterEntry("Bloodworth Goldmane", kin=((CharacterEntry("Tara VanGeld"), "spouse"),)),
        ],
    )
    bloodworth_id = lore_character_id("Bloodworth Goldmane")
    lyath_id = lore_character_id("Lyath")
    tara_id = lore_character_id("Tara VanGeld")
    result = set(q.select_character_kin_both_directions(db.conn, bloodworth_id))
    assert result == {(lyath_id, "child", "", "blood"), (tara_id, "spouse", "", "blood")}


def test_sibling_and_spouse_are_their_own_inverse(db: Database) -> None:
    _story(db, characters=[CharacterEntry("Lyath", kin=((CharacterEntry("Victor"), "sibling"),))])
    victor_id = lore_character_id("Victor")
    lyath_id = lore_character_id("Lyath")
    assert q.select_character_kin_both_directions(db.conn, victor_id) == [(lyath_id, "sibling", "", "blood")]


# ---------------------------------------------------------------------------
# Round trip
# ---------------------------------------------------------------------------


def test_kin_survives_the_csv_round_trip(db: Database, tmp_path) -> None:
    import db._export as ex
    from db._seed import seed_from_csvs

    entry = CharacterEntry(
        "Lyath",
        kin=((CharacterEntry("Bloodworth Goldmane"), "father", "heroes-of-rathe/lyath-about.md"),),
    )
    _story(db, characters=[entry])
    ex.export_registry_tables(db.conn, tmp_path)
    ex.export_story_junctions(db.conn, tmp_path)

    (tmp_path / "csv").mkdir(exist_ok=True)
    fresh = Database(":memory:", data_dir=tmp_path)
    seed_from_csvs(fresh.conn, tmp_path)

    rows = q.select_character_kin(fresh.conn, lore_character_id("Lyath"))
    assert rows == [(lore_character_id("Bloodworth Goldmane"), "father", "heroes-of-rathe/lyath-about.md", "blood")]


def test_character_kin_csv_data_rows_are_well_formed_in_the_committed_data() -> None:
    """Every row in the committed CSV must be a real, well-formed fact.

    This test used to assert headers-only, back when no kinship fact was
    declared anywhere in entries/catalogue/ yet. Mercurius/Minerva Themis
    (``entries/catalogue/characters.py``, "The first ``kin=`` use in the
    catalogue.") landed the first real row, so the guard now checks the row
    itself rather than its absence: right columns, ids that resolve to a
    known character, a relation from the closed vocabulary, and a citation
    that is a real path under ``src/``.
    """
    from pathlib import Path

    repo_root = Path(__file__).resolve().parent.parent
    path = repo_root / "src" / "data" / "csv" / "character-kin.csv"
    assert path.is_file()
    lines = path.read_text(encoding="utf-8").splitlines()
    # Line 0 is the auto-gen banner, line 1 is the header row.
    header = "CharacterId|RelativeId|Relation|StoryKey|Qualifier"
    assert lines[1] == header
    columns = header.split("|")

    characters_path = repo_root / "src" / "data" / "csv" / "characters.csv"
    known_character_ids = {
        row.split("|")[0] for row in characters_path.read_text(encoding="utf-8").splitlines()[2:] if row
    }

    data_rows = lines[2:]
    assert data_rows, "character-kin.csv now carries a real fact; this must not go back to headers-only silently"

    seen: set[tuple[str, str, str]] = set()
    for row in data_rows:
        fields = row.split("|")
        assert len(fields) == len(columns), f"{row!r} does not have {len(columns)} columns"
        character_id, relative_id, relation, story_key, qualifier = fields

        assert character_id in known_character_ids, f"{character_id!r} is not a known CharacterId"
        assert relative_id in known_character_ids, f"{relative_id!r} is not a known RelativeId"
        assert character_id != relative_id, f"{character_id!r} names itself as its own relative"

        assert relation in q.KIN_INVERSE, f"{relation!r} is not one of {sorted(q.KIN_INVERSE)}"
        assert qualifier in q.KIN_QUALIFIERS, f"{qualifier!r} is not one of {sorted(q.KIN_QUALIFIERS)}"

        # Same stated fact must not appear twice, and its inverse must not be
        # separately stated — only the stated direction is ever written.
        assert (character_id, relative_id, relation) not in seen
        seen.add((character_id, relative_id, relation))
        assert (relative_id, character_id, q.KIN_INVERSE[relation]) not in seen

        if story_key:
            assert (repo_root / "src" / story_key).is_file(), f"StoryKey {story_key!r} does not point at a real file"

    mercurius_id = lore_character_id("Mercurius")
    minerva_id = lore_character_id("Minerva Themis")
    assert (mercurius_id, minerva_id, "sibling", "other-characters/minerva-themis.md", "blood") in {
        (*row.split("|"),) for row in data_rows
    }


# ---------------------------------------------------------------------------
# The qualifier vocabulary (migration 21): blood vs adoptive
# ---------------------------------------------------------------------------


def test_kin_qualifier_defaults_to_blood(db: Database) -> None:
    """A fact with no qualifier given is blood, not an empty/unknown value."""
    entry = CharacterEntry("Lyath", kin=((CharacterEntry("Bloodworth Goldmane"), "father"),))
    _story(db, characters=[entry])
    rows = q.select_character_kin(db.conn, lore_character_id("Lyath"))
    assert rows == [(lore_character_id("Bloodworth Goldmane"), "father", "", "blood")]


def test_kin_qualifier_can_be_stated_as_adoptive(db: Database) -> None:
    entry = CharacterEntry(
        "Dromai",
        kin=((CharacterEntry("Min"), "parent", "main-story/uprising/betrayal.md", "adoptive"),),
    )
    _story(db, characters=[entry])
    rows = q.select_character_kin(db.conn, lore_character_id("Dromai"))
    assert rows == [(lore_character_id("Min"), "parent", "main-story/uprising/betrayal.md", "adoptive")]


def test_kin_qualifier_survives_inversion(db: Database) -> None:
    """Adoptive is a fact about how the bond was formed, not about which end reads it."""
    entry = CharacterEntry("Min", kin=((CharacterEntry("Dromai"), "parent", "", "adoptive"),))
    _story(db, characters=[entry])
    dromai_id = lore_character_id("Dromai")
    min_id = lore_character_id("Min")
    assert q.select_character_kin_both_directions(db.conn, min_id) == [(dromai_id, "parent", "", "adoptive")]
    assert q.select_character_kin_both_directions(db.conn, dromai_id) == [(min_id, "child", "", "adoptive")]


def test_an_unknown_qualifier_raises_at_declaration_time(db: Database) -> None:
    with pytest.raises(ValueError, match="unknown kin qualifier"):
        _story(
            db,
            characters=[
                CharacterEntry("Lyath", kin=((CharacterEntry("Bloodworth Goldmane"), "father", "", "foster"),))
            ],
        )


def test_kin_qualifiers_frozenset_is_blood_and_adoptive() -> None:
    assert q.KIN_QUALIFIERS == frozenset({"blood", "adoptive"})


# ---------------------------------------------------------------------------
# The relation vocabulary, checked at write time
# ---------------------------------------------------------------------------
# `status` and `character_epithets.kind` are checked only by validate_data.py, because
# both are read back as text and a typo is a wrong label until the next hook run.
# `relation` cannot be left that late: it keys into KIN_INVERSE to derive the
# other end of the fact, so a bad value raises KeyError inside a query — during
# an mdbook build, long before pre-commit sees the CSV.


def test_an_unknown_relation_raises_at_declaration_time(db: Database) -> None:
    with pytest.raises(ValueError, match="unknown kin relation"):
        _story(db, characters=[CharacterEntry("Lyath", kin=((CharacterEntry("Bloodworth Goldmane"), "faher"),))])


def test_the_error_names_the_relations_that_are_allowed(db: Database) -> None:
    """A closed vocabulary is only usable if the failure says what it is."""
    with pytest.raises(ValueError) as excinfo:
        _story(db, characters=[CharacterEntry("Lyath", kin=((CharacterEntry("Bloodworth Goldmane"), "stepfather"),))])
    message = str(excinfo.value)
    for relation in ("father", "mother", "parent", "sibling", "spouse", "child"):
        assert relation in message


def test_a_bad_relation_writes_nothing(db: Database) -> None:
    """The guard runs during resolution, before any row is written."""
    with pytest.raises(ValueError):
        _story(db, characters=[CharacterEntry("Lyath", kin=((CharacterEntry("Bloodworth Goldmane"), "faher"),))])
    assert db.conn.execute("SELECT COUNT(*) FROM character_kin").fetchone()[0] == 0


def test_validate_datas_vocabulary_is_the_inverse_maps_own_keys() -> None:
    """Two literals would drift; a relation allowed by one and unknown to the
    other raises KeyError in the derivation rather than being reported."""
    import validate_data

    assert validate_data.KIN_RELATIONS == frozenset(q.KIN_INVERSE)


def test_every_relation_inverts_to_a_relation_that_is_itself_valid() -> None:
    """Inverting twice must land back inside the vocabulary, or a derived
    relation could not be stored if someone ever wrote it down."""
    for relation, inverse in q.KIN_INVERSE.items():
        assert inverse in q.KIN_INVERSE, f"{relation!r} inverts to {inverse!r}, which is not a relation"
