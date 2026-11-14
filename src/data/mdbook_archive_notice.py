#!/usr/bin/env python3
"""mdBook preprocessor: inject a superseded-lore notice on archive pages.

Handles two archive subtrees, requiring no manual markup in source files:

  archive/world-of-rathe/**
    Links to world-of-rathe/{region}.md if that file exists.

  archive/heroes-of-rathe/{hero-era}.md  (skips the index page)
    Resolves the current hero page by trying progressively shorter slug
    prefixes until it finds heroes-of-rathe/{prefix}-about.md.
    e.g. rhinar-wtr → rhinar-about.md. The link text is that page's first
    H1, or the slug title-cased if it has none.

Adding a current page automatically upgrades the notice on the next build.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from mdbook_common import iter_chapters, relative_href, run  # noqa: E402

MARK_START = "<!-- fablore-archive-notice:start -->"
MARK_END = "<!-- fablore-archive-notice:end -->"

_H1_RE = re.compile(r"^(#\s+.+)$", re.MULTILINE)


def _display(slug: str) -> str:
    return slug.replace("-", " ").title()


_HEADING_RE = re.compile(r"^#\s+(.+?)\s*#*\s*$", re.MULTILINE)
_LINK_TEXT_SPECIALS = re.compile(r"([\\\[\]*_`<>])")


def _first_h1(path: Path) -> str | None:
    """The text of the first ``# `` heading in ``path``, or None if it has none."""
    m = _HEADING_RE.search(path.read_text(encoding="utf-8"))
    return m.group(1).strip() if m else None


def _link_text(text: str) -> str:
    """``text`` escaped for use inside ``[...]``: brackets, emphasis, code and HTML characters."""
    return _LINK_TEXT_SPECIALS.sub(r"\\\1", text)


def _world_notice(chapter_src_path: str, src_root: Path) -> str | None:
    """Return a [!WARNING] notice for archive/world-of-rathe/ chapters, or None."""
    parts = Path(chapter_src_path).parts
    if len(parts) < 3 or parts[0] != "archive" or parts[1] != "world-of-rathe":
        return None

    region = parts[2] if len(parts) > 3 else Path(parts[2]).stem
    target_src = f"world-of-rathe/{region}.md"

    if (src_root / target_src).is_file():
        href = relative_href(chapter_src_path, target_src)
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
            href = relative_href(chapter_src_path, target_src)
            # The page's own name ("Valda, Seismic Impact", "Arakni, 5l!p3d 7hru 7h3 Cr4x"),
            # not one rebuilt from the slug.
            heading = _first_h1(src_root / target_src)
            display = _link_text(heading) if heading else _display(prefix)
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
    for ch in iter_chapters(sections):
        path = (ch.get("path") or "").strip()
        if path:
            notice = _world_notice(path, src_root) or _hero_notice(path, src_root)
            if notice:
                ch["content"] = _inject_notice(ch.get("content") or "", notice)


def main() -> None:
    run(_walk)


if __name__ == "__main__":
    main()
