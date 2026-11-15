#!/usr/bin/env python3
"""A2-1 · El Niño / La Niña e risco de dez–jan seco (São Miguel do Oeste; Ituporanga como checagem).
ONI da NOAA (fonte externa) só para separar os anos. Saída: resultados/a2_1.json"""
import json, sys
import numpy as np
from base import *

local = sys.argv[1] if len(sys.argv) > 1 else "smo"
D = carregar(local)
T = tabela_safras(D, range(1981, 2025))
val, fase_noaa = oni()
for r in T:
    Y = r["Y"]
    r["oni_ndj"] = val[("NDJ", Y)]
    r["oni_jas"] = val[("JAS", Y)]
    r["fase_ndj"] = fase_noaa.get(("NDJ", Y), "neutro")       # regra NOAA (5 trimestres)
    r["fase_jas"] = fase_simples(val[("JAS", Y)])              # o que se sabe no fim de agosto
    r["fase_aso"] = fase_simples(val[("ASO", Y)])              # o que se sabe no início de novembro

ALVOS = {
    "bh_dj": "balanço P−ET0 dez–jan (tercil inferior)",
    "chuva_dj": "chuva dez–jan (tercil inferior)",
    "gwr_dj": "GWETROOT dez–jan (tercil inferior)",
    "milho": "milho simulado plantio 1/out com rend. relativo < 0,6",
}


def eh_ruim(alvo, v, lim):
    return v < 0.6 if alvo == "milho" else v <= lim


def analisar(alvo, chave_fase):
    L = [r for r in T if r[alvo] is not None]
    vals = [r[alvo] for r in L]
    lim = None if alvo == "milho" else tercil_inferior(vals)
    o = np.array([eh_ruim(alvo, r[alvo], lim) for r in L], float)
    fases = [r[chave_fase] for r in L]
    res = dict(alvo=alvo, fase=chave_fase, n=len(L), base=float(o.mean()), limiar=lim, por_fase={})
    for f in ("nina", "neutro", "nino"):
        idx = [i for i, x in enumerate(fases) if x == f]
        res["por_fase"][f] = dict(n=len(idx), ruins=int(o[idx].sum()), p=float(o[idx].mean()) if idx else None,
                                  anos=[L[i]["Y"] for i in idx if o[i]],
                                  media_alvo=float(np.mean([vals[i] for i in idx])) if idx else None)
    a, b = res["por_fase"]["nina"], res["por_fase"]["nino"]
    res["fisher_nina_maior_que_nino"] = float("nan") if o.sum()==0 else fisher_uni(a["ruins"], a["n"], b["ruins"], b["n"]) if a["n"] and b["n"] else None
    # Brier LOO: previsão = frequência na mesma fase (sem o ano i); limiar recalculado sem o ano i
    pf, pc, ob = [], [], []
    for i in range(len(L)):
        outros = [j for j in range(len(L)) if j != i]
        lim_i = None if alvo == "milho" else tercil_inferior([vals[j] for j in outros])
        oo = np.array([eh_ruim(alvo, vals[j], lim_i) for j in outros], float)
        mesma = [k for k, j in enumerate(outros) if fases[j] == fases[i]]
        pc.append(oo.mean())
        pf.append(oo[mesma].mean() if mesma else oo.mean())
        ob.append(float(eh_ruim(alvo, vals[i], lim_i)))
    bf, bc = brier(pf, ob), brier(pc, ob)
    res["brier_fase"], res["brier_clim"], res["bss"] = bf, bc, (1 - bf / bc) if bc else float("nan")
    # suavizada (encolhe a frequência da fase para a climatologia com peso de 3 anos)
    ps = []
    for i in range(len(L)):
        outros = [j for j in range(len(L)) if j != i]
        lim_i = None if alvo == "milho" else tercil_inferior([vals[j] for j in outros])
        oo = np.array([eh_ruim(alvo, vals[j], lim_i) for j in outros], float)
        mesma = [k for k, j in enumerate(outros) if fases[j] == fases[i]]
        ps.append((oo[mesma].sum() + 3 * oo.mean()) / (len(mesma) + 3))
    res["bss_suavizada"] = (1 - brier(ps, ob) / bc) if bc else float("nan")
    # metades
    met = {}
    for nome, (a0, a1) in {"1981-2004": (1981, 2004), "2005-2024": (2005, 2024)}.items():
        idx = [i for i, r in enumerate(L) if a0 <= r["Y"] <= a1]
        met[nome] = {f: (int(sum(o[i] for i in idx if fases[i] == f)), sum(1 for i in idx if fases[i] == f))
                     for f in ("nina", "neutro", "nino")}
    res["metades"] = met
    # correlação contínua ONI × alvo (Spearman)
    chave_oni = "oni_ndj" if chave_fase == "fase_ndj" else "oni_jas"
    rho, p = stats.spearmanr([r[chave_oni] for r in L], vals)
    res["spearman_oni"] = (float(rho), float(p))
    return res


saida = dict(local=D["nome"], resultados=[])
for alvo in ALVOS:
    for cf in ("fase_ndj", "fase_jas", "fase_aso"):
        saida["resultados"].append(analisar(alvo, cf))

# conferência externa: IBGE PAM milho (microrregião SMO), safra Y -> ano de colheita Y+1
if local == "smo":
    prod, anom = pam()
    conf = {}
    for cf in ("fase_ndj", "fase_jas"):
        g = {}
        for r in T:
            a = anom.get(r["Y"] + 1)
            if a is None: continue
            g.setdefault(r[cf], []).append((r["Y"], a))
        conf[cf] = {f: dict(n=len(v), quebras=sum(1 for _, a in v if a < 0.8), media=float(np.mean([a for _, a in v])),
                            anos_quebra=[y for y, a in v if a < 0.8]) for f, v in g.items()}
    saida["ibge_por_fase"] = conf
    saida["ibge_anomalias"] = {str(k): round(v, 2) for k, v in sorted(anom.items())}

saida["anos"] = [{k: (round(v, 3) if isinstance(v, float) else v) for k, v in r.items()} for r in T]
(AQUI / "resultados").mkdir(exist_ok=True)
json.dump(saida, open(AQUI / f"resultados/a2_1_{local}.json", "w"), ensure_ascii=False, indent=1)

print(D["nome"])
for r in saida["resultados"]:
    pf = r["por_fase"]
    s = " | ".join(f"{f}: {pf[f]['ruins']}/{pf[f]['n']}={pf[f]['p']:.2f}" if pf[f]["n"] else f"{f}: -" for f in ("nina", "neutro", "nino"))
    print(f"{r['alvo']:8s} {r['fase']:8s} base={r['base']:.2f} {s} | Fisher p={r['fisher_nina_maior_que_nino']:.3f} "
          f"BSS={r['bss']:+.3f} BSSsuav={r['bss_suavizada']:+.3f} rho={r['spearman_oni'][0]:+.2f} (p={r['spearman_oni'][1]:.2f})")
    if r["fase"] == "fase_ndj": print("   metades:", r["metades"], " anos ruins La Niña:", pf["nina"]["anos"], "El Niño:", pf["nino"]["anos"])
if local == "smo":
    print("IBGE:", json.dumps(saida["ibge_por_fase"], ensure_ascii=False))
