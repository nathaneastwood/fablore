"""Tests for :mod:`mdbook_graph` preprocessor."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from mdbook_graph import (
    MARK_END,
    MARK_START,
    _DEFAULT_MIN_DEGREE,
    arc_slug_for_story,
    assign_slugs,
    build_graph,
    build_graph_html,
    build_printing_edges,
    inject_into_content,
    load_sets_by_arc,
    page_graph_targets,
    resolve_hero_url,
    walk_and_process,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def src_root(tmp_path: Path) -> Path:
    """A minimal ``src`` tree: two story types, a hero page, a region page, a weapon."""
    (tmp_path / "heroes-of-rathe").mkdir()
    (tmp_path / "heroes-of-rathe" / "dorinthea-about.md").write_text("# Dorinthea\n")
    (tmp_path / "world-of-rathe").mkdir()
    (tmp_path / "world-of-rathe" / "aria.md").write_text("# Aria\n")
    (tmp_path / "weapons").mkdir()
    (tmp_path / "weapons" / "dawnblade.md").write_text("# Dawnblade\n")

    csv_dir = tmp_path / "data" / "csv"
    csv_dir.mkdir(parents=True)

    # Two narrative stories, one reference page (skipped), one archive (skipped).
    (csv_dir / "stories.csv").write_text(
        "# AUTO-GENERATED\n"
        "StoryId|StoryKey|StoryType|Title|Authors|Artists|SourceLink|PublicationDate|ThumbnailImageLink\n"
        "ST1|main-story/monarch/sworn-to-protect.md|main-story|Sworn to Protect|||||\n"
        "ST2|short-stories/monarch/a-tale.md|short-stories|A Tale|||||\n"
        "ST3|heroes-of-rathe/dorinthea-about.md|heroes-of-rathe|Dorinthea|||||\n"
        "ST4|archive/old.md|archive|Old Page|||||\n"
    )
    (csv_dir / "heroes-canonical.csv").write_text(
        "# AUTO-GENERATED\n"
        "CanonicalId|CanonicalSlug|CanonicalHero\n"
        "CN1|dorinthea|Dorinthea\n"
        "CN2|pageless|Pageless Hero\n"
    )
    (csv_dir / "regions.csv").write_text(
        "# AUTO-GENERATED\n"
        "RegionId|RegionName|WorldOfRatheStoryKey\n"
        "RG1|Aria|world-of-rathe/aria.md\n"
        "RG2|Nowhere|\n"
    )
    (csv_dir / "locations.csv").write_text(
        "# AUTO-GENERATED\n"
        "LocationId|Name|RegionId|Notes|LoreFragment\n"
        "LO1|Enion|RG1||enion\n"
        "LO2|Unplaced|RG2||\n"
    )
    (csv_dir / "npcs.csv").write_text(
        "# AUTO-GENERATED\n"
        "CharacterId|Name|Species|Status|OtherCharactersStoryKey\n"
        "LC1|Minerva Themis|Human|Alive|other-characters/minerva-themis.md\n"
        "LC2|Nameless|Human|Unknown|\n"
    )
    (csv_dir / "weapons-canonical.csv").write_text(
        "# AUTO-GENERATED\n" "CanonicalWeaponId|CanonicalSlug|CanonicalWeapon\n" "CW1|dawnblade|Dawnblade\n"
    )
    (csv_dir / "fauna.csv").write_text("# AUTO-GENERATED\nFaunaId|Name|Description\nFA1|Kraken|Big.\n")
    (csv_dir / "sets.csv").write_text(
        "# AUTO-GENERATED\n"
        "SetId|SetTypeId|SetName|InitialReleaseDate\n"
        "MON|TY1|Monarch|2021-04-30T00:00:00.000Z\n"
        "UPR|TY1|Uprising|2022-08-05T00:00:00.000Z\n"
    )
    (csv_dir / "story-arcs.csv").write_text(
        "# Hand-maintained.\n"
        "Slug|SetId|DisplayName|ImageLink|SortDate\n"
        "monarch|MON|||\n"
        "uprising|UPR|The Uprising||\n"
        "interlude||Interlude||2022-04-11\n"
        "ghost-set|ZZZ|||\n"
    )

    # Junctions. ST3/ST4 rows must be dropped with their stories.
    (csv_dir / "story-heroes.csv").write_text(
        "# AUTO-GENERATED\n"
        "StoryId|CanonicalId|Fragment\n"
        "ST1|CN1|\n"
        "ST2|CN1|\n"
        "ST2|CN2|\n"
        "ST3|CN1|\n"
        "ST4|CN1|\n"
    )
    (csv_dir / "story-regions.csv").write_text("# AUTO-GENERATED\nStoryId|RegionId\nST1|RG1\nST2|RG2\n")
    (csv_dir / "story-locations.csv").write_text("# AUTO-GENERATED\nStoryId|LocationId\nST1|LO1\nST2|LO2\n")
    (csv_dir / "story-npcs.csv").write_text("# AUTO-GENERATED\nStoryId|CharacterId|Fragment\nST1|LC1|\nST1|LC2|\n")
    (csv_dir / "story-weapons.csv").write_text("# AUTO-GENERATED\nStoryId|CanonicalWeaponId\nST1|CW1\n")
    (csv_dir / "story-fauna.csv").write_text("# AUTO-GENERATED\nStoryId|FaunaId\nST2|FA1\n")
    return tmp_path


def _by_name(graph: dict) -> dict[str, dict]:
    return {n["n"]: n for n in graph["nodes"]}


def _edge_names(graph: dict) -> set[tuple[str, str]]:
    ns = graph["nodes"]
    return {tuple(sorted((ns[a]["n"], ns[b]["n"]))) for a, b in graph["links"]}


# ---------------------------------------------------------------------------
# build_graph
# ---------------------------------------------------------------------------


def test_narrative_stories_become_nodes(src_root: Path) -> None:
    graph = build_graph(src_root / "data", src_root)
    names = _by_name(graph)
    assert names["Sworn to Protect"]["k"] == "story"
    assert names["Sworn to Protect"]["u"] == "main-story/monarch/sworn-to-protect.html"
    assert names["Sworn to Protect"]["s"] == "Main Story"


def test_every_rendered_story_type_has_its_own_label(src_root: Path) -> None:
    """The panel shows ``sub``, so a story must say which kind of page it is.

    A story type missing from the label map falls back to the bare word
    "Story", which is exactly the ambiguity the column exists to remove.
    """
    csv_dir = src_root / "data" / "csv"
    csv_dir.joinpath("stories.csv").write_text(
        "# AUTO-GENERATED\n"
        "StoryId|StoryKey|StoryType|Title|Authors|Artists|SourceLink|PublicationDate|ThumbnailImageLink\n"
        "ST1|main-story/monarch/a.md|main-story|A|||||\n"
        "ST2|short-stories/monarch/b.md|short-stories|B|||||\n"
        "ST3|flavour/monarch.md|flavour|C|||||\n"
        "ST4|digital-tiles/monarch/d.md|digital-tiles|D|||||\n"
        "ST5|summaries/e.md|summaries|E|||||\n"
        "ST6|world-of-rathe/f.md|world-of-rathe|F|||||\n"
    )
    # Neither sits under an arc folder, so only an entity link keeps them in.
    csv_dir.joinpath("story-regions.csv").write_text("# AUTO-GENERATED\nStoryId|RegionId\nST5|RG1\nST6|RG1\n")
    graph = build_graph(src_root / "data", src_root)
    subs = {n["n"]: n["s"] for n in graph["nodes"] if n["k"] == "story"}
    assert subs == {
        "A": "Main Story",
        "B": "Short Story",
        "C": "Flavour Text",
        "D": "Digital Tile",
        "E": "Summary",
        "F": "World of Rathe",
    }


def test_reference_and_archive_story_types_are_skipped(src_root: Path) -> None:
    """A hero's own page is reached through the hero node, not a duplicate story node."""
    graph = build_graph(src_root / "data", src_root)
    names = _by_name(graph)
    assert "Old Page" not in names
    # ``Dorinthea`` survives, but as the hero node.
    assert names["Dorinthea"]["k"] == "hero"
    assert sum(1 for n in graph["nodes"] if n["n"] == "Dorinthea") == 1


