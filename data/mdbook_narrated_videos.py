#!/usr/bin/env python3
"""mdBook preprocessor: inject responsive narrated-video sections from CSV data.

Reads ``story-narrated-videos.csv`` (keyed by StoryId) and ``stories.csv``
(for StoryId → StoryKey mapping).  For each chapter that has narrated videos,
inserts or replaces the block between
``<!-- fablore-narrated-videos:start -->`` and
``<!-- fablore-narrated-videos:end -->`` markers at the end of the content.

Source ``.md`` files are expected to be pre-cleaned (no old manual sections).
The markers make re-runs idempotent.

Single video: plain responsive iframe + caption.
Multiple videos: accessible tab strip with avatar initials, one panel per narrator.

mdBook passes ``(PreprocessorContext, Book)`` as JSON on stdin; this process
must print only the modified ``Book`` JSON on stdout.  Supports
``supports <renderer>``.
"""

from __future__ import annotations

import html
import json
import sys
from pathlib import Path
from urllib.parse import parse_qs, urlparse

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from pipe_csv_io import read_pipe_csv  # noqa: E402

MARK_START = "<!-- fablore-narrated-videos:start -->"
MARK_END = "<!-- fablore-narrated-videos:end -->"

_AVATAR_COLORS = [
    "#4183c4",
    "#c0392b",
    "#27ae60",
    "#f39c12",
    "#8e44ad",
    "#16a085",
    "#d35400",
    "#2c3e50",
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _to_embed_url(url: str) -> str:
    """Convert a YouTube watch/short URL to an embed URL, preserving timestamps."""
    parsed = urlparse(url)
    if "youtube.com" not in parsed.netloc and "youtu.be" not in parsed.netloc:
        return url
    if "/embed/" in parsed.path:
        return url
    params = parse_qs(parsed.query)
    if "youtu.be" in parsed.netloc:
        video_id = parsed.path.lstrip("/")
    else:
        video_id = (params.get("v") or [""])[0]
    if not video_id:
        return url
    embed = f"https://www.youtube.com/embed/{video_id}"
    start = (params.get("t") or [""])[0].rstrip("s")
    if start.isdigit():
        embed += f"?start={start}"
    return embed


def _initials(name: str) -> str:
    """Return up to two uppercase initials from an author name."""
    import re

    words = [w for w in re.split(r"[\s_]+", name.strip()) if w]
    if not words:
        return "?"
    if len(words) == 1:
        return words[0][:2].upper()
    return (words[0][0] + words[-1][0]).upper()


def _avatar_color(name: str) -> str:
    return _AVATAR_COLORS[sum(ord(c) for c in name) % len(_AVATAR_COLORS)]


# ---------------------------------------------------------------------------
# HTML generation
# ---------------------------------------------------------------------------


def _build_html(story_id: str, videos: list[dict[str, str]]) -> str:
    """Return the full narrated-videos block HTML (without markers)."""
    if not videos:
        return ""

    plural = len(videos) > 1
    heading = "Narrated Videos" if plural else "Narrated Video"
    parts: list[str] = ['<div class="narrated-videos">', "", f"<h1>{heading}</h1>"]

    if plural:
        parts.append('<div class="nv-tabs" role="tablist">')
        for i, v in enumerate(videos):
            author = v["author"]
            panel_id = f"nv-{story_id}-{i}"
            color = _avatar_color(author)
            initials = _initials(author)
            active = " nv-tab--active" if i == 0 else ""
            selected = "true" if i == 0 else "false"
            parts.append(
                f'<button class="nv-tab{active}" '
                f"onclick=\"nvOpenTab(this,'{panel_id}')\" "
                f'role="tab" aria-selected="{selected}" aria-controls="{panel_id}">'
                f'<span class="nv-avatar" style="background-color:{color}">'
                f"{initials}</span>"
                f"{html.escape(author)}"
                f"</button>"
            )
        parts.append("</div>")

    for i, v in enumerate(videos):
        author = v["author"]
        embed_url = _to_embed_url(v["source_link"])
        panel_id = f"nv-{story_id}-{i}"

        if plural:
            hidden_class = "" if i == 0 else " nv-panel--hidden"
            hidden_attr = "" if i == 0 else " hidden"
            parts.append(
                f'<div class="nv-panel{hidden_class}" id="{panel_id}"'
                f' role="tabpanel"{hidden_attr}>'
            )
        else:
            parts.append('<div class="nv-single-video">')

        parts.append('<div class="nv-video-wrap">')
        parts.append(
            f'<iframe src="{html.escape(embed_url)}" title="YouTube video player"'
            ' frameborder="0"'
            ' allow="accelerometer; autoplay; clipboard-write; encrypted-media;'
            ' gyroscope; picture-in-picture; web-share"'
            ' referrerpolicy="strict-origin-when-cross-origin"'
            " allowfullscreen></iframe>"
        )
        parts.append("</div>")  # nv-video-wrap

        parts.append("</div>")  # nv-panel or nv-single-video

    parts += ["", "</div>"]  # narrated-videos
    return "\n".join(parts)


def _inject(content: str, story_id: str, videos: list[dict[str, str]]) -> str:
    """Insert or replace the narrated-videos block at the end of content."""
    inner_html = _build_html(story_id, videos)
    block = f"{MARK_START}\n{inner_html}\n{MARK_END}" if inner_html else ""

    if MARK_START in content and MARK_END in content:
        pre, _, rest = content.partition(MARK_START)
        _, _, post = rest.partition(MARK_END)
        bare = pre.rstrip() + "\n" + post.lstrip()
    else:
        bare = content.rstrip()

    if not block:
        return bare + "\n"
    return bare + "\n\n---\n\n" + block + "\n"


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------


def _load_videos_by_key(
    data_dir: Path,
) -> tuple[dict[str, list[dict[str, str]]], dict[str, str]]:
    """Return (StoryKey → video-list, StoryKey → StoryId)."""
    _, stories = read_pipe_csv(data_dir / "csv" / "stories.csv")
    id_to_key: dict[str, str] = {
        r["StoryId"]: Path(r["StoryKey"]).as_posix()
        for r in stories
        if r.get("StoryId") and r.get("StoryKey")
    }

    _, video_rows = read_pipe_csv(data_dir / "csv" / "story-narrated-videos.csv")
    by_key: dict[str, list[dict[str, str]]] = {}
    sid_by_key: dict[str, str] = {}

    for row in video_rows:
        sid = (row.get("StoryId") or "").strip()
        author = (row.get("Author") or "").strip()
        source = (row.get("SourceLink") or "").strip()
        if not sid or not author or not source:
            continue
        key = id_to_key.get(sid)
        if not key:
            continue
        by_key.setdefault(key, []).append(
            {
                "author": author,
                "source_link": source,
                "channel_link": (row.get("ChannelLink") or "").strip(),
            }
        )
        sid_by_key.setdefault(key, sid)

    return by_key, sid_by_key


# ---------------------------------------------------------------------------
# mdBook walk
# ---------------------------------------------------------------------------


def _walk_sections(
    sections: list,
    videos_by_key: dict[str, list[dict[str, str]]],
    sid_by_key: dict[str, str],
) -> None:
    for item in sections:
        if not isinstance(item, dict):
            continue
        if "Chapter" in item:
            ch = item["Chapter"]
            path = (ch.get("path") or "").strip()
            if path:
                key = Path(path).as_posix()
                videos = videos_by_key.get(key)
                if videos:
                    story_id = sid_by_key.get(key, key)
                    ch["content"] = _inject(ch.get("content") or "", story_id, videos)
            _walk_sections(ch.get("sub_items") or [], videos_by_key, sid_by_key)


def main() -> None:
    if len(sys.argv) >= 3 and sys.argv[1] == "supports":
        sys.exit(0)

    ctx, book = json.load(sys.stdin)
    root = Path(ctx["root"])
    book_cfg = (ctx.get("config") or {}).get("book") or {}
    src_rel = (book_cfg.get("src") or "src").strip() or "src"
    data_dir = (root / src_rel).resolve() / "data"

    videos_by_key, sid_by_key = _load_videos_by_key(data_dir)
    _walk_sections(book.get("items") or [], videos_by_key, sid_by_key)

    json.dump(book, sys.stdout, ensure_ascii=False)


if __name__ == "__main__":
    main()
