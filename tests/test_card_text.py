"""Tests for card_text.format_ability_text()."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src/data"))

from card_text import format_ability_text  # noqa: E402

ICONS = "https://d2hl7maqck52px.cloudfront.net/card-icons"


def test_plain_text_becomes_one_paragraph():
    assert format_ability_text("You may attack any opposing hero.") == "<p>You may attack any opposing hero.</p>"


def test_html_in_the_source_is_escaped():
    assert format_ability_text('Deal 1 <script> & "x"') == "<p>Deal 1 &lt;script&gt; &amp; &quot;x&quot;</p>"


def test_double_space_separates_paragraphs():
    text = "You may attack any opposing hero.  Whenever you steal a Gold, boo.  The end."
    assert format_ability_text(text) == (
        "<p>You may attack any opposing hero.</p><p>Whenever you steal a Gold, boo.</p><p>The end.</p>"
    )


def test_symbol_tokens_become_icons():
    assert format_ability_text("Pay {r}, gain 1{h}.") == (
        f'<p>Pay <img src="{ICONS}/icon_cost.webp" alt="Resource" class="card-glyph">, '
        f'gain 1<img src="{ICONS}/icon_hp.webp" alt="Health" class="card-glyph">.</p>'
    )


def test_every_symbol_maps_to_its_icon():
    expected = [
        ("p", "icon_pwr.webp", "Power"),
        ("r", "icon_cost.webp", "Resource"),
        ("h", "icon_hp.webp", "Health"),
        ("d", "icon_def.webp", "Defense"),
        ("i", "icon_int.webp", "Intellect"),
        ("t", "icon_t.webp", "Tap"),
        ("u", "icon_u.webp", "Untap"),
        ("c", "icon_chi.webp", "Chi"),
    ]
    for code, icon, alt in expected:
        assert format_ability_text("{" + code + "}") == (
            f'<p><img src="{ICONS}/{icon}" alt="{alt}" class="card-glyph"></p>'
        )


def test_unknown_token_is_left_as_is():
    assert format_ability_text("Gain {x} and {zz}.") == "<p>Gain {x} and {zz}.</p>"


def test_double_asterisks_become_bold():
    assert format_ability_text("**Action** - draw a card.") == "<p><b>Action</b> - draw a card.</p>"


def test_bold_keyword_is_only_bold():
    assert format_ability_text("Then **the crowd boos** you.") == "<p>Then <b>the crowd boos</b> you.</p>"


def test_unbolded_rules_word_is_left_plain():
    assert format_ability_text("If it has crush, attack again.") == "<p>If it has crush, attack again.</p>"


def test_bravo_ability_text():
    text = (
        "**Action** - {r}{r}: Until end of turn, your attack action cards with cost 3 or more get "
        "**dominate**. **Go again**"
    )
    r = f'<img src="{ICONS}/icon_cost.webp" alt="Resource" class="card-glyph">'
    assert format_ability_text(text) == (
        f"<p><b>Action</b> - {r}{r}: Until end of turn, your attack action cards with cost 3 or more get "
        "<b>dominate</b>. <b>Go again</b></p>"
    )


def test_empty_text_renders_nothing():
    assert format_ability_text("") == ""
