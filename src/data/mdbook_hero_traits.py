#!/usr/bin/env python3
"""mdBook preprocessor: expand :::hero-trait fenced blocks into HTML.

Usage in markdown::

    :::hero-trait Power of Steam
    ![Power of Steam](https://d2hl7maqck52px.cloudfront.net/heroes-of-rathe/dash-power-of-steam.webp)
    Mechanologists are driven by the pursuit of alternative energy sources…
    :::

Each block is converted to a ``<div class="hero-container">`` structure that
is styled by ``hero.css``.  The preprocessor runs on every chapter; it is not
restricted to ``heroes-of-rathe/``.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from mdbook_common import iter_chapters, read_book, write_book  # noqa: E402

# Matches an entire :::hero-trait block (non-greedy).
# Group 1: title text
# Group 2: image alt text
# Group 3: image URL
# Group 4: description body (may be multiple lines, already stripped of leading whitespace)
_HERO_TRAIT_RE = re.compile(
    r"^:::hero-trait ([^\n]+)\n" r"!\[([^\]]*)\]\(([^)]+)\)\n" r"([\s\S]*?)" r"^:::",
    re.MULTILINE,
)


def _build_html(title: str, img_url: str, description: str) -> str:
    desc = description.strip()
    return (
        f'<article class="hero-trait">\n'
        f'<div class="hero-trait-medal"><img src="{img_url}" class="hero-icon" alt="{title}" /></div>\n'
        f'<h4 class="hero-trait-name">{title}</h4>\n'
        f"\n"
        f"{desc}\n"
        f"\n"
        f"</article>"
    )


def _expand(content: str) -> str:
    out: list[str] = []
    pos = 0
    run: list[str] = []
    for m in _HERO_TRAIT_RE.finditer(content):
        gap = content[pos : m.start()]
        if run and gap.strip():
            out.append(_wrap(run))
            run = []
        if not run:
            out.append(gap)
        run.append(_build_html(m.group(1).strip(), m.group(3).strip(), m.group(4)))
        pos = m.end()
    if run:
        out.append(_wrap(run))
    out.append(content[pos:])
    return "".join(out)


def _wrap(articles: list[str]) -> str:
    return '<div class="hero-traits">\n\n' + "\n\n".join(articles) + "\n\n</div>"


def _walk(sections: list) -> None:
    for ch in iter_chapters(sections):
        ch["content"] = _expand(ch.get("content") or "")


def main() -> None:
    _ctx, book = read_book()
    _walk(book.get("items") or [])
    write_book(book)


if __name__ == "__main__":
    main()
