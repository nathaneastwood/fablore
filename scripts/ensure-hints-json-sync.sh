#!/usr/bin/env bash
# Pre-commit: regenerate hints.json (if DB exists) and fail if it differs.
# When fablore.db is absent (e.g. fresh clone) the check is skipped — CI
# builds from the committed hints.json, which is the intended workflow.
set -euo pipefail
ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"

DB="src/data/fablore.db"
if [[ ! -f "$DB" ]]; then
  echo "ensure-hints-json-sync: fablore.db not found, skipping hints.json check."
  exit 0
fi

python3 src/data/generate_hints_json.py

if ! git diff --quiet -- src/hints.json; then
  echo "ensure-hints-json-sync: src/hints.json is out of date."
  echo "Run from repo root:  python3 src/data/generate_hints_json.py"
  echo "Then stage the updated hints.json. Diff:"
  git diff -- src/hints.json
  exit 1
fi
