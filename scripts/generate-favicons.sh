#!/usr/bin/env bash
# Regenerate favicon and touch-icon assets from the master crop.
# Requires: ImageMagick 7+ ("magick") and Google libwebp ("cwebp") on PATH.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SRC="${ROOT}/src/assets/logo_original_cropped.png"
OUT="${ROOT}/src/assets"

if [[ ! -f "$SRC" ]]; then
    echo "error: missing source image: $SRC" >&2
    exit 1
fi

MAGICK=""
if command -v magick >/dev/null 2>&1; then
    MAGICK="$(command -v magick)"
elif command -v convert >/dev/null 2>&1; then
    MAGICK="$(command -v convert)"
else
    echo "error: ImageMagick not found (install imagemagick; need magick or convert)" >&2
    exit 1
fi

if ! command -v cwebp >/dev/null 2>&1; then
    echo "error: cwebp not found (install libwebp)" >&2
    exit 1
fi

echo "Using source: $SRC"
"$MAGICK" "$SRC" -resize 32x32 "${OUT}/favicon.png"
"$MAGICK" "$SRC" -define icon:auto-resize=48,32,16 "${OUT}/favicon.ico"
"$MAGICK" "$SRC" -resize 180x180 "${OUT}/apple-touch-icon.png"
cwebp -quiet "${OUT}/favicon.png" -o "${OUT}/favicon.webp"

echo "Wrote: ${OUT}/favicon.png, favicon.ico, favicon.webp, apple-touch-icon.png"
echo "Done."
