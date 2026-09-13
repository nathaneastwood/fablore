"""Runner for the story declarations in ``src/data/entries/``.

The declarations themselves used to live here. They now sit one module per
story type under ``entries/`` — this file only decides which of them to run and
prints the summary.

Each declaration registers a story and the entities it links to (heroes, npcs,
locations, regions, monsters, fauna, flora, food/drink, weapons, equipment).
They declare *relationships* only — they do not set lore text. Lore text
(location notes; monster/fauna/flora descriptions) belongs in
``descriptions.py``, not here. See ``descriptions.py`` for why.

Usage (any working directory; the paths below resolve from this file)::

    python3 src/data/data-entry.py                          # preview everything
    python3 src/data/data-entry.py --only src/flavour/monarch.md
    python3 src/data/data-entry.py --only src/flavour/monarch.md --verbose

A declaration carries its own ``dry_run=`` flag: leave it ``True`` to preview,
then set it to ``False`` and re-run to commit. ``--only`` narrows which
declarations run at all, which is what you want while adding one — a bare run
replays every page. Pages with nothing to change are silent by design, so the
one diff worth reading is the only thing on screen; ``--verbose`` prints the
unchanged ones too.
"""

from __future__ import annotations

import argparse
import importlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from entries import SECTIONS  # noqa: E402
from entries._runner import db  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="data-entry.py",
        description="Register stories and the entities they link to.",
    )
    parser.add_argument(
        "--only",
        action="append",
        metavar="PATH",
        help=(
            "Run only the declaration for this story path (repeatable). Takes "
            "src/flavour/monarch.md, flavour/monarch.md or an absolute path. "
            "Exits non-zero if nothing matches."
        ),
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print the preview for unchanged stories too.",
    )
    args = parser.parse_args(argv)

    # The filter has to be in place before the modules run, because importing
    # one is what executes its declarations.
    db.configure(only=args.only, verbose=args.verbose)
    for module in SECTIONS:
        importlib.import_module(f"entries.{module}")
    return db.report()


if __name__ == "__main__":
    raise SystemExit(main())