def test_edges_from_skipped_stories_are_dropped(src_root: Path) -> None:
    graph = build_graph(src_root / "data", src_root)
    edges = _edge_names(graph)
    assert ("Dorinthea", "Sworn to Protect") in edges
    assert ("A Tale", "Dorinthea") in edges
    assert len([e for e in edges if "Dorinthea" in e]) == 2


def test_entity_with_no_story_is_omitted(src_root: Path) -> None:
    """An unreferenced registry row would render as an isolated dot."""
    csv_dir = src_root / "data" / "csv"
    csv_dir.joinpath("fauna.csv").write_text(
        "# AUTO-GENERATED\n" "FaunaId|Name|Description\n" "FA1|Kraken|Big.\n" "FA2|Unmentioned|Never appears.\n"
    )
    graph = build_graph(src_root / "data", src_root)
    assert "Unmentioned" not in _by_name(graph)
    assert "Kraken" in _by_name(graph)


def test_hero_url_resolves_only_when_the_page_exists(src_root: Path) -> None:
    graph = build_graph(src_root / "data", src_root)
    names = _by_name(graph)
    assert names["Dorinthea"]["u"] == "heroes-of-rathe/dorinthea-about.html"
    assert names["Pageless Hero"]["u"] == ""


def test_location_url_deep_links_into_its_region_page(src_root: Path) -> None:
    graph = build_graph(src_root / "data", src_root)
    names = _by_name(graph)
    assert names["Enion"]["u"] == "world-of-rathe/aria.html#enion"
    # A region with no world-of-rathe page cannot host its locations.
    assert names["Unplaced"]["u"] == ""
    assert names["Nowhere"]["u"] == ""


