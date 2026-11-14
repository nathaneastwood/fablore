#!/usr/bin/env python3
"""mdBook preprocessor: link each page to its own node in the Lore Graph.

Without this the graph is reachable only from the table of contents, so nobody
reading a hero or region page ever finds it. Every chapter that *is* a node in
the graph gets one link:

    <!-- fablore-graph-link:start --> … <!-- fablore-graph-link:end -->

pointing at ``graph.html#<slug>``, which opens the graph with that node selected.
Where it goes, first match wins:

* a hero page whose Related Lore heading row ``mdbook_story_meta`` built gets
  the button in that row's ``RELATED_GRAPH_SLOT``, after the source link;
* a page with Related Lore (``mdbook_related``) gets an "Explore in the Lore
  Graph" button beside that heading — the graph is the same kind of "where
  next" as the cards under it;
* a page with a story card (``mdbook_story_meta``) gets it inline in the card's
  links row, at ``GRAPH_SLOT``;
* any other page gets a line of its own under the share sheet, or at the end.

Kept separate from ``mdbook_related.py`` on purpose. That preprocessor computes
the same joins for its Related Lore cards, but it is large and load-bearing;
appending one link does not justify editing it.

Kept separate from ``mdbook_graph.py`` too, although both build the same graph,
because they have to run at opposite ends of the book. This one needs the slots
``story-meta`` and ``related`` leave behind. The graph page's payload has to be
in place before ``hints`` runs: ``hints`` counts the pages that name an entity
(an entity named on one page gets no tooltip), and the payload names every node,
so moving it later changes the tooltips on 27 pages. Running ``hints`` after
this instead changes 330. So this process rebuilds the graph, minus the
printing edges (``printings=False``), which no backlink uses.

mdBook passes ``(PreprocessorContext, Book)`` as JSON on stdin; this process must
print only the modified ``Book`` JSON on stdout. Supports ``supports <renderer>``.
"""

from __future__ import annotations

import html
import re
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from mdbook_common import RELATED_LORE_H1 as RELATED_HEADING  # noqa: E402
from mdbook_common import iter_chapters, md_to_html_url, relative_href, run  # noqa: E402
from mdbook_graph import build_graph, page_graph_targets  # noqa: E402
from mdbook_story_meta import GRAPH_SLOT, RELATED_GRAPH_SLOT  # noqa: E402
from mdbook_story_meta import MARK_END as STORY_META_END  # noqa: E402

MARK_START = "<!-- fablore-graph-link:start -->"
MARK_END = "<!-- fablore-graph-link:end -->"

_GRAPH_SRC_PATH = "graph.md"
# A heading row from an earlier run, unwrapped back to the bare heading.
_RELATED_HEAD_RE = re.compile(
    '<div class="related-head">('
    + re.escape(RELATED_HEADING)
    + ")"
    + re.escape(MARK_START)
    + ".*?"
    + re.escape(MARK_END)
    + "</div>",
    re.DOTALL,
)


def relative_graph_href(chapter_src_path: str, slug: str) -> str:
    """Return an href from a chapter to ``graph.html#slug``.

    mdBook renders each chapter at its own depth, so the link has to climb back
    to the book root rather than assume a flat layout.
    """
    return f"{md_to_html_url(relative_href(Path(chapter_src_path).as_posix(), _GRAPH_SRC_PATH))}#{slug}"


def build_link_html(chapter_src_path: str, node: dict) -> str:
    """Return the one-line link block for a chapter that has a graph node."""
    href = relative_graph_href(chapter_src_path, node["sl"])
    return (
        '<p class="lore-graph-backlink">'
        f'<a href="{html.escape(href)}">'
        f"See {html.escape(node['n'])} in the Lore Graph</a></p>"
    )


def build_card_link_html(chapter_src_path: str, node: dict) -> str:
    """Return the compact link that sits in the story card's links row."""
    href = relative_graph_href(chapter_src_path, node["sl"])
    return (
        f'<a class="story-card-graph" href="{html.escape(href)}" '
        f'title="See {html.escape(node["n"])} in the Lore Graph">'
        '<i class="fas fa-diagram-project" aria-hidden="true"></i> Lore Graph</a>'
    )


