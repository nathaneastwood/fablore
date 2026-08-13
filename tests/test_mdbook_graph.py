"""Tests for :mod:`mdbook_graph` preprocessor."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from mdbook_graph import (
    MARK_END,
    MARK_START,
    arc_slug_for_story,
    assign_slugs,
    build_graph,
    build_graph_html,
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
    assert graph == {"nodes": [], "links": [], "groups": [], "subs": []}


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
