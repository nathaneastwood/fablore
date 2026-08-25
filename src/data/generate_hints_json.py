"""Generate src/hints.json from the database and src/hints_supplement.json.

DB-backed entries (locations, characters, monsters, fauna, flora, groups, kind)
are written first, in that order.
The supplement is then merged on top: supplement fields override DB fields for
matching keys, and supplement-only keys are appended.

Run from the repository root:
    python src/data/generate_hints_json.py
"""

import json
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DB_PATH = ROOT / "src" / "data" / "fablore.db"
SUPPLEMENT_PATH = ROOT / "src" / "hints_supplement.json"
OUTPUT_PATH = ROOT / "src" / "hints.json"


def _region_map(conn: sqlite3.Connection) -> dict[str, str]:
    return {row[0]: row[1] for row in conn.execute("SELECT region_id, region_name FROM regions")}


def _lore_url(story_key: str, fragment: str) -> str:
    """Turn a story key plus a heading fragment into a rendered page URL.

    ``"world-of-rathe/solana.md"`` + ``"the-hand-of-sol"`` becomes
    ``"/world-of-rathe/solana.html#the-hand-of-sol"``. Matches the shape the
    supplement already used by hand for the entries this replaces.
    """
    key = (story_key or "").strip()
    if not key:
        return ""
    path = key[:-3] + ".html" if key.endswith(".md") else key
    frag = (fragment or "").strip().lstrip("#")
    url = f"/{path.lstrip('/')}"
    return f"{url}#{frag}" if frag else url


# Emission order is the tie-break, and it is deliberate: locations are written
# before characters, characters before the categories, and groups before kind,
# so where two entries have equally long match strings a place beats a person, a
# person beats a kind of thing, and a kind loses to everything. The preprocessor sorts candidates by longest match string and Python's sort
# is stable, so the order this file writes them in survives all the way to the
# page. `The Registry` (a place) and `Registry` (a firm) are the live example.
# tests/test_generate_hints_json_full.py locks the order so a reshuffle here cannot
# silently flip a winner.
_LEADING_ARTICLES = ("the ", "a ", "an ")


def _warn_match_collisions(hints: dict) -> list[str]:
    """Report entries that compete for the same prose, and say so on every run.

    Two shapes are worth a warning and no others:

    * **Exact** — two entries look for the identical string. The loser can never
      win a single page, so one of the two tooltips is dead data.
    * **Article** — one entry's string is another's with ``the``/``a``/``an`` in
      front. Longest-first hands the articled form every mention that carries the
      article, which is how ``Registry`` lost "the Registry" to a location row.

    An entry that shadows *itself* is not a clash. ``The Dhani Empire`` carries the
    alias ``Dhani Empire`` precisely so both forms reach the same tooltip, and
    whichever wins is the same entry — so the warning fires only where some other
    key owns the bare form.

    Plain substring overlap is *not* warned about: ``Sol`` inside ``Solarium`` is
    exactly what longest-first exists to resolve, and warning on it would bury the
    two shapes above in noise.

    Returns:
        Warning lines, also written to stderr.
    """
    owners: dict[str, list[str]] = {}
    for key, entry in hints.items():
        for text in _match_strings(key, entry):
            owners.setdefault(text.strip().lower(), []).append(key)

    warnings: list[str] = []
    for text, keys in sorted(owners.items()):
        if len(keys) > 1:
            warnings.append(f"hint clash: {text!r} is claimed by {sorted(keys)} — only the first can ever match")
    for text, keys in sorted(owners.items()):
        for article in _LEADING_ARTICLES:
            if not (text.startswith(article) and text[len(article) :] in owners):
                continue
            bare = text[len(article) :]
            shadowed = sorted(set(owners[bare]) - set(keys))
            if not shadowed:
                continue
            warnings.append(
                f"hint clash: {text!r} ({sorted(keys)}) shadows {bare!r} "
                f"({shadowed}) — the articled form wins every mention that carries it"
            )
    for line in warnings:
        print(line, file=sys.stderr)
    return warnings


def _match_strings(key: str, entry) -> list[str]:
    """The strings this entry looks for — its ``match`` list, or its key."""
    if isinstance(entry, dict):
        match = entry.get("match")
        if match is not None:
            return [match] if isinstance(match, str) else list(match)
    return [key]


