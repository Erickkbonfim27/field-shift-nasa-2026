"""V5 · balanço hídrico do prototipo/modelo/risco.py, parametrizado por município.

Cópia fiel das funções de risco.py (ET0 Penman-Monteith, balde com Ks, Ky por fase, regra de
início de chuva). Só mudam: local (lat, altitude, arquivo POWER) e a janela de busca do início
de chuva (jan-abr no CE/PE/PB; nov-mar na BA). A fidelidade é testada em checa_fidelidade.py.
"""
import json, math, datetime as dt
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DADOS = AQUI / "dados"

# lat, altitude (m, aprox. da sede) [ESTIMATIVA], janela de início de chuva (mês/dia ini do ano anterior?, fim)
LOCAIS = {
    "quixada":      dict(nome="Quixadá (CE)",          lat=-4.97,  alt=190.0, ba=False),
    "quixeramobim": dict(nome="Quixeramobim (CE)",     lat=-5.20,  alt=197.0, ba=False),
    "crateus":      dict(nome="Crateús (CE)",          lat=-5.18,  alt=275.0, ba=False),
    "taua":         dict(nome="Tauá (CE)",             lat=-6.00,  alt=402.0, ba=False),
    "irece":        dict(nome="Irecê (BA)",            lat=-11.30, alt=740.0, ba=True),
    "serratalhada": dict(nome="Serra Talhada (PE)",    lat=-7.99,  alt=429.0, ba=False),
    "patos":        dict(nome="Patos (PB)",            lat=-7.02,  alt=250.0, ba=False),
    "bonfim":       dict(nome="Senhor do Bonfim (BA)", lat=-10.46, alt=415.0, ba=True),
}

CULTURAS = {
    "caupi": dict(nome="Feijão-caupi", fases=(10, 20, 25, 15), kc=(0.40, 1.05, 0.35), ky=(0.2, 0.2, 1.1, 0.75), raiz=0.6),
    "milho": dict(nome="Milho", fases=(20, 30, 30, 20), kc=(0.30, 1.20, 0.60), ky=(0.4, 0.4, 1.5, 0.5), raiz=1.0),
}
SOLOS = {"arenoso": 65, "medio": 125, "argiloso": 175}
P_DEPL = 0.5


def e_sat(t): return 0.6108 * math.exp(17.27 * t / (t + 237.3))
def k(d): return d.strftime("%Y%m%d")


class Local:
    def __init__(self, chave):
        c = LOCAIS[chave]
        self.chave, self.nome, self.lat, self.alt, self.ba = chave, c["nome"], c["lat"], c["alt"], c["ba"]
        self.P = json.load(open(DADOS / f"power_{chave}.json"))["properties"]["parameter"]
        self.dias = sorted(self.P["PRECTOTCORR"].keys())
        self.chuva = {d: max(0.0, self.P["PRECTOTCORR"][d]) for d in self.dias if self.P["PRECTOTCORR"][d] != -999}
        self.et0 = {}
        for d in self.dias:
            if self.P["ALLSKY_SFC_SW_DWN"][d] == -999 or d not in self.chuva: continue
            if any(self.P[v][d] == -999 for v in ("T2M", "T2M_MAX", "T2M_MIN", "RH2M", "WS2M")): continue
            self.et0[d] = self._et0(d)

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

    # ---- funções copiadas de risco.py ----
    def agua_no_solo_em(self, data, cad):
        s = 0.0
        d = dt.date(data.year - 1, 12, 1)
        while d < data:
            kk = k(d)
            if kk not in self.chuva or kk not in self.et0: d += dt.timedelta(1); continue
            s = min(cad, s + self.chuva[kk])
            s = max(0.0, s - 0.35 * self.et0[kk] * min(1.0, s / (0.5 * cad)) * 0.5)
            d += dt.timedelta(1)
        return s

    def inicio_chuva(self, ano):
        """Regra de Sivakumar adaptada (risco.py). Na BA a busca vai de 1/nov do ano anterior a 31/mar."""
        d = dt.date(ano - 1, 11, 1) if self.ba else dt.date(ano, 1, 1)
        fim = dt.date(ano, 3, 31) if self.ba else dt.date(ano, 4, 30)
        while d <= fim:
            ks = [k(d + dt.timedelta(i)) for i in range(3)]
            if all(x in self.chuva for x in ks) and sum(self.chuva[x] for x in ks) >= 20:
                ok, seco = True, 0
                for i in range(3, 33):
                    x = k(d + dt.timedelta(i))
                    if x not in self.chuva: ok = False; break
                    seco = seco + 1 if self.chuva[x] <= 2 else 0
                    if seco > 7: ok = False; break
                if ok: return d + dt.timedelta(2)
            d += dt.timedelta(1)
        return None

    def simular(self, cultura, solo, plantio):
        c = CULTURAS[cultura]
        cad = SOLOS[solo] * c["raiz"]
        s = self.agua_no_solo_em(plantio, cad)
        s0 = s
        n = sum(c["fases"])
        et_a, et_c = [0.0] * 4, [0.0] * 4
        for i in range(n):
            d = plantio + dt.timedelta(i)
            kk = k(d)
            if kk not in self.chuva or kk not in self.et0: return None
            etc = kc_do_dia(c, i) * self.et0[kk]
            s = min(cad, s + self.chuva[kk])
            ks = min(1.0, s / ((1 - P_DEPL) * cad)) if cad > 0 else 0
            eta = etc * ks
            s = max(0.0, s - eta)
            f = fase_do_dia(c, i)
            et_a[f] += eta
            et_c[f] += etc
        isna = [a / b if b else 1 for a, b in zip(et_a, et_c)]
        y = 1.0
        for f in range(4):
            y *= max(0.0, 1 - c["ky"][f] * (1 - isna[f]))
        return dict(y=y, isna=isna, agua_plantio=s0, chuva_ciclo=sum(self.chuva[k(plantio + dt.timedelta(i))] for i in range(n)))

    def chuva_janela(self, ano):
        """Linha de base: chuva bruta da estação chuvosa. CE/PE/PB: 1/jan-31/mai. BA: 1/nov(ano-1)-31/mar."""
        d0, d1 = (dt.date(ano - 1, 11, 1), dt.date(ano, 3, 31)) if self.ba else (dt.date(ano, 1, 1), dt.date(ano, 5, 31))
        tot, n = 0.0, 0
        for i in range((d1 - d0).days + 1):
            kk = k(d0 + dt.timedelta(i))
            if kk in self.chuva: tot += self.chuva[kk]; n += 1
        return tot if n >= 0.95 * ((d1 - d0).days + 1) else None


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


