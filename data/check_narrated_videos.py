#!/usr/bin/env python3
"""Check that every narrated-video URL in the database is still publicly available.

Uses the YouTube oEmbed endpoint (no API key required).  A non-200 response
indicates the video has been deleted, set to private, or is otherwise
unavailable.

Usage::

    python3 src/data/check_narrated_videos.py

Exit code is 0 when all videos are reachable, 1 when any are unavailable or
when network errors occur.
"""

from __future__ import annotations

import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from pipe_csv_io import read_pipe_csv  # noqa: E402

_OEMBED = "https://www.youtube.com/oembed?format=json&url={}"
_DELAY_S = 0.3  # be polite to YouTube


def _check_url(url: str) -> tuple[bool, str]:
    """Return (ok, message) for a single video URL."""
    oembed_url = _OEMBED.format(urllib.parse.quote(url, safe=""))
    req = urllib.request.Request(oembed_url, headers={"User-Agent": "fablore-checker/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            if resp.status == 200:
                return True, "OK"
            return False, f"HTTP {resp.status}"
    except urllib.error.HTTPError as exc:
        if exc.code == 401:
            return False, "private or age-restricted (401)"
        if exc.code == 404:
            return False, "not found / deleted (404)"
        return False, f"HTTP error {exc.code}"
    except urllib.error.URLError as exc:
        return False, f"network error: {exc.reason}"


def main() -> int:
    csv_path = _SCRIPT_DIR / "csv" / "story-narrated-videos.csv"
    _, rows = read_pipe_csv(csv_path)

    if not rows:
        print("No narrated videos found in CSV.")
        return 0

    failures: list[str] = []
    print(f"Checking {len(rows)} video(s)…\n")

    for row in rows:
        story_id = (row.get("StoryId") or "").strip()
        author = (row.get("Author") or "").strip()
        url = (row.get("SourceLink") or "").strip()
        if not url:
            continue

        ok, msg = _check_url(url)
        status = "✓" if ok else "✗"
        print(f"  {status}  [{story_id}] {author} — {url}")
        if not ok:
            print(f"       ↳ {msg}")
            failures.append(f"[{story_id}] {author}: {url} ({msg})")
        time.sleep(_DELAY_S)

    print()
    if failures:
        print(f"UNAVAILABLE ({len(failures)}):")
        for f in failures:
            print(f"  • {f}")
        return 1

    print(f"All {len(rows)} video(s) are available.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
