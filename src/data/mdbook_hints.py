#!/usr/bin/env python3
"""mdBook preprocessor: auto-detect hint terms and inject tooltip spans.

Reads src/hints.json, finds the first unprotected occurrence of each term per
chapter (word-boundary match, case-insensitive), and wraps it in:

    <span class="hint" hint="Key">matched text</span>

Suppression rules:
  Option A: if a match string appears in any ##/### heading, skip that hint
  Option C: per-hint "exclude_pages" list in hints.json
  Option D: if an entity is mentioned on exactly one page in the whole book, skip
            it everywhere — that page introduces and explains it, so a tooltip
            would only restate the surrounding prose

Generated reference tables under data/ are excluded from both detection and the
Option D count, since they name every entity and would distort both.

Protected regions (no injection):
  fenced code blocks, inline code spans, Markdown links/images, HTML tags,
  headings (all levels), existing hint spans, and a hero page's banner (its
  ``:::hero-blurb`` block, or the rendered ``<header class="hero-banner">``).

Backward compat: old [Text](~Key) markup is still converted and its key is
excluded from auto-detection so the term is not double-wrapped.
"""

from __future__ import annotations

import json
import re
import sys
from functools import lru_cache
from pathlib import Path

# ---------------------------------------------------------------------------
# Regex constants
# ---------------------------------------------------------------------------

_FENCED_CODE = re.compile(r"(?:```|~~~)[^\n]*\n[\s\S]*?(?:```|~~~)", re.MULTILINE)
_CODE_SPAN = re.compile(r"`[^`\n]+`")
_LINK = re.compile(r"!?\[(?:[^\]]*)\](?:\([^)]*\)|\[[^\]]*\])")
_SCRIPT_BLOCK = re.compile(r"<script\b[^>]*>[\s\S]*?</script>", re.IGNORECASE)
_HTML_TAG = re.compile(r"<[^>]+>")
_HINT_ELEMENT = re.compile(
    r'<span\b[^>]*class="hint"[^>]*>[\s\S]*?</span>',
)
_ALL_HEADINGS = re.compile(r"^#{1,6}[^\S\n]+.+$", re.MULTILINE)
_SECTION_HEADINGS = re.compile(r"^#{2,3}[^\S\n]+(.+?)(?:[^\S\n]*#+)?\s*$", re.MULTILINE)
# A hero banner's blurb, before (raw block) or after (inside the banner) mdbook_hero_meta.
_HERO_BLURB_BLOCK = re.compile(r"^:::hero-blurb[^\n]*\n[\s\S]*?^:::[^\S\n]*$", re.MULTILINE)
_HERO_BANNER = re.compile(r'<header class="hero-banner\b[\s\S]*?</header>')
_OLD_HINT = re.compile(r"\[([^\]]+)\]\(~([^)]+)\)")

# The only non-ASCII characters that ``re.IGNORECASE`` lets match an ASCII one.
# ``str.lower()`` alone cannot stand in for the regex: ``ı`` and ``ſ`` do not
# lowercase to ASCII at all, and ``İ`` lowercases to two characters. Folding
# these first is what makes :func:`_may_occur` a safe prefilter.
# tests/test_mdbook_hints.py re-derives this table from the running interpreter.
_REGEX_ASCII_FOLD = str.maketrans({"\u0130": "i", "\u0131": "i", "\u017f": "s", "\u212a": "k"})
_NON_ASCII_RUN = re.compile(r"[^\x00-\x7f]+")

# Entity type no longer gates auto-detection. It used to: only DB-backed types
# (location/monster/fauna/flora) were eligible, on the grounds that characters, factions
# and the like are introduced and described in-story. That reasoning is sound but
# applies to the *page* that introduces an entity, not to the entity forever — it
# left long-established characters such as Nasreth with no tooltip on any of the
# eight pages naming them. See compute_single_page_keys for the replacement.

# ---------------------------------------------------------------------------
# Public helpers (importable for tests)
# ---------------------------------------------------------------------------


def load_hints(path: Path) -> dict:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def get_match_strings(key: str, entry) -> list[str]:
    """Return the text strings to search for in chapter content."""
    if isinstance(entry, dict):
        m = entry.get("match")
        if m is not None:
            return [m] if isinstance(m, str) else list(m)
    return [key]


def find_protected_regions(content: str) -> list[tuple[int, int]]:
    """Return (start, end) byte ranges that must not be modified."""
    regions: list[tuple[int, int]] = []
    for pattern in (
        _SCRIPT_BLOCK,
        _HERO_BLURB_BLOCK,
        _HERO_BANNER,
        _FENCED_CODE,
        _CODE_SPAN,
        _LINK,
        _HINT_ELEMENT,
        _HTML_TAG,
        _ALL_HEADINGS,
    ):
        for m in pattern.finditer(content):
            regions.append((m.start(), m.end()))
    return regions


