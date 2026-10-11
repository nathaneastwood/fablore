"""Other-character page registrations — one ``db.upsert_story`` call per page.

Relationships only: a call here declares which entities a page links to, never
lore text. Location ``notes`` and monster/fauna/flora ``description`` values
belong in ``descriptions.py`` — see that file for why.

Preview one page with ``python3 src/data/data-entry.py --only <path>``; see
``data-entry.py`` for the full preview-then-commit workflow.
"""

from __future__ import annotations

from entries._runner import db
from entries.catalogue import (
    characters as people,
)
from entries.catalogue import (
    groups as grp,
)
from entries.catalogue import (
    locations as loc,
)
from entries.catalogue import (
    regions as reg,
)
from entries.catalogue import (
    titles as ttl,
)

db.upsert_story(
    path="src/other-characters/krest-mortimer.md",
    story_type="other-characters",
    title="Dr. Krest Mortimer, 'The Fixer'",
    characters=[
        "arakni-huntsman",
        "arakni-solitary-confinement",
        "arakni-web-of-deceit",
        people.ACHLYS_HAG_OF_MOJIRE,
        people.GAVIN,
        people.LENA_BELLE,
        people.RAVEN,
    ],
    locations=[
        loc.MOJIRE,
        loc.SOUTHMAW,
    ],
    regions=[reg.DEMONASTERY, reg.METRIX, reg.THE_PITS],
    groups=[grp.L_APOCALYPTA],
    dry_run=True,
)


db.upsert_story(
    path="src/other-characters/the-librarian.md",
    story_type="other-characters",
    title="The Librarian",
    authors="Nicola Price, Tarryn Thomas",
    artists="Federico Musetti",
    source_link="https://fabtcg.com/articles/librarian/",
    publication_date="2021-05-24",
    titles=[ttl.MAGISTER],
    dry_run=True,
)

db.upsert_story(
    path="src/other-characters/minerva-themis.md",
    story_type="other-characters",
    title="Minerva Themis",
    authors="Nicola Price, Tarryn Thomas",
    artists="Mihail Spil-Haufter",
    source_link="https://fabtcg.com/articles/minerva-themis/",
    publication_date="2021-05-17",
    characters=[
        people.MERCURIUS,
    ],
    locations=[
        loc.GOLDEN_CHARIOT,
        loc.THE_GOLDEN_FIELDS,
    ],
    regions=[reg.METRIX, reg.SOLANA, reg.VOLCOR],
    groups=[grp.GEMINI],
    dry_run=True,
)

db.upsert_story(
    path="src/other-characters/lord-sutcliffe.md",
    story_type="other-characters",
    title="Lord Sutcliffe",
    authors="Nicola Price, Tarryn Thomas",
    artists="bimawithpencil",
    source_link="https://fabtcg.com/articles/lord-sutcliffe/",
    publication_date="2021-05-10",
    characters=["viserai", people.LORD_SUTCLIFFE],
    regions=[reg.DEMONASTERY],
    groups=[grp.DISCIPLES_OF_PAIN],
    dry_run=True,
)

db.upsert_story(
    path="src/other-characters/README.md",
    story_type="other-characters",
    title="Readme",
    dry_run=True,
)

db.upsert_story(
    path="src/other-characters/lady-barthimont.md",
    story_type="other-characters",
    title="Lady Barthimont",
    authors="Nicola Price, Tarryn Thomas",
    artists="Carlos Cruchaga",
    source_link="https://fabtcg.com/articles/lady-barthimont/",
    publication_date="2021-05-03",
    characters=[people.LADY_BARTHIMONT, people.LORD_BARTHIMONT],
    locations=[loc.THE_NORTHERN_REALMS],
    regions=[reg.SOLANA],
    dry_run=True,
)
