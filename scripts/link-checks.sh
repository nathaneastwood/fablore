#!/usr/bin/env bash
# Link checks hook: build the book, ensure Ruby 3.2, then run htmlproofer.
# Source chruby so it is available in non-interactive pre-commit runs.
set -e
python src/data/create_md.py && mdbook build
for f in /usr/local/share/chruby/chruby.sh /usr/local/opt/chruby/share/chruby/chruby.sh /opt/homebrew/opt/chruby/share/chruby/chruby.sh; do
  [[ -f "$f" ]] && source "$f" && break
done
chruby ruby-3.2.0
htmlproofer ./book --assume-extension --check-html --disable-external --only-4xx --ignore-missing-alt --ignore-files "./book/toc.html,./book/404.html"
