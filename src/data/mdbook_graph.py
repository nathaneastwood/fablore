#!/usr/bin/env python3
"""mdBook preprocessor: generate the Lore Graph page.

Finds the chapter at ``graph.md`` and replaces the
``<!-- fablore-graph:start --> … <!-- fablore-graph:end -->`` marker block with an
inline ``<script>`` carrying the node/link payload plus the canvas shell that
``theme/graph.js`` renders into.

The graph is bipartite: every story is a node, every registry entity that a story
links to is a node, and every row of the ten ``story-*`` junction CSVs is an edge.
Entities that no story references are left out — they would render as isolated
dots. Story types that exist only as reference pages (``heroes-of-rathe``,
``other-characters``, ``weapons``, ``equipment``) are skipped as *story* nodes
because the matching entity node already carries that page's URL; including both
would draw the same page twice. ``archive`` is skipped as superseded.

Nodes are keyed by registry id, which is unique across types by prefix (``ST``,
``CN``, ``LC``, ``LO``, ``RG``, ``MO``, ``FA``, ``FL``, ``FD``, ``CW``, ``CE``),
so no namespacing is needed. Links are emitted as index pairs into the node array
to keep the inline payload small.

Stdlib only, like the other preprocessors, and reads the CSVs rather than
``fablore.db`` so a clean checkout builds without seeding the database.

mdBook passes ``(PreprocessorContext, Book)`` as JSON on stdin; this process must
print only the modified ``Book`` JSON on stdout. Supports ``supports <renderer>``.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from card_name_slug import slugify_card_name_stem  # noqa: E402
from hero_overrides import HERO_SLUG_LORE_FILE_OVERRIDES  # noqa: E402
from pipe_csv_io import read_pipe_csv  # noqa: E402

MARK_START = "<!-- fablore-graph:start -->"
MARK_END = "<!-- fablore-graph:end -->"

_GRAPH_SRC_PATH = "graph.md"

# Story types that are reference pages rather than narrative, or superseded.
# Their pages are reachable through the entity node that represents them.
_SKIP_STORY_TYPES: frozenset[str] = frozenset(
    {
        "archive",
        "heroes-of-rathe",
        "other-characters",
        "weapons",
        "equipment",
    }
)

# Sets have no page of their own; the sets hub carries an anchor per arc slug.
_SETS_HUB_URL = "sets/index.html"

# Folder-per-arc sections. `flavour/` names its arc in the filename instead.
_ARC_FOLDER_SECTIONS: frozenset[str] = frozenset({"main-story", "short-stories", "digital-tiles"})

# Fine-grained node kind -> (display label, colour group, mark shape).
# Groups are capped at four hues plus a neutral. A force layout puts arbitrary
# pairs of nodes side by side, so the palette has to clear the *all-pairs*
# colour-vision separation floor rather than the adjacent-pair one, and four
# hues is what clears it. Everything past the four folds into the neutral group
# and is told apart by the legend text and the inspector panel.
#
# Shape is the secondary channel that hue cannot afford. Two pairs share a hue
# but are not peers: a hero is the canonical character and a region is the
# canonical place, each standing over the npcs and locations beside it. Those
# two draw as stars so the distinction survives without spending a fifth hue —
# and it still reads with no colour vision at all.
_KINDS: dict[str, tuple[str, str, str]] = {
    "set": ("Set", "set", "circle"),
    "story": ("Story", "story", "circle"),
    "hero": ("Hero", "character", "star"),
    "npc": ("Character", "character", "circle"),
    "location": ("Location", "place", "circle"),
    "region": ("Region", "place", "star"),
    "monster": ("Monster", "other", "circle"),
    "fauna": ("Fauna", "other", "circle"),
    "flora": ("Flora", "other", "circle"),
    "food": ("Food & Drink", "other", "circle"),
    "weapon": ("Weapon", "other", "circle"),
    "equipment": ("Equipment", "other", "circle"),
}

# The kinds the graph opens on, and the connection count it opens at.
#
# With all twelve kinds on at a minimum of two, the first thing a reader meets
# is 839 nodes under 1,696 edges, and the shape they came for — which stories a
# set gathers, and which heroes and regions run through them — is buried under
# the one-off mentions that make up most of the archive. The rest are one tap
# away in the legend; nothing is removed, only folded away until asked for.
_DEFAULT_ON_KINDS: frozenset[str] = frozenset({"set", "story", "hero", "region"})
_DEFAULT_MIN_DEGREE = 4

_STORY_TYPE_LABELS: dict[str, str] = {
    "main-story": "Main Story",
    "short-stories": "Short Story",
    "summaries": "Summary",
    "world-of-rathe": "World of Rathe",
    "flavour": "Flavour Text",
    "digital-tiles": "Digital Tile",
    "spoilers": "Spoiler",
    "languages": "Language",
    "sets": "Set",
}


def _rows(path: Path) -> list[dict[str, str]]:
    """Return the rows of a pipe CSV, or an empty list when it is absent."""
    if not path.is_file():
        return []
    _, rs = read_pipe_csv(path)
    return rs


def _html_url(story_key: str) -> str:
    """Convert a ``StoryKey`` (``a/b.md``) to the rendered page URL (``a/b.html``)."""
    key = story_key.strip()
    if not key:
        return ""
    return key[:-3] + ".html" if key.endswith(".md") else key


def resolve_hero_url(src_root: Path, canonical_slug: str) -> str:
    """Return the rendered URL of a hero's lore page, or ``""`` when none exists.

    Mirrors ``mdbook_related.resolve_hero_src_path`` so both features agree on
    which heroes have a page: the override table first, then the two naming
    conventions under ``heroes-of-rathe/``.
    """
    slug = canonical_slug.strip()
    if not slug:
        return ""
    override = HERO_SLUG_LORE_FILE_OVERRIDES.get(slug)
    if override and (src_root / Path(override)).is_file():
        return _html_url(Path(override).as_posix())
    hero_dir = src_root / "heroes-of-rathe"
    for fname in (f"{slug}-about.md", f"{slug}.md"):
        if (hero_dir / fname).is_file():
            return _html_url((Path("heroes-of-rathe") / fname).as_posix())
    return ""


def _card_url(src_root: Path, folder: str, slug: str) -> str:
    """Return the URL of a ``weapons/`` or ``equipment/`` page when the file exists."""
    slug = slug.strip()
    if not slug:
        return ""
    rel = Path(folder) / f"{slug}.md"
    return _html_url(rel.as_posix()) if (src_root / rel).is_file() else ""


def arc_slug_for_story(story_key: str) -> str:
    """Return the arc slug a ``StoryKey`` sits under, or ``""``.

    Arc folders sit one level below the section (``main-story/monarch/x.md``),
    except under ``flavour/`` where the arc is the filename stem
    (``flavour/monarch.md``). The caller still has to confirm the slug is a
    known arc — this only says where to look.
    """
    parts = Path(story_key.strip()).as_posix().split("/")
    if len(parts) == 2 and parts[0] == "flavour":
        return parts[1].removesuffix(".md")
    if len(parts) >= 3 and parts[0] in _ARC_FOLDER_SECTIONS:
        return parts[1]
    return ""


def load_sets_by_arc(data_dir: Path) -> dict[str, str]:
    """Return ``{arc slug: set name}`` for arcs that map to a real released set.

    Arcs with a blank ``SetId`` (``non-set-cards``, ``interlude``) are grouping
    folders, not sets, so they get no node. ``DisplayName`` overrides the
    upstream ``SetName`` when it is set, matching the breadcrumbs and hub pages.
    """
    csv_dir = data_dir / "csv"
    set_names: dict[str, str] = {}
    for r in _rows(csv_dir / "sets.csv"):
        sid = (r.get("SetId") or "").strip()
        name = (r.get("SetName") or "").strip()
        if sid and name:
            set_names[sid] = name

    by_arc: dict[str, str] = {}
    for r in _rows(csv_dir / "story-arcs.csv"):
        slug = (r.get("Slug") or "").strip()
        set_id = (r.get("SetId") or "").strip()
        display = (r.get("DisplayName") or "").strip()
        if not slug or set_id not in set_names:
            continue
        by_arc[slug] = display or set_names[set_id]
    return by_arc


# Every card type that records which set it was printed in. Each needs three
# tables: the printings, and the game table that joins a printing's game id back
# to the canonical entity the graph draws.
#
# (printings csv, game id column, game csv, canonical id column)
# The node kinds a printing can attach to. Everything else in the archive is a
# place, a creature or a person, none of which are printed on a card.
_PRINTED_KINDS: frozenset[str] = frozenset({"hero", "weapon", "equipment"})

_PRINTING_SOURCES: tuple[tuple[str, str, str, str], ...] = (
    ("heroes-printings.csv", "HeroGameId", "heroes-game.csv", "CanonicalId"),
    ("weapons-printings.csv", "WeaponGameId", "weapons-game.csv", "CanonicalWeaponId"),
    ("equipment-printings.csv", "EquipmentGameId", "equipment-game.csv", "CanonicalEquipmentId"),
)


def build_printing_edges(data_dir: Path, card_node: dict[str, int], set_node: dict[str, int]) -> list[tuple[int, int]]:
    """Return ``(card index, set index)`` pairs for the sets a card was printed in.

    This is the one relation in the graph that is not an appearance in a story,
    and it is recorded rather than inferred: a printings table gives the set per
    game id, and the matching game table joins that id back to the canonical
    hero, weapon or equipment the graph draws.

    It is deliberately not the same claim as "this appears in a story from that
    set's arc". For heroes only 75 of the two sets' pairs agree — Boltyn is in
    Everfest, Dynasty and Outsiders stories and was printed in none of them.
    Drawing a printing as an ordinary edge would state the second thing while
    meaning the first, which is why ``theme/graph.js`` strokes these dashed and
    keeps them out of the connection counts.

    Args:
        data_dir: ``src/data`` directory holding ``csv/``.
        card_node: ``{canonical id: node index}`` for the heroes, weapons and
            equipment already in the graph. Canonical ids are unique across the
            three by prefix (``CN``, ``CW``, ``CE``), so one map serves all.
        set_node: ``{arc slug: node index}`` for sets already in the graph.

    Returns:
        Sorted unique index pairs. Cards and sets that are not already nodes are
        skipped — printings must decorate the graph, never grow it.
    """
    csv_dir = data_dir / "csv"

    # A set is a node only where an arc maps to it, so this also filters out
    # every set that has no stories on the site.
    slug_for_set: dict[str, str] = {}
    for r in _rows(csv_dir / "story-arcs.csv"):
        sid = (r.get("SetId") or "").strip()
        slug = (r.get("Slug") or "").strip()
        if sid and slug:
            slug_for_set.setdefault(sid, slug)

    edges: set[tuple[int, int]] = set()
    for printings_csv, game_id_col, game_csv, canonical_col in _PRINTING_SOURCES:
        canonical_for_game: dict[str, str] = {}
        for r in _rows(csv_dir / game_csv):
            gid = (r.get(game_id_col) or "").strip()
            cid = (r.get(canonical_col) or "").strip()
            if gid and cid:
                canonical_for_game[gid] = cid

        for r in _rows(csv_dir / printings_csv):
            gid = (r.get(game_id_col) or "").strip()
            set_id = (r.get("SetId") or "").strip()
            card_idx = card_node.get(canonical_for_game.get(gid, ""))
            set_idx = set_node.get(slug_for_set.get(set_id, ""))
            if card_idx is not None and set_idx is not None and card_idx != set_idx:
                edges.add((card_idx, set_idx))
    return sorted(edges)


class _Builder:
    """Accumulates nodes and edges, de-duplicating nodes by registry id."""

    def __init__(self) -> None:
        self.index: dict[str, int] = {}
        self.nodes: list[dict] = []
        self.edges: set[tuple[int, int]] = set()

    def add_node(self, node_id: str, name: str, kind: str, url: str, sub: str = "") -> int:
        existing = self.index.get(node_id)
        if existing is not None:
            return existing
        label, group, _shape = _KINDS[kind]
        idx = len(self.nodes)
        self.index[node_id] = idx
        self.nodes.append(
            {
                "n": name,
                "k": kind,
                "g": group,
                "u": url,
                "s": sub or label,
            }
        )
        return idx

    def add_edge(self, a: int, b: int) -> None:
        if a != b:
            self.edges.add((a, b) if a < b else (b, a))


def _entity_names(path: Path, id_col: str, name_col: str) -> dict[str, str]:
    """Return ``{id: name}`` for a simple registry CSV."""
    out: dict[str, str] = {}
    for r in _rows(path):
        eid = (r.get(id_col) or "").strip()
        name = (r.get(name_col) or "").strip()
        if eid and name:
            out[eid] = name
    return out


def build_graph(data_dir: Path, src_root: Path) -> dict:
    """Build the graph payload from the committed junction CSVs.

    Args:
        data_dir: ``src/data`` directory holding ``csv/``.
        src_root: Book ``src`` directory, used to confirm a link target exists.

    Returns:
        Dict with ``nodes``, ``links`` (index pairs) and ``groups`` (legend rows).
    """
    csv_dir = data_dir / "csv"
    b = _Builder()

    # --- Story nodes -------------------------------------------------------
    story_idx: dict[str, int] = {}
    story_key: dict[str, str] = {}
    for r in _rows(csv_dir / "stories.csv"):
        sid = (r.get("StoryId") or "").strip()
        key = (r.get("StoryKey") or "").strip()
        stype = (r.get("StoryType") or "").strip()
        title = (r.get("Title") or "").strip()
        if not sid or not key or not title or stype in _SKIP_STORY_TYPES:
            continue
        sub = _STORY_TYPE_LABELS.get(stype, "Story")
        story_idx[sid] = b.add_node(sid, title, "story", _html_url(key), sub)
        story_key[sid] = key

    # --- Set nodes ---------------------------------------------------------
    # A set is not a registry entity — it comes from the hand-maintained
    # arc↔set mapping. Joining every story in an arc to one set node turns the
    # release structure into visible clusters. Ids are prefixed so they cannot
    # collide with a registry id.
    sets_by_arc = load_sets_by_arc(data_dir)
    for sid, key in story_key.items():
        slug = arc_slug_for_story(key)
        set_name = sets_by_arc.get(slug)
        if not set_name:
            continue
        set_node = b.add_node(
            "SET" + slug,
            set_name,
            "set",
            f"{_SETS_HUB_URL}#{slug}",
        )
        b.add_edge(story_idx[sid], set_node)

    # --- Registries needed for names and URLs ------------------------------
    regions: dict[str, tuple[str, str]] = {}
    for r in _rows(csv_dir / "regions.csv"):
        rid = (r.get("RegionId") or "").strip()
        name = (r.get("RegionName") or "").strip()
        key = (r.get("WorldOfRatheStoryKey") or "").strip()
        if rid and name:
            regions[rid] = (name, key)

    locations: dict[str, tuple[str, str, str]] = {}
    for r in _rows(csv_dir / "locations.csv"):
        lid = (r.get("LocationId") or "").strip()
        name = (r.get("Name") or "").strip()
        rid = (r.get("RegionId") or "").strip()
        frag = (r.get("LoreFragment") or "").strip().lstrip("#")
        if lid and name:
            locations[lid] = (name, rid, frag)

    npcs: dict[str, tuple[str, str]] = {}
    for r in _rows(csv_dir / "npcs.csv"):
        cid = (r.get("CharacterId") or "").strip()
        name = (r.get("Name") or "").strip()
        key = (r.get("OtherCharactersStoryKey") or "").strip()
        if cid and name:
            npcs[cid] = (name, key)

    heroes: dict[str, tuple[str, str]] = {}
    for r in _rows(csv_dir / "heroes-canonical.csv"):
        cid = (r.get("CanonicalId") or "").strip()
        slug = (r.get("CanonicalSlug") or "").strip()
        name = (r.get("CanonicalHero") or "").strip()
        if cid and slug:
            heroes[cid] = (name or slug, slug)

    weapons = {
        cid: (name, slug)
        for cid, name, slug in (
            (
                (r.get("CanonicalWeaponId") or "").strip(),
                (r.get("CanonicalWeapon") or "").strip(),
                (r.get("CanonicalSlug") or "").strip(),
            )
            for r in _rows(csv_dir / "weapons-canonical.csv")
        )
        if cid and name
    }
    equipment = {
        cid: (name, slug)
        for cid, name, slug in (
            (
                (r.get("CanonicalEquipmentId") or "").strip(),
                (r.get("CanonicalEquipment") or "").strip(),
                (r.get("CanonicalSlug") or "").strip(),
            )
            for r in _rows(csv_dir / "equipment-canonical.csv")
        )
        if cid and name
    }

    monsters = _entity_names(csv_dir / "monsters.csv", "MonsterId", "Name")
    fauna = _entity_names(csv_dir / "fauna.csv", "FaunaId", "Name")
    flora = _entity_names(csv_dir / "flora.csv", "FloraId", "Name")
    food = _entity_names(csv_dir / "food-and-drink.csv", "FoodDrinkId", "Name")

    def _region_url(region_id: str, fragment: str = "") -> str:
        row = regions.get(region_id)
        if not row or not row[1]:
            return ""
        url = _html_url(row[1])
        return f"{url}#{fragment}" if fragment else url

    # --- Junction tables ---------------------------------------------------
    # (csv file, entity id column, kind, resolver -> (name, url) or None)
    def _hero(eid: str):
        row = heroes.get(eid)
        return None if row is None else (row[0], resolve_hero_url(src_root, row[1]))

    def _npc(eid: str):
        row = npcs.get(eid)
        return None if row is None else (row[0], _html_url(row[1]))

    def _location(eid: str):
        row = locations.get(eid)
        return None if row is None else (row[0], _region_url(row[1], row[2]))

    def _region(eid: str):
        row = regions.get(eid)
        return None if row is None else (row[0], _region_url(eid))

    def _weapon(eid: str):
        row = weapons.get(eid)
        return None if row is None else (row[0], _card_url(src_root, "weapons", row[1]))

    def _equipment(eid: str):
        row = equipment.get(eid)
        return None if row is None else (row[0], _card_url(src_root, "equipment", row[1]))

    def _plain(table: dict[str, str]):
        def resolve(eid: str):
            name = table.get(eid)
            return None if name is None else (name, "")

        return resolve

    junctions = (
        ("story-heroes.csv", "CanonicalId", "hero", _hero),
        ("story-npcs.csv", "CharacterId", "npc", _npc),
        ("story-locations.csv", "LocationId", "location", _location),
        ("story-regions.csv", "RegionId", "region", _region),
        ("story-weapons.csv", "CanonicalWeaponId", "weapon", _weapon),
        ("story-equipment.csv", "CanonicalEquipmentId", "equipment", _equipment),
        ("story-monsters.csv", "MonsterId", "monster", _plain(monsters)),
        ("story-fauna.csv", "FaunaId", "fauna", _plain(fauna)),
        ("story-flora.csv", "FloraId", "flora", _plain(flora)),
        ("story-food-drink.csv", "FoodDrinkId", "food", _plain(food)),
    )

    for filename, id_col, kind, resolve in junctions:
        for r in _rows(csv_dir / filename):
            sid = (r.get("StoryId") or "").strip()
            eid = (r.get(id_col) or "").strip()
            if not sid or not eid or sid not in story_idx:
                continue
            resolved = resolve(eid)
            if resolved is None:
                continue
            name, url = resolved
            b.add_edge(story_idx[sid], b.add_node(eid, name, kind, url))

    # Stories that ended up with no edge are dots with nothing to say.
    linked: set[int] = set()
    for a, c in b.edges:
        linked.add(a)
        linked.add(c)

    keep = sorted(linked)
    remap = {old: new for new, old in enumerate(keep)}
    nodes = [b.nodes[i] for i in keep]
    links = sorted((remap[a], remap[c]) for a, c in b.edges)

    # Printings decorate the graph and never grow it, so they are resolved
    # against the surviving nodes only: a hero no story mentions has no node,
    # and so gets no edge to the set that printed it.
    card_node: dict[str, int] = {}
    set_node: dict[str, int] = {}
    for node_id, old in b.index.items():
        new = remap.get(old)
        if new is None:
            continue
        node_kind = nodes[new]["k"]
        if node_kind in _PRINTED_KINDS:
            card_node[node_id] = new
        elif node_kind == "set" and node_id.startswith("SET"):
            set_node[node_id[len("SET") :]] = new
    prints = build_printing_edges(data_dir, card_node, set_node)

    assign_slugs(nodes)

    counts: dict[str, int] = {}
    for n in nodes:
        counts[n["k"]] = counts.get(n["k"], 0) + 1

    groups = []
    for kind, (label, group, shape) in _KINDS.items():
        if counts.get(kind):
            groups.append(
                {
                    "k": kind,
                    "l": label,
                    "g": group,
                    "s": shape,
                    "c": counts[kind],
                    # Whether the legend chip starts pressed. The opening view
                    # is decided here rather than in the script so the kind
                    # table stays the one place a kind is described.
                    "o": 1 if kind in _DEFAULT_ON_KINDS else 0,
                }
            )

    # Canonical order for the inspector panel's sections. The panel groups a
    # node's connections by their `sub` label, and `sub` is finer than `kind`:
    # every story carries its own type. Sets lead, then the story types in
    # reading order, then the entity kinds.
    present_subs = {n["s"] for n in nodes}
    sub_order: list[str] = []
    for kind, (label, _group, _shape) in _KINDS.items():
        candidates = _STORY_TYPE_LABELS.values() if kind == "story" else [label]
        for candidate in candidates:
            if candidate in present_subs and candidate not in sub_order:
                sub_order.append(candidate)

    return {
        "nodes": nodes,
        "links": links,
        # Kept apart from `links`, not flagged inside it: these are a different
        # relation and the script strokes and counts them differently.
        "prints": prints,
        "groups": groups,
        "subs": sub_order,
    }


def assign_slugs(nodes: list[dict]) -> None:
    """Give every node a stable, human-readable ``sl`` key for deep links.

    ``graph.html#dorinthea`` beats ``graph.html#CNb6ce517916``, so the bare name
    slug is used wherever it is unique. Names that repeat — a set, its flavour
    page and its digital tiles are all "Bright Lights" — take a type suffix, and
    a repeat within one type (which the data does not currently contain) takes a
    numeric one. Assignment walks the nodes in a fixed order so the same data
    always produces the same slugs and a shared link keeps working.

    Mutates ``nodes`` in place.
    """
    counts: dict[str, int] = {}
    for n in nodes:
        key = slugify_card_name_stem(n["n"])
        counts[key] = counts.get(key, 0) + 1

    used: set[str] = set()
    for n in sorted(nodes, key=lambda x: (x["s"], x["n"])):
        base = slugify_card_name_stem(n["n"])
        slug = base if counts[base] == 1 else f"{base}-{slugify_card_name_stem(n['s'])}"
        if slug in used:
            suffix = 2
            while f"{slug}-{suffix}" in used:
                suffix += 1
            slug = f"{slug}-{suffix}"
        used.add(slug)
        n["sl"] = slug


def page_graph_targets(graph: dict) -> dict[str, dict]:
    """Map each ``src`` markdown path to the node a "view in the graph" link means.

    Several nodes can share one page: ``world-of-rathe/aria.md`` is the Region
    "Aria", the World of Rathe story of the same name, and the landing page of
    every location deep-linked into it. Locations are excluded here — their URLs
    carry a ``#fragment``, and a link that lands on the region would misname
    itself. Among what is left the busiest node wins, with a non-story preferred
    on a tie, because the entity is the subject of the page and the story is the
    page itself.

    Args:
        graph: Payload from :func:`build_graph`.

    Returns:
        ``{src markdown path: node}``. Nodes are the dicts from ``graph``.
    """
    degree: dict[int, int] = {}
    for a, b in graph["links"]:
        degree[a] = degree.get(a, 0) + 1
        degree[b] = degree.get(b, 0) + 1

    best: dict[str, tuple[tuple, dict]] = {}
    for i, node in enumerate(graph["nodes"]):
        url = node.get("u") or ""
        if not url or "#" in url:
            continue
        md_path = url[:-5] + ".md" if url.endswith(".html") else url
        # Sort key: busiest first, entity before story, then name for stability.
        rank = (-degree.get(i, 0), node["k"] == "story", node["n"])
        current = best.get(md_path)
        if current is None or rank < current[0]:
            best[md_path] = (rank, node)

    return {path: node for path, (_rank, node) in best.items()}


def build_graph_html(graph: dict) -> str:
    """Return the inline payload plus the DOM shell ``theme/graph.js`` drives."""
    data_json = json.dumps(graph, ensure_ascii=False, separators=(",", ":"))
    return (
        f"<script>window.FABLORE_GRAPH={data_json};</script>\n"
        # The container must not be `id="lore-graph"`: mdBook derives heading ids
        # from the title, so the page's own `# Lore Graph` already owns that id
        # and `getElementById` would hand the script the <h1>.
        '<div id="lore-graph-app" class="lore-graph">\n'
        # The search sits on its own row. Sharing a row with the sliders made it
        # crowd the "Minimum connections" label once the window narrowed.
        '  <div class="lore-graph-search">\n'
        '    <input type="text" id="lore-graph-input" class="lore-graph-input"'
        ' placeholder="Find a story or character…" autocomplete="off"'
        ' aria-label="Find a node in the graph" />\n'
        '    <ul class="lore-graph-dropdown" id="lore-graph-dropdown" hidden></ul>\n'
        "  </div>\n"
        '  <div class="lore-graph-controls">\n'
        '    <label class="lore-graph-degree">\n'
        "      <span>Minimum connections</span>\n"
        # The script reads its opening filter off this value rather than
        # carrying its own copy, so the control cannot disagree with the view.
        f'      <input type="range" id="lore-graph-degree" min="1" max="6" value="{_DEFAULT_MIN_DEGREE}"'
        ' aria-describedby="lore-graph-degree-value" />\n'
        f'      <output id="lore-graph-degree-value">{_DEFAULT_MIN_DEGREE}</output>\n'
        "    </label>\n"
        # Classed so the stylesheet can drop it in list mode without a :has().
        '    <label class="lore-graph-degree lore-graph-spread">\n'
        "      <span>Spread</span>\n"
        '      <input type="range" id="lore-graph-spread" min="60" max="600" step="20"'
        ' value="240" aria-label="How far apart the graph spreads" />\n'
        "    </label>\n"
        '    <button type="button" id="lore-graph-reset" class="lore-graph-reset">Reset view</button>\n'
        "  </div>\n"
        '  <div class="lore-graph-legend" id="lore-graph-legend" role="group"'
        ' aria-label="Filter the graph by node type"></div>\n'
        '  <div class="lore-graph-stage" id="lore-graph-stage">\n'
        '    <canvas id="lore-graph-canvas" class="lore-graph-canvas"'
        ' aria-label="Force-directed graph of lore connections" role="img"></canvas>\n'
        '    <div class="lore-graph-panel" id="lore-graph-panel" hidden></div>\n'
        # A blank canvas with no words on it reads as broken rather than as
        # filtered, and switching Story off empties it completely.
        '    <p class="lore-graph-empty" id="lore-graph-empty" hidden></p>\n'
        "  </div>\n"
        # Narrow-viewport stand-in for the canvas, filled by theme/graph.js. A
        # force layout needs area the phone does not have: at 390px the stage
        # holds 417 nodes at ~420px² each, and the marks land near 19px against
        # Apple's 44px minimum tap target. The list carries the same ranking and
        # the same connection view without asking for the area.
        '  <div class="lore-graph-list" id="lore-graph-list" hidden></div>\n'
        # Outside the stage on purpose: the stage is hidden in list mode, and a
        # hidden ancestor takes the live region down with it.
        '  <p class="lore-graph-status" id="lore-graph-status" role="status"></p>\n'
        '  <p class="lore-graph-hint lore-graph-hint-graph">Hover a node to see its '
        "connections. Click to open its page. Drag to pan, scroll to zoom. "
        "In the panel, a name opens its page and the target button beside it "
        "moves the graph to that connection. "
        # The dashed stroke is the only mark on the graph whose meaning cannot
        # be read off the legend, because it is an edge rather than a node.
        "A solid line means an appearance in a story; a dashed one joins a hero, "
        "weapon or piece of equipment to a set its card was printed in, which is "
        "not the same thing.</p>\n"
        '  <p class="lore-graph-hint lore-graph-hint-list">Tap an entry to read its '
        "connections, most connected first. The number beside a name is how many "
        "connections it has.</p>\n"
        "</div>"
    )


def inject_into_content(content: str, inner_html: str) -> str:
    """Replace the marker block in ``content``, or append one when absent."""
    if MARK_START in content and MARK_END in content:
        pre, _, rest = content.partition(MARK_START)
        _, _, post = rest.partition(MARK_END)
        block = f"{MARK_START}\n{inner_html}\n{MARK_END}"
        return pre.rstrip() + "\n\n" + block + post
    sep = "\n\n" if content.strip() else ""
    return content.rstrip() + sep + f"{MARK_START}\n{inner_html}\n{MARK_END}\n"


def walk_and_process(sections: list, graph: dict) -> None:
    """Inject the graph shell into the ``graph.md`` chapter, recursing sub-items."""
    for item in sections:
        if not isinstance(item, dict):
            continue
        if "Chapter" in item:
            ch = item["Chapter"]
            if (ch.get("path") or "").strip() == _GRAPH_SRC_PATH:
                ch["content"] = inject_into_content(
                    ch.get("content") or "",
                    build_graph_html(graph),
                )
            walk_and_process(ch.get("sub_items") or [], graph)


def main() -> None:
    if len(sys.argv) >= 3 and sys.argv[1] == "supports":
        sys.exit(0)

    ctx, book = json.load(sys.stdin)
    root = Path(ctx["root"])
    book_cfg = (ctx.get("config") or {}).get("book") or {}
    src_rel = (book_cfg.get("src") or "src").strip() or "src"
    src_root = (root / src_rel).resolve()

    graph = build_graph(src_root / "data", src_root)
    walk_and_process(book.get("items") or [], graph)

    json.dump(book, sys.stdout, ensure_ascii=False)


if __name__ == "__main__":
    main()
