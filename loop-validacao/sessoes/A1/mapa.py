#!/usr/bin/env python3
"""A1-1: chance de colher bem por cultura e decêndio de plantio em São Miguel do Oeste."""
import json, statistics as st
from modelo_sc import *

L = Local("power_sao_miguel_do_oeste.json")
ANOS = range(1984, 2025)

def mapa(cultura, solo, t_geada=T_GEADA):
    out = {}
    for dec in range(1, 37):
        rs = [simular(L, cultura, solo, data_plantio(a, dec), t_geada) for a in ANOS]
        rs = [r for r in rs if r]
        if not rs: continue
        n = len(rs)
        agua = sum(r["y"] >= LIMIAR_COLHE for r in rs) / n
        geada = sum(r["geada"] for r in rs) / n
        bem = sum(r["y"] >= LIMIAR_COLHE and not r["geada"] for r in rs) / n
        out[dec] = dict(n=n, agua=round(10 * agua, 1), geada=round(10 * geada, 1), bem=round(10 * bem, 1),
                        y_med=round(st.mean(r["y"] for r in rs), 2), y_min=round(min(r["y"] for r in rs), 2))
    return out

if __name__ == "__main__":
    res = {}
    for solo in ("medio", "argiloso"):
        for c in CULTURAS:
            res[f"{c}|{solo}"] = mapa(c, solo)
    json.dump(res, open("mapa_smo.json", "w"), indent=1)
    MES = "jan fev mar abr mai jun jul ago set out nov dez".split()
    for solo in ("argiloso",):
        print("solo", solo, "| célula = colher bem em 10 (água/geada)")
        for c in CULTURAS:
            m = res[f"{c}|{solo}"]
            print(c)
            print("  " + " ".join(f"{MES[(d-1)//3]}{(d-1)%3+1}:{m[d]['bem']:.0f}({m[d]['agua']:.0f}/{m[d]['geada']:.0f})" for d in m))