def test_npc_and_weapon_urls(src_root: Path) -> None:
    graph = build_graph(src_root / "data", src_root)
    names = _by_name(graph)
    assert names["Minerva Themis"]["u"] == "other-characters/minerva-themis.html"
    assert names["Nameless"]["u"] == ""
    assert names["Dawnblade"]["u"] == "weapons/dawnblade.html"


def test_colour_groups_fold_the_sparse_kinds(src_root: Path) -> None:
    graph = build_graph(src_root / "data", src_root)
    names = _by_name(graph)
    assert names["Sworn to Protect"]["g"] == "story"
    assert names["Dorinthea"]["g"] == "character"
    assert names["Minerva Themis"]["g"] == "character"
    assert names["Enion"]["g"] == "place"
    assert names["Aria"]["g"] == "place"
    assert names["Kraken"]["g"] == "other"
    assert names["Dawnblade"]["g"] == "other"


def test_hero_and_region_carry_a_star_shape(src_root: Path) -> None:
    """Shape separates the two pairs that share a hue.

    ``hero``/``npc`` both sit in the ``character`` colour group and
    ``region``/``location`` both sit in ``place``, because the palette has no
    fifth hue that clears the all-pairs colour-vision floor. Shape is what tells
    them apart, so it must not silently revert to a circle.
    """
    graph = build_graph(src_root / "data", src_root)
    shapes = {g["k"]: g["s"] for g in graph["groups"]}
    assert shapes["hero"] == "star"
    assert shapes["region"] == "star"
    assert shapes["npc"] == "circle"
    assert shapes["location"] == "circle"
    # The starred kind and its circled partner must still share one hue,
    # otherwise the shape channel is redundant and a hue has been overspent.
    colour = {g["k"]: g["g"] for g in graph["groups"]}
    assert colour["hero"] == colour["npc"] == "character"
    assert colour["region"] == colour["location"] == "place"


def test_groups_legend_counts_only_rendered_nodes(src_root: Path) -> None:
    graph = build_graph(src_root / "data", src_root)
    counts = {g["k"]: g["c"] for g in graph["groups"]}
    assert counts["story"] == 2
    assert counts["hero"] == 2
    assert counts["npc"] == 2
    assert counts["region"] == 2
    assert "flora" not in counts


def test_links_are_deduplicated_and_indices_are_in_range(src_root: Path) -> None:
    graph = build_graph(src_root / "data", src_root)
    assert len(graph["links"]) == len(set(map(tuple, graph["links"])))
    for a, b in graph["links"]:
        assert 0 <= a < len(graph["nodes"])
        assert 0 <= b < len(graph["nodes"])
        assert a != b


def test_missing_csv_files_do_not_raise(tmp_path: Path) -> None:
    (tmp_path / "data" / "csv").mkdir(parents=True)
    graph = build_graph(tmp_path / "data", tmp_path)
    assert graph == {"nodes": [], "links": [], "prints": [], "groups": [], "subs": []}


