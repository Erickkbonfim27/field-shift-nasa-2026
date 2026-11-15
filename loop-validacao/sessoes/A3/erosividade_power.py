"""C1: erosividade mensal so com NASA POWER (PRECTOTCORR diario) vs tabela de Back et al. (2023), Ituporanga.
Metodo diario (independente do de Back): dia erosivo P >= 12.7 mm; EI_dia = a * P^1.81 (Richardson et al. 1983).
a nao e calibrado com Back: so a FORMA mensal entra no criterio (Spearman, top-4). Saida: erosividade_mensal.json"""
import json, numpy as np, pandas as pd, sys
f = sys.argv[1] if len(sys.argv) > 1 else '../../dados/power_ituporanga.json'
p = json.load(open(f))['properties']['parameter']['PRECTOTCORR']
s = pd.Series({pd.Timestamp(k): v for k, v in p.items()}).replace(-999, np.nan)
s = s['1981':'2021']
A = 0.41  # coeficiente tipico da literatura (Richardson 1983 ~0.41 no inverno-verao medio). Nao muda a forma.
ei = (A * s.where(s >= 12.7, 0) ** 1.81)
mon_ei = ei.groupby([ei.index.year, ei.index.month]).sum().unstack()      # ano x mes
mon_p = s.groupby([s.index.year, s.index.month]).sum().unstack()
P = mon_p.sum(axis=1)
# Indice de Fournier modificado por mes (p^2/P), mesma forma usada por Back, mas com chuva do POWER
fourn = (mon_p ** 2).div(P, axis=0)
back = [931.0, 828.0, 504.9, 386.4, 455.0, 440.3, 565.9, 574.8, 835.5, 869.0, 483.1, 675.4]  # Back et al. 2023, Tab. 3
back_p = [166.0,154.6,116.5,93.0,103.0,103.6,116.1,117.0,152.4,153.5,109.8,137.2]
from scipy.stats import spearmanr
r = {}
for nome, m in [('diario_P^1.81', mon_ei.mean().values), ('fournier_power', fourn.mean().values)]:
    rho = spearmanr(m, back).correlation
    top4_b = set(np.argsort(back)[-4:] + 1); top4_m = set(np.argsort(m)[-4:] + 1)
    r[nome] = dict(mensal=[round(x, 1) for x in m], anual=round(float(m.sum()), 0), spearman=round(float(rho), 2),
                   top4_back=sorted(int(i) for i in top4_b), top4_power=sorted(int(i) for i in top4_m), acertos_top4=len(top4_b & top4_m),
                   frac_out_fev=round(float(m[[9, 10, 11, 0, 1]].sum() / m.sum()), 2))
r['chuva_mensal_power_media'] = [round(x, 1) for x in mon_p.mean().values]
r['chuva_mensal_back'] = back_p
r['spearman_chuva'] = round(float(spearmanr(mon_p.mean().values, back_p).correlation), 2)
r['chuva_anual_power'] = round(float(P.mean()), 0)
r['back_frac_out_fev'] = round(sum(back[i] for i in [9, 10, 11, 0, 1]) / sum(back), 2)
r['anual_por_ano_diario'] = {int(y): round(float(v), 0) for y, v in mon_ei.sum(axis=1).items()}
# p95 da chuva diaria (mostra suavizacao da grade de 50 km)
r['p99_chuva_diaria_mm'] = round(float(s[s > 0].quantile(0.99)), 1)
r['max_chuva_diaria_mm'] = round(float(s.max()), 1)
json.dump(r, open('erosividade_mensal.json', 'w'), indent=1)
for k, v in r.items():
    if k != 'anual_por_ano_diario': print(k, v)
