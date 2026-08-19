"""The ``db`` object the section modules declare against.

It is not a :class:`~db.Database`. It is a proxy with the same ``upsert_story``
signature that adds the two things a bare ``Database`` cannot, both of which
matter because every module in this package executes in full on import:

- **Filtering.** ``--only`` is answered here, before the database is touched,
  so previewing one page does not replay every other page.
- **Quiet no-ops.** A dry run of an already-registered page prints six lines to
  say nothing changed. At one declaration per page that buries the single diff
  worth reading, so previews are buffered and printed only when the database
  reports a real change.

The connection is opened lazily on the first call that survives the filter: a
``--only`` run costs one open, and a run matching nothing costs none.
"""

from __future__ import annotations

import contextlib
import io
from pathlib import Path
from typing import Any

from db import Database, StoryRecord

ROOT = Path(__file__).resolve().parents[3]
DB_PATH = Path(__file__).resolve().parents[1] / "fablore.db"


def story_key(path: str | Path) -> str:
    """Normalise a path to its ``stories.csv`` ``StoryKey`` form.

    Accepts what a declaration carries (``src/flavour/monarch.md``), what a
    shell completes (an absolute path, ``./src/...``), and the key itself, so
    ``--only`` takes whatever the caller has to hand.
    """
    text = str(path).strip()
    candidate = Path(text)
    if candidate.is_absolute():
        with contextlib.suppress(ValueError):
            text = str(candidate.resolve().relative_to(ROOT))
    if text.startswith("./"):
        text = text[2:]
    if text.startswith("src/"):
        text = text[len("src/") :]
    return text


class Runner:
    """Filters, executes and summarises the declarations in this package."""

    def __init__(self) -> None:
        self.only: set[str] = set()
        self.verbose = False
        self.declared: list[str] = []
        self.matched: set[str] = set()
        self.changed: list[str] = []
        self.written: list[str] = []
        self._db: Database | None = None

    def configure(self, *, only: list[str] | None = None, verbose: bool = False) -> None:
        """Set the filter. Must be called before any section module is imported."""
        self.only = {story_key(p) for p in (only or [])}
        self.verbose = verbose

    @property
    def database(self) -> Database:
        """Open the database on first use, not at import."""
        if self._db is None:
            self._db = Database(DB_PATH)
        return self._db

    def upsert_story(self, *, path: str, **kwargs: Any) -> StoryRecord | None:
        """Proxy for :meth:`db.Database.upsert_story`; identical signature.

        Returns ``None`` for a declaration the filter skipped — no declaration
        uses the return value, and skipping must not open the database.
        """
        key = story_key(path)
        self.declared.append(key)
        if self.only and key not in self.only:
            return None
        self.matched.add(key)

        if not kwargs.get("dry_run", False):
            record = self.database.upsert_story(path=path, **kwargs)
            self.written.append(key)
            print(f"WROTE {key}")
            return record

        # _dry_run_upsert resolves sys.stdout at call time, so redirecting is
        # enough to buffer it — no signature change to the public API that five
        # skills document.
        buffer = io.StringIO()
        try:
            with contextlib.redirect_stdout(buffer):
                record = self.database.upsert_story(path=path, **kwargs)
        except Exception:
            # A failed declaration is exactly when the partial preview is worth
            # seeing: it shows how far the diff got before the raise.
            print(buffer.getvalue(), end="")
            raise
        if self.database.last_dry_run_changed:
            self.changed.append(key)
        if self.database.last_dry_run_changed or self.verbose:
            print(buffer.getvalue(), end="")
        return record

    def report(self) -> int:
        """Print the run summary. Returns the process exit code."""
        unmatched = sorted(self.only - self.matched)
        if unmatched:
            print("\nNo declaration matches:")
            for key in unmatched:
                print(f"  {key}")
                near = [d for d in self.declared if Path(d).name == Path(key).name]
                for suggestion in near:
                    print(f"    did you mean: src/{suggestion}")
            print("\nA story with no declaration here is not an error — it just")
            print("has no entity links recorded yet. Add one to the matching")
            print("module under src/data/entries/.")
            return 1

        total = len(self.declared)
        scope = f"{len(self.matched)} of {total}" if self.only else str(total)
        parts = [f"{scope} declarations checked"]
        if self.written:
            parts.append(f"{len(self.written)} written")
        if self.changed:
            parts.append(f"{len(self.changed)} with pending changes")
        unchanged = len(self.matched) - len(self.changed) - len(self.written)
        if unchanged:
            parts.append(f"{unchanged} unchanged")
        print("\n" + " · ".join(parts))
        if self.changed and not self.written:
            print("Set dry_run=False on a declaration to apply it.")
        return 0


db = Runner()
