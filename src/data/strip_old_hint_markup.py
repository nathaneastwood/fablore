#!/usr/bin/env python3
"""One-time cleanup: strip all [Text](~Key) old hint markup from source .md files.

Replaces each occurrence with just the display text, e.g.:
  [Hand of Sol](~HandOfSol)  →  Hand of Sol

Run from the repository root ONLY after the preview pass (Phase 3 step 10)
confirms the auto-detection results are satisfactory.

    python src/data/strip_old_hint_markup.py
"""

import re
from pathlib import Path

_OLD_HINT = re.compile(r'\[([^\]]+)\]\(~[^)]+\)')

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"


def strip_file(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    new_text = _OLD_HINT.sub(r"\1", text)
    if new_text == text:
        return False
    path.write_text(new_text, encoding="utf-8")
    return True


def main() -> None:
    changed = []
    for path in sorted(SRC.rglob("*.md")):
        if strip_file(path):
            changed.append(path.relative_to(ROOT))

    if changed:
        print(f"Updated {len(changed)} file(s):")
        for p in changed:
            print(f"  {p}")
    else:
        print("No files contained old hint markup.")


if __name__ == "__main__":
    main()
