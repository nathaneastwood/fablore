#!/usr/bin/env bash
# Link checks hook: build the book, then check links with lychee.
#
# Builds into its own temp directory via `mdbook build --dest-dir`, never
# `./book` — `./book` belongs to `mdbook serve` alone, which rebuilds it on
# every source change. Building there too meant this hook could read a
# half-rewritten tree mid-rebuild and report thousands of spurious "file not
# found" errors for CSS assets and the theme favicon; a stray comment here
# used to blame that on `rm -rf` and the filesystem not having "settled" —
# it doesn't, it was this race, and there is no `rm -rf` left to blame now
# that this hook has its own directory.
set -euo pipefail
ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"

python src/data/create_md.py

BUILD_DIR="$(mktemp -d "${TMPDIR:-/tmp}/fablore-link-checks.XXXXXX")"
trap 'rm -rf "$BUILD_DIR"' EXIT

# Fast-fail if a live `mdbook serve` would still collide with $BUILD_DIR —
# it won't, since $BUILD_DIR is never `book/`, but this is the safety net
# for if that ever stops being true (see src/data/build_guard.py).
python3 src/data/build_guard.py "$BUILD_DIR"

mdbook build --dest-dir "$BUILD_DIR"
lychee --config lychee.toml --root-dir "$BUILD_DIR" "$BUILD_DIR"
