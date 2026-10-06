"""Generate ``src/data/md/character-kin.md`` from the database.

One section per connected family cluster (Boltyn's family, Dromai's, and so
on), each carrying two views of the same rows:

- **The tree** — a Mermaid flowchart, one node per person. Parent-child rows
  draw the tree edges; spouse, cousin, aunt-or-uncle and grandparent rows draw
  direct cross-links; a sibling clique with no recorded parent gets one
  synthetic placeholder node to hang off, so the fact still renders as a shape
  instead of being dropped.
- **The cluster's own table** — every fact stated *within* that family, once
  each (not once per direction), naming the pair, the bond and its source.

Has no CSV source, the same reason ``create_character_groups_md.py`` reads the
database directly instead of going through ``create_md.py``: the table is a
join across ``character_kin`` and ``characters``, not a single flat CSV.

Run from the repository root::

    python3 src/data/create_character_kin_md.py
"""

from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "src/data"
DB_PATH = DATA / "fablore.db"
OUTPUT_MD = DATA / "md" / "character-kin.md"

# Needed at module load, unlike create_character_groups_md.py's deferred
# `from db import Database` inside main(): the tree builder below is a pure
# function of KIN_INVERSE, called before main() ever runs in a test that
# imports this module directly. Idempotent and side-effect-free — KIN_INVERSE
# and KIN_QUALIFIERS are plain literals, not a database handle — so doing it
# unconditionally at the top costs nothing, the same way mdbook_graph.py fixes
# up its own sys.path unconditionally at module level.
if str(DATA) not in sys.path:
    sys.path.insert(0, str(DATA))

_BANNER = "<!-- ### NOTE: This file should not be edited by hand. Please edit create_character_kin_md.py. -->\n"

_PARENT_LIKE = frozenset({"father", "mother", "parent"})
"""Stored relations where ``relative_id`` is the *parent* of ``character_id``.
``"child"`` is the other lineage relation and reads the opposite way — see
:func:`_lineage_edges`."""

_SYMMETRIC_LABELS = {
    "sibling": "Siblings",
    "spouse": "Spouses",
    "cousin": "Cousins",
}
"""Pair labels for the relations that read the same from either side — the
asymmetric ones (parent/child, grandparent/grandchild, aunt-or-uncle/
niece-or-nephew) get their label from :func:`_pair_row` instead, since which
name leads depends on which side of the bond each person is on."""


def _md_table(headers: list[str], rows: list[list[str]]) -> str:
    """Render a minimal GFM pipe table — no external padding library."""
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"]
    for row in rows:
        lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines)


def _story_link(story_key: str) -> str:
    """Render ``story_key`` (e.g. ``heroes-of-rathe/boltyn-about.md``) as a page link.

    ``src/data/md/`` sits two directories under ``src/``, the same depth
    ``create_character_groups_md.py`` links its dragon-pronunciation page from.
    """
    title = Path(story_key).stem.replace("-", " ").title()
    return f"[{title}](../../{story_key})"


def _pair_row(char_name: str, relation: str, rel_name: str, qualifier: str) -> tuple[str, str]:
    """Normalise one stated fact to an order-independent ``(pair, label)``.

    ``character_kin`` stores a direction — "Eirina's relation to Aios is
    mother" — but a cluster's own table states the bond once. Parent, elder
    or aunt/uncle leads for the relations that have a "senior" side;
    everything else (siblings, spouses, cousins) sorts alphabetically, since
    neither side reads as the senior one.
    """
    # ``relation`` names what the *relative* is to the declaring character (see
    # ``db._queries.select_character_kin_both_directions``): a "father" row's
    # relative is the father, not the declaring character.
    if relation in _PARENT_LIKE:
        a, b, label = rel_name, char_name, "Parent / child"
    elif relation == "child":
        a, b, label = char_name, rel_name, "Parent / child"
    elif relation == "grandparent":
        a, b, label = rel_name, char_name, "Grandparent / grandchild"
    elif relation == "grandchild":
        a, b, label = char_name, rel_name, "Grandparent / grandchild"
    elif relation == "aunt-or-uncle":
        a, b, label = rel_name, char_name, "Aunt or uncle / niece or nephew"
    elif relation == "niece-or-nephew":
        a, b, label = char_name, rel_name, "Aunt or uncle / niece or nephew"
    else:
        a, b = sorted((char_name, rel_name))
        label = _SYMMETRIC_LABELS[relation]
    if qualifier == "adoptive":
        label += " (adoptive)"
    return f"{a} & {b}", label


