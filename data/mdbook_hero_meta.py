#!/usr/bin/env python3
"""mdBook preprocessor: hero banners, stat blocks and hub talent data.

For each ``heroes-of-rathe/*-about.md`` chapter, every H1 whose text matches a
``CardName`` in ``heroes-game.csv`` becomes one form:

* a ``<header class="hero-banner">`` holding the H1 (still a markdown heading,
  its name and subtitle in spans), the ``<video>`` under it and an optional
  ``:::hero-blurb`` block — the story card goes under it (``mdbook_story_meta``
  looks for ``BANNER_END``);
* the lore and traits as written;
* a stat block at the end, in the style of a Fabrary card page: one header
  (name, Adult | Young, Card | Printings) over the card image and the "Card
  text", "Details" and "Printings" panels. An adult form whose young card
  shares its ability and has no H1 of its own carries that young card as a
  second, switchable variant.

The Details panel also carries the form's playstyles and difficulty, from
``heroes-fabtcg.csv`` (a young card with no row of its own takes its adult
partner's).

A page with two or more forms wraps each in ``<div class="hero-form">`` (with
``data-source``, the form's fabtcg.com page, for the source link) and ends the
forms with a "Forms of <hero>" section of portraits, so ``theme/hero-card.js``
can show one form at a time. Hero videos lose ``autoplay`` and ``controls``;
``theme/hero-card.js`` plays them only while on screen and adds a pause button.

On the hub (``heroes-of-rathe/heroes-of-rathe.md``) each ``.hero-hub-card``
gets ``data-talents`` and ``data-playstyles`` from the forms on the page it
links to. A card for a multi-form page also gets ``data-forms`` (each form's
anchor, name, art, talents and playstyles, in release order) and a link to the
form its image shows; ``hero-hub.js`` points it at the newest matching form
while a playstyle or talent filter is on.

mdBook passes ``(PreprocessorContext, Book)`` as JSON on stdin; this process
must print only the modified ``Book`` JSON on stdout.  Supports
``supports <renderer>``.
"""

from __future__ import annotations

import html
import json
import re
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from card_text import format_ability_text  # noqa: E402
from mdbook_common import HERO_BANNER_END as BANNER_END  # noqa: E402
from mdbook_common import format_date as _format_date  # noqa: E402
from mdbook_common import is_hero_about_page as _is_hero_about_page  # noqa: E402
from mdbook_common import iter_chapters, run  # noqa: E402
from mdbook_heading_ids import collect_heading_anchor_ids  # noqa: E402
from mdbook_related import MARK_START as RELATED_START  # noqa: E402
from pipe_csv_io import read_pipe_csv  # noqa: E402
from text_utils import normalize_name  # noqa: E402

# Set type IDs to exclude when finding the "first set" for a hero variant.
_EXCLUDED_SET_TYPE_IDS = {
    "TY1ac8c9771b",  # Promo
    "TY92969bb9ea",  # Prize
    "TY218948d76b",  # Token Set
}

# Lower value = preferred when release dates tie.
_SET_TYPE_PRIORITY: dict[str, int] = {
    "TY87478277a5": 0,  # Core Booster Set
    "TY858a95be59": 1,  # Expansion Booster Set
    "TY48cd9f30bc": 2,  # Supplementary Booster Set
    "TYd8e2e91515": 3,  # History Pack
    "TYae8fdcc03a": 4,  # Mastery Pack
    "TY00678b0ea7": 5,  # Welcome Deck
    "TY3634cb99aa": 6,  # Hero Deck
    "TY526cd03a42": 7,  # Blitz Deck
    "TYfcaaf6a22f": 8,  # Armory Deck
    "TY6f903c3145": 9,  # Classic Battles Deck
    "TY7fc7966b3b": 10,  # First Strike Deck
    "TY14e59cce5d": 11,  # Box Set
    "TY0143717ab6": 12,  # History Pack Blitz Deck
    "TY4dde9990af": 13,  # Demo Deck
}


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------