def extract_section_heading_texts(content: str) -> list[str]:
    """Return text of every ## and ### heading (for Option A suppression)."""
    return [m.group(1).strip() for m in _SECTION_HEADINGS.finditer(content)]


def page_slug_from_path(path: str | None) -> str:
    """Derive a page slug from a chapter path (e.g. 'Solana/guide.md' → 'Solana/guide')."""
    if not path:
        return ""
    return Path(path).with_suffix("").as_posix()


@lru_cache(maxsize=None)
def _matcher(match_string: str) -> tuple[tuple[str, ...], re.Pattern]:
    """Return a match string's prefilter runs and its compiled word-boundary pattern.

    The runs are the string's ASCII stretches, lowercased. A regex match needs
    each of them, contiguously, in the page folded by :func:`_fold`, so a page
    missing any run cannot match and is skipped without running the regex.
    """
    runs = tuple(r for r in _NON_ASCII_RUN.split(match_string.lower()) if r)
    return runs, re.compile(r"\b" + re.escape(match_string) + r"\b", re.IGNORECASE)


def _fold(text: str) -> str:
    """Lowercase ``text`` so an ASCII run of a match string is found by ``in``."""
    return text.translate(_REGEX_ASCII_FOLD).lower()


def _may_occur(match_string: str, folded: str) -> bool:
    """Cheap necessary condition for ``match_string`` to match the folded text.

    It may admit a page the regex then rejects, but it never rejects a page the
    regex would match.
    """
    return all(run in folded for run in _matcher(match_string)[0])


def process_chapter(
    content: str,
    hints: dict,
    page_slug: str = "",
    single_page_keys: frozenset[str] = frozenset(),
) -> str:
    """Transform a single chapter's Markdown content.

    Args:
        content: The chapter's Markdown.
        hints: Loaded ``hints.json``.
        page_slug: This chapter's slug, for ``exclude_pages`` matching.
        single_page_keys: Keys mentioned on only one page across the whole book;
            see :func:`compute_single_page_keys`.
    """
    # --- Step 1: convert old [Text](~Key) markup ---
    manually_handled: set[str] = set()

    def _replace_old(m: re.Match) -> str:
        text, key = m.group(1), m.group(2)
        manually_handled.add(key)
        return f'<span class="hint" hint="{key}">{text}</span>'

    content = _OLD_HINT.sub(_replace_old, content)

    # --- Step 2: build candidate list ---
    heading_texts = extract_section_heading_texts(content)
    folded = _fold(content)

    # (key, longest match string length, patterns of the strings that may occur)
    candidates: list[tuple[str, int, list[re.Pattern]]] = []
    for key, entry in hints.items():
        if key in manually_handled:
            continue

        # Any entry with a summary is eligible — there is something to put in the
        # tooltip. Entity type is deliberately not consulted: whether a tooltip is
        # wanted depends on where the entity is mentioned, not what kind of thing
        # it is. See Option D below and _single_page_keys.
        if not isinstance(entry, dict) or not entry.get("summary"):
            continue

        # Option D: an entity mentioned on exactly one page is introduced and
        # explained there, so a tooltip would restate the surrounding prose.
        if key in single_page_keys:
            continue

        # Option C: exclude_pages
        exclude = entry.get("exclude_pages") or []
        if page_slug and page_slug in exclude:
            continue

        match_strings = get_match_strings(key, entry)

        # A string absent from the page can neither suppress the hint (headings
        # are part of the page) nor be wrapped, so only the present ones matter.
        patterns = [_matcher(ms)[1] for ms in match_strings if _may_occur(ms, folded)]
        if not patterns:
            continue

        # Option A: skip if any match string appears as a word in any ##/### heading
        if any(p.search(h) for p in patterns for h in heading_texts):
            continue

        candidates.append((key, max(len(s) for s in match_strings), patterns))

    # Longest match string first — prevents "Sol" shadowing "Solarium"
    candidates.sort(key=lambda x: x[1], reverse=True)

    # --- Step 3: find first unprotected occurrence of each candidate ---
    protected = find_protected_regions(content)
    replacements: list[tuple[int, int, str]] = []

    for key, _length, patterns in candidates:
        found = False
        for pattern in patterns:
            for m in pattern.finditer(content):
                start, end = m.start(), m.end()
                if _in_protected(start, end, protected):
                    continue
                if _overlaps(start, end, replacements):
                    continue
                replacements.append((start, end, f'<span class="hint" hint="{key}">{m.group()}</span>'))
                found = True
                break
            if found:
                break

    # --- Step 4: apply replacements end-to-start to preserve positions ---
    replacements.sort(key=lambda x: x[0], reverse=True)
    for start, end, replacement in replacements:
        content = content[:start] + replacement + content[end:]

    return content


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _in_protected(start: int, end: int, regions: list[tuple[int, int]]) -> bool:
    return any(rs <= start and end <= re_ for rs, re_ in regions)