def _alias_map(conn: sqlite3.Connection, table: str, owner_col: str, name_col: str) -> dict[str, list[str]]:
    """Return ``{owner_id: [alias, ...]}`` in declared order for one alias table."""
    out: dict[str, list[str]] = {}
    sql = f"SELECT {owner_col}, {name_col} FROM {table} ORDER BY {owner_col}, sort_order, {name_col}"
    for owner, alias in conn.execute(sql):
        out.setdefault(owner, []).append(alias)
    return out


def _add(hints: dict, key: str, entry: dict, source: str, taken: dict) -> None:
    """Store ``entry`` under ``key``, keeping whichever was emitted first.

    Emission order is the tie-break, and plain ``hints[key] = entry`` inverts it:
    two registries whose rows share a name produce the *same* key, and assignment
    hands it to whoever writes last. ``Rosetta`` is both a group and a kind and
    is the live pair, so first-wins is enforced here rather than relied on.

    The loser is reported, because a row that reaches no tooltip is worth knowing
    about even when — as with Rosetta — both rows carry the same sentence and the
    reader cannot tell. Fields the winner does not have are carried over from it,
    so a tie costs a row its tooltip but never costs the page a link.
    """
    if key in hints:
        # Fields the winner has no way to produce are carried over rather than
        # dropped. `The Foundry` is a location and the organisation inside it; only
        # the group knows a `url`, and losing the tie should not lose the link.
        missing = {f: v for f, v in entry.items() if f not in hints[key]}
        if missing:
            hints[key].update(missing)
        print(
            f"hint clash: {key!r} is emitted by {taken[key]} and by {source} — "
            f"{taken[key]} wins"
            + (
                f", carrying over {sorted(missing)} from the {source} row"
                if missing
                else f"; the {source} row adds nothing"
            ),
            file=sys.stderr,
        )
        return
    hints[key] = entry
    taken[key] = source


def _key(name: str) -> str:
    """Derive a safe hint key from a DB name: strip apostrophes."""
    return name.replace("'", "")


CURLY_APOSTROPHE = "\u2019"


def _apostrophe_variants(name: str) -> list[str]:
    """Return the name written with each apostrophe glyph the prose actually uses.

    The pages are typeset copy, so ``Kraken's Barrel`` appears as often with a
    curly ``\u2019`` as with a straight ``'``, and the matcher compares literal text.
    Emitting both is mechanical, which is the point: 14 supplement entries existed
    for no other reason than to hand-write the curly form of a name the DB already
    held, and a fifteenth was one apostrophe name away from being needed.
    """
    if "'" not in name:
        return [name]
    return [name, name.replace("'", CURLY_APOSTROPHE)]


def _entry_with_match(name: str, base: dict, alt_names: "list[str] | None" = None) -> dict:
    """Add a 'match' field when the key alone cannot find the entity in prose.

    Two reasons it cannot. The key strips apostrophes, so an apostrophe name needs
    an explicit match — and once one is needed, every apostrophe glyph variant
    belongs in it. And an entity may answer to names that are not its display name
    at all (R4, R6): ``Mendacity`` for ``Mendacity Media``, ``Isen's Peak`` for
    ``Mt. Isen``. Those come from the alias tables and are match strings too, which
    is the whole point of storing them — the canonical row keeps the display name
    while every other name still resolves to it.

    Args:
        name: The entity's canonical display name.
        base: The entry fields to carry through.
        alt_names: Aliases or epithets, in declared order. Each contributes its own
            apostrophe variants.
    """
    variants = list(_apostrophe_variants(name))
    for alt in alt_names or []:
        for variant in _apostrophe_variants(alt):
            if variant not in variants:
                variants.append(variant)
    if len(variants) == 1 and _key(name) == name:
        return base
    return {"match": variants[0] if len(variants) == 1 else variants, **base}


def _merge_entry(db_entry: dict, sup_entry: dict) -> dict:
    """Merge a supplement entry over a DB entry, recording the DB's own type.

    A supplement entry often retypes a DB-backed entity so the tooltip reads
    correctly — the Hand of Sol and the Light of Sol are stored as ``locations``
    rows so stories can link them, but they are really orders, and are labelled
    ``faction``. Solana is a location row labelled ``region``.

    The hints preprocessor decides auto-detection eligibility from ``type``, so
    such a relabel silently disqualifies an entity that genuinely is DB-backed —
    Solana lost its tooltips this way. Keep the DB's type under ``db_type`` so
    display and eligibility can differ: the supplement still controls the label,
    while detection follows where the entity actually came from.

    Args:
        db_entry: The DB-generated hint entry.
        sup_entry: The supplement entry overriding it.

    Returns:
        The merged entry, with ``db_type`` set when the supplement relabels it.
    """
    merged = {**db_entry, **sup_entry}
    db_type = db_entry.get("type")
    if db_type and sup_entry.get("type") and sup_entry["type"] != db_type:
        merged["db_type"] = db_type
    return merged


