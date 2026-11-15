#!/usr/bin/env python3
"""B5-1: NDVI de janeiro (MODIS MOD13Q1, 250 m) em 9x9 km em volta de São Miguel do Oeste.

Regra definida antes de comparar com as perdas:
  - usa as composições de 16 dias com data em janeiro (floração e enchimento do milho plantado em set-out);
  - tira os pixels urbanos ou de água (NDVI médio de janeiro < 0,45 em todas as safras);
  - dos que sobram, fica com a metade que mais varia entre os anos (lavoura e pasto respondem ao clima; mata e cidade não);
  - índice da safra = média desses pixels; marca o ano se ficar no 1º quartil.
Saída: ndvi_smo.csv
"""
import json, csv, statistics as st
from pathlib import Path

AQUI = Path(__file__).resolve().parent
jan = {}
for f in sorted((AQUI / "modis").glob("smo_*.json")):
    d = json.load(open(f))
    if "subset" not in d:
        continue
    safra = int(f.stem.split("_")[1])
    camadas = [s["data"] for s in d["subset"] if s["calendar_date"][5:7] == "01"]
    if not camadas:
        continue
    n = len(camadas[0])
    px = []
    for i in range(n):
        v = [c[i] * 0.0001 for c in camadas if c[i] > -2000]
        px.append(st.mean(v) if v else None)
    jan[safra] = px

safras = sorted(jan)
n = len(jan[safras[0]])
media = [st.mean([jan[s][i] for s in safras if jan[s][i] is not None]) for i in range(n)]
dp = [st.pstdev([jan[s][i] for s in safras if jan[s][i] is not None]) for i in range(n)]
validos = [i for i in range(n) if media[i] >= 0.45]
validos.sort(key=lambda i: -dp[i])
sel = validos[: len(validos) // 2]
idx = {s: st.mean([jan[s][i] for i in sel if jan[s][i] is not None]) for s in safras}
m = st.mean(idx.values())
q1 = sorted(idx.values())[len(idx) // 4]
with open(AQUI / "ndvi_smo.csv", "w") as f:
    w = csv.writer(f); w.writerow(["safra", "ndvi_jan", "anomalia", "marca"])
    for s in safras:
        w.writerow([s, round(idx[s], 4), round(idx[s] - m, 4), int(idx[s] < q1)])
print(f"{len(safras)} safras, {n} pixels, {len(validos)} não urbanos, {len(sel)} usados; média {m:.3f}; 1º quartil {q1:.3f}")
for s in safras:
    print(s, round(idx[s], 3), f"{idx[s]-m:+.3f}", "MARCA" if idx[s] < q1 else "")
