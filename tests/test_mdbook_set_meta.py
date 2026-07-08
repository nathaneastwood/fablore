"""Tests for :mod:`mdbook_set_meta` preprocessor helpers."""

from __future__ import annotations

import re

from mdbook_set_meta import _build_set_meta_html


def _meta(set_name="", release_date="", set_type=""):
    return {"set_name": set_name, "release_date": release_date, "set_type": set_type}


# ---------------------------------------------------------------------------
# FA6 icon prefix
# ---------------------------------------------------------------------------

def test_no_bare_fa_prefix_in_set_meta_html() -> None:
    """All icons must use an explicit FA6 prefix, not bare 'fa'."""
    html = _build_set_meta_html(
        _meta(set_name="Welcome to Rathe", release_date="2019-10-11", set_type="Core")
    )
    bare_fa = re.findall(r'class="fa fa-', html)
    assert bare_fa == [], f"Found bare FA4 'fa' prefix in set meta HTML: {bare_fa}"


def test_set_name_icon_uses_fa6_solid() -> None:
    html = _build_set_meta_html(_meta(set_name="Welcome to Rathe"))
    assert 'class="fas fa-cube"' in html


def test_release_date_icon_uses_fa6_solid() -> None:
    html = _build_set_meta_html(_meta(set_name="WTR", release_date="2019-10-11"))
    assert 'class="fas fa-calendar"' in html


def test_set_type_icon_uses_fa6_solid() -> None:
    html = _build_set_meta_html(_meta(set_name="WTR", set_type="Core"))
    assert 'class="fas fa-tag"' in html


def test_empty_meta_returns_empty_string() -> None:
    assert _build_set_meta_html(_meta()) == ""


def test_set_name_appears_in_output() -> None:
    html = _build_set_meta_html(_meta(set_name="Welcome to Rathe"))
    assert "Welcome to Rathe" in html
