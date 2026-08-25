"""Integration checks for :mod:`validate_data`."""

from __future__ import annotations

import json
from pathlib import Path

import validate_data


def test_collect_alerts_empty_when_repository_consistent() -> None:
    """Committed CSVs under ``src/data`` satisfy validation rules."""
    assert validate_data.collect_alerts() == []


def test_check_location_lore_fragments_rejects_unsafe_ids(tmp_path: Path) -> None:
    """``LoreFragment`` must look like an HTML ``id`` fragment."""
    loc = tmp_path / "locations.csv"
    loc.write_text(
        "# banner\n" "LocationId|Name|RegionId|Notes|LoreFragment\n" "LO1|X|RG1||bad frag\n",
        encoding="utf-8",
    )
    alerts = validate_data._check_location_lore_fragments(loc)
    assert len(alerts) == 1
    assert "bad frag" in alerts[0]


def test_title_id_hash_drift_flags_stale_id(tmp_path: Path) -> None:
    from registry_ids import title_id

    path = tmp_path / "titles.csv"
    path.write_text(
        "# banner\nTitleId|Name|GroupId|Notes\nTIdeadbeef01|Grand Magister||\n",
        encoding="utf-8",
    )
    alerts = validate_data._check_id_hash_drift(path, "TitleId", "Name", title_id, "titles.csv")
    assert len(alerts) == 1
    assert "Grand Magister" in alerts[0]


def test_title_group_id_fk_tolerates_empty_string(tmp_path: Path) -> None:
    """titles.GroupId carries no SQL REFERENCES — '' must never be flagged."""
    path = tmp_path / "titles.csv"
    path.write_text("# banner\nTitleId|Name|GroupId|Notes\nTI1|Soothsayer||\n", encoding="utf-8")
    alerts = validate_data._check_fk_column(path, "GroupId", {"GRreal"}, "groups.csv GroupId", "Title <-> group link")
    assert alerts == []


def test_title_holders_fk_flags_an_unknown_title(tmp_path: Path) -> None:
    path = tmp_path / "title-holders.csv"
    path.write_text("# banner\nTitleId|CharacterId|Ordinal|StoryKey\nTIbogus001|LC1|0|\n", encoding="utf-8")
    alerts = validate_data._check_fk_column(path, "TitleId", {"TIreal00001"}, "titles.csv TitleId", "label")
    assert len(alerts) == 1
    assert "TIbogus001" in alerts[0]


def test_title_holders_fk_flags_an_unknown_character(tmp_path: Path) -> None:
    path = tmp_path / "title-holders.csv"
    path.write_text("# banner\nTitleId|CharacterId|Ordinal|StoryKey\nTI1|LCbogus0001|0|\n", encoding="utf-8")
    alerts = validate_data._check_fk_column(
        path, "CharacterId", {"LCreal000001"}, "characters.csv CharacterId", "label"
    )
    assert len(alerts) == 1
    assert "LCbogus0001" in alerts[0]


def test_collect_warnings_does_not_raise_or_block() -> None:
    """``collect_warnings`` is informational only; must always return a list."""
    warnings = validate_data.collect_warnings()
    assert isinstance(warnings, list)


def test_check_id_hash_drift_flags_stale_id(tmp_path: Path) -> None:
    from registry_ids import monster_id

    path = tmp_path / "monsters.csv"
    path.write_text(
        "# banner\nMonsterId|Name|Description\nMOdeadbeef01|Test Beast|\n",
        encoding="utf-8",
    )
    alerts = validate_data._check_id_hash_drift(path, "MonsterId", "Name", monster_id, "monsters.csv")
    assert len(alerts) == 1
    assert "Test Beast" in alerts[0]


def test_check_id_hash_drift_clean_when_id_matches(tmp_path: Path) -> None:
    from registry_ids import monster_id

    computed = monster_id("Test Beast")
    path = tmp_path / "monsters.csv"
    path.write_text(
        f"# banner\nMonsterId|Name|Description\n{computed}|Test Beast|\n",
        encoding="utf-8",
    )
    alerts = validate_data._check_id_hash_drift(path, "MonsterId", "Name", monster_id, "monsters.csv")
    assert alerts == []


