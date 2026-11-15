"""NDVI diario interpolado por pixel (Sentinel-2 L2A, mascara SCL 4/5), 2019-2024. Vetorizado.
Saidas (ndvi_mensal.npz): por mes x pixel: fracao de dias com NDVI<0.30 (descoberto), NDVI medio,
n de obs limpas, fracao de dias a >30 d de uma obs limpa; classe de uso por pixel; fracao limpa por cena."""
import numpy as np, pandas as pd
c = np.load('raw/s2/cubo.npz')
dates = pd.to_datetime(c['dates']); off = c['off']
VALID = np.isin(c['scl'], [4, 5])
red = c['red'].astype(np.float32) - off[:, None, None]; nir = c['nir'].astype(np.float32) - off[:, None, None]
ndvi = np.where(VALID & (red + nir > 0), (nir - red) / np.maximum(nir + red, 1), np.nan).astype(np.float32)
del red, nir
T, H, W = ndvi.shape; N = H * W
X = ndvi.reshape(T, N)
clear_frac = (~np.isnan(X)).mean(1)
X[clear_frac < 0.30] = np.nan                       # descarta cenas quase todas nubladas (bordas de nuvem mal mascaradas)
# filtro de pico: obs que cai > 0.15 abaixo das duas vizinhas validas e nuvem/sombra residual (2 passadas)
ar0 = np.arange(T)[:, None]
for _ in range(2):
    okk = ~np.isnan(X)
    lst = np.maximum.accumulate(np.where(okk, ar0, -1), axis=0); nx = np.flip(np.minimum.accumulate(np.flip(np.where(okk, ar0, T), 0), axis=0), 0)
    pi = np.vstack([np.full((1, N), -1), lst[:-1]]); ni = np.vstack([nx[1:], np.full((1, N), T)])
    Xf0 = np.nan_to_num(X, nan=9.0)
    pv = np.where(pi >= 0, Xf0[np.clip(pi, 0, T-1), np.arange(N)], 9.0); nv = np.where(ni < T, Xf0[np.clip(ni, 0, T-1), np.arange(N)], 9.0)
    spike = okk & (X < np.minimum(pv, nv) - 0.15) & (pv < 9) & (nv < 9)
    print('picos removidos:', int(spike.sum()), 'de', int(okk.sum()), flush=True)
    X[spike] = np.nan
ok = ~np.isnan(X)
print('cenas:', T, ' com >=50% limpo:', int((clear_frac >= .5).sum()), flush=True)
t_obs = (dates - pd.Timestamp('2019-01-01')).days.values
ar = np.arange(T)[:, None]
last = np.maximum.accumulate(np.where(ok, ar, -1), axis=0)                    # ultima cena valida <= i
nxt = np.flip(np.minimum.accumulate(np.flip(np.where(ok, ar, T), 0), axis=0), 0)  # proxima cena valida >= i
Xf = np.nan_to_num(X)
days = pd.date_range('2019-01-01', '2024-12-31'); mlist = pd.period_range('2019-01', '2024-12', freq='M')
cols = np.arange(N)
bare_m = np.full((len(mlist), N), np.nan, np.float32); ndvi_m = bare_m.copy(); gap_m = bare_m.copy()
nobs_m = np.zeros((len(mlist), N), np.int16)
om = pd.PeriodIndex(dates, freq='M')
for mi, m in enumerate(mlist):
    dd = np.arange((m.start_time - days[0]).days, (m.end_time.normalize() - days[0]).days + 1)
    acc_b = np.zeros(N, np.float32); acc_n = np.zeros(N, np.float32); acc_g = np.zeros(N, np.float32); cnt = np.zeros(N, np.float32)
    for d in dd:
        k = np.searchsorted(t_obs, d)                  # primeira cena com t >= d
        lp = last[k - 1] if k >= 1 else np.full(N, -1)
        nn = nxt[k] if k < T else np.full(N, T)
        hasp, hasn = lp >= 0, nn < T
        vp = Xf[np.clip(lp, 0, T - 1), cols]; vn = Xf[np.clip(nn, 0, T - 1), cols]
        tp = t_obs[np.clip(lp, 0, T - 1)]; tn = t_obs[np.clip(nn, 0, T - 1)]
        w = np.where(tn > tp, (d - tp) / np.maximum(tn - tp, 1), 0.5)
        v = np.where(hasp & hasn, vp + w * (vn - vp), np.where(hasp, vp, vn))
        good = hasp | hasn
        dist = np.minimum(np.where(hasp, d - tp, 9999), np.where(hasn, tn - d, 9999))
        acc_b += (v < 0.30) & good; acc_n += np.where(good, v, 0); acc_g += dist > 30; cnt += good
    bare_m[mi] = np.where(cnt > 0, acc_b / np.maximum(cnt, 1), np.nan); ndvi_m[mi] = np.where(cnt > 0, acc_n / np.maximum(cnt, 1), np.nan)
    gap_m[mi] = acc_g / len(dd)
    nobs_m[mi] = ok[om == m].sum(0)
    if mi % 12 == 0: print(m, flush=True)
p05 = np.nanpercentile(X, 5, axis=0); p95 = np.nanpercentile(X, 95, axis=0)
cls = np.full(N, 3, np.int8)                         # 3 pastagem/misto
cls[p05 >= 0.60] = 1                                  # 1 mata/perene (sempre verde)
cls[(p95 >= 0.65) & (p05 < 0.30)] = 2                 # 2 lavoura anual (verde e descoberto no periodo)
cls[(p95 < 0.45) | (ok.sum(0) < 20)] = 0              # 0 urbano/agua/sem dado
np.savez_compressed('ndvi_mensal.npz', months=np.array([str(m) for m in mlist]), bare=bare_m.reshape(-1, H, W),
    ndvi=ndvi_m.reshape(-1, H, W), nobs=nobs_m.reshape(-1, H, W), gap=gap_m.reshape(-1, H, W), cls=cls.reshape(H, W),
    scene_dates=c['dates'], clear_frac=clear_frac)
print('classes (frac):', {k: round(float((cls == k).mean()), 3) for k in range(4)}, flush=True)
