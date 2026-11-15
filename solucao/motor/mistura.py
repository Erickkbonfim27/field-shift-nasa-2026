"""Módulo mistura_talhao: metade da silagem em sorgo no talhão raso.

Cópia de solucao/validacao/V3/modelo_v3.py (simular, casos, mistura) e da conta de
solucao/validacao/V3/v3_02_central_grade.py (central, bootstrap, grade) e v3_03_extras.py
(por data). Diferenças, todas anotadas no rastro:
- a ET0 é a mesma da A4 (altitude 533 m, piso 0,3 mm), recalculada aqui do JSON do POWER;
- o bootstrap usa o gerador da biblioteca padrão (semente 20261114). A V3 usou numpy, então o
  IC95 muda um pouco; o valor central não muda.
"""
import datetime as dt
import itertools
from .power import Power, chave
from .estat import quantil, mediana, bootstrap_por_safra

D0 = dt.date(1984, 1, 1)
DN = dt.date(2025, 12, 31)
GEADA = 2.0
SAFRAS = list(range(1984, 2025))
DATAS = [(9, 11), (9, 21), (10, 1), (10, 11), (10, 21)]
KC = {"milho": (0.30, 1.20, 0.90), "sorgo": (0.30, 1.05, 0.80)}
FRAC_KC = (20 / 110, 35 / 110, 40 / 110, 15 / 110)
P_DEP = 0.55
KY_A4 = {"milho": (0.4, 0.4, 1.5, 0.5), "sorgo": (0.2, 0.2, 0.55, 0.45)}
KY_FAO33 = {"milho": (0.4, 1.5, 0.5, 0.2), "sorgo": (0.2, 0.55, 0.45, 0.2)}
W_GRAO = {"milho": 0.35, "sorgo": 0.39}
FRAC_FAO33 = (55 / 110, 70 / 110, 95 / 110, 1.0)
FRAC_A4 = (20 / 110, 55 / 110, 95 / 110, 1.0)

# cenário central e grade pré-definida da V3 (00_criterio_antes.md)
CENTRAL = dict(scen="FAO33", R=0.88, fracao_sorgo=0.5)
GRADE = dict(kym=(0.5, 0.75, 1.0, 1.5, 2.0), R=(0.75, 0.88, 1.0), scen=("A4", "FAO33", "BIOMASSA"),
             desl=(0, 30), kcm=(0.85, 1.0, 1.15))
CORTE_SOBREVIVE = 70.0  # % da grade (V3)
LIMIAR_PERDA = 0.6


class Serie:
    """ET0, chuva e T2M_MIN diários de 1984 a 2025 em listas (como modelo_v3)."""

    def __init__(self, caminho_power):
        pw = Power(caminho_power, alt=533.0, lat=-26.725, piso=0.3)
        self.pw = pw
        n = (DN - D0).days + 1
        self.n = n
        self.ET0, self.RAIN, self.TMIN = [], [], []
        nan = float("nan")
        for i in range(n):
            k = chave(D0 + dt.timedelta(i))
            e = pw.et0(k)
            self.ET0.append(nan if e is None else e)
            self.RAIN.append(pw.chuva.get(k, nan))
            self.TMIN.append(pw.tmin.get(k, nan))
        self._cache = {}


def kc_dia(crop, k, n, kcm):
    a, b, e = KC[crop]
    ini, dev, mid, late = [f * n for f in FRAC_KC]
    if k < ini:
        v = a
    elif k < ini + dev:
        v = a + (b - a) * (k - ini) / dev
    elif k < ini + dev + mid:
        v = b
    else:
        v = b + (e - b) * (k - ini - dev - mid) / late
    return v * kcm


_estr = {}


def estrutura(crop, scen, n):
    key = (crop, scen, n)
    if key in _estr:
        return _estr[key]
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
        while f >= ends[j] - 1e-9 and j < len(ends) - 1:
            j += 1
        est.append(j)
    geada = [(20 / 110) <= k / n < (95 / 110) for k in range(n)]
    _estr[key] = (est, list(ky), geada)
    return _estr[key]


