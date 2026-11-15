#!/usr/bin/env python3
"""B1-1 · Geada no milho safrinha (2ª safra, silagem) em São Miguel do Oeste.

Para cada data de plantio (jan–mar) e cada ano (1981–2025): soma térmica base 10 °C até o ponto
de silagem (1.250 °C·dia) e se houve geada (T2M_MIN do POWER) antes disso.
"""
import json, datetime as dt, statistics as st
from pathlib import Path
from comum import Local, k

AQUI = Path(__file__).resolve().parent
L = Local("smo")
GDD_SILAGEM = 1250      # °C·dia base 10, híbrido precoce até ~1/2 a 2/3 da linha do leite [ESTIMATIVA]
GEADA_LEVE = 3.0        # T2M_MIN <= 3 °C: geada provável na relva [ESTIMATIVA]
GEADA_FORTE = 1.0       # T2M_MIN <= 1 °C: geada que queima a folhagem do milho [ESTIMATIVA]


def gdd_dia(key):
    tx = min(L.tmax[key], 30.0)
    tn = max(L.tmin[key], 10.0)
    return max(0.0, (tx + tn) / 2 - 10.0)


def safra(ano, mes, dia):
    d = dt.date(ano, mes, dia)
    soma, leve, forte = 0.0, None, None
    while soma < GDD_SILAGEM:
        key = k(d)
        if key not in L.tmin or d > dt.date(ano, 9, 30): return dict(ok=False, motivo="sem soma térmica", leve=leve, forte=forte)
        if leve is None and L.tmin[key] <= GEADA_LEVE: leve = d
        if forte is None and L.tmin[key] <= GEADA_FORTE: forte = d
        soma += gdd_dia(key)
        d += dt.timedelta(1)
    return dict(ok=True, silagem=d, dias=(d - dt.date(ano, mes, dia)).days, leve=leve, forte=forte)


ANOS = list(range(1981, 2026))
datas = [(1, 1), (1, 11), (1, 21), (2, 1), (2, 11), (2, 21), (3, 1), (3, 11)]
curva = []
por_ano = {}
for mes, dia in datas:
    rs = [safra(a, mes, dia) for a in ANOS]
    n = len(rs)
    p_leve = sum(1 for r in rs if r["leve"]) / n
    p_forte = sum(1 for r in rs if r["forte"]) / n
    dias = [r["dias"] for r in rs if r["ok"]]
    curva.append(dict(plantio=f"{dia:02d}/{mes:02d}", n=n, geada_leve_em_10=round(10 * p_leve, 1), geada_forte_em_10=round(10 * p_forte, 1),
                      dias_ate_silagem_med=round(st.median(dias)) if dias else None))
    por_ano[f"{dia:02d}/{mes:02d}"] = {a: (r["leve"].isoformat() if r["leve"] else None, r["forte"].isoformat() if r["forte"] else None) for a, r in zip(ANOS, rs)}

# data-limite: último decêndio com geada leve <= 2 em 10 (risco <= 20%)
lim = [c["plantio"] for c in curva if c["geada_leve_em_10"] <= 2.0]
lim_forte = [c["plantio"] for c in curva if c["geada_forte_em_10"] <= 2.0]

# linha de base sem dado diário: "1ª geada média" a partir das médias mensais de T2M_MIN
med_mensal = {}
for m in range(3, 9):
    vals = [L.tmin[d] for d in L.dias if int(d[4:6]) == m]
    med_mensal[m] = round(st.mean(vals), 1)

# primeira data de geada do outono por ano (para ver a variação entre anos)
prim = {}
for a in ANOS:
    d = dt.date(a, 3, 1)
    while d <= dt.date(a, 8, 31):
        if L.tmin[k(d)] <= GEADA_LEVE: prim[a] = d.timetuple().tm_yday; break
        d += dt.timedelta(1)
prim_vals = sorted(prim.values())
def doy2(s): return (dt.date(2001, 1, 1) + dt.timedelta(s - 1)).strftime("%d/%m")

# validação do proxy: eventos de geada ampla no Sul do Brasil (datas para conferir em Epagri/Ciram e INMET)
EVENTOS = {"1994-06-26": "jun/1994", "2000-07-17": "jul/2000", "2013-07-24": "jul/2013 (neve em SC)", "2021-07-29": "jul/2021",
           "2021-06-30": "jun/2021", "2022-05-19": "mai/2022 (geada precoce)"}
val = {}
for dstr, nome in EVENTOS.items():
    d0 = dt.date.fromisoformat(dstr)
    janela = [L.tmin[k(d0 + dt.timedelta(i))] for i in range(-2, 3)]
    val[nome] = dict(tmin_min=round(min(janela), 1), marca_leve=min(janela) <= GEADA_LEVE, marca_forte=min(janela) <= GEADA_FORTE)

# dias por ano com T2M_MIN <= 3 e <= 1 (média, para dizer quão raro é)
dias_leve = st.mean(sum(1 for d in L.dias if d[:4] == str(a) and L.tmin[d] <= GEADA_LEVE) for a in ANOS)
dias_forte = st.mean(sum(1 for d in L.dias if d[:4] == str(a) and L.tmin[d] <= GEADA_FORTE) for a in ANOS)

out = dict(curva=curva, data_limite_leve=lim[-1] if lim else None, data_limite_forte=lim_forte[-1] if lim_forte else None,
           tmin_media_mensal=med_mensal, primeira_geada_outono=dict(p10=doy2(prim_vals[len(prim_vals) // 10]), mediana=doy2(prim_vals[len(prim_vals) // 2]),
           p90=doy2(prim_vals[9 * len(prim_vals) // 10]), anos_sem=len(ANOS) - len(prim)),
           validacao_eventos=val, dias_ano_tmin_le3=round(dias_leve, 1), dias_ano_tmin_le1=round(dias_forte, 1), por_ano=por_ano)
json.dump(out, open(AQUI / "b1_1_resultado.json", "w"), ensure_ascii=False, indent=1)
for c in curva: print(c)
print("data-limite (leve<=2/10):", out["data_limite_leve"], "| (forte<=2/10):", out["data_limite_forte"])
print("Tmin média mensal:", med_mensal)
print("1ª geada do outono (Tmin<=3):", out["primeira_geada_outono"])
print("validação:", val)
print("dias/ano Tmin<=3:", out["dias_ano_tmin_le3"], " Tmin<=1:", out["dias_ano_tmin_le1"])
