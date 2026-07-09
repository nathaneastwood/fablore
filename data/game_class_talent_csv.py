"""Shared game class and talent reference tables (``classes.csv``, ``talents.csv``).

Hero, weapon, and equipment card generators merge their ``Types`` tokens into the
same two files so **ClassId** / **TalentId** stay consistent (``CL`` / ``TL`` +
SHA-1 hash of :func:`text_utils.normalize_name` of the display name).

Use :func:`merge_classes_and_talents_from_card_rows` from generators or run
``python3 src/data/create_classes_talents_csv.py`` to refresh both tables from the
upstream ``card.csv`` in one pass.
"""

from __future__ import annotations

from pathlib import Path
from typing import Callable

from card_types_extract import (
    extract_card_classes_and_talents,
    extract_equipment_classes_and_talents,
    extract_weapon_classes_and_talents,
    parse_tokens,
    types_include_equipment,
    types_include_weapon,
)
from pipe_csv_io import (
    REGENERATE_CLASSES_TALENTS,
    read_pipe_csv,
    write_pipe_csv_autogen,
)
from registry_ids import assert_unique_ids

ROOT = Path(__file__).resolve().parents[2]
CLASSES_CSV_PATH = ROOT / "src/data/csv/classes.csv"
TALENTS_CSV_PATH = ROOT / "src/data/csv/talents.csv"
UPSTREAM_CARD_CSV_PATH = ROOT.parent / "flesh-and-blood-cards/csvs/english/card.csv"


def merge_classes_and_talents_from_card_rows(
    card_rows: list[dict[str, str]],
    *,
    make_hash_id: Callable[[str, str], str],
    normalize_name: Callable[[str], str],
    regenerate_command: str = REGENERATE_CLASSES_TALENTS,
) -> tuple[dict[str, str], dict[str, str]]:
    """Merge the union of class/talent names from hero, weapon, and equipment rows.

    Scans ``Types`` on every row: rows with a ``Hero`` token contribute via
    :func:`card_types_extract.extract_card_classes_and_talents`; rows whose types
    include a *weapon* token contribute via
    :func:`card_types_extract.extract_weapon_classes_and_talents`; rows with
    *equipment* but not *weapon* contribute via
    :func:`card_types_extract.extract_equipment_classes_and_talents`.

    Args:
        card_rows: Tab-separated ``card.csv`` rows (same shape as :func:`tab_csv_io.read_tab_csv`).
        make_hash_id: ``registry_ids.make_hash_id``.
        normalize_name: ``text_utils.normalize_name``.
        regenerate_command: Banner hint for :func:`pipe_csv_io.write_pipe_csv_autogen`.

    Returns:
        ``(ClassName -> ClassId, TalentName -> TalentId)`` after writing both files.

    Raises:
        ValueError: If merged ids are not unique.
    """
    class_names: set[str] = set()
    talent_names: set[str] = set()
    for card in card_rows:
        types_raw = card.get("Types", "")
        tokens = parse_tokens(types_raw)
        if "Hero" in tokens:
            c_names, t_names = extract_card_classes_and_talents(types_raw)
            class_names.update(c_names)
            talent_names.update(t_names)
        if types_include_weapon(types_raw):
            c_names, t_names = extract_weapon_classes_and_talents(types_raw)
            class_names.update(c_names)
            talent_names.update(t_names)
        if types_include_equipment(types_raw) and not types_include_weapon(types_raw):
            c_names, t_names = extract_equipment_classes_and_talents(types_raw)
            class_names.update(c_names)
            talent_names.update(t_names)
    class_id_by_name = merge_classes(
        sorted(class_names),
        make_hash_id=make_hash_id,
        normalize_name=normalize_name,
        regenerate_command=regenerate_command,
    )
    talent_id_by_name = merge_talents(
        sorted(talent_names),
        make_hash_id=make_hash_id,
        normalize_name=normalize_name,
        regenerate_command=regenerate_command,
    )
    return class_id_by_name, talent_id_by_name


def _load_name_id_map(path: Path, id_col: str, name_col: str) -> dict[str, str]:
    """Load ``name -> id`` from a pipe CSV (skipping ``#`` banners)."""
    _, rows = read_pipe_csv(path)
    out: dict[str, str] = {}
    for row in rows:
        name = (row.get(name_col) or "").strip()
        rid = (row.get(id_col) or "").strip()
        if name and rid:
            out[name] = rid
    return out


def merge_classes(
    names: list[str],
    *,
    make_hash_id: Callable[[str, str], str],
    normalize_name: Callable[[str], str],
    regenerate_command: str = REGENERATE_CLASSES_TALENTS,
) -> dict[str, str]:
    """Write ``classes.csv`` with exactly ``names`` and return ``ClassName`` -> ``ClassId``.

    Rows not present in ``names`` are dropped. Known names reuse ids from disk;
    new names get deterministic ``CL`` ids.

    Args:
        names: Class display names from the current upstream scan (typically union
            across hero, weapon, and equipment rows).
        make_hash_id: ``registry_ids.make_hash_id``.
        normalize_name: ``text_utils.normalize_name``.
        regenerate_command: Banner hint for :func:`pipe_csv_io.write_pipe_csv_autogen`.

    Returns:
        Map of every class name written.

    Raises:
        ValueError: If merged ``ClassId`` values are not unique.
    """
    required = set(names)
    disk = _load_name_id_map(CLASSES_CSV_PATH, "ClassId", "ClassName")
    by_name: dict[str, str] = {}
    for name in required:
        if name in disk:
            by_name[name] = disk[name]
        else:
            by_name[name] = make_hash_id("CL", normalize_name(name))
    assert_unique_ids([(cid, name) for name, cid in by_name.items()], "Class")
    rows = [
        {"ClassId": by_name[n], "ClassName": n} for n in sorted(by_name, key=str.lower)
    ]
    write_pipe_csv_autogen(
        CLASSES_CSV_PATH,
        ["ClassId", "ClassName"],
        rows,
        regenerate_command=regenerate_command,
    )
    return by_name


def merge_talents(
    names: list[str],
    *,
    make_hash_id: Callable[[str, str], str],
    normalize_name: Callable[[str], str],
    regenerate_command: str = REGENERATE_CLASSES_TALENTS,
) -> dict[str, str]:
    """Write ``talents.csv`` with exactly ``names`` and return ``TalentName`` -> ``TalentId``.

    Rows not in ``names`` are dropped. Known names reuse ids from disk; new names
    get deterministic ``TL`` ids.
    """
    required = set(names)
    disk = _load_name_id_map(TALENTS_CSV_PATH, "TalentId", "TalentName")
    by_name: dict[str, str] = {}
    for name in required:
        if name in disk:
            by_name[name] = disk[name]
        else:
            by_name[name] = make_hash_id("TL", normalize_name(name))
    assert_unique_ids([(tid, name) for name, tid in by_name.items()], "Talent")
    rows = [
        {"TalentId": by_name[n], "TalentName": n}
        for n in sorted(by_name, key=str.lower)
    ]
    write_pipe_csv_autogen(
        TALENTS_CSV_PATH,
        ["TalentId", "TalentName"],
        rows,
        regenerate_command=regenerate_command,
    )
    return by_name
