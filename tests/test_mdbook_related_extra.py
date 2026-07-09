"""Additional tests for ``mdbook_related`` targeting uncovered branches."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src/data"))

from mdbook_related import (  # noqa: E402
    RelatedMaps,
    build_character_stories_fragment,
    build_related_fragment,
    inject_marked_block,
    load_related_maps,
    process_chapter_content,
    resolve_hero_src_path,
    walk_mutate_sections,
    story_id_for_chapter,
)


def _maps(**kwargs) -> RelatedMaps:
    """Build a RelatedMaps with empty defaults for use in tests."""
    defaults: dict = dict(
        story_key_to_id={},
        story_id_to_key={},
        story_id_to_title={},
        story_id_to_type={},
        story_heroes={},
        story_npcs={},
        story_locations={},
        story_regions={},
        canonical_hero={},
        npc_row={},
        location_row={},
        region_row={},
        hero_canonical_to_stories={},
        npc_char_to_stories={},
        npc_src_to_char_ids={},
        hero_junction_fragment={},
        npc_junction_fragment={},
    )
    return RelatedMaps(**{**defaults, **kwargs})


# ---------------------------------------------------------------------------
# resolve_hero_src_path filesystem resolution
# ---------------------------------------------------------------------------


def test_resolve_hero_src_path_finds_about_file(tmp_path: Path) -> None:
    hero_dir = tmp_path / "heroes-of-rathe"
    hero_dir.mkdir()
    (hero_dir / "boltyn-about.md").write_text("# Boltyn", encoding="utf-8")
    result = resolve_hero_src_path(tmp_path, "boltyn")
    assert result == "heroes-of-rathe/boltyn-about.md"


def test_resolve_hero_src_path_finds_plain_file(tmp_path: Path) -> None:
    hero_dir = tmp_path / "heroes-of-rathe"
    hero_dir.mkdir()
    (hero_dir / "bravo.md").write_text("# Bravo", encoding="utf-8")
    result = resolve_hero_src_path(tmp_path, "bravo")
    assert result == "heroes-of-rathe/bravo.md"


def test_resolve_hero_src_path_returns_none_when_missing(tmp_path: Path) -> None:
    (tmp_path / "heroes-of-rathe").mkdir()
    result = resolve_hero_src_path(tmp_path, "nonexistent")
    assert result is None


def test_resolve_hero_src_path_override_resolves_file(tmp_path: Path) -> None:
    """A slug in HERO_SLUG_LORE_FILE_OVERRIDES resolves to the override path."""
    hero_dir = tmp_path / "heroes-of-rathe"
    hero_dir.mkdir()
    (hero_dir / "arakni-about.md").write_text("# Arakni", encoding="utf-8")
    result = resolve_hero_src_path(tmp_path, "arakni-huntsman")
    assert result == "heroes-of-rathe/arakni-about.md"


def test_resolve_hero_src_path_override_missing_falls_through(tmp_path: Path) -> None:
    """Override file missing → falls through to regular slug search."""
    hero_dir = tmp_path / "heroes-of-rathe"
    hero_dir.mkdir()
    # override file does not exist, but the plain-file form does
    (hero_dir / "arakni-huntsman-about.md").write_text("# AH", encoding="utf-8")
    result = resolve_hero_src_path(tmp_path, "arakni-huntsman")
    # Override path 'heroes-of-rathe/arakni-about.md' doesn't exist, so it falls through
    assert result == "heroes-of-rathe/arakni-huntsman-about.md"


# ---------------------------------------------------------------------------
# build_character_stories_fragment
# ---------------------------------------------------------------------------


def test_build_character_stories_fragment_returns_story_card(tmp_path: Path) -> None:
    """Hero canonical page shows a card linking to each story it appears in."""
    src = tmp_path / "src"
    story_file = src / "main-story" / "foo.md"
    story_file.parent.mkdir(parents=True)
    story_file.write_text("# Foo Story", encoding="utf-8")

    hero_page = "heroes-of-rathe/foo-about.md"
    maps = _maps(
        hero_canonical_to_stories={"CN1": frozenset(["S1"])},
        story_id_to_key={"S1": "main-story/foo.md"},
        story_id_to_title={"S1": "Foo Story"},
        npc_src_to_char_ids={},
        npc_char_to_stories={},
    )
    hero_src_map = {hero_page: frozenset(["CN1"])}
    result = build_character_stories_fragment(
        maps,
        chapter_src_path=hero_page,
        src_root=src,
        hero_src_map=hero_src_map,
    )
    assert "Related Lore" in result
    assert "Foo Story" in result
    assert "main-story/foo.md" in result


def test_build_character_stories_fragment_npc_page(tmp_path: Path) -> None:
    """NPC page shows cards for stories via npc_src_to_char_ids."""
    src = tmp_path / "src"
    story_file = src / "main-story" / "bar.md"
    story_file.parent.mkdir(parents=True)
    story_file.write_text("# Bar Story", encoding="utf-8")

    npc_page = "other-characters/npc-one.md"
    maps = _maps(
        npc_src_to_char_ids={npc_page: frozenset(["C1"])},
        npc_char_to_stories={"C1": frozenset(["S2"])},
        story_id_to_key={"S2": "main-story/bar.md"},
        story_id_to_title={"S2": "Bar Story"},
        hero_canonical_to_stories={},
    )
    result = build_character_stories_fragment(
        maps,
        chapter_src_path=npc_page,
        src_root=src,
        hero_src_map={},
    )
    assert "Related Lore" in result
    assert "Bar Story" in result


def test_build_character_stories_fragment_returns_empty_when_no_stories(
    tmp_path: Path,
) -> None:
    """No matching stories → empty string."""
    maps = _maps()
    result = build_character_stories_fragment(
        maps,
        chapter_src_path="heroes-of-rathe/nobody-about.md",
        src_root=tmp_path,
        hero_src_map={},
    )
    assert result == ""


def test_build_character_stories_fragment_omits_missing_file(
    tmp_path: Path, capsys
) -> None:
    """Story whose file does not exist on disk is omitted with a warning."""
    src = tmp_path / "src"
    src.mkdir()

    hero_page = "heroes-of-rathe/ghost-about.md"
    maps = _maps(
        hero_canonical_to_stories={"CN1": frozenset(["S1"])},
        story_id_to_key={"S1": "main-story/ghost.md"},
        story_id_to_title={"S1": "Ghost Story"},
        npc_src_to_char_ids={},
        npc_char_to_stories={},
    )
    result = build_character_stories_fragment(
        maps,
        chapter_src_path=hero_page,
        src_root=src,
        hero_src_map={hero_page: frozenset(["CN1"])},
    )
    assert result == ""
    captured = capsys.readouterr()
    assert "ghost.md" in captured.err


def test_build_character_stories_fragment_sorts_by_title(tmp_path: Path) -> None:
    """Multiple stories are sorted alphabetically."""
    src = tmp_path / "src"
    for name in ("alpha.md", "zeta.md", "mango.md"):
        p = src / "main-story" / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(f"# {name}", encoding="utf-8")

    hero_page = "heroes-of-rathe/hero-about.md"
    maps = _maps(
        hero_canonical_to_stories={"CN1": frozenset(["S1", "S2", "S3"])},
        story_id_to_key={
            "S1": "main-story/alpha.md",
            "S2": "main-story/zeta.md",
            "S3": "main-story/mango.md",
        },
        story_id_to_title={
            "S1": "Alpha Tale",
            "S2": "Zeta Tale",
            "S3": "Mango Tale",
        },
        npc_src_to_char_ids={},
        npc_char_to_stories={},
    )
    result = build_character_stories_fragment(
        maps,
        chapter_src_path=hero_page,
        src_root=src,
        hero_src_map={hero_page: frozenset(["CN1"])},
    )
    alpha_pos = result.index("Alpha Tale")
    mango_pos = result.index("Mango Tale")
    zeta_pos = result.index("Zeta Tale")
    assert alpha_pos < mango_pos < zeta_pos


# ---------------------------------------------------------------------------
# build_related_fragment — NPC cards
# ---------------------------------------------------------------------------


def test_build_related_fragment_npc_card(tmp_path: Path) -> None:
    """NPC with a valid story_key produces a Character card."""
    src = tmp_path / "src"
    (src / "other-characters").mkdir(parents=True)
    (src / "other-characters" / "npc-page.md").write_text("# NPC", encoding="utf-8")

    maps = _maps(
        story_key_to_id={"main-story/x.md": "ST1"},
        story_npcs={"ST1": frozenset({"C1"})},
        npc_row={"C1": ("Nefarius", "other-characters/npc-page.md")},
    )
    html = build_related_fragment(
        maps,
        story_id="ST1",
        chapter_src_path="main-story/x.md",
        src_root=src,
    )
    assert "Nefarius" in html
    assert "Character" in html
    assert "other-characters/npc-page.md" in html


def test_build_related_fragment_npc_skips_empty_story_key(tmp_path: Path) -> None:
    """NPC row with no OtherCharactersStoryKey is omitted."""
    src = tmp_path / "src"
    src.mkdir()

    maps = _maps(
        story_key_to_id={"main-story/x.md": "ST1"},
        story_npcs={"ST1": frozenset({"C1"})},
        npc_row={"C1": ("NoLink NPC", "")},
    )
    html = build_related_fragment(
        maps,
        story_id="ST1",
        chapter_src_path="main-story/x.md",
        src_root=src,
    )
    assert html == ""


def test_build_related_fragment_npc_skips_missing_file(tmp_path: Path) -> None:
    """NPC whose story key file doesn't exist on disk is omitted."""
    src = tmp_path / "src"
    src.mkdir()

    maps = _maps(
        story_key_to_id={"main-story/x.md": "ST1"},
        story_npcs={"ST1": frozenset({"C1"})},
        npc_row={"C1": ("Phantom NPC", "other-characters/missing.md")},
    )
    html = build_related_fragment(
        maps,
        story_id="ST1",
        chapter_src_path="main-story/x.md",
        src_root=src,
    )
    assert html == ""


