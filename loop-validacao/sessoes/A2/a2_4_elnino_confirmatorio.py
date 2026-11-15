#!/usr/bin/env python3
"""A2-4 · Confirmatório: El Niño sabido em agosto (ONI JAS, NOAA, só para separar anos) muda o tipo de risco
de out–jan (menos seca, mais excesso) em 4 células NOVAS do POWER no Oeste de SC? Conferência: IBGE PAM milho
em 4 microrregiões. Saída: resultados/a2_4.json"""
import json, datetime as dt
import numpy as np
from base import AQUI, DADOS, soma, tercil_inferior, brier, fisher_uni, oni, fase_simples, stats

val, _ = oni()
ANOS = list(range(1981, 2025))
nino = {Y: val[("JAS", Y)] >= 0.5 for Y in ANOS}
oni_jas = {Y: val[("JAS", Y)] for Y in ANOS}

CELULAS = {"chapeco_xanxere": "dados_novos/power_chapeco.json", "concordia": "dados_novos/power_concordia.json",
           "itapiranga": "dados_novos/power_itapiranga.json", "palmitos": "dados_novos/power_palmitos.json"}
REF = {"smo (já visto)": str(DADOS / "power_sao_miguel_do_oeste.json"), "ituporanga (já visto)": str(DADOS / "power_ituporanga.json")}


def serie(arq):
    P = json.load(open(AQUI / arq if not arq.startswith("/") else arq))["properties"]["parameter"]["PRECTOTCORR"]
    ch = {k: max(0.0, v) for k, v in P.items()}
    return np.array([soma(ch, dt.date(Y, 10, 1), dt.date(Y + 1, 1, 31)) for Y in ANOS])


def avaliar(v):
    n = len(v); e = np.array([nino[Y] for Y in ANOS])
    lo, hi = np.percentile(v, [100 / 3, 200 / 3])
    seco, chuv = (v <= lo).astype(float), (v >= hi).astype(float)
    r = dict(n_nino=int(e.sum()), p_seco_nino=float(seco[e].mean()), p_seco_outros=float(seco[~e].mean()),
             p_chuv_nino=float(chuv[e].mean()), p_chuv_outros=float(chuv[~e].mean()),
             anos_secos_nino=[ANOS[i] for i in range(n) if e[i] and seco[i]],
             fisher_seco=fisher_uni(int(seco[~e].sum()), int((~e).sum()), int(seco[e].sum()), int(e.sum())),
             fisher_chuv=fisher_uni(int(chuv[e].sum()), int(e.sum()), int(chuv[~e].sum()), int((~e).sum())),
             spearman=[float(t) for t in stats.spearmanr([oni_jas[Y] for Y in ANOS], v)])
    for nome, alvo_fn in (("seco", lambda w, i, m: w[i] <= np.percentile(w[m], 100 / 3)),
                          ("chuvoso", lambda w, i, m: w[i] >= np.percentile(w[m], 200 / 3))):
        pf, pc, ob = [], [], []
        for i in range(n):
            m = np.arange(n) != i
            q = np.percentile(v[m], 100 / 3 if nome == "seco" else 200 / 3)
            oo = (v[m] <= q) if nome == "seco" else (v[m] >= q)
            oo = oo.astype(float); em = e[m]
            pc.append(oo.mean()); pf.append(oo[em == e[i]].mean()); ob.append(float(alvo_fn(v, i, m)))
        r[f"bss_{nome}"] = 1 - brier(pf, ob) / brier(pc, ob)
    r["passa_c1"] = r["p_seco_nino"] <= 0.20 and r["p_chuv_nino"] >= 0.50
    return r


saida = dict(celulas={}, referencia={})
for nome, arq in CELULAS.items(): saida["celulas"][nome] = avaliar(serie(arq))
for nome, arq in REF.items(): saida["referencia"][nome] = avaliar(serie(arq))
saida["c1_celulas_que_passam"] = sum(c["passa_c1"] for c in saida["celulas"].values())
saida["c2_bss_seco_medio"] = float(np.mean([c["bss_seco"] for c in saida["celulas"].values()]))

# IBGE PAM milho por microrregião: anomalia (razão para mediana móvel 7 anos), safra Y -> colheita Y+1
def pam(arq):
    d = json.load(open(AQUI / arq))[1:]
    out = {}
    for x in d:
        try: out[int(x["D3N"])] = float(x["V"])
        except ValueError: pass
    anom = {}
    for a in out:
        viz = [out[b] for b in range(a - 3, a + 4) if b in out and b != a]
        if len(viz) >= 4: anom[a] = out[a] / float(np.median(viz))
    return anom

MICRO = {"42001 S. Miguel do Oeste": "externo/pam_milho_micro.json", "42002 Chapecó": "externo/pam_milho_micro_42002.json",
         "42003 Xanxerê": "externo/pam_milho_micro_42003.json", "42005 Concórdia": "externo/pam_milho_micro_42005.json"}
saida["ibge"] = {}
for nome, arq in MICRO.items():
    an = pam(arq)
    en = [an[Y + 1] for Y in ANOS if (Y + 1) in an and nino[Y]]
    ou = [an[Y + 1] for Y in ANOS if (Y + 1) in an and not nino[Y]]
    saida["ibge"][nome] = dict(n_nino=len(en), n_outros=len(ou), quebra_nino=float(np.mean([a < 0.8 for a in en])),
                               quebra_outros=float(np.mean([a < 0.8 for a in ou])), media_nino=float(np.mean(en)), media_outros=float(np.mean(ou)),
                               anos_quebra_nino=[Y + 1 for Y in ANOS if (Y + 1) in an and nino[Y] and an[Y + 1] < 0.8])
saida["c3_micros_que_passam"] = sum(v["quebra_nino"] < v["quebra_outros"] for v in saida["ibge"].values())
saida["anos_nino_jas"] = [Y for Y in ANOS if nino[Y]]

json.dump(saida, open(AQUI / "resultados/a2_4.json", "w"), ensure_ascii=False, indent=1)
print("Anos El Niño (JAS):", saida["anos_nino_jas"])
for grupo in ("celulas", "referencia"):
    for nome, r in saida[grupo].items():
        print(f"{nome:22s} seco|Niño={r['p_seco_nino']:.2f} (outros {r['p_seco_outros']:.2f}, p={r['fisher_seco']:.3f}) "
              f"chuvoso|Niño={r['p_chuv_nino']:.2f} (outros {r['p_chuv_outros']:.2f}, p={r['fisher_chuv']:.3f}) "
              f"BSS seco={r['bss_seco']:+.3f} chuvoso={r['bss_chuvoso']:+.3f} rho={r['spearman'][0]:+.2f} passa={r['passa_c1']} secos Niño={r['anos_secos_nino']}")
print("C1 células que passam:", saida["c1_celulas_que_passam"], "/4 | C2 BSS seco médio:", round(saida["c2_bss_seco_medio"], 3))
for k, v in saida["ibge"].items(): print("IBGE", k, {a: (round(b, 2) if isinstance(b, float) else b) for a, b in v.items()})
print("C3 microrregiões que passam:", saida["c3_micros_que_passam"], "/4")