def test_check_location_id_hash_drift_flags_stale_id(tmp_path: Path) -> None:
    path = tmp_path / "locations.csv"
    path.write_text(
        "# banner\nLocationId|Name|RegionId|Notes|LoreFragment\nLOdeadbeef01|Test Place|RG1||\n",
        encoding="utf-8",
    )
    alerts = validate_data._check_location_id_hash_drift(path)
    assert len(alerts) == 1
    assert "Test Place" in alerts[0]


def test_check_location_id_hash_drift_clean_when_id_matches(tmp_path: Path) -> None:
    from registry_ids import location_id

    computed = location_id("Test Place", "RG1")
    path = tmp_path / "locations.csv"
    path.write_text(
        f"# banner\nLocationId|Name|RegionId|Notes|LoreFragment\n{computed}|Test Place|RG1||\n",
        encoding="utf-8",
    )
    alerts = validate_data._check_location_id_hash_drift(path)
    assert alerts == []


def test_check_near_duplicate_names_flags_typo(tmp_path: Path) -> None:
    path = tmp_path / "locations.csv"
    path.write_text(
        "# banner\n"
        "LocationId|Name|RegionId|Notes|LoreFragment\n"
        "LO1|Amphitheatre|RG1||\n"
        "LO2|Ampitheatre|RG1||\n",
        encoding="utf-8",
    )
    alerts = validate_data._check_near_duplicate_names(
        path, "LocationId", "Name", "locations.csv", group_column="RegionId"
    )
    assert len(alerts) == 1
    assert "Amphitheatre" in alerts[0] and "Ampitheatre" in alerts[0]


def test_check_near_duplicate_names_ignores_unrelated_names(tmp_path: Path) -> None:
    path = tmp_path / "locations.csv"
    path.write_text(
        "# banner\n" "LocationId|Name|RegionId|Notes|LoreFragment\n" "LO1|The Maela|RG1||\n" "LO2|The Valdur|RG1||\n",
        encoding="utf-8",
    )
    alerts = validate_data._check_near_duplicate_names(
        path, "LocationId", "Name", "locations.csv", group_column="RegionId"
    )
    assert alerts == []


def test_check_near_duplicate_names_respects_group_column(tmp_path: Path) -> None:
    """Same near-duplicate name pair in *different* regions should not be flagged
    when grouped by region — they may legitimately be distinct places."""
    path = tmp_path / "locations.csv"
    path.write_text(
        "# banner\n"
        "LocationId|Name|RegionId|Notes|LoreFragment\n"
        "LO1|Ampitheatre|RG1||\n"
        "LO2|Amphitheatre|RG2||\n",
        encoding="utf-8",
    )
    alerts = validate_data._check_near_duplicate_names(
        path, "LocationId", "Name", "locations.csv", group_column="RegionId"
    )
    assert alerts == []


# ---------------------------------------------------------------------------
# hints_supplement.json entity types
# ---------------------------------------------------------------------------


def _supplement(tmp_path: Path, payload: dict) -> Path:
    path = tmp_path / "hints_supplement.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def test_check_supplement_types_accepts_known_types(tmp_path: Path) -> None:
    path = _supplement(tmp_path, {"Nimby": {"type": "ship", "summary": "A vessel."}})
    assert validate_data._check_supplement_types(path) == []


def test_check_supplement_types_flags_a_typo(tmp_path: Path) -> None:
    """The reason this check exists.

    theme/hints.js prints `type` verbatim as the tooltip label, so a misspelling
    ships as a visible label rather than failing anything downstream.
    """
    path = _supplement(tmp_path, {"Rosetta": {"type": "factoin", "summary": "An Order of spell weavers."}})
    alerts = validate_data._check_supplement_types(path)
    assert len(alerts) == 1
    assert "'factoin'" in alerts[0]


def test_check_supplement_types_skips_override_only_entries(tmp_path: Path) -> None:
    """25 entries carry only match/url/exclude_pages and take their type from the DB."""
    path = _supplement(tmp_path, {"Isenloft": {"url": "/world-of-rathe/aria.html#isenloft"}})
    assert validate_data._check_supplement_types(path) == []


