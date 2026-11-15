#!/usr/bin/env python3
"""Monta a página final: injeta dados/gerado/pacote.json e relevo.json em src/app.html.

Saída:
  dist/index.html   para abrir localmente (com <meta charset>)
  e, se passar caminhos como argumento, uma cópia sem o <meta> em cada um
  (é o formato que o artifact do Claude espera; o Claude passa esse caminho ao publicar).
"""
import json, sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
t = (RAIZ / "src" / "app.html").read_text(encoding="utf-8")
pk = json.load(open(RAIZ / "dados" / "gerado" / "pacote.json"))
pk.pop("srtm", None)
rv = json.load(open(RAIZ / "dados" / "gerado" / "relevo.json"))
for marca in ("/*__PACOTE__*/null", "/*__RELEVO__*/null"):
    if marca not in t:
        sys.exit(f"faltou a marca {marca} em src/app.html")
html = (t.replace("/*__PACOTE__*/null", json.dumps(pk, separators=(",", ":"), ensure_ascii=False))
         .replace("/*__RELEVO__*/null", json.dumps(rv, separators=(",", ":"))))
(RAIZ / "dist").mkdir(exist_ok=True)
(RAIZ / "dist" / "index.html").write_text('<meta charset="utf-8">\n' + html, encoding="utf-8")
for destino in sys.argv[1:]:
    Path(destino).write_text(html, encoding="utf-8")
print("dist/index.html:", round(len(html.encode()) / 1e6, 2), "MB", ("+ " + ", ".join(sys.argv[1:])) if len(sys.argv) > 1 else "")