def simular(S, crop, cad, plantio, scen="FAO33", kcm=1.0, kym=1.0, n=110):
    i0 = (plantio - D0).days
    if i0 - 60 < 0 or i0 + n >= S.n:
        return None
    ET0, RAIN, TMIN = S.ET0, S.RAIN, S.TMIN
    s = cad
    for i in range(i0 - 60, i0):
        e = ET0[i]
        if e != e:
            return None
        s = min(cad, s + RAIN[i])
        s = max(0.0, s - 0.3 * e * min(1.0, s / (0.5 * cad)))
    est, ky, gmask = estrutura(crop, scen, n)
    ns = len(ky)
    eta = [0.0] * ns
    etc = [0.0] * ns
    geada = False
    lim = (1 - P_DEP) * cad
    for k in range(n):
        i = i0 + k
        e = ET0[i]
        if e != e:
            return None
        ec = kc_dia(crop, k, n, kcm) * e
        s += RAIN[i]
        if s > cad:
            s = cad
        ks = s / lim
        if ks > 1.0:
            ks = 1.0
        ea = ec * ks
        s = max(0.0, s - ea)
        j = est[k]
        eta[j] += ea
        etc[j] += ec
        if gmask[k] and TMIN[i] <= GEADA:
            geada = True
    isna = [a / b if b else 1.0 for a, b in zip(eta, etc)]
    y = 1.0
    for j in range(ns):
        y *= max(0.0, 1 - min(1.0, ky[j] * kym) * (1 - isna[j]))
    if geada:
        y *= 0.3
    return dict(y=y, isna=isna, geada=geada)


def casos(S, cad, scen="FAO33", kym_sorgo=1.0, kcm_sorgo=1.0, desloca_sorgo=0):
    """Lista (safra, i_data, y_milho, y_sorgo, geada_milho, geada_sorgo): 41 safras x 5 datas."""
    key = (cad, scen, kym_sorgo, kcm_sorgo, desloca_sorgo)
    if key in S._cache:
        return S._cache[key]
    out = []
    for a in SAFRAS:
        for di, (m, d) in enumerate(DATAS):
            pl = dt.date(a, m, d)
            rm = simular(S, "milho", cad, pl, scen)
            rs = simular(S, "sorgo", cad, pl + dt.timedelta(desloca_sorgo), scen, kcm_sorgo, kym_sorgo)
            if not rm or not rs:
                continue
            out.append((a, di, rm["y"], rs["y"], rm["geada"], rs["geada"]))
    S._cache[key] = out
    return out


def _por_safra(cs):
    """Agrupa os casos por safra: lista de listas de (y_milho, y_sorgo)."""
    g = {}
    for c in cs:
        g.setdefault(c[0], []).append((c[2], c[3]))
    return [g[a] for a in sorted(g)]


def _ganho(pares, f, R):
    tot = [(1 - f) * m + f * R * s for m, s in pares]
    base = [m for m, _ in pares]
    p10, bp10 = quantil(tot, 0.10), quantil(base, 0.10)
    med, bmed = sum(tot) / len(tot), sum(base) / len(base)
    return dict(ganho_p10=100 * (p10 / bp10 - 1), var_media=100 * (med / bmed - 1), p10=p10, base_p10=bp10,
                media=med, base_media=bmed, perda=sum(t < LIMIAR_PERDA for t in tot),
                base_perda=sum(b < LIMIAR_PERDA for b in base), n_casos=len(tot))