def test_check_supplement_types_skips_plain_string_entries(tmp_path: Path) -> None:
    """The seven Solanian weekdays are stored as bare summary strings."""
    path = _supplement(tmp_path, {"Lunedes": "Solanian Monday"})
    assert validate_data._check_supplement_types(path) == []


def test_kind_and_faction_are_not_supplement_types() -> None:
    """Both left in stage 4, for the same reason: the DB is the writer now.

    `kind` was added so Chanek could be retyped off `faction`; four months
    later Chanek is a `kinds.csv` row and the supplement entry is gone, so a
    supplement entry claiming either type would be a second writer on one fact.
    """
    assert "kind" not in validate_data._SUPPLEMENT_TYPES
    assert "faction" not in validate_data._SUPPLEMENT_TYPES


def test_real_supplement_has_no_unknown_types() -> None:
    assert validate_data._check_supplement_types(validate_data.SRC / "hints_supplement.json") == []


# ---------------------------------------------------------------------------
# Group lore fragments
# ---------------------------------------------------------------------------


def _group_fragment_fixture(tmp_path: Path, lore_story_key: str, lore_fragment: str) -> tuple[Path, Path, Path]:
    src = tmp_path / "src"
    (src / "world-of-rathe").mkdir(parents=True)
    (src / "world-of-rathe" / "solana.md").write_text("# Solana\n\n### The Hand of Sol\n\ntext\n", encoding="utf-8")
    groups = tmp_path / "groups.csv"
    groups.write_text(
        "# banner\n"
        "GroupId|Name|Kind|Notes|ParentGroupId|LocationId|LoreStoryKey|LoreFragment\n"
        f"GR1|Hand of Sol|order|||| {lore_story_key}|{lore_fragment}\n".replace("| ", "|"),
        encoding="utf-8",
    )
    stories = tmp_path / "stories.csv"
    stories.write_text(
        "# banner\nStoryId|StoryKey|StoryType|Title\nST1|world-of-rathe/solana.md|world-of-rathe|Solana\n",
        encoding="utf-8",
    )
    return groups, stories, src


def test_check_group_lore_fragments_accepts_a_real_heading(tmp_path: Path) -> None:
    groups, stories, src = _group_fragment_fixture(tmp_path, "world-of-rathe/solana.md", "the-hand-of-sol")
    assert validate_data._check_group_lore_fragments(groups, stories, src) == []


def test_check_group_lore_fragments_rejects_a_missing_heading(tmp_path: Path) -> None:
    """Catches a heading renamed in the markdown, which nothing else would see."""
    groups, stories, src = _group_fragment_fixture(tmp_path, "world-of-rathe/solana.md", "the-hand-of-sun")
    alerts = validate_data._check_group_lore_fragments(groups, stories, src)
    assert len(alerts) == 1
    assert "the-hand-of-sun" in alerts[0]


def test_check_group_lore_fragments_rejects_an_unknown_page(tmp_path: Path) -> None:
    groups, stories, src = _group_fragment_fixture(tmp_path, "world-of-rathe/nowhere.md", "the-hand-of-sol")
    alerts = validate_data._check_group_lore_fragments(groups, stories, src)
    assert len(alerts) == 1
    assert "not a StoryKey" in alerts[0]


def test_check_group_lore_fragments_ignores_groups_with_no_link(tmp_path: Path) -> None:
    """Most groups carry no documentation page, and that is not an error."""
    groups, stories, src = _group_fragment_fixture(tmp_path, "", "")
    assert validate_data._check_group_lore_fragments(groups, stories, src) == []


# ---------------------------------------------------------------------------
# Membership and alternate-name FK checks
# ---------------------------------------------------------------------------


def test_epithet_kind_must_be_in_the_closed_list(tmp_path: Path) -> None:
    from validate_data import _check_epithet_kinds

    path = tmp_path / "character-epithets.csv"
    path.write_text("# x\nCharacterId|Name|Kind\nLC1|the Fixer|nickname\n")
    alerts = _check_epithet_kinds(path)
    assert len(alerts) == 1
    assert "nickname" in alerts[0]