# ---------------------------------------------------------------------------
# Sets
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("key", "expected"),
    [
        ("main-story/monarch/sworn-to-protect.md", "monarch"),
        ("short-stories/uprising/betrayal.md", "uprising"),
        ("digital-tiles/monarch/monarch.md", "monarch"),
        ("flavour/monarch.md", "monarch"),
        # No arc level: world pages, summaries and section roots.
        ("world-of-rathe/aria.md", ""),
        ("summaries/monarch.md", ""),
        ("browse.md", ""),
        ("", ""),
    ],
)
def test_arc_slug_for_story(key: str, expected: str) -> None:
    assert arc_slug_for_story(key) == expected


def test_load_sets_by_arc_skips_arcs_without_a_released_set(src_root: Path) -> None:
    by_arc = load_sets_by_arc(src_root / "data")
    assert by_arc["monarch"] == "Monarch"
    # A grouping folder with no SetId is not a set.
    assert "interlude" not in by_arc
    # A SetId with no row in sets.csv cannot be named, so it is dropped.
    assert "ghost-set" not in by_arc


def test_display_name_overrides_the_upstream_set_name(src_root: Path) -> None:
    assert load_sets_by_arc(src_root / "data")["uprising"] == "The Uprising"


def test_set_nodes_link_the_stories_of_their_arc(src_root: Path) -> None:
    graph = build_graph(src_root / "data", src_root)
    names = _by_name(graph)
    assert names["Monarch"]["k"] == "set"
    assert names["Monarch"]["g"] == "set"
    assert names["Monarch"]["u"] == "sets/index.html#monarch"
    assert ("Monarch", "Sworn to Protect") in _edge_names(graph)


def test_panel_section_order_expands_stories_into_their_types(src_root: Path) -> None:
    """The panel groups by ``sub``, so the order must name story types, not "Story"."""
    graph = build_graph(src_root / "data", src_root)
    subs = graph["subs"]
    assert subs[0] == "Set", "sets lead the panel"
    assert "Story" not in subs, "the coarse label must not appear as a section"
    assert subs.index("Main Story") < subs.index("Short Story") < subs.index("Hero")
    # Every node must land in exactly one section.
    assert {n["s"] for n in graph["nodes"]} == set(subs)
    assert len(subs) == len(set(subs))


def test_set_node_ids_cannot_collide_with_a_registry_id(src_root: Path) -> None:
    """A set is keyed by arc slug, so its node id is prefixed to stay distinct."""
    graph = build_graph(src_root / "data", src_root)
    monarch = [n for n in graph["nodes"] if n["n"] == "Monarch"]
    assert len(monarch) == 1


def test_a_story_whose_only_link_is_its_set_still_renders(src_root: Path) -> None:
    """Before set nodes existed this story had no edge and was dropped."""
    csv_dir = src_root / "data" / "csv"
    csv_dir.joinpath("stories.csv").write_text(
        csv_dir.joinpath("stories.csv").read_text() + "ST5|main-story/monarch/lonely.md|main-story|Lonely Tale|||||\n"
    )
    graph = build_graph(src_root / "data", src_root)
    assert "Lonely Tale" in _by_name(graph)
    assert ("Lonely Tale", "Monarch") in _edge_names(graph)


def test_missing_arc_csvs_leave_the_rest_of_the_graph_intact(src_root: Path) -> None:
    (src_root / "data" / "csv" / "story-arcs.csv").unlink()
    graph = build_graph(src_root / "data", src_root)
    assert not [n for n in graph["nodes"] if n["k"] == "set"]
    assert "Sworn to Protect" in _by_name(graph)


# ---------------------------------------------------------------------------
# Deep-link slugs
# ---------------------------------------------------------------------------


def test_a_unique_name_keeps_a_bare_slug(src_root: Path) -> None:
    """``graph.html#dorinthea`` beats ``graph.html#CNb6ce517916``."""
    graph = build_graph(src_root / "data", src_root)
    assert _by_name(graph)["Dorinthea"]["sl"] == "dorinthea"


def test_a_repeated_name_takes_a_type_suffix() -> None:
    nodes = [
        {"n": "Bright Lights", "s": "Set"},
        {"n": "Bright Lights", "s": "Flavour Text"},
        {"n": "Dorinthea", "s": "Hero"},
    ]
    assign_slugs(nodes)
    assert {n["sl"] for n in nodes} == {
        "bright-lights-set",
        "bright-lights-flavour-text",
        "dorinthea",
    }


