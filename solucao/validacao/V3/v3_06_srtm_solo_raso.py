#!/usr/bin/env python3
"""V3-06: identificar solo raso por talhão só com SRTM (aba Resources).

Entrada: tile SRTM 1 arc-s (30 m) S27W054 baixado com curl de s3.amazonaws.com/elevation-tiles-prod/skadi
(caminho passado como argumento; fica fora da pasta do projeto por ter 26 MB).
Saídas: fração da área por classe de declive (IBGE/Embrapa) no entorno de SMO e na área mapeada pela UDESC
(Müller, 2020: 210 ha em SMO; 61,8% Latossolo profundo; resto Neossolo Regolítico + Litólico),
valores de SRTM nos 3 perfis descritos pela UDESC, e fração sinalizada por regra.
"""
import sys, json, math
from pathlib import Path
import numpy as np

hgt = Path(sys.argv[1])
AQUI = Path(__file__).resolve().parent
raw = np.fromfile(hgt, dtype=">i2").reshape(3601, 3601).astype(float)
raw[raw == -32768] = np.nan
LAT0, LON0 = -26.0, -54.0  # canto NW do tile S27W054
dlat = 1 / 3600.0


def rc(lat, lon):
    return (LAT0 - lat) * 3600.0, (lon - LON0) * 3600.0


def utm22s_to_ll(E, N):
    a, f = 6378137.0, 1 / 298.257222101  # SIRGAS 2000
    k0, lon0 = 0.9996, math.radians(-51)
    e2 = f * (2 - f); ep2 = e2 / (1 - e2)
    x = E - 500000.0; y = N - 10000000.0
    M = y / k0
    mu = M / (a * (1 - e2 / 4 - 3 * e2 ** 2 / 64 - 5 * e2 ** 3 / 256))
    e1 = (1 - math.sqrt(1 - e2)) / (1 + math.sqrt(1 - e2))
    phi1 = (mu + (3 * e1 / 2 - 27 * e1 ** 3 / 32) * math.sin(2 * mu) + (21 * e1 ** 2 / 16 - 55 * e1 ** 4 / 32) * math.sin(4 * mu)
            + (151 * e1 ** 3 / 96) * math.sin(6 * mu))
    C1 = ep2 * math.cos(phi1) ** 2; T1 = math.tan(phi1) ** 2
    Nn = a / math.sqrt(1 - e2 * math.sin(phi1) ** 2)
    R1 = a * (1 - e2) / (1 - e2 * math.sin(phi1) ** 2) ** 1.5
    D = x / (Nn * k0)
    lat = phi1 - (Nn * math.tan(phi1) / R1) * (D ** 2 / 2 - (5 + 3 * T1 + 10 * C1 - 4 * C1 ** 2 - 9 * ep2) * D ** 4 / 24)
    lon = lon0 + (D - (1 + 2 * T1 + C1) * D ** 3 / 6 + (5 - 2 * C1 + 28 * T1 - 3 * C1 ** 2 + 8 * ep2 + 24 * T1 ** 2) * D ** 5 / 120) / math.cos(phi1)
    return math.degrees(lat), math.degrees(lon)


# declive em % (Horn), com espaçamento em metros
lat_mid = -26.74
dy = dlat * 111132.0
dx = dlat * 111320.0 * math.cos(math.radians(lat_mid))
z = raw
zp = np.pad(z, 1, mode="edge")
a, b, c = zp[:-2, :-2], zp[:-2, 1:-1], zp[:-2, 2:]
d, f_ = zp[1:-1, :-2], zp[1:-1, 2:]
g, h, i = zp[2:, :-2], zp[2:, 1:-1], zp[2:, 2:]
dzdx = ((c + 2 * f_ + i) - (a + 2 * d + g)) / (8 * dx)
dzdy = ((g + 2 * h + i) - (a + 2 * b + c)) / (8 * dy)
slope = 100 * np.hypot(dzdx, dzdy)


