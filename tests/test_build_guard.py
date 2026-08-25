"""Tests for ``build_guard``: the ``mdbook serve``-collision fast-fail check.

``mdbook serve`` (no ``-d``/``--dest-dir`` override) rebuilds the default
``book/`` directory on every source change. An automated build that also
targets ``book/`` — the ``link-checks`` hook, the ``build_result`` pytest
fixture — can therefore read a half-rewritten tree mid-rebuild and report
spurious errors that look like broken links or a bad build, but are really
just the race. ``build_guard`` detects the collision up front so the failure
names its real cause instead.

Detection is split into small pure functions over text (``ps`` / ``lsof``
output) and paths, each tested here without shelling out to a real process.
The thin orchestration wrapper that actually shells out
(``raise_if_mdbook_serve_running``) was exercised manually against the real
``mdbook serve`` process (PID 63526) instead of unit-tested: run with
``target_dir="book"`` it raised naming that PID; run with an unrelated temp
directory it returned silently. See the change's summary for the transcript.
"""

from __future__ import annotations

from build_guard import (
    find_conflicting_serve_pids,
    find_mdbook_serve_pids,
    parse_lsof_cwd,
    target_collides_with_default_book_dir,
)


class TestFindMdbookServePids:
    """Pure: parse ``ps -eo pid,command`` text for ``mdbook serve`` processes
    that write into the default ``book/`` directory (no ``-d``/``--dest-dir``)."""

    def test_matches_a_bare_mdbook_serve_process(self) -> None:
        ps_output = "  PID COMMAND\n63526 mdbook serve\n"
        assert find_mdbook_serve_pids(ps_output) == [("63526", "mdbook serve")]

    def test_ignores_serve_with_a_short_dest_dir_flag(self) -> None:
        """A serve pointed at its own --dest-dir doesn't collide with book/."""
        ps_output = "70001 mdbook serve -d /tmp/other-dir\n"
        assert find_mdbook_serve_pids(ps_output) == []

    def test_ignores_serve_with_a_long_dest_dir_flag(self) -> None:
        ps_output = "70002 mdbook serve --dest-dir /tmp/other-dir\n"
        assert find_mdbook_serve_pids(ps_output) == []

    def test_ignores_mdbook_build_and_unrelated_processes(self) -> None:
        ps_output = "70003 mdbook build\n70004 /bin/zsh -c mdbook-servesomething\n70005 grep mdbook\n"
        assert find_mdbook_serve_pids(ps_output) == []

    def test_ignores_a_header_line(self) -> None:
        ps_output = "  PID COMMAND\n63526 mdbook serve\n"
        # Header line ("PID COMMAND") must not itself be mistaken for a hit —
        # covered implicitly above since its leading token isn't a digit, but
        # made explicit here so a future refactor can't lose the guard.
        assert ("PID", "COMMAND") not in find_mdbook_serve_pids(ps_output)

    def test_matches_multiple_colliding_processes(self) -> None:
        ps_output = "63526 mdbook serve\n70006 mdbook serve\n"
        assert find_mdbook_serve_pids(ps_output) == [
            ("63526", "mdbook serve"),
            ("70006", "mdbook serve"),
        ]


class TestParseLsofCwd:
    """Pure: parse ``lsof -p PID -a -d cwd -Fn`` output for the process's
    working directory (the fields-mode line prefixed ``n``)."""

    def test_extracts_the_cwd_path(self) -> None:
        lsof_output = "p63526\nfcwd\nn/Users/nathan/Documents/work/NEDataLtd/projects/fablore\n"
        assert parse_lsof_cwd(lsof_output) == "/Users/nathan/Documents/work/NEDataLtd/projects/fablore"

    def test_returns_none_when_no_cwd_line_present(self) -> None:
        assert parse_lsof_cwd("p63526\nfcwd\n") is None

    def test_returns_none_for_empty_output(self) -> None:
        assert parse_lsof_cwd("") is None


class TestFindConflictingServePids:
    """Pure: combine the ``ps`` hits with a pid->cwd mapping (as produced by
    ``parse_lsof_cwd`` per pid) and keep only the ones rooted at this repo —
    an unrelated ``mdbook serve`` for a different book must not fail this
    repo's build."""

    def test_keeps_a_serve_process_rooted_at_this_repo(self) -> None:
        ps_output = "63526 mdbook serve\n"
        pid_cwds = {"63526": "/Users/nathan/Documents/work/NEDataLtd/projects/fablore"}
        result = find_conflicting_serve_pids(
            ps_output, pid_cwds, repo_root="/Users/nathan/Documents/work/NEDataLtd/projects/fablore"
        )
        assert result == [("63526", "mdbook serve")]

    def test_drops_a_serve_process_rooted_elsewhere(self) -> None:
        ps_output = "70007 mdbook serve\n"
        pid_cwds = {"70007": "/Users/nathan/other-book"}
        result = find_conflicting_serve_pids(
            ps_output, pid_cwds, repo_root="/Users/nathan/Documents/work/NEDataLtd/projects/fablore"
        )
        assert result == []

    def test_drops_a_serve_process_with_unknown_cwd(self) -> None:
        """A pid missing from pid_cwds (e.g. lsof lookup failed) is treated
        as not-this-repo rather than raising a KeyError."""
        ps_output = "70008 mdbook serve\n"
        result = find_conflicting_serve_pids(
            ps_output, pid_cwds={}, repo_root="/Users/nathan/Documents/work/NEDataLtd/projects/fablore"
        )
        assert result == []


class TestTargetCollidesWithDefaultBookDir:
    """Pure: a build only collides with a bare ``mdbook serve`` if the build's
    own ``--dest-dir`` resolves to the repo's default ``book/`` output — the
    only directory an override-less ``mdbook serve`` ever writes to (confirmed
    against ``book.toml``, which declares no ``build.build-dir`` override).

    Once a build points ``--dest-dir`` at its own temp directory, this is
    ``False`` and ``raise_if_mdbook_serve_running`` can skip shelling out to
    ``ps``/``lsof`` entirely — a live serve process no longer matters to it.
    """

    def test_true_when_target_is_the_default_book_dir(self) -> None:
        repo_root = "/Users/nathan/Documents/work/NEDataLtd/projects/fablore"
        assert target_collides_with_default_book_dir(repo_root + "/book", repo_root) is True

    def test_false_when_target_is_a_different_directory(self) -> None:
        repo_root = "/Users/nathan/Documents/work/NEDataLtd/projects/fablore"
        assert target_collides_with_default_book_dir("/tmp/fablore-build-xyz", repo_root) is False

    def test_true_for_an_equivalent_but_unnormalized_path(self) -> None:
        repo_root = "/Users/nathan/Documents/work/NEDataLtd/projects/fablore"
        assert target_collides_with_default_book_dir(repo_root + "/./book/../book", repo_root) is True