def test_slugs_are_unique_across_the_whole_graph(src_root: Path) -> None:
    graph = build_graph(src_root / "data", src_root)
    slugs = [n["sl"] for n in graph["nodes"]]
    assert len(slugs) == len(set(slugs))
    assert all(slugs)


def test_a_repeat_within_one_type_still_resolves_to_distinct_slugs() -> None:
    """The data has no such repeat today; the numeric fallback is the safety net."""
    nodes = [{"n": "Echo", "s": "Character"}, {"n": "Echo", "s": "Character"}]
    assign_slugs(nodes)
    assert len({n["sl"] for n in nodes}) == 2


def test_slug_assignment_does_not_depend_on_node_order() -> None:
    """A shared link must survive a reordering of the underlying CSV rows."""
    a = [
        {"n": "Aria", "s": "Region"},
        {"n": "Aria", "s": "World of Rathe"},
        {"n": "Dorinthea", "s": "Hero"},
    ]
    b = list(reversed([dict(n) for n in a]))
    assign_slugs(a)
    assign_slugs(b)
    assert {n["n"] + "|" + n["s"]: n["sl"] for n in a} == {n["n"] + "|" + n["s"]: n["sl"] for n in b}


# ---------------------------------------------------------------------------
# page_graph_targets
# ---------------------------------------------------------------------------


def test_a_page_maps_to_its_busiest_node(src_root: Path) -> None:
    """``world-of-rathe/aria.md`` is both the Region and a story of that name."""
    graph = build_graph(src_root / "data", src_root)
    targets = page_graph_targets(graph)
    assert targets["heroes-of-rathe/dorinthea-about.md"]["n"] == "Dorinthea"
    assert targets["main-story/monarch/sworn-to-protect.md"]["k"] == "story"


def test_deep_linked_locations_never_claim_the_region_page(src_root: Path) -> None:
    """A location's URL carries a ``#fragment``; a backlink there would misname itself."""
    graph = build_graph(src_root / "data", src_root)
    targets = page_graph_targets(graph)
    assert targets["world-of-rathe/aria.md"]["k"] in {"region", "story"}
    assert all(n["k"] != "location" for n in targets.values())


def test_pages_without_a_node_are_absent(src_root: Path) -> None:
    graph = build_graph(src_root / "data", src_root)
    targets = page_graph_targets(graph)
    assert "browse.md" not in targets
    assert all(not path.endswith(".html") for path in targets)


# ---------------------------------------------------------------------------
# resolve_hero_url
# ---------------------------------------------------------------------------


def test_resolve_hero_url_falls_back_to_the_bare_slug(tmp_path: Path) -> None:
    (tmp_path / "heroes-of-rathe").mkdir()
    (tmp_path / "heroes-of-rathe" / "rhinar.md").write_text("# Rhinar\n")
    assert resolve_hero_url(tmp_path, "rhinar") == "heroes-of-rathe/rhinar.html"


def test_resolve_hero_url_empty_for_unknown_slug(tmp_path: Path) -> None:
    (tmp_path / "heroes-of-rathe").mkdir()
    assert resolve_hero_url(tmp_path, "nobody") == ""
    assert resolve_hero_url(tmp_path, "  ") == ""


# ---------------------------------------------------------------------------
# Injection
# ---------------------------------------------------------------------------


def test_build_graph_html_embeds_the_payload() -> None:
    html = build_graph_html(
        {"nodes": [{"n": "A", "k": "story", "g": "story", "u": "", "s": "Story"}], "links": [], "groups": []}
    )
    assert "window.FABLORE_GRAPH=" in html
    assert 'id="lore-graph-canvas"' in html
    assert 'id="lore-graph-legend"' in html


