#!/usr/bin/env bash
# Regenera las láminas VE-00..VE-03 (A3) y las copia a la carpeta laminas/.
# Requiere: python3, pdflatex (TeX Live con babel-spanish, tikz, siunitx, standalone, helvet), pdftoppm.
set -e
cd "$(dirname "$0")"
PDFLATEX=${PDFLATEX:-pdflatex}
python3 gen_ve00.py
for L in VE-00 VE-01 VE-02 VE-03; do
  "$PDFLATEX" -interaction=nonstopmode "$L.tex" >/dev/null
  mv -f "$L.pdf" ..
  pdftoppm -r 200 -png -singlefile "../$L.pdf" "../$L"
done
rm -f *.aux *.log
echo "Láminas generadas en $(cd .. && pwd)"