class _UnionFind:
    """Disjoint-set over character names, for grouping into clusters and units."""

    def __init__(self) -> None:
        self._parent: dict[str, str] = {}

    def find(self, x: str) -> str:
        self._parent.setdefault(x, x)
        while self._parent[x] != x:
            self._parent[x] = self._parent[self._parent[x]]
            x = self._parent[x]
        return x

    def union(self, a: str, b: str) -> None:
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self._parent[ra] = rb


def _lineage_edges(
    stated: list[tuple[str, str, str, str]],
) -> tuple[dict[str, list[tuple[str, str]]], dict[str, list[tuple[str, str]]]]:
    """Resolve every direct father/mother/parent/child row to ``parent -> child``.

    Returns:
        ``(children_of, parents_of)`` — both ``{name: [(other_name, qualifier), ...]}``,
        deduplicated (a "father" row and its sibling "mother" row for the same
        child both keep their own entry; the same pair stated twice does not,
        since ``character_kin``'s primary key already forbids that upstream).
    """
    children_of: dict[str, list[tuple[str, str]]] = {}
    parents_of: dict[str, list[tuple[str, str]]] = {}
    for char_name, relation, rel_name, qualifier in stated:
        if relation in _PARENT_LIKE:
            parent, child = rel_name, char_name
        elif relation == "child":
            parent, child = char_name, rel_name
        else:
            continue
        children_of.setdefault(parent, []).append((child, qualifier))
        parents_of.setdefault(child, []).append((parent, qualifier))
    return children_of, parents_of


_UNKNOWN_PREFIX = "__unknown__"
"""Synthetic node key prefix for a sibling clique with no recorded parent —
can't collide with a real character name, which is never declared this way."""


def _unknown_parent_nodes(
    people: set[str],
    parents_of: dict[str, list[tuple[str, str]]],
    sibling_pairs: set[frozenset],
) -> dict[str, list[str]]:
    """One placeholder node per sibling clique that has no recorded parent at all.

    A sibling fact says two people share a parent without saying who that
    parent is — Ira, Jing and Xilin are stated siblings of each other, and the
    lore names none of their parents. Rather than drop the fact, give the
    clique one synthetic "unknown parent" node and hang each sibling off it,
    the same shape a recorded parent would produce.

    A clique where at least one member already has a recorded parent (Einar
    and Tomass, both children of Hildegun) needs no placeholder — the real
    parent node already draws them together.

    Returns:
        ``{placeholder_key: [member_names]}``, one entry per clique that
        needed one — keys and member order both sorted, for deterministic
        output.
    """
    uf = _UnionFind()
    for name in people:
        uf.find(name)
    for pair in sibling_pairs:
        a, b = tuple(pair)
        uf.union(a, b)

    cliques: dict[str, set[str]] = {}
    for pair in sibling_pairs:
        for name in pair:
            cliques.setdefault(uf.find(name), set()).add(name)

    parentless = sorted(
        (sorted(members) for members in cliques.values() if not any(parents_of.get(m) for m in members)),
        key=lambda members: members[0],
    )
    return {f"{_UNKNOWN_PREFIX}{i}": members for i, members in enumerate(parentless)}


def _lateral_edges(
    stated: list[tuple[str, str, str, str]],
    parents_of: dict[str, list[tuple[str, str]]],
) -> list[tuple[str, str, str, str]]:
    """One ``(relation, from_name, to_name, qualifier)`` per cousin/aunt-or-uncle/
    grandparent fact, for a direct cross-link in the flowchart.

    A grandparent fact is skipped when a stated intermediate parent already
    places the two people two generations apart — the edge would only repeat
    what the parent-child edges already show. It still surfaces when no such
    intermediate is stated (a page names a grandparent with no parent link on
    record), which is the situation this relation exists for.
    """
    edges: list[tuple[str, str, str, str]] = []
    seen: set[frozenset] = set()
    for char_name, relation, rel_name, qualifier in stated:
        if relation not in ("cousin", "aunt-or-uncle", "grandparent", "grandchild"):
            continue
        pair = frozenset({char_name, rel_name})
        if pair in seen:
            continue
        seen.add(pair)
        if relation == "cousin":
            edges.append(("cousin", char_name, rel_name, qualifier))
        elif relation in ("aunt-or-uncle", "niece-or-nephew"):
            aunt_uncle, niece_nephew = (rel_name, char_name) if relation == "aunt-or-uncle" else (char_name, rel_name)
            edges.append(("aunt-or-uncle", aunt_uncle, niece_nephew, qualifier))
        else:
            grandparent, grandchild = (rel_name, char_name) if relation == "grandparent" else (char_name, rel_name)
            grandparents_of_grandchild = {
                gp for parent, _q in parents_of.get(grandchild, []) for gp, _q2 in parents_of.get(parent, [])
            }
            if grandparent in grandparents_of_grandchild:
                continue  # already visible two levels apart via recorded parents
            edges.append(("grandparent", grandparent, grandchild, qualifier))
    edges.sort()  # `seen` and `stated` both admit set/query ordering upstream — sort to stay deterministic
    return edges


