"""V5 · análises extras: bootstrap, sem os anos sem plantio, CE/PE/PB x BA, secas conhecidas, Garantia-Safra, gráficos SVG."""
import json, statistics as st, sys, random
from pathlib import Path
import numpy as np
from scipy.stats import spearmanr
sys.path.insert(0, str(Path(__file__).resolve().parent))
import motor as M

AQUI = Path(__file__).resolve().parent
R = json.load(open(AQUI / "resultado.json"))
LOCS = [l for l in R if l != "sintese"]
CULT = ["milho", "feijao"]
NE = [l for l in LOCS if not M.LOCAIS[l]["ba"]]      # CE, PE, PB
BA = [l for l in LOCS if M.LOCAIS[l]["ba"]]

def tabela(loc, c):
    return {a["ano"]: a for a in R[loc][c]["chuva"]["anos"]}

out = {}
# ---------- 1. subconjuntos ----------
def med_rho(locs, cs=CULT, chave="principal", modo="chuva"):
    v = [R[l][c][modo][chave]["rho"] for l in locs for c in cs]
    return round(st.median(v), 3), len(v)
out["subconjuntos"] = dict(
    todos=med_rho(LOCS), ce_pe_pb=med_rho(NE), bahia=med_rho(BA),
    milho_ce_pe_pb=med_rho(NE, ["milho"]), feijao_ce_pe_pb=med_rho(NE, ["feijao"]),
    milho_bahia=med_rho(BA, ["milho"]), feijao_bahia=med_rho(BA, ["feijao"]),
    ce_pe_pb_data_fixa=med_rho(NE, modo="fixo"), bahia_data_fixa=med_rho(BA, modo="fixo"),
    milho_data_fixa_todos=med_rho(LOCS, ["milho"], modo="fixo"), feijao_data_fixa_todos=med_rho(LOCS, ["feijao"], modo="fixo"),
)

# ---------- 2. sem os anos sem plantio (o balanço sozinho, sem a regra de início) ----------
sp = {}
rhos_sp, rho_regra = [], []
for l in LOCS:
    for c in CULT:
        t = tabela(l, c)
        anos = [a for a, x in t.items() if x["plantio"] and x["pam_rel"] is not None]
        if len(anos) < 15: continue
        r = spearmanr([t[a]["y_mod"] for a in anos], [t[a]["pam_rel"] for a in anos])[0]
        # só a regra: plantou (1) ou não (0)
        todos = [a for a, x in t.items() if x["pam_rel"] is not None]
        flag = [1 if t[a]["plantio"] else 0 for a in todos]
        rr = spearmanr(flag, [t[a]["pam_rel"] for a in todos])[0] if 0 < sum(flag) < len(flag) else float("nan")
        sp[f"{l}/{c}"] = dict(n=len(anos), rho_sem_anos_sem_plantio=round(float(r), 3), rho_so_plantou_ou_nao=None if rr != rr else round(float(rr), 3),
                               rho_com=R[l][c]["chuva"]["principal"]["rho"])
        rhos_sp.append(r); rho_regra.append(rr)
out["sem_plantio"] = dict(por_par=sp, mediana_rho_sem_anos_sem_plantio=round(float(np.median(rhos_sp)), 3),
                          mediana_rho_so_regra=round(float(np.nanmedian(rho_regra)), 3))

# ---------- 3. bootstrap dos anos (todos os pares juntos; preserva a correlação entre municípios) ----------
rng = random.Random(7)
anos_all = list(range(1985, 2026))
mat = {}
for l in LOCS:
    for c in CULT:
        t = tabela(l, c)
        mat[(l, c)] = {a: (t[a]["y_mod"], t[a]["pam_rel"], t[a]["chuva_estacao"]) for a in t if t[a]["pam_rel"] is not None and t[a]["chuva_estacao"] is not None}
def med_boot(anos, chave):
    rs = []
    for k, d in mat.items():
        xs = [d[a] for a in anos if a in d]
        if len(xs) < 15: continue
        ym, yo, yc = zip(*xs)
        rs.append(spearmanr(ym, yo)[0] if chave == "mod" else (spearmanr(ym, yo)[0] - spearmanr(yc, yo)[0]))
    return float(np.nanmedian(rs))
bm, bd = [], []
for _ in range(600):
    s = [rng.choice(anos_all) for _ in anos_all]
    bm.append(med_boot(s, "mod")); bd.append(med_boot(s, "dif"))
pc = lambda v, q: round(float(np.percentile(v, q)), 3)
out["bootstrap_anos"] = dict(mediana_rho=dict(p05=pc(bm, 5), p50=pc(bm, 50), p95=pc(bm, 95), prob_ge_040=round(float(np.mean(np.array(bm) >= 0.40)), 2)),
                             mediana_rho_menos_chuva=dict(p05=pc(bd, 5), p50=pc(bd, 50), p95=pc(bd, 95), prob_ge_005=round(float(np.mean(np.array(bd) >= 0.05)), 2)))

