"""Tests for hero CardName vs CanonicalId resolution in :mod:`validate_data`."""

from __future__ import annotations

from pathlib import Path

from validate_data import (
    _check_heroes_game_ambiguous_card_names,
    _check_heroes_game_cardname_resolution,
    _check_heroes_game_young_hero_column,
)


def _write_pair(tmp_path: Path, canonical_body: str, game_body: str) -> tuple[Path, Path]:
    canon = tmp_path / "heroes-canonical.csv"
    game = tmp_path / "heroes-game.csv"
    canon.write_text(canonical_body, encoding="utf-8")
    game.write_text(game_body, encoding="utf-8")
    return canon, game


def test_heroes_resolution_ok_when_cardname_maps_to_row_canonical_id(
    tmp_path: Path,
) -> None:
    """Matching canonical roster + game CardName yields no alerts."""
    canon, game = _write_pair(
        tmp_path,
        "CanonicalId|CanonicalSlug|CanonicalHero\n" "CNmatchhash1|bravo|Bravo\n",
        "HeroGameId|CardName|CanonicalId\n"
        "HGignored111|Bravo|CNmatchhash1\n"
        "HGignored222|Bravo, Showstopper|CNmatchhash1\n",
    )
    assert _check_heroes_game_cardname_resolution(canon, game) == []


def test_heroes_resolution_alerts_when_canonical_id_wrong_for_cardname(
    tmp_path: Path,
) -> None:
    """Drift between resolution and stored CanonicalId is reported."""
    canon, game = _write_pair(
        tmp_path,
        "CanonicalId|CanonicalSlug|CanonicalHero\n" "CNmatchhash1|bravo|Bravo\n",
        "HeroGameId|CardName|CanonicalId\n" "HGignored111|Bravo|CNwrongwrong1\n",
    )
    alerts = _check_heroes_game_cardname_resolution(canon, game)
    assert len(alerts) == 1
    assert "Bravo" in alerts[0] and "CNmatchhash1" in alerts[0] and "CNwrongwrong1" in alerts[0]


def test_heroes_game_young_hero_column_ok(tmp_path: Path) -> None:
    """YoungHero true/false passes validation."""
    game = tmp_path / "heroes-game.csv"
    game.write_text(
        "HeroGameId|CardName|CanonicalId|YoungHero\n" "HG1|Bravo|CNx|true\n" "HG2|Bravo, Showstopper|CNx|false\n",
        encoding="utf-8",
    )
    assert _check_heroes_game_young_hero_column(game) == []


def test_heroes_game_young_hero_column_rejects_bad_value(tmp_path: Path) -> None:
    """Non-boolean YoungHero is flagged."""
    game = tmp_path / "heroes-game.csv"
    game.write_text(
        "HeroGameId|CardName|CanonicalId|YoungHero\n" "HG1|Bravo|CNx|yes\n",
        encoding="utf-8",
    )
    alerts = _check_heroes_game_young_hero_column(game)
    assert len(alerts) == 1
    assert "YoungHero" in alerts[0] and "yes" in alerts[0]


# ---------------------------------------------------------------------------
# A name before the comma shared by several canonical heroes (Arakni)
# ---------------------------------------------------------------------------

_ARAKNI_ALIASES = {
    "arakni": "arakni-huntsman",
    "araknihuntsman": "arakni-huntsman",
    "araknimarionette": "arakni-web-of-deceit",
}
_ARAKNI_GAME = (
    "HeroGameId|CardName|CanonicalId\n"
    "HG1|Arakni|CNhuntsman\n"
    "HG2|Arakni, Huntsman|CNhuntsman\n"
    "HG3|Arakni, Marionette|CNwebofdeceit\n"
)


def test_shared_hero_name_passes_when_every_card_has_a_full_title_alias(tmp_path: Path) -> None:
    game = tmp_path / "heroes-game.csv"
    game.write_text(_ARAKNI_GAME, encoding="utf-8")
    assert _check_heroes_game_ambiguous_card_names(game, _ARAKNI_ALIASES) == []


def test_new_card_of_a_shared_hero_name_without_a_full_title_alias_alerts(tmp_path: Path) -> None:
    """The generator would hand 'Arakni, Something' to Huntsman via the pre-comma alias."""
    game = tmp_path / "heroes-game.csv"
    game.write_text(_ARAKNI_GAME + "HG4|Arakni, Something|CNhuntsman\n", encoding="utf-8")
    alerts = _check_heroes_game_ambiguous_card_names(game, _ARAKNI_ALIASES)
    assert len(alerts) == 1
    assert "row 5" in alerts[0] and "'Arakni, Something'" in alerts[0]
    assert "hero-card-name-aliases.csv" in alerts[0]


def test_a_name_held_by_one_canonical_hero_needs_no_full_title_alias(tmp_path: Path) -> None:
    game = tmp_path / "heroes-game.csv"
    game.write_text(
        "HeroGameId|CardName|CanonicalId\n" "HG1|Bravo|CNbravo\n" "HG2|Bravo, Showstopper|CNbravo\n",
        encoding="utf-8",
    )
    assert _check_heroes_game_ambiguous_card_names(game, {}) == []


def test_committed_hero_cards_of_shared_names_all_have_full_title_aliases() -> None:
    game = Path(__file__).resolve().parents[1] / "src" / "data" / "csv" / "heroes-game.csv"
    assert _check_heroes_game_ambiguous_card_names(game) == []
