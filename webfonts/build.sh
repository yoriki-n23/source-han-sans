#!/usr/bin/env bash
# Build Source Han Sans JP into the renamed "Kaku Sans JP" web fonts in dist/site
# for Cloudflare Pages (see split.py for why the family is renamed).
# Requires: pip install -r webfonts/requirements.txt
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="${OUT:-$ROOT/dist}"
WEIGHTS="${WEIGHTS:-ExtraLight Light Normal Regular Medium Bold Heavy}"

rm -rf "$OUT"
mkdir -p "$OUT/otf" "$OUT/site"

# Japanese subset OTFs, same command lines as COMMANDS.txt
for w in $WEIGHTS; do
  echo "Building SourceHanSansJP-$w.otf"
  otf="$OUT/otf/SourceHanSansJP-$w.otf"
  cff="$OUT/otf/CFF.JP.$w"
  (
    cd "$ROOT/$w"
    makeotf -f cidfont.ps.JP -o "$otf" -omitMacNames -ff features.JP -fi cidfontinfo.JP \
      -mf ../FontMenuNameDB.SUBSET -r -nS -cs 1 -ch ../UniSourceHanSansJP-UTF32-H \
      -ci ../SourceHanSans_JP_sequences.txt > /dev/null
    tx -cff +S cidfont.ps.JP "$cff" 2> /dev/null
    sfntedit -a CFF="$cff" "$otf"
    rm "$cff"
  )
done

python3 "$ROOT/webfonts/split.py" "$OUT/otf" "$OUT/site"
cp "$ROOT/webfonts/index.html" "$ROOT/webfonts/_headers" "$ROOT/LICENSE.txt" "$OUT/site/"
