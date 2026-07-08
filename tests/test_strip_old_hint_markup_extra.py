"""Extra tests for strip_old_hint_markup.main() — covers lines 32-42, 46."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src" / "data"))

import strip_old_hint_markup as mod


def test_main_reports_changed_files(tmp_path, monkeypatch, capsys):
    src = tmp_path / "src"
    src.mkdir()
    f = src / "test.md"
    f.write_text("[Foo](~FooKey) is here.", encoding="utf-8")
    monkeypatch.setattr(mod, "SRC", src)
    monkeypatch.setattr(mod, "ROOT", tmp_path)
    mod.main()
    captured = capsys.readouterr()
    assert "test.md" in captured.out or "Updated" in captured.out
    assert f.read_text() == "Foo is here."


def test_main_reports_no_changes(tmp_path, monkeypatch, capsys):
    src = tmp_path / "src"
    src.mkdir()
    f = src / "clean.md"
    f.write_text("# Normal heading\n\nNo hint markup here.", encoding="utf-8")
    monkeypatch.setattr(mod, "SRC", src)
    monkeypatch.setattr(mod, "ROOT", tmp_path)
    mod.main()
    captured = capsys.readouterr()
    assert "No files" in captured.out


def test_main_processes_nested_files(tmp_path, monkeypatch, capsys):
    src = tmp_path / "src"
    sub = src / "main-story"
    sub.mkdir(parents=True)
    f = sub / "story.md"
    f.write_text("[Hand of Sol](~HandOfSol) appeared.", encoding="utf-8")
    monkeypatch.setattr(mod, "SRC", src)
    monkeypatch.setattr(mod, "ROOT", tmp_path)
    mod.main()
    assert f.read_text() == "Hand of Sol appeared."


def test_main_counts_multiple_changed_files(tmp_path, monkeypatch, capsys):
    src = tmp_path / "src"
    src.mkdir()
    (src / "a.md").write_text("[Alpha](~A) here.", encoding="utf-8")
    (src / "b.md").write_text("[Beta](~B) there.", encoding="utf-8")
    (src / "c.md").write_text("# Clean file", encoding="utf-8")
    monkeypatch.setattr(mod, "SRC", src)
    monkeypatch.setattr(mod, "ROOT", tmp_path)
    mod.main()
    captured = capsys.readouterr()
    assert "2" in captured.out
    assert "a.md" in captured.out
    assert "b.md" in captured.out


def test_main_multiple_markup_in_one_file(tmp_path, monkeypatch, capsys):
    src = tmp_path / "src"
    src.mkdir()
    f = src / "multi.md"
    f.write_text("[Foo](~FooKey) and [Bar](~BarKey) met.", encoding="utf-8")
    monkeypatch.setattr(mod, "SRC", src)
    monkeypatch.setattr(mod, "ROOT", tmp_path)
    mod.main()
    assert f.read_text() == "Foo and Bar met."
