#!/usr/bin/env python3
"""A2-2 · Umidade do solo de novembro (POWER/MERRA-2 GWETROOT, GWETTOP) prevê dez–jan seco?
Alerta = preditor no tercil inferior. Pontuação: acerto, detecção, Brier LOO (logística) contra climatologia.
Saída: resultados/a2_2_<local>.json"""
import json, sys
import numpy as np
from base import *

local = sys.argv[1] if len(sys.argv) > 1 else "smo"
D = carregar(local)
T = tabela_safras(D, range(1981, 2025))

ALVOS = ["gwr_dj", "bh_dj", "chuva_dj", "milho"]
PREDS = ["gwr_nov", "gwr_nov15", "gwt_nov", "gwp_nov", "chuva_nov"]


def ruim(alvo, v, lim): return v < 0.6 if alvo == "milho" else v <= lim


def avaliar(pred, alvo):
    L = [r for r in T if r[alvo] is not None and r[pred] is not None]
    x = np.array([r[pred] for r in L]); v = np.array([r[alvo] for r in L])
    n = len(L)
    lim_a = None if alvo == "milho" else tercil_inferior(v)
    o = np.array([ruim(alvo, a, lim_a) for a in v], float)
    alerta = x <= tercil_inferior(x)
    acertos = int((alerta & (o == 1)).sum())
    res = dict(pred=pred, alvo=alvo, n=n, base=float(o.mean()), n_alerta=int(alerta.sum()), n_ruins=int(o.sum()),
               acerto=acertos / alerta.sum(), deteccao=acertos / o.sum() if o.sum() else float("nan"),
               anos_ruins=[L[i]["Y"] for i in range(n) if o[i]], anos_alerta=[L[i]["Y"] for i in range(n) if alerta[i]])
    res["fisher"] = fisher_uni(acertos, int(alerta.sum()), int(o.sum()) - acertos, n - int(alerta.sum())) if o.sum() else float("nan")
    res["spearman"] = [float(t) for t in stats.spearmanr(x, v)]
    # LOO: limiares e logística refeitos sem o ano i
    pl, pc, pt, ob = [], [], [], []
    for i in range(n):
        m = np.arange(n) != i
        lim_i = None if alvo == "milho" else tercil_inferior(v[m])
        oo = np.array([ruim(alvo, a, lim_i) for a in v[m]], float)
        oi = float(ruim(alvo, v[i], lim_i))
        pc.append(oo.mean()); ob.append(oi)
        pl.append(float(logit_fit(x[m], oo)(x[i])) if 0 < oo.sum() < len(oo) else oo.mean())
        # previsão por tercil do preditor: frequência de ruins nos anos do mesmo tercil do preditor
        t1, t2 = np.percentile(x[m], [100 / 3, 200 / 3])
        cls = lambda z: 0 if z <= t1 else (1 if z <= t2 else 2)
        mesma = np.array([cls(z) == cls(x[i]) for z in x[m]])
        pt.append((oo[mesma].sum() + 3 * oo.mean()) / (mesma.sum() + 3))
    bc = brier(pc, ob)
    res["bss_logit"] = (1 - brier(pl, ob) / bc) if bc else float("nan")
    res["bss_tercil"] = (1 - brier(pt, ob) / bc) if bc else float("nan")
    # metades (acerto do alerta)
    res["metades"] = {}
    for nome, (a0, a1) in {"1981-2002": (1981, 2002), "2003-2024": (2003, 2024)}.items():
        idx = [i for i in range(n) if a0 <= L[i]["Y"] <= a1]
        al = [i for i in idx if alerta[i]]
        res["metades"][nome] = dict(alertas=len(al), acertos=int(sum(o[i] for i in al)), ruins=int(sum(o[i] for i in idx)), n=len(idx))
    return res


saida = dict(local=D["nome"], resultados=[avaliar(p, a) for a in ALVOS for p in PREDS])

# persistência: correlação nov -> dez-jan no próprio GWETROOT, e GWETROOT dez-jan x balanço P-ET0 dez-jan
L = [r for r in T if r["bh_dj"] is not None]
saida["corr_gwr_dj_vs_bh_dj"] = [float(t) for t in stats.spearmanr([r["gwr_dj"] for r in L], [r["bh_dj"] for r in L])]
saida["corr_gwr_dj_vs_milho"] = [float(t) for t in stats.spearmanr([r["gwr_dj"] for r in L], [r["milho"] for r in L])]

if local == "smo":
    prod, anom = pam()
    conf = {}
    for pred in ("gwr_nov", "gwt_nov", "gwr_dj", "bh_dj", "milho"):
        LL = [r for r in T if r[pred] is not None and (r["Y"] + 1) in anom]
        x = np.array([r[pred] for r in LL]); a = np.array([anom[r["Y"] + 1] for r in LL])
        al = x <= tercil_inferior(x); q = a < 0.8
        conf[pred] = dict(n=len(LL), quebras=int(q.sum()), alertas=int(al.sum()), acertos=int((al & q).sum()),
                          spearman=[float(t) for t in stats.spearmanr(x, a)],
                          anos_quebra=[LL[i]["Y"] + 1 for i in range(len(LL)) if q[i]],
                          anos_alerta=[LL[i]["Y"] + 1 for i in range(len(LL)) if al[i]],
                          media_anom_alerta=float(a[al].mean()), media_anom_sem=float(a[~al].mean()))
    saida["ibge"] = conf

json.dump(saida, open(AQUI / f"resultados/a2_2_{local}.json", "w"), ensure_ascii=False, indent=1)
print(D["nome"], "| corr GWR dez-jan x P-ET0 dez-jan:", np.round(saida["corr_gwr_dj_vs_bh_dj"], 3),
      "| x milho:", np.round(saida["corr_gwr_dj_vs_milho"], 3))
for r in saida["resultados"]:
    print(f"{r['alvo']:8s} <- {r['pred']:9s} n={r['n']} base={r['base']:.2f} alerta: acerto {r['acerto']:.2f} "
          f"detecção {r['deteccao']:.2f} Fisher p={r['fisher']:.3f} | BSS logit={r['bss_logit']:+.3f} tercil={r['bss_tercil']:+.3f} "
          f"| rho={r['spearman'][0]:+.2f} | metades={[(k, v['acertos'], v['alertas']) for k, v in r['metades'].items()]}")
if local == "smo":
    for k, v in saida["ibge"].items(): print("IBGE", k, v)