def test_build_related_fragment_npc_skips_self(tmp_path: Path) -> None:
    """NPC card whose story key equals chapter_src_path is omitted."""
    src = tmp_path / "src"
    (src / "other-characters").mkdir(parents=True)
    (src / "other-characters" / "npc-page.md").write_text("# NPC", encoding="utf-8")

    maps = _maps(
        story_key_to_id={"other-characters/npc-page.md": "ST1"},
        story_npcs={"ST1": frozenset({"C1"})},
        npc_row={"C1": ("Self NPC", "other-characters/npc-page.md")},
    )
    html = build_related_fragment(
        maps,
        story_id="ST1",
        chapter_src_path="other-characters/npc-page.md",
        src_root=src,
    )
    assert html == ""


# ---------------------------------------------------------------------------
# build_related_fragment — hero card warning branch
# ---------------------------------------------------------------------------


def test_build_related_fragment_hero_no_lore_file_omits_and_warns(
    tmp_path: Path, capsys
) -> None:
    """Hero with no resolvable lore file is omitted and a warning printed to stderr."""
    src = tmp_path / "src"
    (src / "heroes-of-rathe").mkdir(parents=True)
    # no file created for 'phantom' slug

    maps = _maps(
        story_key_to_id={"main-story/x.md": "ST1"},
        story_heroes={"ST1": frozenset({"CN1"})},
        canonical_hero={"CN1": ("phantom", "Phantom Hero")},
    )
    html = build_related_fragment(
        maps,
        story_id="ST1",
        chapter_src_path="main-story/x.md",
        src_root=src,
    )
    assert html == ""
    captured = capsys.readouterr()
    assert "phantom" in captured.err


