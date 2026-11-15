"""Módulos de geada (só NASA POWER T2M_MIN e T2M_MAX).

geada_janela_safra  <- solucao/validacao/V4/v4_motor.py, safra_milho (parte da geada):
    milho de verão, fases 25/35/40/30 dias; geada = dia com T2M_MIN < 2 °C nas fases I a III
    (100 primeiros dias). Critério D1 pré-registrado na V4 (passou). N3.
geada_limite_2a_safra <- solucao/validacao/V2/v2_geada.py, safra / curva / limite_diario:
    2º milho de silagem; geada = T2M_MIN <= L entre o plantio e o ponto de silagem
    (graus-dia base 10 °C, teto 30 °C). N2.
"""
import datetime as dt
import statistics
from .power import chave
from .estat import em10, ic10

# ------------------------------------------------------------------ janela da safra (V4 D1)
FASES_MILHO_V4 = (25, 35, 40, 30)
LIMIAR_SAFRA = 2.0
DATAS_SAFRA = [(8, 1), (8, 11), (8, 21), (9, 1), (9, 11), (9, 21), (10, 1), (10, 11), (10, 21),
               (11, 1), (11, 11), (11, 21), (12, 1), (12, 11), (12, 21)]
ANOS_COLHEITA_V4 = list(range(1985, 2026))  # plantios de 1984 a 2024, como na V4 (41 safras)


def geada_safra(pw, plantio, limiar=LIMIAR_SAFRA, fases=FASES_MILHO_V4):
    """Número de dias com T2M_MIN < limiar nas fases I a III. None se faltar dado."""
    n3 = sum(fases[:3])
    c = 0
    for i in range(n3):
        k = chave(plantio + dt.timedelta(i))
        if k not in pw.tmin:
            return None
        c += pw.tmin[k] < limiar
    return c


def tabela_janela_safra(pw, anos_colheita=ANOS_COLHEITA_V4, datas=DATAS_SAFRA, limiar=LIMIAR_SAFRA):
    linhas = []
    for (m, d) in datas:
        anos_com = []
        n = 0
        for a in anos_colheita:
            g = geada_safra(pw, dt.date(a - 1, m, d), limiar)
            if g is None:
                continue
            n += 1
            if g > 0:
                anos_com.append(a - 1)
        k = len(anos_com)
        linhas.append(dict(decendio=f"{d:02d}/{m:02d}", k=k, n=n, em10=em10(k, n), ic95=ic10(k, n),
                           anos_plantio_com_geada=anos_com))
    return dict(limiar_c=limiar, fases_dias=list(FASES_MILHO_V4), dias_avaliados=sum(FASES_MILHO_V4[:3]),
                anos_plantio=f"{anos_colheita[0] - 1}-{anos_colheita[-1] - 1}", linhas=linhas)


def primeiro_seguro(tabela, corte=2.0):
    """Primeiro decêndio com em10 <= corte (conferência A3 da spec)."""
    for l in tabela["linhas"]:
        if l["em10"] <= corte:
            return l["decendio"]
    return None


# ------------------------------------------------------------------ 2º milho (V2)
LIMIARES_2M = (2.0, 3.0, 4.0)
GDD_PADRAO = 1250
GDD_SENS = (1100, 1250, 1400)
DECENDIOS_2M = [(1, 1), (1, 11), (1, 21), (2, 1), (2, 11), (2, 21), (3, 1), (3, 11), (3, 21)]
ANOS_V2 = list(range(1981, 2026))
CORTE_LIMITE = 0.2


def gdd_dia(pw, k, base=10.0, teto=30.0):
    tx = min(pw.tmax[k], teto)
    tn = max(pw.tmin[k], base)
    return max(0.0, (tx + tn) / 2 - base)


def safra_2m(pw, ano, mes, dia, gdd_alvo=GDD_PADRAO, limiares=LIMIARES_2M):
    """Igual a V2 `safra`: data da silagem e 1ª geada (por limiar) entre plantio e silagem."""
    d0 = dt.date(ano, mes, dia)
    d = d0
    soma = 0.0
    prim = {L: None for L in limiares}
    while soma < gdd_alvo:
        k = chave(d)
        if k not in pw.tmin or k not in pw.tmax or d > dt.date(ano, 9, 30):
            return None
        for L in limiares:
            if prim[L] is None and pw.tmin[k] <= L:
                prim[L] = d
        soma += gdd_dia(pw, k)
        d += dt.timedelta(1)
    return dict(ano=ano, silagem=d, dias=(d - d0).days, prim=prim)


