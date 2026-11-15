#!/usr/bin/env python3
"""B1-4 · Clima favorável ao míldio da cebola em Ituporanga (critérios em CRITERIOS_ANTES_DO_TESTE.md)."""
import json, datetime as dt, statistics as st
from pathlib import Path
from comum import Local, k, spearman, p_perm, sem_tendencia, acerto_piores, pam

AQUI = Path(__file__).resolve().parent
L = Local("itu")
RH = L.P["RH2M"]
obs = sem_tendencia(pam(AQUI / "externo/pam_cebola_ituporanga.json", "40107", "4208500"))
ANOS = [a for a in range(1984, 2026) if a in obs]
o = [obs[a] for a in ANOS]

def fav(d0, d1, rh_min):
    n = 0
    d = d0
    while d <= d1:
        x = k(d)
        if RH[x] >= rh_min and 10 <= L.t2m[x] <= 22 and L.chuva[x] >= 1: n += 1
        d += dt.timedelta(1)
    return n

out = {}
for rh in (85, 90):
    idx = {a: fav(dt.date(a, 8, 1), dt.date(a, 10, 31), rh) for a in ANOS}
    v = [idx[a] for a in ANOS]
    hit, po, pm = acerto_piores({a: -idx[a] for a in ANOS}, obs, 8)
    # C3 por data de transplante: janela de 90 dias começando 15 dias após o transplante
    todos = range(1981, 2026)
    por_tr = {}
    vals_all = {}
    for m in (6, 7, 8):
        vals_all[m] = [fav(dt.date(a, m, 1) + dt.timedelta(15), dt.date(a, m, 1) + dt.timedelta(105), rh) for a in todos]
    p70 = sorted(sum(vals_all.values(), []))[int(0.7 * 3 * len(todos))]
    for m in (6, 7, 8):
        por_tr[f"01/{m:02d}"] = dict(media_dias=round(st.mean(vals_all[m]), 1), muito_favoravel_em_10=round(10 * sum(1 for x in vals_all[m] if x > p70) / len(todos), 1))
    out[str(rh)] = dict(rho=round(spearman(v, o), 2), p=round(p_perm(v, o, lado="neg"), 4), acerto8=hit, piores_obs=po, piores_indice=pm,
                        media=round(st.mean(v), 1), min=min(v), max=max(v), p70=p70, por_transplante=por_tr, por_ano=idx)
json.dump(out, open(AQUI / "b1_4_resultado.json", "w"), ensure_ascii=False, indent=1)
for rh, r in out.items(): print(rh, {kk: vv for kk, vv in r.items() if kk != "por_ano"})
