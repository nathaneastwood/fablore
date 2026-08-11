# Flavour Text

This folder contains the individual set files which hold the flavour text printed on that set's cards. One page per set: the page's filename stem is the set's slug, and `story-arcs.csv` maps that slug to the set, which is what puts the set metadata card on the page.

The `flavour-to-page` skill drives the whole process. To do it by hand:

* Generate the file with [`get_flavour.py`](get_flavour.py), which needs the [flesh-and-blood-cards](https://github.com/the-fab-cube/flesh-and-blood-cards) repo cloned alongside this one:

  ```python
  from get_flavour import create_flavour_md

  kept, dropped = create_flavour_md("OMN", "../flesh-and-blood-cards/json/english/card-flattened.json",
                                    "omens-of-the-third-age.md")
  ```

  It writes the H1 from `sets.csv`, converts typographic punctuation to ASCII, and excludes any flavour text already published on an earlier set's page — `dropped` lists those with the page they came from. Review it rather than discarding it: a reprinted *card* often carries brand new flavour text, and only the text is compared.
* Check every name the text attributes a quote to against the database. Where a card and an existing record disagree, the printed card decides — and record the correction in the commit message, because regenerating the page will reproduce the upstream spelling.
* Add any new characters, heroes or locations to the [data files](../data) by registering the page as a story in [`data-entry.py`](../data/data-entry.py).
* Add the flavour text file to the [SUMMARY.md](../SUMMARY.md) file, in set release order.

Do **not** add links to first mentions. The `hints` preprocessor detects entities automatically by mention count, and adding markup by hand duplicates it — see the linking rules in [CLAUDE.md](../../CLAUDE.md).

The file structure should look like this:

```
# Set Name

#### Card Name - (XXX000)
Flavour text
```

Where `(XXX000)` is the card's unique set identifier. Where several printings of a card share a line — the pitch cycle of a common, say — the lowest identifier is the one cited.
