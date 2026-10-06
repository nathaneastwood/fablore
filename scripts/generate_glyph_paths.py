#!/usr/bin/env python3
"""Outline the Rathe script faces into JSON for the SVG export.

The translator on the language pages offers an SVG download whose glyphs are
real paths, so a printer can scale the artwork without the typeface being
installed. The browser cannot read outlines from a webfont, so they are
extracted here, once, from the .otf files in theme/fonts/.

Writes src/languages/glyphs/<script>.json. mdBook copies those to the site
unchanged, and glyph-tool.js fetches one only when a reader asks for an SVG.
Re-run after a font file changes:

    python3 scripts/generate_glyph_paths.py

Needs fonttools (in requirements-dev.txt). Advance widths and, for Runetura, kern
pairs are the only layout the SVG export has to reproduce.
"""

import json
import string
from pathlib import Path

from fontTools.pens.recordingPen import RecordingPen
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parent.parent
FONTS = ROOT / "theme" / "fonts"
OUT = ROOT / "src" / "languages" / "glyphs"

# Each file is the one the site serves as the script's webfont, so the SVG and
# the on-page rendering share advance widths. Arcane is Runetura, not
# ArcaneRathe-Regular: see the header of theme/glyph-tool.css.
SCRIPTS = {
    "arcane": "Runetura.woff2",
    "okana": "OkanaRathe-Regular.otf",
    "seers": "SeersRathe-Regular.otf",
    "solanian": "SolanianRathe-Regular.otf",
}

# Letters are stored once, upper case: every face maps a and A to one glyph.
CHARS = string.ascii_uppercase + " "


def num(v: float) -> str:
    v = round(v, 1)
    return str(int(v)) if v == int(v) else str(v)


def outline(glyph_set, name: str) -> str:
    """Absolute M/L/C/Z path in font units, y flipped so the baseline is 0 and up is negative."""
    pen = RecordingPen()
    glyph_set[name].draw(pen)
    parts = []
    for op, pts in pen.value:
        if op == "moveTo":
            letter = "M"
        elif op == "lineTo":
            letter = "L"
        elif op == "curveTo":
            letter = "C"
        elif op in ("closePath", "endPath"):
            parts.append("Z")
            continue
        else:
            raise ValueError(f"unexpected pen operation {op!r} in {name}")
        coords = " ".join(f"{num(x)} {num(-y)}" for x, y in pts)
        parts.append(f"{letter} {coords}")
    return " ".join(parts)


def kerning(font, names: dict) -> dict:
    """Pair adjustments from a plain-pairs GPOS kern lookup, keyed by the two characters.

    Browsers apply kerning by default, so an SVG that only summed advance
    widths would come out wider than the page and the PNG. Runetura is the one
    face that has any. Anything beyond explicit pairs would need a fuller
    shaper, so it is refused rather than silently dropped.
    """
    if "GPOS" not in font:
        return {}
    chars = {glyph: ch for ch, glyph in names.items()}
    pairs = {}
    for lookup in font["GPOS"].table.LookupList.Lookup:
        for sub in lookup.SubTable:
            if lookup.LookupType != 2 or sub.Format != 1:
                raise ValueError("GPOS holds more than explicit kern pairs")
            firsts = sub.Coverage.glyphs
            for first, pair_set in zip(firsts, sub.PairSet):
                for rec in pair_set.PairValueRecord:
                    value = getattr(rec.Value1, "XAdvance", 0) if rec.Value1 else 0
                    a, b = chars.get(first), chars.get(rec.SecondGlyph)
                    if value and a and b:
                        pairs[a + b] = value
    return pairs


def build(font_file: str) -> dict:
    font = TTFont(FONTS / font_file)
    cmap = font.getBestCmap()
    glyphs = font.getGlyphSet()
    for ch in string.ascii_lowercase:
        assert cmap[ord(ch)] == cmap[ord(ch.upper())], f"{ch} and {ch.upper()} differ"
    hhea = font["hhea"]
    return {
        "upm": font["head"].unitsPerEm,
        # Canvas "middle" puts the baseline this far below the line's centre.
        "drop": (hhea.ascent + hhea.descent) / 2,
        "adv": {ch: glyphs[cmap[ord(ch)]].width for ch in CHARS},
        "kern": kerning(font, {ch: cmap[ord(ch)] for ch in CHARS}),
        "d": {ch: outline(glyphs, cmap[ord(ch)]) for ch in CHARS if ch != " "},
    }


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for key, font_file in SCRIPTS.items():
        path = OUT / f"{key}.json"
        path.write_text(json.dumps(build(font_file), separators=(",", ":")) + "\n")
        print(f"{path.relative_to(ROOT)}  {path.stat().st_size // 1024} KB")


if __name__ == "__main__":
    main()