# ---------------------------------------------------------------------------
# build_related_fragment — location without lfrag
# ---------------------------------------------------------------------------


def test_build_related_fragment_location_skips_empty_lfrag(tmp_path: Path) -> None:
    """Location with empty LoreFragment is omitted."""
    src = tmp_path / "src"
    (src / "world-of-rathe").mkdir(parents=True)
    (src / "world-of-rathe" / "metrix.md").write_text("# M", encoding="utf-8")

    maps = _maps(
        story_key_to_id={"main-story/x.md": "ST1"},
        story_locations={"ST1": frozenset({"LO1"})},
        location_row={"LO1": ("Beacon", "RG1", "")},  # empty lfrag
        region_row={"RG1": ("Metrix", "world-of-rathe/metrix.md")},
    )
    html = build_related_fragment(
        maps,
        story_id="ST1",
        chapter_src_path="main-story/x.md",
        src_root=src,
    )
    assert html == ""


def test_build_related_fragment_location_skips_no_region(tmp_path: Path) -> None:
    """Location whose region has no WorldOfRatheStoryKey is omitted."""
    src = tmp_path / "src"
    src.mkdir()

    maps = _maps(
        story_key_to_id={"main-story/x.md": "ST1"},
        story_locations={"ST1": frozenset({"LO1"})},
        location_row={"LO1": ("Beacon", "RG1", "beacon")},
        region_row={"RG1": ("Nowhere", "")},  # empty world_key
    )
    html = build_related_fragment(
        maps,
        story_id="ST1",
        chapter_src_path="main-story/x.md",
        src_root=src,
    )
    assert html == ""