def merge_supplement(hints: dict, supplement: dict) -> dict:
    """Merge supplement entries into DB-generated hints.

    Three cases:
    - Exact key match: supplement fields override DB fields.
    - Match-based merge: supplement key differs from DB key but its "match"
      field resolves (via _key()) to a DB key — the DB entry is replaced by
      the camelCase supplement key with fields merged.
    - No match: supplement entry is appended as-is.
    """
    match_to_db_key: dict[str, str] = {}
    for sup_key, value in supplement.items():
        if isinstance(value, dict):
            match = value.get("match")
            if match:
                db_key = _key(match) if isinstance(match, str) else _key(match[0])
                if db_key in hints:
                    match_to_db_key[sup_key] = db_key

    result = dict(hints)
    for key, value in supplement.items():
        if key in result and isinstance(value, dict) and isinstance(result[key], dict):
            result[key] = _merge_entry(result[key], value)
        elif key in match_to_db_key and isinstance(value, dict):
            db_key = match_to_db_key[key]
            merged = _merge_entry(result[db_key], value)
            del result[db_key]
            result[key] = merged
        else:
            result[key] = value
    return result


def generate() -> None:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    hints: dict = {}
    taken: dict[str, str] = {}
    regions = _region_map(conn)

    location_aliases = _alias_map(conn, "location_aliases", "location_id", "alias")
    group_aliases = _alias_map(conn, "group_aliases", "group_id", "alias")

    for row in conn.execute("SELECT location_id, name, notes, region_id FROM locations ORDER BY name"):
        if not row["notes"]:
            continue
        entry: dict = {"type": "location", "summary": row["notes"]}
        region = regions.get(row["region_id"], "")
        if region:
            entry["region"] = region
        _add(
            hints,
            _key(row["name"]),
            _entry_with_match(row["name"], entry, location_aliases.get(row["location_id"], [])),
            "location",
            taken,
        )

    # Characters, second — after locations, ahead of every category.
    #
    # A person is a named individual, so it outranks a kind of thing: if a page
    # writes "Bellona", it means the Herald, not a class of them. Locations keep
    # their existing precedence, so nothing already emitted changes rank.
    #
    # Measured before choosing, 2026-08-22: all 411 character names and all 43
    # epithet and short-name strings are distinct from every location, monster,
    # fauna, flora, group and kind name. So this position is unobservable
    # today and was picked on principle rather than to dodge a live collision.
    # `_warn_match_collisions` reports the first one that appears.
    #
    # `type` is derived, never hand-classified (the user's call, 2026-08-22): a
    # character linked to a hero emits "hero", one without emits "npc". The
    # value goes straight onto the badge through theme/hints.js, and deriving it
    # means resolving an identity pair later moves the badge with no edit here.
    character_epithets = _alias_map(conn, "character_epithets", "character_id", "name")
    character_kinds: dict[str, list[str]] = {}
    for cid, kind_name in conn.execute(
        """
        SELECT ns.character_id, s.name
        FROM character_kinds ns JOIN kinds s ON s.kind_id = ns.kind_id
        ORDER BY ns.character_id, ns.sort_order, s.name
        """
    ):
        character_kinds.setdefault(cid, []).append(kind_name)

    character_sql = """
        SELECT c.character_id, c.name, c.status, c.summary,
               ch.canonical_id AS hero_canonical_id
        FROM characters c
        LEFT JOIN character_heroes ch ON ch.character_id = c.character_id
        ORDER BY c.name
    """
    for row in conn.execute(character_sql):
        if not row["summary"]:
            continue
        entry = {
            "type": "hero" if row["hero_canonical_id"] else "npc",
            "summary": row["summary"],
        }
        # theme/hints.js has read entry.kind for the badge since stage 4 and
        # no entry has ever carried it. Two kinds are joined rather than
        # ranked — Scooba is a Zombie and a Dog, and neither is the lesser half.
        kind_names = character_kinds.get(row["character_id"], [])
        if kind_names:
            entry["kind"] = ", ".join(kind_names)
        # hints.js skips "Unknown", so emitting it costs nothing and a real
        # status reaches the badge.
        if row["status"]:
            entry["status"] = row["status"]
        _add(
            hints,
            _key(row["name"]),
            _entry_with_match(row["name"], entry, character_epithets.get(row["character_id"], [])),
            "character",
            taken,
        )

    for row in conn.execute("SELECT name, description FROM monsters ORDER BY name"):
        if not row["description"]:
            continue
        _add(
            hints,
            _key(row["name"]),
            _entry_with_match(row["name"], {"type": "monster", "summary": row["description"]}),
            "monster",
            taken,
        )

    for row in conn.execute("SELECT name, description FROM fauna ORDER BY name"):
        if not row["description"]:
            continue
        _add(
            hints,
            _key(row["name"]),
            _entry_with_match(row["name"], {"type": "fauna", "summary": row["description"]}),
            "fauna",
            taken,
        )

    for row in conn.execute("SELECT name, description FROM flora ORDER BY name"):
        if not row["description"]:
            continue
        _add(
            hints,
            _key(row["name"]),
            _entry_with_match(row["name"], {"type": "flora", "summary": row["description"]}),
            "flora",
            taken,
        )

    # Groups. `kind` is the displayed type when it is set ("clan", "guild",
    # "order"), which reads better than a flat "group" label and matches what
    # hints_supplement.json has been doing by hand with `faction` /
    # `organisation`. Rows with empty notes are skipped like every other
    # registry above, so a group with no summary yet renders nothing rather
    # than an empty tooltip — and until the supplement summaries move into
    # descriptions.py, that is most of them.
    # A group's region is *derived*, never stored: groups move about, so most carry
    # no region at all, but one tied to a place (Ikaru Clan, Teklo Industries, the
    # Maela) borrows the region of that place for the badge.
    #
    # The url comes from lore_story_key + lore_fragment, which the group carries
    # itself. A location walks region_id -> world_of_rathe_story_key to reach its
    # page; a group has no region to walk.
    group_sql = """
        SELECT g.group_id, g.name, g.kind, g.notes, g.lore_story_key, g.lore_fragment,
               l.region_id AS loc_region_id
        FROM groups g
        LEFT JOIN locations l ON l.location_id = g.location_id
        ORDER BY g.name
    """
    for row in conn.execute(group_sql):
        if not row["notes"]:
            continue
        entry = {"type": row["kind"] or "group", "summary": row["notes"]}
        region = regions.get(row["loc_region_id"] or "", "")
        if region:
            entry["region"] = region
        url = _lore_url(row["lore_story_key"], row["lore_fragment"])
        if url:
            entry["url"] = url
        _add(
            hints,
            _key(row["name"]),
            _entry_with_match(row["name"], entry, group_aliases.get(row["group_id"], [])),
            "group",
            taken,
        )

    # Kind last. A location or a group takes any tie against one — `Rosetta`
    # the order beats `Rosetta` the people, which is why the two rows are kept
    # word-for-word identical rather than ranked.
    kind_aliases = _alias_map(conn, "kind_aliases", "kind_id", "alias")
    for row in conn.execute("SELECT kind_id, name, notes FROM kinds ORDER BY name"):
        if not row["notes"]:
            continue
        entry = {"type": "kind", "summary": row["notes"]}
        _add(
            hints,
            _key(row["name"]),
            _entry_with_match(row["name"], entry, kind_aliases.get(row["kind_id"], [])),
            "kind",
            taken,
        )

    conn.close()

    supplement: dict = {}
    if SUPPLEMENT_PATH.exists():
        with SUPPLEMENT_PATH.open(encoding="utf-8") as f:
            supplement = json.load(f)

    hints = merge_supplement(hints, supplement)
    _warn_match_collisions(hints)

    with OUTPUT_PATH.open("w", encoding="utf-8") as f:
        json.dump(hints, f, ensure_ascii=False, indent=2)
        f.write("\n")

    print(
        f"Wrote {len(hints)} entries to {OUTPUT_PATH.relative_to(ROOT)}",
        file=sys.stderr,
    )


if __name__ == "__main__":
    generate()
