#!/usr/bin/env bash
# Pre-commit: regenerate data markdown mirrors and fail if they differ from the index.
# Deps: requirements-data.txt (included in requirements-dev.txt).
set -euo pipefail
ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"

if ! python3 -c "import numpy, pandas, py_markdown_table" 2>/dev/null; then
  echo "ensure-create-md-sync: missing Python deps. From the repo root, install with:"
  echo "  pip install -r requirements-dev.txt"
  echo "or, for create_md only:"
  echo "  pip install -r requirements-data.txt"
  exit 1
fi

python3 src/data/create_md.py

MD_FILES=(
  src/data/npcs.md
  src/data/fauna.md
  src/data/flora.md
  src/data/food-and-drink.md
  src/data/locations.md
  src/data/monsters.md
)

if ! git diff --quiet -- "${MD_FILES[@]}"; then
  echo "ensure-create-md-sync: Markdown mirrors are out of date with the CSVs."
  echo "Run from repo root:  python3 src/data/create_md.py"
  echo "Then stage the updated .md files. Diff:"
  git diff -- "${MD_FILES[@]}"
  exit 1
fi