def tpi(r, c, raio_px):
    r, c = int(round(r)), int(round(c))
    jan = z[r - raio_px: r + raio_px + 1, c - raio_px: c + raio_px + 1]
    return z[r, c] - np.nanmean(jan)


def recorte(lat1, lat2, lon1, lon2):
    r1, c1 = rc(lat2, lon1); r2, c2 = rc(lat1, lon2)
    return slope[int(r1):int(r2), int(c1):int(c2)], z[int(r1):int(r2), int(c1):int(c2)]


CLASSES = [(0, 3, "plano 0-3%"), (3, 8, "suave ondulado 3-8%"), (8, 20, "ondulado 8-20%"), (20, 45, "forte ondulado 20-45%"), (45, 1e9, "montanhoso >45%")]


def classes(s):
    s = s[~np.isnan(s)]
    return {n: float(((s >= lo) & (s < hi)).mean()) for lo, hi, n in CLASSES}, int(s.size)


def sinalizada(s, lim):
    s = s[~np.isnan(s)]
    return float((s >= lim).mean())


res = {}
# 1) caixa de 15 x 15 km em torno do ponto do POWER (aproxima a área do município, 236 km2; não é o polígono)
s_mun, z_mun = recorte(-26.725 - 0.0675, -26.725 + 0.0675, -53.518 - 0.0750, -53.518 + 0.0750)
res["entorno_smo_15km"] = dict(zip(("classes", "n_pixels"), classes(s_mun)))
res["entorno_smo_15km"]["fracao_sinalizada"] = {str(l): sinalizada(s_mun, l) for l in (8, 12, 15, 20, 30, 45)}
res["entorno_smo_15km"]["declive_mediano"] = float(np.nanmedian(s_mun))
# 2) área mapeada pela UDESC: UTM 22S E 246800-248800, N 7038800-7040400
ll = [utm22s_to_ll(E, N) for E in (246800, 248800) for N in (7038800, 7040400)]
la = [x[0] for x in ll]; lo = [x[1] for x in ll]
res["udesc_caixa_latlon"] = dict(lat=[min(la), max(la)], lon=[min(lo), max(lo)])
s_u, z_u = recorte(min(la), max(la), min(lo), max(lo))
res["udesc_210ha"] = dict(zip(("classes", "n_pixels"), classes(s_u)))
res["udesc_210ha"]["fracao_sinalizada"] = {str(l): sinalizada(s_u, l) for l in (8, 12, 15, 20, 30, 45)}
res["udesc_210ha"]["referencia_mapa_UDESC"] = dict(LVdf_profundo=0.618, RRd_neossolos_raso_ate_50cm=0.382)
# 3) perfis da UDESC (coordenadas do apêndice) contra o SRTM
perf = {
    "perfil5_Latossolo_terco_medio": dict(lat=-(26 + 44 / 60 + 37.7 / 3600), lon=-(53 + 32 / 60 + 41.1 / 3600), campo_declive=9, solo="Latossolo Vermelho (profundo)"),
    "perfil6_Neossolo_Regolitico_terco_inferior": dict(lat=-(26 + 44 / 60 + 37.1 / 3600), lon=-(53 + 32 / 60 + 20 / 3600), campo_declive=38, solo="Neossolo Regolítico (contato lítico fragmentário < 50 cm)"),
    "perfil7_Neossolo_Litolico_topo": dict(lat=-(26 + 44 / 60 + 28.7 / 3600), lon=-(53 + 32 / 60 + 21.4 / 3600), campo_declive=19, solo="Neossolo Litólico (< 50 cm, muito pedregoso)"),
}
for k, p in perf.items():
    r, c = rc(p["lat"], p["lon"])
    r0, c0 = int(round(r)), int(round(c))
    jan = slope[r0 - 1: r0 + 2, c0 - 1: c0 + 2]
    p["srtm_declive_pct"] = float(np.nanmean(jan))
    p["srtm_elev_m"] = float(z[r0, c0])
    p["tpi_300m_m"] = float(tpi(r, c, 10))  # raio ~300 m
    p["tpi_90m_m"] = float(tpi(r, c, 3))
