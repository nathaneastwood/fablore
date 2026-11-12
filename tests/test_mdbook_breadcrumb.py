"""Tests for :mod:`mdbook_breadcrumb` — the Section › Page trail above each chapter."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SCRIPT = REPO / "src" / "data" / "mdbook_breadcrumb.py"


def _render(path: str, name: str) -> str:
    """Run the preprocessor over a one-chapter book and return that chapter's content."""
    ctx = {"root": str(REPO), "config": {"book": {"src": "src"}}}
    book = {"items": [{"Chapter": {"name": name, "path": path, "content": f"# {name}\n", "sub_items": []}}]}
    out = subprocess.run(
        [sys.executable, str(SCRIPT)],
        input=json.dumps([ctx, book]),
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(out.stdout)["items"][0]["Chapter"]["content"]


def test_a_hero_page_has_no_breadcrumb() -> None:
    """The banner opens a hero page; a trail above it only crowds it."""
    assert _render("heroes-of-rathe/bravo-about.md", "Bravo") == "# Bravo\n"
