#!/usr/bin/env python3
"""B5: compara os indicadores do modelo com os anos de perda do IBGE/PAM (só conferência).

Ano de perda (definido antes do teste) = rendimento < 70% da tendência linear 1990-2024.
Uso: python3 avaliar.py [smo|itu] [arquivo_indicadores]
"""
import csv, sys, statistics as st
from pathlib import Path

AQUI = Path(__file__).resolve().parent
local = sys.argv[1] if len(sys.argv) > 1 else "smo"
arq = sys.argv[2] if len(sys.argv) > 2 else f"indicadores_{local}.csv"
MUN = {"smo": "São Miguel do Oeste (SC)", "itu": "Ituporanga (SC)"}[local]
PROD = "Milho (em grão)"

import os
REG = os.environ.get("REGIAO")   # ex.: "São Miguel do Oeste - SC" (microrregião) para checar a escala
pam = {}
if REG:
    MUN = REG
    for r in csv.DictReader(open(AQUI / "pam_regiao.csv")):
        if r["regiao"] == REG and r["produto"] == PROD:
            pam[int(r["ano"])] = float(r["rend_kg_ha"])
else:
    for r in csv.DictReader(open(AQUI / "pam_ibge.csv")):
        if r["municipio"] == MUN and r["produto"] == PROD and r["rend_kg_ha"] not in ("", "-", "...", "None"):
            pam[int(r["ano"])] = float(r["rend_kg_ha"])
anos = sorted(a for a in pam if 1990 <= a <= 2024)
x = anos; yv = [pam[a] for a in anos]
mx, my = st.mean(x), st.mean(yv)
b = sum((xi - mx) * (yi - my) for xi, yi in zip(x, yv)) / sum((xi - mx) ** 2 for xi in x)
a0 = my - b * mx
rel = {a: pam[a] / (a0 + b * a) for a in anos}
perda = {a for a in anos if rel[a] < 0.70}

ind = {int(r["safra"]): r for r in csv.DictReader(open(AQUI / arq))}
anos = [a for a in anos if a in ind]


def q1(v): return sorted(v)[len(v) // 4]


chuva = {a: float(ind[a]["chuva_out_fev"]) for a in anos}
gw = {a: float(ind[a]["gwroot_dez_jan"]) for a in anos}
cq1, gq1 = q1(list(chuva.values())), q1(list(gw.values()))

regras = {
    "laudo: y_mun < 0,70 (balanço hídrico POWER)": {a for a in anos if float(ind[a]["y_mun"]) < 0.70},
    "base: chuva out-fev < 1º quartil": {a for a in anos if chuva[a] < cq1},
    "extra: GWETROOT dez-jan < 1º quartil": {a for a in anos if gw[a] < gq1},
    "alerta B5-2: modelo até o dia 80": {a for a in anos if ind[a]["alerta_dia"] != ""},
    "base B5-2: olho do agricultor (15 dias < 5 mm)": {a for a in anos if ind[a]["olho_dia"] != ""},
}

print(f"{MUN} · {PROD} · {anos[0]}-{anos[-1]} ({len(anos)} safras) · tendência {a0 + b * anos[0]:.0f} -> {a0 + b * anos[-1]:.0f} kg/ha")
print("Anos de perda (PAM < 70% da tendência):", sorted(perda), f"= {len(perda)} de {len(anos)} (taxa {len(perda)/len(anos):.0%})")
print()
print(f"{'regra':52s} marca acertos alarmes_falsos recall precisão")
res = {}
for nome, s in regras.items():
    tp = len(s & perda); fp = len(s - perda)
    rec = tp / len(perda) if perda else 0; prec = tp / len(s) if s else 0
    res[nome] = (s, tp, fp, rec, prec)
    print(f"{nome:52s} {len(s):5d} {tp:7d} {fp:14d} {rec:6.0%} {prec:8.0%}   marcados={sorted(s)}")
print()
print("Por safra: ano, rend PAM, % da tendência, perda?, y_mun, chuva, alerta_dia, olho_dia")
for a in anos:
    print(a, int(pam[a]), f"{rel[a]:.0%}", "PERDA" if a in perda else "", ind[a]["y_mun"], chuva[a], ind[a]["alerta_dia"], ind[a]["olho_dia"])

# correlação de Spearman entre y_mun e rendimento relativo
def rank(v):
    o = sorted(range(len(v)), key=lambda i: v[i]); r = [0] * len(v)
    for k, i in enumerate(o): r[i] = k
    return r
ra, rb = rank([float(ind[a]["y_mun"]) for a in anos]), rank([rel[a] for a in anos])
n = len(anos)
rho = 1 - 6 * sum((p - q) ** 2 for p, q in zip(ra, rb)) / (n * (n * n - 1))
rc = rank([chuva[a] for a in anos])
rho_c = 1 - 6 * sum((p - q) ** 2 for p, q in zip(rc, rb)) / (n * (n * n - 1))
print(f"\nSpearman y_mun x rendimento relativo: {rho:.2f} | chuva out-fev x rendimento relativo: {rho_c:.2f}")
