"""Tests for hero CardName vs CanonicalId resolution in :mod:`validate_data`."""

from __future__ import annotations

from pathlib import Path

from validate_data import _check_heroes_game_cardname_resolution


def _write_pair(tmp_path: Path, canonical_body: str, game_body: str) -> tuple[Path, Path]:
    canon = tmp_path / "heroes-canonical.csv"
    game = tmp_path / "heroes-game.csv"
    canon.write_text(canonical_body, encoding="utf-8")
    game.write_text(game_body, encoding="utf-8")
    return canon, game


def test_heroes_resolution_ok_when_cardname_maps_to_row_canonical_id(tmp_path: Path) -> None:
    """Matching canonical roster + game CardName yields no alerts."""
    canon, game = _write_pair(
        tmp_path,
        "CanonicalId|CanonicalSlug|CanonicalHero\n"
        "CNmatchhash1|bravo|Bravo\n",
        "HeroGameId|CardName|CanonicalId\n"
        "HGignored111|Bravo|CNmatchhash1\n"
        "HGignored222|Bravo, Showstopper|CNmatchhash1\n",
    )
    assert _check_heroes_game_cardname_resolution(canon, game) == []


def test_heroes_resolution_alerts_when_canonical_id_wrong_for_cardname(tmp_path: Path) -> None:
    """Drift between resolution and stored CanonicalId is reported."""
    canon, game = _write_pair(
        tmp_path,
        "CanonicalId|CanonicalSlug|CanonicalHero\n"
        "CNmatchhash1|bravo|Bravo\n",
        "HeroGameId|CardName|CanonicalId\n"
        "HGignored111|Bravo|CNwrongwrong1\n",
    )
    alerts = _check_heroes_game_cardname_resolution(canon, game)
    assert len(alerts) == 1
    assert "Bravo" in alerts[0] and "CNmatchhash1" in alerts[0] and "CNwrongwrong1" in alerts[0]
