#!/usr/bin/env python3
"""V3: balanço hídrico FAO-56 + FAO-33 para milho e sorgo de silagem em São Miguel do Oeste.

Reaproveita a ET0 e a chuva da sessão A4 (mesmo NASA POWER, mesmo Penman-Monteith), só leitura.
Novidades em relação à A4:
  - Ky por estágio FAO-33 (vegetativo, floração, formação do rendimento, maturação), não por fase FAO-56;
  - cenário "biomassa" (Ky = 1 nas duas culturas), coerente com silagem de planta inteira;
  - CAD em mm direto (grade de 24 a 175 mm), em vez de 3 solos fixos;
  - plantio do sorgo deslocado em relação ao milho;
  - ISNA por fase do ZARC (para conferência).
Rodar sempre com: python3 -I (o -I tira o diretório do script do sys.path; este módulo é importado via sys.path.insert).
"""
import sys, datetime as dt
sys.dont_write_bytecode = True  # não escrever __pycache__ na pasta da A4
from pathlib import Path

AQUI = Path(__file__).resolve().parent
A4 = AQUI.parents[2] / "loop-validacao" / "sessoes" / "A4"
sys.path.insert(0, str(A4))
import modelo_smo as M  # só leitura: ET0, CHUVA, TMIN do POWER de SMO

D0 = dt.date(1984, 1, 1)
DN = dt.date(2025, 12, 31)
N = (DN - D0).days + 1
ET0, RAIN, TMIN = [], [], []
for i in range(N):
    k = (D0 + dt.timedelta(i)).strftime("%Y%m%d")
    ET0.append(M.ET0.get(k, float("nan")))
    RAIN.append(M.CHUVA.get(k, float("nan")))
    TMIN.append(M.TMIN.get(k, float("nan")))

GEADA = 2.0
SAFRAS = list(range(1984, 2025))
DATAS = [(9, 11), (9, 21), (10, 1), (10, 11), (10, 21)]  # plantio do milho, como na A4

# Kc FAO-56 (ini, mid, end) e duração das fases Kc (ini, dev, mid, late) como fração do ciclo.
# A4: 20/35/40/15 de 110 dias.
KC = {"milho": (0.30, 1.20, 0.90), "sorgo": (0.30, 1.05, 0.80)}
FRAC_KC = (20 / 110, 35 / 110, 40 / 110, 15 / 110)
P_DEP = 0.55  # FAO-56 tab. 22, igual para milho e sorgo

# Ky
KY_A4 = {"milho": (0.4, 0.4, 1.5, 0.5), "sorgo": (0.2, 0.2, 0.55, 0.45)}  # por fase Kc (A4)
KY_FAO33 = {"milho": (0.4, 1.5, 0.5, 0.2), "sorgo": (0.2, 0.55, 0.45, 0.2)}  # por estágio FAO-33
# MISTO (pós-teste): silagem = planta inteira. Parte do grão segue o Ky FAO-33; o resto (colmo, folha) segue Ky = 1.
# Fração de grão na MS da silagem: milho 35%, sorgo 39% (Paziani et al., Embrapa/APTA/ESALQ: 6 de 17 t/ha e 7 de 18 t/ha).
W_GRAO = {"milho": 0.35, "sorgo": 0.39}
FRAC_FAO33 = (55 / 110, 70 / 110, 95 / 110, 1.0)  # fim de cada estágio (fração do ciclo)
FRAC_A4 = (20 / 110, 55 / 110, 95 / 110, 1.0)


def kc_dia(crop, k, n, kcm):
    a, b, e = KC[crop]
    ini, dev, mid, late = [f * n for f in FRAC_KC]
    if k < ini: v = a
    elif k < ini + dev: v = a + (b - a) * (k - ini) / dev
    elif k < ini + dev + mid: v = b
    else: v = b + (e - b) * (k - ini - dev - mid) / late
    return v * kcm


_cache = {}


