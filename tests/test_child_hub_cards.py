"""The card each weapons/equipment page shows on its hub, pinned against the real data.

Recorded from the filename-based fuzzy matcher before cards moved to the
``story-weapons.csv`` / ``story-equipment.csv`` junction, so a change in how a
card is picked shows up here before it shows up in the build. ``None`` means
the card has no image; ``"page"`` marks an image taken from the page's own
``<img>`` rather than card art.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from mdbook_child_hub import _process

SRC = Path(__file__).resolve().parent.parent / "src"

_GCS = "https://storage.googleapis.com/fabmaster/cardfaces/"
_LSS = "https://legendstory-production-s3-public.s3.amazonaws.com/media/cards/large/"

EXPECTED = {
    "weapons": {
        "cintari-saber.md": _GCS + "2020-CRU/CRU079.png",
        "hanabi-blaster.md": _GCS + "2022-DYN/EN/DYN088.png",
        "mandible-claw.md": _GCS + "2020-CRU/CRU004.png",
        "merciless-battleaxe.md": _GCS + "2022-DYN/EN/DYN068.png",
        "nebula-blade.md": _GCS + "2020-ARC/ARC077.png",
        "plasma-barrel-shot.md": _GCS + "2020-CRU/CRU101.png",
        "reaping-blade.md": _GCS + "2020-CRU/CRU140.png",
        "red-liner.md": _GCS + "2020-CRU/CRU121.png",
        "rok.md": _GCS + "2022-DYN/EN/DYN005.png",
        "sandscour-greatbow.md": _GCS + "2022-DYN/EN/DYN151.png",
        "savage-claw.md": _LSS + "PEN001.webp",
        "sledge-of-anvilheim.md": _GCS + "2020-CRU/CRU024.png",
        "surgent-aethertide.md": _GCS + "2022-DYN/EN/DYN192.png",
        # Filename drops "the": canonical slug is talishar-the-lost-prince.
        "talishar-lost-prince.md": _GCS + "2020-CRU/CRU177.png",
        "zephyr-needle.md": "https://storage.googleapis.com/fabmaster/media/images/CRU051_Zephyr_Needle.width-10000.png",
    },
    "equipment": {
        "amethyst-tiara.md": _GCS + "2022-DYN/EN/DYN171.png",
        "blazen-yoroi.md": _GCS + "2022-DYN/EN/DYN045.png",
        "bloodsheath-skeleta.md": _GCS + "2020-CRU/CRU141.png",
        # Filename has an extra hyphen: canonical slug is boltn-boots.
        "bolt-n-boots.md": _LSS + "PEN082.webp",
        "breeze-rider-boots.md": _GCS + "2020-CRU/CRU053.png",
        "celestial-kimono.md": _GCS + "2022-DYN/EN/DYN213.png",
        "comeback-kicks.md": _LSS + "PEN288.webp",
        "courage-of-bladehold.md": _GCS + "2020-CRU/CRU081.png",
        "crater-fist.md": _GCS + "2020-CRU/CRU025.png",
        "grimoire-of-fellingsong.md": _LSS + "PEN092.webp",
        "metacarpus-node.md": _GCS + "2020-CRU/CRU161.png",
        "myrkhellir-helm.md": _LSS + "PEN315.webp",
        "seasoned-saviour.md": _GCS + "2022-DYN/EN/DYN026.png",
        "skullhorn.md": _GCS + "2020-CRU/CRU006.png",
        "synapse-sparkcap.md": _LSS + "PEN057.webp",
        "trench-of-watery-depths.md": _LSS + "PEN168.webp",
        "viziertronic-model-i.md": _GCS + "2020-CRU/CRU102.png",
        "wind-cutter.md": _LSS + "PEN029.webp",
    },
}

_HUBS = {
    "weapons": "weapons/armed-to-the-teeth.md",
    "equipment": "equipment/in-the-fires-of-the-forge.md",
}

_CARD_RE = re.compile(
    r'<a class="sets-hub-card" href="([^"]+)">\s*(?:<img( class="child-hub-card-art")? src="([^"]+)")?',
)


def _rendered_cards(kind: str) -> dict[str, str | None]:
    """Run the preprocessor over the real hub with every page in its folder as a child."""
    hub = _HUBS[kind]
    children = sorted(p.name for p in (SRC / kind).glob("*.md") if f"{kind}/{p.name}" != hub)
    items = [
        {
            "Chapter": {
                "name": "Hub",
                "path": hub,
                "content": "",
                "sub_items": [{"Chapter": {"name": c, "path": f"{kind}/{c}", "sub_items": []}} for c in children],
            }
        }
    ]
    _process(items, SRC)
    cards = {}
    for href, card_art, src in _CARD_RE.findall(items[0]["Chapter"]["content"]):
        page = Path(href).with_suffix(".md").name
        cards[page] = (src if card_art else "page") if src else None
    return cards


@pytest.mark.parametrize("kind", sorted(EXPECTED))
def test_every_hub_card_shows_the_card_it_showed_before_the_junction(kind: str) -> None:
    assert _rendered_cards(kind) == EXPECTED[kind]