@pytest.fixture
def printings_root(tmp_path: Path) -> Path:
    """Two sets that each have a story, and a hero printed in both but written
    into only one — the shape the real data takes, where Boltyn appears in
    Everfest stories and his card was printed in none of them.
    """
    csv_dir = tmp_path / "data" / "csv"
    csv_dir.mkdir(parents=True)
    (csv_dir / "stories.csv").write_text(
        "# AUTO-GENERATED\n"
        "StoryId|StoryKey|StoryType|Title|Authors|Artists|SourceLink|PublicationDate|ThumbnailImageLink\n"
        "ST1|main-story/monarch/a.md|main-story|A|||||\n"
        "ST2|main-story/uprising/b.md|main-story|B|||||\n"
    )
    (csv_dir / "sets.csv").write_text(
        "# AUTO-GENERATED\n"
        "SetId|SetTypeId|SetName|InitialReleaseDate\n"
        "MON|TY1|Monarch|2021-04-30T00:00:00.000Z\n"
        "UPR|TY1|Uprising|2022-08-05T00:00:00.000Z\n"
    )
    (csv_dir / "story-arcs.csv").write_text(
        "# Hand-maintained.\n"
        "Slug|SetId|DisplayName|ImageLink|SortDate\n"
        "monarch|MON|||\n"
        "uprising|UPR|||\n"
        "ghost|ZZZ|||\n"  # an arc whose set is not in sets.csv, so has no node
    )
    (csv_dir / "heroes-canonical.csv").write_text(
        "# AUTO-GENERATED\n"
        "CanonicalId|CanonicalSlug|CanonicalHero\n"
        "CN1|dorinthea|Dorinthea\n"
        "CN2|rhinar|Rhinar\n"
        "CN3|ghost|Ghost\n"
    )
    # CN1 is written into Monarch only; CN2 into Uprising only; CN3 nowhere, so
    # it never becomes a node.
    (csv_dir / "story-heroes.csv").write_text("# AUTO-GENERATED\nStoryId|CanonicalId|Fragment\nST1|CN1|\nST2|CN2|\n")
    (csv_dir / "heroes-game.csv").write_text(
        "# AUTO-GENERATED\n"
        "HeroGameId|CardName|CanonicalId|ClassIds|TalentIds|Health|Intellect|AbilityText|YoungHero\n"
        "HG1|Dorinthea|CN1|||20|4||false\n"
        "HG2|Rhinar|CN2|||20|4||false\n"
        "HG3|Ghost|CN3|||20|4||false\n"
    )
    (csv_dir / "heroes-printings.csv").write_text(
        "# AUTO-GENERATED\n"
        "HeroGameId|SetId|CardId|Rarity\n"
        "HG1|MON|MON001|M\n"  # printed where it is also written
        "HG1|MON|MON002|R\n"  # a second printing of the same pair
        "HG1|UPR|UPR001|M\n"  # printed where it is NOT written — the point
        "HG1|ZZZ|ZZZ001|M\n"  # set has an arc but no node
        "HG3|MON|MON003|M\n"  # hero has no node
        "HG9|MON|MON004|M\n"  # game id in no join table
    )

    # Weapons and equipment join the same way, through their own three tables.
    (csv_dir / "weapons-canonical.csv").write_text(
        "# AUTO-GENERATED\nCanonicalWeaponId|CanonicalSlug|CanonicalWeapon\nCW1|dawnblade|Dawnblade\n"
    )
    (csv_dir / "story-weapons.csv").write_text("# AUTO-GENERATED\nStoryId|CanonicalWeaponId\nST1|CW1\n")
    (csv_dir / "weapons-game.csv").write_text(
        "# AUTO-GENERATED\n"
        "WeaponGameId|CardName|CanonicalWeaponId|ClassIds|TalentIds|Cost|Power|AbilityText|Types\n"
        "WG1|Dawnblade|CW1||||||\n"
    )
    (csv_dir / "weapons-printings.csv").write_text(
        "# AUTO-GENERATED\nWeaponGameId|SetId|CardId|Rarity|ImageURL\nWG1|UPR|UPR050|R|\n"
    )
    (csv_dir / "equipment-canonical.csv").write_text(
        "# AUTO-GENERATED\nCanonicalEquipmentId|CanonicalSlug|CanonicalEquipment\nCE1|helm-of-light|Helm of Light\n"
    )
    (csv_dir / "story-equipment.csv").write_text("# AUTO-GENERATED\nStoryId|CanonicalEquipmentId\nST1|CE1\n")
    (csv_dir / "equipment-game.csv").write_text(
        "# AUTO-GENERATED\n"
        "EquipmentGameId|CardName|CanonicalEquipmentId|ClassIds|TalentIds|Cost|Defense|AbilityText|Types\n"
        "EG1|Helm of Light|CE1||||||\n"
    )
    (csv_dir / "equipment-printings.csv").write_text(
        "# AUTO-GENERATED\nEquipmentGameId|SetId|CardId|Rarity|ImageURL\nEG1|MON|MON110|P|\n"
    )
    return tmp_path


