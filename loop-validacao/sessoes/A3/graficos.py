"""Graficos das fichas A3 e checagem de robustez do A3-1 com o 'solo exposto' do NDTI."""
import json, numpy as np, pandas as pd, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
er = json.load(open('erosividade_mensal.json')); r1 = json.load(open('a3_1_resultado.json')); r3 = json.load(open('a3_3_resultado_0.09.json'))
b = np.load('a3_1_blocos.npz'); x3 = np.load('a3_3_exposto.npz'); d = np.load('ndvi_mensal.npz'); g = np.load('declive.npz')
M = ['jan','fev','mar','abr','mai','jun','jul','ago','set','out','nov','dez']
back = [931.0, 828.0, 504.9, 386.4, 455.0, 440.3, 565.9, 574.8, 835.5, 869.0, 483.1, 675.4]
f = np.array(er['fournier_power']['mensal']); di = np.array(er['diario_P^1.81']['mensal'])
fig, ax = plt.subplots(2, 1, figsize=(9, 7), sharex=True)
ax[0].plot(M, np.array(back) / np.mean(back), 'k-o', label='ANA/Back et al. 2023 (pluviômetro, EI30)')
ax[0].plot(M, f / f.mean(), 'C0-s', label='POWER, índice de Fournier (Spearman 0,85)')
ax[0].plot(M, di / di.mean(), 'C1--^', label='POWER, método diário P^1,81 (Spearman 0,64)')
ax[0].set_ylabel('erosividade relativa (média = 1)'); ax[0].legend(fontsize=8); ax[0].set_title('Ituporanga: quando a chuva é mais erosiva')
ax[1].bar(np.arange(12) - 0.2, r1['perfil_descoberto_lavoura_por_mes'], 0.4, label='NDVI < 0,30 (descoberto ou palhada)')
ax[1].bar(np.arange(12) + 0.2, r3['perfil_exposto_lavoura_por_mes'], 0.4, label='NDVI < 0,30 e NDTI < 0,09 (solo nu)')
ax2 = ax[1].twinx(); ax2.plot(M, r1['perfil_exposicao_lavoura_por_mes_rel'], 'r-o', label='exposição = erosividade × descoberto × declive')
ax2.set_ylabel('exposição relativa', color='r')
ax[1].set_ylabel('fração de dias'); ax[1].legend(fontsize=8, loc='upper left'); ax2.legend(fontsize=8, loc='upper right')
ax[1].set_title('Lavoura anual (2.302 talhões de 50 m), Sentinel-2, 2019–2024')
plt.tight_layout(); plt.savefig('a3_1_calendario.png', dpi=110); plt.close()
# mapa
fig, ax = plt.subplots(1, 3, figsize=(13, 4.5))
cm = matplotlib.colors.ListedColormap(['#999999', '#1b7837', '#e08214', '#a6dba0'])
ax[0].imshow(d['cls'], cmap=cm, vmin=0, vmax=3); ax[0].set_title('uso (cinza urbano, verde-escuro mata,\nlaranja lavoura anual, verde-claro pasto)', fontsize=9)
im = ax[1].imshow(g['slope'], cmap='magma_r', vmin=0, vmax=50); ax[1].set_title('declive SRTM (%)', fontsize=9); plt.colorbar(im, ax=ax[1], fraction=.046)
Ea = np.where(b['crop_b'], b['Eann'], np.nan)
im = ax[2].imshow(Ea, cmap='Reds', vmin=0, vmax=np.nanpercentile(Ea, 95)); ax[2].set_title('exposição anual média (só lavoura)\np90/p10 = 9', fontsize=9); plt.colorbar(im, ax=ax[2], fraction=.046)
for a in ax: a.set_xticks([]); a.set_yticks([])
plt.suptitle('Recorte de 5 × 5 km em Ituporanga (-27,414; -49,601)'); plt.tight_layout(); plt.savefig('a3_1_mapa.png', dpi=110); plt.close()
# robustez C3 com NDTI
R = b['R']; E2 = R[:, None, None] * x3['exp_month_b'] * b['S_b'][None]; crop_b = b['crop_b']
pk, outside = [], []
for y in range(6):
    Ey = E2[y*12:(y+1)*12][:, crop_b]; v = Ey.sum(0) > 0; p = Ey.argmax(0)[v] + 1
    pk.append(p != 1); outside.append(~np.isin(p, [10, 11, 12, 1, 2]))
rob = {'C3_ndti_frac_pico_diferente_jan': round(float(np.concatenate(pk).mean()), 2),
       'C3_ndti_frac_pico_fora_out_fev': round(float(np.concatenate(outside).mean()), 2),
       'C3_ndti_frac_talhao_ano_com_exposicao': round(float(np.mean([(E2[y*12:(y+1)*12][:, crop_b].sum(0) > 0).mean() for y in range(6)])), 2)}
json.dump(rob, open('a3_1_robustez_ndti.json', 'w'), indent=1); print(rob)
# A3-2 / A3-3: distribuicao de dias descobertos vs referencia do Censo
r2 = np.load('a3_2_nota.npz'); bd = r2['bd'].mean(0)[crop_b]; ed = x3['exp_days_b'].mean(0)[crop_b]
fig, ax = plt.subplots(figsize=(8, 4))
ax.hist(bd, bins=np.arange(0, 200, 7.5), alpha=.6, label='dias com NDVI < 0,30 (A3-2)')
ax.hist(ed, bins=np.arange(0, 200, 7.5), alpha=.6, label='dias de solo nu pelo NDTI (A3-3)')
ax.axvline(60, color='C0', ls='--'); ax.axvline(30, color='C1', ls='--')
ax.set_xlabel('dias por ano (média 2019–2024), por talhão de lavoura'); ax.set_ylabel('talhões')
ax.set_title('"Tipo plantio direto": 70% (NDVI ≤ 60 d) e 97% (NDTI ≤ 30 d), contra 21–25% no Censo 2017', fontsize=9)
ax.legend(); plt.tight_layout(); plt.savefig('a3_2_a3_3_dias_descobertos.png', dpi=110); plt.close()
# A3-4
r4 = json.load(open('a3_4_resultado.json')); lab = list(r4['P_dia_25mm_45d'].keys())
fig, ax = plt.subplots(figsize=(8, 4))
ax.plot(lab, list(r4['P_dia_25mm_45d'].values()), 'k-o', label='1981–2025'); ax.plot(lab, r4['P_1981_2003'], 'C0--', label='1981–2003'); ax.plot(lab, r4['P_2004_2025'], 'C1--', label='2004–2025')
ax2 = ax.twinx(); ax2.plot(lab, r4['back_EI30_janela'], 'r:s', label='EI30 da janela (ANA/Back 2023)'); ax2.set_ylabel('EI30 na janela', color='r')
ax.set_ylabel('P(≥1 dia ≥ 25 mm em 45 d)'); ax.set_xlabel('data de preparo do solo'); ax.legend(fontsize=8, loc='lower left'); ax2.legend(fontsize=8, loc='lower right')
ax.set_title('A ordem das janelas muda entre metades da série e não bate com o pluviômetro', fontsize=9)
plt.tight_layout(); plt.savefig('a3_4_janelas.png', dpi=110); plt.close()
