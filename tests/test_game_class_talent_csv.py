"""Tests for :mod:`game_class_talent_csv`."""

from __future__ import annotations

from pathlib import Path

import pytest

import game_class_talent_csv as gct
from registry_ids import make_hash_id
from text_utils import normalize_name


def test_merge_classes_and_talents_writes_pipe_csvs(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Merged classes/talents are written to the patched paths."""
    classes_path = tmp_path / "classes.csv"
    talents_path = tmp_path / "talents.csv"
    monkeypatch.setattr(gct, "CLASSES_CSV_PATH", classes_path)
    monkeypatch.setattr(gct, "TALENTS_CSV_PATH", talents_path)

    card_rows = [{"Types": "Warrior, Hero, Young"}]
    gct.merge_classes_and_talents_from_card_rows(
        card_rows,
        make_hash_id=make_hash_id,
        normalize_name=normalize_name,
    )

    classes_text = classes_path.read_text(encoding="utf-8")
    talents_text = talents_path.read_text(encoding="utf-8")
    assert "Warrior" in classes_text
    assert classes_text.startswith("# AUTO-GENERATED")
    assert talents_text.startswith("# AUTO-GENERATED")
