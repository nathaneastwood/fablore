"""Render Flesh and Blood card ability text as safe HTML.

Stdlib-only so the mdBook preprocessors can import it.
"""

from __future__ import annotations

import html
import re

ICON_BASE = "https://d2hl7maqck52px.cloudfront.net/card-icons"

# FaB game symbols: token letter -> (icon filename, alt text)
_SYMBOLS = {
    "p": ("icon_pwr.webp", "Power"),
    "r": ("icon_cost.webp", "Resource"),
    "h": ("icon_hp.webp", "Health"),
    "d": ("icon_def.webp", "Defense"),
    "i": ("icon_int.webp", "Intellect"),
    "t": ("icon_t.webp", "Tap"),
    "u": ("icon_u.webp", "Untap"),
    "c": ("icon_chi.webp", "Chi"),
}
_SYMBOL_RE = re.compile(r"\{([a-zA-Z])\}")
_BOLD_RE = re.compile(r"\*\*(.+?)\*\*")


def _symbol(m: re.Match) -> str:
    code = m.group(1).lower()
    if code not in _SYMBOLS:
        return m.group(0)
    icon, alt = _SYMBOLS[code]
    return f'<img src="{ICON_BASE}/{icon}" alt="{alt}" class="card-glyph">'


def _format_paragraph(paragraph: str) -> str:
    out = _SYMBOL_RE.sub(_symbol, html.escape(paragraph))
    return _BOLD_RE.sub(r"<b>\1</b>", out)


def format_ability_text(text: str) -> str:
    """Return ``text`` as ``<p>`` paragraphs with symbol icons and ``**bold**`` keywords.

    Upstream card text already bolds every keyword, so bold markup is all a keyword needs.
    """
    paragraphs = [p.strip() for p in re.split(r" {2,}|\n+", text) if p.strip()]
    return "".join(f"<p>{_format_paragraph(p)}</p>" for p in paragraphs)