def test_build_related_fragment_location_skips_unknown_region(tmp_path: Path) -> None:
    """Location pointing to an unrecognised RegionId is omitted."""
    src = tmp_path / "src"
    src.mkdir()

    maps = _maps(
        story_key_to_id={"main-story/x.md": "ST1"},
        story_locations={"ST1": frozenset({"LO1"})},
        location_row={"LO1": ("Somewhere", "RG_UNKNOWN", "frag")},
        region_row={},  # region not present
    )
    html = build_related_fragment(
        maps,
        story_id="ST1",
        chapter_src_path="main-story/x.md",
        src_root=src,
    )
    assert html == ""


# ---------------------------------------------------------------------------
# build_related_fragment — region without world_key
# ---------------------------------------------------------------------------


def test_build_related_fragment_region_skips_empty_world_key(tmp_path: Path) -> None:
    """Region with empty WorldOfRatheStoryKey is omitted."""
    src = tmp_path / "src"
    src.mkdir()

    maps = _maps(
        story_key_to_id={"main-story/x.md": "ST1"},
        story_regions={"ST1": frozenset({"RG1"})},
        region_row={"RG1": ("Nowhere", "")},
    )
    html = build_related_fragment(
        maps,
        story_id="ST1",
        chapter_src_path="main-story/x.md",
        src_root=src,
    )
    assert html == ""


# ---------------------------------------------------------------------------
# build_related_fragment — spacer between card groups
# ---------------------------------------------------------------------------


def test_build_related_fragment_spacer_between_groups(tmp_path: Path) -> None:
    """Two card groups (hero + location) must produce exactly one spacer between them."""
    src = tmp_path / "src"
    (src / "heroes-of-rathe").mkdir(parents=True)
    (src / "heroes-of-rathe" / "boltyn-about.md").write_text("# B", encoding="utf-8")
    (src / "world-of-rathe").mkdir(parents=True)
    (src / "world-of-rathe" / "metrix.md").write_text("# M", encoding="utf-8")

    maps = _maps(
        story_key_to_id={"main-story/x.md": "ST1"},
        story_heroes={"ST1": frozenset({"CN1"})},
        story_locations={"ST1": frozenset({"LO1"})},
        canonical_hero={"CN1": ("boltyn", "Boltyn")},
        location_row={"LO1": ("Beacon", "RG1", "beacon")},
        region_row={"RG1": ("Metrix", "world-of-rathe/metrix.md")},
    )
    html = build_related_fragment(
        maps,
        story_id="ST1",
        chapter_src_path="main-story/x.md",
        src_root=src,
    )
    assert html.count("related-cards-spacer") == 1


def test_build_related_fragment_no_spacer_single_group(tmp_path: Path) -> None:
    """A single card group does not produce a spacer."""
    src = tmp_path / "src"
    (src / "world-of-rathe").mkdir(parents=True)
    (src / "world-of-rathe" / "metrix.md").write_text("# M", encoding="utf-8")

    maps = _maps(
        story_key_to_id={"main-story/x.md": "ST1"},
        story_regions={"ST1": frozenset({"RG1"})},
        region_row={"RG1": ("Metrix", "world-of-rathe/metrix.md")},
    )
    html = build_related_fragment(
        maps,
        story_id="ST1",
        chapter_src_path="main-story/x.md",
        src_root=src,
    )
    assert "related-cards-spacer" not in html


