"""Tests for :mod:`mdbook_archive_notice` preprocessor."""

from __future__ import annotations

from pathlib import Path

import pytest

from mdbook_archive_notice import (
    _hero_notice,
    _inject_notice,
    _world_notice,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def src_root(tmp_path: Path) -> Path:
    """Minimal src tree with one world-of-rathe page and one hero about page."""
    (tmp_path / "world-of-rathe").mkdir()
    (tmp_path / "world-of-rathe" / "volcor.md").write_text("# Volcor\n")
    (tmp_path / "heroes-of-rathe").mkdir()
    (tmp_path / "heroes-of-rathe" / "rhinar-about.md").write_text("# Rhinar\n")
    return tmp_path


# ---------------------------------------------------------------------------
# _world_notice
# ---------------------------------------------------------------------------


def test_world_notice_none_for_non_archive(src_root: Path) -> None:
    assert _world_notice("world-of-rathe/volcor.md", src_root) is None


def test_world_notice_none_for_heroes_archive(src_root: Path) -> None:
    assert _world_notice("archive/heroes-of-rathe/rhinar-wtr.md", src_root) is None


def test_world_notice_with_link(src_root: Path) -> None:
    notice = _world_notice("archive/world-of-rathe/volcor/wildlife.md", src_root)
    assert notice is not None
    assert "[!WARNING]" in notice
    assert "[Volcor]" in notice
    assert "volcor.md" in notice or "volcor" in notice


def test_world_notice_without_link(src_root: Path) -> None:
    """When no current page exists, notice omits the link."""
    notice = _world_notice("archive/world-of-rathe/pits/pits.md", src_root)
    assert notice is not None
    assert "[!WARNING]" in notice
    assert "historical reference" in notice
    assert "](" not in notice  # no Markdown link in message


def test_world_notice_relative_href(src_root: Path) -> None:
    """Relative link must be correct for nested archive path."""
    notice = _world_notice("archive/world-of-rathe/volcor/wildlife.md", src_root)
    # From archive/world-of-rathe/volcor/ to world-of-rathe/volcor.md
    assert "../../world-of-rathe/volcor.md" in notice


def test_world_notice_uses_warning_admonition(src_root: Path) -> None:
    notice = _world_notice("archive/world-of-rathe/volcor/volcor.md", src_root)
    assert notice is not None
    assert notice.startswith("> [!WARNING]")


# ---------------------------------------------------------------------------
# _hero_notice
# ---------------------------------------------------------------------------


def test_hero_notice_none_for_non_archive(src_root: Path) -> None:
    assert _hero_notice("heroes-of-rathe/rhinar-about.md", src_root) is None


def test_hero_notice_none_for_world_archive(src_root: Path) -> None:
    assert _hero_notice("archive/world-of-rathe/volcor/volcor.md", src_root) is None


def test_hero_notice_skips_index_page(src_root: Path) -> None:
    """The heroes-of-rathe.md index page must not receive a notice."""
    assert _hero_notice("archive/heroes-of-rathe/heroes-of-rathe.md", src_root) is None


def test_hero_notice_resolves_slug(src_root: Path) -> None:
    """rhinar-wtr should resolve to rhinar-about.md via prefix stripping."""
    notice = _hero_notice("archive/heroes-of-rathe/rhinar-wtr.md", src_root)
    assert notice is not None
    assert "[!WARNING]" in notice
    assert "[Rhinar]" in notice
    assert "rhinar-about.md" in notice


def test_hero_notice_relative_href(src_root: Path) -> None:
    notice = _hero_notice("archive/heroes-of-rathe/rhinar-wtr.md", src_root)
    assert "../../heroes-of-rathe/rhinar-about.md" in notice


def test_hero_notice_uses_warning_admonition(src_root: Path) -> None:
    notice = _hero_notice("archive/heroes-of-rathe/rhinar-wtr.md", src_root)
    assert notice is not None
    assert notice.startswith("> [!WARNING]")


def test_hero_notice_fallback_when_no_current_page(src_root: Path) -> None:
    """An archive hero with no matching current page gets a generic notice."""
    notice = _hero_notice("archive/heroes-of-rathe/unknown-arc.md", src_root)
    assert notice is not None
    assert "[!WARNING]" in notice
    assert "historical reference" in notice


# ---------------------------------------------------------------------------
# _inject_notice
# ---------------------------------------------------------------------------


def test_inject_notice_after_h1() -> None:
    content = "# Title\n\nBody text.\n"
    notice = "> [!WARNING]\n> Superseded."
    out = _inject_notice(content, notice)
    assert out.index("# Title") < out.index("> [!WARNING]") < out.index("Body text.")


def test_inject_notice_replaces_existing_markers() -> None:
    content = (
        "# Title\n\n"
        "<!-- fablore-archive-notice:start -->\n"
        "> [!WARNING]\n> OLD\n"
        "<!-- fablore-archive-notice:end -->\n\n"
        "Body."
    )
    out = _inject_notice(content, "> [!WARNING]\n> NEW")
    assert "OLD" not in out
    assert "NEW" in out
    assert "Body." in out


def test_inject_notice_idempotent(src_root: Path) -> None:
    content = "# Title\n\nBody.\n"
    notice = "> [!WARNING]\n> Superseded."
    once = _inject_notice(content, notice)
    twice = _inject_notice(once, notice)
    assert twice.count("fablore-archive-notice:start") == 1


def test_inject_notice_no_h1_prepends() -> None:
    content = "Just a paragraph.\n"
    notice = "> [!WARNING]\n> Superseded."
    out = _inject_notice(content, notice)
    assert out.startswith("<!-- fablore-archive-notice:start -->")
