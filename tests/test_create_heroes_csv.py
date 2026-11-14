"""Tests for helpers in :mod:`create_heroes_csv`."""

from __future__ import annotations

import sqlite3

from create_heroes_csv import (
    HEROES_CANONICAL_CSV_PATH,
    HEROES_GAME_CSV_PATH,
    dedupe_printings,
    hero_printing_rows,
    resolve_card_canonical_slug,
    sort_like_db_export,
    split_name_variant,
)
from hero_overrides import load_canonical_hero_card_name_aliases
from pipe_csv_io import read_pipe_csv
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


def _real_roster_index() -> dict[str, str]:
    """``normalize_name(CanonicalHero) -> CanonicalSlug`` from the committed roster, first row wins."""
    _, rows = read_pipe_csv(HEROES_CANONICAL_CSV_PATH)
    index: dict[str, str] = {}
    for row in rows:
        index.setdefault(normalize_name(row["CanonicalHero"]), row["CanonicalSlug"])
    return index


def test_arakni_forms_resolve_to_distinct_slugs() -> None:
    """Arakni's forms are distinct characters and must not collapse to one slug.

    The forms share the name before the comma, so only the full printed title
    can tell them apart; those full-name rows live in the alias CSV.
    """
    roster = _real_roster_index()
    aliases = load_canonical_hero_card_name_aliases()
    cases = {
        "Arakni, Marionette": "arakni-web-of-deceit",
        "Arakni, Web of Deceit": "arakni-web-of-deceit",
        "Arakni, Solitary Confinement": "arakni-solitary-confinement",
        "Arakni, 5L!p3d 7hRu 7h3 cR4X": "arakni-solitary-confinement",
        "Arakni, Huntsman": "arakni-huntsman",
        "Arakni": "arakni-huntsman",
    }
    for card_name, expected in cases.items():
        assert resolve_card_canonical_slug(card_name, roster, aliases) == expected, card_name


def test_full_card_name_alias_wins_over_the_name_before_the_comma() -> None:
    """A full-title alias beats both a pre-comma alias and the roster index."""
    roster = {"ira": "ira"}
    aliases = {"ira": "ira-old", "iracrimsonhaze": "ira-crimson"}
    assert resolve_card_canonical_slug("Ira, Crimson Haze", roster, aliases) == "ira-crimson"
    assert resolve_card_canonical_slug("Ira, Scarlet Revenger", roster, aliases) == "ira-old"


def test_pre_comma_alias_wins_over_the_roster_index() -> None:
    """``Ser Boltyn, Breaker of Dawn`` routes through the alias to ``boltyn``."""
    roster = {"serboltyn": "wrong", "boltyn": "boltyn"}
    aliases = {"serboltyn": "boltyn"}
    assert resolve_card_canonical_slug("Ser Boltyn, Breaker of Dawn", roster, aliases) == "boltyn"


def test_unknown_hero_falls_back_to_the_normalised_name() -> None:
    """A name in neither table resolves to its own normalised key."""
    assert resolve_card_canonical_slug("Bravo, Showstopper", {"bravo": "bravo"}, {}) == "bravo"
    assert resolve_card_canonical_slug("Nobody, Nowhere", {}, {}) == "nobody"


def test_every_committed_game_row_resolves_to_its_canonical_id() -> None:
    """Characterisation: the resolver reproduces every committed ``heroes-game.csv`` link."""
    roster = _real_roster_index()
    aliases = load_canonical_hero_card_name_aliases()
    _, canonical_rows = read_pipe_csv(HEROES_CANONICAL_CSV_PATH)
    id_by_slug = {row["CanonicalSlug"]: row["CanonicalId"] for row in canonical_rows}
    _, game_rows = read_pipe_csv(HEROES_GAME_CSV_PATH)
    assert game_rows
    for row in game_rows:
        slug = resolve_card_canonical_slug(row["CardName"], roster, aliases)
        assert id_by_slug.get(slug) == row["CanonicalId"], row["CardName"]


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
        {"HeroGameId": "HGb", "SetId": "MPA", "CardId": "MPA003", "Rarity": "V", "PrintingUniqueId": "p4"},
        {"HeroGameId": "HGa", "SetId": "WIN", "CardId": "WIN050", "Rarity": "P", "PrintingUniqueId": "p1"},
        {"HeroGameId": "HGb", "SetId": "MPA", "CardId": "MPA002", "Rarity": "B", "PrintingUniqueId": "p2"},
        {"HeroGameId": "HGa", "SetId": "SUP", "CardId": "SUP001", "Rarity": "B", "PrintingUniqueId": "p3"},
        # one card id, three printings: the printing id breaks the tie
        {
            "HeroGameId": "HGc",
            "SetId": "EVR",
            "CardId": "EVR017",
            "Rarity": "M",
            "PrintingUniqueId": "nRMnPD6nnmCpFf7WkwTN7",
        },
        {
            "HeroGameId": "HGc",
            "SetId": "EVR",
            "CardId": "EVR017",
            "Rarity": "M",
            "PrintingUniqueId": "FKC8qdBgdwgfrLmkq8htq",
        },
        {
            "HeroGameId": "HGc",
            "SetId": "EVR",
            "CardId": "EVR017",
            "Rarity": "M",
            "PrintingUniqueId": "DFjQGNbTkNqjWhJPFL78C",
        },
    ]
    canonical = [
        {"CanonicalId": "CN2", "CanonicalSlug": "zane", "CanonicalHero": "Zane"},
        {"CanonicalId": "CN1", "CanonicalSlug": "dr-mortimer", "CanonicalHero": "Dr. Mortimer"},
        {"CanonicalId": "CN3", "CanonicalSlug": "arakni-huntsman", "CanonicalHero": "Arakni"},
    ]

    sorted_game, sorted_printings, sorted_canonical = sort_like_db_export(game, printings, canonical)

    assert sorted_game == _sqlite_order(["HeroGameId", "CardName"], game, "CardName")
    assert sorted_printings == _sqlite_order(
        ["HeroGameId", "SetId", "CardId", "Rarity", "PrintingUniqueId"],
        printings,
        "HeroGameId, SetId, CardId, PrintingUniqueId",
    )
    assert sorted_canonical == _sqlite_order(
        ["CanonicalId", "CanonicalSlug", "CanonicalHero"], canonical, "CanonicalSlug"
    )


