#!/bin/bash
# Render the Gazette prototype to PDF via CDP (render.py).
# Chrome's --print-to-pdf stamps date/URL/title chrome (flag ignored since ~v131),
# so we use Page.printToPDF with displayHeaderFooter=false. (Style guide section 1.)
# Usage: ./render.sh prototype/monday-v2.html [output.pdf]
set -e
SRC="${1:-prototype/monday-v6.html}"
OUT="${2:-${SRC%.html}.pdf}"
python3 prototype/render.py "$SRC" "$OUT"
pdfinfo "$OUT" | grep Pages
