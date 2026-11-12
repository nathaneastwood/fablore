"""Tests for the hero page preprocessor :mod:`mdbook_hero_meta`.

Two seams: ``render_hero_page`` (a hero about-page chapter in → out: stat
blocks, form rail, video rewrite) and ``render_hero_hub`` (the hub chapter in
→ out). Both read a data directory loaded by ``load_hero_data``; the tests
build a small one in ``tmp_path`` so every expected value is a literal here.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from mdbook_hero_meta import load_hero_data, render_hero_hub, render_hero_page

CARDS = "https://d2hl7maqck52px.cloudfront.net/hero-cards"

_CSVS = {
    "heroes-game.csv": """\
HeroGameId|CardName|CanonicalId|ClassIds|TalentIds|Health|Intellect|AbilityText|YoungHero
HG_BS|Bravo, Showstopper|CN_B|CL_G||40|4|**Action** - {r}{r}: Your attacks get **dominate**.|false
HG_BY|Bravo|CN_B|CL_G||20|4|**Action** - {r}{r}:  Your attacks get **dominate**. |true
HG_BSS|Bravo, Star of the Show|CN_B|CL_G|TL_E|40|4|**Essence of Earth, Ice, and Lightning**|false
HG_K|Killjoy, the Crooked Blade|CN_K|CL_W, CL_T|TL_R|20|4|Whenever you steal, **the crowd boos** you.|true
HG_AY|Arakni, Solitary Confinement|CN_A|CL_A||19|4|The first attack with **stealth** gets go again.|true
HG_A|Arakni, 5L!p3d 7hRu 7h3 cR4X|CN_A|CL_A|TL_C|38|4|Your first attack with **stealth** gets go again.|false
HG_FY|Florian|CN_F|||20|4|If there are 4 or more Earth cards in your banished zone, Florian grows.|true
HG_F|Florian, Rotwood Harbinger|CN_F|||40|4|If there are 8 or more Earth cards in your banished zone, Florian grows.|false
""",
    "heroes-printings.csv": """\
HeroGameId|SetId|CardId|Rarity|PrintingUniqueId|Foiling|ArtVariation|Artist
HG_BS|XXX|XXX001|P|promo1|S||Alexander Mokhov
HG_BS|WTR|WTR038|T|zz-unl|S||Alexander Mokhov
HG_BS|WTR|WTR038|T|aa-rf|R||Alexander Mokhov
HG_BS|WTR|WTR038|T|ab-ea|S|EA|Alexander Mokhov
HG_BS|WTR|WTR038|T|mm-std|S||Alexander Mokhov
HG_BS|CRU|CRU022|C|cru1|S||Alexander Mokhov
HG_BY|WTR|WTR039|T|byoung|S||Adolfo Navarro
HG_BSS|EVR|EVR017|M|bss1|R||Alexander Mokhov
HG_K|SPW|SPW001|R|kj1|R||Henrique Lindner
HG_AY|HNT|HNT001|M|ay1|S||Artist A
HG_A|AAK|AAK001|M|a1|S||Artist B
""",
    "sets.csv": """\
SetId|SetTypeId|SetName|InitialReleaseDate
WTR|TY87478277a5|Welcome to Rathe|2019-10-11T00:00:00.000Z
CRU|TY858a95be59|Crucible of War|2020-08-28T00:00:00.000Z
XXX|TY1ac8c9771b|Promos|2019-01-01T00:00:00.000Z
EVR|TY858a95be59|Everfest|2022-02-04T00:00:00.000Z
SPW|TY858a95be59|Super Slam|
HNT|TY87478277a5|The Hunted|2025-01-31T00:00:00.000Z
AAK|TYfcaaf6a22f|Armory Deck: Arakni|2025-03-14T00:00:00.000Z
""",
    "set-types.csv": """\
SetTypeId|SetType|SetTypeLayer
TY87478277a5|Core Booster Set|Booster Sets
TY858a95be59|Expansion Booster Set|Booster Sets
TY1ac8c9771b|Promo|Promos
TYfcaaf6a22f|Armory Deck|Deck Releases
""",
    "classes.csv": """\
ClassId|ClassName
CL_G|Guardian
CL_W|Warrior
CL_T|Thief
CL_A|Assassin
""",
    "talents.csv": """\
TalentId|TalentName
TL_E|Elemental
TL_R|Reviled
TL_C|Chaos
""",
    "heroes-ll.csv": """\
