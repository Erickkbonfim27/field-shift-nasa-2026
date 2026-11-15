"""Funções comuns da sessão B3: leitura do NASA POWER, ET0 FAO-56, balanço hídrico,
leitura do IBGE (só conferência), rendimento relativo, LOO e Spearman.
ET0 e balanço adaptados de prototipo/modelo/risco.py (mesmas fórmulas)."""
import json, math, datetime as dt, statistics as st
from pathlib import Path

B3 = Path(__file__).resolve().parent
DADOS = B3.parent.parent / "dados"


class Power:
    def __init__(self, nome, pasta=None):
        d = json.load(open((pasta or DADOS) / f"power_{nome}.json"))
        self.lon, self.lat, self.alt = d["geometry"]["coordinates"]
        self.P = d["properties"]["parameter"]
        self.chuva = {k: max(0.0, v) for k, v in self.P["PRECTOTCORR"].items()}
        self._et0 = {}

    def v(self, par, dia):
        x = self.P[par].get(dia, -999)
        return None if x == -999 else x

    def et0(self, dia):
        if dia in self._et0: return self._et0[dia]
        P = self.P
        tmax, tmin, tm = P["T2M_MAX"][dia], P["T2M_MIN"][dia], P["T2M"][dia]
        rh, u2, rs = P["RH2M"][dia], P["WS2M"][dia], P["ALLSKY_SFC_SW_DWN"][dia]
        if -999 in (tmax, tmin, tm, rh, u2, rs): self._et0[dia] = None; return None
        e = lambda t: 0.6108 * math.exp(17.27 * t / (t + 237.3))
        es, ea = (e(tmax) + e(tmin)) / 2, rh / 100 * e(tm)
        delta = 4098 * e(tm) / (tm + 237.3) ** 2
        gam = 0.000665 * 101.3 * ((293 - 0.0065 * self.alt) / 293) ** 5.26
        d = dt.date(int(dia[:4]), int(dia[4:6]), int(dia[6:]))
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
        r = max(0.5, num / (delta + gam * (1 + 0.34 * u2)))
        self._et0[dia] = r
        return r


def dias(ini, fim):
    d = ini
    while d <= fim:
        yield d, d.strftime("%Y%m%d")
        d += dt.timedelta(1)


def kc_curva(fases, kc, k):
    ini, dev, mid, late = fases
    a, b, c = kc
    if k < ini: return a
    if k < ini + dev: return a + (b - a) * (k - ini) / dev
    if k < ini + dev + mid: return b
    return b + (c - b) * min(1, (k - ini - dev - mid) / late)


def balanco(pw, plantio, fim, fases, kc, cad, p_depl=0.5, s0=None, kc_antes=0.5):
    """Balde diário. Antes do plantio (a partir de 60 dias antes, começando cheio) usa kc_antes.
    Retorna lista diária de dict(dia, k, etc, eta, exced, s)."""
    s = cad if s0 is None else s0
    out = []
    for d, key in dias(plantio - dt.timedelta(60), fim):
        e0 = pw.et0(key)
        if e0 is None or key not in pw.chuva: return None
        k = (d - plantio).days
        kcd = kc_antes if k < 0 else kc_curva(fases, kc, k)
        etc = kcd * e0
        s += pw.chuva[key]
        exced = max(0.0, s - cad)
        s = min(cad, s)
        ks = min(1.0, s / ((1 - p_depl) * cad))
        eta = etc * ks
        s = max(0.0, s - eta)
        if k >= 0: out.append(dict(dia=key, d=d, k=k, etc=etc, eta=eta, exced=exced, s=s))
    return out


# ---------- IBGE (conferência, nunca entrada da solução) ----------
def ibge_serie(arquivo, var_prefixo):
    rows = json.load(open(B3 / "externo" / arquivo))[1:]
    out = {}
    for r in rows:
        if r["D2N"].startswith(var_prefixo) and r["V"] not in ("...", "-", "X", ".."):
            out[int(r["D3N"])] = float(r["V"])
    return out


def rend_relativo(serie, raio=3):
    """Rendimento do ano / mediana dos anos t-raio..t+raio (sem t)."""
    out = {}
    for a, y in serie.items():
        viz = [serie[b] for b in range(a - raio, a + raio + 1) if b != a and b in serie]
        if len(viz) >= 3: out[a] = y / st.median(viz)
    return out


# ---------- estatística ----------
def ranks(x):
    o = sorted(range(len(x)), key=lambda i: x[i])
    r = [0.0] * len(x)
    i = 0
    while i < len(o):
        j = i
        while j + 1 < len(o) and x[o[j + 1]] == x[o[i]]: j += 1
        for t in range(i, j + 1): r[o[t]] = (i + j) / 2 + 1
        i = j + 1
    return r


def spearman(x, y):
    rx, ry = ranks(x), ranks(y)
    mx, my = st.mean(rx), st.mean(ry)
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    den = math.sqrt(sum((a - mx) ** 2 for a in rx) * sum((b - my) ** 2 for b in ry))
    return num / den


