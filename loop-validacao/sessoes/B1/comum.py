"""Funções comuns da sessão B1: leitura do NASA POWER, ET0 FAO-56 e balanço hídrico.

Adaptado de prototipo/modelo/risco.py (Quixadá) para Santa Catarina.
"""
import json, math, datetime as dt
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]  # loop-validacao/
DADOS = RAIZ / "dados"

LOCAIS = {
    "smo": dict(nome="São Miguel do Oeste", arq="power_sao_miguel_do_oeste.json", lat=-26.725, alt=533.0),
    "itu": dict(nome="Ituporanga", arq="power_ituporanga.json", lat=-27.414, alt=677.0),
}


def e_sat(t):
    return 0.6108 * math.exp(17.27 * t / (t + 237.3))


class Local:
    def __init__(self, chave):
        cfg = LOCAIS[chave]
        self.nome, self.lat, self.alt = cfg["nome"], cfg["lat"], cfg["alt"]
        self.P = json.load(open(DADOS / cfg["arq"]))["properties"]["parameter"]
        self.dias = sorted(self.P["PRECTOTCORR"].keys())
        self.chuva = {d: max(0.0, self.P["PRECTOTCORR"][d]) for d in self.dias}
        self.tmin = self.P["T2M_MIN"]
        self.tmax = self.P["T2M_MAX"]
        self.t2m = self.P["T2M"]
        self.et0 = {d: self._et0(d) for d in self.dias if self.P["ALLSKY_SFC_SW_DWN"][d] != -999}

    def _et0(self, day):
        P = self.P
        d = dt.date(int(day[:4]), int(day[4:6]), int(day[6:]))
        tmax, tmin, tm = P["T2M_MAX"][day], P["T2M_MIN"][day], P["T2M"][day]
        rh, u2, rs = P["RH2M"][day], P["WS2M"][day], P["ALLSKY_SFC_SW_DWN"][day]
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
        return max(0.5, num / (delta + gam * (1 + 0.34 * u2)))


def k(d):
    return d.strftime("%Y%m%d")


# ---------- culturas (FAO-56 tab. 11/12 e FAO-33; ajustadas ao Sul do Brasil) ----------
CULTURAS = {
    # milho de verão, híbrido de ciclo médio (~130 dias até a maturação)
    "milho": dict(nome="Milho", fases=(25, 35, 40, 30), kc=(0.30, 1.20, 0.60), ky=(0.4, 0.4, 1.5, 0.5), raiz=1.0),
    # cebola de bulbo, transplante (FAO-56: 15/25/70/40)
    "cebola": dict(nome="Cebola", fases=(15, 25, 70, 40), kc=(0.70, 1.05, 0.75), ky=(0.45, 0.45, 0.8, 0.3), raiz=0.4),
}
SOLOS = {"arenoso": 65, "medio": 125, "argiloso": 175}  # mm/m, GAEZ v5 (valores do protótipo)
P_DEPL = {"milho": 0.55, "cebola": 0.30}  # FAO-56 tab. 22


def kc_do_dia(c, i):
    ini, dev, mid, late = c["fases"]
    a, b, e = c["kc"]
    if i < ini: return a
    if i < ini + dev: return a + (b - a) * (i - ini) / dev
    if i < ini + dev + mid: return b
    return b + (e - b) * (i - ini - dev - mid) / late


def fase_do_dia(c, i):
    acum = 0
    for f, n in enumerate(c["fases"]):
        acum += n
        if i < acum: return f
    return 3


def simular(L, cultura, solo, plantio, s_ini_frac=0.7):
    """Balanço de balde. No Sul o solo não começa seco: parte de 70% do CAD [ESTIMATIVA]."""
    c = CULTURAS[cultura]
    cad = SOLOS[solo] * c["raiz"]
    p = P_DEPL[cultura]
    s = s_ini_frac * cad
    n = sum(c["fases"])
    eta_f, etc_f = [0.0] * 4, [0.0] * 4
    excesso = 0.0
    for i in range(n):
        key = k(plantio + dt.timedelta(i))
        if key not in L.et0: return None
        etc = kc_do_dia(c, i) * L.et0[key]
        s += L.chuva[key]
        if s > cad:
            excesso += s - cad
            s = cad
        ks = min(1.0, s / ((1 - p) * cad))
        eta = etc * ks
        s = max(0.0, s - eta)
        f = fase_do_dia(c, i)
        eta_f[f] += eta
        etc_f[f] += etc
    isna = [a / b if b else 1 for a, b in zip(eta_f, etc_f)]
    y = 1.0
    for f in range(4):
        y *= max(0.0, 1 - c["ky"][f] * (1 - isna[f]))
    return dict(y=y, isna=isna, excesso=excesso)


# ---------- estatística simples (sem numpy/scipy) ----------
def ranks(v):
    o = sorted(range(len(v)), key=lambda i: v[i])
    r = [0.0] * len(v)
    i = 0
    while i < len(o):
        j = i
        while j + 1 < len(o) and v[o[j + 1]] == v[o[i]]: j += 1
        for t in range(i, j + 1): r[o[t]] = (i + j) / 2 + 1
        i = j + 1
    return r


def pearson(a, b):
    n = len(a)
    ma, mb = sum(a) / n, sum(b) / n
    sab = sum((x - ma) * (y - mb) for x, y in zip(a, b))
    sa = math.sqrt(sum((x - ma) ** 2 for x in a))
    sb = math.sqrt(sum((y - mb) ** 2 for y in b))
    return sab / (sa * sb) if sa and sb else 0.0


def spearman(a, b):
    return pearson(ranks(a), ranks(b))


def p_perm(a, b, n=5000, seed=1, lado="duas"):
    """Valor-p por permutação para Spearman."""
    import random
    rnd = random.Random(seed)
    r0 = spearman(a, b)
    bb = list(b)
    cont = 0
    for _ in range(n):
        rnd.shuffle(bb)
        r = spearman(a, bb)
        if lado == "duas" and abs(r) >= abs(r0): cont += 1
        elif lado == "neg" and r <= r0: cont += 1
        elif lado == "pos" and r >= r0: cont += 1
    return (cont + 1) / (n + 1)


def sem_tendencia(serie, janela=9):
    """Rendimento relativo à mediana móvel centrada (robusta a anos extremos)."""
    anos = sorted(serie)
    out = {}
    for a in anos:
        viz = [serie[b] for b in anos if abs(b - a) <= janela // 2]
        viz.sort()
        m = viz[len(viz) // 2] if len(viz) % 2 else (viz[len(viz) // 2 - 1] + viz[len(viz) // 2]) / 2
        out[a] = serie[a] / m
    return out


def acerto_piores(modelo, obs, n):
    """Quantos dos n piores anos observados estão entre os n piores do modelo."""
    anos = sorted(set(modelo) & set(obs))
    po = set(sorted(anos, key=lambda a: obs[a])[:n])
    pm = set(sorted(anos, key=lambda a: modelo[a])[:n])
    return len(po & pm), sorted(po), sorted(pm)


def pam(caminho, produto, municipio):
    d = json.load(open(caminho))[1:]
    out = {}
    for r in d:
        if r["D4C"] == produto and r["D1C"] == municipio and r["D2N"].startswith("Rendimento") and r["V"] not in ("-", "...", "X"):
            out[int(r["D3N"])] = float(r["V"])
    return out
