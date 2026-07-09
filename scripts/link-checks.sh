#!/usr/bin/env bash
# Link checks hook: build the book, then check links with lychee.
set -e
python src/data/create_md.py
rm -rf book
# mdbook build can intermittently fail right after rm -rf with "File exists
# (os error 17)" if the filesystem hasn't settled the removal yet; retry once.
mdbook build || mdbook build
lychee --config lychee.toml --root-dir "$(pwd)/book" ./book
