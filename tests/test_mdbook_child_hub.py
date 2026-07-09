"""Tests for :mod:`mdbook_child_hub` preprocessor."""

from __future__ import annotations

from pathlib import Path

import pytest

from mdbook_child_hub import (
    _card_grid_html,
    _child_image,
    _inject_hub,
    _load_card_image_lookup,
    _page_img_fallback,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def src_root(tmp_path: Path) -> Path:
    """Minimal src tree with a weapon page (has <img>) and a plain page (no <img>)."""
    (tmp_path / "weapons").mkdir()
    (tmp_path / "weapons" / "cintari-saber.md").write_text(
        "# Cintari Saber\n\n"
        '<img src="https://d2hl7maqck52px.cloudfront.net/weapons/cintari-saber.webp" '
        'alt="cintari-saber" class="center">\n'
    )
    (tmp_path / "weapons" / "no-image-weapon.md").write_text("# No Image Weapon\n")
    (tmp_path / "other-characters").mkdir()
    (tmp_path / "other-characters" / "the-librarian.md").write_text("# The Librarian\n")
    return tmp_path


@pytest.fixture
def data_dir(tmp_path: Path) -> Path:
    """Minimal weapons CSV trio, plus sets.csv.

    Printings CSV deliberately lists the *later*-released reprint set (1HP,
    2022) before the true earliest set (CRU, 2020), mirroring upstream
    ``card-printing.csv`` row order — the lookup must pick by release date,
    not file order.
    """
    data = tmp_path / "data"
    csv_dir = data / "csv"
    csv_dir.mkdir(parents=True)

    (csv_dir / "sets.csv").write_text(
        "# AUTO-GENERATED\n"
        "SetId|SetName|InitialReleaseDate\n"
        "1HP|History Pack 1|2022-05-06T00:00:00.000Z\n"
        "CRU|Crucible of War|2020-08-28T00:00:00.000Z\n"
    )
    (csv_dir / "weapons-canonical.csv").write_text(
        "# AUTO-GENERATED\n"
        "CanonicalWeaponId|CanonicalSlug|CanonicalWeapon\n"
        "CW1|cintari-saber|Cintari Saber\n"
    )
    (csv_dir / "weapons-game.csv").write_text(
        "# AUTO-GENERATED\n"
        "WeaponGameId|CardName|CanonicalWeaponId\n"
        "WG1|Cintari Saber|CW1\n"
    )
    (csv_dir / "weapons-printings.csv").write_text(
        "# AUTO-GENERATED\n"
        "WeaponGameId|SetId|CardId|Rarity|ImageURL\n"
        "WG1|1HP|1HP141|R|https://storage.googleapis.com/fabmaster/1HP141.png\n"
        "WG1|CRU|CRU079|R|https://storage.googleapis.com/fabmaster/cardfaces/2020-CRU/CRU079.png\n"
    )
    return data


# ---------------------------------------------------------------------------
# _load_card_image_lookup
# ---------------------------------------------------------------------------


def test_load_card_image_lookup_picks_earliest_release_not_file_order(
    data_dir: Path,
) -> None:
    """The 1HP reprint row appears first in the CSV but released later than CRU —
    the true earliest-release printing (CRU) must win."""
    lookup = _load_card_image_lookup(data_dir, "weapons")
    assert (
        lookup["cintari-saber"]
        == "https://storage.googleapis.com/fabmaster/cardfaces/2020-CRU/CRU079.png"
    )


def test_load_card_image_lookup_missing_files(tmp_path: Path) -> None:
    """Missing CSVs (empty data dir) yield an empty lookup, not an error."""
    data = tmp_path / "data"
    (data / "csv").mkdir(parents=True)
    assert _load_card_image_lookup(data, "weapons") == {}


# ---------------------------------------------------------------------------
# _page_img_fallback
# ---------------------------------------------------------------------------


def test_page_img_fallback_finds_img(src_root: Path) -> None:
    src = _page_img_fallback(src_root, "weapons/cintari-saber.md")
    assert src == "https://d2hl7maqck52px.cloudfront.net/weapons/cintari-saber.webp"


def test_page_img_fallback_no_img(src_root: Path) -> None:
    assert _page_img_fallback(src_root, "weapons/no-image-weapon.md") == ""


def test_page_img_fallback_missing_file(src_root: Path) -> None:
    assert _page_img_fallback(src_root, "weapons/does-not-exist.md") == ""


# ---------------------------------------------------------------------------
# _child_image
# ---------------------------------------------------------------------------


def test_child_image_uses_csv_lookup(src_root: Path, data_dir: Path) -> None:
    lookup = _load_card_image_lookup(data_dir, "weapons")
    image, is_card_art = _child_image(
        src_root, "weapons/cintari-saber.md", "weapons", lookup
    )
    assert (
        image
        == "https://storage.googleapis.com/fabmaster/cardfaces/2020-CRU/CRU079.png"
    )
    assert is_card_art is True


def test_child_image_loose_slug_match(src_root: Path) -> None:
    """A file slug like talishar-lost-prince (missing "the") still resolves
    against a canonical slug of talishar-the-lost-prince."""
    lookup = {
        "talishar-the-lost-prince": "https://storage.googleapis.com/fabmaster/talishar.png"
    }
    (src_root / "weapons" / "talishar-lost-prince.md").write_text("# Talishar\n")
    image, is_card_art = _child_image(
        src_root, "weapons/talishar-lost-prince.md", "weapons", lookup
    )
    assert image == "https://storage.googleapis.com/fabmaster/talishar.png"
    assert is_card_art is True


def test_child_image_falls_back_to_page_img_when_no_csv_match(src_root: Path) -> None:
    """A weapon whose file slug doesn't match any canonical slug at all falls
    back to scanning the page's own <img> tag."""
    image, is_card_art = _child_image(
        src_root, "weapons/cintari-saber.md", "weapons", {}
    )
    assert image == "https://d2hl7maqck52px.cloudfront.net/weapons/cintari-saber.webp"
    assert is_card_art is False


def test_child_image_plain_has_no_image(src_root: Path) -> None:
    image, is_card_art = _child_image(
        src_root, "other-characters/the-librarian.md", "plain", {}
    )
    assert image == ""
    assert is_card_art is False


def test_child_image_no_match_no_img_is_empty(src_root: Path) -> None:
    image, is_card_art = _child_image(
        src_root, "weapons/no-image-weapon.md", "weapons", {}
    )
    assert image == ""
    assert is_card_art is False


# ---------------------------------------------------------------------------
# _card_grid_html
# ---------------------------------------------------------------------------


def test_card_grid_html_renders_image_and_link(src_root: Path, data_dir: Path) -> None:
    lookup = _load_card_image_lookup(data_dir, "weapons")
    children = [{"name": "Cintari Saber", "path": "weapons/cintari-saber.md"}]
    html_out = _card_grid_html(
        "weapons/armed-to-the-teeth.md", src_root, children, "weapons", lookup
    )
    assert 'class="sets-hub-grid"' in html_out
    assert 'class="sets-hub-card"' in html_out
    assert 'href="cintari-saber.md"' in html_out
    assert "Cintari Saber" in html_out
    assert "storage.googleapis.com" in html_out


def test_card_grid_html_plain_has_no_img_tag(src_root: Path) -> None:
    children = [{"name": "The Librarian", "path": "other-characters/the-librarian.md"}]
    html_out = _card_grid_html(
        "other-characters/README.md", src_root, children, "plain", {}
    )
    assert "<img" not in html_out
    assert "The Librarian" in html_out


def test_card_grid_html_escapes_name() -> None:
    children = [{"name": "A & B", "path": "weapons/a-and-b.md"}]
    html_out = _card_grid_html(
        "weapons/armed-to-the-teeth.md", Path("/nonexistent"), children, "plain", {}
    )
    assert "A &amp; B" in html_out


# ---------------------------------------------------------------------------
# _inject_hub
# ---------------------------------------------------------------------------


def test_inject_hub_appends_block() -> None:
    content = "# Title\n\nBody text.\n"
    out = _inject_hub(content, "<div>grid</div>")
    assert out.index("Body text.") < out.index("<!-- fablore-child-hub:start -->")
    assert "<div>grid</div>" in out


def test_inject_hub_idempotent() -> None:
    content = "# Title\n\nBody.\n"
    once = _inject_hub(content, "<div>grid</div>")
    twice = _inject_hub(once, "<div>grid</div>")
    assert twice.count("fablore-child-hub:start") == 1


def test_inject_hub_replaces_existing_markers() -> None:
    content = (
        "# Title\n\n"
        "<!-- fablore-child-hub:start -->\n"
        "<div>OLD</div>\n"
        "<!-- fablore-child-hub:end -->\n"
    )
    out = _inject_hub(content, "<div>NEW</div>")
    assert "OLD" not in out
    assert "NEW" in out
