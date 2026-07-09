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
    supplement = {
        "SomeKey": {"match": "Unknown Entity", "type": "npc", "summary": "..."}
    }
    result = merge_supplement(hints, supplement)
    assert "SomeKey" in result
    assert "Unknown Entity" not in result
    assert "Brawnhide" in result


def test_original_hints_not_mutated():
    hints = {"Brawnhide": {"type": "fauna", "summary": "A beast."}}
    supplement = {"Brawnhide": {"exclude_pages": ["some/page"]}}
    merge_supplement(hints, supplement)
    assert "exclude_pages" not in hints["Brawnhide"]
