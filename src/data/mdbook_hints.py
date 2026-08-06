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
_OLD_HINT = re.compile(r"\[([^\]]+)\]\(~([^)]+)\)")

# Entity type no longer gates auto-detection. It used to: only DB-backed types
# (location/monster/fauna/flora) were eligible, on the grounds that NPCs, factions
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

    candidates: list[tuple[str, list[str]]] = []
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
            pattern = re.compile(r"\b" + re.escape(ms) + r"\b", re.IGNORECASE)
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
        pat = re.compile(r"\b" + re.escape(ms) + r"\b", re.IGNORECASE)
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


def _collect_chapters(sections: list, out: list[tuple[str, str]]) -> list[tuple[str, str]]:
    """Flatten the book into ``(slug, content)`` pairs, skipping generated pages."""
    for section in sections:
        chapter = section.get("Chapter")
        if not chapter:
            continue
        slug = page_slug_from_path(chapter.get("path"))
        if not _is_generated_page(slug):
            out.append((slug, chapter.get("content") or ""))
        _collect_chapters(chapter.get("sub_items") or [], out)
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
    singles: set[str] = set()
    for key, entry in hints.items():
        if not isinstance(entry, dict) or not entry.get("summary"):
            continue
        patterns = [re.compile(rf"\b{re.escape(s)}\b", re.IGNORECASE) for s in get_match_strings(key, entry)]
        pages = 0
        for _slug, content in chapters:
            if any(p.search(content) for p in patterns):
                pages += 1
                if pages > 1:
                    break
        if pages == 1:
            singles.add(key)
    return frozenset(singles)


def _is_generated_page(slug: str) -> bool:
    """True for generated reference tables, which list every entity by name.

    ``data/md/npcs.md`` and friends are produced by ``create_md.py``. Auto-linking
    there would make each row link to a tooltip describing itself, and would also
    inflate the mention count so that genuinely single-page entities look shared.
    """
    return slug.startswith("data/")


def _process_sections(sections: list, hints: dict, single_page_keys: frozenset[str]) -> None:
    for section in sections:
        chapter = section.get("Chapter")
        if not chapter:
            continue
        slug = page_slug_from_path(chapter.get("path"))
        if not _is_generated_page(slug):
            chapter["content"] = process_chapter(chapter["content"], hints, slug, single_page_keys)
        _process_sections(chapter.get("sub_items") or [], hints, single_page_keys)


def main() -> None:
    if len(sys.argv) >= 3 and sys.argv[1] == "supports":
        sys.exit(0)

    db_path = Path(__file__).resolve().parents[2] / "src" / "data" / "fablore.db"
    if db_path.exists():
        from generate_hints_json import generate

        generate()

    hints_path = Path(__file__).resolve().parents[2] / "src" / "hints.json"
    hints = load_hints(hints_path) if hints_path.exists() else {}

    ctx, book = json.load(sys.stdin)
    items = book.get("items") or []
    single_page_keys = compute_single_page_keys(_collect_chapters(items, []), hints)
    _process_sections(items, hints, single_page_keys)
    json.dump(book, sys.stdout, ensure_ascii=False)


if __name__ == "__main__":
    main()