def test_dedupe_printings_keeps_a_marvel_beside_its_base_printing() -> None:
    """``heroes_printings`` is keyed on (HeroGameId, PrintingUniqueId).

    Upstream lists Tuffnut's Marvels under the same card id as the base printing
    (SUP002 is ``B`` once and ``V`` twice). Each is a separate printing with its
    own image, so all three are kept; only a repeated printing id collapses.
    """
    base = {"HeroGameId": "HG042046d307", "SetId": "SUP", "CardId": "SUP002"}
    rows = [
        {**base, "PrintingUniqueId": "krkbfC6CQFhfPmGtCHN6R", "Rarity": "B"},
        {**base, "PrintingUniqueId": "pC8KwqFWtpwKbddzTHffz", "Rarity": "V"},
        {**base, "PrintingUniqueId": "tFMDn6HF7gcKqQjj8kWnq", "Rarity": "V"},
        {**base, "PrintingUniqueId": "tFMDn6HF7gcKqQjj8kWnq", "Rarity": "V"},
    ]

    kept = dedupe_printings(rows)

    assert sorted((r["PrintingUniqueId"], r["Rarity"]) for r in kept) == [
        ("krkbfC6CQFhfPmGtCHN6R", "B"),
        ("pC8KwqFWtpwKbddzTHffz", "V"),
        ("tFMDn6HF7gcKqQjj8kWnq", "V"),
    ]


def _upstream_printing(unique_id: str, set_id: str, card_id: str, rarity: str, foiling: str, art: str, artists: str):
    """One ``card-printing.csv`` row, keyed by the upstream column names."""
    return {
        "Unique ID": unique_id,
        "Card ID": card_id,
        "Set ID": set_id,
        "Rarity": rarity,
        "Foiling": foiling,
        "Art Variations": art,
        "Artists": artists,
    }


def test_every_upstream_printing_becomes_its_own_row() -> None:
    """Bravo, Star of the Show (EVR017) has three printings under one card id:
    the rainbow-foil standard, the cold foil, and the cold-foil full art. Each
    has its own image, so each is its own row, carrying its printing id."""
    upstream = [
        _upstream_printing("FKC8qdBgdwgfrLmkq8htq", "EVR", "EVR017", "M", "S", "", "Marco Wulfr"),
        _upstream_printing("DFjQGNbTkNqjWhJPFL78C", "EVR", "EVR017", "M", "C", "", "Marco Wulfr"),
        _upstream_printing("nRMnPD6nnmCpFf7WkwTN7", "EVR", "EVR017", "M", "C", "FA", "Marco Wulfr"),
    ]

    assert hero_printing_rows("HG871c3ec849", upstream) == [
        {
            "HeroGameId": "HG871c3ec849",
            "PrintingUniqueId": "FKC8qdBgdwgfrLmkq8htq",
            "SetId": "EVR",
            "CardId": "EVR017",
            "Rarity": "M",
            "Foiling": "S",
            "ArtVariation": "",
            "Artist": "Marco Wulfr",
        },
        {
            "HeroGameId": "HG871c3ec849",
            "PrintingUniqueId": "DFjQGNbTkNqjWhJPFL78C",
            "SetId": "EVR",
            "CardId": "EVR017",
            "Rarity": "M",
            "Foiling": "C",
            "ArtVariation": "",
            "Artist": "Marco Wulfr",
        },
        {
            "HeroGameId": "HG871c3ec849",
            "PrintingUniqueId": "nRMnPD6nnmCpFf7WkwTN7",
            "SetId": "EVR",
            "CardId": "EVR017",
            "Rarity": "M",
            "Foiling": "C",
            "ArtVariation": "FA",
            "Artist": "Marco Wulfr",
        },
    ]