def build_related_button_html(chapter_src_path: str, node: dict) -> str:
    """Return the button that sits beside the Related Lore heading."""
    href = relative_graph_href(chapter_src_path, node["sl"])
    return (
        f'<a class="related-graph-btn" href="{html.escape(href)}">'
        'Explore in the Lore Graph <span aria-hidden="true">→</span></a>'
    )


def inject_beside_related_heading(content: str, inner_html: str) -> str:
    """Put the link beside the Related Lore heading, in a row of its own."""
    content = _RELATED_HEAD_RE.sub(lambda m: m.group(1), content)
    return content.replace(
        RELATED_HEADING,
        f'<div class="related-head">{RELATED_HEADING}{MARK_START}{inner_html}{MARK_END}</div>',
        1,
    )


def inject_into_slot(content: str, inner_html: str, slot: str = GRAPH_SLOT) -> str:
    """Put the link in the story card's slot, inline with the other links.

    The slot comment stays put and the link follows it, so a rebuild strips
    the old link and finds the slot again.
    """
    if MARK_START in content and MARK_END in content:
        pre, _, rest = content.partition(MARK_START)
        _, _, post = rest.partition(MARK_END)
        content = pre + post
    return content.replace(slot, f"{slot}{MARK_START}{inner_html}{MARK_END}", 1)


def inject_into_content(content: str, inner_html: str) -> str:
    """Put the backlink directly beneath the share sheet.

    ``mdbook_story_meta`` renders the metadata card and share buttons in a block
    just under the page's H1, so its end marker is where the link belongs — the
    graph is a way of navigating the archive, and it sits with the other
    navigation rather than buried above Related Lore. Pages with no share sheet
    (``book.toml`` runs this after ``story-meta``, so its absence is real, not a
    matter of ordering) fall back to the end of the page.

    Replaces any previous block, so re-running the build never stacks links up.
    """
    block = f"{MARK_START}\n{inner_html}\n{MARK_END}"

    if MARK_START in content and MARK_END in content:
        pre, _, rest = content.partition(MARK_START)
        _, _, post = rest.partition(MARK_END)
        content = pre.rstrip("\n") + post

    if STORY_META_END in content:
        head, marker, tail = content.partition(STORY_META_END)
        return f"{head}{marker}\n\n{block}\n\n{tail.lstrip()}"

    sep = "\n\n" if content.strip() else ""
    return content.rstrip() + sep + f"{block}\n"


def walk_and_process(sections: list, targets: dict[str, dict]) -> None:
    """Append the backlink to every chapter that maps to a node."""
    for ch in iter_chapters(sections):
        path = (ch.get("path") or "").strip()
        node = targets.get(Path(path).as_posix()) if path else None
        # Never on the graph page itself — it would link to where you already are.
        if node and path != _GRAPH_SRC_PATH:
            content = ch.get("content") or ""
            if RELATED_GRAPH_SLOT in content:
                # A hero page: the Related Lore heading row already holds the source link.
                ch["content"] = inject_into_slot(content, build_related_button_html(path, node), RELATED_GRAPH_SLOT)
            elif RELATED_HEADING in content:
                ch["content"] = inject_beside_related_heading(content, build_related_button_html(path, node))
            elif GRAPH_SLOT in content:
                ch["content"] = inject_into_slot(content, build_card_link_html(path, node))
            else:
                ch["content"] = inject_into_content(content, build_link_html(path, node))


def process(items: list, src_root: Path) -> None:
    """Link every page that has a node to it, building the graph without its printings.

    Printing edges never add or drop a node, so no page's target depends on them.
    """
    graph = build_graph(src_root / "data", src_root, printings=False)
    walk_and_process(items, page_graph_targets(graph))


def main() -> None:
    run(process)


if __name__ == "__main__":
    main()
