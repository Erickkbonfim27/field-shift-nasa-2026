#!/usr/bin/env python3
"""Exporta os dados gerados do Harvesty para o app Next (harvesty-web).

Lê harvesty/dados/gerado/pacote.json e relevo.json e grava:
  harvesty-web/data/celulas.json          só o servidor lê: 20 pontos do NASA POWER (séries diárias em base64
                                          int16 e as saídas do motor de cada ponto)
  harvesty-web/data/relevo-meta.json      caixa, tamanhos e classes do relevo
  harvesty-web/public/dados/malha.json    contorno dos municípios (IBGE, só desenho), baixado pelo navegador
  harvesty-web/public/relevo/classes.png  classes de declive (valor do pixel = classe; 6 = fora da região)
  harvesty-web/public/relevo/sombra.png   relevo sombreado (com transparência fora da região)

Uso: python3 harvesty/scripts/exportar_web.py   (rode depois de build.sh --dados)
"""
import base64, json
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
WEB = RAIZ.parent / "harvesty-web"
GER = RAIZ / "dados" / "gerado"

pk = json.load(open(GER / "pacote.json"))
rv = json.load(open(GER / "relevo.json"))

(WEB / "data").mkdir(parents=True, exist_ok=True)
(WEB / "public" / "dados").mkdir(parents=True, exist_ok=True)
(WEB / "public" / "relevo").mkdir(parents=True, exist_ok=True)

cel = dict(ini=pk["ini"], ndias=pk["ndias"], meta=pk["meta"], celulas=pk["celulas"])
json.dump(cel, open(WEB / "data" / "celulas.json", "w"), separators=(",", ":"), ensure_ascii=False)
json.dump(pk["malha"], open(WEB / "public" / "dados" / "malha.json", "w"), separators=(",", ":"), ensure_ascii=False)
(WEB / "public" / "relevo" / "classes.png").write_bytes(base64.b64decode(rv["classe"]["png"]))
(WEB / "public" / "relevo" / "sombra.png").write_bytes(base64.b64decode(rv["sombra"]["png"]))
meta = dict(bbox=rv["bbox"], classes=rv["classes"], folhas=rv.get("folhas"), fonte=rv["fonte"],
            classe=dict(w=rv["classe"]["w"], h=rv["classe"]["h"], res_m=rv["classe"]["res_m"]),
            sombra=dict(w=rv["sombra"]["w"], h=rv["sombra"]["h"]))
json.dump(meta, open(WEB / "data" / "relevo-meta.json", "w"), ensure_ascii=False, indent=1)

for p in [WEB / "data" / "celulas.json", WEB / "public" / "dados" / "malha.json",
          WEB / "public" / "relevo" / "classes.png", WEB / "public" / "relevo" / "sombra.png"]:
    print(f"{p.relative_to(WEB)}: {p.stat().st_size / 1e6:.2f} MB")
