"""Tests for mdbook_hero_traits._expand() and _build_html()."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src/data"))

from mdbook_hero_traits import _build_html, _expand, _walk, main  # noqa: E402

IMG = "https://example.com/image.webp"


def test_build_html_structure():
    result = _build_html("Power of Steam", IMG, "Mechanologists pursue energy sources.")
    assert '<div class="hero-container">' in result
    assert f'<img src="{IMG}"' in result
    assert 'class="hero-icon"' in result
    assert "<b>Power of Steam</b>" in result
    assert "Mechanologists pursue energy sources." in result


def test_build_html_strips_description_whitespace():
    result = _build_html("Title", IMG, "  Body text.  ")
    assert "Body text." in result
    assert "  Body text.  " not in result


def test_expand_single_block():
    content = (
        ":::hero-trait Power of Steam\n"
        f"![Power of Steam]({IMG})\n"
        "Mechanologists are driven by alternative energy.\n"
        ":::"
    )
    result = _expand(content)
    assert '<div class="hero-container">' in result
    assert ":::hero-trait" not in result
    assert "<b>Power of Steam</b>" in result


def test_expand_multiple_blocks():
    block = (
        ":::hero-trait Title One\n"
        f"![Alt]({IMG})\n"
        "Description one.\n"
        ":::\n\n"
        ":::hero-trait Title Two\n"
        f"![Alt]({IMG})\n"
        "Description two.\n"
        ":::"
    )
    result = _expand(block)
    assert result.count('<div class="hero-container">') == 2
    assert "<b>Title One</b>" in result
    assert "<b>Title Two</b>" in result


def test_expand_no_block_unchanged():
    content = "Just regular markdown content.\n"
    assert _expand(content) == content


def test_expand_preserves_surrounding_content():
    content = (
        "# Hero Page\n\n"
        ":::hero-trait Special Ability\n"
        f"![SA]({IMG})\n"
        "Does something great.\n"
        ":::\n\n"
        "More text after.\n"
    )
    result = _expand(content)
    assert "# Hero Page" in result
    assert "More text after." in result


def test_expand_multiline_description():
    content = (
        ":::hero-trait My Trait\n" f"![img]({IMG})\n" "Line one.\n" "Line two.\n" ":::"
    )
    result = _expand(content)
    assert "Line one." in result
    assert "Line two." in result


def test_walk_expands_chapter_content():
    content = f":::hero-trait T\n![T]({IMG})\nDesc.\n:::"
    sections = [{"Chapter": {"content": content, "sub_items": []}}]
    _walk(sections)
    assert '<div class="hero-container">' in sections[0]["Chapter"]["content"]


def test_walk_recurses_into_sub_items():
    content = f":::hero-trait T\n![T]({IMG})\nDesc.\n:::"
    sections = [
        {
            "Chapter": {
                "content": "outer",
                "sub_items": [{"Chapter": {"content": content, "sub_items": []}}],
            }
        }
    ]
    _walk(sections)
    assert (
        '<div class="hero-container">'
        in sections[0]["Chapter"]["sub_items"][0]["Chapter"]["content"]
    )


def test_walk_skips_non_dict():
    _walk(["not a dict"])  # should not raise


def test_walk_handles_empty_content():
    sections = [{"Chapter": {"content": None, "sub_items": []}}]
    _walk(sections)
    assert sections[0]["Chapter"]["content"] == ""


def test_main_processes_book(monkeypatch):
    import io, json

    block = f":::hero-trait T\n![T]({IMG})\nDesc.\n:::"
    book = {"items": [{"Chapter": {"content": block, "sub_items": []}}]}
    ctx = {"root": "/tmp"}
    payload = json.dumps([ctx, book])
    monkeypatch.setattr(sys, "stdin", io.TextIOWrapper(io.BytesIO(payload.encode())))
    out = io.StringIO()
    monkeypatch.setattr(sys, "stdout", out)
    main()
    result = json.loads(out.getvalue())
    assert '<div class="hero-container">' in result["items"][0]["Chapter"]["content"]


def test_main_supports_exits(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["mdbook_hero_traits", "supports", "html"])
    with pytest.raises(SystemExit) as exc:
        main()
    assert exc.value.code == 0
