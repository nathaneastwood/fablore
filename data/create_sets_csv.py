"""Generate ``sets.csv`` and ``set-types.csv`` from the upstream flesh-and-blood-cards tab-separated set exports.

Upstream files (sibling repo ``flesh-and-blood-cards``):

- ``set.csv`` — set identifiers and display names.
- ``set-printing.csv`` — earliest release date per set.

Outputs are pipe-delimited under ``src/data/``. Run ``validate_data.py`` when
executed as ``__main__``.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from pipe_csv_io import REGENERATE_CREATE_SETS, write_pipe_csv_autogen  # noqa: E402
from registry_ids import make_hash_id  # noqa: E402
from tab_csv_io import read_tab_csv  # noqa: E402
from text_utils import normalize_name  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
SETS_CSV_PATH = ROOT / "src/data/csv/sets.csv"
SET_TYPES_CSV_PATH = ROOT / "src/data/csv/set-types.csv"
UPSTREAM_SET_CSV_PATH = ROOT.parent / "flesh-and-blood-cards/csvs/english/set.csv"
UPSTREAM_SET_PRINTING_CSV_PATH = (
    ROOT.parent / "flesh-and-blood-cards/csvs/english/set-printing.csv"
)


def infer_set_type_label(set_id: str, set_name: str) -> str:
    """Infer a human-readable set type label from id and name heuristics.

    Args:
        set_id: Game set code (e.g. ``CRU``).
        set_name: Full set display name from upstream data.

    Returns:
        A label such as ``Blitz Deck`` or ``Core Booster Set``.
    """
    name = set_name.lower()
    if "armory deck" in name or "amory deck" in name:
        return "Armory Deck"
    if "blitz deck" in name:
        if "history pack" in name:
            return "History Pack Blitz Deck"
        return "Blitz Deck"
    if "hero deck" in name:
        return "Hero Deck"
    if "demo deck" in name:
        return "Demo Deck"
    if "first strike" in name:
        return "First Strike Deck"
    if "classic battles" in name:
        return "Classic Battles Deck"
    if "welcome deck" in name:
        return "Welcome Deck"
    if "history pack" in name:
        return "History Pack"
    if "promo" in name:
        return "Promo"
    if "prize" in name:
        return "Prize"
    if "token" in name:
        return "Token Set"
    if "mastery pack" in name:
        return "Mastery Pack"
    if "silver age chapter" in name:
        return "Silver Age Chapter Deck"
    if "round the table" in name:
        return "Box Set"
    if set_id in {"CRU", "EVR", "DTD", "SMP", "SUP"}:
        return "Supplementary Booster Set"
    if set_id in {"DYN", "EVO"}:
        return "Expansion Booster Set"
    return "Core Booster Set"


def infer_set_type_layer(set_type: str) -> str:
    """Map a set type label to a coarse release layer for grouping.

    Args:
        set_type: Label produced by :func:`infer_set_type_label`.

    Returns:
        One of ``Deck Releases``, ``Booster Releases``, or ``Other``.
    """
    deck_release_types = {
        "Armory Deck",
        "Blitz Deck",
        "Box Set",
        "Classic Battles Deck",
        "Demo Deck",
        "First Strike Deck",
        "Hero Deck",
        "History Pack Blitz Deck",
        "Silver Age Chapter Deck",
        "Welcome Deck",
    }
    booster_release_types = {
        "Core Booster Set",
        "History Pack",
        "Mastery Pack",
        "Supplementary Booster Set",
    }
    if set_type in deck_release_types:
        return "Deck Releases"
    if set_type in booster_release_types:
        return "Booster Releases"
    return "Other"


def generate_sets_csv() -> None:
    """Read upstream set files and write ``set-types.csv`` and ``sets.csv``.

    Raises:
        FileNotFoundError: Implicit if upstream paths are wrong (empty reads).
    """
    set_rows = read_tab_csv(UPSTREAM_SET_CSV_PATH)
    set_printing_rows = read_tab_csv(UPSTREAM_SET_PRINTING_CSV_PATH)

    set_identifier_by_unique = {row["Unique ID"]: row["Identifier"] for row in set_rows}
    set_name_by_identifier: dict[str, str] = {}
    for row in set_rows:
        identifier = row.get("Identifier", "")
        if identifier:
            set_name_by_identifier.setdefault(identifier, row.get("Name", ""))

    set_release_by_identifier: dict[str, str] = {}
    for row in set_printing_rows:
        set_identifier = set_identifier_by_unique.get(row.get("Set Unique ID", ""))
        release = row.get("Initial Release Date", "").strip()
        if not set_identifier or not release:
            continue
        current = set_release_by_identifier.get(set_identifier)
        if not current or release < current:
            set_release_by_identifier[set_identifier] = release

    set_type_label_by_set_id: dict[str, str] = {}
    for set_id, set_name in set_name_by_identifier.items():
        set_type_label_by_set_id[set_id] = infer_set_type_label(set_id, set_name)

    set_types_rows = []
    for set_type in sorted(set(set_type_label_by_set_id.values())):
        set_types_rows.append(
            {
                "SetTypeId": make_hash_id("TY", normalize_name(set_type)),
                "SetType": set_type,
                "SetTypeLayer": infer_set_type_layer(set_type),
            }
        )
    set_type_id_lookup = {row["SetType"]: row["SetTypeId"] for row in set_types_rows}
    set_type_id_by_set_id = {
        set_id: set_type_id_lookup.get(set_type_label_by_set_id.get(set_id, ""), "")
        for set_id in set_name_by_identifier.keys()
    }

    output_rows = []
    for set_id in sorted(set_name_by_identifier.keys()):
        output_rows.append(
            {
                "SetId": set_id,
                "SetTypeId": set_type_id_by_set_id.get(set_id, ""),
                "SetName": set_name_by_identifier.get(set_id, ""),
                "InitialReleaseDate": set_release_by_identifier.get(set_id, ""),
            }
        )

    write_pipe_csv_autogen(
        SET_TYPES_CSV_PATH,
        ["SetTypeId", "SetType", "SetTypeLayer"],
        set_types_rows,
        regenerate_command=REGENERATE_CREATE_SETS,
    )

    write_pipe_csv_autogen(
        SETS_CSV_PATH,
        ["SetId", "SetTypeId", "SetName", "InitialReleaseDate"],
        output_rows,
        regenerate_command=REGENERATE_CREATE_SETS,
    )


if __name__ == "__main__":
    generate_sets_csv()
    _vd = Path(__file__).resolve().parent / "validate_data.py"
    _rc = subprocess.run([sys.executable, str(_vd)], cwd=str(ROOT))
    raise SystemExit(_rc.returncode)
