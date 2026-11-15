"""A3-2 Nota de saude do solo (0-100) por talhao (bloco 50 m) e ano, 2019-2024.
nota = 100 - [60*min(dias_descobertos/180,1) + 25*min(declive/45,1) + 15*(1 - umid_norm)]
dias_descobertos: dias com NDVI < 0.30 no ano (Sentinel-2). declive: SRTM (%). umid: GWETTOP medio anual do NASA POWER
normalizado entre anos (o mesmo para todos os talhoes: grade de ~50 km)."""
import json, numpy as np, pandas as pd
from scipy.stats import spearmanr
d = np.load('ndvi_mensal.npz'); b = np.load('a3_1_blocos.npz')
months = pd.PeriodIndex(d['months'], freq='M'); ndays = np.array([m.days_in_month for m in months])
bare_b, slope_b, crop_b, forest_b = b['bare_b'], b['slope_b'], b['crop_b'], b['forest_b']
yrs = list(range(2019, 2025))
bd = np.stack([(bare_b[months.year == y] * ndays[months.year == y][:, None, None]).sum(0) for y in yrs])   # ano x bloco
gw = json.load(open('../../dados/power_ituporanga.json'))['properties']['parameter']['GWETTOP']
g = pd.Series({pd.Timestamp(k): v for k, v in gw.items()}).replace(-999, np.nan)
gy = np.array([g[str(y)].mean() for y in yrs]); gn = (gy - gy.min()) / (gy.max() - gy.min())
nota = 100 - (60 * np.minimum(bd / 180, 1) + 25 * np.minimum(slope_b / 45, 1)[None] + 15 * (1 - gn)[:, None, None])
nota_decl = 100 - 25 * np.minimum(slope_b / 45, 1)          # linha de base: so declive
res = {'GWETTOP_anual': dict(zip(yrs, gy.round(3).tolist()))}
# S1 ICC(1) nos talhoes de lavoura
X = nota[:, crop_b].T                                         # n x anos
k = X.shape[1]; gm = X.mean(); msb = k * ((X.mean(1) - gm) ** 2).sum() / (X.shape[0] - 1)
msw = ((X - X.mean(1, keepdims=True)) ** 2).sum() / (X.shape[0] * (k - 1))
res['S1_ICC'] = round(float((msb - msw) / (msb + (k - 1) * msw)), 2)
Xb = bd[:, crop_b].T; gmb = Xb.mean(); msb2 = k * ((Xb.mean(1) - gmb) ** 2).sum() / (Xb.shape[0] - 1)
msw2 = ((Xb - Xb.mean(1, keepdims=True)) ** 2).sum() / (Xb.shape[0] * (k - 1))
res['S1_ICC_so_dias_descobertos'] = round(float((msb2 - msw2) / (msb2 + (k - 1) * msw2)), 2)
res['corr_ano_a_ano_dias_descobertos'] = [round(float(np.corrcoef(Xb[:, i], Xb[:, i + 1])[0, 1]), 2) for i in range(k - 1)]
# S2 sanidade
res['S2_mediana_nota_mata'] = round(float(np.median(nota[:, forest_b])), 1)
res['S2_mediana_nota_lavoura'] = round(float(np.median(nota[:, crop_b])), 1)
# S3 fracao 'tipo plantio direto' (<= 60 dias descobertos/ano, media dos anos)
mbd = bd.mean(0)
res['S3_frac_lavoura_ate_60_dias'] = round(float((mbd[crop_b] <= 60).mean()), 2)
res['dias_descobertos_lavoura_p10_p50_p90'] = [round(float(x)) for x in np.percentile(mbd[crop_b], [10, 50, 90])]
res['hist_dias_descobertos_lavoura'] = np.histogram(mbd[crop_b], bins=[0, 15, 30, 45, 60, 90, 120, 180, 366])[0].tolist()
# S4 ordem nota completa vs so declive
res['S4_spearman_nota_vs_so_declive'] = round(float(spearmanr(nota.mean(0)[crop_b], nota_decl[crop_b]).correlation), 2)
res['S4_spearman_nota_vs_dias_descobertos'] = round(float(spearmanr(nota.mean(0)[crop_b], -mbd[crop_b]).correlation), 2)
res['parcela_variancia_nota_lavoura_por_termo'] = {
    'descoberto': round(float(np.var(60 * np.minimum(bd / 180, 1)[:, crop_b])), 1),
    'declive': round(float(np.var(25 * np.minimum(slope_b / 45, 1)[crop_b])), 1),
    'umidade_POWER': round(float(np.var(15 * (1 - gn))), 1)}
res['nota_media_lavoura_por_ano'] = dict(zip(yrs, [round(float(x), 1) for x in nota[:, crop_b].mean(1)]))
res['dias_descobertos_medios_lavoura_por_ano'] = dict(zip(yrs, [round(float(x)) for x in bd[:, crop_b].mean(1)]))
json.dump(res, open('a3_2_resultado.json', 'w'), indent=1, ensure_ascii=False)
for kk, v in res.items(): print(kk, v)
np.savez_compressed('a3_2_nota.npz', nota=nota, bd=bd)
