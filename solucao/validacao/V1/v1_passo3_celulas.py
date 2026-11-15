#!/usr/bin/env python3
"""Passo 3: confere se a chuva diária do POWER dos pontos novos é diferente da dos pontos já usados
(regra de criterios.md: exclui se a chuva é igual, |dif| < 0,01 mm, em mais de 50% dos dias)."""
import json
from v1_comum import *

USADOS = {"sao_miguel_do_oeste": None, "ituporanga": None, "chapeco": B3 / "power_extra",
          "concordia": B3 / "power_extra", "rio_do_sul": B3 / "power_extra"}
NOVOS = [p.stem.replace("power_", "") for p in sorted(POWER_V1.glob("power_*.json"))]
chuva = {}
for n, pasta in USADOS.items(): chuva[n] = Power(n, pasta).chuva
for n in NOVOS:
    pw = Power(n, POWER_V1); chuva[n] = pw.chuva
    chuva[n + "_coord"] = (pw.lat, pw.lon)

def igual(a, b):
    ks = [k for k in chuva[a] if k in chuva[b] and k >= "19900101"]
    return sum(abs(chuva[a][k] - chuva[b][k]) < 0.01 for k in ks) / len(ks)

out = {}
todos = list(USADOS) + NOVOS
for n in NOVOS:
    m = {o: round(igual(n, o), 3) for o in todos if o != n}
    top = max(m.items(), key=lambda x: x[1])
    out[n] = dict(coord=chuva[n + "_coord"], mais_parecido=top[0], frac_dias_iguais=top[1],
                  iguais_a=[o for o, v in m.items() if v > 0.5])
    print(n, out[n])
json.dump(out, open(V1 / "celulas_identidade.json", "w"), ensure_ascii=False, indent=1)