# ---------------------------------------------------------------------------
# build_related_fragment — hero_src_map reverse-story logic
# ---------------------------------------------------------------------------


def test_build_related_fragment_hero_src_map_adds_story_cards(tmp_path: Path) -> None:
    """When hero_src_map is provided, other stories featuring this hero are added."""
    src = tmp_path / "src"
    (src / "main-story").mkdir(parents=True)
    (src / "main-story" / "other.md").write_text("# Other", encoding="utf-8")

    maps = _maps(
        story_key_to_id={
            "main-story/current.md": "ST1",
            "main-story/other.md": "ST2",
        },
        story_id_to_key={"ST1": "main-story/current.md", "ST2": "main-story/other.md"},
        story_id_to_title={"ST2": "Other Story"},
        story_id_to_type={"ST2": "main-story"},
        hero_canonical_to_stories={"CN1": frozenset(["ST1", "ST2"])},
        npc_src_to_char_ids={},
        npc_char_to_stories={},
    )
    # chapter is main-story/current.md (a hero's story page)
    # hero_src_map says this story is for CN1, so reverse lookup finds ST2
    html = build_related_fragment(
        maps,
        story_id="ST1",
        chapter_src_path="main-story/current.md",
        src_root=src,
        hero_src_map={"main-story/current.md": frozenset(["CN1"])},
    )
    assert "Other Story" in html
    assert "Main Story" in html


def test_build_related_fragment_hero_src_map_skips_skip_types(tmp_path: Path) -> None:
    """Stories with types in _STORY_TYPES_SKIP are excluded from reverse story cards."""
    src = tmp_path / "src"
    (src / "heroes-of-rathe").mkdir(parents=True)
    (src / "heroes-of-rathe" / "hero.md").write_text("# H", encoding="utf-8")

    maps = _maps(
        story_key_to_id={
            "main-story/current.md": "ST1",
            "heroes-of-rathe/hero.md": "ST2",
        },
        story_id_to_key={
            "ST1": "main-story/current.md",
            "ST2": "heroes-of-rathe/hero.md",
        },
        story_id_to_title={"ST2": "Hero Bio"},
        story_id_to_type={"ST2": "heroes-of-rathe"},  # in _STORY_TYPES_SKIP
        hero_canonical_to_stories={"CN1": frozenset(["ST1", "ST2"])},
        npc_src_to_char_ids={},
        npc_char_to_stories={},
    )
    html = build_related_fragment(
        maps,
        story_id="ST1",
        chapter_src_path="main-story/current.md",
        src_root=src,
        hero_src_map={"main-story/current.md": frozenset(["CN1"])},
    )
    assert "Hero Bio" not in html


def test_build_related_fragment_hero_src_map_npc_path(tmp_path: Path) -> None:
    """NPC character IDs from npc_src_to_char_ids drive reverse story lookup."""
    src = tmp_path / "src"
    (src / "main-story").mkdir(parents=True)
    (src / "main-story" / "other.md").write_text("# Other NPC Story", encoding="utf-8")

    npc_page = "other-characters/npc-page.md"
    maps = _maps(
        story_key_to_id={
            "main-story/current.md": "ST1",
            "main-story/other.md": "ST2",
        },
        story_id_to_key={"ST1": "main-story/current.md", "ST2": "main-story/other.md"},
        story_id_to_title={"ST2": "NPC Adventure"},
        story_id_to_type={"ST2": "main-story"},
        npc_src_to_char_ids={npc_page: frozenset(["C1"])},
        npc_char_to_stories={"C1": frozenset(["ST1", "ST2"])},
        hero_canonical_to_stories={},
    )
    html = build_related_fragment(
        maps,
        story_id="ST1",
        chapter_src_path=npc_page,
        src_root=src,
        hero_src_map={},
    )
    assert "NPC Adventure" in html


