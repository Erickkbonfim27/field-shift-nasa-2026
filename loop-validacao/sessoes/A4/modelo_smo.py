#!/usr/bin/env python3
"""Balanço hídrico FAO-56 + FAO-33 para São Miguel do Oeste (SC).

Adaptado de prototipo/modelo/risco.py (Quixadá). Mudanças: ponto de SMO, balde contínuo,
mais culturas (soja, trigo, aveia, azevém), geada, solo raso.
Fonte única de clima: NASA POWER diário (comunidade AG), 1984-2025.
"""
import json, math, datetime as dt
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DADOS = AQUI.parent.parent / "dados"
LAT, ALT = -26.725, 533.0

P = json.load(open(DADOS / "power_sao_miguel_do_oeste.json"))["properties"]["parameter"]


def key(d): return d.strftime("%Y%m%d")


def e_sat(t): return 0.6108 * math.exp(17.27 * t / (t + 237.3))


def _et0(k):
    d = dt.date(int(k[:4]), int(k[4:6]), int(k[6:]))
    tmax, tmin, tm = P["T2M_MAX"][k], P["T2M_MIN"][k], P["T2M"][k]
    rh, u2, rs = P["RH2M"][k], P["WS2M"][k], P["ALLSKY_SFC_SW_DWN"][k]
    if rs < 0: return None
    es = (e_sat(tmax) + e_sat(tmin)) / 2
    ea = rh / 100 * e_sat(tm)
    delta = 4098 * e_sat(tm) / (tm + 237.3) ** 2
    pr = 101.3 * ((293 - 0.0065 * ALT) / 293) ** 5.26
    gam = 0.000665 * pr
    j = d.timetuple().tm_yday
    phi = math.radians(LAT)
    dr = 1 + 0.033 * math.cos(2 * math.pi * j / 365)
    dec = 0.409 * math.sin(2 * math.pi * j / 365 - 1.39)
    ws = math.acos(max(-1, min(1, -math.tan(phi) * math.tan(dec))))
    ra = 24 * 60 / math.pi * 0.082 * dr * (ws * math.sin(phi) * math.sin(dec) + math.cos(phi) * math.cos(dec) * math.sin(ws))
    rso = (0.75 + 2e-5 * ALT) * ra
    rnl = 4.903e-9 * (((tmax + 273.16) ** 4 + (tmin + 273.16) ** 4) / 2) * (0.34 - 0.14 * math.sqrt(max(ea, 0.01))) * (1.35 * min(rs / rso, 1) - 0.35)
    rn = 0.77 * rs - rnl
    num = 0.408 * delta * rn + gam * 900 / (tm + 273) * u2 * (es - ea)
    return max(0.3, num / (delta + gam * (1 + 0.34 * u2)))


ET0 = {}
for k in P["PRECTOTCORR"]:
    v = _et0(k)
    if v is not None: ET0[k] = v
CHUVA = {k: max(0.0, v) for k, v in P["PRECTOTCORR"].items()}
TMIN = P["T2M_MIN"]
TMED = P["T2M"]
GWR = P["GWETROOT"]

# fases (ini, dev, mid, late) em dias; kc (ini, mid, end); ky por fase; raiz (m); p (depleção)
# Fontes: FAO-56 tab. 11/12/22 e FAO-33 tab. 24. Sorgo: valores GENÉRICOS da FAO (não calibrados para SC).
CULT = {
    "milho_sil": dict(nome="Milho silagem", fases=(20, 35, 40, 15), kc=(0.30, 1.20, 0.90), ky=(0.4, 0.4, 1.5, 0.5), raiz=1.0, p=0.55),
    "milho_gr":  dict(nome="Milho grão", fases=(25, 40, 45, 30), kc=(0.30, 1.20, 0.50), ky=(0.4, 0.4, 1.5, 0.5), raiz=1.0, p=0.55),
    "sorgo_sil": dict(nome="Sorgo silagem", fases=(20, 35, 40, 15), kc=(0.30, 1.05, 0.80), ky=(0.2, 0.2, 0.55, 0.45), raiz=1.0, p=0.55),
    "soja":      dict(nome="Soja", fases=(15, 25, 50, 30), kc=(0.40, 1.15, 0.50), ky=(0.2, 0.2, 0.8, 1.0), raiz=0.8, p=0.5),
    "trigo":     dict(nome="Trigo", fases=(20, 30, 50, 30), kc=(0.40, 1.15, 0.30), ky=(0.2, 0.2, 0.6, 0.5), raiz=0.8, p=0.55),
    "aveia":     dict(nome="Aveia (pastejo/cobertura)", fases=(20, 30, 50, 20), kc=(0.40, 1.00, 0.40), ky=(0.2, 0.2, 0.5, 0.3), raiz=0.6, p=0.55),
    "azevem":    dict(nome="Azevém (pastagem)", fases=(20, 30, 110, 20), kc=(0.50, 0.95, 0.90), ky=(0.2, 0.3, 0.6, 0.3), raiz=0.5, p=0.6),
}
SOLOS = {"argiloso": (175, None), "medio": (125, None), "raso": (175, 0.5)}  # (mm/m, limite de raiz em m)
FASES_NOME = ["emergência", "crescimento", "floração/enchimento", "final"]
INVERNO = {"trigo", "aveia", "azevem"}  # tolerantes a geada no vegetativo; geada na floração do trigo NÃO modelada
GEADA = 2.0  # T2M_MIN em °C; geada na relva costuma ocorrer com o ar a 2 m abaixo de ~2-3 °C


