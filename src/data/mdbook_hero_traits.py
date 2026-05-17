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

import json
import re
import sys

# Matches an entire :::hero-trait block (non-greedy).
# Group 1: title text
# Group 2: image alt text
# Group 3: image URL
# Group 4: description body (may be multiple lines, already stripped of leading whitespace)
_HERO_TRAIT_RE = re.compile(
    r"^:::hero-trait ([^\n]+)\n"
    r"!\[([^\]]*)\]\(([^)]+)\)\n"
    r"([\s\S]*?)"
    r"^:::",
    re.MULTILINE,
)


def _build_html(title: str, img_url: str, description: str) -> str:
    desc = description.strip()
    return (
        f'<div class="hero-container">\n'
        f'  <img src="{img_url}" class="hero-icon" alt="{title}" />\n'
        f'  <div class="hero-content">\n'
        f"    <b>{title}</b><br>\n"
        f"    {desc}\n"
        f"  </div>\n"
        f"</div>"
    )


def _expand(content: str) -> str:
    return _HERO_TRAIT_RE.sub(
        lambda m: _build_html(
            m.group(1).strip(),
            m.group(3).strip(),
            m.group(4),
        ),
        content,
    )


def _walk(sections: list) -> None:
    for item in sections:
        if not isinstance(item, dict):
            continue
        if "Chapter" in item:
            ch = item["Chapter"]
            ch["content"] = _expand(ch.get("content") or "")
            _walk(ch.get("sub_items") or [])


def main() -> None:
    if len(sys.argv) >= 3 and sys.argv[1] == "supports":
        sys.exit(0)

    ctx, book = json.load(sys.stdin)
    _walk(book.get("sections") or [])
    json.dump(book, sys.stdout, ensure_ascii=False)


if __name__ == "__main__":
    main()