def p_perm(x, y, n=5000, seed=1):
    """p bilateral da correlação de Spearman por permutação."""
    import random
    rnd = random.Random(seed)
    r0 = abs(spearman(x, y))
    yy = list(y)
    c = 0
    for _ in range(n):
        rnd.shuffle(yy)
        if abs(spearman(x, yy)) >= r0: c += 1
    return (c + 1) / (n + 1)


def melhor_limiar(xs, ruins, sentido):
    """Limiar que maximiza acertos - falsos (Peirce). sentido=-1: alerta se x <= limiar; +1: x >= limiar."""
    cand = sorted(set(xs))
    nb, ng = sum(ruins), len(ruins) - sum(ruins)
    best, bl = -9, None
    for c in cand:
        al = [(x <= c) if sentido < 0 else (x >= c) for x in xs]
        h = sum(1 for a, r in zip(al, ruins) if a and r)
        f = sum(1 for a, r in zip(al, ruins) if a and not r)
        sc = (h / nb if nb else 0) - (f / ng if ng else 0)
        if sc > best: best, bl = sc, c
    return bl


def loo(xs, ruins, sentido):
    """Para cada ano, escolhe o limiar nos outros anos e classifica o ano deixado de fora."""
    al = []
    for i in range(len(xs)):
        c = melhor_limiar(xs[:i] + xs[i + 1:], ruins[:i] + ruins[i + 1:], sentido)
        al.append((xs[i] <= c) if sentido < 0 else (xs[i] >= c))
    h = sum(1 for a, r in zip(al, ruins) if a and r)
    f = sum(1 for a, r in zip(al, ruins) if a and not r)
    return dict(alertas=al, acertos=h, ruins=sum(ruins), falsos=f,
                taxa_acerto=h / sum(ruins) if sum(ruins) else None,
                frac_falsos=f / (h + f) if h + f else None)


# ---------- gráfico SVG simples ----------
def svg_dispersao(caminho, pontos, xlabel, ylabel, titulo, limiar_y=0.85, limiar_x=None, rotulos=True):
    """pontos: lista de (x, y, rotulo, destaque)."""
    W, H, m = 760, 480, 60
    xs = [p[0] for p in pontos]; ys = [p[1] for p in pontos]
    x0, x1 = min(xs), max(xs); y0, y1 = min(min(ys), 0.4), max(max(ys), 1.3)
    dx = (x1 - x0) or 1; x0 -= 0.05 * dx; x1 += 0.05 * dx
    X = lambda v: m + (v - x0) / (x1 - x0) * (W - 2 * m)
    Y = lambda v: H - m - (v - y0) / (y1 - y0) * (H - 2 * m)
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" font-family="sans-serif" font-size="12">',
         '<rect width="100%" height="100%" fill="white"/>',
         f'<text x="{W/2}" y="24" text-anchor="middle" font-size="15" font-weight="bold">{titulo}</text>',
         f'<line x1="{m}" y1="{H-m}" x2="{W-m}" y2="{H-m}" stroke="#333"/>',
         f'<line x1="{m}" y1="{m}" x2="{m}" y2="{H-m}" stroke="#333"/>',
         f'<text x="{W/2}" y="{H-18}" text-anchor="middle">{xlabel}</text>',
         f'<text x="16" y="{H/2}" text-anchor="middle" transform="rotate(-90 16 {H/2})">{ylabel}</text>']
    for t in range(6):
        v = y0 + t * (y1 - y0) / 5
        s.append(f'<text x="{m-6}" y="{Y(v)+4}" text-anchor="end">{v:.2f}</text>')
        v = x0 + t * (x1 - x0) / 5
        s.append(f'<text x="{X(v)}" y="{H-m+16}" text-anchor="middle">{v:.2f}</text>')
    s.append(f'<line x1="{m}" y1="{Y(limiar_y)}" x2="{W-m}" y2="{Y(limiar_y)}" stroke="#c33" stroke-dasharray="5,4"/>')
    s.append(f'<text x="{W-m}" y="{Y(limiar_y)-5}" text-anchor="end" fill="#c33">ano ruim (≤ {limiar_y:.0%} da mediana)</text>')
    if limiar_x is not None:
        s.append(f'<line x1="{X(limiar_x)}" y1="{m}" x2="{X(limiar_x)}" y2="{H-m}" stroke="#36c" stroke-dasharray="5,4"/>')
        s.append(f'<text x="{X(limiar_x)+4}" y="{m+12}" fill="#36c">limiar do alerta</text>')
    for x, y, r, dest in pontos:
        cor = "#c33" if dest else "#555"
        s.append(f'<circle cx="{X(x):.1f}" cy="{Y(y):.1f}" r="4" fill="{cor}"/>')
        if rotulos: s.append(f'<text x="{X(x)+5:.1f}" y="{Y(y)-5:.1f}" font-size="10" fill="{cor}">{r}</text>')
    s.append('</svg>')
    Path(caminho).write_text("\n".join(s))
