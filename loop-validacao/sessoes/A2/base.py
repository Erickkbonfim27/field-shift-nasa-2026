#!/usr/bin/env python3
"""A2 · funções comuns: ET0 (FAO-56, de prototipo/modelo/risco.py), métricas por safra,
milho simulado (balanço hídrico FAO-56/33 de risco.py), ONI (NOAA, só para separar anos),
IBGE PAM (só conferência) e estatística (Brier LOO, Fisher)."""
import json, math, datetime as dt
from pathlib import Path
import numpy as np
from scipy import stats

AQUI = Path(__file__).resolve().parent
DADOS = AQUI.parent.parent / "dados"

LOCAIS = {
    "smo": dict(arq="power_sao_miguel_do_oeste.json", lat=-26.725, alt=533.0, nome="São Miguel do Oeste"),
    "itu": dict(arq="power_ituporanga.json", lat=-27.414, alt=None, nome="Ituporanga"),
}


def carregar(local="smo"):
    cfg = LOCAIS[local]
    d = json.load(open(DADOS / cfg["arq"]))
    P = d["properties"]["parameter"]
    alt = cfg["alt"] if cfg["alt"] is not None else d["geometry"]["coordinates"][2]
    lat = cfg["lat"]

    def e_sat(t): return 0.6108 * math.exp(17.27 * t / (t + 237.3))

    def et0(day):
        y, m, dd = int(day[:4]), int(day[4:6]), int(day[6:])
        tmax, tmin, tm = P["T2M_MAX"][day], P["T2M_MIN"][day], P["T2M"][day]
        rh, u2, rs = P["RH2M"][day], P["WS2M"][day], P["ALLSKY_SFC_SW_DWN"][day]
        if -999 in (tmax, tmin, tm, rh, u2, rs): return None
        es = (e_sat(tmax) + e_sat(tmin)) / 2
        ea = rh / 100 * e_sat(tm)
        delta = 4098 * e_sat(tm) / (tm + 237.3) ** 2
        pr = 101.3 * ((293 - 0.0065 * alt) / 293) ** 5.26
        gam = 0.000665 * pr
        j = dt.date(y, m, dd).timetuple().tm_yday
        phi = math.radians(lat)
        dr = 1 + 0.033 * math.cos(2 * math.pi * j / 365)
        dec = 0.409 * math.sin(2 * math.pi * j / 365 - 1.39)
        ws = math.acos(max(-1, min(1, -math.tan(phi) * math.tan(dec))))
        ra = 24 * 60 / math.pi * 0.082 * dr * (ws * math.sin(phi) * math.sin(dec) + math.cos(phi) * math.cos(dec) * math.sin(ws))
        rso = (0.75 + 2e-5 * alt) * ra
        rnl = 4.903e-9 * (((tmax + 273.16) ** 4 + (tmin + 273.16) ** 4) / 2) * (0.34 - 0.14 * math.sqrt(max(ea, 0.01))) * (1.35 * min(rs / rso, 1) - 0.35)
        rn = 0.77 * rs - rnl
        num = 0.408 * delta * rn + gam * 900 / (tm + 273) * u2 * (es - ea)
        return max(0.5, num / (delta + gam * (1 + 0.34 * u2)))

    dias = sorted(P["PRECTOTCORR"])
    chuva = {k: max(0.0, P["PRECTOTCORR"][k]) for k in dias}
    et = {k: et0(k) for k in dias}
    return dict(P=P, chuva=chuva, et0=et, dias=dias, nome=cfg["nome"])


def _intervalo(a, b):
    d = a
    while d <= b:
        yield d.strftime("%Y%m%d")
        d += dt.timedelta(1)


def soma(serie, a, b):
    vals = [serie.get(k) for k in _intervalo(a, b)]
    if any(v is None for v in vals): return None
    return float(sum(vals))


def media(serie, a, b):
    vals = [serie.get(k) for k in _intervalo(a, b)]
    if any(v is None or v == -999 for v in vals): return None
    return float(np.mean(vals))


# ---------- milho simulado (mesmo método de risco.py, solo argiloso, plantio 1/out) ----------
MILHO = dict(fases=(20, 30, 30, 20), kc=(0.30, 1.20, 0.60), ky=(0.4, 0.4, 1.5, 0.5), raiz=1.0)
CAD_ARGILOSO = 175  # mm/m (mesma tabela GAEZ de risco.py)


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


def milho_simulado(D, ano, mes=10, dia=1):
    c = MILHO; cad = CAD_ARGILOSO * c["raiz"]
    # solo começa cheio em 1/ago e perde água em pousio até o plantio (inverno chuvoso no Oeste de SC)
    s = cad
    for k in _intervalo(dt.date(ano, 8, 1), dt.date(ano, mes, dia) - dt.timedelta(1)):
        if D["et0"][k] is None: return None
        s = min(cad, s + D["chuva"][k])
        s = max(0.0, s - 0.35 * D["et0"][k] * min(1.0, s / (0.5 * cad)))
    pl = dt.date(ano, mes, dia)
    eta, etc = [0.0] * 4, [0.0] * 4
    for k in range(sum(c["fases"])):
        key = (pl + dt.timedelta(k)).strftime("%Y%m%d")
        e0 = D["et0"].get(key)
        if e0 is None: return None
        kc = kc_do_dia(c, k); ec = kc * e0
        s = min(cad, s + D["chuva"][key])
        ks = min(1.0, s / (0.5 * cad))
        ea = ec * ks; s = max(0.0, s - ea)
        f = fase_do_dia(c, k); eta[f] += ea; etc[f] += ec
    y = 1.0
    for i in range(4):
        y *= max(0.0, 1 - c["ky"][i] * (1 - eta[i] / etc[i]))
    return y


