"""Tests for :func:`create_heroes_csv.living_legend_rows`.

One seam: the parsed fabtcg.com hero API JSON (a committed fixture, no
network) plus the game/canonical rows and the optional upstream
``living-legend-cc.csv`` rows in, ``heroes-ll.csv`` rows out.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from create_heroes_csv import living_legend_rows

_API = json.loads((Path(__file__).parent / "fixtures" / "fabtcg-heroes-api.json").read_text(encoding="utf-8"))

_CANONICAL = [
    {"CanonicalId": "CN_BRAVO", "CanonicalSlug": "bravo", "CanonicalHero": "Bravo"},
    {"CanonicalId": "CN_CINDRA", "CanonicalSlug": "cindra", "CanonicalHero": "Cindra"},
    {"CanonicalId": "CN_ENIGMA", "CanonicalSlug": "enigma", "CanonicalHero": "Enigma"},
    {"CanonicalId": "CN_MAXX", "CanonicalSlug": "maxx", "CanonicalHero": "Maxx 'The Hype' Nitro"},
    {"CanonicalId": "CN_OSCILIO", "CanonicalSlug": "oscilio", "CanonicalHero": "Oscilio"},
    {"CanonicalId": "CN_DORI", "CanonicalSlug": "dorinthea", "CanonicalHero": "Dorinthea"},
    {"CanonicalId": "CN_FAI", "CanonicalSlug": "fai", "CanonicalHero": "Fai"},
    {"CanonicalId": "CN_ZYGGY", "CanonicalSlug": "zyggy", "CanonicalHero": "Zyggy"},
]

_GAME = [
    {"CardName": name, "CanonicalId": cid, "YoungHero": young}
    for name, cid, young in [
        ("Bravo", "CN_BRAVO", "true"),
        ("Bravo, Showstopper", "CN_BRAVO", "false"),
        ("Bravo, Star of the Show", "CN_BRAVO", "false"),
        ("Cindra", "CN_CINDRA", "true"),
        ("Cindra, Dracai of Retribution", "CN_CINDRA", "false"),
        ("Enigma, Ledger of Ancestry", "CN_ENIGMA", "false"),
        ("Maxx 'The Hype' Nitro", "CN_MAXX", "false"),
        ("Oscilio, Constella Intelligence", "CN_OSCILIO", "false"),
        ("Oscilio, Forked Continuum", "CN_OSCILIO", "false"),
        ("Dorinthea Ironsong", "CN_DORI", "false"),
        ("Fai", "CN_FAI", "true"),
        ("Fai, Rising Rebellion", "CN_FAI", "false"),
        ("Zyggy Starlight", "CN_ZYGGY", "false"),
    ]
]

_UPSTREAM_CC = [
    {
        "Card Name": "Bravo, Star of the Show",
        "Status Active": "Yes",
        "Date In Effect": "2022-06-24T00:00:00.000Z",
    },
]


def test_a_cc_living_legend_from_the_api_takes_its_date_from_the_upstream_list():
    rows = living_legend_rows(_API, _GAME, _CANONICAL, _UPSTREAM_CC)
    assert {
        "CanonicalSlug": "bravo",
        "CardName": "Bravo, Star of the Show",
        "Format": "CC",
        "DateInEffect": "2022-06-24",
    } in rows


def test_heroes_still_legal_in_cc_below_1000_points_or_unreleased_are_not_living_legends():
    rows = living_legend_rows(_API, _GAME, _CANONICAL, _UPSTREAM_CC)
    names = {row["CardName"] for row in rows}
    assert names.isdisjoint(
        {"Bravo, Showstopper", "Oscilio, Forked Continuum", "Dorinthea Ironsong", "Zyggy Starlight"}
    )


def test_a_living_legend_with_no_matching_adult_card_fails_and_names_the_hero():
    stranger = {
        "slug": "nobody-unknown",
        "title": "Nobody",
        "subtitle": "Unknown",
        "type": "adult",
        "is_released": "yes",
        "status": "1100",
        "format": {"cc": {"status": "not_legal"}, "living-legend": {"status": "legal"}},
    }
    api = {"heroes": [*_API["heroes"], stranger]}
    with pytest.raises(ValueError, match="Nobody, Unknown"):
        living_legend_rows(api, _GAME, _CANONICAL, _UPSTREAM_CC)


def test_a_young_hero_in_the_api_is_never_reported():
    rows = living_legend_rows(_API, _GAME, _CANONICAL, _UPSTREAM_CC)
    assert "Fai" not in {row["CardName"] for row in rows}


def test_a_hero_with_adult_and_young_cards_is_reported_on_the_adult_card_with_no_date_when_upstream_has_none():
    rows = living_legend_rows(_API, _GAME, _CANONICAL, _UPSTREAM_CC)
    assert {
        "CanonicalSlug": "cindra",
        "CardName": "Cindra, Dracai of Retribution",
        "Format": "CC",
        "DateInEffect": "",
    } in rows


def test_api_names_that_differ_from_the_card_in_case_or_quotes_still_carry_the_printed_card_name():
    rows = living_legend_rows(_API, _GAME, _CANONICAL, _UPSTREAM_CC)
    names = {row["CardName"] for row in rows}
    assert {"Enigma, Ledger of Ancestry", "Maxx 'The Hype' Nitro"} <= names


def test_an_upstream_entry_superseded_by_a_later_inactive_one_gives_no_date():
    upstream = [
        {
            "Card Name": "Oscilio, Constella Intelligence",
            "Status Active": "Yes",
            "Date In Effect": "2025-01-10T00:00:00.000Z",
        },
        {
            "Card Name": "Oscilio, Constella Intelligence",
            "Status Active": "No",
            "Date In Effect": "2025-06-01T00:00:00.000Z",
        },
    ]
    rows = living_legend_rows(_API, _GAME, _CANONICAL, upstream)
    assert {
        "CanonicalSlug": "oscilio",
        "CardName": "Oscilio, Constella Intelligence",
        "Format": "CC",
        "DateInEffect": "",
    } in rows
