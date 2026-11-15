#!/usr/bin/env python3
"""Passo 4: extensão fora da amostra em células novas do POWER (critérios C0-C3 em criterios.md).
Regras fixas de B3-3, sem recalibrar. Rendimento: IBGE PAM tabela 1612, microrregião (só conferência)."""
import json
from v1_comum import *

# microrregião, nome, ponto (município de maior área da cultura, 2015-2023), área média micro (ha)
MILHO = [("42003", "Xanxerê", "abelardo_luz", 25519), ("42004", "Joaçaba", "fraiburgo", 61736),
         ("42006", "Canoinhas", "itaiopolis", 32349), ("42009", "Curitibanos", "campos_novos", 24393),
         ("42010", "Campos de Lages", "sao_jose_do_cerrito", 34400), ("42018", "Tubarão", "treze_de_maio", 5016),
         ("42019", "Criciúma", "icara", 7955), ("42020", "Araranguá", "turvo", 7893)]
# cebola: 42002 fica fora (microrregião já usada em B3-3); 42005 fora (ponto = célula de Concórdia, já usada)
# 42008 fora (6 anos); 42015 fora (Leoberto Leal = célula de Ituporanga? conferido abaixo)
CEBOLA = [("42003", "Xanxerê", "ipuacu", 48), ("42004", "Joaçaba", "lebon_regis", 1862),
          ("42006", "Canoinhas", "irineopolis", 332), ("42007", "São Bento do Sul", "campo_alegre", 4),
          ("42009", "Curitibanos", "curitibanos", 358), ("42010", "Campos de Lages", "bom_retiro", 1322),
          ("42016", "Florianópolis", "sao_pedro_de_alcantara", 6), ("42018", "Tubarão", "pedras_grandes", 38),
          ("42019", "Criciúma", "icara", 6)]
VISTOS = {"milho": {1996, 2009, 2012, 2022}, "cebola": {1997, 2008, 2015, 2023}}  # anos de alerta em B3-1/2/3


def rend_micro(arq, cod):
    rows = json.load(open(EXTERNO_V1 / arq))[1:]
    return {int(r["D3N"]): float(r["V"]) for r in rows
            if r["D1C"] == cod and r["D2C"] == "112" and r["V"] not in ("...", "-", "X", "..", "0")}


tab = []
for cult, lista, arq in (("milho", MILHO, "milho_micro_sc.json"), ("cebola", CEBOLA, "cebola_micro_sc.json")):
    for cod, nome, ponto, area in lista:
        serie = rend_micro(arq, cod)
        if len([a for a in serie if 1990 <= a <= 2025]) < 20:
            print("fora (menos de 20 safras):", cult, cod); continue
        rel = rend_relativo(serie)
        pw = Power(ponto, POWER_V1)
        for a in range(1990, 2026):
            if a not in rel: continue
            s = ind_milho(pw, a) if cult == "milho" else ind_cebola(pw, a)
            if not s: continue
            L = dict(cultura=cult, regiao=f"{nome} {cod}", ponto=ponto, area=area, ano=a, rel=round(rel[a], 4))
            if cult == "milho": L.update(ind=round(s["isna_dec"], 4), chuva=round(s["chuva_novdez"], 1))
            else: L.update(ind=round(s["exced"], 1), chuva=round(s["chuva"], 1), isna=round(s["isna"], 4))
            tab.append(L)
json.dump(tab, open(V1 / "tabela_extensao.json", "w"), ensure_ascii=False, indent=0)

LIM_N = {}
for t in tab:
    LIM_N.setdefault((t["cultura"], t["ponto"]), []).append(t)
LIM_N = {k: dict(ind=(q10 if k[0] == "milho" else q90)([x["ind"] for x in v]),
                 chuva=(q10 if k[0] == "milho" else q90)([x["chuva"] for x in v])) for k, v in LIM_N.items()}
FIXA = {"milho": lambda r: r["ind"] < 0.75, "cebola": lambda r: r["ind"] >= 360}


def neutra(cult, campo="ind"):
    if cult == "milho": return lambda r: r[campo] <= LIM_N[(cult, r["ponto"])][campo]
    return lambda r: r[campo] >= LIM_N[(cult, r["ponto"])][campo]


