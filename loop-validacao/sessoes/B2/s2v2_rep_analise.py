"""B2-1: indicador de solo nu (Sentinel-2) contra o Censo Agro 2017 (cultivo convencional).
Lê dados/s2/<cod>.npz (de s2_extrair.py) e dados/censo2017_6855_preparo_solo_SC.json.
REPLICAÇÃO B2-4 com o método congelado da B2-3. VERSÃO AJUSTADA (B2-3): observação não verde só conta com confirmação no tempo; mata excluída.
Saída: s2v2_resultado.json e s2v2_solo_nu_x_censo.svg.
  python3 s2_analise.py
"""
import json, os, math
import numpy as np
from scipy import stats

AQUI = os.path.dirname(os.path.abspath(__file__))
D = os.path.join(AQUI, "dados")
GRUPOS = {"REP": open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "dados", "ids_replicacao.txt")).read().split()}
NDVI_VERDE, NDVI_NU = 0.60, 0.30

# Censo
cen = {}
for r in json.load(open(os.path.join(D, "censo2017_6855_preparo_solo_SC.json")))[1:]:
    n = r["D3N"]
    k = ("nao" if "não utilizaram" in n else "usou" if "utilizaram sistema" in n else "conv" if "convencional" in n
         else "min" if "mínimo" in n else "pd" if ("plantio direto" in n and "Número" in n) else "area_pd")
    v = r["V"]
    cen.setdefault(r["D1C"], {"nome": r["D1N"].replace(" - SC", "")})[k] = 0.0 if v == "-" else (float(v) if v.replace(".", "").isdigit() else math.nan)


def confirmados(ndvi, dia):
    """NDVI < 0,30 confirmado: a obs. válida anterior ou seguinte (<= 30 dias) também < 0,40."""
    T, N = ndvi.shape
    out = np.zeros((T, N), bool)
    val = ~np.isnan(ndvi)
    v = np.where(val, ndvi, np.nan)
    # índice da obs válida anterior/seguinte por pixel
    prev_v = np.full(N, np.nan, "float32"); prev_d = np.full(N, -10**9)
    ant_v = np.full((T, N), np.nan, "float32"); ant_d = np.zeros((T, N), "int64")
    for t in range(T):
        ant_v[t], ant_d[t] = prev_v, prev_d
        m = val[t]; prev_v = np.where(m, v[t], prev_v); prev_d = np.where(m, dia[t], prev_d)
    nxt_v = np.full(N, np.nan, "float32"); nxt_d = np.full(N, 10**9)
    seg_v = np.full((T, N), np.nan, "float32"); seg_d = np.zeros((T, N), "int64")
    for t in range(T - 1, -1, -1):
        seg_v[t], seg_d[t] = nxt_v, nxt_d
        m = val[t]; nxt_v = np.where(m, v[t], nxt_v); nxt_d = np.where(m, dia[t], nxt_d)
    with np.errstate(invalid="ignore"):
        baixo = v < NDVI_NU
        ok_a = (ant_v < 0.40) & ((dia[:, None] - ant_d) <= 30)
        ok_s = (seg_v < 0.40) & ((seg_d - dia[:, None]) <= 30)
    return baixo & (ok_a | ok_s)


def indicadores(cod, limiar):
    z = np.load(os.path.join(D, "s2", f"{cod}.npz"))
    datas, ndvi, ndti = z["datas"], z["ndvi"], z["ndti"]
    _, idx = np.unique(datas, return_index=True)  # uma cena por data
    datas, ndvi, ndti = datas[idx], ndvi[idx], ndti[idx]
    val = ~np.isnan(ndvi)
    nval = val.sum(0)
    dia = np.array([np.datetime64(x) for x in datas]).astype("int64")
    conf = confirmados(ndvi, dia)
    with np.errstate(invalid="ignore"):
        mx = np.nanmax(np.where(val, ndvi, -9), 0)
        med = np.nanmedian(np.where(val, ndvi, np.nan), 0)
    lav = (nval >= 8) & (mx >= NDVI_VERDE) & (conf.sum(0) >= 2) & (med < 0.70)
    nv, nt = ndvi[:, lav], ndti[:, lav]
    with np.errstate(invalid="ignore"):
        naoverde = conf[:, lav]
        nu = naoverde & (nt < limiar)
    I1 = nu.sum() / max(naoverde.sum(), 1)
    I2 = float((nu.sum(0) >= 2).mean())
    mes = np.array([int(d[5:7]) for d in datas])
    por_mes = {}
    for m in range(1, 13):
        s = mes == m
        nobs = (~np.isnan(nv[s])).sum()
        por_mes[m] = dict(frac_nu=float(nu[s].sum() / nobs) if nobs else None,
                          frac_palha=float((naoverde[s] & ~nu[s]).sum() / nobs) if nobs else None, n_obs=int(nobs))
    return dict(I1=float(I1), I2=I2, frac_lavoura=float(lav.mean()), n_pix=int(val.shape[1]), n_lav=int(lav.sum()),
                n_cenas=int(len(datas)), obs_validas_med=float(np.median(nval)), obs_naoverde=int(naoverde.sum()),
                por_mes=por_mes)


