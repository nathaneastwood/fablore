"""Tests for the ``heroes-printings.csv`` round trip through the database.

``heroes-printings.csv`` has two writers: ``create_heroes_csv.py`` and
``db.export_to_csv()``. Whatever the generator writes must come back out of
seed -> export unchanged, or every ``create_stories_index.py`` run silently
rewrites the file.
"""

from __future__ import annotations

from pathlib import Path

import db._export as _export
from db import Database
from db._seed import seed_from_csvs

_BANNER = "# AUTO-GENERATED FILE — do not edit by hand. Regenerate with: python3 src/data/create_heroes_csv.py"

_PRINTINGS = [
    "HeroGameId|SetId|CardId|Rarity|PrintingUniqueId|Foiling|ArtVariation|Artist",
    "HG871c3ec849|EVR|EVR017|M|DFjQGNbTkNqjWhJPFL78C|C||Marco Wulfr",
    "HG871c3ec849|EVR|EVR017|M|FKC8qdBgdwgfrLmkq8htq|S||Marco Wulfr",
    "HG871c3ec849|EVR|EVR017|M|nRMnPD6nnmCpFf7WkwTN7|C|FA|Marco Wulfr",
]


def _write(path: Path, lines: list[str]) -> None:
    path.write_text("\n".join([_BANNER, *lines]) + "\n", encoding="utf-8")


def test_seed_then_export_keeps_every_printing_of_one_card(tmp_path: Path) -> None:
    """Bravo, Star of the Show's three EVR017 printings share a card id and
    differ by printing id, foiling and art variation. All three survive the
    database, with every column intact."""
    src = tmp_path / "src"
    (src / "csv").mkdir(parents=True)
    _write(
        src / "csv" / "heroes-canonical.csv", ["CanonicalId|CanonicalSlug|CanonicalHero", "CN962665711e|bravo|Bravo"]
    )
    _write(
        src / "csv" / "heroes-game.csv",
        [
            "HeroGameId|CardName|CanonicalId|ClassIds|TalentIds|Health|Intellect|AbilityText|YoungHero",
            "HG871c3ec849|Bravo, Star of the Show|CN962665711e|||40|4||false",
        ],
    )
    _write(src / "csv" / "heroes-printings.csv", _PRINTINGS)

    db = Database(":memory:", data_dir=src)
    seed_from_csvs(db.conn, src)
    out = tmp_path / "out"
    _export.export_all(db.conn, out)

    exported = (out / "csv" / "heroes-printings.csv").read_text(encoding="utf-8").splitlines()
    assert [line for line in exported if line and not line.startswith("#")] == _PRINTINGS
