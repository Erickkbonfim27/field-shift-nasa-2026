#!/usr/bin/env python3
"""B1-3 · Calor na floração do milho em São Miguel do Oeste (critérios em CRITERIOS_ANTES_DO_TESTE.md)."""
import json, math, datetime as dt, statistics as st
from pathlib import Path
from comum import Local, k, spearman, p_perm, sem_tendencia, acerto_piores, pam, simular

AQUI = Path(__file__).resolve().parent
L = Local("smo")
obs = sem_tendencia(pam(AQUI / "externo/pam_5457.json", "40122", "4217204"))
ctrl = {d["ano"]: d["y_mod"] for d in json.load(open(AQUI / "b1_0_resultado.json"))["milho_smo"]["anos"]}
FLOR = (55, 80)
PEN = 0.05  # índice combinado: y_controle × (1 − 5% por dia de calor) [ESTIMATIVA fixada antes]


def dias_calor(ano_colheita, mes, dia, lim):
    p = dt.date(ano_colheita - 1, mes, dia)
    return sum(1 for i in range(*FLOR) if L.tmax[k(p + dt.timedelta(i))] >= lim)


ANOS = sorted(a for a in ctrl if a in obs)
o = [obs[a] for a in ANOS]
out = {}
for lim in (32.0, 34.0):
    h = {a: dias_calor(a, 9, 20, lim) for a in ANOS}
    v = [h[a] for a in ANOS]
    r = spearman(v, o)
    # correlação parcial (Spearman) descontando o controle
    c = [ctrl[a] for a in ANOS]
    rxy, rxz, ryz = r, spearman(v, c), spearman(o, c)
    parc = (rxy - rxz * ryz) / math.sqrt((1 - rxz ** 2) * (1 - ryz ** 2))
    comb = {a: ctrl[a] * max(0.0, 1 - PEN * h[a]) for a in ANOS}
    hit_c, po, pm = acerto_piores(comb, obs, 8)
    hit_h, _, ph = acerto_piores({a: -h[a] for a in ANOS}, obs, 8)
    rho_comb = spearman([comb[a] for a in ANOS], o)
    # C3: chance de >= 3 dias de calor por data de plantio
    por_data = {}
    for mes, dia in [(8, 1), (8, 21), (9, 11), (10, 1), (10, 21), (11, 11), (12, 1), (12, 21)]:
        vals = [dias_calor(a, mes, dia, lim) for a in range(1985, 2026)]
        por_data[f"{dia:02d}/{mes:02d}"] = round(10 * sum(1 for x in vals if x >= 3) / len(vals), 1)
    out[str(lim)] = dict(rho=round(r, 2), p=round(p_perm(v, o, lado="neg"), 4), rho_parcial=round(parc, 2), rho_calor_controle=round(rxz, 2),
                         acerto8_calor=hit_h, acerto8_combinado=hit_c, rho_combinado=round(rho_comb, 2), piores_obs=po, piores_comb=pm, piores_calor=ph,
                         anos_com_calor=sum(1 for x in v if x > 0), media_dias=round(st.mean(v), 2),
                         ge3_em_10_por_data=por_data, por_ano={a: h[a] for a in ANOS})
json.dump(out, open(AQUI / "b1_3_resultado.json", "w"), ensure_ascii=False, indent=1)
for lim, r in out.items():
    print(lim, {kk: vv for kk, vv in r.items() if kk != "por_ano"})
# distribuição de T2M_MAX no verão (para dizer quão raros são os picos na grade)
verao = sorted(L.tmax[d] for d in L.dias if d[4:6] in ("12", "01", "02"))
print("T2M_MAX dez–fev p50/p90/p99/máx:", verao[len(verao) // 2], verao[9 * len(verao) // 10], verao[99 * len(verao) // 100], verao[-1])
