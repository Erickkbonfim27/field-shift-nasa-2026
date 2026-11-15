#!/usr/bin/env python3
"""B1-2 · Chuva na colheita e cura da cebola em Ituporanga.

Índices pré-registrados (CRITERIOS_ANTES_DO_TESTE.md):
  - chuva acumulada e dias com chuva >= 10 mm de 15/out a 31/dez;
  - "colheita sem janela de cura": nos 15 dias após a data de colheita não há 4 dias seguidos com chuva < 2 mm.
Confere com o rendimento da cebola na PAM/IBGE (sem tendência), 1981–2025.
"""
import json, datetime as dt, statistics as st
from pathlib import Path
from comum import Local, k, spearman, p_perm, sem_tendencia, acerto_piores, pam

AQUI = Path(__file__).resolve().parent
L = Local("itu")
obs = sem_tendencia(pam(AQUI / "externo/pam_cebola_ituporanga.json", "40107", "4208500"))
ctrl = {d["ano"]: d["y_mod"] for d in json.load(open(AQUI / "b1_0_resultado.json"))["cebola_itu"]["anos"]}
ANOS = [a for a in range(1981, 2026) if a in obs]


def chuva_periodo(a, d0, d1):
    d0, d1 = dt.date(a, *d0), dt.date(a, *d1)
    return [L.chuva[k(d0 + dt.timedelta(i))] for i in range((d1 - d0).days + 1)]


def sem_janela(a, mes, dia, n=15, seca=2.0, seguidos=4):
    d0 = dt.date(a, mes, dia)
    run = 0
    for i in range(n):
        if L.chuva[k(d0 + dt.timedelta(i))] < seca:
            run += 1
            if run >= seguidos: return False
        else:
            run = 0
    return True


acum = {a: sum(chuva_periodo(a, (10, 15), (12, 31))) for a in ANOS}
dias10 = {a: sum(1 for x in chuva_periodo(a, (10, 15), (12, 31)) if x >= 10) for a in ANOS}
# índice do agricultor: fração das 4 datas de colheita (1/nov, 15/nov, 1/dez, 15/dez) sem janela de cura
DATAS = [(11, 1), (11, 15), (12, 1), (12, 15)]
frac_sem = {a: sum(sem_janela(a, m, d) for m, d in DATAS) / len(DATAS) for a in ANOS}

o = [obs[a] for a in ANOS]
def bloco(nome, idx, lado):
    v = [idx[a] for a in ANOS]
    r = spearman(v, o)
    # para índices de chuva o "pior" é o maior valor: inverter o sinal para o acerto dos piores
    inv = {a: -idx[a] for a in ANOS} if lado == "neg" else idx
    h, po, pm = acerto_piores(inv, obs, 8)
    return dict(indice=nome, rho=round(r, 2), p=round(p_perm(v, o, lado=lado), 4), acerto8=h, piores_obs=po, piores_indice=pm)

resultados = [
    bloco("chuva 15/out–31/dez (mm)", acum, "neg"),
    bloco("dias com chuva >= 10 mm 15/out–31/dez", dias10, "neg"),
    bloco("fração de datas de colheita sem janela de cura", frac_sem, "neg"),
    bloco("controle: rendimento relativo do balanço hídrico", {a: ctrl[a] for a in ANOS if a in ctrl}, "pos") if all(a in ctrl for a in ANOS) else None,
]

# sensibilidade (não pré-registrada; só para leitura): correlação da chuva mês a mês
mes_a_mes = {}
for m in range(6, 13):
    fim = 30 if m in (6, 9, 11) else 31
    v = [sum(chuva_periodo(a, (m, 1), (m, fim))) for a in ANOS]
    mes_a_mes[m] = round(spearman(v, o), 2)

# C3: chance de colheita sem janela de cura por data (todos os anos 1981–2025)
todos = range(1981, 2026)
por_data = {}
for m, d in [(10, 15), (11, 1), (11, 15), (12, 1), (12, 15), (12, 31)]:
    if (m, d) == (12, 31):
        vals = [sem_janela(a, 12, 17) for a in todos]  # 15 dias até 31/dez
    else:
        vals = [sem_janela(a, m, d) for a in todos]
    por_data[f"{d:02d}/{m:02d}"] = round(10 * sum(vals) / len(vals), 1)

# chuva média por quinzena (para a curva da ficha)
quinz = {}
for m in (10, 11, 12):
    for d0, d1 in ((1, 15), (16, 30 if m == 11 else 31)):
        quinz[f"{d0:02d}-{d1:02d}/{m:02d}"] = round(st.mean(sum(chuva_periodo(a, (m, d0), (m, d1))) for a in todos), 1)

out = dict(n=len(ANOS), resultados=[r for r in resultados if r], rho_mes_a_mes=mes_a_mes, sem_janela_em_10_por_data=por_data,
           chuva_media_quinzena=quinz,
           anos=[dict(ano=a, obs_rel=round(obs[a], 3), chuva_out_dez=round(acum[a]), dias10=dias10[a], frac_sem_janela=frac_sem[a]) for a in ANOS])
json.dump(out, open(AQUI / "b1_2_resultado.json", "w"), ensure_ascii=False, indent=1)
for r in out["resultados"]: print(r)
print("rho mês a mês (chuva x rendimento):", mes_a_mes)
print("sem janela de cura, em 10 anos, por data de colheita:", por_data)
print("chuva média por quinzena:", quinz)
