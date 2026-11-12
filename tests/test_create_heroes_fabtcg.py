"""Tests for :func:`create_heroes_csv.fabtcg_hero_rows`.

One seam: the parsed fabtcg.com hero API JSON (a committed fixture trimmed from
the live response, no network) plus the ``heroes-game.csv`` rows in,
``heroes-fabtcg.csv`` rows out.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from create_heroes_csv import fabtcg_hero_rows

_API = json.loads((Path(__file__).parent / "fixtures" / "fabtcg-heroes-api-detail.json").read_text(encoding="utf-8"))

_GAME = [
    {"CardName": name, "YoungHero": young}
    for name, young in [
        ("Arakni, 5L!p3d 7hRu 7h3 cR4X", "false"),
        ("Arakni, Solitary Confinement", "true"),
        ("Aurora", "true"),
        ("Aurora, Shooting Star", "false"),
        ("Dash I/O", "false"),
        ("Dr. Mortimer, Blight of the Pits", "false"),
        ("Jarl Vetreiði", "false"),
        ("Maxx 'The Hype' Nitro", "false"),
        ("Valda Brightaxe", "true"),
        ("Valda, Seismic Impact", "false"),
    ]
]


def _row(card_name: str) -> dict[str, str]:
    rows = {row["CardName"]: row for row in fabtcg_hero_rows(_API, _GAME)}
    return rows[card_name]


def test_a_released_hero_is_keyed_by_its_printed_card_name_with_link_difficulty_portrait_and_playstyles():
    assert _row("Aurora, Shooting Star") == {
        "CardName": "Aurora, Shooting Star",
        "HeroPageLink": "https://fabtcg.com/hero/aurora-3/",
        "Difficulty": "1",
        "PortraitKey": "aurora-shooting-star",
        "Playstyles": "Aggressive",
    }


def test_an_unreleased_hero_with_no_page_gives_no_row():
    names = {row["CardName"] for row in fabtcg_hero_rows(_API, _GAME)}
    assert not any(name.startswith("Azalea") for name in names)


def test_disruption_is_folded_into_disruptive_and_a_half_point_difficulty_is_kept():
    row = _row("Dr. Mortimer, Blight of the Pits")
    assert (row["Playstyles"], row["Difficulty"]) == ("Disruptive, Midrange", "2.5")


def test_a_released_hero_with_no_matching_card_fails_and_names_the_hero():
    stranger = {"title": "Nobody", "subtitle": "Unknown", "link": "https://fabtcg.com/hero/nobody/"}
    with pytest.raises(ValueError, match="Nobody, Unknown"):
        fabtcg_hero_rows({"heroes": [*_API["heroes"], stranger]}, _GAME)


@pytest.mark.parametrize(
    ("card_name", "key"),
    [
        ("Dash I/O", "dash-i-o"),
        ("Jarl Vetreiði", "jarl-vetrei-i"),
        ("Arakni, 5L!p3d 7hRu 7h3 cR4X", "arakni-5l-p3d-7hru-7h3-cr4x"),
        ("Maxx 'The Hype' Nitro", "maxx-the-hype-nitro"),
    ],
)
def test_the_portrait_key_is_the_api_title_and_subtitle_as_the_cdn_names_it(card_name, key):
    assert _row(card_name)["PortraitKey"] == key


def test_a_card_with_no_api_entry_of_its_own_gets_no_row():
    """A young side the API folds into its adult hero is shown inside the adult's form."""
    names = {row["CardName"] for row in fabtcg_hero_rows(_API, _GAME)}
    assert names.isdisjoint({"Arakni, Solitary Confinement", "Valda Brightaxe", "Aurora"})
