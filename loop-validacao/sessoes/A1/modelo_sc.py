#!/usr/bin/env python3
"""Balanço hídrico por fase (FAO-56 + FAO-33) + risco de geada, só com NASA POWER.

Adaptado de prototipo/modelo/risco.py (Quixadá) para Santa Catarina.
Mudanças: local e altitude lidos do JSON, anos 1984+ (radiação), solo começa
cheio 60 dias antes do plantio (Sul úmido), culturas e ciclos do Sul, geada.
Parâmetros de cultura são [ESTIMATIVA] a partir da FAO-56 (tab. 11/12) e FAO-33.
"""
import json, math, datetime as dt
from pathlib import Path

DADOS = Path(__file__).resolve().parents[2] / "dados"


def e_sat(t): return 0.6108 * math.exp(17.27 * t / (t + 237.3))


class Local:
    def __init__(self, arquivo):
        d = json.load(open(DADOS / arquivo))
        self.lon, self.lat, self.alt = d["geometry"]["coordinates"]
        P = d["properties"]["parameter"]
        self.P = P
        self.chuva, self.et0, self.tmin = {}, {}, {}
        for k in sorted(P["PRECTOTCORR"]):
            day = dt.date(int(k[:4]), int(k[4:6]), int(k[6:]))
            vals = [P[x][k] for x in ("PRECTOTCORR", "T2M", "T2M_MAX", "T2M_MIN", "RH2M", "WS2M", "ALLSKY_SFC_SW_DWN")]
            if any(v == -999 for v in vals):
                continue
            self.chuva[day] = max(0.0, vals[0])
            self.tmin[day] = vals[3]
            self.et0[day] = self._et0(day, *vals[1:])

    def _et0(self, d, tm, tmax, tmin, rh, u2, rs):
        es = (e_sat(tmax) + e_sat(tmin)) / 2
        ea = rh / 100 * e_sat(tm)
        delta = 4098 * e_sat(tm) / (tm + 237.3) ** 2
        pr = 101.3 * ((293 - 0.0065 * self.alt) / 293) ** 5.26
        gam = 0.000665 * pr
        j = d.timetuple().tm_yday
        phi = math.radians(self.lat)
        dr = 1 + 0.033 * math.cos(2 * math.pi * j / 365)
        dec = 0.409 * math.sin(2 * math.pi * j / 365 - 1.39)
        ws = math.acos(max(-1, min(1, -math.tan(phi) * math.tan(dec))))
        ra = 24 * 60 / math.pi * 0.082 * dr * (ws * math.sin(phi) * math.sin(dec) + math.cos(phi) * math.cos(dec) * math.sin(ws))
        rso = (0.75 + 2e-5 * self.alt) * ra
        rnl = 4.903e-9 * (((tmax + 273.16) ** 4 + (tmin + 273.16) ** 4) / 2) * (0.34 - 0.14 * math.sqrt(max(ea, 0.01))) * (1.35 * min(rs / rso, 1) - 0.35)
        rn = 0.77 * rs - rnl
        num = 0.408 * delta * rn + gam * 900 / (tm + 273) * u2 * (es - ea)
        return max(0.3, num / (delta + gam * (1 + 0.34 * u2)))


# fases (ini, dev, mid, late) em dias; kc (ini, mid, end); ky por fase; raiz (m); geada: sensível?
CULTURAS = {
    "milho_safra":     dict(nome="Milho safra (ciclo normal)", fases=(25, 40, 45, 30), kc=(0.30, 1.20, 0.60), ky=(0.4, 0.4, 1.5, 0.5), raiz=1.0, geada=True),
    "milho_safrinha":  dict(nome="Milho safrinha (precoce)",   fases=(20, 35, 35, 25), kc=(0.30, 1.20, 0.60), ky=(0.4, 0.4, 1.5, 0.5), raiz=1.0, geada=True),
    "feijao":          dict(nome="Feijão",                     fases=(15, 25, 35, 15), kc=(0.40, 1.15, 0.35), ky=(0.2, 0.2, 1.1, 0.75), raiz=0.6, geada=True),
    "sorgo":           dict(nome="Sorgo",                      fases=(20, 35, 40, 30), kc=(0.30, 1.05, 0.55), ky=(0.2, 0.2, 0.55, 0.45), raiz=1.0, geada=True),
    "pastagem_inv":    dict(nome="Pastagem de inverno (aveia+azevém)", fases=(20, 30, 70, 30), kc=(0.40, 1.00, 0.90), ky=(0.5, 0.9, 0.9, 0.5), raiz=0.6, geada=False),
}
SOLOS = {"arenoso": 65, "medio": 125, "argiloso": 175}  # mm/m (GAEZ, como no protótipo)
P_DEPL = 0.5
LIMIAR_COLHE = 0.6
T_GEADA = 2.0


def kc_do_dia(c, k):
    ini, dev, mid, late = c["fases"]; a, b, e = c["kc"]
    if k < ini: return a
    if k < ini + dev: return a + (b - a) * (k - ini) / dev
    if k < ini + dev + mid: return b
    return b + (e - b) * (k - ini - dev - mid) / late


def fase_do_dia(c, k):
    acum = 0
    for i, n in enumerate(c["fases"]):
        acum += n
        if k < acum: return i
    return 3


def simular(L, cultura, solo, plantio, t_geada=T_GEADA, dias_antes=60):
    c = CULTURAS[cultura]
    cad = SOLOS[solo] * c["raiz"]
    # solo começa cheio `dias_antes` dias antes e perde água como solo nu
    s = cad
    d = plantio - dt.timedelta(dias_antes)
    while d < plantio:
        if d not in L.chuva: return None
        s = min(cad, s + L.chuva[d])
        s = max(0.0, s - 0.5 * L.et0[d] * min(1.0, s / (0.5 * cad)))
        d += dt.timedelta(1)
    n = sum(c["fases"])
    et_a, et_c = [0.0] * 4, [0.0] * 4
    geada_fase = None
    for k in range(n):
        d = plantio + dt.timedelta(k)
        if d not in L.chuva: return None
        etc = kc_do_dia(c, k) * L.et0[d]
        s = min(cad, s + L.chuva[d])
        ks = min(1.0, s / ((1 - P_DEPL) * cad))
        eta = etc * ks
        s = max(0.0, s - eta)
        f = fase_do_dia(c, k)
        et_a[f] += eta; et_c[f] += etc
        if c["geada"] and geada_fase is None and 7 <= k <= 0.9 * n and L.tmin[d] <= t_geada:
            geada_fase = f
    isna = [a / b if b else 1 for a, b in zip(et_a, et_c)]
    y = 1.0
    for i in range(4):
        y *= max(0.0, 1 - c["ky"][i] * (1 - isna[i]))
    return dict(y=y, isna=isna, geada=geada_fase is not None, geada_fase=geada_fase)


def dia_meio(dec):
    """Decêndio ZARC (1..36) -> (mes, dia do meio)."""
    m = (dec - 1) // 3 + 1
    return m, (5, 15, 25)[(dec - 1) % 3]


def data_plantio(ano_safra, dec):
    """ano_safra = ano de início da safra de verão (ago..dez no ano, jan..jul no ano+1)."""
    m, d = dia_meio(dec)
    return dt.date(ano_safra if m >= 8 else ano_safra + 1, m, d)
