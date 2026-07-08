#!/usr/bin/env python3
"""mdBook preprocessor: inject a superseded-lore notice on archive pages.

Handles two archive subtrees, requiring no manual markup in source files:

  archive/world-of-rathe/**
    Links to world-of-rathe/{region}.md if that file exists.

  archive/heroes-of-rathe/{hero-era}.md  (skips the index page)
    Resolves the current hero page by trying progressively shorter slug
    prefixes until it finds heroes-of-rathe/{prefix}-about.md.
    e.g. rhinar-wtr → rhinar-about.md

Adding a current page automatically upgrades the notice on the next build.
"""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

MARK_START = "<!-- fablore-archive-notice:start -->"
MARK_END = "<!-- fablore-archive-notice:end -->"

_H1_RE = re.compile(r"^(#\s+.+)$", re.MULTILINE)


def _display(slug: str) -> str:
    return slug.replace("-", " ").title()


def _relative_href(chapter_src_path: str, target_src_path: str) -> str:
    return Path(
        os.path.relpath(Path(target_src_path), start=Path(chapter_src_path).parent)
    ).as_posix()


def _world_notice(chapter_src_path: str, src_root: Path) -> str | None:
    """Return a [!WARNING] notice for archive/world-of-rathe/ chapters, or None."""
    parts = Path(chapter_src_path).parts
    if len(parts) < 3 or parts[0] != "archive" or parts[1] != "world-of-rathe":
        return None

    region = parts[2] if len(parts) > 3 else Path(parts[2]).stem
    target_src = f"world-of-rathe/{region}.md"

    if (src_root / target_src).is_file():
        href = _relative_href(chapter_src_path, target_src)
        msg = f"This lore has been superseded. For the current version, see [{_display(region)}]({href})."
    else:
        msg = "This lore has been superseded and is kept for historical reference."

    return f"> [!WARNING]\n> {msg}"


def _hero_notice(chapter_src_path: str, src_root: Path) -> str | None:
    """Return a [!WARNING] notice for archive/heroes-of-rathe/ individual pages, or None."""
    parts = Path(chapter_src_path).parts
    if len(parts) < 3 or parts[0] != "archive" or parts[1] != "heroes-of-rathe":
        return None

    stem = Path(parts[-1]).stem
    if stem == "heroes-of-rathe":
        return None

    # Try progressively shorter slug prefixes to find {prefix}-about.md
    components = stem.split("-")
    for length in range(len(components), 0, -1):
        prefix = "-".join(components[:length])
        target_src = f"heroes-of-rathe/{prefix}-about.md"
        if (src_root / target_src).is_file():
            href = _relative_href(chapter_src_path, target_src)
            display = _display(prefix)
            msg = f"This hero overview has been superseded. For the current version, see [{display}]({href})."
            return f"> [!WARNING]\n> {msg}"

    return f"> [!WARNING]\n> This hero overview has been superseded and is kept for historical reference."


def _inject_notice(content: str, notice: str) -> str:
    """Insert or replace the archive notice block after the first H1."""
    block = f"{MARK_START}\n{notice}\n{MARK_END}"

    if MARK_START in content and MARK_END in content:
        pre, _, rest = content.partition(MARK_START)
        _, _, post = rest.partition(MARK_END)
        return pre.rstrip() + "\n\n" + block + post

    m = _H1_RE.search(content)
    if m:
        return content[: m.end()] + "\n\n" + block + content[m.end() :]
    return block + "\n\n" + content


def _walk(sections: list, src_root: Path) -> None:
    for item in sections:
        if not isinstance(item, dict):
            continue
        if "Chapter" in item:
            ch = item["Chapter"]
            path = (ch.get("path") or "").strip()
            if path:
                notice = _world_notice(path, src_root) or _hero_notice(path, src_root)
                if notice:
                    ch["content"] = _inject_notice(ch.get("content") or "", notice)
            _walk(ch.get("sub_items") or [], src_root)


def main() -> None:
    if len(sys.argv) >= 3 and sys.argv[1] == "supports":
        sys.exit(0)

    ctx, book = json.load(sys.stdin)
    root = Path(ctx["root"])
    book_cfg = (ctx.get("config") or {}).get("book") or {}
    src_rel = (book_cfg.get("src") or "src").strip() or "src"
    src_root = (root / src_rel).resolve()

    _walk(book.get("items") or [], src_root)
    json.dump(book, sys.stdout, ensure_ascii=False)


if __name__ == "__main__":
    main()
