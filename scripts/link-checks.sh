#!/usr/bin/env bash
# Link checks hook: build the book, ensure Ruby 3.2, then run htmlproofer.
# Source chruby so it is available in non-interactive pre-commit runs.
set -e
python src/data/create_md.py
rm -rf book
# mdbook build can intermittently fail right after rm -rf with "File exists
# (os error 17)" if the filesystem hasn't settled the removal yet; retry once.
mdbook build || mdbook build
for f in /usr/local/share/chruby/chruby.sh /usr/local/opt/chruby/share/chruby/chruby.sh /opt/homebrew/opt/chruby/share/chruby/chruby.sh; do
  [[ -f "$f" ]] && source "$f" && break
done
chruby ruby-3.2.0
# bundle exec pins to the versions in Gemfile.lock; running htmlproofer bare
# lets RubyGems resolve against whatever's globally installed, which here
# means old gems without built native extensions (ffi/racc/io-event) — every
# `require` then re-probes and skips them, adding minutes to each run.
bundle exec htmlproofer ./book --assume-extension --check-html --disable-external --only-4xx --ignore-missing-alt --ignore-files "./book/toc.html,./book/404.html"