def test_build_related_fragment_hero_src_map_with_fragment(tmp_path: Path) -> None:
    """hero_junction_fragment appended to story card href when present."""
    src = tmp_path / "src"
    (src / "main-story").mkdir(parents=True)
    (src / "main-story" / "other.md").write_text("# Other", encoding="utf-8")

    maps = _maps(
        story_key_to_id={
            "main-story/current.md": "ST1",
            "main-story/other.md": "ST2",
        },
        story_id_to_key={"ST1": "main-story/current.md", "ST2": "main-story/other.md"},
        story_id_to_title={"ST2": "Other Story"},
        story_id_to_type={"ST2": "main-story"},
        hero_canonical_to_stories={"CN1": frozenset(["ST1", "ST2"])},
        hero_junction_fragment={("ST2", "CN1"): "my-section"},
        npc_src_to_char_ids={},
        npc_char_to_stories={},
    )
    html = build_related_fragment(
        maps,
        story_id="ST1",
        chapter_src_path="main-story/current.md",
        src_root=src,
        hero_src_map={"main-story/current.md": frozenset(["CN1"])},
    )
    assert "#my-section" in html


# ---------------------------------------------------------------------------
# inject_marked_block edge cases
# ---------------------------------------------------------------------------


def test_inject_marked_block_empty_content_with_inner_html() -> None:
    """Empty content + non-empty inner_html → markers appended."""
    out = inject_marked_block("", "<p>x</p>")
    assert "fablore-related:start" in out
    assert "<p>x</p>" in out


def test_inject_marked_block_non_empty_content_empty_inner_html() -> None:
    """Non-empty content with no existing markers and empty inner_html → unchanged."""
    out = inject_marked_block("Some text", "")
    assert "fablore-related" not in out
    assert "Some text" in out


def test_inject_marked_block_whitespace_only_inner_html() -> None:
    """Whitespace-only inner_html is treated as empty (no block inserted)."""
    out = inject_marked_block("Body text", "   \n  ")
    assert "fablore-related" not in out


def test_inject_marked_block_existing_markers_empty_inner_html_strips() -> None:
    """Existing markers + empty inner_html → markers fully removed."""
    base = "A\n\n<!-- fablore-related:start -->\nOLD\n<!-- fablore-related:end -->\n"
    out = inject_marked_block(base, "")
    assert "fablore-related" not in out
    assert "A" in out


# ---------------------------------------------------------------------------
# process_chapter_content
# ---------------------------------------------------------------------------


def test_process_chapter_content_story_page(tmp_path: Path) -> None:
    """chapter_src_path IS a story key → build_related_fragment path taken."""
    # No heroes/locations, so fragment will be empty, but function must return str.
    maps = _maps(story_key_to_id={"main-story/foo.md": "S1"})
    result = process_chapter_content(
        "# Foo\n",
        maps,
        chapter_src_path="main-story/foo.md",
        src_root=tmp_path,
        hero_src_map={},
    )
    assert isinstance(result, str)
    # Empty related block → content unchanged (no markers appended)
    assert "# Foo" in result


def test_process_chapter_content_hero_page(tmp_path: Path) -> None:
    """chapter_src_path NOT a story key → build_character_stories_fragment path taken."""
    maps = _maps()  # no story_key_to_id entries
    result = process_chapter_content(
        "# Hero\n",
        maps,
        chapter_src_path="heroes-of-rathe/nobody-about.md",
        src_root=tmp_path,
        hero_src_map={},
    )
    assert isinstance(result, str)
    assert "# Hero" in result


def test_process_chapter_content_story_page_injects_related(tmp_path: Path) -> None:
    """Story page with hero data produces an injected related block."""
    src = tmp_path / "src"
    (src / "heroes-of-rathe").mkdir(parents=True)
    (src / "heroes-of-rathe" / "boltyn-about.md").write_text("# B", encoding="utf-8")

    maps = _maps(
        story_key_to_id={"main-story/x.md": "ST1"},
        story_heroes={"ST1": frozenset({"CN1"})},
        canonical_hero={"CN1": ("boltyn", "Boltyn")},
    )
    result = process_chapter_content(
        "# Story\n",
        maps,
        chapter_src_path="main-story/x.md",
        src_root=src,
        hero_src_map={},
    )
    assert "fablore-related:start" in result
    assert "Boltyn" in result