def estrutura(crop, scen, n):
    """Retorna (kc[], estagio[], ky[], mascara_geada[]) sem multiplicadores."""
    key = (crop, scen, n)
    if key in _cache: return _cache[key]
    if scen == "A4":
        ends, ky = FRAC_A4, KY_A4[crop]
    elif scen == "FAO33":
        ends, ky = FRAC_FAO33, KY_FAO33[crop]
    elif scen == "MISTO":
        w = W_GRAO[crop]
        ends, ky = FRAC_FAO33, tuple(w * x + (1 - w) * 1.0 for x in KY_FAO33[crop])
    elif scen == "BIOMASSA":
        ends, ky = (1.0,), (1.0,)
    else:
        raise ValueError(scen)
    est = []
    for k in range(n):
        f = k / n
        j = 0
        while f >= ends[j] - 1e-9 and j < len(ends) - 1: j += 1
        est.append(j)
    geada = [(20 / 110) <= k / n < (95 / 110) for k in range(n)]
    out = (est, list(ky), geada)
    _cache[key] = out
    return out


def simular(crop, cad, plantio, scen="FAO33", kcm=1.0, kym=1.0, n=110, cad_pre=None):
    """Rendimento relativo (0-1) de uma cultura plantada em `plantio` (date). Retorna dict ou None."""
    i0 = (plantio - D0).days
    if i0 - 60 < 0 or i0 + n >= N: return None
    s = cad
    for i in range(i0 - 60, i0):
        e = ET0[i]
        if e != e: return None
        s = min(cad, s + RAIN[i])
        s = max(0.0, s - 0.3 * e * min(1.0, s / (0.5 * cad)))
    est, ky, gmask = estrutura(crop, scen, n)
    ns = len(ky)
    eta = [0.0] * ns; etc = [0.0] * ns
    geada = False
    lim = (1 - P_DEP) * cad
    for k in range(n):
        i = i0 + k
        e = ET0[i]
        if e != e: return None
        ec = kc_dia(crop, k, n, kcm) * e
        s += RAIN[i]
        if s > cad: s = cad
        ks = s / lim
        if ks > 1.0: ks = 1.0
        ea = ec * ks
        s = max(0.0, s - ea)
        j = est[k]
        eta[j] += ea; etc[j] += ec
        if gmask[k] and TMIN[i] <= GEADA: geada = True
    isna = [a / b if b else 1.0 for a, b in zip(eta, etc)]
    y = 1.0
    for j in range(ns):
        y *= max(0.0, 1 - min(1.0, ky[j] * kym) * (1 - isna[j]))
    if geada: y *= 0.3
    return dict(y=y, isna=isna, geada=geada)


def casos(cad, scen="FAO33", kym_sorgo=1.0, kcm_sorgo=1.0, desloca_sorgo=0, kym_milho=1.0, cad_sorgo=None, n_milho=110, n_sorgo=110, kcm_milho=1.0):
    """Lista de casos (41 safras x 5 datas): rendimento do milho e do sorgo (relativos), geada."""
    out = []
    for a in SAFRAS:
        for di, (m, d) in enumerate(DATAS):
            pl = dt.date(a, m, d)
            rm = simular("milho", cad, pl, scen, kcm_milho, kym_milho, n_milho)
            rs = simular("sorgo", cad_sorgo or cad, pl + dt.timedelta(desloca_sorgo), scen, kcm_sorgo, kym_sorgo, n_sorgo)
            if not rm or not rs: continue
            out.append((a, di, rm["y"], rs["y"], rm["geada"], rs["geada"]))
    return out


# ---------- estatísticas ----------
def q(v, p):
    v = sorted(v); i = p * (len(v) - 1); lo = int(i); hi = min(lo + 1, len(v) - 1)
    return v[lo] + (v[hi] - v[lo]) * (i - lo)


def mistura(cs, f, R):
    return [(1 - f) * c[2] + f * R * c[3] for c in cs]


def resumo(tot):
    return dict(media=sum(tot) / len(tot), p10=q(tot, 0.10), p05=q(tot, 0.05), perda=sum(t < 0.6 for t in tot), n=len(tot), minimo=min(tot),
                cvar10=sum(sorted(tot)[: max(1, round(0.1 * len(tot)))]) / max(1, round(0.1 * len(tot))))
