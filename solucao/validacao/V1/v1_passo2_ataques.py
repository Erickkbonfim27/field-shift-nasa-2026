#!/usr/bin/env python3
"""Passo 2: ataques A1-A6 à ficha B3-3 (critérios em criterios.md). Entrada: tabela_original.json (passo 1)."""
import json
from v1_comum import *

tab = json.load(open(V1 / "tabela_original.json"))
FORA = [t for t in tab if t["papel"] == "fora B3-3"]
AMOSTRA = [t for t in tab if t["papel"].startswith("amostra")]


def passa_b33(R):
    return R["alertas"] >= 3 and R["precisao"] is not None and R["precisao"] >= 0.5 and R["precisao"] >= 2 * R["taxa_base"]


def regra_fixa(cult, lim_m=0.75, lim_c=360):
    return (lambda r: r["ind"] < lim_m) if cult == "milho" else (lambda r: r["ind"] >= lim_c)


# limiares neutros (10% extremos da própria célula, 1990-2025, sem olhar rendimento)
neutro = {}
for t in tab:
    neutro.setdefault((t["cultura"], t["ponto"]), {})[t["ano"]] = t
LIM_N = {}
for (cult, ponto), d in neutro.items():
    xs = [v["ind"] for v in d.values()]; cs = [v["chuva"] for v in d.values()]
    LIM_N[(cult, ponto)] = dict(ind=q10(xs) if cult == "milho" else q90(xs),
                               chuva=q10(cs) if cult == "milho" else q90(cs))


def regra_neutra(cult, campo="ind"):
    if cult == "milho": return lambda r: r[campo] <= LIM_N[(cult, r["ponto"])][campo]
    return lambda r: r[campo] >= LIM_N[(cult, r["ponto"])][campo]


out = {}
for cult in ("milho", "cebola"):
    g = [t for t in FORA if t["cultura"] == cult]
    o = {}
    # reprodução
    R = resumo(aplica(g, regra_fixa(cult))); R["passa_criterio_B33"] = passa_b33(R)
    R["permutacao"] = permutacao_conjunta(g, regra_fixa(cult))
    o["reproducao_B33"] = R
    # A1 limiar objetivo de B3-1/B3-2 (limiar_todos em teste1/teste2_resultado.json)
    obj = (lambda r: r["ind"] <= 0.881) if cult == "milho" else (lambda r: r["ind"] >= 282.18)
    R = resumo(aplica(g, obj)); R["passa_criterio_B33"] = passa_b33(R)
    o["A1_limiar_objetivo"] = R
    R = resumo(aplica(g, regra_neutra(cult))); R["passa_criterio_B33"] = passa_b33(R)
    R["permutacao"] = permutacao_conjunta(g, regra_neutra(cult))
    o["A1_regra_neutra_10pct"] = R
    # A2 sensibilidade
    sens = []
    grade = [round(0.70 + 0.01 * i, 2) for i in range(11)] if cult == "milho" else list(range(300, 430, 10))
    for L in grade:
        f = regra_fixa(cult, lim_m=L) if cult == "milho" else regra_fixa(cult, lim_c=L)
        R = resumo(aplica(g, f))
        sens.append(dict(limiar=L, alertas=R["alertas"], acertos=R["acertos"], precisao=R["precisao"],
                         taxa_base=R["taxa_base"], eventos=R["eventos"], acerto_evento=R["acerto_evento"],
                         passa=passa_b33(R)))
    o["A2_sensibilidade"] = sens
    # A3 corte de ano ruim
    a3 = {}
    for corte in (0.80, 0.90):
        R = resumo(aplica(g, regra_fixa(cult)), corte=corte); R["passa_criterio_B33"] = passa_b33(R)
        a3[f"corte {corte}"] = R
    o["A3_corte"] = a3
    # A6 chuva bruta, regra neutra
    R = resumo(aplica(g, regra_neutra(cult, "chuva"))); R["passa_criterio_B33"] = passa_b33(R)
    R["permutacao"] = permutacao_conjunta(g, regra_neutra(cult, "chuva"))
    o["A6_chuva_bruta_neutra"] = R
    out[cult] = o

