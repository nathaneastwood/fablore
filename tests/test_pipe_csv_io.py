"""Tests for :mod:`pipe_csv_io`."""

from __future__ import annotations

from pathlib import Path

from pipe_csv_io import (
    read_pipe_csv,
    strip_leading_hash_comments,
    write_pipe_csv_autogen,
)


def test_strip_leading_hash_comments() -> None:
    """Comment banner lines are removed from file bodies."""
    raw = "# hi\n# there\nA|B\n"
    assert strip_leading_hash_comments(raw) == "A|B\n"


def test_read_pipe_csv_missing_file(tmp_path: Path) -> None:
    """Missing paths yield empty structures."""
    missing = tmp_path / "nope.csv"
    fieldnames, rows = read_pipe_csv(missing)
    assert fieldnames == []
    assert rows == []


def test_write_and_read_pipe_roundtrip(tmp_path: Path) -> None:
    """Written autogen files skip the banner on read."""
    path = tmp_path / "sample.csv"
    write_pipe_csv_autogen(
        path,
        ["K", "V"],
        [{"K": "a", "V": "1"}],
        regenerate_command="python3 noop.py",
    )
    fieldnames, rows = read_pipe_csv(path)
    assert fieldnames == ["K", "V"]
    assert rows == [{"K": "a", "V": "1"}]
