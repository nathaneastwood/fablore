"""Tests for :mod:`mdbook_hero_meta` preprocessor helpers."""

from __future__ import annotations

import re

from mdbook_hero_meta import _build_hero_meta_html


# ---------------------------------------------------------------------------
# FA6 icon prefix — mirrors the guards in test_mdbook_story_meta.py
# ---------------------------------------------------------------------------

def _meta(first_set_name="", classes=(), talents=(), ll=()):
    return {
        "first_set_name": first_set_name,
        "first_set_date": "",
        "classes": list(classes),
        "talents": list(talents),
        "ll": list(ll),
    }


def test_no_bare_fa_prefix_in_meta_html() -> None:
    """All icons must use an explicit FA6 prefix (fas/fab/far), not bare 'fa'.
    Bare 'fa' defaults to FA6 regular and emits a build warning for
    icons that only exist in solid (cube, tag, trophy)."""
    html = _build_hero_meta_html(
        _meta(
            first_set_name="Welcome to Rathe",
            classes=["Warrior"],
            ll=[{"Format": "CC", "DateInEffect": "2024-01-01"}],
        )
    )
    bare_fa = re.findall(r'class="fa fa-', html)
    assert bare_fa == [], f"Found bare FA4 'fa' prefix in hero meta HTML: {bare_fa}"


def test_set_icon_uses_fa6_solid() -> None:
    html = _build_hero_meta_html(_meta(first_set_name="Welcome to Rathe"))
    assert 'class="fas fa-cube"' in html


def test_class_talent_icon_uses_fa6_solid() -> None:
    html = _build_hero_meta_html(_meta(classes=["Warrior"], talents=["Earth"]))
    assert 'class="fas fa-tag"' in html


def test_living_legend_icon_uses_fa6_solid() -> None:
    html = _build_hero_meta_html(
        _meta(ll=[{"Format": "CC", "DateInEffect": "2024-01-01"}])
    )
    assert 'class="fas fa-trophy"' in html


def test_empty_meta_returns_empty_string() -> None:
    assert _build_hero_meta_html(_meta()) == ""


def test_classes_and_talents_combined() -> None:
    html = _build_hero_meta_html(_meta(classes=["Warrior"], talents=["Earth"]))
    assert "Warrior" in html
    assert "Earth" in html
