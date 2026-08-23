"""Tests for :func:`generate_hints_json.merge_supplement`."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src/data"))

from generate_hints_json import merge_supplement  # noqa: E402


def test_exact_key_override():
    hints = {"Brawnhide": {"type": "fauna", "summary": "A beast."}}
    supplement = {"Brawnhide": {"summary": "Updated summary."}}
    result = merge_supplement(hints, supplement)
    assert result["Brawnhide"]["summary"] == "Updated summary."
    assert result["Brawnhide"]["type"] == "fauna"


def test_exact_key_adds_exclude_pages():
    hints = {"Brawnhide": {"type": "fauna", "summary": "A beast."}}
    supplement = {"Brawnhide": {"exclude_pages": ["main-story/set/story"]}}
    result = merge_supplement(hints, supplement)
    assert result["Brawnhide"]["exclude_pages"] == ["main-story/set/story"]
    assert result["Brawnhide"]["type"] == "fauna"


def test_match_based_merge_replaces_db_key():
    # DB key has a space; supplement uses camelCase + "match" field
    hints = {"Shadowrealm Walker": {"type": "monster", "summary": "Big predator."}}
    supplement = {
        "ShadowrealmWalker": {
            "match": "Shadowrealm Walker",
            "exclude_pages": ["main-story/set/story"],
        }
    }
    result = merge_supplement(hints, supplement)
    assert "Shadowrealm Walker" not in result
    assert "ShadowrealmWalker" in result
    entry = result["ShadowrealmWalker"]
    assert entry["type"] == "monster"
    assert entry["summary"] == "Big predator."
    assert entry["match"] == "Shadowrealm Walker"
    assert entry["exclude_pages"] == ["main-story/set/story"]


def test_match_based_merge_apostrophe_key():
    # DB key strips apostrophes; supplement match field contains the apostrophe
    hints = {"Kaeio": {"match": "Kae'io", "type": "fauna", "summary": "A bird."}}
    supplement = {"KaeioCustom": {"match": "Kae'io", "exclude_pages": ["some/page"]}}
    result = merge_supplement(hints, supplement)
    assert "Kaeio" not in result
    assert "KaeioCustom" in result
    assert result["KaeioCustom"]["type"] == "fauna"
    assert result["KaeioCustom"]["exclude_pages"] == ["some/page"]


def test_supplement_only_key_appended():
    hints = {"Brawnhide": {"type": "fauna", "summary": "A beast."}}
    supplement = {"NewFaction": {"type": "faction", "summary": "A new group."}}
    result = merge_supplement(hints, supplement)
    assert "Brawnhide" in result
    assert "NewFaction" in result
    assert result["NewFaction"]["type"] == "faction"


def test_match_field_not_in_db_does_not_merge():
    # supplement "match" points to something not in hints — treat as new entry
    hints = {"Brawnhide": {"type": "fauna", "summary": "A beast."}}
    supplement = {"SomeKey": {"match": "Unknown Entity", "type": "npc", "summary": "..."}}
    result = merge_supplement(hints, supplement)
    assert "SomeKey" in result
    assert "Unknown Entity" not in result
    assert "Brawnhide" in result


def test_original_hints_not_mutated():
    hints = {"Brawnhide": {"type": "fauna", "summary": "A beast."}}
    supplement = {"Brawnhide": {"exclude_pages": ["some/page"]}}
    merge_supplement(hints, supplement)
    assert "exclude_pages" not in hints["Brawnhide"]


# ---------------------------------------------------------------------------
# The ensure-hints-json-sync pre-commit trigger
# ---------------------------------------------------------------------------


def _hints_hook_csv_stems() -> tuple[set[str], str]:
    """Return the CSV stems named in the ensure-hints-json-sync trigger, and the regex."""
    import re

    config = (ROOT / ".pre-commit-config.yaml").read_text(encoding="utf-8")
    hook = config[config.index("id: ensure-hints-json-sync") :]
    line = next(x for x in hook.splitlines() if x.strip().startswith("files:"))
    pattern = line.split("files:", 1)[1].strip()
    stems: set[str] = set()
    for group in re.findall(r"csv/\(([a-z0-9|-]+)\)\\\.csv", pattern):
        stems |= set(group.split("|"))
    return stems, pattern


def test_the_hints_sync_hook_triggers_on_files_that_actually_exist() -> None:
    """Every CSV the ensure-hints-json-sync trigger names must be a real file."""
    stems, pattern = _hints_hook_csv_stems()
    assert stems, f"no CSV stems found in the trigger: {pattern}"
    missing = [s for s in sorted(stems) if not (ROOT / "src/data/csv" / f"{s}.csv").is_file()]
    assert not missing, f"ensure-hints-json-sync triggers on files that do not exist: {missing}"


def test_the_hints_sync_hook_triggers_on_every_csv_the_generator_reads() -> None:
    """Every table `generate_hints_json.py` reads must reach the hook's trigger.

    Stage 10 gave the generator two new sources — `characters` and
    `npc_epithets` — and left this regex naming only locations, monsters, fauna
    and flora. Editing either new source therefore did not fire the check, and
    `src/hints.json` could go stale in a commit that nothing complained about.
    That is the same shape as the `ensure-create-md-sync` bug that named
    `npcs.csv` for four commits after the rename: a new source, like a rename,
    cannot break a hook loudly.

    The table list is read out of the generator's own SQL rather than written
    down here, so adding a `FROM` or a `_alias_map` call to the generator fails
    this test until the trigger names its CSV too.
    """
    import re

    source = (ROOT / "src/data/generate_hints_json.py").read_text(encoding="utf-8")
    tables: set[str] = set()
    tables |= set(re.findall(r"\bFROM\s+([a-z_]+)", source))
    tables |= set(re.findall(r"\bJOIN\s+([a-z_]+)", source))
    tables |= set(re.findall(r'_alias_map\(\s*conn,\s*"([a-z_]+)"', source))
    assert tables, "found no tables in the generator's SQL — has the extraction drifted?"

    # Every table the generator reads is seeded from the CSV of the same name
    # with underscores as hyphens. A table that breaks that rule fails here
    # rather than silently dropping out of the comparison.
    wanted = {t.replace("_", "-") for t in tables}
    unseeded = [s for s in sorted(wanted) if not (ROOT / "src/data/csv" / f"{s}.csv").is_file()]
    assert not unseeded, f"no CSV found for tables the generator reads: {unseeded}"

    stems, pattern = _hints_hook_csv_stems()
    untriggered = sorted(wanted - stems)
    assert not untriggered, f"ensure-hints-json-sync does not fire for: {untriggered}\n{pattern}"