CanonicalSlug|CardName|Format|DateInEffect
bravo|Bravo, Star of the Show|CC|2022-06-24
bravo|Bravo|CC|2023-01-01
arakni|Arakni, 5L!p3d 7hRu 7h3 cR4X|CC|
""",
    "heroes-canonical.csv": """\
CanonicalId|CanonicalSlug|CanonicalHero
CN_B|bravo|Bravo
CN_K|killjoy|Killjoy
CN_A|arakni-5l|Arakni
CN_F|florian|Florian
""",
    "heroes-fabtcg.csv": """\
# AUTO-GENERATED FILE — do not edit by hand.
CardName|HeroPageLink|Difficulty|PortraitKey|Playstyles
Arakni, 5L!p3d 7hRu 7h3 cR4X|https://fabtcg.com/hero/arakni-5l/|1|arakni-5l-p3d-7hru-7h3-cr4x|Aggressive, Disruptive
Bravo, Showstopper|https://fabtcg.com/hero/bravo/|2.5|bravo-showstopper|Board Presence, Defensive
Bravo, Star of the Show|https://fabtcg.com/hero/bravo-star/|4|bravo-star-of-the-show|Combo
Florian, Rotwood Harbinger|https://fabtcg.com/hero/florian/|3|florian-rotwood-harbinger|Board Presence
""",
}

_VIDEO = (
    '<video width="100%" height="100%" controls autoplay muted loop playsinline>\n'
    '  <source src="https://example.test/bravo.mp4" type="video/mp4">\n'
    "</video>\n"
)


@pytest.fixture(scope="module")
def data(tmp_path_factory):
    root: Path = tmp_path_factory.mktemp("data")
    (root / "csv").mkdir()
    for name, text in _CSVS.items():
        (root / "csv" / name).write_text(text, encoding="utf-8")
    return load_hero_data(root)


def _block(out: str, start: int = 0) -> str:
    """The first stat block at or after ``start``."""
    i = out.index('<section class="hero-statblock"', start)
    return out[i : out.index("</section>", i) + len("</section>")]


# ---------------------------------------------------------------------------
# Seam 1 — stat block
# ---------------------------------------------------------------------------


_TRAIT = ":::hero-trait Domination\n![Domination](https://example.test/domination.webp)\nTrait text.\n:::\n"


def test_stat_block_ends_the_form_after_the_lore_and_the_traits(data):
    page = "# Bravo, Showstopper\n\n" + _VIDEO + "\nLore paragraph.\n\n" + _TRAIT
    out = render_hero_page(page, data)
    assert out.index("Lore paragraph.") < out.index("Trait text.\n:::") < out.index('<section class="hero-statblock"')
    assert '<p class="hero-statblock-name">Bravo, Showstopper</p>' in _block(out)


def test_stat_block_ends_each_form_before_the_next_one(data):
    page = "# Bravo, Showstopper\n\nOld lore.\n\n---\n\n# Bravo, Star of the Show\n\nNew lore.\n"
    out = render_hero_page(page, data)
    first = out.index('aria-label="Hero card: Bravo, Showstopper"')
    second = out.index('aria-label="Hero card: Bravo, Star of the Show"')
    assert out.index("Old lore.") < first < out.index("New lore.") < second


def test_life_and_intellect_rows_carry_their_icons(data):
    out = render_hero_page("# Bravo, Showstopper\n\nLore.\n", data)
    block = _block(out)
    assert (
        '<div class="hero-detail"><dt>Life</dt><dd>'
        '<img src="https://d2hl7maqck52px.cloudfront.net/card-icons/icon_hp.webp" alt="" '
        'class="hero-detail-icon" width="16" height="16"> 40</dd></div>'
        '<div class="hero-detail"><dt>Intellect</dt><dd>'
        '<img src="https://d2hl7maqck52px.cloudfront.net/card-icons/icon_int.webp" alt="" '
        'class="hero-detail-icon" width="16" height="16"> 4</dd></div>'
    ) in block


def test_type_row_marks_a_young_hero(data):
    out = render_hero_page("# Killjoy, the Crooked Blade\n\nLore.\n", data)
    assert '<div class="hero-detail"><dt>Type</dt><dd>Hero — Young</dd></div>' in _block(out)


def test_type_row_of_an_adult_hero_is_plain_hero(data):
    out = render_hero_page("# Bravo, Showstopper\n\nLore.\n", data)
    assert '<div class="hero-detail"><dt>Type</dt><dd>Hero</dd></div>' in _block(out)


def test_ability_text_sits_in_a_card_text_panel_with_glyphs_and_bold_keywords(data):
    out = render_hero_page("# Bravo, Showstopper\n\nLore.\n", data)
    cost = (
        '<img src="https://d2hl7maqck52px.cloudfront.net/card-icons/icon_cost.webp" alt="Resource" class="card-glyph">'
    )
    assert (
        '<div class="hero-panel hero-panel--text"><p class="hero-panel-title">Card text</p>'
        '<div class="hero-statblock-text no-zoom">'
        f"<p><b>Action</b> - {cost}{cost}: Your attacks get "
        "<b>dominate</b>.</p></div></div>"
    ) in _block(out)


def test_header_row_holds_the_name_and_a_card_or_printings_control(data):
    out = render_hero_page("# Killjoy, the Crooked Blade\n\nLore.\n", data)
    assert (
        '<section class="hero-statblock" aria-label="Hero card: Killjoy, the Crooked Blade">\n'
        '<div class="hero-statblock-head"><p class="hero-statblock-name">Killjoy, the Crooked Blade</p>'
        '<div class="hero-statblock-controls">'
        '<div class="hero-seg hero-view-switch" role="group" aria-label="Show">'
        '<button type="button" class="hero-seg-btn" data-view="card" aria-pressed="true">Card</button>'
        '<button type="button" class="hero-seg-btn" data-view="printings" aria-pressed="false">Printings</button>'
        "</div></div></div>\n"
        '<div class="hero-statblock-variant" data-variant="only" data-name="Killjoy, the Crooked Blade">'
    ) in out


def test_one_header_sits_above_the_card_then_card_text_details_and_printings_last(data):
    block = _block(render_hero_page("# Bravo, Showstopper\n\nLore.\n", data))
    assert block.count('<div class="hero-statblock-head">') == 1
    marks = [
        '<div class="hero-statblock-head">',
        '<figure class="hero-statblock-card">',
        '<div class="hero-statblock-main">',
        '<div class="hero-panel hero-panel--text">',
        '<div class="hero-panel hero-panel--details">',
        '<div class="hero-panel hero-panel--printings">',
    ]
    positions = [block.index(m) for m in marks]
    assert positions == sorted(positions)


def test_details_rows_replace_the_old_pills_type_line_chips_and_footer(data):
    block = _block(render_hero_page("# Killjoy, the Crooked Blade\n\nLore.\n", data))
    for gone in (
        "hero-stat ",
        "hero-statblock-stats",
        "hero-statblock-type",
        "hero-statblock-chips",
        "hero-statblock-footer",
    ):
        assert gone not in block


def test_thumbnail_is_the_standard_printing_from_the_first_non_promo_set(data):
    out = render_hero_page("# Bravo, Showstopper\n\nLore.\n", data)
    assert (
        '<figure class="hero-statblock-card">'
        f'<img src="{CARDS}/mm-std.webp" alt="Bravo, Showstopper card (WTR038)" '
        'class="hero-statblock-thumb" width="546" height="763">'
    ) in _block(out)


def test_card_caption_names_the_card_id_and_finish_then_the_artist(data):
    out = render_hero_page("# Bravo, Showstopper\n\nLore.\n", data)
    assert (
        '<figcaption class="hero-statblock-caption">'
        '<span class="hero-statblock-print"><code>WTR038</code> · Standard</span>'
        '<span class="hero-statblock-artist">Alexander Mokhov</span></figcaption></figure>'
    ) in _block(out)


def test_thumbnail_falls_back_to_a_foil_when_no_standard_printing_exists(data):
    out = render_hero_page("# Bravo, Star of the Show\n\nLore.\n", data)
    assert f'<img src="{CARDS}/bss1.webp" alt="Bravo, Star of the Show card (EVR017)"' in _block(out)


def test_first_released_row_names_the_set_and_date_across_the_full_width(data):
    out = render_hero_page("# Bravo, Showstopper\n\nLore.\n", data)
    assert (
        '<div class="hero-detail hero-detail--wide"><dt>First released</dt><dd>Welcome to Rathe (11 October 2019)</dd></div>'
    ) in _block(out)


def test_sets_rarities_and_artists_rows_list_distinct_values_in_release_order(data):
    out = render_hero_page("# Bravo, Showstopper\n\nLore.\n", data)
    block = _block(out)
    assert (
        '<div class="hero-detail hero-detail--wide"><dt>Sets</dt><dd>'
        '<span class="hero-chip">Promos</span><span class="hero-chip">Welcome to Rathe</span>'
        '<span class="hero-chip">Crucible of War</span></dd></div>'
        '<div class="hero-detail hero-detail--wide"><dt>Rarities</dt><dd>Promo, Token, Common</dd></div>'
        '<div class="hero-detail hero-detail--wide"><dt>Artists</dt><dd><span class="hero-chip">Alexander Mokhov</span></dd></div>'
    ) in block


def test_living_legend_row_holds_a_badge_naming_the_format_and_date(data):
    out = render_hero_page("# Bravo, Star of the Show\n\nLore.\n", data)
    assert (
        '<div class="hero-detail hero-detail--wide hero-detail--ll"><dt>Living Legend</dt><dd>'
        '<span class="hero-ll-badge"><i class="fas fa-trophy" aria-hidden="true"></i> '
        "Classic Constructed · 24 June 2022</span></dd></div>"
    ) in _block(out)


def test_a_hero_that_is_not_a_living_legend_has_no_badge(data):
    out = render_hero_page("# Bravo, Showstopper\n\nLore.\n", data)
    assert "hero-ll-badge" not in out


def test_a_living_legend_with_no_date_names_the_format_alone(data):
    out = render_hero_page("# Arakni, 5L!p3d 7hRu 7h3 cR4X\n\nLore.\n", data)
    assert (
        '<span class="hero-ll-badge"><i class="fas fa-trophy" aria-hidden="true"></i> ' "Classic Constructed</span>"
    ) in _block(out)


def test_a_young_card_never_shows_a_living_legend_row(data):
    switched = _block(render_hero_page("# Bravo, Showstopper\n\nLore.\n", data))
    young_variant = switched[switched.index('data-variant="young" data-name="Bravo"') :]
    own_heading = _block(render_hero_page("# Bravo\n\nYoung lore.\n", data))
    assert "hero-detail--ll" not in young_variant + own_heading


def test_details_panel_opens_with_class_and_talent_rows_linking_to_the_filtered_hub(data):
    out = render_hero_page("# Killjoy, the Crooked Blade\n\nLore.\n", data)
    assert (
        '<div class="hero-panel hero-panel--details"><p class="hero-panel-title">Details</p><dl class="hero-details">'
        '<div class="hero-detail"><dt>Class</dt><dd>'
        '<a href="heroes-of-rathe.md#class-warrior">Warrior</a>, '
        '<a href="heroes-of-rathe.md#class-thief">Thief</a></dd></div>'
        '<div class="hero-detail"><dt>Talent</dt><dd>'
        '<a href="heroes-of-rathe.md#talent-reviled">Reviled</a></dd></div>'
    ) in _block(out)


def test_a_hero_with_no_talent_has_no_talent_row(data):
    out = render_hero_page("# Bravo, Showstopper\n\nLore.\n", data)
    assert "<dt>Talent</dt>" not in _block(out)


def test_printings_panel_is_a_grid_of_every_printing_in_release_order(data):
    out = render_hero_page("# Bravo, Showstopper\n\nLore.\n", data)
    block = _block(out)
    assert (
        '<div class="hero-panel hero-panel--printings"><p class="hero-panel-title">Printings (6)</p>'
        '<div class="hero-printings-grid no-zoom">'
    ) in block
    grid = block[block.index('<div class="hero-printings-grid') :]
    order = ["promo1", "aa-rf", "ab-ea", "mm-std", "zz-unl", "cru1"]
    positions = [grid.index(f'src="{CARDS}/{i}.webp"') for i in order]
    assert positions == sorted(positions)
    assert "<details" not in block


def test_each_printing_is_a_lazy_thumbnail_captioned_with_card_id_and_finish(data):
    out = render_hero_page("# Bravo, Showstopper\n\nLore.\n", data)
    label = "WTR038, Welcome to Rathe, Standard, Extended Art, art by Alexander Mokhov"
    assert (
        '<figure class="hero-printing-item">'
        f'<img src="{CARDS}/ab-ea.webp" alt="{label}" title="{label}" '
        'class="hero-printing" loading="lazy" width="546" height="763" data-artist="Alexander Mokhov">'
        "<figcaption><code>WTR038</code> · Standard · Extended Art</figcaption></figure>"
    ) in _block(out)


_BANNER_MEDIA = (
    '<div class="hero-banner-media">\n'
    '<video width="100%" height="100%" muted loop playsinline preload="none" data-hero-autoplay>\n'
    '  <source src="https://example.test/bravo.mp4" type="video/mp4">\n'
    "</video>\n"
    '<button type="button" class="hero-banner-play" aria-label="Pause video" aria-pressed="false">'
    '<span class="hero-banner-play-pause"><i class="fas fa-pause" aria-hidden="true"></i></span>'
    '<span class="hero-banner-play-play"><i class="fas fa-play" aria-hidden="true"></i></span></button>\n'
    "</div>\n"
)


def test_heading_and_video_become_one_banner_with_the_heading_still_a_markdown_h1(data):
    out = render_hero_page("# Bravo, Showstopper\n\n" + _VIDEO + "\nLore.\n", data)
    assert out.startswith(
        '<header class="hero-banner">\n' + _BANNER_MEDIA + '<div class="hero-banner-text">\n\n'
        '# <span class="hero-banner-name">Bravo</span><span class="hero-banner-comma">, </span>'
        '<span class="hero-banner-subtitle">Showstopper</span>\n\n'
        "</div>\n"
        "</header>\n"
        "<!-- fablore-hero-banner:end -->\n\n"
        "Lore."
    )


def test_blurb_block_under_the_heading_joins_the_banner_after_a_divider(data):
    page = "# Bravo, Showstopper\n\n:::hero-blurb\nThe “strongest” man in Rathe.\n:::\n\n" + _VIDEO + "\nLore.\n"
    out = render_hero_page(page, data)
    assert (
        '<span class="hero-banner-subtitle">Showstopper</span>\n\n'
        '<div class="hero-banner-rule" aria-hidden="true"></div>\n'
        '<p class="hero-banner-blurb">The “strongest” man in Rathe.</p>\n'
        "</div>\n"
        "</header>\n"
    ) in out
    assert ":::hero-blurb" not in out
    assert out.index("</header>") < out.index("Lore.")


def test_a_form_with_no_video_gets_a_plain_banner_and_a_name_with_no_comma_has_no_subtitle(data):
    out = render_hero_page("# Bravo\n\nLore.\n", data)
    assert out.startswith(
        '<header class="hero-banner hero-banner--plain">\n'
        '<div class="hero-banner-text">\n\n'
        '# <span class="hero-banner-name">Bravo</span>\n\n'
        "</div>\n"
        "</header>\n"
    )


def test_hero_video_has_no_autoplay_and_no_controls_and_plays_only_on_screen(data):
    out = render_hero_page("# Bravo, Showstopper\n\n" + _VIDEO + "\nLore.\n", data)
    assert "autoplay muted" not in out
    assert '<video width="100%" height="100%" muted loop playsinline preload="none" data-hero-autoplay>' in out


def test_young_card_with_the_same_ability_and_no_heading_of_its_own_joins_as_a_switchable_variant(data):
    out = render_hero_page("# Bravo, Showstopper\n\nLore.\n", data)
    block = _block(out)
    assert block.count("hero-variant-switch") == 1
    assert (
        '<div class="hero-statblock-head"><p class="hero-statblock-name">Bravo, Showstopper</p>'
        '<div class="hero-statblock-controls">'
        '<div class="hero-seg hero-variant-switch" role="group" aria-label="Card version">'
        '<button type="button" class="hero-seg-btn" data-variant="adult" aria-pressed="true">Adult</button>'
        '<button type="button" class="hero-seg-btn" data-variant="young" aria-pressed="false">Young</button>'
        "</div>"
    ) in block
    young_at = block.index('<div class="hero-statblock-variant" data-variant="young" data-name="Bravo">')
    adult, young = block[:young_at], block[young_at:]
    assert '<div class="hero-statblock-variant" data-variant="adult" data-name="Bravo, Showstopper">' in adult
    assert '<div class="hero-detail"><dt>Type</dt><dd>Hero — Young</dd></div>' in young
    assert f'<img src="{CARDS}/byoung.webp"' in young


def test_young_card_worded_differently_joins_the_only_adult_card_of_its_identity_as_a_switchable_variant(data):
    block = _block(render_hero_page("# Arakni, 5L!p3d 7hRu 7h3 cR4X\n\nLore.\n", data))
    assert (
        '<button type="button" class="hero-seg-btn" data-variant="young" aria-pressed="false">Young</button>' in block
    )
    assert '<div class="hero-statblock-variant" data-variant="young" data-name="Arakni, Solitary Confinement">' in block


def test_young_card_with_its_own_heading_gets_its_own_block_not_a_switch(data):
    page = "# Bravo\n\nYoung lore.\n\n---\n\n# Bravo, Showstopper\n\nAdult lore.\n"
    out = render_hero_page(page, data)
    assert out.count('<section class="hero-statblock"') == 2
    assert "hero-variant-switch" not in out


# ---------------------------------------------------------------------------
# Forms — one at a time
# ---------------------------------------------------------------------------

_TWO_FORMS = "# Bravo, Star of the Show\n\nStar lore.\n\n---\n\n# Bravo, Showstopper\n\nShowstopper lore.\n"


def test_a_page_with_several_forms_has_no_form_rail(data):
    out = render_hero_page(_TWO_FORMS, data)
    assert "hero-form-rail" not in out


def test_each_form_is_wrapped_so_the_page_can_show_one_at_a_time(data):
    page = "# Bravo, Showstopper\n\nOld lore.\n\n---\n\n# Bravo, Star of the Show\n\nNew lore.\n"
    out = render_hero_page(page, data)
    first = out.index(
        '<div class="hero-form" data-form="bravo-showstopper" data-source="https://fabtcg.com/hero/bravo/">'
        '\n\n<header class="hero-banner'
    )
    second = out.index(
        '<div class="hero-form" data-form="bravo-star-of-the-show" data-source="https://fabtcg.com/hero/bravo-star/">'
        '\n\n<header class="hero-banner'
    )
    closes = out.index("</section>\n\n</div>", first)
    assert first < out.index("Old lore.") < closes < second < out.index("New lore.")
    assert out.index("</section>\n\n</div>\n\n", second) < out.index('<section class="hero-forms"')


def test_rule_between_forms_is_dropped_once_the_forms_are_wrapped(data):
    page = "# Bravo, Showstopper\n\nOld lore.\n\n---\n\n# Bravo, Star of the Show\n\nNew lore.\n"
    assert "---" not in render_hero_page(page, data)


def test_a_page_with_one_form_is_not_wrapped(data):
    out = render_hero_page("# Killjoy, the Crooked Blade\n\nLore.\n", data)
    assert "hero-form" not in out


# ---------------------------------------------------------------------------
# Hub — talent data for the filter
# ---------------------------------------------------------------------------


def test_hub_cards_carry_the_talents_of_every_form_on_the_linked_page(data):
    hub = (
        '<div class="hero-hub">\n'
        '    <a class="world-hub-card hero-hub-card" data-classes="guardian" href="bravo-about.md">\n'
        '    <a class="world-hub-card hero-hub-card" data-classes="warrior thief" href="killjoy-about.md">\n'
        '    <a class="world-hub-card hero-hub-card" data-classes="assassin" href="arakni-about.md">\n'
        "</div>\n"
    )
    pages = {
        "bravo-about.md": _TWO_FORMS,
        "killjoy-about.md": "# Killjoy, the Crooked Blade\n\nLore.\n",
        "arakni-about.md": "# Arakni, Solitary Confinement\n\nLore.\n",
    }
    out = render_hero_hub(hub, pages, data)
    assert 'data-classes="guardian" data-talents="elemental" ' in out
    assert 'data-classes="warrior thief" data-talents="reviled" ' in out
    assert 'data-classes="assassin" data-talents="" ' in out


def test_hub_cards_carry_the_playstyles_of_every_form_on_the_linked_page_once_each(data):
    hub = (
        '<a class="world-hub-card hero-hub-card" data-classes="guardian" href="bravo-about.md">\n'
        '<a class="world-hub-card hero-hub-card" data-classes="warrior thief" href="killjoy-about.md">\n'
        '<a class="world-hub-card hero-hub-card" data-classes="assassin" href="arakni-about.md">\n'
    )
    pages = {
        "bravo-about.md": "# Bravo\n\nYoung.\n\n---\n\n" + _TWO_FORMS,
        "killjoy-about.md": "# Killjoy, the Crooked Blade\n\nLore.\n",
        "arakni-about.md": "# Arakni, Solitary Confinement\n\nLore.\n",
    }
    cards = {line.split('href="')[1].rstrip('">'): line for line in render_hero_hub(hub, pages, data).splitlines()}
    assert ' data-playstyles="board-presence defensive combo" ' in cards["bravo-about.md"]
    assert ' data-playstyles="" ' in cards["killjoy-about.md"]
    assert ' data-playstyles="aggressive disruptive" ' in cards["arakni-about.md"]


# ---------------------------------------------------------------------------
# fabtcg.com hero data — playstyles, difficulty, portraits, source links
# ---------------------------------------------------------------------------

_PLAYSTYLE_ICONS = "https://d2hl7maqck52px.cloudfront.net/playstyle-icons"


def test_details_panel_has_a_playstyle_row_of_icons_and_names_and_a_difficulty_row_in_half_stars(data):
    block = _block(render_hero_page("# Bravo, Showstopper\n\nLore.\n", data))
    assert (
        '<div class="hero-detail hero-detail--wide"><dt>Playstyle</dt><dd>'
        '<a class="hero-playstyle" href="heroes-of-rathe.md#playstyle-board-presence">'
        f'<img class="hero-playstyle-icon" src="{_PLAYSTYLE_ICONS}/board-presence.webp" alt="" width="20" height="20">Board Presence</a>'
        '<a class="hero-playstyle" href="heroes-of-rathe.md#playstyle-defensive">'
        f'<img class="hero-playstyle-icon" src="{_PLAYSTYLE_ICONS}/defensive.webp" alt="" width="20" height="20">Defensive</a>'
        "</dd></div>"
    ) in block
    assert (
        '<div class="hero-detail"><dt>Difficulty</dt><dd>'
        '<span class="hero-difficulty" role="img" aria-label="2.5 out of 5">'
        '<span class="hero-star hero-star--full"></span><span class="hero-star hero-star--full"></span>'
        '<span class="hero-star hero-star--half"></span><span class="hero-star"></span><span class="hero-star"></span>'
        "</span></dd></div>"
    ) in block


def test_a_young_form_with_no_fabtcg_row_takes_its_adult_partners_playstyles_and_difficulty(data):
    block = _block(render_hero_page("# Bravo\n\nYoung lore.\n", data))
    assert '<a class="hero-playstyle" href="heroes-of-rathe.md#playstyle-board-presence">' in block
    assert 'aria-label="2.5 out of 5"' in block


def test_a_young_form_whose_text_differs_takes_the_only_adult_card_of_its_identity_with_a_row(data):
    block = _block(render_hero_page("# Florian\n\nYoung lore.\n", data))
    assert '<a class="hero-playstyle" href="heroes-of-rathe.md#playstyle-board-presence">' in block
    assert 'aria-label="3 out of 5"' in block


def test_a_card_with_no_fabtcg_row_or_partner_has_no_playstyle_or_difficulty_row(data):
    block = _block(render_hero_page("# Killjoy, the Crooked Blade\n\nLore.\n", data))
    assert "<dt>Playstyle</dt>" not in block
    assert "<dt>Difficulty</dt>" not in block


def test_each_form_of_a_multi_form_page_carries_its_own_fabtcg_page_for_the_source_link(data):
    out = render_hero_page(_TWO_FORMS, data)
    assert (
        '<div class="hero-form" data-form="bravo-star-of-the-show" data-source="https://fabtcg.com/hero/bravo-star/">'
        in out
    )
    assert '<div class="hero-form" data-form="bravo-showstopper" data-source="https://fabtcg.com/hero/bravo/">' in out


def test_a_form_with_no_fabtcg_page_carries_no_source_link_data(data):
    page = "# Killjoy, the Crooked Blade\n\nLore.\n\n---\n\n# Bravo, Showstopper\n\nLore.\n"
    assert '<div class="hero-form" data-form="killjoy-the-crooked-blade">' in render_hero_page(page, data)


def test_card_from_a_set_with_no_release_date_yet_still_shows_its_card_id_and_artist(data):
    out = render_hero_page("# Killjoy, the Crooked Blade\n\nLore.\n", data)
    block = _block(out)
    assert f'<img src="{CARDS}/kj1.webp" alt="Killjoy, the Crooked Blade card (SPW001)"' in block
    assert (
        '<span class="hero-statblock-print"><code>SPW001</code> · Rainbow Foil</span>'
        '<span class="hero-statblock-artist">Henrique Lindner</span>'
    ) in block
    assert "<dt>First released</dt>" not in block


_PORTRAITS = "https://d2hl7maqck52px.cloudfront.net/hero-icons"


def _tab(form_id: str, selected: str, key: str, label: str, year: str, sub: str) -> str:
    return (
        f'<a class="hero-tab" role="tab" href="#{form_id}" aria-selected="{selected}">'
        f'<span class="hero-tab-year">{year}</span>'
        f'<img class="hero-tab-portrait" src="{_PORTRAITS}/{key}.webp" alt="" width="112" height="112" loading="lazy">'
        f'<span class="hero-tab-label">{label}</span><span class="hero-tab-sub">{sub}</span></a>'
    )


def test_a_multi_form_page_ends_with_a_forms_section_listing_every_form_in_release_order_newest_selected(data):
    out = render_hero_page(_TWO_FORMS + "\n" + _RELATED, data)
    rail = (
        '<section class="hero-forms" aria-labelledby="hero-forms-title">\n\n'
        '<p class="hero-forms-title" id="hero-forms-title" role="heading" aria-level="2">Forms of Bravo</p>\n\n'
        '<div class="hero-forms-rail" role="tablist" aria-label="Forms of Bravo">'
        + _tab("bravo-showstopper", "false", "bravo-showstopper", "Showstopper", "2019", "Welcome to Rathe")
        + _tab(
            "bravo-star-of-the-show",
            "true",
            "bravo-star-of-the-show",
            "Star of the Show",
            "2022",
            "Everfest · Living Legend",
        )
        + "</div>\n\n</section>\n\n"
    )
    assert out.endswith("</section>\n\n</div>\n\n" + rail + _DIVIDER + "\n\n" + _RELATED)


def test_the_forms_title_is_no_markdown_heading_so_it_stays_out_of_the_sidebar(data):
    out = render_hero_page(_TWO_FORMS, data)
    assert "## Forms of" not in out
    assert "<h2" not in out


def test_the_banner_no_longer_carries_the_forms(data):
    out = render_hero_page(_TWO_FORMS, data)
    assert out.count("</header>\n<!-- fablore-hero-banner:end -->") == 2
    assert out.count('class="hero-tab"') == 2


def test_a_young_form_with_no_subtitle_is_labelled_by_its_full_name_marked_young_and_shows_its_partners_portrait(
    data,
):
    page = "# Bravo\n\nYoung lore.\n\n---\n\n# Bravo, Showstopper\n\nAdult lore.\n"
    out = render_hero_page(page, data)
    assert _tab("bravo", "false", "bravo-showstopper", "Bravo", "2019", "Welcome to Rathe · Young") in out


def test_a_page_with_one_form_has_no_forms_section(data):
    assert "hero-forms" not in render_hero_page("# Bravo, Showstopper\n\nLore.\n", data)


# ---------------------------------------------------------------------------
# Dividers — the emblem rule between the parts of a hero page
# ---------------------------------------------------------------------------

_DIVIDER = (
    '<div class="hero-divider" role="presentation" aria-hidden="true">'
    '<img src="../assets/logo-emblem.webp" alt="" class="hero-divider-emblem" width="44" height="44" '
    'loading="lazy" decoding="async"></div>'
)


def test_a_divider_separates_the_trait_grid_from_the_stat_block(data):
    out = render_hero_page("# Bravo, Showstopper\n\nLore.\n\n" + _TRAIT, data)
    assert "Trait text.\n:::\n\n" + _DIVIDER + '\n\n<section class="hero-statblock"' in out


def test_a_form_with_no_traits_has_no_divider_before_its_stat_block(data):
    out = render_hero_page("# Bravo, Showstopper\n\nLore.\n", data)
    assert "hero-divider" not in out


_RELATED = (
    "<!-- fablore-related:start -->\n"
    '<section class="related-section" aria-label="Related Lore"><h1 id="related-lore">Related Lore</h1></section>\n'
    "<!-- fablore-related:end -->\n"
)


def test_related_lore_follows_the_forms_section_after_a_divider(data):
    out = render_hero_page(_TWO_FORMS + "\n" + _RELATED, data)
    assert out.endswith("</div>\n\n</section>\n\n" + _DIVIDER + "\n\n" + _RELATED)
