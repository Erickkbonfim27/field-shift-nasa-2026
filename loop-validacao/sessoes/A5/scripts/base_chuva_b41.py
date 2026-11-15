"""A5-3, linha de base do item 3: índice de chuva set-nov (POWER, como na B4-1) x produtividade de Ituporanga sem tendência."""
import json, sys
import numpy as np
from scipy.stats import spearmanr
POWER, PAM = sys.argv[1], sys.argv[2]
P = json.load(open(POWER))["properties"]["parameter"]["PRECTOTCORR"]
d = json.load(open(PAM))[1:]
rend = {int(r["D3N"]): float(r["V"]) for r in d if r["D2N"].startswith("Rendimento")}
anos = np.array(sorted(rend)); y = np.array([rend[a] for a in anos])
tend = np.polyval(np.polyfit(anos, y, 1), anos); anom = y / tend - 1
chuva = np.array([sum(max(0, v) for k, v in P.items() if int(k[:4]) == a and 9 <= int(k[4:6]) <= 11) for a in anos])
rho, p = spearmanr(chuva, anom)
quebra = anom <= -0.15
alarme = chuva >= np.percentile(chuva, 200 / 3)
print("anos", anos[0], anos[-1], "n", len(anos))
print("quebras (>=15% abaixo da tendência):", list(anos[quebra]))
print(f"chuva set-nov x produtividade Ituporanga: rho={rho:.2f} p={p:.2f}")
print("terço mais chuvoso pega", int((quebra & alarme).sum()), "de", int(quebra.sum()), "quebras")
json.dump(dict(anos=anos.tolist(), anom=anom.round(3).tolist(), chuva=chuva.round(0).tolist(), quebras=anos[quebra].tolist(), rho=round(rho, 2), p=round(p, 3)), open(sys.argv[3], "w"))
