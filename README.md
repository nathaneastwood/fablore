<a name="readme-top"></a>

<p align="center">
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="src/assets/logo_transparent_white.png">
  <img alt="Legendary Stories" src="src/assets/logo_transparent.png" width="220">
</picture>
</p>

# fablore

[![Build Status](https://github.com/nathaneastwood/fablore/actions/workflows/ci.yml/badge.svg)](https://github.com/nathaneastwood/fablore/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Website](https://img.shields.io/website?url=https%3A%2F%2Flegendarystories.net)](https://legendarystories.net)
[![Buy Me a Coffee](https://img.shields.io/badge/Buy%20Me%20a%20Coffee-%E2%98%95-ef61a3.svg)](https://www.buymeacoffee.com/nathaneastwood)

**fablore** is the source repository for [Legendary Stories](https://legendarystories.net/), a community-curated digital archive of all known official *Flesh and Blood* lore. The site is built using [mdBook](https://github.com/rust-lang/mdBook).

## 🚀 Getting Started

### Prerequisites

* Install [mdBook](https://github.com/rust-lang/mdBook) 0.5 or later
* Python 3.12: every build runs the preprocessors in [`src/data/`](src/data/), so `python3` must be on your `PATH`
* Clone the repository:

```bash
git clone https://github.com/nathaneastwood/fablore.git
cd fablore
```

### Build the Book

```bash
mdbook build
```

### Serve Locally

```bash
mdbook serve --open
```

### Python data pipeline tests

Optional checks on CSV helpers, generators, and validation (see [`src/data/README.md`](src/data/README.md)):

```bash
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
python3 -m pytest
```

`requirements-dev.txt` pulls in `requirements-data.txt` (numpy, pandas, `py-markdown-table`) so `tests/test_create_md.py` and the pre-commit `ensure-create-md-sync` hook can run without extra installs.

<p align="right"><a href="#readme-top">Back to top</a></p>

## 🖼️ Images

Images should be optimised and converted to [WebP](https://chromium.googlesource.com/webm/libwebp) format before use.

Convert a directory of images like so:

```bash
for file in path/to/files/*; do cwebp "$file" -o "${file%.*}.webp"; done
```

Install `cwebp` using your system package manager, or refer to the [official installation guide](https://developers.google.com/speed/webp/download).

<p align="right"><a href="#readme-top">Back to top</a></p>

## 🧩 Preprocessors

There are no third-party mdBook plugins. Each extension is a local Python preprocessor, registered in [`book.toml`](book.toml) and run by mdBook on each build:

| Preprocessor | What it does |
|---|---|
| `hints` | Auto-links entities and injects tooltip markup (see [Linking Rules](#-linking-rules)) |
| `related` | Adds the "related stories" block to story pages |
| `story-meta` / `hero-meta` / `set-meta` | Renders metadata headers |
| `hero-traits` | Renders hero trait icons |
| `breadcrumb` | Builds the breadcrumb trail (runs after `set-meta`) |
| `browse` / `sets-hub` / `set-index` / `child-hub` | Generate index and hub pages |
| `narrated-videos` | Embeds narrated-video links |
| `archive-notice` | Adds the archival banner |

The preprocessors are stdlib-only, so a plain `mdbook build` needs no `pip install`. `numpy`, `pandas` and `py-markdown-table` are only needed for the generators and tests (see [Python data pipeline tests](#python-data-pipeline-tests)).

### Tooltips

The hint tooltips are rendered client-side by [`theme/hints.js`](theme/hints.js) against the generated [`src/hints.json`](src/hints.json). The two libraries it depends on are loaded in [`theme/head.hbs`](theme/head.hbs):

```html
<!-- Required by the hints preprocessor -->
<script src="https://unpkg.com/@popperjs/core@2"></script>
<script src="https://unpkg.com/tippy.js@6"></script>
```

Per-page tables of contents come from mdBook 0.5's built-in sidebar heading navigation.

<p align="right"><a href="#readme-top">Back to top</a></p>

## 🔍 Link Checking with `lychee`

Check the links in the built site with [`lychee`](https://github.com/lycheeverse/lychee), run against the `book/` output:

```bash
brew install lychee
mdbook build
lychee --config lychee.toml --root-dir "$(pwd)/book" ./book
```

This catches broken links and missing anchors. See [`scripts/link-checks.sh`](scripts/link-checks.sh) for more detail.

<p align="right"><a href="#readme-top">Back to top</a></p>

## ✅ Pre-commit Hooks

The hooks only run on `git commit` once they are installed into the clone. `pre-commit` comes with [`requirements-dev.txt`](requirements-dev.txt); enable the hooks once per clone with:

```bash
pre-commit install
```

Without that step the config below is inert and commits go through unchecked. To run the hooks by hand at any time:

```bash
pre-commit run --all-files
```

| Hook | Trigger | What it does |
|---|---|---|
| `ensure-create-md-sync` | A mirrored CSV or `create_md.py` changed | Verifies the CSV/Markdown mirror is current |
| `ensure-hints-json-sync` | `hints_supplement.json`, `generate_hints_json.py`, `descriptions.py` or a described CSV changed | Regenerates `src/hints.json` and fails if it differs |
| `validate-data` | Any `src/data/` CSV or `.py` changed | Runs [`validate_data.py`](src/data/validate_data.py) |
| `link-checks` | Always | Builds the book and runs `lychee` |
| `black` | Python files | Auto-formats |

Plus the standard `check-yaml`, `end-of-file-fixer` and `trailing-whitespace` hooks.

<p align="right"><a href="#readme-top">Back to top</a></p>

## 📏 Linking Rules

Heroes and documented places get inline links to their own pages. The `hints` preprocessor covers everything else. It detects entities by how many pages mention them rather than by what type they are, so you do not need to add manual links for anything it already picks up.

An entity is auto-linked when both of these hold:

1. It has a summary. That means either a non-empty `notes`/`description` in the database, set via [`descriptions.py`](src/data/descriptions.py) for `locations`, `monsters`, `fauna` and `flora`, or a `summary` in [`src/hints_supplement.json`](src/hints_supplement.json) for everything else. Both feed the generated [`src/hints.json`](src/hints.json).
2. It is mentioned on more than one rendered page. An entity named on exactly one page is introduced and explained there, so a tooltip would only restate the sentence the reader is already looking at. See `compute_single_page_keys` in [`mdbook_hints.py`](src/data/mdbook_hints.py).

Type is not a gate. NPCs, factions, aesir, embra, organisations, ships, concepts and artifacts all get tooltips once those two conditions hold.

A new entry in `hints_supplement.json` often renders nothing at first. That is usually condition 2 rather than a mistake: so far the entity is named on one page only, and it will start rendering once a second page mentions it.

To force a link the heuristics skip, write it as `[Text](~Key)`, where `Key` is the `hints_supplement.json` key. To suppress one on a single page, add that page's slug (its path minus `src/` and `.md`) to the entity's `exclude_pages`. That is meant for the page that introduces and describes the entity.

Pages under `data/` are never linked, so `data/md/npcs.md` and its siblings do not tooltip each row against itself. See `_is_generated_page`.

A supplement entry can also override `type` so the tooltip label reads correctly. `Hand of Sol`, for example, is a `locations` row displayed as a `faction`. This changes the label only and never disables detection.

After changing a description or the supplement, regenerate the hint data:

```bash
python3 src/data/generate_hints_json.py
```

<p align="right"><a href="#readme-top">Back to top</a></p>

## 📜 License

The code in this repository is licensed under the MIT License. The lore content is © Legend Story Studios and is not covered by that licence. See [LICENSE](./LICENSE) for the exact wording.

<p align="right"><a href="#readme-top">Back to top</a></p>