def veredito(R, perm):
    c0 = R["eventos"] >= 3
    c1 = R["acerto_evento"] is not None and R["acerto_evento"] >= 0.5 and R["acerto_evento"] >= 2 * R["taxa_base"]
    c2 = perm["p_evento"] <= 0.10
    c3 = R["rel_medio_alerta"] is not None and R["rel_medio_alerta"] <= 0.85
    v = "inconclusivo" if not c0 else ("sustenta" if c1 and c2 and c3 else ("parcial" if c1 else "não sustenta"))
    return dict(C0=c0, C1=c1, C2=c2, C3=c3, veredito=v)


out = {}
for cult in ("milho", "cebola"):
    for rotulo, filtro in (("todas", lambda t: True), ("area>=100ha", lambda t: t["area"] >= 100)):
        if cult == "milho" and rotulo != "todas": continue
        g = [t for t in tab if t["cultura"] == cult and filtro(t)]
        o = {"regioes": sorted({t["regiao"] for t in g})}
        for nome_regra, fn in (("regra_fixa_B33", FIXA[cult]), ("regra_neutra_10pct", neutra(cult)),
                               ("chuva_bruta_neutra", neutra(cult, "chuva"))):
            R = resumo(aplica(g, fn))
            perm = permutacao_conjunta(g, fn)
            R["permutacao"] = perm
            R["criterios"] = veredito(R, perm)
            ev = R["lista_eventos"]
            R["eventos_novos"] = [e for e in ev if e["ano"] not in VISTOS[cult]]
            R["acerto_eventos_novos"] = f'{sum(e["acerto"] for e in R["eventos_novos"])}/{len(R["eventos_novos"])}'
            # alertas por região
            R["por_regiao"] = {}
            for reg in o["regioes"]:
                gg = [t for t in g if t["regiao"] == reg]
                R["por_regiao"][reg] = dict(anos=len(gg), ruins=sum(t["rel"] <= 0.85 for t in gg),
                                            alertas=[(t["ano"], t["ind"], t["rel"]) for t in gg if fn(t)])
            o[nome_regra] = R
        out[f"{cult} ({rotulo})"] = o

# dependência: rendimento relativo das regiões novas x SMO / Ituporanga (rel da amostra)
orig = json.load(open(V1 / "tabela_original.json"))
ref = {"milho": {t["ano"]: t["rel"] for t in orig if t["regiao"] == "SMO 42001"},
       "cebola": {t["ano"]: t["rel"] for t in orig if t["regiao"] == "Ituporanga 42014"}}
refi = {"milho": {t["ano"]: t["ind"] for t in orig if t["regiao"] == "SMO 42001"},
        "cebola": {t["ano"]: t["ind"] for t in orig if t["regiao"] == "Ituporanga 42014"}}
dep = {}
for cult in ("milho", "cebola"):
    for reg in sorted({t["regiao"] for t in tab if t["cultura"] == cult}):
        s = {t["ano"]: t for t in tab if t["regiao"] == reg and t["cultura"] == cult}
        anos = sorted(set(s) & set(ref[cult]))
        dep[f"{cult} {reg}"] = dict(rel_x_ref=round(spearman([s[a]["rel"] for a in anos], [ref[cult][a] for a in anos]), 2),
                                    ind_x_ref=round(spearman([s[a]["ind"] for a in anos], [refi[cult][a] for a in anos]), 2))
out["dependencia_com_amostra"] = dep
out["limiares_neutros"] = {f"{k[0]} {k[1]}": {kk: round(vv, 3) for kk, vv in v.items()} for k, v in LIM_N.items()}
json.dump(out, open(V1 / "resultado_extensao.json", "w"), ensure_ascii=False, indent=1)

for k, o in out.items():
    if k in ("dependencia_com_amostra", "limiares_neutros"): continue
    print("=" * 10, k, o["regioes"])
    for r in ("regra_fixa_B33", "regra_neutra_10pct", "chuva_bruta_neutra"):
        R = o[r]
        print(r, {x: R[x] for x in ("anos_regiao", "ruins", "taxa_base", "alertas", "acertos", "precisao", "recall",
                                     "rel_medio_alerta", "eventos", "eventos_acerto", "acerto_evento", "ic95_evento",
                                     "acerto_eventos_novos")}, R["permutacao"], R["criterios"])
        print("   eventos:", [(e["ano"], e["frac_ruim"], len(e["regioes"])) for e in R["lista_eventos"]])
print(json.dumps(dep, ensure_ascii=False))
