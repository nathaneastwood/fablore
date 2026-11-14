"""Tests for :mod:`mdbook_archive_notice` preprocessor."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from mdbook_archive_notice import (
    _hero_archive,
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
# _hero_archive: archive/heroes-of-rathe/ pages name their current page
# ---------------------------------------------------------------------------


def _old(target: str = "heroes-of-rathe/rhinar-about.md") -> str:
    return f"# Rhinar, Old\n\n:::archive-of {target}:::\n\n<video></video>\n\nOld lore.\n"


def test_hero_archive_none_for_non_archive(src_root: Path) -> None:
    assert _hero_archive("heroes-of-rathe/rhinar-about.md", _old(), src_root) is None


def test_hero_archive_none_for_world_archive(src_root: Path) -> None:
    assert _hero_archive("archive/world-of-rathe/volcor/volcor.md", _old(), src_root) is None


def test_hero_archive_skips_the_hub_page(src_root: Path) -> None:
    """The heroes-of-rathe.md hub has no directive and gets no notice."""
    assert _hero_archive("archive/heroes-of-rathe/heroes-of-rathe.md", "# Heroes\n", src_root) is None


def test_hero_archive_links_the_directive_target(src_root: Path) -> None:
    notice, _ = _hero_archive("archive/heroes-of-rathe/rhinar-wtr.md", _old(), src_root)
    assert notice == (
        "> [!WARNING]\n> This hero overview has been superseded. "
        "For the current version, see [Rhinar](../../heroes-of-rathe/rhinar-about.md)."
    )


def test_hero_archive_removes_the_directive_line(src_root: Path) -> None:
    _, content = _hero_archive("archive/heroes-of-rathe/rhinar-wtr.md", _old(), src_root)
    assert content == "# Rhinar, Old\n\n<video></video>\n\nOld lore.\n"


def test_hero_archive_target_need_not_share_the_archive_slug(src_root: Path) -> None:
    """The directive, not the file name, decides: no prefix guessing."""
    (src_root / "heroes-of-rathe" / "valda-about.md").write_text("# Valda, Seismic Impact\n")
    notice, _ = _hero_archive("archive/heroes-of-rathe/rhinar-wtr.md", _old("heroes-of-rathe/valda-about.md"), src_root)
    assert "see [Valda, Seismic Impact](../../heroes-of-rathe/valda-about.md)." in notice


def test_hero_archive_links_with_the_current_pages_first_h1(src_root: Path) -> None:
    (src_root / "heroes-of-rathe" / "valda-about.md").write_text(
        "<!-- note -->\n\n# Valda, Seismic Impact\n\nLore.\n\n# Valda Brightaxe\n"
    )
    notice, _ = _hero_archive(
        "archive/heroes-of-rathe/valda-brightaxe.md", _old("heroes-of-rathe/valda-about.md"), src_root
    )
    assert "see [Valda, Seismic Impact](../../heroes-of-rathe/valda-about.md)." in notice


def test_hero_archive_falls_back_to_the_target_slug_when_it_has_no_h1(src_root: Path) -> None:
    (src_root / "heroes-of-rathe" / "bravo-about.md").write_text("Lore only.\n")
    notice, _ = _hero_archive("archive/heroes-of-rathe/bravo-wtr.md", _old("heroes-of-rathe/bravo-about.md"), src_root)
    assert "see [Bravo](../../heroes-of-rathe/bravo-about.md)." in notice


def test_hero_archive_escapes_markdown_in_the_link_text(src_root: Path) -> None:
    (src_root / "heroes-of-rathe" / "odd-about.md").write_text("# Odd [One]_*\\x\n")
    notice, _ = _hero_archive("archive/heroes-of-rathe/odd-old.md", _old("heroes-of-rathe/odd-about.md"), src_root)
    assert "see [Odd \\[One\\]\\_\\*\\\\x](../../heroes-of-rathe/odd-about.md)." in notice


def test_hero_archive_without_a_directive_fails(src_root: Path) -> None:
    with pytest.raises(ValueError, match=r"archive/heroes-of-rathe/rhinar-wtr\.md.*:::archive-of"):
        _hero_archive("archive/heroes-of-rathe/rhinar-wtr.md", "# Rhinar\n\nOld lore.\n", src_root)


def test_hero_archive_with_a_missing_target_fails(src_root: Path) -> None:
    with pytest.raises(ValueError, match=r"heroes-of-rathe/nobody-about\.md"):
        _hero_archive("archive/heroes-of-rathe/rhinar-wtr.md", _old("heroes-of-rathe/nobody-about.md"), src_root)


# ---------------------------------------------------------------------------
# The committed archive pages
# ---------------------------------------------------------------------------

_SRC = Path(__file__).resolve().parents[1] / "src"
_HERO_ARCHIVE = _SRC / "archive" / "heroes-of-rathe"


def _hero_archive_pages() -> list[Path]:
    return sorted(p for p in _HERO_ARCHIVE.glob("*.md") if p.name != "heroes-of-rathe.md")


def test_every_hero_archive_page_names_an_existing_current_page() -> None:
    pages = _hero_archive_pages()
    assert pages
    for page in pages:
        m = re.search(r"^:::archive-of (\S+):::$", page.read_text(encoding="utf-8"), re.MULTILINE)
        assert m, f"{page.name} has no :::archive-of directive"
        assert (_SRC / m.group(1)).is_file(), f"{page.name}: {m.group(1)} does not exist"


# What the shrinking-slug-prefix guess produced before the directive replaced it.
_PINNED_NOTICES = {
    "arakni-5l!p3d-7hru-7h3-cr4x-about.md": (
        "[Arakni, 5l!p3d 7hru 7h3 Cr4x](../../heroes-of-rathe/arakni-5l!p3d-7hru-7h3-cr4x-about.md)"
    ),
    "rhinar-wtr.md": "[Rhinar, Reckless Rampage](../../heroes-of-rathe/rhinar-about.md)",
    "valda-brightaxe.md": "[Valda, Seismic Impact](../../heroes-of-rathe/valda-about.md)",
}


def test_committed_hero_archive_notices_are_unchanged() -> None:
    got = {}
    for page in _hero_archive_pages():
        notice, content = _hero_archive(f"archive/heroes-of-rathe/{page.name}", page.read_text(encoding="utf-8"), _SRC)
        assert ":::archive-of" not in content
        got[page.name] = notice
    assert got == {
        name: f"> [!WARNING]\n> This hero overview has been superseded. For the current version, see {link}."
        for name, link in _PINNED_NOTICES.items()
    }


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
