#!/bin/bash
# Regression test for render.sh's math-punctuation rewriting and stylesheet ordering.
#
# For each fixture under test/render/, render it via the Makefile (capturing render.sh's
# post-sed, pre-renderer stream through RENDER_INTERMEDIATE) and compare that intermediate
# against the checked-in golden. Also check, in the rendered HTML, that our style.css loads
# after the KaTeX CSS (so our `.katex .*` font overrides win the cascade).
#
# Update goldens after an intended render.sh change with:
#   RENDER_INTERMEDIATE=test/render/<stem>.intermediate make rendered/test/<stem>.html
set -euo pipefail

cd "$(dirname "$0")/.."   # repo root

# `.Makefile.uptodate` runs `make clean` (which removes temp/), so create temp/ after it.
make .Makefile.uptodate >/dev/null
mkdir -p temp
# Clean up our own intermediates on exit, so we don't leave files that would trip
# update_check.sh's `rmdir temp` (it shares temp/ but expects to empty it).
trap 'rm -f temp/test-render-*.intermediate' EXIT

status=0

check() {
    stem="$1"
    html="rendered/test/${stem}.html"
    golden="test/render/${stem}.intermediate"
    got="temp/${stem}.intermediate"

    rm -f "$html"
    RENDER_INTERMEDIATE="$got" make "$html" >/dev/null

    if diff -u "$golden" "$got"; then
        echo "PASS  intermediate  ${stem}"
    else
        echo "FAIL  intermediate  ${stem}  (diff above: golden vs actual)"
        status=1
    fi

    # Our style.css must load after the KaTeX CSS, else our `.katex .*` overrides lose.
    katex_line="$(grep -n 'katex\.min\.css' "$html" | head -1 | cut -d: -f1 || true)"
    style_line="$(grep -n 'href="css/style\.css"' "$html" | head -1 | cut -d: -f1 || true)"
    if [ -n "$katex_line" ] && [ -n "$style_line" ] && [ "$style_line" -gt "$katex_line" ]; then
        echo "PASS  css-order     ${stem}  (style.css@${style_line} after katex@${katex_line})"
    else
        echo "FAIL  css-order     ${stem}  (katex=${katex_line:-none} style=${style_line:-none})"
        status=1
    fi
}

check test-render-rst
check test-render-md

if [ "$status" -eq 0 ]; then
    echo "render tests: PASS"
else
    echo "render tests: FAIL"
fi
exit "$status"
