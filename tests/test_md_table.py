"""Tests for :func:`generator_utils.md_table`."""

from __future__ import annotations

import re
import sys
from pathlib import Path

_DATA_DIR = Path(__file__).resolve().parent.parent / "src" / "data"
if str(_DATA_DIR) not in sys.path:
    sys.path.insert(0, str(_DATA_DIR))

from generator_utils import md_table  # noqa: E402


def _cells(line: str) -> list[str]:
    """Split a GFM table row the way a renderer does: on pipes not preceded by ``\\``."""
    inner = line.strip()[1:-1]
    return [c.strip() for c in re.split(r"(?<!\\)\|", inner)]


def test_renders_header_separator_and_rows() -> None:
    assert md_table(["Name", "Notes"], [["Amy", "Elf"]]) == ("| Name | Notes |\n" "| --- | --- |\n" "| Amy | Elf |")


def test_a_cell_containing_a_pipe_stays_one_cell() -> None:
    table = md_table(["Name", "Notes"], [["Amy", "either | or"]])
    row = table.splitlines()[2]
    assert row == r"| Amy | either \| or |"
    assert _cells(row) == ["Amy", r"either \| or"]


def test_a_header_containing_a_pipe_stays_one_cell() -> None:
    header = md_table(["A|B"], []).splitlines()[0]
    assert _cells(header) == [r"A\|B"]
