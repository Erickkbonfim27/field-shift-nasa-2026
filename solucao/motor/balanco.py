"""Balanço hídrico diário (balde) FAO-56, com Ks e Kc por fase.

`balde` é o balde da sessão B3 (loop-validacao/sessoes/B3/comum.py, função `balanco`):
começa cheio 60 dias antes do plantio, com Kc 0,5 nesse período. É o balde usado nos
índices de ano extremo validados em B3-1, B3-2 e V1. A ISNA (índice de satisfação da
necessidade de água) é ETa/ETc.
"""
import datetime as dt
from .power import chave


def kc_curva(fases, kc, k):
    """Kc do dia k do ciclo (FAO-56, curva em 4 fases)."""
    ini, dev, mid, late = fases
    a, b, c = kc
    if k < ini:
        return a
    if k < ini + dev:
        return a + (b - a) * (k - ini) / dev
    if k < ini + dev + mid:
        return b
    return b + (c - b) * min(1, (k - ini - dev - mid) / late)


def balde(pw, plantio, fim, fases, kc, cad, p_depl=0.5, s0=None, kc_antes=0.5, dias_antes=60):
    """Simula de `plantio - dias_antes` até `fim` (inclusive). Devolve lista diária
    (só dias >= plantio) de dict(d, k, etc, eta, exced, s), ou None se faltar dado."""
    s = cad if s0 is None else s0
    out = []
    d = plantio - dt.timedelta(dias_antes)
    while d <= fim:
        key = chave(d)
        e0 = pw.et0(key)
        if e0 is None or key not in pw.chuva:
            return None
        k = (d - plantio).days
        etc = (kc_antes if k < 0 else kc_curva(fases, kc, k)) * e0
        s += pw.chuva[key]
        exced = max(0.0, s - cad)
        s = min(cad, s)
        ks = min(1.0, s / ((1 - p_depl) * cad))
        eta = etc * ks
        s = max(0.0, s - eta)
        if k >= 0:
            out.append(dict(d=d, k=k, etc=etc, eta=eta, exced=exced, s=s))
        d += dt.timedelta(1)
    return out


def isna(dias_balde, ate=None):
    """ETa/ETc somados até `ate` (inclusive)."""
    g = [x for x in dias_balde if ate is None or x["d"] <= ate]
    etc = sum(x["etc"] for x in g)
    return sum(x["eta"] for x in g) / etc if etc else None


# ---------------- índices validados (parâmetros fixos das fichas) ----------------
MILHO_B31 = dict(fases=(25, 40, 45, 30), kc=(0.30, 1.20, 0.60), cad=125.0, p_depl=0.5,
                 plantio=(9, 20), decisao=(1, 10),
                 fonte="B3-1 (loop-validacao/sessoes/B3/teste1_estiagem_milho.py, safra)")
CEBOLA_B32 = dict(fases=(15, 25, 70, 40), kc=(0.70, 1.05, 0.75), cad=125 * 0.3, p_depl=0.3,
                  transplante=(8, 1), janela=((9, 1), (11, 30)),
                  fonte="B3-2 (loop-validacao/sessoes/B3/teste2_excesso_cebola.py, safra)")


def isna_milho_b31(pw, ano_colheita, ate=None):
    """ISNA do milho de 20/set (ano anterior) até 10/jan (ou até `ate`, se antes).
    Igual a B3-1 `safra(...)['isna_dec']`. O balde é causal: parar em `ate` não muda os dias anteriores."""
    c = MILHO_B31
    pl = dt.date(ano_colheita - 1, *c["plantio"])
    dec = dt.date(ano_colheita, *c["decisao"])
    fim = dec if ate is None else min(dec, ate)
    if fim < pl:
        return None
    b = balde(pw, pl, fim, c["fases"], c["kc"], c["cad"], c["p_depl"])
    if b is None:
        return None
    return isna(b, fim)


def excedente_cebola_b32(pw, ano):
    """Excedente hídrico (mm) de 1/set a 30/nov, cebola transplantada em 1/ago, raiz 0,3 m.
    Igual a B3-2 `safra(...)['exced']`."""
    c = CEBOLA_B32
    pl = dt.date(ano, *c["transplante"])
    a, z = dt.date(ano, *c["janela"][0]), dt.date(ano, *c["janela"][1])
    b = balde(pw, pl, z, c["fases"], c["kc"], c["cad"], c["p_depl"])
    if b is None:
        return None
    return sum(x["exced"] for x in b if a <= x["d"] <= z)
