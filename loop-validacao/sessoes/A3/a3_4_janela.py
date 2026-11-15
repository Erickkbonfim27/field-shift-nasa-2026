"""A3-4 Janela de preparo: P(>=1 dia com chuva >= 25 mm nos 45 dias apos o preparo), NASA POWER 1981-2025, Ituporanga."""
import json, numpy as np, pandas as pd
from scipy.stats import spearmanr
p = json.load(open('../../dados/power_ituporanga.json'))['properties']['parameter']['PRECTOTCORR']
s = pd.Series({pd.Timestamp(k): v for k, v in p.items()}).replace(-999, np.nan)
datas = [(5, 1), (5, 15), (6, 1), (6, 15), (7, 1), (7, 15), (8, 1)]
back = [931.0, 828.0, 504.9, 386.4, 455.0, 440.3, 565.9, 574.8, 835.5, 869.0, 483.1, 675.4]
def win(y, m, d): t0 = pd.Timestamp(y, m, d); return s[t0:t0 + pd.Timedelta(days=44)]
res = {}
def prob(years):
    out = []
    for m, d in datas:
        hits = [int((win(y, m, d) >= 25).any()) for y in years]
        out.append(np.mean(hits))
    return np.array(out)
Y = list(range(1981, 2026)); pa = prob(Y)
res['P_dia_25mm_45d'] = {f'{d:02d}/{m:02d}': round(float(x), 2) for (m, d), x in zip(datas, pa)}
res['J1_diferenca_pp'] = round(float((pa.max() - pa.min()) * 100), 1)
# chuva media e soma de P^2 na janela (forma de erosividade), para ordem
er = []
for m, d in datas:
    er.append(np.mean([(win(y, m, d) ** 2).sum() for y in Y]))
res['soma_P2_media_janela'] = [round(float(x)) for x in er]
# Back por janela: erosividade mensal (gauge) ponderada pelos dias de cada mes na janela
bw = []
for m, d in datas:
    dd = pd.date_range(pd.Timestamp(2001, m, d), periods=45)
    bw.append(sum(back[x.month - 1] / x.days_in_month for x in dd))
res['back_EI30_janela'] = [round(x) for x in bw]
res['J2_spearman_prob_vs_back'] = round(float(spearmanr(pa, bw).correlation), 2)
res['J2_spearman_somaP2_vs_back'] = round(float(spearmanr(er, bw).correlation), 2)
p1, p2 = prob(range(1981, 2004)), prob(range(2004, 2026))
lab = [f'{d:02d}/{m:02d}' for m, d in datas]
res['J3_melhor_pior_1981_2003'] = [lab[int(p1.argmin())], lab[int(p1.argmax())]]
res['J3_melhor_pior_2004_2025'] = [lab[int(p2.argmin())], lab[int(p2.argmax())]]
res['P_1981_2003'] = [round(float(x), 2) for x in p1]; res['P_2004_2025'] = [round(float(x), 2) for x in p2]
# IC aproximado (binomial) da diferenca melhor-pior
n = len(Y); se = np.sqrt(pa.max() * (1 - pa.max()) / n + pa.min() * (1 - pa.min()) / n)
res['J1_IC95_pp'] = [round(float((pa.max() - pa.min() - 1.96 * se) * 100), 1), round(float((pa.max() - pa.min() + 1.96 * se) * 100), 1)]
json.dump(res, open('a3_4_resultado.json', 'w'), indent=1, ensure_ascii=False)
for k, v in res.items(): print(k, v)
