#!/usr/bin/env python3
"""mdBook preprocessor: inject a superseded-lore notice on archive pages.

Handles two archive subtrees:

  archive/world-of-rathe/**
    Links to world-of-rathe/{region}.md if that file exists. No markup needed;
    adding a current page upgrades the notice on the next build.

  archive/heroes-of-rathe/*.md  (skips the heroes-of-rathe.md hub)
    Each page names its current page with a one-line directive, e.g.
    ``:::archive-of heroes-of-rathe/rhinar-about.md:::`` (a ``src``-relative
    path). The directive line is removed from the output. The link text is
    the target's first H1, or its slug title-cased if it has none. A page
    with no directive, or one naming a file that does not exist, raises
    ValueError, which fails the build.
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


_HERO_ARCHIVE_DIR = ("archive", "heroes-of-rathe")
_HERO_ARCHIVE_HUB = "heroes-of-rathe.md"

# One directive line, plus the blank line after it, so removing it leaves the
# page exactly as it would read without the line.
_ARCHIVE_OF_RE = re.compile(r"^:::archive-of[ \t]+(\S+?)[ \t]*:::[ \t]*(?:\n|\Z)(?:[ \t]*\n)?", re.MULTILINE)


def _hero_archive(chapter_src_path: str, content: str, src_root: Path) -> tuple[str, str] | None:
    """The [!WARNING] notice for an archive/heroes-of-rathe/ page, and its content without the directive.

    Returns None for any other page, and for the hub page.

    Raises:
        ValueError: The page has no ``:::archive-of`` directive, or its target is not a file.
    """
    parts = Path(chapter_src_path).parts
    if len(parts) != 3 or parts[:2] != _HERO_ARCHIVE_DIR or parts[2] == _HERO_ARCHIVE_HUB:
        return None

    m = _ARCHIVE_OF_RE.search(content)
    if not m:
        raise ValueError(
            f"{chapter_src_path}: a hero archive page needs a ':::archive-of <src path>:::' line "
            "naming its current page"
        )
    target_src = m.group(1)
    if not (src_root / target_src).is_file():
        raise ValueError(f"{chapter_src_path}: ':::archive-of' names {target_src}, which does not exist")

    href = relative_href(chapter_src_path, target_src)
    # The page's own name ("Valda, Seismic Impact", "Arakni, 5l!p3d 7hru 7h3 Cr4x"),
    # not one rebuilt from the slug.
    heading = _first_h1(src_root / target_src)
    display = _link_text(heading) if heading else _display(Path(target_src).stem.removesuffix("-about"))
    msg = f"This hero overview has been superseded. For the current version, see [{display}]({href})."
    return f"> [!WARNING]\n> {msg}", content[: m.start()] + content[m.end() :]


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
        if not path:
            continue
        content = ch.get("content") or ""
        notice = _world_notice(path, src_root)
        if notice is None:
            hero = _hero_archive(path, content, src_root)
            if hero is None:
                continue
            notice, content = hero
        ch["content"] = _inject_notice(content, notice)


def main() -> None:
    run(_walk)


if __name__ == "__main__":
    main()
