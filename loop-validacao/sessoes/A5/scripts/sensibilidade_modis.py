"""A5-3, sensibilidade NÃO pré-registrada: tira a tendência do NDVI também e repete; e só 2010-2025."""
import json, sys
import numpy as np
from scipy.stats import spearmanr
r = json.load(open(sys.argv[1]))
anos = np.array([int(a) for a in r["indicador"]]); ind = np.array(list(r["indicador"].values())); an = np.array(list(r["anom_rend"].values()))
ind_dt = ind - np.polyval(np.polyfit(anos, ind, 1), anos)
q = an <= -0.15
for nome, x, sel in (("NDVI sem tendência, 2000-2025", ind_dt, anos >= 2000), ("NDVI sem tendência, 2010-2025", ind_dt, anos >= 2010),
                     ("NDVI bruto, 2010-2025", ind, anos >= 2010)):
    rho, p = spearmanr(x[sel], an[sel])
    baixo = x[sel] <= np.percentile(x[sel], 100 / 3)
    print(f"{nome}: rho={rho:.2f} p={p:.2f}; terço mais baixo pega {(q[sel] & baixo).sum()} de {q[sel].sum()} quebras")
print("tendência do NDVI: %.2f%% por ano" % (100 * np.polyfit(anos, ind, 1)[0]))