def test_process_chapter_content_hero_page_with_stories(tmp_path: Path) -> None:
    """Hero page with related stories produces injected block."""
    src = tmp_path / "src"
    (src / "main-story").mkdir(parents=True)
    (src / "main-story" / "foo.md").write_text("# Foo Story", encoding="utf-8")

    hero_page = "heroes-of-rathe/foo-about.md"
    maps = _maps(
        hero_canonical_to_stories={"CN1": frozenset(["S1"])},
        story_id_to_key={"S1": "main-story/foo.md"},
        story_id_to_title={"S1": "Foo Story"},
        npc_src_to_char_ids={},
        npc_char_to_stories={},
    )
    result = process_chapter_content(
        "# Hero\n",
        maps,
        chapter_src_path=hero_page,
        src_root=src,
        hero_src_map={hero_page: frozenset(["CN1"])},
    )
    assert "fablore-related:start" in result
    assert "Foo Story" in result


# ---------------------------------------------------------------------------
# walk_mutate_sections
# ---------------------------------------------------------------------------


def test_walk_mutate_sections_updates_chapter(tmp_path: Path) -> None:
    """walk_mutate_sections modifies chapter content in place."""
    src = tmp_path / "src"
    (src / "heroes-of-rathe").mkdir(parents=True)
    (src / "heroes-of-rathe" / "boltyn-about.md").write_text("# B", encoding="utf-8")

    maps = _maps(
        story_key_to_id={"main-story/x.md": "ST1"},
        story_heroes={"ST1": frozenset({"CN1"})},
        canonical_hero={"CN1": ("boltyn", "Boltyn")},
    )
    sections = [
        {
            "Chapter": {
                "path": "main-story/x.md",
                "content": "# Story\n",
                "sub_items": [],
            }
        }
    ]
    walk_mutate_sections(sections, maps, src, {})
    assert "Boltyn" in sections[0]["Chapter"]["content"]


def test_walk_mutate_sections_skips_separator(tmp_path: Path) -> None:
    """Separator items are silently skipped (no error)."""
    maps = _maps()
    sections = [{"Separator": None}]
    walk_mutate_sections(sections, maps, tmp_path, {})  # should not raise


def test_walk_mutate_sections_skips_part_title(tmp_path: Path) -> None:
    """PartTitle items are silently skipped (no error)."""
    maps = _maps()
    sections = [{"PartTitle": "Some Part"}]
    walk_mutate_sections(sections, maps, tmp_path, {})  # should not raise


def test_walk_mutate_sections_skips_non_dict(tmp_path: Path) -> None:
    """Non-dict items in sections are silently ignored."""
    maps = _maps()
    sections = ["not a dict", 42, None]  # type: ignore[list-item]
    walk_mutate_sections(sections, maps, tmp_path, {})  # should not raise


def test_walk_mutate_sections_skips_chapter_without_path(tmp_path: Path) -> None:
    """Chapter with None path is not processed."""
    maps = _maps()
    sections = [{"Chapter": {"path": None, "content": "# Hello\n", "sub_items": []}}]
    walk_mutate_sections(sections, maps, tmp_path, {})
    assert sections[0]["Chapter"]["content"] == "# Hello\n"


def test_walk_mutate_sections_recurses_sub_items(tmp_path: Path) -> None:
    """walk_mutate_sections recurses into sub_items."""
    src = tmp_path / "src"
    (src / "heroes-of-rathe").mkdir(parents=True)
    (src / "heroes-of-rathe" / "boltyn-about.md").write_text("# B", encoding="utf-8")

    maps = _maps(
        story_key_to_id={"main-story/sub/x.md": "ST1"},
        story_heroes={"ST1": frozenset({"CN1"})},
        canonical_hero={"CN1": ("boltyn", "Boltyn")},
    )
    sub_chapter = {
        "Chapter": {
            "path": "main-story/sub/x.md",
            "content": "# Sub\n",
            "sub_items": [],
        }
    }
    sections = [
        {"Chapter": {"path": None, "content": "# Parent\n", "sub_items": [sub_chapter]}}
    ]
    walk_mutate_sections(sections, maps, src, {})
    assert "Boltyn" in sub_chapter["Chapter"]["content"]


# ---------------------------------------------------------------------------
# load_related_maps — NPC junction loading
# ---------------------------------------------------------------------------


