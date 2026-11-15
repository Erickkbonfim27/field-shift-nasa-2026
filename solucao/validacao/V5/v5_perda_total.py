"""V5 · análise POSTERIOR (declarada como tal): na PAM, rendimento "-" (SIDRA: valor igual a zero) = perda total.

O protocolo de SC descarta "-" como dado faltante. No Semiárido, os "-" caem em 1993, 1998, 2012 e 2013,
que são anos de seca. Descartá-los tira da conta os piores anos. Aqui eles entram com rendimento 0.
Esta análise NÃO foi pré-registrada; o critério principal continua sendo o de v5_teste.py.
"""
import json, statistics as st, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import motor as M

AQUI = Path(__file__).resolve().parent
R = json.load(open(AQUI / "resultado.json"))
LOCS = [l for l in R if l != "sintese"]
PROD = {"milho": "40122", "feijao": "40112"}
NE = [l for l in LOCS if not M.LOCAIS[l]["ba"]]


def pam_zero(loc, prod):
    d = json.load(open(M.DADOS / f"pam_{loc}.json"))[1:]
    out = {}
    for r in d:
        if r["D4C"] == prod and r["D2N"].startswith("Rendimento") and int(r["D3N"]) >= 1974:
            if r["V"] == "-": out[int(r["D3N"])] = 0.0
            elif r["V"] not in ("...", "X", ".."): out[int(r["D3N"])] = float(r["V"])
    return out


res, rhos, hits, difs, zeros = {}, [], [], [], {}
for l in LOCS:
    for c, prod in PROD.items():
        b = pam_zero(l, prod)
        rel = M.sem_tendencia(b)
        t = {a["ano"]: a for a in R[l][c]["chuva"]["anos"]}
        mod = {a: t[a]["y_mod"] for a in t if a in rel}
        chuva = {a: t[a]["chuva_estacao"] for a in t if a in rel and t[a]["chuva_estacao"] is not None}
        anos = sorted(set(mod) & set(chuva))
        ym = [mod[a] for a in anos]; yo = [rel[a] for a in anos]; yc = [chuva[a] for a in anos]
        rho, rc = M.spearman(ym, yo), M.spearman(yc, yo)
        h, po, pm = M.acerto_piores({a: mod[a] for a in anos}, {a: rel[a] for a in anos}, 8)
        hc, _, _ = M.acerto_piores({a: chuva[a] for a in anos}, {a: rel[a] for a in anos}, 8)
        res[f"{l}/{c}"] = dict(n=len(anos), rho=round(rho, 3), p=round(M.p_perm(ym, yo, n=3000), 4), rho_chuva=round(rc, 3),
                               acerto8=h, p_acerto=round(M.p_hiper(h, len(anos)), 4), acerto8_chuva=hc,
                               anos_zero=[a for a in anos if b.get(a) == 0.0], piores_pam=po, piores_modelo=pm)
        rhos.append(rho); hits.append(h); difs.append(rho - rc)
        print(f"{M.LOCAIS[l]['nome']:24s} {c:6s} n={len(anos)} rho={rho:+.2f} (p={res[f'{l}/{c}']['p']}) acerto8={h} | chuva rho={rc:+.2f} acerto8={hc} | zeros={res[f'{l}/{c}']['anos_zero']}")

def med(f, ls, cs):
    return round(st.median([f(res[f"{l}/{c}"]) for l in ls for c in cs]), 3)
sint = dict(
    mediana_rho=round(st.median(rhos), 3), mediana_acerto8=st.median(hits), mediana_rho_menos_chuva=round(st.median(difs), 3),
    pares_rho_ge_040=sum(1 for r in rhos if r >= 0.4),
    milho_mediana_rho=med(lambda x: x["rho"], LOCS, ["milho"]), feijao_mediana_rho=med(lambda x: x["rho"], LOCS, ["feijao"]),
    ce_pe_pb_mediana_rho=med(lambda x: x["rho"], NE, ["milho", "feijao"]),
    ce_pe_pb_milho_mediana_rho=med(lambda x: x["rho"], NE, ["milho"]), ce_pe_pb_feijao_mediana_rho=med(lambda x: x["rho"], NE, ["feijao"]),
    bahia_mediana_rho=med(lambda x: x["rho"], [l for l in LOCS if l not in NE], ["milho", "feijao"]),
    mediana_acerto8_ce_pe_pb=st.median([res[f"{l}/{c}"]["acerto8"] for l in NE for c in PROD]),
    mediana_rho_chuva=round(st.median([res[k]["rho_chuva"] for k in res]), 3),
)
print(json.dumps(sint, ensure_ascii=False, indent=1))
json.dump(dict(por_par=res, sintese=sint), open(AQUI / "resultado_perda_total.json", "w"), ensure_ascii=False, indent=1)
