#!/usr/bin/env python3
"""B1-0 · Controle: balanço hídrico (risco.py adaptado) contra a PAM/IBGE.

Milho em São Miguel do Oeste (plantio padrão 20/set) e cebola em Ituporanga (transplante 15/jul).
Saída: sessoes/B1/b1_0_resultado.json e impressão dos números da ficha.
"""
import json, datetime as dt, statistics as st
from pathlib import Path
from comum import Local, simular, spearman, p_perm, sem_tendencia, acerto_piores, pam, k

AQUI = Path(__file__).resolve().parent
EXT = AQUI / "externo"
LIM = 0.6  # "colher" = y >= 0,6 (mesmo corte do protótipo)

res = {}

# ======================= MILHO · SÃO MIGUEL DO OESTE =======================
L = Local("smo")
obs = sem_tendencia(pam(EXT / "pam_5457.json", "40122", "4217204"))
SOLO = "argiloso"  # Latossolos/Nitossolos argilosos do Oeste de SC [INFERÊNCIA]

def safra_milho(ano_colheita, mes, dia, solo=SOLO):
    return simular(L, "milho", solo, dt.date(ano_colheita - 1, mes, dia))

anos = [a for a in range(1985, 2026) if a in obs]
mod = {}
chuva_djf = {}
for a in anos:
    r = safra_milho(a, 9, 20)
    if r: mod[a] = r["y"]
    # linha de base dura: chuva de 1/dez a 28/fev (floração e enchimento)
    d0, d1 = dt.date(a - 1, 12, 1), dt.date(a, 2, 28)
    chuva_djf[a] = sum(L.chuva[k(d0 + dt.timedelta(i))] for i in range((d1 - d0).days + 1))
anos = sorted(mod)
y_mod = [mod[a] for a in anos]
y_obs = [obs[a] for a in anos]
y_chu = [chuva_djf[a] for a in anos]
rho = spearman(y_mod, y_obs)
rho_chu = spearman(y_chu, y_obs)
hit, piores_obs, piores_mod = acerto_piores(mod, obs, 8)
hit_chu, _, piores_chu = acerto_piores(chuva_djf, obs, 8)

# janelas de plantio (decêndio) para comparar com o ZARC e ver se a data muda a decisão
janelas = []
for mes, dia in [(8, 1), (8, 11), (8, 21), (9, 1), (9, 11), (9, 21), (10, 1), (10, 11), (10, 21), (11, 1), (11, 11), (11, 21), (12, 1), (12, 11), (12, 21)]:
    ys = []
    for a in range(1985, 2026):
        r = safra_milho(a, mes, dia) if mes >= 8 else None
        if r: ys.append(r["y"])
    perda = sum(1 for y in ys if y < LIM) / len(ys)
    janelas.append(dict(data=f"{dia:02d}/{mes:02d}", n=len(ys), perda_em_10=round(10 * perda, 1), y_med=round(st.median(ys), 2),
                        y_p20=round(sorted(ys)[len(ys) // 5], 2)))
# por solo, plantio padrão
por_solo = {}
for solo in ("arenoso", "medio", "argiloso"):
    ys = [safra_milho(a, 9, 20, solo)["y"] for a in range(1985, 2026)]
    por_solo[solo] = round(10 * sum(1 for y in ys if y < LIM) / len(ys), 1)

res["milho_smo"] = dict(
    n=len(anos), rho_modelo=round(rho, 2), p_modelo=round(p_perm(y_mod, y_obs, lado="pos"), 4),
    rho_chuva_djf=round(rho_chu, 2), p_chuva=round(p_perm(y_chu, y_obs, lado="pos"), 4),
    acerto8_modelo=hit, acerto8_chuva=hit_chu, piores_obs=piores_obs, piores_modelo=piores_mod, piores_chuva=piores_chu,
    janelas=janelas, perda_em_10_por_solo=por_solo,
    anos=[dict(ano=a, y_mod=round(mod[a], 3), obs_rel=round(obs[a], 3), chuva_djf=round(chuva_djf[a])) for a in anos],
)

# ======================= CEBOLA · ITUPORANGA =======================
Li = Local("itu")
obs_c = sem_tendencia(pam(EXT / "pam_cebola_ituporanga.json", "40107", "4208500"))
mod_c, exc_c = {}, {}
for a in range(1984, 2026):
    if a not in obs_c: continue
    r = simular(Li, "cebola", "medio", dt.date(a, 7, 15))
    if r:
        mod_c[a] = r["y"]
        exc_c[a] = r["excesso"]
anos_c = sorted(mod_c)
rho_c = spearman([mod_c[a] for a in anos_c], [obs_c[a] for a in anos_c])
hit_c, po_c, pm_c = acerto_piores(mod_c, obs_c, 8)
perdas_c = sum(1 for a in anos_c if mod_c[a] < LIM)
res["cebola_itu"] = dict(
    n=len(anos_c), rho_modelo=round(rho_c, 2), p_modelo=round(p_perm([mod_c[a] for a in anos_c], [obs_c[a] for a in anos_c], lado="pos"), 4),
    acerto8=hit_c, piores_obs=po_c, piores_modelo=pm_c, anos_com_perda_modelo=perdas_c,
    y_mod_mediano=round(st.median(mod_c.values()), 2), y_mod_min=round(min(mod_c.values()), 2),
    anos=[dict(ano=a, y_mod=round(mod_c[a], 3), obs_rel=round(obs_c[a], 3), excesso_mm=round(exc_c[a])) for a in anos_c],
)

json.dump(res, open(AQUI / "b1_0_resultado.json", "w"), ensure_ascii=False, indent=1)
m = res["milho_smo"]
print(f"MILHO SMO n={m['n']}  rho modelo={m['rho_modelo']} (p={m['p_modelo']})  rho chuva DJF={m['rho_chuva_djf']} (p={m['p_chuva']})")
print(f"  8 piores PAM: {m['piores_obs']}\n  8 piores modelo: {m['piores_modelo']} -> acerto {m['acerto8_modelo']}\n  8 piores chuva: {m['piores_chuva']} -> acerto {m['acerto8_chuva']}")
print("  perda em 10 por solo (20/set):", m["perda_em_10_por_solo"])
for j in m["janelas"]: print("  ", j)
c = res["cebola_itu"]
print(f"CEBOLA ITU n={c['n']} rho={c['rho_modelo']} (p={c['p_modelo']}) acerto8={c['acerto8']} anos com perda no modelo={c['anos_com_perda_modelo']} y mediano={c['y_mod_mediano']} min={c['y_mod_min']}")
print("  piores PAM", c["piores_obs"], " piores modelo", c["piores_modelo"])