def test_load_related_maps_loads_story_npcs(tmp_path: Path) -> None:
    """load_related_maps populates story_npcs from story-npcs.csv."""
    data = tmp_path / "data"
    csv = data / "csv"
    csv.mkdir(parents=True)
    (csv / "stories.csv").write_text(
        "StoryId|StoryKey|StoryType|Title\nST1|main-story/x.md|main-story|X\n",
        encoding="utf-8",
    )
    (csv / "story-heroes.csv").write_text("StoryId|CanonicalId\n", encoding="utf-8")
    (csv / "story-locations.csv").write_text("StoryId|LocationId\n", encoding="utf-8")
    (csv / "story-npcs.csv").write_text(
        "StoryId|CharacterId|Fragment\nST1|C1|\n", encoding="utf-8"
    )
    (csv / "heroes-canonical.csv").write_text(
        "CanonicalId|CanonicalSlug|CanonicalHero\n", encoding="utf-8"
    )
    (csv / "locations.csv").write_text("LocationId|Name|RegionId\n", encoding="utf-8")
    (csv / "regions.csv").write_text(
        "RegionId|RegionName|WorldOfRatheStoryKey\n", encoding="utf-8"
    )
    m = load_related_maps(data)
    assert m.story_npcs["ST1"] == frozenset({"C1"})
    assert "C1" in m.npc_char_to_stories
    assert "ST1" in m.npc_char_to_stories["C1"]


def test_load_related_maps_loads_npc_junction_fragment(tmp_path: Path) -> None:
    """load_related_maps populates npc_junction_fragment for non-empty Fragment."""
    data = tmp_path / "data"
    csv = data / "csv"
    csv.mkdir(parents=True)
    (csv / "stories.csv").write_text(
        "StoryId|StoryKey|StoryType|Title\nST1|main-story/x.md|main-story|X\n",
        encoding="utf-8",
    )
    (csv / "story-heroes.csv").write_text("StoryId|CanonicalId\n", encoding="utf-8")
    (csv / "story-locations.csv").write_text("StoryId|LocationId\n", encoding="utf-8")
    (csv / "story-npcs.csv").write_text(
        "StoryId|CharacterId|Fragment\nST1|C1|my-fragment\n", encoding="utf-8"
    )
    (csv / "heroes-canonical.csv").write_text(
        "CanonicalId|CanonicalSlug|CanonicalHero\n", encoding="utf-8"
    )
    (csv / "locations.csv").write_text("LocationId|Name|RegionId\n", encoding="utf-8")
    (csv / "regions.csv").write_text(
        "RegionId|RegionName|WorldOfRatheStoryKey\n", encoding="utf-8"
    )
    m = load_related_maps(data)
    assert m.npc_junction_fragment[("ST1", "C1")] == "my-fragment"


def test_load_related_maps_loads_npc_src_map(tmp_path: Path) -> None:
    """load_related_maps builds npc_src_to_char_ids from npcs.csv OtherCharactersStoryKey."""
    data = tmp_path / "data"
    csv = data / "csv"
    csv.mkdir(parents=True)
    (csv / "stories.csv").write_text(
        "StoryId|StoryKey|StoryType|Title\n", encoding="utf-8"
    )
    (csv / "story-heroes.csv").write_text("StoryId|CanonicalId\n", encoding="utf-8")
    (csv / "story-locations.csv").write_text("StoryId|LocationId\n", encoding="utf-8")
    (csv / "heroes-canonical.csv").write_text(
        "CanonicalId|CanonicalSlug|CanonicalHero\n", encoding="utf-8"
    )
    (csv / "locations.csv").write_text("LocationId|Name|RegionId\n", encoding="utf-8")
    (csv / "regions.csv").write_text(
        "RegionId|RegionName|WorldOfRatheStoryKey\n", encoding="utf-8"
    )
    (csv / "npcs.csv").write_text(
        "CharacterId|Name|OtherCharactersStoryKey\nC1|The Villain|other-characters/villain.md\n",
        encoding="utf-8",
    )
    m = load_related_maps(data)
    assert "other-characters/villain.md" in m.npc_src_to_char_ids
    assert "C1" in m.npc_src_to_char_ids["other-characters/villain.md"]
    assert m.npc_row["C1"] == ("The Villain", "other-characters/villain.md")