res = {"municipios": {}, "testes": {}}
for lim in (0.05, 0.07, 0.09):
    linhas = []
    for g, cods in GRUPOS.items():
        for c in cods:
            if not os.path.exists(os.path.join(D, "s2", f"{c}.npz")):
                continue
            ce = cen.get(c, {})
            s = ce.get("conv", math.nan) + ce.get("min", math.nan) + ce.get("pd", math.nan)
            if not (ce.get("usou", 0) >= 150) or math.isnan(s):
                continue
            ind = indicadores(c, lim)
            C = ce["conv"] / s
            linhas.append((g, c, ce["nome"], C, ind))
            if lim == 0.07:
                res["municipios"][c] = dict(grupo=g, nome=ce["nome"], C_convencional=C, censo=ce,
                                            **{k: v for k, v in ind.items()})
    C = np.array([l[3] for l in linhas]); I1 = np.array([l[4]["I1"] for l in linhas])
    I2 = np.array([l[4]["I2"] for l in linhas]); FL = np.array([l[4]["frac_lavoura"] for l in linhas])
    g = np.array([l[0] for l in linhas])
    t = dict(n=len(linhas), rho_I1=stats.spearmanr(I1, C)[0], p_I1=stats.spearmanr(I1, C)[1],
             rho_I2=stats.spearmanr(I2, C)[0], p_I2=stats.spearmanr(I2, C)[1],
             rho_base_frac_lavoura=stats.spearmanr(FL, C)[0], p_base=stats.spearmanr(FL, C)[1])
    for gg in ():
        m = g == gg
        if m.sum() >= 4:
            t[f"rho_I1_{gg}"] = stats.spearmanr(I1[m], C[m])[0]; t[f"p_I1_{gg}"] = stats.spearmanr(I1[m], C[m])[1]
            t[f"n_{gg}"] = int(m.sum())
    res["testes"][lim] = {k: (float(v) if not isinstance(v, int) else v) for k, v in t.items()}
json.dump(res, open(os.path.join(AQUI, "s2v2_rep_resultado.json"), "w"), indent=1, ensure_ascii=False)

for lim, t in res["testes"].items():
    print(lim, {k: round(v, 3) if isinstance(v, float) else v for k, v in t.items()})
for c, m in res["municipios"].items():
    print(f"{m['grupo']} {m['nome'][:20]:20s} C={m['C_convencional']:.2f} I1={m['I1']:.3f} I2={m['I2']:.2f} lav={m['frac_lavoura']:.2f} nlav={m['n_lav']} cenas={m['n_cenas']} obs_med={m['obs_validas_med']:.0f}")

# gráfico SVG: I1 x C
ms = list(res["municipios"].values())
W, H, M = 640, 440, 60
xs = [m["C_convencional"] for m in ms]; ys = [m["I1"] for m in ms]
x0, x1 = 0, max(xs) * 1.1; y0, y1 = 0, max(ys) * 1.15
X = lambda v: M + (W - 2 * M) * (v - x0) / (x1 - x0)
Y = lambda v: H - M - (H - 2 * M) * (v - y0) / (y1 - y0)
t7 = res["testes"][0.07]
s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" font-family="sans-serif" font-size="11">',
     f'<rect width="{W}" height="{H}" fill="white"/>',
     f'<text x="{M}" y="22" font-size="13">Replicação no Oeste (32 municípios fora da amostra): solo nu x convencional</text>',
     f'<text x="{M}" y="38" fill="#555">Spearman ρ = {t7["rho_I1"]:.2f} (p = {t7["p_I1"]:.3f}, n = {t7["n"]}); método congelado da B2-3</text>',
     f'<line x1="{M}" y1="{H-M}" x2="{W-M}" y2="{H-M}" stroke="#333"/><line x1="{M}" y1="{M}" x2="{M}" y2="{H-M}" stroke="#333"/>',
     f'<text x="{W/2-140}" y="{H-20}">Censo 2017: fração de estabelecimentos com cultivo convencional</text>',
     f'<text x="14" y="{H/2+90}" transform="rotate(-90 14 {H/2+90})">Sentinel-2: fração das vezes sem planta em que o solo está nu</text>']
for v in np.linspace(0, x1, 5):
    s.append(f'<text x="{X(v)-8:.0f}" y="{H-M+14}">{v:.2f}</text>')
for v in np.linspace(0, y1, 5):
    s.append(f'<text x="{M-34}" y="{Y(v)+4:.0f}">{v:.2f}</text>')
for m in ms:
    cor = "#d9822b"
    s.append(f'<circle cx="{X(m["C_convencional"]):.1f}" cy="{Y(m["I1"]):.1f}" r="5" fill="{cor}"/>')
    s.append(f'<text x="{X(m["C_convencional"])+7:.1f}" y="{Y(m["I1"])+4:.1f}" fill="#333">{m["nome"]}</text>')
s.append("</svg>")
open(os.path.join(AQUI, "s2v2_rep_solo_nu_x_censo.svg"), "w").write("\n".join(s))