def test_epithet_kind_accepts_both_valid_kinds(tmp_path: Path) -> None:
    from validate_data import _check_epithet_kinds

    path = tmp_path / "character-epithets.csv"
    path.write_text("# x\nCharacterId|Name|Kind\nLC1|the Fixer|epithet\nLC1|Mortimer|short-name\n")
    assert _check_epithet_kinds(path) == []


def test_character_status_must_be_in_the_closed_list(tmp_path: Path) -> None:
    from validate_data import _check_character_statuses

    path = tmp_path / "characters.csv"
    path.write_text("# x\nCharacterId|Name|Status|OtherCharactersStoryKey\nLC1|Lord Sutcliffe|Deceased|\n")
    alerts = _check_character_statuses(path)
    assert len(alerts) == 1
    assert "Deceased" in alerts[0]


def test_character_status_accepts_all_five_values(tmp_path: Path) -> None:
    from validate_data import _check_character_statuses

    path = tmp_path / "characters.csv"
    path.write_text(
        "# x\nCharacterId|Name|Status|OtherCharactersStoryKey\n"
        "LC1|A|Unknown|\nLC2|B|Alive|\nLC3|C|Dead|\nLC4|D|Assumed Dead|\nLC5|E|Missing|\n"
    )
    assert _check_character_statuses(path) == []


def test_kin_relation_must_be_in_the_closed_list(tmp_path: Path) -> None:
    from validate_data import _check_kin_relations

    path = tmp_path / "character-kin.csv"
    path.write_text("# x\nCharacterId|RelativeId|Relation|StoryKey\nLC1|LC2|stepfather|\n")
    alerts = _check_kin_relations(path)
    assert len(alerts) == 1
    assert "stepfather" in alerts[0]


def test_kin_relation_accepts_all_six_values(tmp_path: Path) -> None:
    from validate_data import _check_kin_relations

    path = tmp_path / "character-kin.csv"
    path.write_text(
        "# x\nCharacterId|RelativeId|Relation|StoryKey\n"
        "LC1|LC2|father|\nLC1|LC3|mother|\nLC1|LC4|parent|\n"
        "LC1|LC5|sibling|\nLC1|LC6|spouse|\nLC2|LC1|child|\n"
    )
    assert _check_kin_relations(path) == []


def test_no_self_kin_flags_a_character_named_as_its_own_relative(tmp_path: Path) -> None:
    from validate_data import _check_no_self_kin

    path = tmp_path / "character-kin.csv"
    path.write_text("# x\nCharacterId|RelativeId|Relation|StoryKey\nLC1|LC1|sibling|\n")
    alerts = _check_no_self_kin(path)
    assert len(alerts) == 1
    assert "LC1" in alerts[0]


def test_no_self_kin_accepts_two_different_characters(tmp_path: Path) -> None:
    from validate_data import _check_no_self_kin

    path = tmp_path / "character-kin.csv"
    path.write_text("# x\nCharacterId|RelativeId|Relation|StoryKey\nLC1|LC2|sibling|\n")
    assert _check_no_self_kin(path) == []


def test_character_kin_fk_flags_an_unknown_relative(tmp_path: Path) -> None:
    from validate_data import _check_fk_column

    path = tmp_path / "character-kin.csv"
    path.write_text("# x\nCharacterId|RelativeId|Relation|StoryKey\nLC1|LCbogus0001|father|\n")
    alerts = _check_fk_column(path, "RelativeId", {"LCreal000001"}, "characters.csv CharacterId", "Character kin")
    assert len(alerts) == 1
    assert "LCbogus0001" in alerts[0]


def test_character_heroes_fk_flags_an_unknown_hero(tmp_path: Path) -> None:
    from validate_data import _check_fk_column

    path = tmp_path / "character-heroes.csv"
    path.write_text("# x\nCanonicalId|CharacterId\nCNbogus0001|LC1\n")
    alerts = _check_fk_column(path, "CanonicalId", {"CNreal000001"}, "heroes-canonical.csv CanonicalId", "label")
    assert len(alerts) == 1
    assert "CNbogus0001" in alerts[0]