def kc_dia(c, k):
    ini, dev, mid, late = c["fases"]; a, b, e = c["kc"]
    if k < ini: return a
    if k < ini + dev: return a + (b - a) * (k - ini) / dev
    if k < ini + dev + mid: return b
    return b + (e - b) * (k - ini - dev - mid) / late


def fase_dia(c, k):
    ac = 0
    for i, n in enumerate(c["fases"]):
        ac += n
        if k < ac: return i
    return 3


def cad_de(c, solo):
    mm_m, lim = SOLOS[solo]
    z = c["raiz"] if lim is None else min(c["raiz"], lim)
    return mm_m * z


def simular(cultura, solo, plantio, s_ini=None, kc_mult=1.0, ky_mult=1.0, raiz=None):
    """Simula uma cultura. Se s_ini for None, solo começa cheio 60 dias antes e perde água como solo nu."""
    c = dict(CULT[cultura])
    if raiz: c["raiz"] = raiz
    cad = cad_de(c, solo)
    if s_ini is None:
        s = cad
        d = plantio - dt.timedelta(60)
        while d < plantio:
            k = key(d)
            if k not in ET0: return None
            s = min(cad, s + CHUVA[k])
            s = max(0.0, s - 0.3 * ET0[k] * min(1.0, s / (0.5 * cad)))
            d += dt.timedelta(1)
    else:
        s = min(cad, s_ini)
    out = _ciclo(c, cad, plantio, s, kc_mult, ky_mult)
    return out


def _ciclo(c, cad, plantio, s, kc_mult=1.0, ky_mult=1.0):
    s0 = s
    n = sum(c["fases"])
    eta = [0.0] * 4; etc = [0.0] * 4; chuva = 0.0; drena = 0.0
    geada = False
    for k in range(n):
        d = plantio + dt.timedelta(k); kk = key(d)
        if kk not in ET0: return None
        f = fase_dia(c, k)
        e_c = kc_dia(c, k) * kc_mult * ET0[kk]
        chuva += CHUVA[kk]
        s += CHUVA[kk]
        if s > cad: drena += s - cad; s = cad
        ks = min(1.0, s / ((1 - c["p"]) * cad))
        e_a = e_c * ks
        s = max(0.0, s - e_a)
        eta[f] += e_a; etc[f] += e_c
        if f in (1, 2) and TMIN[kk] <= GEADA: geada = True
    isna = [a / b if b else 1 for a, b in zip(eta, etc)]
    y = 1.0
    for i in range(4):
        y *= max(0.0, 1 - min(1.0, c["ky"][i] * ky_mult) * (1 - isna[i]))
    if geada: y *= 0.3
    return dict(y=y, isna=isna, etc=sum(etc), eta=sum(eta), chuva=chuva, drena=drena, s_fim=s, s_ini=s0, cad=cad, geada=geada,
                fim=plantio + dt.timedelta(n))


def pousio(solo, ini, fim, s, cad):
    """Solo sem cultura (palhada/plantas espontâneas): evaporação 0,3*ET0 limitada pela água."""
    d = ini; ev = 0.0; drena = 0.0; demanda = 0.0
    while d < fim:
        k = key(d)
        if k not in ET0: return None
        s += CHUVA[k]
        if s > cad: drena += s - cad; s = cad
        e = 0.3 * ET0[k] * min(1.0, s / (0.5 * cad))
        demanda += 0.3 * ET0[k]
        s = max(0.0, s - e); ev += e
        d += dt.timedelta(1)
    return s, ev, drena