def _overlaps(start: int, end: int, replacements: list[tuple[int, int, str]]) -> bool:
    return any(rs < end and start < re_ for rs, re_, _ in replacements)


# ---------------------------------------------------------------------------
# mdBook preprocessor entry point
# ---------------------------------------------------------------------------


def _iter_chapters(sections: list):
    """Yield ``(slug, chapter)`` for every chapter, depth first, skipping generated pages.

    Separators and part titles are not dicts carrying a ``Chapter``, so they are
    passed over rather than indexed.
    """
    for section in sections:
        chapter = section.get("Chapter") if isinstance(section, dict) else None
        if not chapter:
            continue
        slug = page_slug_from_path(chapter.get("path"))
        if not _is_generated_page(slug):
            yield slug, chapter
        yield from _iter_chapters(chapter.get("sub_items") or [])


def _collect_chapters(sections: list, out: list[tuple[str, str]]) -> list[tuple[str, str]]:
    """Flatten the book into ``(slug, content)`` pairs, skipping generated pages."""
    out.extend((slug, chapter.get("content") or "") for slug, chapter in _iter_chapters(sections))
    return out


def compute_single_page_keys(chapters: list[tuple[str, str]], hints: dict) -> frozenset[str]:
    """Return hint keys mentioned on exactly one page across the whole book.

    An entity named on a single page is, by definition, introduced and explained
    there — Gawain and Marbles appear only in *A Rising Star*, Kien only in
    *Letters from the Beyond*. Wrapping those in a tooltip restates the sentence
    the reader is already looking at, which is the redundancy this avoids.

    An entity named on several pages is the opposite case: a reader arriving at
    any page but the first has no context, so every mention earns a tooltip.

    Counting mentions rather than consulting ``SUMMARY.md`` order matters: the
    world lore pages are ordered alphabetically, not narratively, so "the first
    page that mentions it" is not reliably the page that introduces it — Sol
    would be pinned to the Demonastery page purely because D precedes S.

    Args:
        chapters: ``(slug, content)`` pairs for every rendered page.
        hints: Loaded ``hints.json``.

    Returns:
        The keys to skip entirely.
    """
    folded_chapters = [(content, _fold(content)) for _slug, content in chapters]
    singles: set[str] = set()
    for key, entry in hints.items():
        if not isinstance(entry, dict) or not entry.get("summary"):
            continue
        match_strings = get_match_strings(key, entry)
        pages = 0
        for content, folded in folded_chapters:
            if any(_may_occur(ms, folded) and _matcher(ms)[1].search(content) for ms in match_strings):
                pages += 1
                if pages > 1:
                    break
        if pages == 1:
            singles.add(key)
    return frozenset(singles)


def _is_generated_page(slug: str) -> bool:
    """True for generated reference tables, which list every entity by name.

    ``data/md/characters.md`` and friends are produced by ``create_md.py``. Auto-linking
    there would make each row link to a tooltip describing itself, and would also
    inflate the mention count so that genuinely single-page entities look shared.
    """
    return slug.startswith("data/")


def _process_sections(sections: list, hints: dict, single_page_keys: frozenset[str]) -> None:
    for slug, chapter in _iter_chapters(sections):
        chapter["content"] = process_chapter(chapter["content"], hints, slug, single_page_keys)


def main() -> None:
    if len(sys.argv) >= 3 and sys.argv[1] == "supports":
        sys.exit(0)

    db_path = Path(__file__).resolve().parents[2] / "src" / "data" / "fablore.db"
    if db_path.exists():
        from generate_hints_json import generate

        generate(quiet=True)

    hints_path = Path(__file__).resolve().parents[2] / "src" / "hints.json"
    hints = load_hints(hints_path) if hints_path.exists() else {}

    ctx, book = json.load(sys.stdin)
    items = book.get("items") or []
    single_page_keys = compute_single_page_keys(_collect_chapters(items, []), hints)
    _process_sections(items, hints, single_page_keys)
    json.dump(book, sys.stdout, ensure_ascii=False)


if __name__ == "__main__":
    main()
