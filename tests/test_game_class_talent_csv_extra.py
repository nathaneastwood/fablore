"""Extra tests for :mod:`game_class_talent_csv` — targeting uncovered branches."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src/data"))

import game_class_talent_csv as gct
import pytest
from pipe_csv_io import write_pipe_csv_autogen
from registry_ids import make_hash_id
from text_utils import normalize_name


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _write_classes_csv(path: Path, rows: list[dict[str, str]]) -> None:
    write_pipe_csv_autogen(path, ["ClassId", "ClassName"], rows, regenerate_command="test")


def _write_talents_csv(path: Path, rows: list[dict[str, str]]) -> None:
    write_pipe_csv_autogen(path, ["TalentId", "TalentName"], rows, regenerate_command="test")


# ---------------------------------------------------------------------------
# merge_classes_and_talents_from_card_rows — weapon branch (lines 72-74)
# ---------------------------------------------------------------------------


def test_merge_weapon_types_branch(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Weapon card rows contribute classes/talents via the weapon branch (lines 72-74)."""
    classes_path = tmp_path / "classes.csv"
    talents_path = tmp_path / "talents.csv"
    monkeypatch.setattr(gct, "CLASSES_CSV_PATH", classes_path)
    monkeypatch.setattr(gct, "TALENTS_CSV_PATH", talents_path)

    # A Warrior Weapon card — should hit the types_include_weapon branch
    card_rows = [{"Types": "Warrior, Weapon"}]
    class_map, talent_map = gct.merge_classes_and_talents_from_card_rows(
        card_rows,
        make_hash_id=make_hash_id,
        normalize_name=normalize_name,
    )

    assert "Warrior" in class_map
    classes_text = classes_path.read_text(encoding="utf-8")
    assert "Warrior" in classes_text


# ---------------------------------------------------------------------------
# merge_classes_and_talents_from_card_rows — equipment (not weapon) branch (lines 76-78)
# ---------------------------------------------------------------------------


def test_merge_equipment_not_weapon_branch(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Equipment (non-weapon) rows contribute via the equipment branch (lines 76-78)."""
    classes_path = tmp_path / "classes.csv"
    talents_path = tmp_path / "talents.csv"
    monkeypatch.setattr(gct, "CLASSES_CSV_PATH", classes_path)
    monkeypatch.setattr(gct, "TALENTS_CSV_PATH", talents_path)

    # A Ninja Equipment card (no Weapon token) — hits the equipment-not-weapon branch
    card_rows = [{"Types": "Ninja, Equipment"}]
    class_map, talent_map = gct.merge_classes_and_talents_from_card_rows(
        card_rows,
        make_hash_id=make_hash_id,
        normalize_name=normalize_name,
    )

    assert "Ninja" in class_map
    classes_text = classes_path.read_text(encoding="utf-8")
    assert "Ninja" in classes_text


def test_weapon_equipment_hybrid_only_uses_weapon_branch(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """A card with both Weapon and Equipment uses only the weapon branch, not equipment."""
    classes_path = tmp_path / "classes.csv"
    talents_path = tmp_path / "talents.csv"
    monkeypatch.setattr(gct, "CLASSES_CSV_PATH", classes_path)
    monkeypatch.setattr(gct, "TALENTS_CSV_PATH", talents_path)

    # Both Weapon and Equipment — equipment branch is skipped (lines 75-78 condition)
    card_rows = [{"Types": "Warrior, Weapon, Equipment"}]
    class_map, _ = gct.merge_classes_and_talents_from_card_rows(
        card_rows,
        make_hash_id=make_hash_id,
        normalize_name=normalize_name,
    )
    assert "Warrior" in class_map


# ---------------------------------------------------------------------------
# _load_name_id_map — filters out blank names/ids (lines 99-102)
# ---------------------------------------------------------------------------


def test_load_name_id_map_filters_blanks(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """_load_name_id_map skips rows with blank name or blank id (lines 99-102)."""
    classes_path = tmp_path / "classes.csv"
    # Write a CSV with a mix of valid, blank-name, and blank-id rows
    _write_classes_csv(
        classes_path,
        [
            {"ClassId": "CLabcdef1234", "ClassName": "Warrior"},
            {"ClassId": "", "ClassName": "Orphan"},  # blank id — should be skipped
            {"ClassId": "CLdeadbeef12", "ClassName": ""},  # blank name — should be skipped
        ],
    )
    monkeypatch.setattr(gct, "CLASSES_CSV_PATH", classes_path)

    result = gct._load_name_id_map(classes_path, "ClassId", "ClassName")

    assert result == {"Warrior": "CLabcdef1234"}
    assert "Orphan" not in result
    assert "" not in result


# ---------------------------------------------------------------------------
# merge_classes — reuses existing id from disk (line 136)
# ---------------------------------------------------------------------------


def test_merge_classes_reuses_existing_id(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """merge_classes preserves known ClassId from disk rather than re-hashing (line 136)."""
    classes_path = tmp_path / "classes.csv"
    existing_id = "CL1234567890"
    _write_classes_csv(
        classes_path,
        [{"ClassId": existing_id, "ClassName": "Warrior"}],
    )
    monkeypatch.setattr(gct, "CLASSES_CSV_PATH", classes_path)

    result = gct.merge_classes(
        ["Warrior"],
        make_hash_id=make_hash_id,
        normalize_name=normalize_name,
    )

    assert result["Warrior"] == existing_id
    written = classes_path.read_text(encoding="utf-8")
    assert existing_id in written


def test_merge_classes_generates_new_id_for_unknown(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """merge_classes generates a new deterministic id for a name not on disk."""
    classes_path = tmp_path / "classes.csv"
    # CSV exists but does not contain "Ninja"
    _write_classes_csv(classes_path, [{"ClassId": "CL0000000001", "ClassName": "Warrior"}])
    monkeypatch.setattr(gct, "CLASSES_CSV_PATH", classes_path)

    result = gct.merge_classes(
        ["Ninja"],
        make_hash_id=make_hash_id,
        normalize_name=normalize_name,
    )

    assert "Ninja" in result
    assert result["Ninja"].startswith("CL")
    assert "Warrior" not in result  # only names in the supplied list are kept


# ---------------------------------------------------------------------------
# merge_talents — new names generate TL ids (lines 169-172)
# ---------------------------------------------------------------------------


def test_merge_talents_generates_new_id(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """merge_talents generates a TL-prefixed id for a talent not yet on disk (lines 169-172)."""
    talents_path = tmp_path / "talents.csv"
    # Start with an empty (missing) talents file so nothing is on disk
    monkeypatch.setattr(gct, "TALENTS_CSV_PATH", talents_path)

    result = gct.merge_talents(
        ["Shadow"],
        make_hash_id=make_hash_id,
        normalize_name=normalize_name,
    )

    assert "Shadow" in result
    assert result["Shadow"].startswith("TL")
    written = talents_path.read_text(encoding="utf-8")
    assert "Shadow" in written


def test_merge_talents_reuses_existing_id(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """merge_talents preserves a known TalentId from disk."""
    talents_path = tmp_path / "talents.csv"
    existing_id = "TL9999999999"
    _write_talents_csv(talents_path, [{"TalentId": existing_id, "TalentName": "Shadow"}])
    monkeypatch.setattr(gct, "TALENTS_CSV_PATH", talents_path)

    result = gct.merge_talents(
        ["Shadow"],
        make_hash_id=make_hash_id,
        normalize_name=normalize_name,
    )

    assert result["Shadow"] == existing_id
    written = talents_path.read_text(encoding="utf-8")
    assert existing_id in written