class TestPrintingEdges:
    """A hero card is printed in a set. That is the one relation on the graph
    that is not an appearance in a story, and it is recorded rather than
    inferred — so it must stay separable from the story edges at every step.
    """

    def _graph(self, root: Path) -> dict:
        return build_graph(root / "data", root)

    def test_printings_only_ever_join_a_printed_card_to_a_set(self, printings_root: Path) -> None:
        """Heroes, weapons and equipment are printed on cards. Regions, monsters
        and the rest are not, and must never gain a dashed line."""
        graph = self._graph(printings_root)
        kinds = [n["k"] for n in graph["nodes"]]
        assert graph["prints"], "no printing edges were built at all"
        wrong = set()
        for a, b in graph["prints"]:
            pair = {kinds[a], kinds[b]}
            if "set" not in pair or not (pair - {"set"}) <= {"hero", "weapon", "equipment"}:
                wrong.add((kinds[a], kinds[b]))
        assert wrong == set(), f"printing edges joining the wrong kinds: {sorted(wrong)}"

    def test_weapons_and_equipment_are_printed_too(self, printings_root: Path) -> None:
        """All three card types use the same three-table join, so a column name
        drifting on any one of them must fail here rather than silently drop
        that type's dashed lines."""
        graph = self._graph(printings_root)
        kinds = [n["k"] for n in graph["nodes"]]
        printed_kinds = {kinds[a] for a, b in graph["prints"]} | {kinds[b] for a, b in graph["prints"]}
        assert {"hero", "weapon", "equipment"} <= printed_kinds

    def test_a_printing_is_not_the_same_claim_as_appearing_in_a_story(self, printings_root: Path) -> None:
        """The whole reason these are drawn differently. Dorinthea is written
        into Monarch and printed in both Monarch and Uprising; the Uprising edge
        is a fact no story edge carries."""
        graph = self._graph(printings_root)
        names = [n["n"] for n in graph["nodes"]]
        printed = {tuple(sorted((names[a], names[b]))) for a, b in graph["prints"]}
        assert printed == {
            ("Dorinthea", "Monarch"),
            ("Dorinthea", "Uprising"),
            ("Dawnblade", "Uprising"),
            ("Helm of Light", "Monarch"),
        }
        # Nothing joins Dorinthea to an Uprising story, so the graph says this
        # only because a printing says it.
        story_pairs = {tuple(sorted((names[a], names[b]))) for a, b in graph["links"]}
        assert ("Dorinthea", "Uprising") not in story_pairs

    def test_printings_decorate_the_graph_and_never_grow_it(self, printings_root: Path) -> None:
        """A hero no story mentions has no node and must not gain one here, or
        the legend counts stop agreeing with the story edges they came from."""
        graph = self._graph(printings_root)
        assert "Ghost" not in {n["n"] for n in graph["nodes"]}
        n = len(graph["nodes"])
        assert all(0 <= a < n and 0 <= b < n for a, b in graph["prints"])
        story_linked = {x for e in graph["links"] for x in e}
        stranded = {x for e in graph["prints"] for x in e} - story_linked
        assert stranded == set(), (
            f"{len(stranded)} node(s) held in the graph by a printing alone. "
            "Printings are supplementary; they must not pull in nodes."
        )

    def test_repeat_printings_of_one_card_collapse_to_one_edge(self, printings_root: Path) -> None:
        """A hero is reprinted; the graph still draws one line."""
        graph = self._graph(printings_root)
        pairs = [tuple(e) for e in graph["prints"]]
        assert len(pairs) == len(set(pairs))
        assert all(a != b for a, b in pairs)

    def test_the_real_archive_builds_printings(self, src_root: Path) -> None:
        """The fixture proves the rules; this proves the join actually resolves
        against the committed CSVs, which is where the column names can drift."""
        root = Path(__file__).resolve().parents[1]
        graph = build_graph(root / "src" / "data", root / "src")
        assert len(graph["prints"]) > 50, "the printings join stopped resolving"

    def test_missing_join_tables_are_skipped_rather_than_raising(self, tmp_path: Path) -> None:
        """Most sets have no arc, so no node, and a clean checkout may be
        missing a table entirely. Neither may break the build."""
        assert build_printing_edges(tmp_path, {"CN1": 0}, {}) == []
        assert build_printing_edges(tmp_path, {}, {"welcome-to-rathe": 1}) == []


