"""Unit tests for ``mdbook_browse``."""

from __future__ import annotations

from pathlib import Path

from mdbook_browse import build_index
from pipe_csv_io import write_pipe_csv_autogen


def _data_dir(tmp_path: Path) -> Path:
    data_dir = tmp_path / "data"
    write_pipe_csv_autogen(
        data_dir / "csv" / "stories.csv",
        ["StoryId", "StoryKey", "StoryType", "Title", "PublicationDate"],
        [
            {"StoryId": "ST1", "StoryKey": "main-story/a.md", "StoryType": "main-story", "Title": "A"},
            {"StoryId": "ST2", "StoryKey": "main-story/README.md", "StoryType": "main-story", "Title": "Docs"},
            {"StoryId": "ST3", "StoryKey": "summaries/README.md", "StoryType": "summaries", "Title": "Hub"},
        ],
        regenerate_command="test",
    )
    return data_dir


def test_build_index_without_rendered_set_keeps_every_story(tmp_path: Path) -> None:
    urls = [s["u"] for s in build_index(_data_dir(tmp_path))["stories"]]
    assert sorted(urls) == ["main-story/a.html", "main-story/index.html", "summaries/index.html"]


def test_build_index_drops_stories_the_book_does_not_render(tmp_path: Path) -> None:
    """A registered page absent from SUMMARY.md gets no card: its link would 404."""
    rendered = {"main-story/a.md", "summaries/README.md"}
    urls = [s["u"] for s in build_index(_data_dir(tmp_path), rendered=rendered)["stories"]]
    assert sorted(urls) == ["main-story/a.html", "summaries/index.html"]
