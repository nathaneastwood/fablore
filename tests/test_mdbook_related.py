"""Tests for ``mdbook_related`` mdBook preprocessor helpers."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src/data"))

from mdbook_related import (  # noqa: E402
    RelatedMaps,
    build_related_fragment,
    inject_marked_block,
    load_related_maps,
    relative_md_href,
    resolve_hero_src_path,
)


def test_relative_md_href_nested_chapter_to_hero() -> None:
    assert (
        relative_md_href(
            "main-story/01-welcome-to-rathe/a-rising-star.md",
            "heroes-of-rathe/bravo-about.md",
        )
        == "../../heroes-of-rathe/bravo-about.md"
    )


def test_relative_md_href_same_directory() -> None:
    assert (
        relative_md_href("world-of-rathe/solana.md", "world-of-rathe/metrix.md")
        == "metrix.md"
    )


def test_inject_marked_block_appends() -> None:
    out = inject_marked_block("# Hi\n", "<p>x</p>")
    assert "<!-- fablore-related:start -->" in out
    assert "<p>x</p>" in out
    assert "# Hi" in out


def test_inject_marked_block_replaces() -> None:
    base = "A\n\n<!-- fablore-related:start -->\nOLD\n<!-- fablore-related:end -->\nB"
    out = inject_marked_block(base, "<p>NEW</p>")
    assert "OLD" not in out
    assert "<p>NEW</p>" in out
    assert "A" in out and "B" in out


def test_inject_marked_block_clears() -> None:
    base = "A\n\n<!-- fablore-related:start -->\nX\n<!-- fablore-related:end -->\n"
    out = inject_marked_block(base, "")
    assert "fablore-related" not in out
    assert "A" in out


def test_load_related_maps_minimal_csvs(tmp_path: Path) -> None:
    data = tmp_path / "data"
    data.mkdir()
    (data / "stories.csv").write_text(
        "StoryId|StoryKey|StoryType|Title\nST1|main-story/x.md|main-story|X\n",
        encoding="utf-8",
    )
    (data / "story-heroes.csv").write_text(
        "StoryId|CanonicalId\nST1|CN1\n", encoding="utf-8"
    )
    (data / "story-locations.csv").write_text(
        "StoryId|LocationId\nST1|LO1\n", encoding="utf-8"
    )
    (data / "heroes-canonical.csv").write_text(
        "CanonicalId|CanonicalSlug|CanonicalHero\nCN1|boltyn|Boltyn\n",
        encoding="utf-8",
    )
    (data / "locations.csv").write_text(
        "LocationId|Name|RegionId|Notes\nLO1|Beacon|RG1|\n", encoding="utf-8"
    )
    (data / "regions.csv").write_text(
        "RegionId|RegionName|WorldOfRatheStoryKey\n"
        "RG1|Metrix|world-of-rathe/metrix.md\n",
        encoding="utf-8",
    )
    m = load_related_maps(data)
    assert m.story_key_to_id["main-story/x.md"] == "ST1"
    assert m.story_heroes["ST1"] == frozenset({"CN1"})
    assert m.story_locations["ST1"] == frozenset({"LO1"})


def test_resolve_hero_slug_override_arakni(tmp_path: Path) -> None:
    src = tmp_path / "src"
    (src / "heroes-of-rathe").mkdir(parents=True)
    (src / "heroes-of-rathe" / "arakni-about.md").write_text("# A\n", encoding="utf-8")
    assert (
        resolve_hero_src_path(src, "arakni-huntsman")
        == "heroes-of-rathe/arakni-about.md"
    )


def test_build_related_fragment_hero_and_location(tmp_path: Path) -> None:
    src = tmp_path / "src"
    (src / "heroes-of-rathe").mkdir(parents=True)
    (src / "heroes-of-rathe" / "boltyn-about.md").write_text("# B\n", encoding="utf-8")
    (src / "world-of-rathe").mkdir(parents=True)
    (src / "world-of-rathe" / "metrix.md").write_text("# M\n", encoding="utf-8")

    maps = RelatedMaps(
        story_key_to_id={"main-story/x.md": "ST1"},
        story_heroes={"ST1": frozenset({"CN1"})},
        story_locations={"ST1": frozenset({"LO1"})},
        canonical_hero={"CN1": ("boltyn", "Boltyn")},
        location_row={"LO1": ("Beacon", "RG1", "")},
        region_row={"RG1": ("Metrix", "world-of-rathe/metrix.md")},
    )
    html = build_related_fragment(
        maps,
        story_id="ST1",
        chapter_src_path="main-story/x.md",
        src_root=src,
    )
    assert "Related Lore" in html
    assert '<h1 id="related-lore">Related Lore</h1>' in html
    assert "../heroes-of-rathe/boltyn-about.md" in html
    assert "../world-of-rathe/metrix.md" in html
    assert "Beacon" in html
    assert html.count('<div class="related-cards">') == 1
    assert "related-cards-spacer" in html


def test_build_related_fragment_skips_location_without_world_lore_file(
    tmp_path: Path,
) -> None:
    """Locations only appear when ``WorldOfRatheStoryKey`` resolves to a real file."""
    src = tmp_path / "src"
    (src / "heroes-of-rathe").mkdir(parents=True)
    (src / "heroes-of-rathe" / "boltyn-about.md").write_text("# B\n", encoding="utf-8")
    (src / "world-of-rathe").mkdir(parents=True)
    (src / "world-of-rathe" / "metrix.md").write_text("# M\n", encoding="utf-8")

    maps = RelatedMaps(
        story_key_to_id={"main-story/x.md": "ST1"},
        story_heroes={"ST1": frozenset({"CN1"})},
        story_locations={"ST1": frozenset({"LO1", "LO2"})},
        canonical_hero={"CN1": ("boltyn", "Boltyn")},
        location_row={
            "LO1": ("Beacon", "RG1", ""),
            "LO2": ("The Undercroft", "RG2", ""),
        },
        region_row={
            "RG1": ("Metrix", "world-of-rathe/metrix.md"),
            "RG2": ("Deathmatch Arena", "world-of-rathe/deathmatch-arena.md"),
        },
    )
    html = build_related_fragment(
        maps,
        story_id="ST1",
        chapter_src_path="main-story/x.md",
        src_root=src,
    )
    assert "Beacon" in html
    assert "Undercroft" not in html
    assert "Deathmatch" not in html


def test_build_related_fragment_location_lore_fragment_in_href(tmp_path: Path) -> None:
    src = tmp_path / "src"
    (src / "world-of-rathe").mkdir(parents=True)
    (src / "world-of-rathe" / "aria.md").write_text("# A\n", encoding="utf-8")

    maps = RelatedMaps(
        story_key_to_id={"main-story/05-tales-of-aria/x.md": "ST1"},
        story_heroes={},
        story_locations={"ST1": frozenset({"LO1"})},
        canonical_hero={},
        location_row={"LO1": ("Enion", "RG1", "enion")},
        region_row={"RG1": ("Aria", "world-of-rathe/aria.md")},
    )
    html = build_related_fragment(
        maps,
        story_id="ST1",
        chapter_src_path="main-story/05-tales-of-aria/x.md",
        src_root=src,
    )
    assert "Enion" in html
    assert "../../world-of-rathe/aria.md#enion" in html


def test_build_related_fragment_skips_location_when_chapter_is_that_world_page(
    tmp_path: Path,
) -> None:
    """No location cards to the same ``.md`` the reader is already on."""
    src = tmp_path / "src"
    (src / "world-of-rathe").mkdir(parents=True)
    (src / "world-of-rathe" / "aria.md").write_text("# A\n", encoding="utf-8")
    (src / "world-of-rathe" / "solana.md").write_text("# S\n", encoding="utf-8")

    maps = RelatedMaps(
        story_key_to_id={"world-of-rathe/aria.md": "ST1"},
        story_heroes={},
        story_locations={"ST1": frozenset({"LO1", "LO2"})},
        canonical_hero={},
        location_row={
            "LO1": ("Enion", "RG1", "enion"),
            "LO2": ("Golden Sands", "RG2", ""),
        },
        region_row={
            "RG1": ("Aria", "world-of-rathe/aria.md"),
            "RG2": ("Solana", "world-of-rathe/solana.md"),
        },
    )
    html = build_related_fragment(
        maps,
        story_id="ST1",
        chapter_src_path="world-of-rathe/aria.md",
        src_root=src,
    )
    assert "Enion" not in html
    assert "enion" not in html.lower()
    assert "Golden Sands" in html
    assert "solana.md" in html
    assert "related-cards-spacer" not in html


def test_build_related_fragment_skips_hero_when_chapter_is_that_hero_page(
    tmp_path: Path,
) -> None:
    """No hero card linking to the hero page you are already reading."""
    src = tmp_path / "src"
    (src / "heroes-of-rathe").mkdir(parents=True)
    (src / "heroes-of-rathe" / "boltyn-about.md").write_text("# B\n", encoding="utf-8")

    maps = RelatedMaps(
        story_key_to_id={"heroes-of-rathe/boltyn-about.md": "ST1"},
        story_heroes={"ST1": frozenset({"CN1"})},
        story_locations={},
        canonical_hero={"CN1": ("boltyn", "Boltyn")},
        location_row={},
        region_row={},
    )
    html = build_related_fragment(
        maps,
        story_id="ST1",
        chapter_src_path="heroes-of-rathe/boltyn-about.md",
        src_root=src,
    )
    assert html == ""


def test_build_related_fragment_wraps_type_and_title_in_body(tmp_path: Path) -> None:
    """Markup uses ``related-card-body`` for flex layout (subtitle pinned down)."""
    src = tmp_path / "src"
    (src / "heroes-of-rathe").mkdir(parents=True)
    (src / "heroes-of-rathe" / "boltyn-about.md").write_text("# B\n", encoding="utf-8")

    maps = RelatedMaps(
        story_key_to_id={"main-story/x.md": "ST1"},
        story_heroes={"ST1": frozenset({"CN1"})},
        story_locations={},
        canonical_hero={"CN1": ("boltyn", "Boltyn")},
        location_row={},
        region_row={},
    )
    html = build_related_fragment(
        maps,
        story_id="ST1",
        chapter_src_path="main-story/x.md",
        src_root=src,
    )
    assert "related-card-body" in html
    assert html.index("related-cards") < html.index("related-card-body")
