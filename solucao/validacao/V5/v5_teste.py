"""V5 · o balanço hídrico do risco.py contra a PAM/IBGE no Semiárido (mesma lógica da B1-0 em SC).

Saída: resultado.json e tabela no terminal.
"""
import json, datetime as dt, statistics as st, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import motor as M

AQUI = Path(__file__).resolve().parent
ANOS = range(1985, 2026)
CULT = {"milho": ("40122", "milho"), "feijao": ("40112", "caupi")}  # PAM -> cultura simulada
LOCS = list(M.LOCAIS)
SOLO = "medio"


def plantio_fixo(L, ano):
    return dt.date(ano - 1, 12, 15) if L.ba else dt.date(ano, 2, 15)


def roda(L, cult_sim, modo):
    y, chuva_ciclo, plant = {}, {}, {}
    for a in ANOS:
        pl = L.inicio_chuva(a) if modo == "chuva" else plantio_fixo(L, a)
        if pl is None:
            y[a] = 0.0; plant[a] = None; chuva_ciclo[a] = None; continue  # sem plantio: y=0 como no risco.py
        r = L.simular(cult_sim, SOLO, pl)
        if r is None: continue
        y[a] = r["y"]; plant[a] = pl.isoformat(); chuva_ciclo[a] = r["chuva_ciclo"]
    return y, plant, chuva_ciclo


def repetidos(serie):
    anos = sorted(serie)
    iguais = sum(1 for a, b in zip(anos, anos[1:]) if serie[a] == serie[b])
    return iguais / max(1, len(anos) - 1)


def avalia(modelo, obs_rel, base):
    anos = sorted(set(modelo) & set(obs_rel) & set(base))
    ym = [modelo[a] for a in anos]; yo = [obs_rel[a] for a in anos]; yb = [base[a] for a in anos]
    rho = M.spearman(ym, yo); rho_b = M.spearman(yb, yo)
    h, po, pm = M.acerto_piores({a: modelo[a] for a in anos}, {a: obs_rel[a] for a in anos}, 8)
    hb, _, pb = M.acerto_piores({a: base[a] for a in anos}, {a: obs_rel[a] for a in anos}, 8)
    return dict(n=len(anos), rho=round(rho, 3), p=round(M.p_perm(ym, yo), 4), rho_chuva=round(rho_b, 3),
                acerto8=h, p_acerto=round(M.p_hiper(h, len(anos)), 4), acerto8_chuva=hb,
                piores_pam=po, piores_modelo=pm, piores_chuva=pb)


res = {}
for loc in LOCS:
    L = M.Local(loc)
    res[loc] = {"nome": L.nome}
    chuva_j = {a: L.chuva_janela(a) for a in ANOS}
    chuva_j = {a: v for a, v in chuva_j.items() if v is not None}
    for cult, (prod, sim) in CULT.items():
        bruto = M.pam(loc, prod)
        entrada = {a: v for a, v in bruto.items() if a in ANOS and v > 0}
        obs_mm = M.sem_tendencia(M.pam(loc, prod))  # mediana móvel sobre a série completa (1974-2025)
        obs_mm = {a: v for a, v in obs_mm.items() if a in ANOS}
        obs_ll = {a: v for a, v in M.sem_tendencia_loglin({a: v for a, v in bruto.items() if v > 0}).items() if a in ANOS}
        obs_raw = {a: v for a, v in bruto.items() if a in ANOS}
        out = dict(n_pam=len(entrada), pct_repetido=round(100 * repetidos(bruto), 0))
        for modo in ("chuva", "fixo"):
            y, plant, ccic = roda(L, sim, modo)
            out["sem_plantio_" + modo] = sum(1 for a in y if plant.get(a) is None)
            # linha de base 1: chuva da estação; linha de base 2: chuva do ciclo (só no modo "chuva", onde existe plantio)
            base = chuva_j
            out[modo] = dict(
                principal=avalia(y, obs_mm, base),
                loglin=avalia(y, obs_ll, base),
                bruto=avalia(y, obs_raw, base),
            )
            if modo == "chuva":
                out[modo]["anos"] = [dict(ano=a, y_mod=round(y[a], 3), plantio=plant.get(a), pam_rel=round(obs_mm[a], 3) if a in obs_mm else None,
                                          pam_kgha=bruto.get(a), chuva_estacao=round(chuva_j[a]) if a in chuva_j else None) for a in sorted(y)]
                ycc = {a: v for a, v in ccic.items() if v is not None}
                out[modo]["chuva_ciclo"] = avalia({a: ycc[a] for a in ycc}, obs_mm, ycc)  # rho da chuva do ciclo (modelo=base)
        res[loc][cult] = out
        p = out["chuva"]["principal"]; q = out["fixo"]["principal"]
        print(f"{L.nome:24s} {cult:6s} n={p['n']} | chuva-regra rho={p['rho']:+.2f} (p={p['p']}) acerto8={p['acerto8']} | chuva bruta rho={p['rho_chuva']:+.2f} acerto8={p['acerto8_chuva']} "
              f"| data fixa rho={q['rho']:+.2f} acerto8={q['acerto8']} | loglin rho={out['chuva']['loglin']['rho']:+.2f} | sem plantio={out['sem_plantio_chuva']} | rep={out['pct_repetido']}%")

# ---------- síntese contra os critérios ----------
pares = [(loc, c) for loc in LOCS for c in CULT]
def serie(f): return [f(res[l][c]) for l, c in pares]
rhos = serie(lambda o: o["chuva"]["principal"]["rho"])
hits = serie(lambda o: o["chuva"]["principal"]["acerto8"])
dif = serie(lambda o: o["chuva"]["principal"]["rho"] - o["chuva"]["principal"]["rho_chuva"])
sint = dict(
    n_pares=len(pares), mediana_rho=round(st.median(rhos), 3), media_rho=round(st.mean(rhos), 3),
    mediana_acerto8=st.median(hits), pares_rho_ge_040=sum(1 for r in rhos if r >= 0.40),
    mediana_rho_menos_chuva=round(st.median(dif), 3),
    mediana_rho_chuva=round(st.median(serie(lambda o: o["chuva"]["principal"]["rho_chuva"])), 3),
    mediana_rho_fixo=round(st.median(serie(lambda o: o["fixo"]["principal"]["rho"])), 3),
    mediana_rho_loglin=round(st.median(serie(lambda o: o["chuva"]["loglin"]["rho"])), 3),
    mediana_rho_bruto=round(st.median(serie(lambda o: o["chuva"]["bruto"]["rho"])), 3),
    mediana_rho_ciclo=round(st.median(serie(lambda o: o["chuva"]["chuva_ciclo"]["rho"])), 3),
    por_cultura={c: dict(mediana_rho=round(st.median([res[l][c]["chuva"]["principal"]["rho"] for l in LOCS]), 3),
                         mediana_acerto8=st.median([res[l][c]["chuva"]["principal"]["acerto8"] for l in LOCS]),
                         rho_ge_040=sum(1 for l in LOCS if res[l][c]["chuva"]["principal"]["rho"] >= 0.4)) for c in CULT},
)
res["sintese"] = sint
json.dump(res, open(AQUI / "resultado.json", "w"), ensure_ascii=False, indent=1)
print("\nSÍNTESE", json.dumps(sint, ensure_ascii=False, indent=1))