# ---------- 4. secas conhecidas: dos 6 municípios CE/PE/PB, quantos pares falham (y < 0,6) no modelo e na PAM ----------
def pares_ano(a, locs=NE):
    nm = npam = n = 0; ym = []; yp = []
    for l in locs:
        for c in CULT:
            d = mat[(l, c)]
            if a in d:
                n += 1; nm += d[a][0] < 0.6; npam += d[a][1] < 0.6; ym.append(d[a][0]); yp.append(d[a][1])
    return dict(n=n, modelo_falha=nm, pam_abaixo_06=npam, y_mod_medio=round(float(np.mean(ym)), 2), pam_rel_mediano=round(float(np.median(yp)), 2))
secas = [1993, 1998, 2001, 2005, 2010, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2021, 2023, 2024, 2025]
out["anos_ne"] = {a: pares_ano(a) for a in anos_all}
out["secas_conhecidas"] = {a: out["anos_ne"][a] for a in secas}
# Quixadá: PAM bruta em kg/ha de 2010 a 2025
for c, prod in (("milho", "40122"), ("feijao", "40112")):
    b = M.pam("quixada", prod)
    out[f"quixada_pam_{c}_kgha"] = {a: b.get(a) for a in range(2008, 2026)}

# ---------- 5. Garantia-Safra (MDA/SPA, Relatório Geral 2019; Tabelas 3 e 4) ----------
# safra 2011-2012 -> colheita 2012 (a safra começa em 1/jul)
adesao = {2003: 333, 2004: 365, 2005: 465, 2006: 543, 2007: 471, 2008: 635, 2009: 714, 2010: 860, 2011: 989, 2012: 1035, 2013: 1118, 2014: 1263, 2015: 1248, 2016: 1220, 2017: 1096, 2018: 1215}
perda = {2003: 148, 2004: 136, 2005: 311, 2006: 174, 2007: 390, 2008: 190, 2009: 509, 2010: 801, 2011: 261, 2012: 1015, 2013: 980, 2014: 894, 2015: 1010, 2016: 1035, 2017: 704, 2018: 560}
# ATENÇÃO: aqui o índice é o ano de término da safra (2002-2003 -> 2003). Tabela 3 tem 2002-03 a 2018-19; Tabela 4 vai até 2017/18.
# Tabela 3 (adesão): 2002-03=333 ... 2018-19=1142; Tabela 4 (perda): 2002-03=148 ... 2017-18=560. Realinha por safra:
ad = [333, 365, 465, 543, 471, 635, 714, 860, 989, 1035, 1118, 1263, 1248, 1220, 1096, 1215, 1142]   # 2002-03 .. 2018-19
pe = [148, 136, 311, 174, 390, 190, 509, 801, 261, 1015, 980, 894, 1010, 1035, 704, 560]            # 2002-03 .. 2017-18
gs = {}
for i, p in enumerate(pe):
    ano_fim = 2003 + i  # 2002-03 -> colheita em 2003
    gs[ano_fim] = round(p / ad[i], 3)
out["garantia_safra_fracao_municipios_com_perda"] = gs
reg = {}
for a in gs:
    if a < 1985 or a > 2025: continue
    d = out["anos_ne"][a]
    reg[a] = d
ys = [reg[a]["y_mod_medio"] for a in gs]
pm = [reg[a]["pam_rel_mediano"] for a in gs]
g = [gs[a] for a in gs]
# chuva bruta média (z-score por município) como base
zr = []
for a in gs:
    v = []
    for l in NE:
        d = mat[(l, "milho")]
        s = [d[b][2] for b in d]; mu, sd = np.mean(s), np.std(s)
        if a in d: v.append((d[a][2] - mu) / sd)
    zr.append(float(np.mean(v)))
out["garantia_safra_vs_regiao"] = dict(
    anos=list(gs), n=len(g),
    rho_modelo_vs_gs=round(float(spearmanr(ys, g)[0]), 3), p_modelo=round(float(spearmanr(ys, g)[1]), 4),
    rho_pam_vs_gs=round(float(spearmanr(pm, g)[0]), 3), p_pam=round(float(spearmanr(pm, g)[1]), 4),
    rho_chuva_vs_gs=round(float(spearmanr(zr, g)[0]), 3), p_chuva=round(float(spearmanr(zr, g)[1]), 4),
    tabela=[dict(ano=a, gs=gs[a], y_mod=reg[a]["y_mod_medio"], pam=reg[a]["pam_rel_mediano"]) for a in gs],
)
json.dump(out, open(AQUI / "resultado_extra.json", "w"), ensure_ascii=False, indent=1, default=str)
print(json.dumps({k: out[k] for k in ("subconjuntos", "bootstrap_anos", "garantia_safra_vs_regiao")}, ensure_ascii=False, indent=1))
print("sem plantio:", out["sem_plantio"]["mediana_rho_sem_anos_sem_plantio"], out["sem_plantio"]["mediana_rho_so_regra"])
for a in secas: print(a, out["secas_conhecidas"][a], gs.get(a))
print("QX milho", out["quixada_pam_milho_kgha"]); print("QX feijao", out["quixada_pam_feijao_kgha"])