# A3 variante: mediana t-5..t+5 (refaz rel a partir do IBGE)
from v1_passo1_reproduz import REG
rel5 = {}
for cult, ponto, pasta, arq, nome, papel in REG:
    rel5[nome] = rend_relativo(ibge(arq), raio=5)
for cult in ("milho", "cebola"):
    g = [dict(t, rel=rel5[t["regiao"]][t["ano"]]) for t in FORA if t["cultura"] == cult and t["ano"] in rel5[t["regiao"]]]
    R = resumo(aplica(g, regra_fixa(cult))); R["passa_criterio_B33"] = passa_b33(R)
    out[cult]["A3_corte"]["mediana t-5..t+5"] = R

# A4 dependência
dep = {}
def serie(nome, campo):
    return {t["ano"]: t[campo] for t in tab if t["regiao"] == nome}
pares = [("SMO 42001", "Chapecó 42002"), ("SMO 42001", "Concórdia 42005"), ("Chapecó 42002", "Concórdia 42005"),
         ("Ituporanga 42014", "Rio do Sul 42011"), ("Ituporanga 42014", "Tabuleiro 42017"), ("Rio do Sul 42011", "Tabuleiro 42017")]
for a, b in pares:
    for campo in ("ind", "rel"):
        sa, sb = serie(a, campo), serie(b, campo)
        anos = sorted(set(sa) & set(sb))
        dep[f"{a} x {b} ({campo})"] = round(spearman([sa[y] for y in anos], [sb[y] for y in anos]), 2)
# eventos novos
al_am = {c: sorted({t["ano"] for t in AMOSTRA if t["cultura"] == c and regra_fixa(c)(t)}) for c in ("milho", "cebola")}
al_fo = {c: sorted({t["ano"] for t in FORA if t["cultura"] == c and regra_fixa(c)(t)}) for c in ("milho", "cebola")}
dep["anos_alerta_amostra"] = al_am
dep["anos_alerta_B33"] = al_fo
dep["eventos_novos_B33"] = {c: sorted(set(al_fo[c]) - set(al_am[c])) for c in al_fo}
# amostra: o que a regra fixa faz na própria amostra (para comparação)
for c in ("milho", "cebola"):
    g = [t for t in AMOSTRA if t["cultura"] == c]
    dep[f"amostra_{c}"] = {k: v for k, v in resumo(aplica(g, regra_fixa(c))).items() if k != "lista_eventos"}
out["A4_dependencia"] = dep
out["limiares_neutros"] = {f"{k[0]} {k[1]}": {kk: round(vv, 3) for kk, vv in v.items()} for k, v in LIM_N.items()}

json.dump(out, open(V1 / "resultado_ataques.json", "w"), ensure_ascii=False, indent=1)
for cult in ("milho", "cebola"):
    print("=" * 20, cult)
    for k, v in out[cult].items():
        if k == "A2_sensibilidade":
            print(k); [print("   ", s) for s in v]
        elif k == "A3_corte":
            for kk, vv in v.items(): print(k, kk, {x: vv[x] for x in ("alertas", "acertos", "precisao", "taxa_base", "eventos", "acerto_evento", "passa_criterio_B33")})
        else:
            print(k, {x: v.get(x) for x in ("alertas", "acertos", "precisao", "taxa_base", "rel_medio_alerta", "eventos", "eventos_acerto", "acerto_evento", "ic95_evento", "passa_criterio_B33", "permutacao")})
            print("    eventos:", [(e["ano"], e["frac_ruim"]) for e in v["lista_eventos"]])
print(json.dumps(out["A4_dependencia"], ensure_ascii=False, indent=1))
print(out["limiares_neutros"])
