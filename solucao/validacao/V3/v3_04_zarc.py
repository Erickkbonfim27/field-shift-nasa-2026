#!/usr/bin/env python3
"""V3-04: conferência com o ZARC 2026/27 de SMO. Recalcula o ISNA por fase com os critérios do ZARC e compara a ordem de risco milho x sorgo por CAD.

Critérios (Portaria SPA/MAPA 236/2026 milho 1ª safra SC; Portaria 128/2023 e 315/2026 sorgo forrageiro SC):
  milho grupo I (fases 25/35/40/20 dias): evento se ISNA_I < 0,70 ou ISNA_III < 0,55
  sorgo grupo I (fases 20/30/25/35 dias, 110 d): evento se ISNA_I < 0,70 ou ISNA_II < 0,60 ou ISNA_III < 0,40
  risco ZARC = fração de anos com evento: <=20% -> 20; <=30% -> 30; <=40% -> 40; senão "não indicado".
Nosso ISNA usa nosso Kc e nosso balde (ZARC usa o SARRA); só a ordem e a classe são comparáveis.
ZARC SMO (resumo da A4, CSV oficial): ver sessoes/A4/zarc_smo_resumo.txt.
"""
import sys, json, datetime as dt
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
import modelo_v3 as V
AQUI = Path(__file__).resolve().parent

FASES = {"milho": (25, 35, 40, 20), "sorgo": (20, 30, 25, 35)}


def isna_zarc(crop, cad, plantio):
    fases = FASES[crop]; n = sum(fases)
    i0 = (plantio - V.D0).days
    if i0 - 60 < 0 or i0 + n >= V.N: return None
    s = cad
    for i in range(i0 - 60, i0):
        e = V.ET0[i]
        if e != e: return None
        s = min(cad, s + V.RAIN[i]); s = max(0.0, s - 0.3 * e * min(1.0, s / (0.5 * cad)))
    lim = (1 - V.P_DEP) * cad
    eta = [0.0] * 4; etc = [0.0] * 4
    bounds = np.cumsum(fases)
    for k in range(n):
        i = i0 + k; e = V.ET0[i]
        if e != e: return None
        ec = V.kc_dia(crop, k, n, 1.0) * e
        s = min(cad, s + V.RAIN[i])
        ea = ec * min(1.0, s / lim); s = max(0.0, s - ea)
        j = int(np.searchsorted(bounds, k, side="right"))
        eta[j] += ea; etc[j] += ec
    return [a / b for a, b in zip(eta, etc)]


def evento(crop, isna):
    if crop == "milho": return isna[0] < 0.70 or isna[2] < 0.55
    return isna[0] < 0.70 or isna[1] < 0.60 or isna[2] < 0.40


def classe(p):
    return 20 if p <= 0.20 else 30 if p <= 0.30 else 40 if p <= 0.40 else 99


# CAD de cada classe: milho AD1..AD6 (ZARC SC, Ze 60 cm); sorgo tipos 1..3
CAD_MILHO = {"AD1": 24.0, "AD2": 31.8, "AD3": 41.4, "AD4": 54.6, "AD5": 72.6, "AD6": 95.4}
CAD_SORGO = {"tipo1": 42.0, "tipo2": 66.0, "tipo3": 90.0}
# ZARC SMO 2026/27 (grupo I, resumo A4): risco % por decêndio de plantio 11/09, 21/09, 01/10, 11/10, 21/10 (0 = não indicado)
ZARC_MILHO = {"AD1": [0, 0, 0, 0, 0], "AD2": [40, 0, 0, 0, 40], "AD3": [30, 30, 30, 30, 30], "AD4": [20, 30, 30, 30, 30], "AD5": [20, 20, 20, 20, 20], "AD6": [20, 20, 20, 20, 20]}
ZARC_SORGO = {"tipo1": [20] * 5, "tipo2": [20] * 5, "tipo3": [20] * 5}
DATAS = [(9, 11), (9, 21), (10, 1), (10, 11), (10, 21)]
out = {"milho": {}, "sorgo": {}}
for crop, cads, zarc in (("milho", CAD_MILHO, ZARC_MILHO), ("sorgo", CAD_SORGO, ZARC_SORGO)):
    for nome, cad in cads.items():
        pdate = []
        for (m, d) in DATAS:
            ev = []
            for a in V.SAFRAS:
                r = isna_zarc(crop, cad, dt.date(a, m, d))
                if r is None: continue
                ev.append(evento(crop, r))
            pdate.append(float(np.mean(ev)))
        out[crop][nome] = dict(cad=cad, p_evento=pdate, classe_modelo=[classe(p) for p in pdate], zarc=zarc[nome])
        print(f"{crop:5s} {nome} CAD {cad:5.1f} | P(evento) por data {['%.2f' % p for p in pdate]} | classe nossa {[classe(p) for p in pdate]} | ZARC {zarc[nome]}")
# comparação de ordem: em cada CAD comum, sorgo mais seguro que milho?
comp = []
for sn, cs in CAD_SORGO.items():
    for mn, cm in CAD_MILHO.items():
        if abs(cs - cm) / cm < 0.15:
            ps = np.mean(out["sorgo"][sn]["p_evento"]); pm = np.mean(out["milho"][mn]["p_evento"])
            zs = np.mean([x for x in out["sorgo"][sn]["zarc"] if x]); zm_l = [x for x in out["milho"][mn]["zarc"] if x]
            comp.append(dict(sorgo=sn, milho=mn, p_sorgo=float(ps), p_milho=float(pm), zarc_sorgo=float(zs), zarc_milho=float(np.mean(zm_l)) if zm_l else None))
out["comparacao_mesmo_cad"] = comp
for c in comp: print("mesmo CAD:", c)
# correlação de ordem entre P(evento) nossa e classe ZARC (milho, datas indicadas)
xs, ys = [], []
for nome, r in out["milho"].items():
    for p, z in zip(r["p_evento"], r["zarc"]):
        if z: xs.append(p); ys.append(z)
from scipy.stats import spearmanr
rho = spearmanr(xs, ys)
out["spearman_milho_p_evento_x_zarc"] = dict(rho=float(rho.statistic), p=float(rho.pvalue), n=len(xs))
print("Spearman (milho) P(evento) nosso x risco ZARC:", out["spearman_milho_p_evento_x_zarc"])
json.dump(out, open(AQUI / "res_04_zarc.json", "w"), indent=1)