def _mermaid_label(name: str) -> str:
    """Escape a person's name for a quoted Mermaid node label."""
    return name.replace('"', "'")


def _cluster_data(
    stated: list[tuple[str, str, str, str]],
) -> tuple[
    list[str],
    dict[str, list[str]],
    dict[str, list[str]],
    dict[str, list[tuple[str, str]]],
    set[frozenset],
    list[tuple[str, str, str, str]],
]:
    """Group every stated kin fact into connected family clusters.

    One node per person — a person with several recorded parents (Dromai: two
    blood, one adoptive) just gets several incoming edges. No merging step,
    and no risk of a shared child appearing twice under two different parent
    boxes, the problem the previous nested-list renderer needed a union-find
    over "family units" to avoid.

    Returns:
        ``(cluster_order, clusters, unknown_nodes, children_of, spouse_pairs, lateral)``:
        ``cluster_order`` is every cluster's key, sorted by its earliest real
        name; ``clusters`` maps each key to its node list (real people plus
        any synthetic unknown-parent placeholders); the rest are what
        :func:`_render_tree_block` and the per-cluster table both draw edges
        from.
    """
    children_of, parents_of = _lineage_edges(stated)

    people: set[str] = set()
    cluster_uf = _UnionFind()
    spouse_pairs: set[frozenset] = set()
    sibling_pairs: set[frozenset] = set()
    for char_name, relation, rel_name, _ql in stated:
        people.add(char_name)
        people.add(rel_name)
        cluster_uf.union(char_name, rel_name)
        if relation == "spouse":
            spouse_pairs.add(frozenset({char_name, rel_name}))
        elif relation == "sibling":
            sibling_pairs.add(frozenset({char_name, rel_name}))

    unknown_nodes = _unknown_parent_nodes(people, parents_of, sibling_pairs)
    for placeholder, members in unknown_nodes.items():
        for member in members:
            cluster_uf.union(placeholder, member)

    lateral = _lateral_edges(stated, parents_of)

    all_nodes = people | set(unknown_nodes)
    clusters: dict[str, list[str]] = {}
    for node in all_nodes:
        clusters.setdefault(cluster_uf.find(node), []).append(node)

    cluster_order = sorted(clusters, key=lambda r: min(n for n in clusters[r] if n in people))
    return cluster_order, clusters, unknown_nodes, children_of, spouse_pairs, lateral


def _render_tree_block(
    cluster_nodes: list[str],
    unknown_nodes: dict[str, list[str]],
    children_of: dict[str, list[tuple[str, str]]],
    spouse_pairs: set[frozenset],
    lateral: list[tuple[str, str, str, str]],
) -> str:
    """Render one Mermaid ``flowchart TD`` for a single family cluster."""
    # Real people first (alphabetical), placeholders last — deterministic
    # regardless of the set iteration order that built `cluster_nodes`.
    cluster_nodes = sorted(cluster_nodes, key=lambda n: (n in unknown_nodes, n))
    node_id = {name: f"n{i}" for i, name in enumerate(cluster_nodes)}

    lines = ["flowchart TD"]
    for name in cluster_nodes:
        if name in unknown_nodes:
            lines.append(f'    {node_id[name]}(("?")):::unknown')
        else:
            lines.append(f'    {node_id[name]}["{_mermaid_label(name)}"]')

    for parent, child_list in children_of.items():
        if parent not in node_id:
            continue
        for child, qualifier in child_list:
            if child not in node_id:
                continue
            arrow = "-. adoptive .->" if qualifier == "adoptive" else "-->"
            lines.append(f"    {node_id[parent]} {arrow} {node_id[child]}")

    for placeholder, members in unknown_nodes.items():
        if placeholder not in node_id:
            continue
        for member in members:
            lines.append(f"    {node_id[placeholder]} -.-> {node_id[member]}")

    for a, b in sorted(tuple(sorted(pair)) for pair in spouse_pairs):
        if a not in node_id or b not in node_id:
            continue
        lines.append(f"    {node_id[a]} --- {node_id[b]}")

    for relation, a, b, qualifier in lateral:
        if a not in node_id or b not in node_id:
            continue
        tag = " (adoptive)" if qualifier == "adoptive" else ""
        if relation == "cousin":
            lines.append(f"    {node_id[a]} -. cousin{tag} .- {node_id[b]}")
        elif relation == "aunt-or-uncle":
            lines.append(f"    {node_id[a]} -. aunt/uncle{tag} .-> {node_id[b]}")
        else:
            lines.append(f"    {node_id[a]} -. grandparent{tag} .-> {node_id[b]}")

    lines.append("    classDef unknown stroke-dasharray: 4 3,fill:transparent;")
    return "```mermaid\n" + "\n".join(lines) + "\n```"


