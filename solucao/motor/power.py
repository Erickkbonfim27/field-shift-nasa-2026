"""Leitura do NASA POWER (diário, comunidade AG) e ET0 Penman-Monteith FAO-56.

As fórmulas são as mesmas de prototipo/modelo/risco.py, loop-validacao/sessoes/B3/comum.py,
solucao/validacao/V4/v4_motor.py e loop-validacao/sessoes/A4/modelo_smo.py. Os scripts
validados diferem só em dois detalhes, que aqui viram parâmetros:
- altitude usada na pressão (altitude da grade do POWER ou da sede do município);
- piso da ET0 diária (0,5 mm em risco.py/B3/V4; 0,3 mm em A4/V3).
"""
import math
import datetime as dt
from . import config as C

FALTA = -999


def e_sat(t):
    """Pressão de saturação do vapor (kPa), FAO-56 eq. 11."""
    return 0.6108 * math.exp(17.27 * t / (t + 237.3))


def radiacao_ra(lat_graus, doy):
    """Radiação extraterrestre Ra (MJ m-2 dia-1), FAO-56 eq. 21-25."""
    phi = math.radians(lat_graus)
    dr = 1 + 0.033 * math.cos(2 * math.pi * doy / 365)
    dec = 0.409 * math.sin(2 * math.pi * doy / 365 - 1.39)
    ws = math.acos(max(-1.0, min(1.0, -math.tan(phi) * math.tan(dec))))
    return 24 * 60 / math.pi * 0.082 * dr * (
        ws * math.sin(phi) * math.sin(dec) + math.cos(phi) * math.cos(dec) * math.sin(ws))


def et0_fao56(tmax, tmin, tmed, rh, u2, rs, lat, alt, doy, piso=0.5):
    """ET0 diária (mm). rs em MJ m-2 dia-1 (ALLSKY_SFC_SW_DWN da comunidade AG).
    ea = RH2M/100 * e_sat(T2M), como nos scripts validados (o POWER não dá RH máx e mín)."""
    es = (e_sat(tmax) + e_sat(tmin)) / 2
    ea = rh / 100 * e_sat(tmed)
    delta = 4098 * e_sat(tmed) / (tmed + 237.3) ** 2
    gam = 0.000665 * 101.3 * ((293 - 0.0065 * alt) / 293) ** 5.26
    ra = radiacao_ra(lat, doy)
    rso = (0.75 + 2e-5 * alt) * ra
    rnl = 4.903e-9 * (((tmax + 273.16) ** 4 + (tmin + 273.16) ** 4) / 2) * \
        (0.34 - 0.14 * math.sqrt(max(ea, 0.01))) * (1.35 * min(rs / rso, 1) - 0.35)
    rn = 0.77 * rs - rnl
    num = 0.408 * delta * rn + gam * 900 / (tmed + 273) * u2 * (es - ea)
    return max(piso, num / (delta + gam * (1 + 0.34 * u2)))


def chave(d):
    return d.strftime("%Y%m%d")


def data(k):
    return dt.date(int(k[:4]), int(k[4:6]), int(k[6:]))


class Power:
    """Série diária de um ponto do POWER.

    alt: altitude para a ET0 (None = altitude da grade no JSON).
    lat: latitude para a ET0 (None = do JSON).
    piso: piso da ET0 (mm/dia).
    """

    VARS_ET0 = ("T2M_MAX", "T2M_MIN", "T2M", "RH2M", "WS2M", "ALLSKY_SFC_SW_DWN")

    def __init__(self, caminho, alt=None, lat=None, piso=0.5):
        d = C.ler_json(caminho)
        lon, lat_j, alt_j = d["geometry"]["coordinates"]
        self.caminho = caminho
        self.lon, self.lat_grade, self.alt_grade = lon, lat_j, alt_j
        self.lat = lat if lat is not None else lat_j
        self.alt = alt if alt is not None else alt_j
        self.piso = piso
        self.P = d["properties"]["parameter"]
        self.dias = sorted(self.P["PRECTOTCORR"])
        self.chuva = {k: max(0.0, v) for k, v in self.P["PRECTOTCORR"].items() if v != FALTA}
        self.tmin = {k: v for k, v in self.P["T2M_MIN"].items() if v != FALTA}
        self.tmax = {k: v for k, v in self.P["T2M_MAX"].items() if v != FALTA}
        self._et0 = {}

    @property
    def periodo(self):
        return self.dias[0][:4] + "-" + self.dias[-1][:4]

    def et0(self, k):
        if k in self._et0:
            return self._et0[k]
        vals = [self.P[v].get(k, FALTA) for v in self.VARS_ET0]
        if FALTA in vals:
            self._et0[k] = None
            return None
        tmax, tmin, tm, rh, u2, rs = vals
        r = et0_fao56(tmax, tmin, tm, rh, u2, rs, self.lat, self.alt, data(k).timetuple().tm_yday, self.piso)
        self._et0[k] = r
        return r

    def primeiro_dia_com_et0(self):
        for k in self.dias:
            if self.et0(k) is not None:
                return k
        return None


def mesma_celula(pw_a, pw_b, var="T2M_MIN", tol=0.005):
    """Conta dias com valor diferente entre duas séries. 0 = mesma célula do POWER."""
    a, b = pw_a.P[var], pw_b.P[var]
    ks = sorted(set(a) & set(b))
    dif = sum(1 for k in ks if abs(a[k] - b[k]) > tol)
    return dict(dias_diferentes=dif, de=len(ks))
