"""A5-3: NDVI MODIS (MOD13Q1) de 1º/out a 15/nov nos pixels com mais cebola x produtividade da cebola de Ituporanga.

Pixels: fração de cebola do Sentinel-2 (máscaras cebola_<ano>.npz da A5-2) agregada na grade MODIS de 250 m.
Regra pré-registrada: células com fração >= 30%; se forem menos de 10, as 20 de maior fração.
Indicador por ano: média, nas células escolhidas, da anomalia relativa do NDVI (composições de 30/set, 16/out e 1º/nov,
só pixels com confiabilidade 0 ou 1).
Uso: python analisa_modis.py <pasta_modis> <pasta_s2_npz> <anos_mascara> <pam_json> <base_chuva_json> <saida_json> <saida_png>
"""
import sys, json, glob
import numpy as np
from scipy.stats import spearmanr
from pyproj import Transformer
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

PM, PS, ANOS_M, PAM, BASE, SAIDA, PNG = sys.argv[1], sys.argv[2], [int(a) for a in sys.argv[3].split(",")], sys.argv[4], sys.argv[5], sys.argv[6], sys.argv[7]

def le(ano, banda):
    d = json.load(open(f"{PM}/mod13q1_{ano}_{banda}.json"))
    return d, {s["calendar_date"]: np.array(s["data"], float).reshape(d["nrows"], d["ncols"]) for s in d["subset"]}

# --- grade MODIS e fração de cebola do Sentinel-2
g = json.load(open(sorted(glob.glob(f"{PM}/mod13q1_*_250m_16_days_NDVI.json"))[0]))
nr, nc, cs, xll, yll = g["nrows"], g["ncols"], g["cellsize"], float(g["xllcorner"]), float(g["yllcorner"])
mk = np.load(f"{PS}/mascara_municipio.npz"); m, (xmin, ymin, xmax, ymax) = mk["m"], mk["bounds"]
H, W = m.shape
ceb = np.mean([np.load(f"{PS}/cebola_{a}.npz")["c"].astype(float) for a in ANOS_M], axis=0)
rr, cc = np.nonzero(m)
x = xmin + (cc + 0.5) * 10; y = ymax - (rr + 0.5) * 10
t = Transformer.from_crs(32722, "+proj=sinu +R=6371007.181 +nadgrids=@null +wktext", always_xy=True)
sx, sy = t.transform(x, y)
col = np.floor((sx - xll) / cs).astype(int); row = (nr - 1 - np.floor((sy - yll) / cs)).astype(int)
ok = (col >= 0) & (col < nc) & (row >= 0) & (row < nr)
idx = row[ok] * nc + col[ok]
tot = np.bincount(idx, minlength=nr * nc); som = np.bincount(idx, weights=ceb[rr[ok], cc[ok]], minlength=nr * nc)
frac = np.where(tot > 400, som / np.maximum(tot, 1), np.nan).reshape(nr, nc)  # só células quase todas dentro do município
sel = np.nan_to_num(frac) >= 0.30
regra = ">= 30%"
if sel.sum() < 10:
    lim = np.sort(np.nan_to_num(frac).ravel())[-20]
    sel = np.nan_to_num(frac) >= lim; regra = f"20 maiores (fração >= {lim:.2f})"
print("células escolhidas:", int(sel.sum()), regra, "fração média de cebola:", round(float(np.nanmean(frac[sel])), 2))

# --- série de NDVI out-nov
anos = list(range(2000, 2026))
V = np.full((len(anos), int(sel.sum())), np.nan); Vall = np.full((len(anos), int(np.isfinite(frac).sum())), np.nan)
for i, a in enumerate(anos):
    _, nd = le(a, "250m_16_days_NDVI"); _, rel = le(a, "250m_16_days_pixel_reliability")
    vals = []
    for dte in sorted(nd):
        if not ("09-28" <= dte[5:] <= "11-05"):
            continue
        v = nd[dte] * 1e-4
        v[(rel[dte] > 1) | (nd[dte] < -2000)] = np.nan
        vals.append(v)
    if vals:
        with np.errstate(all="ignore"):
            mv = np.nanmean(np.stack(vals), axis=0)
        V[i] = mv[sel]; Vall[i] = mv[np.isfinite(frac)]
with np.errstate(all="ignore"):
    anomc = V / np.nanmean(V, axis=0) - 1
    ind = np.nanmean(anomc, axis=1)
    ind_all = np.nanmean(Vall / np.nanmean(Vall, axis=0) - 1, axis=1)

d = json.load(open(PAM))[1:]
rend = {int(r["D3N"]): float(r["V"]) for r in d if r["D2N"].startswith("Rendimento")}
yv = np.array([rend[a] for a in anos]); an = np.array(anos)
anom = yv / np.polyval(np.polyfit(an, yv, 1), an) - 1
quebra = anom <= -0.15
rho, p = spearmanr(ind, anom)
rho_all, p_all = spearmanr(ind_all, anom)
baixo = ind <= np.percentile(ind, 100 / 3)
pegas = int((quebra & baixo).sum())
base = json.load(open(BASE))
res = dict(celulas=int(sel.sum()), regra=regra, frac_media=round(float(np.nanmean(frac[sel])), 3),
           rho=round(rho, 2), p=round(p, 3), quebras=an[quebra].tolist(), anos_alarme=an[baixo].tolist(),
           quebras_pegas=pegas, n_quebras=int(quebra.sum()), rho_municipio_todo=round(rho_all, 2), p_municipio_todo=round(p_all, 3),
           rho_chuva_B41=base["rho"], indicador=dict(zip(anos, np.round(ind, 4).tolist())), anom_rend=dict(zip(anos, np.round(anom, 3).tolist())))
json.dump(res, open(SAIDA, "w"), ensure_ascii=False, indent=1)
print({k: v for k, v in res.items() if k not in ("indicador", "anom_rend")})

fig, ax = plt.subplots(1, 2, figsize=(12, 4.5))
ax[0].scatter(100 * ind, 100 * anom, c=["#d7301f" if q else "#3182bd" for q in quebra])
for a, xi, yi in zip(anos, ind, anom):
    ax[0].annotate(str(a)[2:], (100 * xi, 100 * yi), fontsize=7, xytext=(3, 2), textcoords="offset points")
ax[0].axhline(-15, color="grey", ls=":"); ax[0].axvline(100 * np.percentile(ind, 100 / 3), color="grey", ls="--")
ax[0].set_xlabel("anomalia de NDVI MODIS, 1º/out–15/nov, células com cebola (%)"); ax[0].set_ylabel("produtividade de Ituporanga vs tendência (%)")
ax[0].set_title(f"Spearman ρ = {rho:.2f} (p = {p:.2f}); vermelho = quebra ≥ 15%", fontsize=9)
im = ax[1].imshow(frac, cmap="Reds", vmin=0, vmax=0.6); ax[1].contour(sel, levels=[0.5], colors="k", linewidths=.6)
ax[1].set_title(f"Fração de cebola (Sentinel-2) na grade MODIS; contorno = {int(sel.sum())} células usadas", fontsize=9); ax[1].set_axis_off()
plt.colorbar(im, ax=ax[1], fraction=.04)
fig.suptitle("A5-3 · Vigor da cebola no MODIS antes da colheita x produtividade (IBGE PAM), 2000–2025", fontsize=10)
fig.tight_layout(); fig.savefig(PNG, dpi=100)
