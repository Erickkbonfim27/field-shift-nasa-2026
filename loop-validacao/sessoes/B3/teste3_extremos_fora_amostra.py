#!/usr/bin/env python3
"""B3-3: regras fixas de B3-1 (ISNA < 0,75) e B3-2 (excedente >= 360 mm) aplicadas, sem recalibrar,
em outras microrregiões com outro ponto do NASA POWER. Conferência: IBGE PAM (tabela 1612)."""
import json, statistics as st
import teste1_estiagem_milho as t1
import teste2_excesso_cebola as t2
from comum import *

EXTRA = B3 / "power_extra"
CASOS = [("milho", "chapeco", "milho_micro_42002.json", "Chapecó (42002)"),
         ("milho", "concordia", "milho_micro_42005.json", "Concórdia (42005)"),
         ("cebola", "rio_do_sul", "cebola_micro_42011.json", "Rio do Sul (42011)"),
         ("cebola", "alfredo_wagner", "cebola_micro_42017.json", "Tabuleiro (42017)")]
REGRA = {"milho": ("isna_dec", lambda x: x < 0.75), "cebola": ("exced", lambda x: x >= 360)}

out, tabela = {}, []
for cult, ponto, arq, nome in CASOS:
    pw = Power(ponto, EXTRA)
    mod = t1 if cult == "milho" else t2
    mod.pw = pw
    rel = rend_relativo(ibge_serie(arq, "Rendimento"))
    anos = range(1985, 2026) if cult == "milho" else range(1984, 2026)
    ls = [s for a in anos if a in rel and (s := mod.safra(a))]
    ind, regra = REGRA[cult]
    for s in ls:
        s["rel"] = rel[s["ano"]]; s["alerta"] = regra(s[ind]); s["regiao"] = nome; s["cultura"] = cult
    tabela += ls
    al = [s for s in ls if s["alerta"]]
    out[nome] = dict(n=len(ls), ruins=sum(s["rel"] <= 0.85 for s in ls),
                     alertas=[(s["ano"], round(s[ind], 2), round(s["rel"], 2)) for s in al],
                     spearman=round(spearman([s[ind] for s in ls], [s["rel"] for s in ls]), 2))
for cult in ("milho", "cebola"):
    g = [s for s in tabela if s["cultura"] == cult]
    al = [s for s in g if s["alerta"]]
    base = sum(s["rel"] <= 0.85 for s in g) / len(g)
    prec = sum(s["rel"] <= 0.85 for s in al) / len(al) if al else None
    out[f"juntando ({cult})"] = dict(anos=len(g), freq_ruins=round(base, 2), n_alertas=len(al),
        precisao=round(prec, 2) if prec is not None else None,
        rel_medio_alerta=round(st.mean(s["rel"] for s in al), 2) if al else None,
        rel_medio_sem_alerta=round(st.mean(s["rel"] for s in g if not s["alerta"]), 2))
print(json.dumps(out, ensure_ascii=False, indent=1))
json.dump(out, open(B3 / "teste3_resultado.json", "w"), ensure_ascii=False, indent=1)

for cult, ind, lab, lim in (("milho", "isna_dec", "ISNA do milho de 20/set a 10/jan", 0.75),
                            ("cebola", "exced", "Excedente hídrico de 1/set a 30/nov, mm", 360)):
    g = [s for s in tabela if s["cultura"] == cult]
    svg_dispersao(B3 / f"teste3_{cult}_fora_amostra.svg",
                  [(s[ind], s["rel"], f'{s["ano"]} {s["regiao"].split()[0][:3]}', s["rel"] <= 0.85) for s in g],
                  lab + " (NASA POWER)", "Rendimento / mediana dos vizinhos (IBGE PAM)",
                  f"Fora da amostra ({cult}): regra fixa nas microrregiões vizinhas", limiar_x=lim, rotulos=True)
