"""Archive pages — deliberately empty.

``src/archive/`` holds retired, superseded content: pages the live site has
moved past. **An archived page is never declared**, so it links to no entity.
A declaration would make a retired page assert links that can outlive the
reason it was archived, and would list it in Related Lore and the Lore Graph
beside the live page that replaced it. When a page moves into the archive,
delete its declaration rather than moving it here.

``tests/test_data_entry.py`` fails on any declaration under ``src/archive/``,
and ``validate_data.py`` does not count archive pages as undeclared.

The module exists only because ``archive`` is a story type: ``SECTIONS`` maps
every story root ``create_stories_index.py`` scans to a module. Archive pages
still get ``stories.csv`` rows from that scan, just never story links.
"""
