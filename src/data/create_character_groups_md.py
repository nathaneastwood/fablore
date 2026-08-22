"""Generate ``src/data/md/character-groups.md`` from the database.

Unlike every other file under ``src/data/md/``, this page has no CSV source —
it is a join across ``groups``, ``group_npcs``, ``characters``, ``npc_epithets``,
``npc_species``, ``species`` and ``titles``/``title_holders``, with parent
nesting that recurses (``groups.parent_group_id``). ``create_md.py`` renders one
flat CSV per table; this page cannot be that shape, so it gets its own
generator that reads ``fablore.db`` directly.

Sections with nothing behind them in the database (currently ``Dracai`` and
``Grand Magisters`` — ``titles``/``title_holders`` are empty, pending data
entry) are omitted entirely rather than rendered empty or hand-filled; they
reappear on their own the moment rows exist, with no code change here.

**This generator is not yet the source of the live page** (the user's call,
2026-08-22). ``src/data/md/character-groups.md`` is still hand-maintained, is
live in ``SUMMARY.md``, and is deliberately *not* wired into ``create_md.py``,
``scripts/ensure-create-md-sync.sh`` or the ``ensure-create-md-sync`` hook —
because what this renders today would be a net loss to a reader. Five pieces of
data entry stand between it and the swap:

- **``Infernai``** is stored as ``Aesir of Flames`` — his epithet standing in for
  his name — so the Aesir section renders that name against a blank epithet cell.
- **Nine comma-tails are still glued into ``characters.name``**: the eight
  Heralds (``Aegis, the Shield of Light``) and ``Raven, Aesir of Chaos``. Their
  ``npc_epithets`` rows already exist, so each renders its epithet twice — once
  inside the name and once in the Epithets column.
- **``titles`` is empty**, so ``Dracai`` and ``Grand Magisters`` do not render.
- **``Anarchs of L'Apocalypta`` has no data path.** Zeir's species is ``Human``,
  not ``Aesir``, and the ``L'Apocalypta`` group carries no ``parent_group_id``
  tying it to anything. Reproducing that section needs a lore decision, not code.
- **Dragons cannot be split by sex.** No registry table has such a column, so the
  hand page's Male/Female tables become one list.

When those land, the swap is small: give ``main`` back a default of
:data:`OUTPUT_MD`, call it from ``create_md.py``'s ``main()``, and add
``character-groups.md`` to ``MD_FILES`` in ``scripts/ensure-create-md-sync.sh``
and to the ``ensure-create-md-sync`` trigger regex in ``.pre-commit-config.yaml``
— all four, or the page drifts exactly as the hand-written one did.

``output_md`` is deliberately **required** until then. It defaulted to the live
page while this was being written and a stray call overwrote it; nothing that
cannot name its destination should be able to.

Run from the repository root, naming where the output goes::

    python3 src/data/create_character_groups_md.py /tmp/preview.md
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "src/data"
DB_PATH = DATA / "fablore.db"
OUTPUT_MD = DATA / "md" / "character-groups.md"

_BANNER = "<!-- ### NOTE: This file should not be edited by hand. " "Please edit create_character_groups_md.py. -->\n"

# The Dragons section drops the Pronounciation/Phonetic (sic) columns the
# hand-written page carried — no registry table has anywhere to put them — and
# links this page instead, where the identical table (typo included) is live
# and was verified cell-for-cell.
_DRAGON_PRONUNCIATION_PAGE = "../../archive/world-of-rathe/volcor/welcome-to-volcor.md"


def _md_table(headers: list[str], rows: list[list[str]]) -> str:
    """Render a minimal GFM pipe table — no external padding library."""
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"]
    for row in rows:
        lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines)


def _epithets_for(conn: sqlite3.Connection, character_id: str) -> str:
    """Comma-join a character's alternate names in declared (sort_order) order."""
    rows = conn.execute(
        "SELECT name FROM npc_epithets WHERE character_id = ? ORDER BY sort_order, name",
        (character_id,),
    ).fetchall()
    return ", ".join(r["name"] for r in rows)


def _species_members(conn: sqlite3.Connection, species_name: str) -> list[sqlite3.Row]:
    """Characters carrying ``species_name``, sorted by name for determinism."""
    return conn.execute(
        """
        SELECT c.character_id, c.name
        FROM npc_species ns
        JOIN species s ON s.species_id = ns.species_id
        JOIN characters c ON c.character_id = ns.character_id
        WHERE s.name = ?
        ORDER BY c.name
        """,
        (species_name,),
    ).fetchall()