def _load_card_meta(data_dir: Path) -> dict[str, dict]:
    """Return a map from ``CardName`` → per-variant hero metadata."""
    _, game_rows = read_pipe_csv(data_dir / "csv" / "heroes-game.csv")
    _, printings_rows = read_pipe_csv(data_dir / "csv" / "heroes-printings.csv")
    _, sets_rows = read_pipe_csv(data_dir / "csv" / "sets.csv")
    _, classes_rows = read_pipe_csv(data_dir / "csv" / "classes.csv")
    _, talents_rows = read_pipe_csv(data_dir / "csv" / "talents.csv")
    _, ll_rows = read_pipe_csv(data_dir / "csv" / "heroes-ll.csv")
    _, fabtcg_rows = read_pipe_csv(data_dir / "csv" / "heroes-fabtcg.csv")
    _, canonical_rows = read_pipe_csv(data_dir / "csv" / "heroes-canonical.csv")
    hero_by_canonical_id = {
        (row.get("CanonicalId") or "").strip(): (row.get("CanonicalHero") or "").strip() for row in canonical_rows
    }
    fabtcg_by_card_name = {
        name: {
            "link": (row.get("HeroPageLink") or "").strip(),
            "difficulty": (row.get("Difficulty") or "").strip(),
            "portrait": (row.get("PortraitKey") or "").strip(),
            "playstyles": [p.strip() for p in (row.get("Playstyles") or "").split(",") if p.strip()],
        }
        for row in fabtcg_rows
        if (name := (row.get("CardName") or "").strip())
    }

    # --- sets ---
    set_type_id_by_set_id: dict[str, str] = {}
    set_name_by_id: dict[str, str] = {}
    set_release_by_id: dict[str, str] = {}
    for row in sets_rows:
        sid = (row.get("SetId") or "").strip()
        if sid:
            set_type_id_by_set_id[sid] = (row.get("SetTypeId") or "").strip()
            set_name_by_id[sid] = (row.get("SetName") or "").strip()
            set_release_by_id[sid] = (row.get("InitialReleaseDate") or "").strip().split("T")[0]

    # --- classes / talents ---
    class_name_by_id: dict[str, str] = {
        (row.get("ClassId") or "").strip(): (row.get("ClassName") or "").strip()
        for row in classes_rows
        if (row.get("ClassId") or "").strip()
    }
    talent_name_by_id: dict[str, str] = {
        (row.get("TalentId") or "").strip(): (row.get("TalentName") or "").strip()
        for row in talents_rows
        if (row.get("TalentId") or "").strip()
    }

    # --- printings per HeroGameId ---
    printings_by_game_id: dict[str, list[dict[str, str]]] = {}
    for row in printings_rows:
        gid = (row.get("HeroGameId") or "").strip()
        sid = (row.get("SetId") or "").strip()
        if gid and sid:
            printings_by_game_id.setdefault(gid, []).append(
                {
                    "set_id": sid,
                    "card_id": (row.get("CardId") or "").strip(),
                    "rarity": (row.get("Rarity") or "").strip(),
                    "unique_id": (row.get("PrintingUniqueId") or "").strip(),
                    "foiling": (row.get("Foiling") or "").strip(),
                    "art_variation": (row.get("ArtVariation") or "").strip(),
                    "artist": (row.get("Artist") or "").strip(),
                }
            )

    # --- LL entries per CardName ---
    ll_by_card_name: dict[str, list[dict[str, str]]] = {}
    for row in ll_rows:
        card_name = (row.get("CardName") or "").strip()
        if card_name:
            ll_by_card_name.setdefault(card_name, []).append(
                {
                    "Format": (row.get("Format") or "").strip(),
                    "DateInEffect": (row.get("DateInEffect") or "").strip(),
                }
            )

    # --- build per-CardName metadata ---
    result: dict[str, dict] = {}
    for row in game_rows:
        card_name = (row.get("CardName") or "").strip()
        hero_game_id = (row.get("HeroGameId") or "").strip()
        if not card_name or not hero_game_id:
            continue

        classes = [
            class_name_by_id[cid]
            for raw in (row.get("ClassIds") or "").split(",")
            if (cid := raw.strip()) and cid in class_name_by_id
        ]
        talents = [
            talent_name_by_id[tid]
            for raw in (row.get("TalentIds") or "").split(",")
            if (tid := raw.strip()) and tid in talent_name_by_id
        ]

        best_set_id, best_date, best_priority = "", "", 9999
        printings = printings_by_game_id.get(hero_game_id, [])
        for sid in dict.fromkeys(p["set_id"] for p in printings):
            type_id = set_type_id_by_set_id.get(sid, "")
            if type_id in _EXCLUDED_SET_TYPE_IDS:
                continue
            release = set_release_by_id.get(sid, "")
            if not release:
                continue
            priority = _SET_TYPE_PRIORITY.get(type_id, 50)
            if not best_date or release < best_date or (release == best_date and priority < best_priority):
                best_date = release
                best_set_id = sid
                best_priority = priority

        # Default printing: from the first set, standard foiling and no art
        # variation preferred, then the lowest unique id for determinism.
        # A card whose sets have no release date yet falls back to any
        # non-promo printing, so an announced hero still shows its card.
        in_first_set = [p for p in printings if p["set_id"] == best_set_id] or [
            p for p in printings if set_type_id_by_set_id.get(p["set_id"], "") not in _EXCLUDED_SET_TYPE_IDS
        ]
        default_printing = min(
            in_first_set,
            key=lambda p: (p["foiling"] != "S", p["art_variation"] != "", p["unique_id"]),
            default=None,
        )

        all_printings = sorted(
            (
                {
                    **p,
                    "set_name": set_name_by_id.get(p["set_id"], ""),
                    "release": set_release_by_id.get(p["set_id"], ""),
                }
                for p in printings
            ),
            key=lambda p: (p["release"] or "9999", p["card_id"], p["unique_id"]),
        )

        result[card_name] = {
            "name": card_name,
            "printings": all_printings,
            "default_printing": default_printing,
            "health": (row.get("Health") or "").strip(),
            "intellect": (row.get("Intellect") or "").strip(),
            "ability_text": row.get("AbilityText") or "",
            "canonical_id": (row.get("CanonicalId") or "").strip(),
            "hero": hero_by_canonical_id.get((row.get("CanonicalId") or "").strip(), ""),
            "young": (row.get("YoungHero") or "").strip().lower() == "true",
            "first_set_name": set_name_by_id.get(best_set_id, ""),
            "first_set_date": best_date,
            "classes": classes,
            "talents": talents,
            "ll": ll_by_card_name.get(card_name, []),
            "fabtcg": fabtcg_by_card_name.get(card_name),
        }

    return result