# ---------- estatística ----------
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
    sa = math.sqrt(sum((x - ma) ** 2 for x in a)); sb = math.sqrt(sum((y - mb) ** 2 for y in b))
    return sab / (sa * sb) if sa and sb else 0.0


def spearman(a, b): return pearson(ranks(a), ranks(b))


def p_perm(a, b, n=4000, seed=1):
    """p unilateral (ρ positivo) por permutação."""
    import random
    rnd = random.Random(seed)
    r0 = spearman(a, b); bb = list(b); c = 0
    for _ in range(n):
        rnd.shuffle(bb)
        if spearman(a, bb) >= r0: c += 1
    return (c + 1) / (n + 1)


def mediana(v):
    v = sorted(v); n = len(v)
    return v[n // 2] if n % 2 else (v[n // 2 - 1] + v[n // 2]) / 2


def sem_tendencia(serie, janela=9):
    anos = sorted(serie); out = {}
    for a in anos:
        viz = [serie[b] for b in anos if abs(b - a) <= janela // 2]
        m = mediana(viz)
        if m == 0:  # janela com mais da metade de zeros (perda total): usa a média dos valores positivos da janela
            pos = [v for v in viz if v > 0]
            m = sum(pos) / len(pos) if pos else 1.0
        out[a] = serie[a] / m
    return out


def sem_tendencia_loglin(serie):
    anos = sorted(a for a in serie if serie[a] > 0)
    x = [a - anos[0] for a in anos]; y = [math.log(serie[a]) for a in anos]
    mx, my = sum(x) / len(x), sum(y) / len(y)
    b = sum((i - mx) * (j - my) for i, j in zip(x, y)) / sum((i - mx) ** 2 for i in x)
    a0 = my - b * mx
    return {a: serie[a] / math.exp(a0 + b * (a - anos[0])) for a in anos}


def acerto_piores(modelo, obs, n):
    anos = sorted(set(modelo) & set(obs))
    po = set(sorted(anos, key=lambda a: obs[a])[:n])
    pm = set(sorted(anos, key=lambda a: modelo[a])[:n])
    return len(po & pm), sorted(po), sorted(pm)


def p_hiper(hit, N, K=8, n=8):
    """P(X >= hit) hipergeométrica: acaso de acertar `hit` ou mais dos K piores."""
    from math import comb
    tot = comb(N, n)
    return sum(comb(K, x) * comb(N - K, n - x) for x in range(hit, min(K, n) + 1)) / tot


def pam(municipio_chave, produto):
    d = json.load(open(DADOS / f"pam_{municipio_chave}.json"))[1:]
    out = {}
    for r in d:
        if r["D4C"] == produto and r["D2N"].startswith("Rendimento") and r["V"] not in ("-", "...", "X", ".."):
            out[int(r["D3N"])] = float(r["V"])
    return out