def _section_species(conn: sqlite3.Connection, heading: str, species_name: str) -> str:
    members = _species_members(conn, species_name)
    if not members:
        return ""
    rows = [[m["name"], _epithets_for(conn, m["character_id"])] for m in members]
    table = _md_table(["Name", "Epithets"], rows)
    return f"## {heading}\n\n{table}\n"


def _section_dragons(conn: sqlite3.Connection) -> str:
    members = _species_members(conn, "Dragon")
    if not members:
        return ""
    table = _md_table(["Name"], [[m["name"]] for m in members])
    note = (
        "Pronunciation and phonetic spellings for these names are recorded on "
        f"[Welcome to Volcor]({_DRAGON_PRONUNCIATION_PAGE})."
    )
    return f"## Dragons\n\n{table}\n\n{note}\n"


# ---------------------------------------------------------------------------
# Titles — deferred data. Empty tables today; both sections vanish until
# `titles`/`title_holders` are populated, with no further code change.
# ---------------------------------------------------------------------------


def _group_by_name(conn: sqlite3.Connection, name: str) -> sqlite3.Row | None:
    return conn.execute("SELECT * FROM groups WHERE name = ?", (name,)).fetchone()


def _title_holders_display(conn: sqlite3.Connection, title_id: str) -> list[tuple[int, str]]:
    rows = conn.execute(
        """
        SELECT th.ordinal, c.name
        FROM title_holders th
        JOIN characters c ON c.character_id = th.character_id
        WHERE th.title_id = ?
        ORDER BY th.ordinal, c.name
        """,
        (title_id,),
    ).fetchall()
    return [(r["ordinal"], r["name"]) for r in rows]


def _section_dracai(conn: sqlite3.Connection) -> str:
    dracai_group = _group_by_name(conn, "Dracai")
    if dracai_group is None:
        return ""
    titles = conn.execute(
        "SELECT title_id, name FROM titles WHERE group_id = ? ORDER BY name",
        (dracai_group["group_id"],),
    ).fetchall()
    rows = []
    for t in titles:
        holders = _title_holders_display(conn, t["title_id"])
        rows.append([t["name"], ", ".join(name for _ordinal, name in holders)])
    if not rows:
        return ""
    table = _md_table(["Name", "Character"], rows)
    return f"## Dracai\n\n{table}\n"


def _section_grand_magisters(conn: sqlite3.Connection) -> str:
    title = conn.execute("SELECT title_id FROM titles WHERE name = ?", ("Grand Magister",)).fetchone()
    if title is None:
        return ""
    holders = _title_holders_display(conn, title["title_id"])
    if not holders:
        return ""
    rows = [[str(ordinal), name] for ordinal, name in holders]
    table = _md_table(["Position", "Name"], rows)
    return f"## Grand Magisters\n\n{table}\n"


# ---------------------------------------------------------------------------
# Deities / Gods — a group that nests one level (Deities -> Dhani Deities),
# walked generically with a cycle guard per the same rule parent_group_id
# carries everywhere else in the schema.
# ---------------------------------------------------------------------------


def _child_groups(conn: sqlite3.Connection, group_id: str) -> list[sqlite3.Row]:
    return conn.execute(
        "SELECT * FROM groups WHERE parent_group_id = ? ORDER BY name",
        (group_id,),
    ).fetchall()


def _group_person_rows(conn: sqlite3.Connection, group_id: str) -> list[list[str]]:
    rows = conn.execute(
        """
        SELECT c.character_id, c.name
        FROM group_npcs gn
        JOIN characters c ON c.character_id = gn.character_id
        WHERE gn.group_id = ?
        ORDER BY c.name
        """,
        (group_id,),
    ).fetchall()
    return [[r["name"], _epithets_for(conn, r["character_id"])] for r in rows]