# ---------------------------------------------------------------------------
# HTML building
# ---------------------------------------------------------------------------


_CARD_ICON_BASE = "https://d2hl7maqck52px.cloudfront.net/card-icons"
_CARD_IMAGE_BASE = "https://d2hl7maqck52px.cloudfront.net/hero-cards"


_FORMAT_NAMES = {"CC": "Classic Constructed"}


def _ll_rows(meta: dict) -> str:
    # Living Legend status is a Classic Constructed fact about the adult card only.
    if meta["young"]:
        return ""
    out = ""
    for entry in meta["ll"]:
        pieces = []
        fmt = entry.get("Format", "")
        if fmt:
            pieces.append(html.escape(_FORMAT_NAMES.get(fmt, fmt)))
        date = _format_date(entry.get("DateInEffect", ""))
        if date:
            pieces.append(html.escape(date))
        out += (
            '<div class="hero-detail hero-detail--wide hero-detail--ll"><dt>Living Legend</dt><dd>'
            f'<span class="hero-ll-badge"><i class="fas fa-trophy" aria-hidden="true"></i> {" · ".join(pieces)}</span>'
            "</dd></div>"
        )
    return out


# Every hero page sits beside the hub, so a bare relative link reaches it.
_HUB_HREF = "heroes-of-rathe.md"


