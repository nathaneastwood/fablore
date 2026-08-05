#!/usr/bin/env bash
# One-off migration: drop the numeric set prefix from media paths.
#
#   main-story/22-usurp-the-shadow-throne/x.webp  ->  main-story/usurp-the-shadow-throne/x.webp
#
# Why: repo folders are unnumbered (src/main-story/usurp-the-shadow-throne/) but
# media paths are numbered, so nothing can derive one from the other. The numbers
# were the 0-based row index of story-arcs.csv until that invariant broke, and
# they are referenced nowhere except image URLs in markdown -- no code sorts,
# joins, or routes on them. Flattening makes the rule "media prefix = repo dir
# minus src/", with no lookup table to maintain.
#
# Objects are COPIED, never moved. The numbered keys stay live so any external
# hotlink (Discord embed, another site) keeps working, and re-running is safe.
#
# Usage:
#   scripts/flatten-s3-prefixes.sh              # dry run: show the plan, touch nothing
#   scripts/flatten-s3-prefixes.sh --apply      # copy in S3, verify, then rewrite markdown
#   scripts/flatten-s3-prefixes.sh --verify     # only re-check that target URLs resolve
set -euo pipefail

BUCKET="${FABLORE_S3_BUCKET:-legendary-stories}"
PROFILE="${FABLORE_AWS_PROFILE:-legendary-stories-media}"
CDN="https://d2hl7maqck52px.cloudfront.net"

ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"

MODE="dry-run"
case "${1:-}" in
  --apply)  MODE="apply" ;;
  --verify) MODE="verify" ;;
  "")       ;;
  *) echo "unknown argument: $1" >&2; exit 2 ;;
esac

# Numbered prefixes, enumerated from S3 -- the authoritative source. Deriving them
# from markdown instead would silently miss any prefix that no page happens to
# reference, and those objects would be stranded at the old path after the rewrite.
mapfile -t PREFIXES < <(
  aws s3 ls "s3://${BUCKET}/" --recursive --profile "$PROFILE" \
    | awk '{print $4}' \
    | sed 's|/[^/]*$||' \
    | grep -E '(^|/)[0-9]{2}-' \
    | sort -u
)

# Cross-check against what markdown references, and report either kind of drift.
mapfile -t MD_PREFIXES < <(
  grep -rho "cloudfront.net/[a-z0-9./-]*" src/ --include="*.md" \
    | sed 's|.*net/||; s|/[^/]*$||' \
    | grep -E '(^|/)[0-9]{2}-' \
    | sort -u
)
orphans="$(comm -23 <(printf '%s\n' "${PREFIXES[@]}") <(printf '%s\n' "${MD_PREFIXES[@]}") || true)"
dangling="$(comm -13 <(printf '%s\n' "${PREFIXES[@]}") <(printf '%s\n' "${MD_PREFIXES[@]}") || true)"
if [ -n "$orphans" ]; then
  echo "note: in S3 but referenced by no markdown (still migrated, so nothing is stranded):"
  printf '  %s\n' $orphans
fi
if [ -n "$dangling" ]; then
  echo "ERROR: referenced by markdown but absent from S3 -- these are already broken links:" >&2
  printf '  %s\n' $dangling >&2
  exit 1
fi

if [ "${#PREFIXES[@]}" -eq 0 ]; then
  echo "Nothing to do: no numbered media prefixes found in src/."
  exit 0
fi

# Every distinct numbered URL, so we can verify each target key individually
# rather than trusting that a --recursive copy covered everything.
mapfile -t URLS < <(
  grep -rho "cloudfront.net/[^\"')[:space:]]*" src/ --include="*.md" \
    | sed 's|.*net/||' \
    | grep -E '/[0-9]{2}-' \
    | sort -u
)

unnumber() { sed -E 's|/[0-9]{2}-|/|'; }

echo "bucket:   s3://${BUCKET}"
echo "profile:  ${PROFILE}"
echo "prefixes: ${#PREFIXES[@]}"
echo "objects:  ${#URLS[@]}"
echo "files:    $(grep -rlE "cloudfront.net/[a-z-]+/[0-9]{2}-" src/ --include='*.md' | wc -l | tr -d ' ')"
echo

# ---------------------------------------------------------------------------
# Phase 1 - copy each numbered prefix to its unnumbered twin
# ---------------------------------------------------------------------------
if [ "$MODE" != "verify" ]; then
  echo "== phase 1: copy =="
  for src_prefix in "${PREFIXES[@]}"; do
    dst_prefix="$(printf '%s' "$src_prefix" | unnumber)"
    echo "  ${src_prefix}/ -> ${dst_prefix}/"
    if [ "$MODE" = "apply" ]; then
      aws s3 cp "s3://${BUCKET}/${src_prefix}/" "s3://${BUCKET}/${dst_prefix}/" \
        --recursive --profile "$PROFILE" --only-show-errors
    fi
  done
  echo
fi

if [ "$MODE" = "dry-run" ]; then
  echo "Dry run. Re-run with --apply to perform the copy and rewrite."
  exit 0
fi

# ---------------------------------------------------------------------------
# Phase 2 - verify every target URL resolves before touching any markdown
# ---------------------------------------------------------------------------
echo "== phase 2: verify =="
missing=0
for url in "${URLS[@]}"; do
  target="$(printf '%s' "$url" | unnumber)"
  code="$(curl -s -o /dev/null -w '%{http_code}' --head "${CDN}/${target}" || true)"
  if [ "$code" != "200" ]; then
    echo "  MISSING (${code}): ${CDN}/${target}"
    missing=$((missing + 1))
  fi
done

if [ "$missing" -gt 0 ]; then
  echo
  echo "${missing}/${#URLS[@]} target URLs did not resolve. No markdown was changed."
  echo "CloudFront can negative-cache a 404 briefly after upload -- wait a minute"
  echo "and re-run with --verify before assuming the copy failed."
  exit 1
fi
echo "  all ${#URLS[@]} target URLs return 200"
echo

if [ "$MODE" = "verify" ]; then
  exit 0
fi

# ---------------------------------------------------------------------------
# Phase 3 - rewrite markdown
# ---------------------------------------------------------------------------
echo "== phase 3: rewrite =="
mapfile -t FILES < <(grep -rlE "cloudfront.net/[a-z-]+/[0-9]{2}-" src/ --include='*.md')
for f in "${FILES[@]}"; do
  # Anchored to the CDN host so only media URLs are touched, never prose.
  perl -pi -e 's{(cloudfront\.net/[a-z-]+)/\d{2}-}{$1/}g' "$f"
  echo "  ${f}"
done

echo
echo "Rewrote ${#FILES[@]} files. Numbered keys are still live in S3 -- delete them"
echo "later, separately, once you are satisfied nothing external depends on them."
echo "Now run: mdbook build && python3 src/data/validate_data.py"