def test_character_heroes_fk_flags_an_unknown_character(tmp_path: Path) -> None:
    from validate_data import _check_fk_column

    path = tmp_path / "character-heroes.csv"
    path.write_text("# x\nCanonicalId|CharacterId\nCN1|LCbogus0001\n")
    alerts = _check_fk_column(path, "CharacterId", {"LCreal000001"}, "characters.csv CharacterId", "label")
    assert len(alerts) == 1
    assert "LCbogus0001" in alerts[0]


def _stranded_fixture(tmp_path: Path, characters: str, links: str) -> tuple[Path, Path, Path]:
    """Write the three CSVs the stranded-hero check reads, and return their paths."""
    chars = tmp_path / "characters.csv"
    chars.write_text("# x\nCharacterId|Name|Status|OtherCharactersStoryKey\n" + characters)
    canonical = tmp_path / "heroes-canonical.csv"
    canonical.write_text("# x\nCanonicalId|CanonicalSlug|CanonicalHero\nCN1|kox|Kox\n")
    link = tmp_path / "character-heroes.csv"
    link.write_text("# x\nCanonicalId|CharacterId\n" + links)
    return chars, canonical, link


def test_a_hero_named_character_with_no_link_is_reported_as_stranded(tmp_path: Path) -> None:
    """Resolving an identity pair re-points the hero and leaves the minted row behind."""
    from validate_data import _check_no_stranded_hero_character

    paths = _stranded_fixture(
        tmp_path,
        characters="LC1|Kox|Unknown|\nLC2|Fightmaster Kox|Unknown|\n",
        links="CN1|LC2\n",
    )
    alerts = _check_no_stranded_hero_character(*paths)
    assert len(alerts) == 1
    assert "'Kox'" in alerts[0] and "LC1" in alerts[0]


def test_a_hero_named_character_that_still_holds_its_link_is_not_reported(tmp_path: Path) -> None:
    """The unresolved state is the normal one and must stay silent."""
    from validate_data import _check_no_stranded_hero_character

    paths = _stranded_fixture(tmp_path, characters="LC1|Kox|Unknown|\n", links="CN1|LC1\n")
    assert _check_no_stranded_hero_character(*paths) == []


def test_an_ordinary_character_is_never_reported_as_stranded(tmp_path: Path) -> None:
    """The signature is 'named after a hero', so an unlinked ordinary character is fine."""
    from validate_data import _check_no_stranded_hero_character

    paths = _stranded_fixture(
        tmp_path,
        characters="LC1|Kox|Unknown|\nLC9|Xathari|Dead|\n",
        links="CN1|LC1\n",
    )
    assert _check_no_stranded_hero_character(*paths) == []


def test_the_catalogue_check_reaches_all_six_registries(monkeypatch) -> None:
    """The check must open every registry CSV, not return ``[]`` on a bad import.

    The bare ``except`` around the import turned a renamed module into a clean
    pass: ``catalogue/npcs.py`` became ``characters.py`` and all six specs
    stopped running, silently, while ``validate_data`` still printed OK. Count
    the CSVs the check opens — zero means it never got past the import.
    """
    opened: list[str] = []
    real = validate_data.read_pipe_csv

    def record(path, *args, **kwargs):
        opened.append(Path(path).name)
        return real(path, *args, **kwargs)

    monkeypatch.setattr(validate_data, "read_pipe_csv", record)
    validate_data._check_new_catalogue_names({})
    assert set(opened) == {
        "locations.csv",
        "characters.csv",
        "monsters.csv",
        "fauna.csv",
        "flora.csv",
        "food-and-drink.csv",
    }


def test_a_broken_catalogue_import_warns_instead_of_passing_quietly(monkeypatch) -> None:
    """An import the check cannot satisfy must reach the operator as a warning."""
    import builtins

    real_import = builtins.__import__

    def refuse_the_catalogue(name, *args, **kwargs):
        if name == "entries.catalogue":
            raise ImportError("no catalogue here")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", refuse_the_catalogue)
    alerts = validate_data._check_new_catalogue_names({})
    assert len(alerts) == 1
    assert "could not import" in alerts[0]
