"""A3-1 Alerta mensal de erosao. Exposicao E(talhao, ano, mes) = R(ano, mes) x descoberto(talhao, ano, mes) x S(declive).
R: indice de Fournier mensal do NASA POWER (p_mes^2 / P_ano), escolhido no C1 (passou; o metodo diario nao passou).
descoberto: fracao de dias do mes com NDVI < 0.30 (Sentinel-2). S: fator de declive de McCool (USLE), L fixo.
Unidade 'talhao': bloco de 5 x 5 pixels (50 m) com maioria de lavoura anual."""
import json, numpy as np, pandas as pd
d = np.load('ndvi_mensal.npz'); g = np.load('declive.npz')
months = pd.PeriodIndex(d['months'], freq='M'); bare = d['bare']; cls = d['cls']; nobs = d['nobs']; gap = d['gap']
p = json.load(open('../../dados/power_ituporanga.json'))['properties']['parameter']['PRECTOTCORR']
s = pd.Series({pd.Timestamp(k): v for k, v in p.items()}).replace(-999, np.nan)
mp = s.resample('MS').sum(); mp.index = mp.index.to_period('M')
Pann = s.resample('YS').sum(); Pann.index = Pann.index.year
R = np.array([mp[m] ** 2 / Pann[m.year] for m in months])            # Fournier mensal por ano (mm)
Rclim = pd.Series([mp[mp.index.month == k]['1981':'2021'].pow(2).mean() for k in range(1, 13)], index=range(1, 13))
th = np.arctan(g['slope'] / 100); S = np.where(g['slope'] < 9, 10.8 * np.sin(th) + 0.03, 16.8 * np.sin(th) - 0.50)
B = 5; H = bare.shape[1] // B
def blk(a): return a.reshape(*a.shape[:-2], H, B, H, B).mean(axis=(-3, -1))
crop_frac = blk((cls == 2).astype(float)); forest_frac = blk((cls == 1).astype(float))
bare_b = blk(np.nan_to_num(bare)); S_b = blk(S); slope_b = blk(g['slope'])
E = R[:, None, None] * bare_b * S_b[None]                             # mes x bloco
res = {}
# C2: viabilidade
cf = d['clear_frac']; sd = pd.to_datetime(d['scene_dates']).to_period('M')
mes_ok = pd.Series(cf >= 0.5, index=sd).groupby(level=0).any().reindex(months, fill_value=False)
cropmask = cls == 2
res['C2_frac_meses_com_cena_50pct_limpa'] = round(float(mes_ok.mean()), 2)
res['C2_frac_pixel_mes_lavoura_com_obs'] = round(float((nobs[:, cropmask] >= 1).mean()), 2)
res['C2_frac_pixel_mes_lavoura_gap_maior_30d'] = round(float((gap[:, cropmask] > 0.5).mean()), 2)
res['C2_meses_sem_cena_boa'] = [str(m) for m in months[~mes_ok.values]]
# C3: mes de pico da exposicao vs pico da linha de base (calendario de chuva)
base_peak = int(Rclim.idxmax()); res['linha_base_mes_pico'] = base_peak
res['linha_base_top3'] = [int(x) for x in Rclim.sort_values().index[-3:][::-1]]
crop_b = crop_frac >= 0.6; forest_b = forest_frac >= 0.6
res['n_talhoes_lavoura'] = int(crop_b.sum()); res['n_blocos_mata'] = int(forest_b.sum())
peaks, outside, share_top3 = [], [], []
peak_hist = np.zeros(13, int)
for y in range(2019, 2025):
    idx = np.where(months.year == y)[0]
    Ey = E[idx][:, crop_b]                                           # 12 x n
    tot = Ey.sum(0); valid = tot > 0
    pk = Ey.argmax(0) + 1
    peaks.append(pk[valid] != base_peak)
    outside.append(~np.isin(pk[valid], [10, 11, 12, 1, 2]))
    srt = np.sort(Ey[:, valid], 0)[::-1]; share_top3.append(srt[:3].sum(0) / tot[valid])
    for k in pk[valid]: peak_hist[k] += 1
res['C3_frac_talhao_ano_pico_diferente_da_base'] = round(float(np.concatenate(peaks).mean()), 2)
res['C3_frac_talhao_ano_pico_fora_out_fev'] = round(float(np.concatenate(outside).mean()), 2)
res['C3_frac_exposicao_nos_3_meses_mais_expostos_mediana'] = round(float(np.median(np.concatenate(share_top3))), 2)
res['C3_histograma_mes_pico'] = {int(k): int(v) for k, v in enumerate(peak_hist) if k}
# C4: separacao
Eann = np.stack([E[months.year == y].sum(0) for y in range(2019, 2025)]).mean(0)
ec = Eann[crop_b]; ef = Eann[forest_b]
res['C4_p90_p10_lavoura'] = round(float(np.percentile(ec, 90) / max(np.percentile(ec, 10), 1e-6)), 1)
res['C4_p10_p50_p90_lavoura'] = [round(float(x), 2) for x in np.percentile(ec, [10, 50, 90])]
res['C4_mediana_lavoura_sobre_mata'] = round(float(np.median(ec) / max(np.median(ef), 1e-6)), 1)
res['C4_mediana_mata'] = round(float(np.median(ef)), 3); res['declive_lavoura_p10_p50_p90'] = [round(float(x), 1) for x in np.percentile(slope_b[crop_b], [10, 50, 90])]
# perfil mensal medio dos talhoes de lavoura: descoberto e exposicao
mm = months.month
res['perfil_descoberto_lavoura_por_mes'] = [round(float(bare_b[mm == k][:, crop_b].mean()), 2) for k in range(1, 13)]
res['perfil_exposicao_lavoura_por_mes_rel'] = [round(float(E[mm == k][:, crop_b].mean() / E[:, crop_b].mean()), 2) for k in range(1, 13)]
res['R_clim_rel'] = [round(float(x / Rclim.mean()), 2) for x in Rclim.values]
# variacao entre anos (o mesmo talhao): o mes de pico muda?
pk_by_year = np.stack([E[months.year == y][:, crop_b].argmax(0) for y in range(2019, 2025)])
res['frac_talhoes_pico_muda_entre_anos'] = round(float((pk_by_year.max(0) != pk_by_year.min(0)).mean()), 2)
json.dump(res, open('a3_1_resultado.json', 'w'), indent=1, ensure_ascii=False)
for k, v in res.items(): print(k, v)
np.savez_compressed('a3_1_blocos.npz', E=E, Eann=Eann, crop_b=crop_b, forest_b=forest_b, bare_b=bare_b, S_b=S_b, slope_b=slope_b, R=R)
