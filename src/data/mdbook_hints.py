#!/usr/bin/env python3
"""mdBook preprocessor: auto-detect hint terms and inject tooltip spans.

Reads src/hints.json, finds the first unprotected occurrence of each term per
chapter (word-boundary match, case-insensitive), and wraps it in:

    <span class="hint" hint="Key">matched text</span>

Suppression rules:
  Option A: if a match string appears in any ##/### heading, skip that hint
  Option C: per-hint "exclude_pages" list in hints.json

Protected regions (no injection):
  fenced code blocks, inline code spans, Markdown links/images, HTML tags,
  headings (all levels), and existing hint spans.

Backward compat: old [Text](~Key) markup is still converted and its key is
excluded from auto-detection so the term is not double-wrapped.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Regex constants
# ---------------------------------------------------------------------------

_FENCED_CODE = re.compile(r'(?:```|~~~)[^\n]*\n[\s\S]*?(?:```|~~~)', re.MULTILINE)
_CODE_SPAN = re.compile(r'`[^`\n]+`')
_LINK = re.compile(r'!?\[(?:[^\]]*)\](?:\([^)]*\)|\[[^\]]*\])')
_SCRIPT_BLOCK = re.compile(r'<script\b[^>]*>[\s\S]*?</script>', re.IGNORECASE)
_HTML_TAG = re.compile(r'<[^>]+>')
_HINT_ELEMENT = re.compile(
    r'<span\b[^>]*class="hint"[^>]*>[\s\S]*?</span>',
)
_ALL_HEADINGS = re.compile(r'^#{1,6}[^\S\n]+.+$', re.MULTILINE)
_SECTION_HEADINGS = re.compile(r'^#{2,3}[^\S\n]+(.+?)(?:[^\S\n]*#+)?\s*$', re.MULTILINE)
_OLD_HINT = re.compile(r'\[([^\]]+)\]\(~([^)]+)\)')

# Entity types sourced from the DB — the only types eligible for auto-detection.
# Supplement-only types (npc, faction, aesir, ancient, concept, etc.) are
# intentionally excluded: they are introduced and described in-story, so
# auto-linking them produces redundant or context-breaking tooltips.
# Manual [Text](~Key) markup still works for any type.
_AUTO_DETECT_TYPES = frozenset({"location", "monster", "fauna", "flora"})

# ---------------------------------------------------------------------------
# Public helpers (importable for tests)
# ---------------------------------------------------------------------------


def load_hints(path: Path) -> dict:
    with path.open(encoding='utf-8') as f:
        return json.load(f)


def get_match_strings(key: str, entry) -> list[str]:
    """Return the text strings to search for in chapter content."""
    if isinstance(entry, dict):
        m = entry.get('match')
        if m is not None:
            return [m] if isinstance(m, str) else list(m)
    return [key]


def find_protected_regions(content: str) -> list[tuple[int, int]]:
    """Return (start, end) byte ranges that must not be modified."""
    regions: list[tuple[int, int]] = []
    for pattern in (
        _SCRIPT_BLOCK,
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
        return ''
    return Path(path).with_suffix('').as_posix()


def process_chapter(
    content: str,
    hints: dict,
    page_slug: str = '',
) -> str:
    """Transform a single chapter's Markdown content."""
    # --- Step 1: convert old [Text](~Key) markup ---
    manually_handled: set[str] = set()

    def _replace_old(m: re.Match) -> str:
        text, key = m.group(1), m.group(2)
        manually_handled.add(key)
        return f'<span class="hint" hint="{key}">{text}</span>'

    content = _OLD_HINT.sub(_replace_old, content)

    # --- Step 2: build candidate list ---
    heading_texts = extract_section_heading_texts(content)

    candidates: list[tuple[str, list[str]]] = []
    for key, entry in hints.items():
        if key in manually_handled:
            continue

        # Only auto-detect DB-backed entity types
        if not isinstance(entry, dict) or entry.get('type') not in _AUTO_DETECT_TYPES:
            continue

        # Option C: exclude_pages
        exclude = entry.get('exclude_pages') or []
        if page_slug and page_slug in exclude:
            continue

        match_strings = get_match_strings(key, entry)

        # Option A: skip if any match string appears as a word in any ##/### heading
        if _heading_suppressed(match_strings, heading_texts):
            continue

        candidates.append((key, match_strings))

    # Longest match string first — prevents "Sol" shadowing "Solarium"
    candidates.sort(key=lambda x: max(len(s) for s in x[1]), reverse=True)

    # --- Step 3: find first unprotected occurrence of each candidate ---
    protected = find_protected_regions(content)
    replacements: list[tuple[int, int, str]] = []

    for key, match_strings in candidates:
        found = False
        for ms in match_strings:
            pattern = re.compile(r'\b' + re.escape(ms) + r'\b', re.IGNORECASE)
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


def _heading_suppressed(match_strings: list[str], heading_texts: list[str]) -> bool:
    for ms in match_strings:
        pat = re.compile(r'\b' + re.escape(ms) + r'\b', re.IGNORECASE)
        if any(pat.search(h) for h in heading_texts):
            return True
    return False


def _in_protected(start: int, end: int, regions: list[tuple[int, int]]) -> bool:
    return any(rs <= start and end <= re_ for rs, re_ in regions)


def _overlaps(start: int, end: int, replacements: list[tuple[int, int, str]]) -> bool:
    return any(rs < end and start < re_ for rs, re_, _ in replacements)


# ---------------------------------------------------------------------------
# mdBook preprocessor entry point
# ---------------------------------------------------------------------------


def _process_sections(sections: list, hints: dict) -> None:
    for section in sections:
        chapter = section.get('Chapter')
        if not chapter:
            continue
        slug = page_slug_from_path(chapter.get('path'))
        chapter['content'] = process_chapter(chapter['content'], hints, slug)
        _process_sections(chapter.get('sub_items') or [], hints)


def main() -> None:
    if len(sys.argv) >= 3 and sys.argv[1] == 'supports':
        sys.exit(0)

    from generate_hints_json import generate
    generate()

    hints_path = Path(__file__).resolve().parents[2] / 'src' / 'hints.json'
    hints = load_hints(hints_path) if hints_path.exists() else {}

    ctx, book = json.load(sys.stdin)
    _process_sections(book.get('items') or [], hints)
    json.dump(book, sys.stdout, ensure_ascii=False)


if __name__ == '__main__':
    main()
