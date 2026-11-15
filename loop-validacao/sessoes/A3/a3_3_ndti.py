"""A3-3 Palhada vs solo exposto com NDTI (B11, B12) do Sentinel-2.
Mesma mascara do NDVI (SCL 4/5, cenas >= 30% limpas, filtro de pico). Em cada obs limpa:
 exposto = NDVI < 0.30 e NDTI < 0.09 ; palhada = NDVI < 0.30 e NDTI >= 0.09 ; verde = NDVI >= 0.30.
Dia a dia: classe da obs limpa mais proxima (vizinho mais proximo). Talhao = bloco 5x5 px (50 m)."""
import json, numpy as np, pandas as pd
c = np.load('raw/s2/cubo.npz'); w = np.load('raw/s2/cubo_swir.npz')
assert (c['dates'] == w['dates']).all()
off = c['off']; dates = pd.to_datetime(c['dates'])
VALID = np.isin(c['scl'], [4, 5])
red = c['red'].astype(np.float32) - off[:, None, None]; nir = c['nir'].astype(np.float32) - off[:, None, None]
ndvi = np.where(VALID & (red + nir > 0), (nir - red) / np.maximum(nir + red, 1), np.nan).astype(np.float32); del red, nir
up = lambda a: np.repeat(np.repeat(a, 2, 1), 2, 2)[:, :500, :500]
b11 = up(w['b11']).astype(np.float32) - off[:, None, None]; b12 = up(w['b12']).astype(np.float32) - off[:, None, None]
ndti = np.where(b11 + b12 > 0, (b11 - b12) / np.maximum(b11 + b12, 1), np.nan).astype(np.float32); del b11, b12
T, H, W_ = ndvi.shape; N = H * W_
X = ndvi.reshape(T, N); Z = ndti.reshape(T, N)
cf = (~np.isnan(X)).mean(1); X[cf < 0.30] = np.nan
ar0 = np.arange(T)[:, None]
for _ in range(2):   # mesmo filtro de pico do ndvi_processar.py
    okk = ~np.isnan(X)
    lst = np.maximum.accumulate(np.where(okk, ar0, -1), axis=0); nx = np.flip(np.minimum.accumulate(np.flip(np.where(okk, ar0, T), 0), axis=0), 0)
    pi = np.vstack([np.full((1, N), -1), lst[:-1]]); ni = np.vstack([nx[1:], np.full((1, N), T)])
    Xf0 = np.nan_to_num(X, nan=9.0)
    pv = np.where(pi >= 0, Xf0[np.clip(pi, 0, T-1), np.arange(N)], 9.0); nv = np.where(ni < T, Xf0[np.clip(ni, 0, T-1), np.arange(N)], 9.0)
    X[okk & (X < np.minimum(pv, nv) - 0.15) & (pv < 9) & (nv < 9)] = np.nan
