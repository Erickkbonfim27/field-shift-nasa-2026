#!/usr/bin/env python3
"""A2-3 · La Niña sabida no fim de agosto (ONI JAS, NOAA, só para separar anos) prevê primavera seca (out–nov)?
E muda a melhor data de plantio do milho simulado? Saída: resultados/a2_3_<local>.json"""
import json, sys, datetime as dt
import numpy as np
from base import *

local = sys.argv[1] if len(sys.argv) > 1 else "smo"
D = carregar(local)
val, _ = oni()
L = []
for Y in range(1981, 2025):
    r = dict(Y=Y, oni=val[("JAS", Y)], fase=fase_simples(val[("JAS", Y)]))
    r["chuva_on"] = soma(D["chuva"], dt.date(Y, 10, 1), dt.date(Y, 11, 30))
    et = soma(D["et0"], dt.date(Y, 10, 1), dt.date(Y, 11, 30))
    r["bh_on"] = None if et is None else r["chuva_on"] - et
    r["gwr_30nov"] = D["P"]["GWETROOT"][f"{Y}1130"]
    L.append(r)


def teste(alvo):
    LL = [r for r in L if r[alvo] is not None]
    v = np.array([r[alvo] for r in LL]); fases = [r["fase"] for r in LL]; n = len(LL)
    o = (v <= tercil_inferior(v)).astype(float)
    res = dict(alvo=alvo, n=n, base=float(o.mean()), por_fase={})
    for f in ("nina", "neutro", "nino"):
        idx = [i for i in range(n) if fases[i] == f]
        res["por_fase"][f] = dict(n=len(idx), secos=int(o[idx].sum()), p=float(o[idx].mean()),
                                  anos_secos=[LL[i]["Y"] for i in idx if o[i]], mediana=float(np.median(v[idx])))
    a, b = res["por_fase"]["nina"], res["por_fase"]["nino"]
    res["fisher"] = fisher_uni(a["secos"], a["n"], b["secos"], b["n"])
    pf, pc, ob = [], [], []
    for i in range(n):
        m = [j for j in range(n) if j != i]
        lim = tercil_inferior(v[m]); oo = (v[m] <= lim).astype(float)
        mesma = [k for k, j in enumerate(m) if fases[j] == fases[i]]
        pc.append(oo.mean()); pf.append(oo[mesma].mean()); ob.append(float(v[i] <= lim))
    res["bss"] = 1 - brier(pf, ob) / brier(pc, ob)
    res["metades"] = {}
    for nome, (a0, a1) in {"1981-2002": (1981, 2002), "2003-2024": (2003, 2024)}.items():
        res["metades"][nome] = {f: [int(sum(o[i] for i in range(n) if fases[i] == f and a0 <= LL[i]["Y"] <= a1)),
                                    sum(1 for i in range(n) if fases[i] == f and a0 <= LL[i]["Y"] <= a1)] for f in ("nina", "neutro", "nino")}
    res["spearman_oni"] = [float(t) for t in stats.spearmanr([r["oni"] for r in LL], v)]
    return res


saida = dict(local=D["nome"], testes=[teste("bh_on"), teste("chuva_on"), teste("gwr_30nov")])

# muda a decisão? melhor data de plantio do milho simulado por fase JAS
DATAS = [(8, 21), (9, 11), (10, 1), (10, 21), (11, 11)]
tab = {}
for (m, d) in DATAS:
    ys = {}
    for r in L:
        y = milho_simulado(D, r["Y"], m, d)
        if y is not None: ys[r["Y"]] = y
    tab[f"{d:02d}/{m:02d}"] = ys
dec = {}
for grupo in ("todos", "nina", "neutro", "nino"):
    linha = {}
    for data, ys in tab.items():
        anos = [a for a in ys if grupo == "todos" or next(r["fase"] for r in L if r["Y"] == a) == grupo]
        perda = float(np.mean([ys[a] < 0.6 for a in anos])); med = float(np.mean([ys[a] for a in anos]))
        linha[data] = dict(n=len(anos), perda=perda, media=med)
    melhor = min(linha, key=lambda k: (linha[k]["perda"], -linha[k]["media"]))
    dec[grupo] = dict(datas=linha, melhor=melhor)
saida["decisao_data_plantio"] = dec

if local == "smo":
    _, anom = pam()
    g = {}
    for r in L:
        a = anom.get(r["Y"] + 1)
        if a is not None: g.setdefault(r["fase"], []).append(a)
    saida["ibge_por_fase_jas"] = {f: dict(n=len(v), quebras=sum(1 for a in v if a < 0.8), media=float(np.mean(v))) for f, v in g.items()}

json.dump(saida, open(AQUI / f"resultados/a2_3_{local}.json", "w"), ensure_ascii=False, indent=1)
print(D["nome"])
for t in saida["testes"]:
    pf = t["por_fase"]
    print(f"{t['alvo']:9s} n={t['n']} base={t['base']:.2f} " + " | ".join(f"{f}: {pf[f]['secos']}/{pf[f]['n']}={pf[f]['p']:.2f}" for f in pf)
          + f" | Fisher p={t['fisher']:.3f} BSS={t['bss']:+.3f} rho={t['spearman_oni'][0]:+.2f} (p={t['spearman_oni'][1]:.2f}) metades={t['metades']}")
    print("    secos La Niña:", pf["nina"]["anos_secos"], " El Niño:", pf["nino"]["anos_secos"])
for gname, x in dec.items():
    print(gname, "melhor:", x["melhor"], {k: (round(v["perda"], 2), round(v["media"], 2), v["n"]) for k, v in x["datas"].items()})
if local == "smo": print("IBGE:", saida["ibge_por_fase_jas"])
