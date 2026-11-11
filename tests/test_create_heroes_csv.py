"""Tests for helpers in :mod:`create_heroes_csv`."""

from __future__ import annotations

import sqlite3

from create_heroes_csv import (
    apply_lore_canonical_override,
    dedupe_printings,
    sort_like_db_export,
    split_name_variant,
)
from registry_ids import make_hash_id
from text_utils import normalize_name


def test_normalize_name_folds_to_alnum() -> None:
    """Non-alphanumeric characters are removed for matching keys."""
    assert normalize_name("Ser Boltyn") == "serboltyn"


def test_split_name_variant() -> None:
    """Printed titles split on the first comma."""
    name, sub = split_name_variant("Ira, Crimson Haze")
    assert name == "Ira"
    assert sub == "Crimson Haze"


def test_make_hash_id_deterministic() -> None:
    """Same input yields the same id prefix and length."""
    a = make_hash_id("HG", "stable-key")
    b = make_hash_id("HG", "stable-key")
    assert a == b
    assert a.startswith("HG")
    assert len(a) == len("HG") + 10


def test_lore_canonical_override_splits_arakni_forms() -> None:
    """Arakni's forms are distinct characters and must not collapse to one slug.

    The override table is keyed by the base hero name, but the caller passes a
    ``base_slug`` that has already been resolved through the roster's name index
    — for Arakni that is ``arakni-huntsman``, not ``arakni``. Looking up only the
    resolved slug silently routed every Arakni card to the Huntsman.
    """
    cases = {
        "Arakni, Marionette": "arakni-web-of-deceit",
        "Arakni, Web of Deceit": "arakni-web-of-deceit",
        "Arakni, Solitary Confinement": "arakni-solitary-confinement",
        "Arakni, 5L!p3d 7hRu 7h3 cR4X": "arakni-solitary-confinement",
        "Arakni, Huntsman": "arakni-huntsman",
        "Arakni": "arakni-huntsman",
    }
    for card_name, expected in cases.items():
        name, variant = split_name_variant(card_name)
        assert apply_lore_canonical_override("arakni-huntsman", name, variant) == expected, card_name


def test_lore_canonical_override_passes_through_unknown_heroes() -> None:
    """A hero with no override table keeps the slug it was resolved to."""
    assert apply_lore_canonical_override("bravo", "Bravo", "Showstopper") == "bravo"


def _sqlite_order(columns: list[str], rows: list[dict[str, str]], order_by: str) -> list[dict[str, str]]:
    """Return ``rows`` in the order SQLite's ``ORDER BY`` puts them (default BINARY collation)."""
    conn = sqlite3.connect(":memory:")
    conn.execute(f"CREATE TABLE t ({', '.join(f'{c} TEXT' for c in columns)})")
    conn.executemany(
        f"INSERT INTO t VALUES ({', '.join('?' for _ in columns)})",
        [[r[c] for c in columns] for r in rows],
    )
    ordered = conn.execute(f"SELECT {', '.join(columns)} FROM t ORDER BY {order_by}").fetchall()
    return [dict(zip(columns, values)) for values in ordered]


def test_generator_rows_follow_the_db_export_order() -> None:
    """The generator and ``db.export_to_csv()`` both write the hero CSVs.

    If their row orders differ, every run of one after the other reorders the whole
    file, and the line diff hides the real changes. The orders must match the
    ``ORDER BY`` clauses in ``db/_queries.py`` exactly — including SQLite's
    case-sensitive BINARY collation, which ``str.lower()`` would break.
    """
    game = [
        {"HeroGameId": "HG3", "CardName": "Arakni, Huntsman"},
        {"HeroGameId": "HG1", "CardName": "Ira, Crimson Haze"},
        {"HeroGameId": "HG4", "CardName": "Arakni, 5L!p3d 7hRu 7h3 cR4X"},
        {"HeroGameId": "HG2", "CardName": "Arakni"},
        {"HeroGameId": "HG5", "CardName": "arakni lowercase"},
        {"HeroGameId": "HG6", "CardName": "Dr. Mortimer"},
    ]
    printings = [
        {"HeroGameId": "HGb", "SetId": "MPA", "CardId": "MPA003", "Rarity": "V"},
        {"HeroGameId": "HGa", "SetId": "WIN", "CardId": "WIN050", "Rarity": "P"},
        {"HeroGameId": "HGb", "SetId": "MPA", "CardId": "MPA002", "Rarity": "B"},
        {"HeroGameId": "HGa", "SetId": "SUP", "CardId": "SUP001", "Rarity": "B"},
    ]
    canonical = [
        {"CanonicalId": "CN2", "CanonicalSlug": "zane", "CanonicalHero": "Zane"},
        {"CanonicalId": "CN1", "CanonicalSlug": "dr-mortimer", "CanonicalHero": "Dr. Mortimer"},
        {"CanonicalId": "CN3", "CanonicalSlug": "arakni-huntsman", "CanonicalHero": "Arakni"},
    ]

    sorted_game, sorted_printings, sorted_canonical = sort_like_db_export(game, printings, canonical)

    assert sorted_game == _sqlite_order(["HeroGameId", "CardName"], game, "CardName")
    assert sorted_printings == _sqlite_order(
        ["HeroGameId", "SetId", "CardId", "Rarity"], printings, "HeroGameId, SetId, CardId"
    )
    assert sorted_canonical == _sqlite_order(
        ["CanonicalId", "CanonicalSlug", "CanonicalHero"], canonical, "CanonicalSlug"
    )


def test_dedupe_printings_keeps_one_row_per_db_key() -> None:
    """``heroes_printings`` is keyed on (HeroGameId, SetId, CardId), not rarity.

    Upstream lists a Marvel printing under the same card id as the base one
    (SUP002 is both ``B`` and ``V``). Writing both made every generator run add a
    row that the next DB export dropped again. The base rarity is the one kept,
    whichever order upstream lists them in.
    """
    rows = [
        {"HeroGameId": "HGa", "SetId": "SUP", "CardId": "SUP002", "Rarity": "V"},
        {"HeroGameId": "HGa", "SetId": "SUP", "CardId": "SUP002", "Rarity": "B"},
        {"HeroGameId": "HGa", "SetId": "IAR", "CardId": "IAR106", "Rarity": "T"},
        {"HeroGameId": "HGa", "SetId": "IAR", "CardId": "IAR106", "Rarity": "V"},
        {"HeroGameId": "HGb", "SetId": "MPA", "CardId": "MPA003", "Rarity": "V"},
        {"HeroGameId": "HGb", "SetId": "HER", "CardId": "HER150", "Rarity": "P"},
    ]

    kept = dedupe_printings(rows)

    assert sorted((r["HeroGameId"], r["CardId"], r["Rarity"]) for r in kept) == [
        ("HGa", "IAR106", "T"),
        ("HGa", "SUP002", "B"),
        ("HGb", "HER150", "P"),
        ("HGb", "MPA003", "V"),  # a Marvel-only printing is still a printing
    ]