def _section_gods(conn: sqlite3.Connection) -> str:
    deities = _group_by_name(conn, "Deities")
    if deities is None:
        return ""

    blocks: list[str] = []
    seen: set[str] = {deities["group_id"]}
    for pantheon in _child_groups(conn, deities["group_id"]):
        if pantheon["group_id"] in seen:
            continue  # cycle guard — a malformed parent chain must not hang the build
        seen.add(pantheon["group_id"])
        rows = _group_person_rows(conn, pantheon["group_id"])
        if not rows:
            continue
        table = _md_table(["Name", "Epithets"], rows)
        blocks.append(f"### {pantheon['name']}\n\n{table}\n")

    if not blocks:
        return ""
    return "## Gods\n\n" + "\n".join(blocks)


# ---------------------------------------------------------------------------
# Deathmatch Super Slam Guilds — three levels: a federation holds stables,
# each fronted by a patron (group_npcs on the stable itself) who does not
# fight in it, and each stable holds guilds. A patron is rendered as a prose
# line, never as a row in the guild-name table — the word "member" strains
# there and a table row would say it anyway.
# ---------------------------------------------------------------------------


def _section_super_slam(conn: sqlite3.Connection) -> str:
    federation = _group_by_name(conn, "Super Slam Guilds")
    if federation is None:
        return ""

    stable_blocks: list[str] = []
    seen: set[str] = {federation["group_id"]}
    for stable in _child_groups(conn, federation["group_id"]):
        if stable["group_id"] in seen:
            continue  # cycle guard
        seen.add(stable["group_id"])

        lines = [f"### {stable['name']}"]

        patrons = conn.execute(
            """
            SELECT c.name
            FROM group_npcs gn
            JOIN characters c ON c.character_id = gn.character_id
            WHERE gn.group_id = ?
            ORDER BY c.name
            """,
            (stable["group_id"],),
        ).fetchall()
        if patrons:
            lines.append("**Patron:** " + ", ".join(p["name"] for p in patrons))

        guilds = _child_groups(conn, stable["group_id"])
        if guilds:
            table = _md_table(["Name"], [[g["name"]] for g in guilds])
            lines.append(table)
        else:
            # Moloca's Guilds: a stable fronted with no guild. Recorded, not
            # dropped — an empty stable is the only row shape that could say so.
            lines.append("*No guilds recorded.*")

        stable_blocks.append("\n\n".join(lines) + "\n")

    if not stable_blocks:
        return ""
    return "## Deathmatch Super Slam Guilds\n\n" + "\n".join(stable_blocks)


# ---------------------------------------------------------------------------
# Assembly
# ---------------------------------------------------------------------------


def render_markdown(conn: sqlite3.Connection) -> str:
    """Render the full Character Groups page from ``conn``.

    Deterministic: every query orders by name (or ordinal, then name), so two
    runs against the same database produce byte-identical output.
    """
    # Hand-written page's own section order.
    sections: list[str] = [
        _section_species(conn, "Aesir", "Aesir"),
        _section_species(conn, "Ancients", "Ancient"),
        _section_dracai(conn),
        _section_dragons(conn),
        _section_species(conn, "Embra", "Embra"),
        _section_grand_magisters(conn),
        _section_gods(conn),
        _section_species(conn, "Heralds", "Herald"),
        _section_super_slam(conn),
    ]

    body = "\n".join(s for s in sections if s)
    text = "# Character Groups\n"
    if body:
        text += "\n" + body
    return text


def main(output_md: Path, *, db_path: Path | None = None) -> None:
    """Render the Character Groups markdown from ``fablore.db`` to ``output_md``.

    Opens the database through :class:`db.Database`, not a bare ``sqlite3``
    connection — the DB is a runtime artefact seeded from the CSVs on first
    open, so this works on a fresh clone where ``fablore.db`` does not exist
    yet, the same way every other entry point into the database does.

    Args:
        output_md: Destination path. **Required, and deliberately so** — see the
            module docstring. :data:`OUTPUT_MD` names the live page this will
            write once the data entry it waits on has landed; until then nothing
            should be able to reach that path without naming it.
        db_path: Database path. Defaults to ``src/data/fablore.db``.
    """
    from db import Database

    database = Database(db_path if db_path is not None else DB_PATH)
    try:
        text = render_markdown(database.conn)
    finally:
        database.conn.close()
    Path(output_md).write_text(_BANNER + text, encoding="utf-8")


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        raise SystemExit(
            "usage: python3 src/data/create_character_groups_md.py <output.md>\n"
            "The destination is required. This does not yet generate the live page — "
            "see the module docstring for what has to land first."
        )
    main(Path(sys.argv[1]))