def _slug(label: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", label.lower()).strip("-")


def _row(label: str, value: str, wide: bool = False) -> str:
    cls = "hero-detail hero-detail--wide" if wide else "hero-detail"
    return f'<div class="{cls}"><dt>{html.escape(label)}</dt><dd>{value}</dd></div>'


def _hub_links(kind: str, labels: list[str]) -> str:
    return ", ".join(f'<a href="{_HUB_HREF}#{kind}-{_slug(label)}">{html.escape(label)}</a>' for label in labels)


_PLAYSTYLE_ICON_BASE = "https://d2hl7maqck52px.cloudfront.net/playstyle-icons"


def _playstyles(names: list[str]) -> str:
    """Each playstyle as its icon and name, linking to the filtered hub.

    A plain image: the CDN sends no CORS header, so a CSS mask (which would take the
    text colour) cannot load it. theme/hero-card.css darkens the gold on light themes.
    """
    return "".join(
        f'<a class="hero-playstyle" href="{_HUB_HREF}#playstyle-{_slug(name)}">'
        f'<img class="hero-playstyle-icon" src="{_PLAYSTYLE_ICON_BASE}/{_slug(name)}.webp" alt="" width="20" height="20">'
        f"{html.escape(name)}</a>"
        for name in names
    )


def _difficulty(value: str) -> str:
    """Five stars, filled to ``value`` in halves, read out as "2.5 out of 5"."""
    try:
        halves = round(float(value) * 2)
    except ValueError:
        return ""
    stars = "".join(
        (
            '<span class="hero-star hero-star--full"></span>'
            if halves >= 2 * i
            else (
                '<span class="hero-star hero-star--half"></span>'
                if halves == 2 * i - 1
                else '<span class="hero-star"></span>'
            )
        )
        for i in range(1, 6)
    )
    return f'<span class="hero-difficulty" role="img" aria-label="{html.escape(value)} out of 5">{stars}</span>'


def _details(meta: dict) -> str:
    rows = ""
    if meta["classes"]:
        rows += _row("Class", _hub_links("class", meta["classes"]))
    if meta["talents"]:
        rows += _row("Talent", _hub_links("talent", meta["talents"]))
    rows += _row("Type", "Hero — Young" if meta["young"] else "Hero")
    for label, icon, key in (("Life", "icon_hp.webp", "health"), ("Intellect", "icon_int.webp", "intellect")):
        if meta[key]:
            rows += _row(
                label,
                f'<img src="{_CARD_ICON_BASE}/{icon}" alt="" class="hero-detail-icon" width="16" height="16"> '
                f"{html.escape(meta[key])}",
            )
    fabtcg = meta.get("fabtcg") or {}
    if fabtcg.get("difficulty") and (stars := _difficulty(fabtcg["difficulty"])):
        rows += _row("Difficulty", stars)
    if fabtcg.get("playstyles"):
        rows += _row("Playstyle", _playstyles(fabtcg["playstyles"]), wide=True)
    if meta["first_set_name"]:
        date = _format_date(meta["first_set_date"])
        rows += _row(
            "First released",
            html.escape(meta["first_set_name"]) + (f" ({html.escape(date)})" if date else ""),
            wide=True,
        )
    printings = meta["printings"]
    sets = _distinct(p["set_name"] for p in printings)
    if sets:
        rows += _row("Sets", "".join(f'<span class="hero-chip">{html.escape(n)}</span>' for n in sets), wide=True)
    rarities = _distinct(_RARITIES.get(p["rarity"], p["rarity"]) for p in printings)
    if rarities:
        rows += _row("Rarities", ", ".join(map(html.escape, rarities)), wide=True)
    artists = _distinct(p["artist"] for p in printings)
    if artists:
        rows += _row("Artists", "".join(f'<span class="hero-chip">{html.escape(n)}</span>' for n in artists), wide=True)
    rows += _ll_rows(meta)
    return _panel("details", "Details", f'<dl class="hero-details">{rows}</dl>')


# Upstream rarity.json.
_RARITIES = {
    "C": "Common",
    "R": "Rare",
    "S": "Super Rare",
    "M": "Majestic",
    "L": "Legendary",
    "F": "Fabled",
    "T": "Token",
    "B": "Basic",
    "V": "Marvel",
    "P": "Promo",
}


def _distinct(values) -> list[str]:
    return list(dict.fromkeys(v for v in values if v))


_FOILINGS = {"S": "Standard", "R": "Rainbow Foil", "C": "Cold Foil", "G": "Gold Foil"}
_ART_VARIATIONS = {
    "AA": "Alternate Art",
    "AB": "Alternate Border",
    "AT": "Alternate Text",
    "EA": "Extended Art",
    "FA": "Full Art",
}


def _finish(printing: dict) -> list[str]:
    """Foiling then art variations, as display names."""
    names = [_FOILINGS.get(printing["foiling"], printing["foiling"])] if printing["foiling"] else []
    for code in filter(None, (c.strip() for c in printing["art_variation"].split(","))):
        names.append(_ART_VARIATIONS.get(code, code))
    return names


def _print_line(printing: dict) -> str:
    """``<code>WTR038</code> · Standard`` — the card id and its finish."""
    return " · ".join([f"<code>{html.escape(printing['card_id'])}</code>", *map(html.escape, _finish(printing))])


def _printing_label(printing: dict) -> str:
    pieces = [printing["card_id"]]
    if printing["set_name"]:
        pieces.append(printing["set_name"])
    pieces += _finish(printing)
    if printing["artist"]:
        pieces.append(f"art by {printing['artist']}")
    return ", ".join(pieces)


def _printings(meta: dict) -> str:
    printings = meta["printings"]
    if not printings:
        return ""
    items = ""
    for p in printings:
        label = html.escape(_printing_label(p))
        items += (
            '<figure class="hero-printing-item">'
            f'<img src="{_CARD_IMAGE_BASE}/{html.escape(p["unique_id"])}.webp" alt="{label}" title="{label}" '
            f'class="hero-printing" loading="lazy" width="546" height="763" data-artist="{html.escape(p["artist"])}">'
            f"<figcaption>{_print_line(p)}</figcaption></figure>"
        )
    return _panel(
        "printings", f"Printings ({len(printings)})", f'<div class="hero-printings-grid no-zoom">{items}</div>'
    )


def _panel(kind: str, title: str, inner: str) -> str:
    return (
        f'<div class="hero-panel hero-panel--{kind}"><p class="hero-panel-title">{html.escape(title)}</p>'
        f"{inner}</div>\n"
    )


def _card_text(meta: dict) -> str:
    return f'<div class="hero-statblock-text no-zoom">{format_ability_text(meta["ability_text"])}</div>'


def _variant_switch(selected: str) -> str:
    def button(name: str, label: str) -> str:
        pressed = "true" if name == selected else "false"
        return f'<button type="button" class="hero-seg-btn" data-variant="{name}" aria-pressed="{pressed}">{label}</button>'

    return (
        '<div class="hero-seg hero-variant-switch" role="group" aria-label="Card version">'
        f'{button("adult", "Adult")}{button("young", "Young")}</div>'
    )


def _variant(meta: dict, variant: str) -> str:
    name = meta["name"]
    thumb = ""
    printing = meta["default_printing"]
    if printing:
        alt = html.escape(f"{name} card ({printing['card_id']})")
        artist = (
            f'<span class="hero-statblock-artist">{html.escape(printing["artist"])}</span>'
            if printing["artist"]
            else ""
        )
        thumb = (
            '<figure class="hero-statblock-card">'
            f'<img src="{_CARD_IMAGE_BASE}/{html.escape(printing["unique_id"])}.webp" alt="{alt}" '
            'class="hero-statblock-thumb" width="546" height="763">'
            '<figcaption class="hero-statblock-caption">'
            f'<span class="hero-statblock-print">{_print_line(printing)}</span>{artist}'
            "</figcaption></figure>\n"
        )
    return (
        f'<div class="hero-statblock-variant" data-variant="{variant}" data-name="{html.escape(name)}">\n'
        f"{thumb}"
        '<div class="hero-statblock-main">\n'
        f"{_panel('text', 'Card text', _card_text(meta))}"
        f"{_details(meta)}"
        f"{_printings(meta)}"
        "</div>\n"
        "</div>\n"
    )


_VIEW_SWITCH = (
    '<div class="hero-seg hero-view-switch" role="group" aria-label="Show">'
    '<button type="button" class="hero-seg-btn" data-view="card" aria-pressed="true">Card</button>'
    '<button type="button" class="hero-seg-btn" data-view="printings" aria-pressed="false">Printings</button>'
    "</div>"
)


def _build_stat_block(meta: dict, young: dict | None = None) -> str:
    """One header (name, Adult | Young, Card | Printings) shared by the variants below it.

    Switching variant swaps the name and the variant in place, so the page does not jump.
    """
    variants = [(meta, "adult" if young else "only")] + ([(young, "young")] if young else [])
    controls = (_variant_switch("adult") if young else "") + (
        _VIEW_SWITCH if any(m["printings"] for m, _ in variants) else ""
    )
    head = (
        f'<div class="hero-statblock-head"><p class="hero-statblock-name">{html.escape(meta["name"])}</p>'
        f'<div class="hero-statblock-controls">{controls}</div></div>\n'
    )
    return (
        f'<section class="hero-statblock" aria-label="Hero card: {html.escape(meta["name"])}">\n'
        f"{head}" + "".join(_variant(m, v) for m, v in variants) + "</section>"
    )


def _normalise(text: str) -> str:
    return " ".join(text.split())


def _adult_partner(young: dict, adults: list[dict]) -> dict | None:
    """The adult card a young card is the young side of, from ``adults``: the adult cards of its identity.

    It shares the young card's ability; failing that, it is the only adult card
    of that identity. The fallback covers young cards worded differently:
    young Florian's text halves the adult's Earth count, and Arakni, Solitary
    Confinement says "The first attack" where Arakni, 5L!p3d 7hRu 7h3 cR4X says "Your".
    """
    same_text = [a for a in adults if _normalise(a["ability_text"]) == _normalise(young["ability_text"])]
    if same_text:
        return same_text[0]
    return adults[0] if len(adults) == 1 else None


def _young_partner(meta: dict, data: dict, named_on_page: set[str]) -> dict | None:
    """The young side of this adult card (see :func:`_adult_partner`), if the page has no heading for it.

    A young card with the same ability wins over one that pairs only by identity.
    """
    if meta["young"]:
        return None
    youngs = [y for y in data["youngs"].get(meta["name"], []) if y["name"] not in named_on_page]
    youngs.sort(key=lambda y: _normalise(y["ability_text"]) != _normalise(meta["ability_text"]))
    return youngs[0] if youngs else None


# ---------------------------------------------------------------------------
# Heading → CardName resolution
# ---------------------------------------------------------------------------


def _resolve(heading: str, data: dict) -> dict | None:
    """The card ``heading`` names: its exact name, else the card whose name folds the same.

    The fold (:func:`text_utils.normalize_name`) covers headings styled apart from
    the card name: case (``Benji, The Piercing Wind``) and punctuation
    (``Dash, I/O`` for ``Dash I/O``).
    """
    return data["cards"].get(heading) or data["cards_by_key"].get(normalize_name(heading))


# ---------------------------------------------------------------------------
# Injection
# ---------------------------------------------------------------------------

_H1_RE = re.compile(r"^# ([^\n]+)\n", re.MULTILINE)
# A <video> block directly under the heading (blank lines allowed between).
_VIDEO_AFTER_RE = re.compile(r"\s*<video\b.*?</video>[ \t]*\n?", re.DOTALL)
# A :::hero-blurb block directly under the heading: one sentence for the banner.
_BLURB_AFTER_RE = re.compile(r"\s*^:::hero-blurb[ \t]*\n(.*?)\n:::[ \t]*(?:\n|$)", re.DOTALL | re.MULTILINE)


def hero_forms(content: str, data: dict) -> list[tuple[re.Match, dict]]:
    """Each H1 on a hero page that names a hero card, with that card's metadata, in page order."""
    return [
        (match, meta)
        for match in _H1_RE.finditer(content)
        if (meta := _resolve(match.group(1).strip(), data)) is not None
    ]


def load_hero_data(data_dir: Path) -> dict:
    """Load everything the hero page renderers need from ``data_dir/csv``.

    ``youngs`` maps an adult card's name to the young cards that pair with it
    (:func:`_adult_partner`), in card order. ``cards_by_key`` indexes the cards by
    :func:`text_utils.normalize_name` of their name, first card winning, for
    :func:`_resolve`.
    """
    cards = _load_card_meta(data_dir)
    cards_by_key: dict[str, dict] = {}
    for card_name, card in cards.items():
        cards_by_key.setdefault(normalize_name(card_name), card)
    adults_by_identity: dict[str, list[dict]] = {}
    for card in cards.values():
        if not card["young"]:
            adults_by_identity.setdefault(card["canonical_id"], []).append(card)
    youngs: dict[str, list[dict]] = {}
    for card in cards.values():
        if not card["young"]:
            continue
        partner = _adult_partner(card, adults_by_identity.get(card["canonical_id"], []))
        if partner:
            youngs.setdefault(partner["name"], []).append(card)
        # fabtcg.com lists a hero once, on its adult card: a young card with no row
        # of its own takes its adult partner's.
        if not card["fabtcg"]:
            card["fabtcg"] = partner["fabtcg"] if partner else None
    return {"cards": cards, "cards_by_key": cards_by_key, "youngs": youngs}


_VIDEO_TAG_RE = re.compile(r"<video\b([^>]*)>")


def _defer_video(match: re.Match) -> str:
    """Drop ``autoplay``; ``hero-card.js`` plays the video only while it is on screen."""
    attrs = re.sub(r"\s+(?:autoplay|controls)\b", "", match.group(1)).rstrip()
    attrs = re.sub(r'\s+preload="[^"]*"', "", attrs)
    return f'<video{attrs} preload="none" data-hero-autoplay>'


def _heading_id(content: str, match: re.Match) -> str:
    """The id mdBook gives this heading: the last one up to and including its line."""
    return collect_heading_anchor_ids(content[: match.end()])[-1]


_TRAILING_RULE_RE = re.compile(r"\n\s*(?:-{3,}|\*{3,}|_{3,})\s*$")


_PLAY_BUTTON = (
    '<button type="button" class="hero-banner-play" aria-label="Pause video" aria-pressed="false">'
    '<span class="hero-banner-play-pause"><i class="fas fa-pause" aria-hidden="true"></i></span>'
    '<span class="hero-banner-play-play"><i class="fas fa-play" aria-hidden="true"></i></span></button>\n'
)


_PORTRAIT_BASE = "https://d2hl7maqck52px.cloudfront.net/hero-icons"


def _forms_section(forms: list[tuple[str, str, dict]]) -> str:
    """ "Forms of <hero>": one item per form, in release order; theme/hero-card.js switches between them.

    ``forms`` holds ``(anchor, heading, meta)`` in release order. Each item is a real link
    to its form's anchor, so it works without JS. The newest form is selected, as it is
    the one theme/hero-card.js shows first.
    """
    first_heading, first_meta = forms[0][1], forms[0][2]
    hero = first_meta["hero"] or first_heading.partition(",")[0].strip()
    title = f"Forms of {hero}"

    def item(form_id: str, heading: str, meta: dict, selected: bool) -> str:
        _, comma, subtitle = heading.partition(",")
        label = subtitle.strip() if comma else heading
        year = meta["first_set_date"][:4]
        portrait = (meta.get("fabtcg") or {}).get("portrait", "")
        sub = [meta["first_set_name"]] if meta["first_set_name"] else []
        if meta["young"]:
            sub.append("Young")
        elif meta["ll"]:
            sub.append("Living Legend")
        return (
            f'<a class="hero-tab" role="tab" href="#{html.escape(form_id)}" '
            f'aria-selected="{"true" if selected else "false"}">'
            + (f'<span class="hero-tab-year">{html.escape(year)}</span>' if year else "")
            + (
                f'<img class="hero-tab-portrait" src="{_PORTRAIT_BASE}/{html.escape(portrait)}.webp" alt="" '
                'width="112" height="112" loading="lazy">'
                if portrait
                else ""
            )
            + f'<span class="hero-tab-label">{html.escape(label)}</span>'
            + (f'<span class="hero-tab-sub">{html.escape(" · ".join(sub))}</span>' if sub else "")
            + "</a>"
        )

    items = "".join(item(*form, i == len(forms) - 1) for i, form in enumerate(forms))
    return (
        '<section class="hero-forms" aria-labelledby="hero-forms-title">\n\n'
        # Not a markdown heading: mdBook would list it in the sidebar.
        f'<p class="hero-forms-title" id="hero-forms-title" role="heading" aria-level="2">{html.escape(title)}</p>\n\n'
        f'<div class="hero-forms-rail" role="tablist" aria-label="{html.escape(title)}">{items}</div>\n\n'
        "</section>\n\n"
    )


def _banner(heading: str, video: str, blurb: str = "") -> str:
    """The H1 (still a markdown heading, so mdBook gives it its id) over the hero video.

    ``mdbook_story_meta`` puts the story card after ``BANNER_END`` rather than
    straight after the H1, so the card sits under the banner, not inside it.
    """
    name, comma, subtitle = heading.partition(",")
    title = f'<span class="hero-banner-name">{html.escape(name.strip())}</span>'
    if comma:
        title += (
            '<span class="hero-banner-comma">, </span>'
            f'<span class="hero-banner-subtitle">{html.escape(subtitle.strip())}</span>'
        )
    media = f'<div class="hero-banner-media">\n{video.strip()}\n{_PLAY_BUTTON}</div>\n' if video else ""
    blurb_html = (
        '<div class="hero-banner-rule" aria-hidden="true"></div>\n'
        f'<p class="hero-banner-blurb">{html.escape(blurb, quote=False)}</p>\n'
        if blurb
        else ""
    )
    return (
        f'<header class="hero-banner{"" if video else " hero-banner--plain"}">\n'
        f"{media}"
        '<div class="hero-banner-text">\n\n'
        f"# {title}\n\n"
        f"{blurb_html}"
        "</div>\n"
        "</header>\n"
        f"{BANNER_END}\n\n"
    )


# A horizontal rule with the site's emblem in the middle (theme: hero.css).
# Decorative only, so screen readers skip it.
_DIVIDER = (
    '<div class="hero-divider" role="presentation" aria-hidden="true">'
    '<img src="../assets/logo-emblem.webp" alt="" class="hero-divider-emblem" width="44" height="44" '
    'loading="lazy" decoding="async"></div>'
)

_TRAIT_BLOCK_RE = re.compile(r"^:::hero-trait ", re.MULTILINE)


def _render_form(content: str, match: re.Match, end: int, meta: dict, data: dict, named_on_page: set) -> str:
    """One form's text, from its H1 to ``end``, with the stat block at its end.

    The order is banner, lore, traits, stat block. A ``---`` rule closing the form
    stays after the stat block.
    """
    # The video and the :::hero-blurb block may follow the H1 in either order.
    cut = match.end()
    video, blurb = "", ""
    while True:
        if not video and (m := _VIDEO_AFTER_RE.match(content, cut)):
            video, cut = m.group(0), m.end()
        elif not blurb and (m := _BLURB_AFTER_RE.match(content, cut)):
            blurb, cut = " ".join(m.group(1).split()), m.end()
        else:
            break
    banner = _banner(match.group(1).strip(), video, blurb)
    body = banner + content[cut:end].strip()
    rule = _TRAILING_RULE_RE.search(body)
    tail = ""
    if rule:
        body, tail = body[: rule.start()].rstrip(), rule.group(0).strip() + "\n\n"
    block = _build_stat_block(meta, _young_partner(meta, data, named_on_page))
    divider = _DIVIDER + "\n\n" if _TRAIT_BLOCK_RE.search(body) else ""
    return body + "\n\n" + divider + block + "\n\n" + tail


def _source_attr(meta: dict) -> str:
    """``data-source``: the form's fabtcg.com hero page, which theme/hero-card.js gives the source link."""
    link = (meta.get("fabtcg") or {}).get("link", "")
    return f' data-source="{html.escape(link)}"' if link else ""


def render_hero_page(content: str, data: dict) -> str:
    """Turn each H1 that names a hero card into a form: banner, lore, traits, stat block.

    On a page with two or more forms, each form is wrapped in
    ``<div class="hero-form" data-form="<anchor>">`` so theme/hero-card.js can show one
    form at a time, and a "Forms of <hero>" section after the last form lists them
    all (:func:`_forms_section`). The ``---`` rule between forms is dropped there:
    the wrappers separate the forms instead.
    """
    content = _VIDEO_TAG_RE.sub(_defer_video, content)
    # mdbook_related has already appended Related Lore; it follows every form, in no form.
    content, marker, related = content.partition(RELATED_START)
    related = marker + related
    forms = hero_forms(content, data)
    if not forms:
        return content + related
    if related:
        related = _DIVIDER + "\n\n" + related
    named_on_page = {meta["name"] for _, meta in forms}
    ends = [match.start() for match, _ in forms[1:]] + [len(content)]
    ids = [_heading_id(content, match) for match, _ in forms]
    rendered = [_render_form(content, match, end, meta, data, named_on_page) for (match, meta), end in zip(forms, ends)]
    head = content[: forms[0][0].start()]
    if len(forms) < 2:
        return head + rendered[0] + related
    wrapped = [
        f'<div class="hero-form" data-form="{form_id}"{_source_attr(meta)}>\n\n'
        + _TRAILING_RULE_RE.sub("", text.rstrip())
        + "\n\n</div>\n\n"
        for (_, meta), form_id, text in zip(forms, ids, rendered)
    ]
    return head + "".join(wrapped) + _forms_section(_in_release_order(content, forms)) + related


def _in_release_order(content: str, forms: list[tuple[re.Match, dict]]) -> list[tuple[str, str, dict]]:
    """``(anchor, heading, meta)`` for each form, oldest first: the order of the "Forms of" rail."""
    return sorted(
        ((_heading_id(content, match), match.group(1).strip(), meta) for match, meta in forms),
        key=lambda f: f[2]["first_set_date"] or "9999",
    )


_HUB_CARD_RE = re.compile(r'(<a class="[^"]*\bhero-hub-card\b[^"]*"[^>]*?)(\s+href="([^"]+)")')


def _page_slugs(forms: list[tuple[re.Match, dict]], values) -> list[str]:
    """The slugs of ``values(meta)`` over every form of a page, in page order, each once."""
    slugs: list[str] = []
    for _, meta in forms:
        for value in values(meta):
            if _slug(value) not in slugs:
                slugs.append(_slug(value))
    return slugs


# The hub's hero art, one image per form, named by the form's heading anchor.
_FULL_ART_BASE = "https://d2hl7maqck52px.cloudfront.net/heroes-of-rathe/full-hero-art"


def _playstyle_names(meta: dict) -> list[str]:
    return (meta.get("fabtcg") or {}).get("playstyles", [])


def _hub_forms(page: str, forms: list[tuple[re.Match, dict]]) -> list[dict]:
    """Each of ``page``'s ``forms``, oldest first, for hero-hub.js to pick from; ``[]`` for one form."""
    if len(forms) < 2:
        return []
    return [
        {
            "id": form_id,
            "name": heading,
            "art": f"{_FULL_ART_BASE}/{form_id}.webp",
            "talents": [_slug(t) for t in meta["talents"]],
            "playstyles": [_slug(p) for p in _playstyle_names(meta)],
        }
        for form_id, heading, meta in _in_release_order(page, forms)
    ]


_CARD_IMG_SRC_RE = re.compile(r'<img\b[^>]*?\ssrc="([^"]+)"')


def render_hero_hub(content: str, pages: dict[str, str], data: dict) -> str:
    """Give each hub card ``data-talents`` and ``data-playstyles`` lists from the H1 forms on the page it links to.

    ``pages`` maps a hero page's path, relative to the hub, to its markdown.

    A card for a page with two or more forms also gets ``data-forms``
    (:func:`_hub_forms`), so hero-hub.js can show and link to the form a filter
    matches, and its link gains the anchor of the form its image shows: the
    page would otherwise open on its newest form.
    """

    def annotate(m: re.Match) -> str:
        href = m.group(3)
        page = pages.get(href, "")
        page_forms = hero_forms(page, data)
        talents = " ".join(_page_slugs(page_forms, lambda meta: meta["talents"]))
        playstyles = " ".join(_page_slugs(page_forms, _playstyle_names))
        attrs = f' data-talents="{talents}" data-playstyles="{playstyles}"'
        forms = _hub_forms(page, page_forms)
        if not forms:
            return f"{m.group(1)}{attrs}{m.group(2)}"
        close = content.find("</a>", m.end())
        img = _CARD_IMG_SRC_RE.search(content, m.end(), close if close != -1 else len(content))
        shown = next((f["id"] for f in forms if img and f["art"] == html.unescape(img.group(1))), None)
        attrs += f' data-forms="{html.escape(json.dumps(forms, ensure_ascii=False))}"'
        return f'{m.group(1)}{attrs} href="{href}#{shown}"' if shown else f"{m.group(1)}{attrs}{m.group(2)}"

    return _HUB_CARD_RE.sub(annotate, content)


# ---------------------------------------------------------------------------
# mdBook walk
# ---------------------------------------------------------------------------

_HERO_DIR = "heroes-of-rathe/"


_HUB_PATH = "heroes-of-rathe/heroes-of-rathe.md"


def _walk_sections(sections: list, data: dict) -> None:
    chapters = list(iter_chapters(sections))
    # The hub reads the hero pages as written, before any stat block goes in.
    pages = {
        Path(path).as_posix()[len(_HERO_DIR) :]: ch.get("content") or ""
        for ch in chapters
        if (path := (ch.get("path") or "").strip()) and _is_hero_about_page(path)
    }
    for ch in chapters:
        path = Path((ch.get("path") or "").strip()).as_posix()
        if _is_hero_about_page(path):
            ch["content"] = render_hero_page(ch.get("content") or "", data)
        elif path == _HUB_PATH:
            ch["content"] = render_hero_hub(ch.get("content") or "", pages, data)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main() -> None:
    """stdin: ``(PreprocessorContext, Book)`` JSON; stdout: ``Book`` JSON only."""
    run(lambda items, src_root: _walk_sections(items, load_hero_data(src_root / "data")))


if __name__ == "__main__":
    main()
