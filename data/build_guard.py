#!/usr/bin/env python3
"""Fast-fail guard against a colliding ``mdbook serve``.

``mdbook serve`` (started with no ``-d``/``--dest-dir`` override) rebuilds
the default ``book/`` directory on every source-file change. An automated
build that also targets ``book/`` directly — the ``link-checks`` pre-commit
hook, the ``build_result`` pytest fixture — can then read a half-rewritten
tree mid-rebuild: files missing, files truncated. That looked, nine times on
this branch, like thousands of broken links or a failed regression test; it
was really this race, not a content or link problem.

Both automated builders now write to their own ``--dest-dir`` instead of
``book/``, so in steady state there is nothing left to collide: a bare
``mdbook serve`` only ever writes into the repo's default ``book/`` (there is
no ``build.build-dir`` override in ``book.toml``), and an isolated
``--dest-dir`` is never that path. ``raise_if_mdbook_serve_running`` exists as
the safety net for when that stops being true — a build accidentally passed
``book/`` as its own target, a future change drops the override — so the
failure names its real cause instead of the caller working through a wall of
spurious link/content errors caused by reading a half-rewritten tree.

Detection is deliberately split into small, pure, text-in/text-out functions
so the logic is unit-testable without a real process tree:

  ``target_collides_with_default_book_dir`` -- does this build's own target
                                                even reach serve's output dir?
  ``find_mdbook_serve_pids``                 -- parse ``ps -eo pid,command``
  ``parse_lsof_cwd``                         -- parse ``lsof -p PID -a -d cwd -Fn``
  ``find_conflicting_serve_pids``            -- combine the two against a repo root

``raise_if_mdbook_serve_running`` is the only impure piece: it shells out to
``ps`` and ``lsof`` only when ``target_collides_with_default_book_dir`` says
there's something worth checking, and calls the pure functions above.
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

_SERVE_RE = re.compile(r"\bmdbook\s+serve\b")
_DEST_DIR_RE = re.compile(r"(^|\s)(-d\b|--dest-dir\b)")


class MdbookServeRunningError(RuntimeError):
    """Raised when a live ``mdbook serve`` targeting the default ``book/``
    output directory is detected while an automated build is starting."""


def target_collides_with_default_book_dir(target_dir: str, repo_root: str) -> bool:
    """Is ``target_dir`` the same directory a bare ``mdbook serve`` (no
    ``-d``/``--dest-dir``) writes to for this repo?

    ``book.toml`` declares no ``build.build-dir`` override, so that
    directory is always ``{repo_root}/book``. Paths are resolved (``..``,
    ``.`` and symlinks included) before comparing, so an equivalent but
    differently-spelled path still counts as a collision.
    """
    return Path(target_dir).resolve() == (Path(repo_root) / "book").resolve()


def find_mdbook_serve_pids(ps_output: str) -> list[tuple[str, str]]:
    """Return ``(pid, command)`` for every ``mdbook serve`` process in
    ``ps_output`` that has no ``-d``/``--dest-dir`` override — the ones that
    write into the default ``book/`` directory and can race an automated
    build targeting the same directory.

    ``ps_output`` is text in ``ps -eo pid,command`` format: PID first,
    whitespace, then the full command line. Lines that don't mention
    ``mdbook serve`` (e.g. ``mdbook build``, unrelated processes) are
    ignored, as are header lines and anything where the leading token isn't
    a PID.
    """
    hits: list[tuple[str, str]] = []
    for line in ps_output.splitlines():
        stripped = line.strip()
        if not stripped or not _SERVE_RE.search(stripped):
            continue
        if _DEST_DIR_RE.search(stripped):
            continue
        pid, _, command = stripped.partition(" ")
        if not pid.isdigit():
            continue
        hits.append((pid, command.strip()))
    return hits


def parse_lsof_cwd(lsof_output: str) -> str | None:
    """Return the working-directory path from ``lsof -p PID -a -d cwd -Fn``
    output, or ``None`` if the process (or its cwd) can't be found — e.g. it
    exited between ``ps`` and this call.

    ``lsof -F n`` field-mode prefixes the value line with the field letter
    (here ``n`` for name/path); the path itself is everything after it.
    """
    for line in lsof_output.splitlines():
        if line.startswith("n"):
            return line[1:]
    return None


def find_conflicting_serve_pids(
    ps_output: str, pid_cwds: dict[str, str | None], repo_root: str
) -> list[tuple[str, str]]:
    """Return ``(pid, command)`` for ``mdbook serve`` processes (per
    ``find_mdbook_serve_pids``) whose working directory — looked up in
    ``pid_cwds``, keyed by the same pid strings — is exactly ``repo_root``.

    A serve process for a different repo, or one whose cwd couldn't be
    determined (missing from ``pid_cwds``), does not conflict with this
    repo's build and is dropped rather than raising.
    """
    return [(pid, command) for pid, command in find_mdbook_serve_pids(ps_output) if pid_cwds.get(pid) == repo_root]


def raise_if_mdbook_serve_running(target_dir: str, repo_root: str | None = None) -> None:
    """Shell out to ``ps`` and ``lsof`` and raise ``MdbookServeRunningError``
    if a live, override-less ``mdbook serve`` for ``repo_root`` (default:
    this repo) would collide with a build writing to ``target_dir``.

    ``target_dir`` is required on purpose: a build isolated to its own
    directory can't collide regardless of what's running, so callers must
    say where they're building before this does anything. When
    ``target_collides_with_default_book_dir`` says no collision is possible,
    this returns immediately without shelling out to ``ps``/``lsof`` at all.

    This is the only impure function in the module — everything it decides
    is delegated to ``target_collides_with_default_book_dir``,
    ``find_conflicting_serve_pids``, ``find_mdbook_serve_pids`` and
    ``parse_lsof_cwd`` above, which are what's unit-tested. ``ps``/``lsof``
    failures (neither installed, permission denied) are treated as "can't
    tell" and swallowed rather than raised — a missing tool must not block
    every build.
    """
    root = repo_root if repo_root is not None else str(ROOT)
    if not target_collides_with_default_book_dir(target_dir, root):
        return

    try:
        ps_result = subprocess.run(["ps", "-eo", "pid,command"], capture_output=True, text=True, check=True)
    except (OSError, subprocess.CalledProcessError):
        return

    candidates = find_mdbook_serve_pids(ps_result.stdout)
    pid_cwds: dict[str, str | None] = {}
    for pid, _command in candidates:
        try:
            lsof_result = subprocess.run(
                ["lsof", "-p", pid, "-a", "-d", "cwd", "-Fn"], capture_output=True, text=True, check=True
            )
        except (OSError, subprocess.CalledProcessError):
            pid_cwds[pid] = None
            continue
        pid_cwds[pid] = parse_lsof_cwd(lsof_result.stdout)

    conflicts = find_conflicting_serve_pids(ps_result.stdout, pid_cwds, root)
    if conflicts:
        named = "\n".join(f"  PID {pid}: {command}" for pid, command in conflicts)
        raise MdbookServeRunningError(
            "A live `mdbook serve` is running against this repo and rebuilds "
            f"book/ on every source change:\n{named}\n\n"
            "This collides with an automated build reading or writing the "
            "same directory — that reader can see a half-rewritten tree "
            "mid-rebuild, which looks like broken links or a failed build "
            "but isn't. Stop `mdbook serve` before running this, or point "
            "it at a review copy elsewhere and leave serve alone."
        )


if __name__ == "__main__":
    import sys

    # Usage: build_guard.py [target-dir]  (default: book/, i.e. "am I about
    # to build into the directory mdbook serve owns by default?")
    cli_target_dir = sys.argv[1] if len(sys.argv) > 1 else str(ROOT / "book")
    try:
        raise_if_mdbook_serve_running(cli_target_dir)
    except MdbookServeRunningError as exc:
        print(f"build_guard: {exc}", file=sys.stderr)
        sys.exit(1)