def _render_cluster_table(
    cluster_people: set[str],
    stated_with_story: list[tuple[str, str, str, str, str]],
) -> tuple[str, str]:
    """Return ``(heading, table)`` for one cluster's own sourced facts.

    ``stated_with_story`` is filtered to facts whose declaring character
    falls in this cluster — every fact's relative is a cluster-mate by
    construction (they were unioned together to make the cluster), so that
    one membership test is enough. Each stated fact becomes exactly one row:
    the doubled book-keeping a flat, page-wide table needs (one row per
    direction, so every character's page shows their own relatives) is not
    needed once a table is already scoped to one small family.

    The heading names every story the cluster's facts cite, so a reader knows
    which pages to check without opening the table.
    """
    story_titles: set[str] = set()
    rows: list[list[str]] = []
    for char_name, relation, rel_name, story_key, qualifier in stated_with_story:
        if char_name not in cluster_people:
            continue
        pair, label = _pair_row(char_name, relation, rel_name, qualifier)
        rows.append([pair, label, _story_link(story_key) if story_key else ""])
        if story_key:
            story_titles.add(Path(story_key).stem.replace("-", " ").title())
    rows.sort()
    heading = " / ".join(sorted(story_titles))
    return heading, _md_table(["Pair", "Relation", "Source"], rows)


def render_markdown(conn: sqlite3.Connection) -> str:
    """Render the full Character Relationships page from ``conn``.

    Deterministic: every cluster, its tree and its table are all built from
    sorted input, so two runs against the same database produce
    byte-identical output.
    """
    stated_rows = conn.execute(
        """
        SELECT c.name AS char_name, k.relation, r.name AS rel_name, k.story_key, k.qualifier
        FROM character_kin k
        JOIN characters c ON c.character_id = k.character_id
        JOIN characters r ON r.character_id = k.relative_id
        ORDER BY c.name, r.name, k.relation
        """
    ).fetchall()
    stated_with_story = [
        (r["char_name"], r["relation"], r["rel_name"], r["story_key"], r["qualifier"]) for r in stated_rows
    ]
    stated = [
        (char_name, relation, rel_name, qualifier)
        for char_name, relation, rel_name, _sk, qualifier in stated_with_story
    ]

    intro = (
        "Named family relationships stated in the lore — parents, children, siblings, "
        "spouses, cousins, aunts/uncles and grandparents, marked *(adoptive)* where the "
        "story is explicit that a bond is fostered or adopted rather than blood.\n"
    )

    if not stated:
        return "# Character Relationships\n\n" + intro

    cluster_order, clusters, unknown_nodes, children_of, spouse_pairs, lateral = _cluster_data(stated)

    sections: list[str] = []
    for root in cluster_order:
        cluster_nodes = clusters[root]
        cluster_people = {n for n in cluster_nodes if n not in unknown_nodes}
        tree = _render_tree_block(cluster_nodes, unknown_nodes, children_of, spouse_pairs, lateral)
        heading, table = _render_cluster_table(cluster_people, stated_with_story)
        sections.append(f"### {heading}\n\n{tree}\n\n{table}")

    return "# Character Relationships\n\n" f"{intro}\n" "## Families\n\n" + "\n\n".join(sections) + "\n"


def main(output_md: Path = OUTPUT_MD, *, db_path: Path | None = None) -> None:
    """Render the Character Relationships markdown from ``fablore.db`` to ``output_md``.

    Opens the database through :class:`db.Database`, not a bare ``sqlite3``
    connection — the DB is a runtime artefact seeded from the CSVs on first
    open, so this works on a fresh clone where ``fablore.db`` does not exist
    yet, the same way ``create_character_groups_md.py`` does.
    """
    from db import Database

    database = Database(db_path if db_path is not None else DB_PATH)
    try:
        text = render_markdown(database.conn)
    finally:
        database.conn.close()
    Path(output_md).write_text(_BANNER + text, encoding="utf-8")


if __name__ == "__main__":
    main()