def _safras_dia(pw, mes, dia, gdd, anos):
    """Safras de um dia de plantio, com cache guardado no próprio objeto `pw`.

    Antes o cache era um dict global indexado por id(pw). Quando um objeto Power era liberado,
    o Python reaproveitava o id para o próximo, e a nova célula recebia as safras da anterior
    (com 20 células seguidas, SMO saía com limite 19/01 em vez de 05/02)."""
    cache = pw.__dict__.setdefault("_cache_safras_2m", {})
    key = (mes, dia, gdd, tuple(anos))
    if key not in cache:
        cache[key] = [r for a in anos if (r := safra_2m(pw, a, mes, dia, gdd))]
    return cache[key]


def curva_2m(pw, datas=DECENDIOS_2M, gdd=GDD_PADRAO, anos=ANOS_V2, limiar=3.0):
    linhas = []
    for (m, d) in datas:
        rs = _safras_dia(pw, m, d, gdd, anos)
        n = len(rs)
        anos_com = [r["ano"] for r in rs if r["prim"][limiar]]
        k = len(anos_com)
        linhas.append(dict(decendio=f"{d:02d}/{m:02d}", k=k, n=n, em10=em10(k, n), ic95=ic10(k, n),
                           dias_ate_silagem_mediana=round(statistics.median(r["dias"] for r in rs)),
                           anos_com_geada=anos_com))
    return dict(limiar_c=limiar, gdd_alvo=gdd, base_c=10.0, teto_c=30.0, periodo=f"{anos[0]}-{anos[-1]}", linhas=linhas)


def limite_diario(pw, limiar=3.0, gdd=GDD_PADRAO, anos=ANOS_V2, corte=CORTE_LIMITE):
    """Igual a V2 `limite_diario`: plantio diário 1/jan a 31/mar; risco suavizado (média móvel de
    5 dias); limite = dia anterior ao 1º dia com risco > corte."""
    dias = []
    d = dt.date(2001, 1, 1)
    while d <= dt.date(2001, 3, 31):
        dias.append(d)
        d += dt.timedelta(1)
    risco = []
    for dd in dias:
        rs = _safras_dia(pw, dd.month, dd.day, gdd, anos)
        risco.append(sum(1 for r in rs if r["prim"][limiar]) / len(rs))
    sm = []
    for i in range(len(risco)):
        j0, j1 = max(0, i - 2), min(len(risco), i + 3)
        sm.append(sum(risco[j0:j1]) / (j1 - j0))
    lim = None
    for dd, r in zip(dias, sm):
        if r > corte:
            lim = dd - dt.timedelta(1)
            break
    return dict(limite=lim.strftime("%d/%m") if lim else None, limiar_c=limiar, gdd_alvo=gdd, corte=corte,
                risco_suavizado=[round(x, 3) for x in sm])


def limites_2m(pw):
    """Limite central (3 °C, 1.250 °C·dia) e as faixas por limiar e por ciclo."""
    central = limite_diario(pw, 3.0, GDD_PADRAO)
    por_limiar = {f"{L:g}": limite_diario(pw, L, GDD_PADRAO)["limite"] for L in LIMIARES_2M}
    por_ciclo = {str(g): limite_diario(pw, 3.0, g)["limite"] for g in GDD_SENS}
    return dict(central=central["limite"], por_limiar_c=por_limiar, por_ciclo_gdd=por_ciclo,
                corte_em10=10 * CORTE_LIMITE, risco_suavizado_3c=central["risco_suavizado"])


def ddmm_para_data(s, ano=2001):
    return dt.date(ano, int(s[3:5]), int(s[:2]))


def decendio_de(d):
    """Primeiro dia do decêndio que contém a data (dd/mm)."""
    dia = 1 if d.day <= 10 else (11 if d.day <= 20 else 21)
    return f"{dia:02d}/{d.month:02d}"


def decendio_seguinte(dec):
    d, m = int(dec[:2]), int(dec[3:5])
    if d == 21:
        m = m % 12 + 1
        return f"01/{m:02d}"
    return f"{d + 10:02d}/{m:02d}"


def indice_decendio(dec):
    """'01/01' -> 1 ... '21/12' -> 36."""
    d, m = int(dec[:2]), int(dec[3:5])
    return (m - 1) * 3 + (d - 1) // 10 + 1
