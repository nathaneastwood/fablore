#!/usr/bin/env python3
"""mdBook preprocessor: inject a superseded-lore notice on archive pages.

For every chapter under ``archive/world-of-rathe/``, inserts a notice banner
after the first H1 heading.  If ``world-of-rathe/{region}.md`` exists in the
book source the banner links to it; otherwise it omits the link.

The region is derived from the folder name — no manual configuration is needed.
Adding a current world page for any region will automatically upgrade its banner
on the next build.
"""

from __future__ import annotations

import html
import json
import os
import re
import sys
from pathlib import Path

MARK_START = "<!-- fablore-archive-notice:start -->"
MARK_END = "<!-- fablore-archive-notice:end -->"

_H1_RE = re.compile(r"^(#\s+.+)$", re.MULTILINE)


def _region_from_path(chapter_path: str) -> str | None:
    """Return the region slug for a chapter under archive/world-of-rathe/, else None."""
    parts = Path(chapter_path).parts
    if len(parts) < 3 or parts[0] != "archive" or parts[1] != "world-of-rathe":
        return None
    # archive/world-of-rathe/REGION/file.md  →  parts[2] is the region folder
    # archive/world-of-rathe/file.md         →  stem of parts[2] is the region
    return parts[2] if len(parts) > 3 else Path(parts[2]).stem


def _region_display(slug: str) -> str:
    return slug.replace("-", " ").title()


def _relative_href(chapter_src_path: str, target_src_path: str) -> str:
    return Path(
        os.path.relpath(Path(target_src_path), start=Path(chapter_src_path).parent)
    ).as_posix()


def _build_notice(chapter_src_path: str, region: str, src_root: Path) -> str:
    target_src = f"world-of-rathe/{region}.md"
    display = _region_display(region)

    if (src_root / target_src).is_file():
        href = html.escape(_relative_href(chapter_src_path, target_src))
        link = f'<a href="{href}">{html.escape(display)}</a>'
        msg = f"This lore has been superseded. For the current version, see {link}."
    else:
        msg = "This lore has been superseded and is kept for historical reference."

    return f'<div class="archive-notice" role="note">\n  {msg}\n</div>'


def _inject_notice(content: str, notice_html: str) -> str:
    """Insert or replace the archive notice block after the first H1."""
    block = f"{MARK_START}\n{notice_html}\n{MARK_END}"

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
            region = _region_from_path(path) if path else None
            if region:
                notice = _build_notice(path, region, src_root)
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

    _walk(book.get("sections") or [], src_root)
    json.dump(book, sys.stdout, ensure_ascii=False)


if __name__ == "__main__":
    main()