def test_the_graph_opens_on_sets_stories_heroes_and_regions(src_root: Path) -> None:
    """The opening view is the release structure and who runs through it.

    Everything else is in the legend but folded away: all twelve kinds at once
    is a hairball, and the shape a reader came for is under it.
    """
    graph = build_graph(src_root / "data", src_root)
    on = {g["k"] for g in graph["groups"] if g["o"]}
    assert on == {"set", "story", "hero", "region"}
    # Every kind still has to declare itself either way — a new kind that
    # silently defaulted to off would just be missing.
    assert all("o" in g for g in graph["groups"])


def test_the_slider_and_the_script_agree_on_the_opening_minimum() -> None:
    """The script reads its opening filter off this markup. If the rendered
    value drifts from what the graph shows, the control lies about the view."""
    html = build_graph_html({"nodes": [], "links": [], "groups": []})
    assert f'id="lore-graph-degree" min="1" max="6" value="{_DEFAULT_MIN_DEGREE}"' in html
    assert f'<output id="lore-graph-degree-value">{_DEFAULT_MIN_DEGREE}</output>' in html


def test_build_graph_html_carries_the_narrow_viewport_list_container() -> None:
    """``theme/graph.js`` fills this below the canvas breakpoint; without it the
    phone gets a stage too small to hit."""
    html = build_graph_html({"nodes": [], "links": [], "groups": []})
    assert 'id="lore-graph-list"' in html
    assert 'class="lore-graph-hint lore-graph-hint-graph"' in html
    assert 'class="lore-graph-hint lore-graph-hint-list"' in html


def test_status_live_region_sits_outside_the_stage() -> None:
    """A silent coupling: list mode hides the stage, and a hidden ancestor takes
    the live region down with it, so the node tally would stop reaching screen
    readers on exactly the viewport that has no canvas to look at."""
    html = build_graph_html({"nodes": [], "links": [], "groups": []})
    stage = html.split('id="lore-graph-stage"', 1)[1].split('id="lore-graph-list"', 1)[0]
    assert "lore-graph-status" not in stage
    assert 'id="lore-graph-status"' in html


def test_build_graph_html_payload_is_valid_json(src_root: Path) -> None:
    graph = build_graph(src_root / "data", src_root)
    html = build_graph_html(graph)
    payload = html.split("window.FABLORE_GRAPH=", 1)[1].split(";</script>", 1)[0]
    assert json.loads(payload)["nodes"]


def test_inject_replaces_an_existing_marker_block() -> None:
    content = f"# Title\n\nIntro.\n\n{MARK_START}\nstale\n{MARK_END}\n\nAfter.\n"
    out = inject_into_content(content, "<div>fresh</div>")
    assert "stale" not in out
    assert "<div>fresh</div>" in out
    assert "After." in out
    assert out.count(MARK_START) == 1


def test_inject_appends_when_no_marker_is_present() -> None:
    out = inject_into_content("# Title\n", "<div>fresh</div>")
    assert out.startswith("# Title")
    assert MARK_START in out and MARK_END in out


def test_walk_only_touches_the_graph_chapter() -> None:
    book = {
        "items": [
            {"Chapter": {"path": "intro.md", "content": "# Intro\n", "sub_items": []}},
            {
                "Chapter": {
                    "path": "graph.md",
                    "content": f"# Graph\n\n{MARK_START}\n{MARK_END}\n",
                    "sub_items": [{"Chapter": {"path": "other.md", "content": "# Other\n", "sub_items": []}}],
                }
            },
        ]
    }
    walk_and_process(book["items"], {"nodes": [], "links": [], "groups": []})
    assert "FABLORE_GRAPH" not in book["items"][0]["Chapter"]["content"]
    assert "FABLORE_GRAPH" in book["items"][1]["Chapter"]["content"]
    assert "FABLORE_GRAPH" not in book["items"][1]["Chapter"]["sub_items"][0]["Chapter"]["content"]