def central(S, cad, nb=2000, semente=20261114):
    cs = casos(S, cad, scen=CENTRAL["scen"])
    pares = [(c[2], c[3]) for c in cs]
    f, R = CENTRAL["fracao_sorgo"], CENTRAL["R"]
    r = _ganho(pares, f, R)
    blocos = _por_safra(cs)
    bs = bootstrap_por_safra(blocos, lambda am: _ganho([p for b in am for p in b], f, R), nb, semente)
    g = [b["ganho_p10"] for b in bs]
    m = [b["var_media"] for b in bs]
    r.update(ic95_ganho_p10=[quantil(g, 0.025), quantil(g, 0.975)],
             ic95_var_media=[quantil(m, 0.025), quantil(m, 0.975)],
             prob_ganho_pos=sum(x > 0 for x in g) / len(g), n_safras=len(blocos), nb=nb, semente=semente)
    return r


def grade(S, cad):
    """Grade pré-definida da V3: 3 cenários x 5 Ky x 2 deslocamentos x 3 Kc x 3 R = 270."""
    linhas = []
    for scen in GRADE["scen"]:
        for kym, desl, kcm in itertools.product(GRADE["kym"], GRADE["desl"], GRADE["kcm"]):
            cs = casos(S, cad, scen=scen, kym_sorgo=kym, kcm_sorgo=kcm, desloca_sorgo=desl)
            pares = [(c[2], c[3]) for c in cs]
            for R in GRADE["R"]:
                g = _ganho(pares, 0.5, R)
                linhas.append(dict(scen=scen, kym=kym, desl=desl, kcm=kcm, R=R, ganho_p10=g["ganho_p10"],
                                   var_media=g["var_media"], ok=bool(g["ganho_p10"] > 0 and g["var_media"] >= -3)))
    gp = [l["ganho_p10"] for l in linhas]
    vm = [l["var_media"] for l in linhas]
    return dict(n=len(linhas), sobrevive_pct=100 * sum(l["ok"] for l in linhas) / len(linhas),
                ganho_p10_mediana=mediana(gp), ganho_p10_p10_p90=[quantil(gp, 0.1), quantil(gp, 0.9)],
                var_media_mediana=mediana(vm), var_media_p10_p90=[quantil(vm, 0.1), quantil(vm, 0.9)],
                corte_sobrevive_pct=CORTE_SOBREVIVE, linhas=linhas)


def por_data(S, cad):
    cs = casos(S, cad, scen="FAO33")
    out = []
    for di, (m, d) in enumerate(DATAS):
        pares = [(c[2], c[3]) for c in cs if c[1] == di]
        g = _ganho(pares, 0.5, 0.88)
        geada = sum(1 for c in cs if c[1] == di and (c[4] or c[5]))
        out.append(dict(decendio=f"{d:02d}/{m:02d}", n=len(pares), p10_base=g["base_p10"],
                        p10_mistura=g["p10"], ganho_p10_pct=g["ganho_p10"], var_media_pct=g["var_media"],
                        safras_com_geada=geada))
    return out


def ano_a_ano(S, cad):
    """Safras em que a mistura 50/50 rende mais (ganho > 0) e em que rende mais de 0,02 menos (V3, fig. 4)."""
    f, R = CENTRAL["fracao_sorgo"], CENTRAL["R"]
    ganhos = []
    for b in _por_safra(casos(S, cad, scen=CENTRAL["scen"])):
        ganhos.append(sum((1 - f) * m + f * R * s - m for m, s in b) / len(b))
    return dict(safras_ganho=sum(g > 0 for g in ganhos), safras_perda=sum(g < -0.02 for g in ganhos))


def avaliar(S, cad, com_grade=True):
    r = dict(cad_mm=cad, central=central(S, cad), por_data=por_data(S, cad), **ano_a_ano(S, cad), parametros=dict(
        CENTRAL, kc=KC, frac_kc=FRAC_KC, p_depl=P_DEP, ky_fao33=KY_FAO33, geada_limiar_c=GEADA,
        fator_geada=0.3, safras=f"{SAFRAS[0]}-{SAFRAS[-1]}", datas=[f"{d:02d}/{m:02d}" for m, d in DATAS],
        et0=dict(alt_m=533.0, piso_mm=0.3), limiar_perda=LIMIAR_PERDA))
    if com_grade:
        r["grade"] = grade(S, cad)
    return r
