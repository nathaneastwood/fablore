#!/usr/bin/env bash
# Pre-commit: regenerate hints.json and fail if it differs.
# generate_hints_json.py opens fablore.db through db.Database, so a missing DB
# (e.g. a fresh clone) is seeded from the committed CSVs first and the check
# always runs.
set -euo pipefail
ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"

python3 src/data/generate_hints_json.py

if ! git diff --quiet -- src/hints.json; then
  echo "ensure-hints-json-sync: src/hints.json is out of date."
  echo "Run from repo root:  python3 src/data/generate_hints_json.py"
  echo "Then stage the updated hints.json. Diff:"
  git diff -- src/hints.json
  exit 1
fi
