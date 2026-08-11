"""Invariants for the story declarations in ``src/data/entries/``.

The declarations are read with :mod:`ast`, never imported. Importing a section
module executes its ``upsert_story`` calls against the real database, which
these tests must not do — and parsing means they still run in a checkout with
no ``fablore.db``.

What they protect:

- **One declaration per story.** ``upsert_story`` has replace semantics, so a
  second declaration for the same path silently wins and the first becomes a
  block of edits that look applied and are not.
- **Every declared path still exists.** ``StoryId`` is a hash of the path, so
  moving a page mints a new id and strands the junction rows pointing at the
  old one. A declaration left behind on the old path is how that happens
  quietly.
- **Declarations sit in the module their path implies**, which is what makes
  ``entries/`` navigable as it grows.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from entries import SECTIONS

ROOT = Path(__file__).resolve().parent.parent
ENTRIES_DIR = ROOT / "src" / "data" / "entries"
STORIES_CSV = ROOT / "src" / "data" / "csv" / "stories.csv"


def _declarations(module: str) -> list[tuple[str, str, int]]:
    """Return ``(path, story_type, lineno)`` for each ``db.upsert_story`` call."""
    source = (ENTRIES_DIR / f"{module}.py").read_text(encoding="utf-8")
    tree = ast.parse(source, filename=f"{module}.py")
    found: list[tuple[str, str, int]] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if not (
            isinstance(func, ast.Attribute)
            and func.attr == "upsert_story"
            and isinstance(func.value, ast.Name)
            and func.value.id == "db"
        ):
            continue
        kwargs = {kw.arg: kw.value.value for kw in node.keywords if kw.arg and isinstance(kw.value, ast.Constant)}
        found.append((kwargs.get("path"), kwargs.get("story_type"), node.lineno))
    return found


ALL_DECLARATIONS = [(module, *decl) for module in SECTIONS for decl in _declarations(module)]


def _story_keys() -> set[str]:
    lines = STORIES_CSV.read_text(encoding="utf-8").splitlines()
    rows = [ln for ln in lines if not ln.startswith("#")][1:]  # skip banner + header
    return {ln.split("|")[1] for ln in rows if ln.strip()}


def test_every_section_module_exists() -> None:
    """SECTIONS is the runner's import list — a missing module fails silently there."""
    for module in SECTIONS:
        assert (ENTRIES_DIR / f"{module}.py").is_file(), f"entries/{module}.py is missing"


def test_no_section_module_is_unlisted() -> None:
    """A module the runner never imports would hold declarations that never run."""
    on_disk = {p.stem for p in ENTRIES_DIR.glob("*.py") if not p.stem.startswith("_")}
    assert on_disk == set(SECTIONS), f"entries/ modules not listed in SECTIONS: {on_disk - set(SECTIONS)}"


def test_declarations_were_found() -> None:
    """Guard the AST matcher itself: a rename would otherwise make every test below vacuous."""
    assert len(ALL_DECLARATIONS) > 0


@pytest.mark.parametrize("module, path, story_type, lineno", ALL_DECLARATIONS)
def test_declaration_has_literal_path_and_type(module, path, story_type, lineno) -> None:
    """Both are string literals — everything else here reads them statically."""
    assert path, f"entries/{module}.py:{lineno} has no literal path="
    assert story_type, f"entries/{module}.py:{lineno} has no literal story_type="


def test_no_duplicate_paths() -> None:
    seen: dict[str, str] = {}
    duplicates: list[str] = []
    for module, path, _story_type, lineno in ALL_DECLARATIONS:
        where = f"entries/{module}.py:{lineno}"
        if path in seen:
            duplicates.append(f"{path} declared at {seen[path]} and again at {where}")
        else:
            seen[path] = where
    assert not duplicates, "\n".join(duplicates)


@pytest.mark.parametrize("module, path, story_type, lineno", ALL_DECLARATIONS)
def test_declared_path_exists_on_disk(module, path, story_type, lineno) -> None:
    assert (ROOT / path).is_file(), f"entries/{module}.py:{lineno} declares a missing page: {path}"


@pytest.mark.parametrize("module, path, story_type, lineno", ALL_DECLARATIONS)
def test_declared_path_is_a_known_story(module, path, story_type, lineno) -> None:
    """A declared page must have a stories.csv row, or its links point at nothing."""
    key = path[len("src/") :] if path.startswith("src/") else path
    assert key in _story_keys(), (
        f"entries/{module}.py:{lineno} declares {path}, which has no stories.csv row — "
        "run python3 src/data/create_stories_index.py"
    )


@pytest.mark.parametrize("module, path, story_type, lineno", ALL_DECLARATIONS)
def test_story_type_matches_path_and_module(module, path, story_type, lineno) -> None:
    from_path = path[len("src/") :].split("/")[0] if path.startswith("src/") else ""
    assert story_type == from_path, (
        f"entries/{module}.py:{lineno} declares story_type={story_type!r} " f"but sits at {path!r}"
    )
    assert story_type == SECTIONS[module], (
        f"entries/{module}.py:{lineno} holds a {story_type!r} declaration; " f"that module is for {SECTIONS[module]!r}"
    )