# ---------- métricas por safra (Y = ano de dezembro) ----------
def tabela_safras(D, anos):
    linhas = []
    for Y in anos:
        dez1, jan31 = dt.date(Y, 12, 1), dt.date(Y + 1, 1, 31)
        if jan31 > dt.date(2025, 12, 31): continue
        r = dict(Y=Y)
        r["chuva_dj"] = soma(D["chuva"], dez1, jan31)
        et = soma(D["et0"], dez1, jan31)
        r["bh_dj"] = None if et is None else r["chuva_dj"] - et
        r["gwr_dj"] = media(D["P"]["GWETROOT"], dez1, jan31)
        r["gwt_dj"] = media(D["P"]["GWETTOP"], dez1, jan31)
        r["gwr_nov"] = media(D["P"]["GWETROOT"], dt.date(Y, 11, 1), dt.date(Y, 11, 30))
        r["gwr_nov15"] = media(D["P"]["GWETROOT"], dt.date(Y, 11, 1), dt.date(Y, 11, 15))
        r["gwt_nov"] = media(D["P"]["GWETTOP"], dt.date(Y, 11, 1), dt.date(Y, 11, 30))
        r["gwp_nov"] = media(D["P"]["GWETPROF"], dt.date(Y, 11, 1), dt.date(Y, 11, 30))
        r["chuva_nov"] = soma(D["chuva"], dt.date(Y, 11, 1), dt.date(Y, 11, 30))
        r["milho"] = milho_simulado(D, Y)
        linhas.append(r)
    return linhas


# ---------- ONI (NOAA CPC) ----------
def oni():
    """Retorna {(estacao, ano): anom} e fases por estação com a regra NOAA (5 trimestres seguidos >= 0,5)."""
    seq = []
    for ln in open(AQUI / "externo/oni.ascii.txt").read().splitlines()[1:]:
        p = ln.split()
        if len(p) == 4: seq.append((p[0], int(p[1]), float(p[3])))
    fase = {}
    n = len(seq)
    for sinal, nome in ((1, "nino"), (-1, "nina")):
        i = 0
        while i < n:
            j = i
            while j < n and sinal * seq[j][2] >= 0.5: j += 1
            if j - i >= 5:
                for k in range(i, j): fase[(seq[k][0], seq[k][1])] = nome
            i = max(j, i + 1)
    val = {(s, y): a for s, y, a in seq}
    return val, fase


def fase_simples(a):
    return "nino" if a >= 0.5 else ("nina" if a <= -0.5 else "neutro")


# ---------- IBGE PAM (conferência) ----------
def pam(arq="externo/pam_milho_micro.json"):
    d = json.load(open(AQUI / arq))[1:]
    out = {}
    for x in d:
        try: out[int(x["D3N"])] = float(x["V"])
        except ValueError: pass
    anos = sorted(out)
    # anomalia: razão para a mediana móvel centrada de 7 anos (tira a tendência tecnológica)
    anom = {}
    for a in anos:
        viz = [out[b] for b in range(a - 3, a + 4) if b in out and b != a]
        if len(viz) >= 4: anom[a] = out[a] / float(np.median(viz))
    return out, anom


# ---------- estatística ----------
def tercil_inferior(vals):
    return float(np.percentile(vals, 100 / 3))


def brier(p, o):
    p, o = np.asarray(p, float), np.asarray(o, float)
    return float(np.mean((p - o) ** 2))


def fisher_uni(a_sim, a_tot, b_sim, b_tot):
    """H1: proporção em A > proporção em B."""
    tab = [[a_sim, a_tot - a_sim], [b_sim, b_tot - b_sim]]
    return float(stats.fisher_exact(tab, alternative="greater")[1])


def logit_fit(x, y, l2=1e-3):
    x = np.asarray(x, float); y = np.asarray(y, float)
    mu, sd = x.mean(), x.std() or 1.0
    z = (x - mu) / sd
    X = np.column_stack([np.ones_like(z), z]); w = np.zeros(2)
    for _ in range(100):
        p = 1 / (1 + np.exp(-X @ w))
        g = X.T @ (y - p) - l2 * np.r_[0, w[1]]
        H = -(X.T * (p * (1 - p))) @ X - l2 * np.diag([0, 1])
        step = np.linalg.solve(H, g); w -= step
        if np.abs(step).max() < 1e-8: break
    return lambda xn: 1 / (1 + np.exp(-(w[0] + w[1] * (np.asarray(xn, float) - mu) / sd)))