res["perfis_udesc"] = perf
# 4) quanto vale o TPI e o declive como regra: valor nos 3 perfis vs distribuição na área
tp = np.full(z_u.shape, np.nan)
r_off = int(rc(max(la), min(lo))[0]); c_off = int(rc(max(la), min(lo))[1])
for rr in range(z_u.shape[0]):
    for cc in range(z_u.shape[1]):
        tp[rr, cc] = tpi(r_off + rr, c_off + cc, 3)
res["udesc_210ha"]["tpi90_percentis"] = {str(p_): float(np.nanpercentile(tp, p_)) for p_ in (10, 25, 50, 75, 90)}
res["udesc_210ha"]["fracao_declive_ge12_ou_tpi_gt_2"] = float(np.nanmean(((s_u >= 12) | (tp > 2)).astype(float)))
# 5) variantes de regra (post-hoc: os limiares foram escolhidos depois de ver os 3 perfis; n = 3, não é validação)
from scipy.ndimage import uniform_filter
zf = np.where(np.isnan(z), np.nanmean(z), z)
TPI90 = z - uniform_filter(zf, size=7, mode="nearest")
TPI90_u = TPI90[int(rc(max(la), min(lo))[0]): int(rc(min(la), max(lo))[0]), int(rc(max(la), min(lo))[1]): int(rc(min(la), max(lo))[1])]
TPI90_m = TPI90[int(rc(-26.725 + 0.0675, 0)[0]): int(rc(-26.725 - 0.0675, 0)[0]), int(rc(0, -53.518 - 0.075)[1]): int(rc(0, -53.518 + 0.075)[1])]
regras = {
    "declive>=20": lambda sl, tp_: sl >= 20,
    "declive>=12": lambda sl, tp_: sl >= 12,
    "declive>=15": lambda sl, tp_: sl >= 15,
    "TPI90>=2": lambda sl, tp_: tp_ >= 2,
    "declive>=15 ou TPI90>=2": lambda sl, tp_: (sl >= 15) | (tp_ >= 2),
    "declive>=20 ou TPI90>=2": lambda sl, tp_: (sl >= 20) | (tp_ >= 2),
}
res["regras"] = {}
for nome, fn in regras.items():
    hit = {}
    for k, p in perf.items():
        hit[k] = bool(fn(np.array(p["srtm_declive_pct"]), np.array(p["tpi_90m_m"])))
    n = min(s_u.shape[0], TPI90_u.shape[0]), min(s_u.shape[1], TPI90_u.shape[1])
    n2 = min(s_mun.shape[0], TPI90_m.shape[0]), min(s_mun.shape[1], TPI90_m.shape[1])
    fu = float(np.nanmean(fn(s_u[:n[0], :n[1]], TPI90_u[:n[0], :n[1]]).astype(float)))
    fm = float(np.nanmean(fn(s_mun[:n2[0], :n2[1]], TPI90_m[:n2[0], :n2[1]]).astype(float)))
    res["regras"][nome] = dict(marca_perfil5_profundo=hit["perfil5_Latossolo_terco_medio"], marca_perfil6_regolitico=hit["perfil6_Neossolo_Regolitico_terco_inferior"],
                               marca_perfil7_litolico=hit["perfil7_Neossolo_Litolico_topo"], frac_area_udesc=fu, frac_entorno_smo=fm)
json.dump(res, open(AQUI / "res_06_srtm.json", "w"), indent=1)
for nome, r in res["regras"].items():
    print(f"{nome:26s} perfil5(profundo) {r['marca_perfil5_profundo']!s:5} perfil6(RR) {r['marca_perfil6_regolitico']!s:5} perfil7(RL) {r['marca_perfil7_litolico']!s:5} | área UDESC {100*r['frac_area_udesc']:.0f}% (mapa: 38%) | entorno 15 km {100*r['frac_entorno_smo']:.0f}%")
