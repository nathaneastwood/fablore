"""The hero card each H1 on a hero page resolves to, pinned against the real data.

Recorded from the old lookup (exact name, then a ``_HEADING_ALIASES`` table,
then ``str.lower()``) before headings were matched on
``text_utils.normalize_name``, so a change in which card a heading names shows
up here before it shows up in the build. Every H1 on every hero about-page is
listed, in page order; today all of them name a card.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from mdbook_common import is_hero_about_page
from mdbook_hero_meta import hero_forms, load_hero_data

SRC = Path(__file__).resolve().parent.parent / "src"

EXPECTED: dict[str, list[tuple[str, str]]] = {
    "heroes-of-rathe/arakni-5l!p3d-7hru-7h3-cr4x-about.md": [
        ("Arakni, 5l!p3d 7hru 7h3 Cr4x", "Arakni, 5L!p3d 7hRu 7h3 cR4X"),
    ],
    "heroes-of-rathe/arakni-about.md": [
        ("Arakni, Huntsman", "Arakni, Huntsman"),
    ],
    "heroes-of-rathe/arakni-marionette-about.md": [
        ("Arakni, Marionette", "Arakni, Marionette"),
    ],
    "heroes-of-rathe/aurora-about.md": [
        ("Aurora, Shooting Star", "Aurora, Shooting Star"),
        ("Aurora, Legacy of Tempest", "Aurora, Legacy of Tempest"),
    ],
    "heroes-of-rathe/azalea-about.md": [
        ("Azalea, Ace in the Hole", "Azalea, Ace in the Hole"),
    ],
    "heroes-of-rathe/baalghor-about.md": [
        ("Baalghor, Omen of the End", "Baalghor, Omen of the End"),
    ],
    "heroes-of-rathe/benji-about.md": [
        ("Benji, The Piercing Wind", "Benji, the Piercing Wind"),
    ],
    "heroes-of-rathe/betsy-about.md": [
        ("Betsy, Skin in the Game", "Betsy, Skin in the Game"),
    ],
    "heroes-of-rathe/blaze-about.md": [
        ("Blaze, Firemind", "Blaze, Firemind"),
    ],
    "heroes-of-rathe/boltyn-about.md": [
        ("Ser Boltyn, Breaker of Dawn", "Ser Boltyn, Breaker of Dawn"),
    ],
    "heroes-of-rathe/bravo-about.md": [
        ("Bravo, Showstopper", "Bravo, Showstopper"),
        ("Bravo, Star of the Show", "Bravo, Star of the Show"),
        ("Bravo, Flattering Showman", "Bravo, Flattering Showman"),
    ],
    "heroes-of-rathe/brevant-about.md": [
        ("Brevant, Civic Protector", "Brevant, Civic Protector"),
    ],
    "heroes-of-rathe/briar-about.md": [
        ("Briar, Warden of Thorns", "Briar, Warden of Thorns"),
    ],
    "heroes-of-rathe/chane-about.md": [
        ("Chane, Bound by Shadow", "Chane, Bound by Shadow"),
    ],
    "heroes-of-rathe/cindra-about.md": [
        ("Cindra, Dracai of Retribution", "Cindra, Dracai of Retribution"),
    ],
    "heroes-of-rathe/dash-about.md": [
        ("Dash, Inventor Extraordinaire", "Dash, Inventor Extraordinaire"),
        ("Dash, I/O", "Dash I/O"),
    ],
    "heroes-of-rathe/data-doll-mkii-about.md": [
        ("Data Doll, MKII", "Data Doll MKII"),
    ],
    "heroes-of-rathe/dorinthea-about.md": [
        ("Dorinthea, Ironsong", "Dorinthea Ironsong"),
        ("Dorinthea, Quicksilver Prodigy", "Dorinthea, Quicksilver Prodigy"),
    ],
    "heroes-of-rathe/dr-mortimer-about.md": [
        ("Dr. Mortimer, Blight of the Pits", "Dr. Mortimer, Blight of the Pits"),
    ],
    "heroes-of-rathe/dromai-about.md": [
        ("Dromai, Ash Artist", "Dromai, Ash Artist"),
    ],
    "heroes-of-rathe/emperor-about.md": [
        ("Emperor, Dracai of Aesir", "Emperor, Dracai of Aesir"),
    ],
    "heroes-of-rathe/enigma-about.md": [
        ("Enigma, Ledger of Ancestry", "Enigma, Ledger of Ancestry"),
    ],
    "heroes-of-rathe/fai-about.md": [
        ("Fai, Rising Rebellion", "Fai, Rising Rebellion"),
    ],
    "heroes-of-rathe/fang-about.md": [
        ("Fang, Dracai of Blades", "Fang, Dracai of Blades"),
    ],
    "heroes-of-rathe/florian-about.md": [
        ("Florian, Rotwood Harbinger", "Florian, Rotwood Harbinger"),
    ],
    "heroes-of-rathe/frankie-about.md": [
        ("Frankie, Make Ends Meat", "Frankie, Make Ends Meat"),
    ],
    "heroes-of-rathe/genis-about.md": [
        ("Genis Wotchuneed", "Genis Wotchuneed"),
    ],
    "heroes-of-rathe/gravy-about.md": [
        ("Gravy Bones, Shipwrecked Looter", "Gravy Bones, Shipwrecked Looter"),
    ],
    "heroes-of-rathe/hala-about.md": [
        ("Hala, Bladesaint of the Vow", "Hala, Bladesaint of the Vow"),
    ],
    "heroes-of-rathe/ira-about.md": [
        ("Ira, Scarlet Revenger", "Ira, Scarlet Revenger"),
    ],
    "heroes-of-rathe/iyslander-about.md": [
        ("Iyslander, Stormbind", "Iyslander, Stormbind"),
    ],
    "heroes-of-rathe/jarl-about.md": [
        ("Jarl Vetreiði", "Jarl Vetreiði"),
    ],
    "heroes-of-rathe/kano-about.md": [
        ("Kano, Dracai of Aether", "Kano, Dracai of Aether"),
    ],
    "heroes-of-rathe/kassai-about.md": [
        ("Kassai, Cintari Sellsword", "Kassai, Cintari Sellsword"),
        ("Kassai of the Golden Sand", "Kassai of the Golden Sand"),
    ],
    "heroes-of-rathe/katsu-about.md": [
        ("Katsu, The Wanderer", "Katsu, the Wanderer"),
    ],
    "heroes-of-rathe/kavdaen-about.md": [
        ("Kavdaen, Trader of Skins", "Kavdaen, Trader of Skins"),
    ],
    "heroes-of-rathe/kayo-about.md": [
        ("Kayo, Berserker Runt", "Kayo, Berserker Runt"),
        ("Kayo, Armed and Dangerous", "Kayo, Armed and Dangerous"),
        ("Kayo, Underhanded Cheat", "Kayo, Underhanded Cheat"),
    ],
    "heroes-of-rathe/killjoy-about.md": [
        ("Killjoy, the Crooked Blade", "Killjoy, the Crooked Blade"),
    ],
    "heroes-of-rathe/levia-about.md": [
        ("Levia, Shadowborn Abomination", "Levia, Shadowborn Abomination"),
    ],
    "heroes-of-rathe/lexi-about.md": [
        ("Lexi, Livewire", "Lexi, Livewire"),
    ],
    "heroes-of-rathe/lyath-about.md": [
        ("Lyath Goldmane, Vile Savant", "Lyath Goldmane, Vile Savant"),
    ],
    "heroes-of-rathe/malice-about.md": [
        ("Malice, Domina of the Dead", "Malice, Domina of the Dead"),
    ],
    "heroes-of-rathe/marlynn-about.md": [
        ("Marlynn, Treasure Hunter", "Marlynn, Treasure Hunter"),
    ],
    "heroes-of-rathe/maxx-about.md": [
        ("Maxx 'The Hype' Nitro", "Maxx 'The Hype' Nitro"),
    ],
    "heroes-of-rathe/melody-about.md": [
        ("Melody, Sing-along", "Melody, Sing-along"),
    ],
    "heroes-of-rathe/nuu-about.md": [
        ("Nuu, Alluring Desire", "Nuu, Alluring Desire"),
    ],
    "heroes-of-rathe/oldhim-about.md": [
        ("Oldhim, Grandfather of Eternity", "Oldhim, Grandfather of Eternity"),
    ],
    "heroes-of-rathe/olympia-about.md": [
        ("Olympia, Prized Fighter", "Olympia, Prized Fighter"),
    ],
    "heroes-of-rathe/oscilio-about.md": [
        ("Oscilio, Constella Intelligence", "Oscilio, Constella Intelligence"),
        ("Oscilio, Forked Continuum", "Oscilio, Forked Continuum"),
    ],
    "heroes-of-rathe/pleiades-about.md": [
        ("Pleiades, Superstar", "Pleiades, Superstar"),
    ],
    "heroes-of-rathe/prism-about.md": [
        ("Prism, Sculptor of Arc Light", "Prism, Sculptor of Arc Light"),
        ("Prism, Awakener of Sol", "Prism, Awakener of Sol"),
    ],
    "heroes-of-rathe/puffin-about.md": [
        ("Puffin, Hightail", "Puffin, Hightail"),
    ],
    "heroes-of-rathe/rhinar-about.md": [
        ("Rhinar, Reckless Rampage", "Rhinar, Reckless Rampage"),
    ],
    "heroes-of-rathe/riptide-about.md": [
        ("Riptide, Lurker of the Deep", "Riptide, Lurker of the Deep"),
    ],
    "heroes-of-rathe/scurv-about.md": [
        ("Scurv, Stowaway", "Scurv, Stowaway"),
    ],
    "heroes-of-rathe/shiyana-about.md": [
        ("Shiyana, Diamond Gemini", "Shiyana, Diamond Gemini"),
    ],
    "heroes-of-rathe/teklovossen-about.md": [
        ("Teklovossen, Esteemed Magnate", "Teklovossen, Esteemed Magnate"),
    ],
    "heroes-of-rathe/terra-about.md": [
        ("Terra", "Terra"),
    ],
    "heroes-of-rathe/tuffnut-about.md": [
        ("Tuffnut, Bumbling Hulkster", "Tuffnut, Bumbling Hulkster"),
    ],
    "heroes-of-rathe/uzuri-about.md": [
        ("Uzuri, Switchblade", "Uzuri, Switchblade"),
    ],
    "heroes-of-rathe/valda-about.md": [
        ("Valda, Seismic Impact", "Valda, Seismic Impact"),
    ],
    "heroes-of-rathe/verdance-about.md": [
        ("Verdance, Thorn of the Rose", "Verdance, Thorn of the Rose"),
    ],
    "heroes-of-rathe/victor-goldmane-about.md": [
        ("Victor Goldmane, High and Mighty", "Victor Goldmane, High and Mighty"),
    ],
    "heroes-of-rathe/viserai-about.md": [
        ("Viserai, Rune Blood", "Viserai, Rune Blood"),
        ("Viserai, The Forsaken", "Viserai, the Forsaken"),
    ],
    "heroes-of-rathe/vynnset-about.md": [
        ("Vynnset, Iron Maiden", "Vynnset, Iron Maiden"),
    ],
    "heroes-of-rathe/yoji-about.md": [
        ("Yoji, Royal Protector", "Yoji, Royal Protector"),
    ],
    "heroes-of-rathe/zane-about.md": [
        ("Zane, Broadly Beloved", "Zane, Broadly Beloved"),
    ],
    "heroes-of-rathe/zen-about.md": [
        ("Zen, Tamer of Purpose", "Zen, Tamer of Purpose"),
    ],
    "heroes-of-rathe/zyggy-about.md": [
        ("Zyggy Starlight", "Zyggy Starlight"),
    ],
}


@pytest.fixture(scope="module")
def data() -> dict:
    return load_hero_data(SRC / "data")


def test_every_hero_page_is_pinned():
    pages = sorted(
        rel for p in (SRC / "heroes-of-rathe").rglob("*.md") if is_hero_about_page(rel := p.relative_to(SRC).as_posix())
    )
    assert pages == sorted(EXPECTED)


@pytest.mark.parametrize("page", sorted(EXPECTED))
def test_headings_resolve_to_the_same_card(page: str, data: dict):
    forms = hero_forms((SRC / page).read_text(encoding="utf-8"), data)
    assert [(m.group(1).strip(), meta["name"]) for m, meta in forms] == EXPECTED[page]
