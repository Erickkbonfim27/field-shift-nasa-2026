#!/usr/bin/env python3
"""B5-3: semanas de risco de doença na cebola (Ituporanga) com NASA POWER, contra o IBGE/PAM.

Dia de risco: PRECTOTCORR >= 2 mm, RH2M >= 85%, 10 <= T2M <= 24 °C.
Semana de risco: >= 4 dias de risco em 7 (semanas fixas de 1/ago a 30/nov).
Ano de quebra: rendimento < 70% da tendência 1990-2024 (80% se der menos de 3 anos).
"""
import json, csv, datetime as dt, statistics as st
from pathlib import Path

AQUI = Path(__file__).resolve().parent
P = json.load(open(AQUI.parent.parent / "dados/power_ituporanga.json"))["properties"]["parameter"]


def k(d): return d.strftime("%Y%m%d")


def dia_risco(d):
    x = k(d)
    return P["PRECTOTCORR"][x] >= 2 and P["RH2M"][x] >= 85 and 10 <= P["T2M"][x] <= 24


linhas = []
for ano in range(1990, 2025):
    ini, fim = dt.date(ano, 8, 1), dt.date(ano, 11, 30)
    semanas, s = [], ini
    while s + dt.timedelta(6) <= fim:
        n = sum(dia_risco(s + dt.timedelta(i)) for i in range(7))
        semanas.append(n)
        s += dt.timedelta(7)
    chuva = sum(max(0, P["PRECTOTCORR"][k(ini + dt.timedelta(i))]) for i in range((fim - ini).days + 1))
    dias = sum(dia_risco(ini + dt.timedelta(i)) for i in range((fim - ini).days + 1))
    linhas.append(dict(ano=ano, semanas_risco=sum(1 for n in semanas if n >= 4), dias_risco=dias,
                       chuva_ago_nov=round(chuva, 1), n_semanas=len(semanas)))

pam = {}
for r in csv.DictReader(open(AQUI / "pam_ibge.csv")):
    if r["municipio"] == "Ituporanga (SC)" and r["produto"] == "Cebola":
        pam[int(r["ano"])] = float(r["rend_kg_ha"])
anos = sorted(pam)
mx, my = st.mean(anos), st.mean(pam.values())
b = sum((a - mx) * (pam[a] - my) for a in anos) / sum((a - mx) ** 2 for a in anos)
a0 = my - b * mx
rel = {a: pam[a] / (a0 + b * a) for a in anos}
corte = 0.70
perda = {a for a in anos if rel[a] < corte}
if len(perda) < 3:
    corte = 0.80
    perda = {a for a in anos if rel[a] < corte}

L = {x["ano"]: x for x in linhas}
def q3(v): return sorted(v)[(3 * len(v)) // 4]
qs, qc = q3([x["semanas_risco"] for x in linhas]), q3([x["chuva_ago_nov"] for x in linhas])
regras = {
    "painel: semanas de risco no quartil de cima": {a for a in anos if L[a]["semanas_risco"] >= qs},
    "base: chuva ago-nov no quartil de cima": {a for a in anos if L[a]["chuva_ago_nov"] >= qc},
}
with open(AQUI / "indicadores_cebola_itu.csv", "w") as f:
    w = csv.DictWriter(f, fieldnames=list(linhas[0].keys()) + ["rend_pam", "pct_tendencia"]); w.writeheader()
    for x in linhas: w.writerow({**x, "rend_pam": int(pam[x["ano"]]), "pct_tendencia": round(rel[x["ano"]], 3)})

print(f"Ituporanga · cebola · 1990-2024 · tendência {a0 + b*1990:.0f} -> {a0 + b*2024:.0f} kg/ha · corte {corte:.0%}")
print("Anos de quebra:", sorted(perda))
print(f"Semanas vermelhas por safra: média {st.mean(x['semanas_risco'] for x in linhas):.1f} de {linhas[0]['n_semanas']} (limiar do quartil: {qs})")
for nome, s in regras.items():
    tp, fp = len(s & perda), len(s - perda)
    print(f"{nome:45s} marca {len(s):2d} acertos {tp} falsos {fp} recall {tp/len(perda):.0%} precisão {tp/len(s):.0%} {sorted(s)}")
print("\nano rend %tend quebra? semanas dias chuva")
for a in anos:
    x = L[a]; print(a, int(pam[a]), f"{rel[a]:.0%}", "QUEBRA" if a in perda else "", x["semanas_risco"], x["dias_risco"], x["chuva_ago_nov"])

def rank(v):
    o = sorted(range(len(v)), key=lambda i: v[i]); r = [0] * len(v)
    for j, i in enumerate(o): r[i] = j
    return r
n = len(anos); rb = rank([rel[a] for a in anos])
for nome, campo in [("semanas", "semanas_risco"), ("chuva", "chuva_ago_nov")]:
    ra = rank([-L[a][campo] for a in anos])
    rho = 1 - 6 * sum((p - q) ** 2 for p, q in zip(ra, rb)) / (n * (n * n - 1))
    print(f"Spearman (-{nome}) x rendimento relativo: {rho:.2f}")
