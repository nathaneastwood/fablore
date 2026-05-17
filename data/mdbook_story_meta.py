#!/usr/bin/env python3
"""mdBook preprocessor: inject a story metadata card after the title of story chapters.

Reads ``stories.csv`` and, for each chapter whose path matches a ``StoryKey``,
builds a single HTML card showing authors, artists, publication date, source link,
and word count / estimated reading time.  Fields are omitted when empty.
The card is inserted after the first H1 heading in the chapter content.

mdBook passes ``(PreprocessorContext, Book)`` as JSON on stdin; this process must
print only the modified ``Book`` JSON on stdout.  Supports ``supports <renderer>``.
"""

from __future__ import annotations

import html
import json
import re
import sys
from datetime import datetime
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from pipe_csv_io import read_pipe_csv  # noqa: E402

MARK_START = "<!-- fablore-story-meta:start -->"
MARK_END = "<!-- fablore-story-meta:end -->"

_WORDS_PER_MINUTE = 250
_MIN_WORDS_FOR_READTIME = 50


def _count_words(markdown: str) -> int:
    """Count prose words in markdown, stripping markup and syntax."""
    text = re.sub(r"```[\s\S]*?```", "", markdown)
    text = re.sub(r"`[^`]*`", "", text)
    text = re.sub(r"<!--[\s\S]*?-->", "", text)
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", text)
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"\[([^\]]*)\]\[[^\]]*\]", r"\1", text)
    text = re.sub(r"^#{1,6}\s+", "", text, flags=re.MULTILINE)
    text = re.sub(r"\*{1,3}|_{1,3}", "", text)
    return len(text.split())


def _format_date(date_str: str) -> str:
    """Format ``YYYY-MM-DD`` as ``D Month YYYY``.  Returns the raw string on failure."""
    s = date_str.strip()
    if not s:
        return ""
    try:
        dt = datetime.strptime(s, "%Y-%m-%d")
        return f"{dt.day} {dt.strftime('%B %Y')}"
    except ValueError:
        pass
    # Handle swapped month/day (e.g. ``2019-29-08``)
    parts = s.split("-")
    if len(parts) == 3:
        try:
            dt = datetime(int(parts[0]), int(parts[2]), int(parts[1]))
            return f"{dt.day} {dt.strftime('%B %Y')}"
        except (ValueError, IndexError):
            pass
    return s


def _item(icon: str, inner: str) -> str:
    return (
        f'<span class="story-meta-item">'
        f'<i class="fa {icon}" aria-hidden="true"></i>'
        f" {inner}</span>"
    )


def _build_meta_html(
    *,
    authors: str,
    artists: str,
    publication_date: str,
    source_link: str,
    word_count: int,
) -> str:
    """Return the ``story-meta`` div HTML, or an empty string when nothing to show."""
    items: list[str] = []

    if authors:
        items.append(_item("fa-pencil", f"Written by <strong>{html.escape(authors)}</strong>"))

    if artists:
        items.append(_item("fa-image", f"Art by <strong>{html.escape(artists)}</strong>"))

    formatted_date = _format_date(publication_date)
    if formatted_date:
        items.append(_item("fa-calendar", html.escape(formatted_date)))

    if source_link:
        link_esc = html.escape(source_link)
        items.append(
            _item(
                "fa-external-link",
                f'<a href="{link_esc}" target="_blank" rel="noopener">Original article</a>',
            )
        )

    if word_count > 0:
        count_fmt = f"{word_count:,}"
        if word_count >= _MIN_WORDS_FOR_READTIME:
            minutes = max(1, round(word_count / _WORDS_PER_MINUTE))
            time_label = f"{minutes} min read"
            wc_text = f"{count_fmt} words · {time_label}"
        else:
            wc_text = f"{count_fmt} words"
        items.append(_item("fa-clock-o", wc_text))

    if not items:
        return ""

    inner = "\n  ".join(items)
    return f'<div class="story-meta" aria-label="Story information">\n  {inner}\n</div>'


def _inject_after_heading(content: str, inner_html: str) -> str:
    """Insert or replace the story-meta block after the first H1 in ``content``."""
    if MARK_START in content and MARK_END in content:
        pre, _, rest = content.partition(MARK_START)
        _, _, post = rest.partition(MARK_END)
        bare = pre.rstrip() + ("\n\n" if pre.strip() else "") + post.lstrip()
    else:
        bare = content

    if not inner_html.strip():
        return bare

    block = f"{MARK_START}\n{inner_html}\n{MARK_END}"
    match = re.search(r"^#{1,6}[^\n]*\n", bare, flags=re.MULTILINE)
    if match:
        cut = match.end()
        return bare[:cut] + "\n" + block + "\n\n" + bare[cut:].lstrip("\n")
    return block + "\n\n" + bare


def _load_story_meta(data_dir: Path) -> dict[str, dict[str, str]]:
    """Return a map from ``StoryKey`` (POSIX path) to its ``stories.csv`` row."""
    path = data_dir / "csv" / "stories.csv"
    if not path.is_file():
        return {}
    _fn, rows = read_pipe_csv(path)
    return {
        Path(r["StoryKey"]).as_posix(): r
        for r in rows
        if (r.get("StoryKey") or "").strip()
    }


def _process_chapter(content: str, row: dict[str, str]) -> str:
    """Inject the story-meta block for one chapter."""
    # Strip any existing block before counting so injected HTML is excluded
    if MARK_START in content and MARK_END in content:
        pre, _, rest = content.partition(MARK_START)
        _, _, post = rest.partition(MARK_END)
        bare_for_count = pre + post
    else:
        bare_for_count = content
    word_count = _count_words(bare_for_count)
    inner = _build_meta_html(
        authors=(row.get("Authors") or "").strip(),
        artists=(row.get("Artists") or "").strip(),
        publication_date=(row.get("PublicationDate") or "").strip(),
        source_link=(row.get("SourceLink") or "").strip(),
        word_count=word_count,
    )
    return _inject_after_heading(content, inner)


def _walk_sections(
    sections: list,
    meta_by_key: dict[str, dict[str, str]],
) -> None:
    for item in sections:
        if not isinstance(item, dict):
            continue
        if "Chapter" in item:
            ch = item["Chapter"]
            path = (ch.get("path") or "").strip()
            if path:
                row = meta_by_key.get(Path(path).as_posix())
                if row is not None:
                    ch["content"] = _process_chapter(ch.get("content") or "", row)
            _walk_sections(ch.get("sub_items") or [], meta_by_key)


def main() -> None:
    """stdin: ``(PreprocessorContext, Book)`` JSON; stdout: ``Book`` JSON only."""
    if len(sys.argv) >= 3 and sys.argv[1] == "supports":
        sys.exit(0)

    ctx, book = json.load(sys.stdin)
    root = Path(ctx["root"])
    book_cfg = (ctx.get("config") or {}).get("book") or {}
    src_rel = (book_cfg.get("src") or "src").strip() or "src"
    src_root = (root / src_rel).resolve()
    data_dir = src_root / "data"

    meta_by_key = _load_story_meta(data_dir)
    _walk_sections(book.get("sections") or [], meta_by_key)

    json.dump(book, sys.stdout, ensure_ascii=False)


if __name__ == "__main__":
    main()
