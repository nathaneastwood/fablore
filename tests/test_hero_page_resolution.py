"""Which page a canonical hero resolves to, over the committed data.

A canonical hero is one lore character; its cards (Adult, Young, later forms) are
``heroes-game.csv`` rows pointing at it. Each canonical hero has at most one
``heroes-of-rathe/*-about.md`` page: ``{slug}-about.md`` by default, or the
``hero_overrides.HERO_SLUG_LORE_FILE_OVERRIDES`` path (the three Arakni).
"""

from __future__ import annotations

from collections import Counter
from pathlib import Path

from hero_overrides import HERO_SLUG_LORE_FILE_OVERRIDES
from mdbook_common import read_rows
from mdbook_related import resolve_hero_src_path

SRC = Path(__file__).resolve().parents[1] / "src"

# What resolve_hero_src_path answered for every canonical hero before the
# ``{slug}.md`` probe was deleted (file names under heroes-of-rathe/).
_PAGES = {
    "arakni-huntsman": "arakni-about.md",
    "arakni-solitary-confinement": "arakni-5l!p3d-7hru-7h3-cr4x-about.md",
    "arakni-web-of-deceit": "arakni-marionette-about.md",
    "aurora": "aurora-about.md",
    "azalea": "azalea-about.md",
    "baalghor": "baalghor-about.md",
    "benji": "benji-about.md",
    "betsy": "betsy-about.md",
    "blaze": "blaze-about.md",
    "boltyn": "boltyn-about.md",
    "bravo": "bravo-about.md",
    "brevant": "brevant-about.md",
    "briar": "briar-about.md",
    "chane": "chane-about.md",
    "cindra": "cindra-about.md",
    "dash": "dash-about.md",
    "data-doll-mkii": "data-doll-mkii-about.md",
    "dorinthea": "dorinthea-about.md",
    "dr-mortimer": "dr-mortimer-about.md",
    "dromai": "dromai-about.md",
    "emperor": "emperor-about.md",
    "enigma": "enigma-about.md",
    "fai": "fai-about.md",
    "fang": "fang-about.md",
    "florian": "florian-about.md",
    "frankie": "frankie-about.md",
    "genis": "genis-about.md",
    "gravy": "gravy-about.md",
    "hala": "hala-about.md",
    "ira": "ira-about.md",
    "iyslander": "iyslander-about.md",
    "jarl": "jarl-about.md",
    "kano": "kano-about.md",
    "kassai": "kassai-about.md",
    "katsu": "katsu-about.md",
    "kavdaen": "kavdaen-about.md",
    "kayo": "kayo-about.md",
    "killjoy": "killjoy-about.md",
    "levia": "levia-about.md",
    "lexi": "lexi-about.md",
    "lyath": "lyath-about.md",
    "malice": "malice-about.md",
    "marlynn": "marlynn-about.md",
    "maxx": "maxx-about.md",
    "melody": "melody-about.md",
    "nuu": "nuu-about.md",
    "oldhim": "oldhim-about.md",
    "olympia": "olympia-about.md",
    "oscilio": "oscilio-about.md",
    "pleiades": "pleiades-about.md",
    "prism": "prism-about.md",
    "puffin": "puffin-about.md",
    "rhinar": "rhinar-about.md",
    "riptide": "riptide-about.md",
    "scurv": "scurv-about.md",
    "shiyana": "shiyana-about.md",
    "teklovossen": "teklovossen-about.md",
    "terra": "terra-about.md",
    "tuffnut": "tuffnut-about.md",
    "uzuri": "uzuri-about.md",
    "valda": "valda-about.md",
    "verdance": "verdance-about.md",
    "victor-goldmane": "victor-goldmane-about.md",
    "viserai": "viserai-about.md",
    "vynnset": "vynnset-about.md",
    "yoji": "yoji-about.md",
    "zane": "zane-about.md",
    "zen": "zen-about.md",
    "zyggy": "zyggy-about.md",
}
_NO_PAGE = {
    "bolfar",
    "brutus",
    "crix",
    "kox",
    "reya",
    "ruudi",
    "squizzyfloof",
    "taipanis",
    "taylor",
    "the-librarian",
    "theryon",
    "yorick",
}


def _canonical_slugs() -> list[str]:
    return [r["CanonicalSlug"].strip() for r in read_rows(SRC / "data" / "csv" / "heroes-canonical.csv")]


def _resolutions() -> dict[str, str | None]:
    return {slug: resolve_hero_src_path(SRC, slug) for slug in _canonical_slugs()}


def test_every_canonical_hero_resolves_as_pinned() -> None:
    expected = {slug: f"heroes-of-rathe/{name}" for slug, name in _PAGES.items()}
    expected.update({slug: None for slug in _NO_PAGE})
    assert _resolutions() == expected


def test_every_hero_about_page_belongs_to_exactly_one_canonical_hero() -> None:
    claimed = Counter(p for p in _resolutions().values() if p)
    pages = {f"heroes-of-rathe/{p.name}" for p in (SRC / "heroes-of-rathe").glob("*-about.md")}
    assert set(claimed) == pages
    assert [p for p, n in claimed.items() if n > 1] == []


def test_every_override_target_is_an_existing_about_page() -> None:
    slugs = set(_canonical_slugs())
    for slug, target in HERO_SLUG_LORE_FILE_OVERRIDES.items():
        assert slug in slugs, slug
        assert target.startswith("heroes-of-rathe/") and target.endswith("-about.md"), target
        assert (SRC / target).is_file(), target
