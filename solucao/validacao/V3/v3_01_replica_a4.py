#!/usr/bin/env python3
"""V3-01: confere se meu modelo (cenário "A4") reproduz os casos da A4 (mesmos números)."""
import sys, json, datetime as dt
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import modelo_v3 as V
A4 = V.A4
out = {}
for nome, cad in (("raso", 87.5), ("medio", 125.0), ("argiloso", 175.0)):
    ref = json.load(open(A4 / f"casos_a4_1_R0.85_{nome}_ky1.0_kc1.0_raizNone.json"))
    ref = {(c["safra"], c["dec"] - 2): c for c in ref if c["dec"] in (2, 3, 4, 5, 6)}
    cs = V.casos(cad, scen="A4")
    dmax = 0.0
    for a, di, ym, ys, gm, gs in cs:
        r = ref[(a, di)]
        dmax = max(dmax, abs(r["ym"] - ym), abs(r["ys"] - ys))
    tot0 = V.resumo(V.mistura(cs, 0, 0.85)); tot5 = V.resumo(V.mistura(cs, 0.5, 0.85))
    out[nome] = dict(n=len(cs), dif_max=dmax, base=tot0, f50=tot5)
    print(f"{nome}: n={len(cs)} dif_max vs A4 = {dmax:.2e} | base média {tot0['media']:.3f} P10 {tot0['p10']:.3f} perda {tot0['perda']} | 50% média {tot5['media']:.3f} P10 {tot5['p10']:.3f} perda {tot5['perda']}")
json.dump(out, open(Path(__file__).resolve().parent / "res_01_replica_a4.json", "w"), indent=1)
