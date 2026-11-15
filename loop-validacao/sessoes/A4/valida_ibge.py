#!/usr/bin/env python3
"""Confere anos de perda do milho no modelo com a produtividade do milho no IBGE/PAM (tab. 1612), SMO."""
import json, statistics as st, sys
SOLO = sys.argv[1] if len(sys.argv) > 1 else "argiloso"
d = json.load(open("externo/pam_smo_milho_sorgo.json"))[1:]
pam = {int(r["D3N"]): float(r["V"]) for r in d if r["D2N"].startswith("Rendimento") and r["D4N"].startswith("Milho") and r["V"].replace('.','').isdigit()}
anos = sorted(pam)
# queda: rendimento >= 20% abaixo da mediana dos 5 anos ao redor (exclui o próprio), por causa da tendência tecnológica
queda = {}
for a in anos:
    viz = [pam[b] for b in range(a - 3, a + 4) if b != a and b in pam]
    queda[a] = pam[a] / st.median(viz) - 1
c = json.load(open(f"casos_a4_1_R0.85_{SOLO}_ky1.0_kc1.0_raizNone.json"))
mod = {}
for x in c:
    if x["dec"] in (2, 3, 4, 5, 6):  # plantio 11/set a 21/out (janela usual do milho no Extremo Oeste)
        mod.setdefault(x["safra"], []).append(x["ym"])
ym = {a + 1: st.mean(v) for a, v in mod.items()}  # safra plantada em a é colhida (PAM) em a+1
comuns = [a for a in anos if a in ym]
ruim_ibge = [a for a in comuns if queda[a] <= -0.20]
ruim_mod = [a for a in comuns if ym[a] < 0.70]
print("anos comuns", comuns[0], comuns[-1], len(comuns))
print("quedas IBGE (>=20%):", [(a, round(queda[a], 2), round(ym[a], 2)) for a in ruim_ibge])
print("anos ruins no modelo (y<0,70):", [(a, round(ym[a], 2), round(queda[a], 2)) for a in ruim_mod])
hit = [a for a in ruim_ibge if a in ruim_mod]
print("acertos", len(hit), "de", len(ruim_ibge), "| alarmes falsos", len([a for a in ruim_mod if a not in ruim_ibge]))
xs = [ym[a] for a in comuns]; ys = [queda[a] for a in comuns]
mx, my = st.mean(xs), st.mean(ys)
r = sum((a - mx) * (b - my) for a, b in zip(xs, ys)) / (sum((a - mx) ** 2 for a in xs) * sum((b - my) ** 2 for b in ys)) ** 0.5
print("correlação y_modelo x desvio IBGE: %.2f (n=%d)" % (r, len(comuns)))
json.dump(dict(pam=pam, queda=queda, ym=ym, r=r, ruim_ibge=ruim_ibge, ruim_mod=ruim_mod), open(f"valida_ibge_{SOLO}.json", "w"))
