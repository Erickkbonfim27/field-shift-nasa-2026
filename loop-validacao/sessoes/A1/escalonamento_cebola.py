#!/usr/bin/env python3
"""A1-2 (cebola): transplante em 1, 2 ou 3 datas em Ituporanga. Só déficit hídrico (sem excesso de chuva)."""
import json, statistics as st
from modelo_sc import *
CULTURAS["cebola"] = dict(nome="Cebola (transplante)", fases=(15, 25, 60, 30), kc=(0.70, 1.05, 0.75), ky=(0.45, 0.45, 0.8, 0.3), raiz=0.4, geada=False)
L = Local("power_ituporanga.json")
ANOS = list(range(1984, 2025)); J = list(range(16, 25))
def stats(ys):
    ys = sorted(ys); n = len(ys)
    return dict(media=st.mean(ys), pior=ys[0], p10=ys[int(0.1*n)], dp=st.pstdev(ys), anos_perda40=sum(y < 0.6 for y in ys))
S = {d: {a: simular(L, "cebola", "medio", dt.date(a, *dia_meio(d)))["y"] for a in ANOS} for d in J}
chuva_fim = {d: st.mean(sum(L.chuva[dt.date(a, *dia_meio(d)) + dt.timedelta(k)] for k in range(100, 130)) for a in ANOS) for d in J}
for d in J:
    s = stats(S[d].values()); print(f"dec {d}: média {s['media']:.3f} pior {s['pior']:.2f} P10 {s['p10']:.2f} anos<0,6 {s['anos_perda40']}  chuva nos 30 dias finais {chuva_fim[d]:.0f} mm")
best = max(J, key=lambda d: stats(S[d].values())["media"])
for nome, c in (("única melhor", (best,)), ("habitual 15/jul", (20,)), ("2 datas 15/jun+15/jul", (17, 20)), ("3 datas jun+jul+ago", (17, 20, 23))):
    s = stats([st.mean(S[d][a] for d in c) for a in ANOS])
    print(f"{nome:24} {c}: média {s['media']:.3f} pior {s['pior']:.2f} P10 {s['p10']:.2f} dp {s['dp']:.3f} anos<0,6 {s['anos_perda40']}")
piores = sorted(ANOS, key=lambda a: S[20][a])[:5]
print("5 piores anos (15/jul):", [(a, round(S[20][a], 2), [round(S[d][a], 2) for d in (17, 23)]) for a in piores])
# contexto IBGE (não é critério)
d = json.load(open("../B4/ext/pam_cebola_ituporanga.json"))
y = {int(r["D3N"]): float(r["V"]) for r in d[1:] if r["D2C"] == "112" and r["V"].replace('.', '').isdigit()}
an = {a: y[a] / st.median([y[b] for b in range(a-3, a+4) if b in y]) for a in y}
pi = sorted([a for a in an if 1985 <= a <= 2025], key=lambda a: an[a])[:6]
print("6 piores anos IBGE cebola (colheita):", [(a, round(an[a], 2), round(S[20].get(a, float('nan')), 2)) for a in pi])
json.dump({str(k): v for k, v in S.items()}, open("series_cebola.json", "w"))