ok = ~np.isnan(X) & ~np.isnan(Z)
THR = float(__import__('sys').argv[1]) if len(__import__('sys').argv) > 1 else 0.09
low = ok & (X < 0.30)
exp_obs = low & (Z < THR); straw_obs = low & (Z >= THR)
d0 = np.load('ndvi_mensal.npz'); cls = d0['cls'].reshape(-1)
crop = cls == 2
mon = dates.month.values
sel = low[:, crop] & np.isin(mon, [5, 6, 7, 8])[:, None]
res = {'limiar_ndti': THR}
res['T1_frac_obs_baixo_ndvi_mai_ago_palhada'] = round(float(straw_obs[:, crop][sel].mean()), 2)
res['ndti_obs_baixo_ndvi_lavoura_p10_p50_p90'] = [round(float(x), 3) for x in np.percentile(Z[:, crop][low[:, crop]], [10, 50, 90])]
res['ndti_obs_verde_lavoura_p50'] = round(float(np.median(Z[:, crop][(ok & (X >= 0.6))[:, crop]])), 3)
res['ndti_urbano_p50'] = round(float(np.nanmedian(Z[:, cls == 0][ok[:, cls == 0]])), 3)
res['hist_ndti_baixo_ndvi_lavoura'] = np.histogram(Z[:, crop][low[:, crop]], bins=np.arange(-0.1, 0.31, 0.02))[0].tolist()
# dias de solo exposto por ano: classe da obs limpa mais proxima
t_obs = (dates - pd.Timestamp('2019-01-01')).days.values
lst = np.maximum.accumulate(np.where(ok, ar0, -1), axis=0); nx = np.flip(np.minimum.accumulate(np.flip(np.where(ok, ar0, T), 0), axis=0), 0)
E8 = exp_obs.astype(np.int8); L8 = low.astype(np.int8); cols = np.arange(N)
yrs = list(range(2019, 2025)); days = pd.date_range('2019-01-01', '2024-12-31')
exp_days = np.zeros((6, N), np.float32); low_days = np.zeros((6, N), np.float32)
exp_month = np.zeros((72, N), np.float32)
for di, dd in enumerate(days):
    k = np.searchsorted(t_obs, di)
    lp = lst[k - 1] if k >= 1 else np.full(N, -1); nn = nx[k] if k < T else np.full(N, T)
    tp = np.where(lp >= 0, t_obs[np.clip(lp, 0, T-1)], -10**6); tn = np.where(nn < T, t_obs[np.clip(nn, 0, T-1)], 10**6)
    use = np.where(di - tp <= tn - di, np.clip(lp, 0, T-1), np.clip(nn, 0, T-1))
    e = E8[use, cols]; l = L8[use, cols]
    yi = dd.year - 2019; exp_days[yi] += e; low_days[yi] += l
    exp_month[yi * 12 + dd.month - 1] += e / dd.days_in_month
B = 5; Hb = 100
blk = lambda a: a.reshape(*a.shape[:-2], Hb, B, Hb, B).mean(axis=(-3, -1))
ed = blk(exp_days.reshape(6, H, W_)); ld = blk(low_days.reshape(6, H, W_))
crop_b = np.load('a3_1_blocos.npz')['crop_b']
me, ml = ed.mean(0)[crop_b], ld.mean(0)[crop_b]
res['T2_frac_talhoes_ate_30_dias_exposto'] = round(float((me <= 30).mean()), 2)
res['frac_talhoes_ate_60_dias_exposto'] = round(float((me <= 60).mean()), 2)
res['baseline_ndvi_vizinho_frac_ate_30_dias'] = round(float((ml <= 30).mean()), 2)
res['baseline_ndvi_vizinho_frac_ate_60_dias'] = round(float((ml <= 60).mean()), 2)
res['dias_exposto_p10_p50_p90'] = [round(float(x)) for x in np.percentile(me, [10, 50, 90])]
res['dias_ndvi_baixo_p10_p50_p90'] = [round(float(x)) for x in np.percentile(ml, [10, 50, 90])]
Xb = ed[:, crop_b].T; k = 6; gm = Xb.mean(); msb = k * ((Xb.mean(1) - gm) ** 2).sum() / (Xb.shape[0] - 1)
msw = ((Xb - Xb.mean(1, keepdims=True)) ** 2).sum() / (Xb.shape[0] * (k - 1))
res['T4_ICC_dias_exposto'] = round(float((msb - msw) / (msb + (k - 1) * msw)), 2)
res['dias_exposto_medio_por_ano'] = dict(zip(yrs, [round(float(x)) for x in ed[:, crop_b].mean(1)]))
em = blk(exp_month.reshape(72, H, W_))
res['perfil_exposto_lavoura_por_mes'] = [round(float(em[m::12][:, crop_b].mean()), 3) for m in range(12)]
json.dump(res, open(f'a3_3_resultado_{THR:.2f}.json', 'w'), indent=1, ensure_ascii=False)
for kk, v in res.items(): print(kk, v)
if abs(THR - 0.09) < 1e-9: np.savez_compressed('a3_3_exposto.npz', exp_month_b=em, exp_days_b=ed, low_days_b=ld)
