#!/usr/bin/env python3
"""Passo 1: reproduzir B3-3 e montar a tabela ano x região (indicador, rendimento relativo).
Também guarda as regiões da amostra original (B3-1: 42001; B3-2: 42014)."""
import json
from v1_comum import *

EXTRA = B3 / "power_extra"
REG = [  # cultura, ponto POWER, pasta, arquivo IBGE, nome, papel
    ("milho", "sao_miguel_do_oeste", None, "milho_micro_smo.json", "SMO 42001", "amostra B3-1"),
    ("milho", "chapeco", EXTRA, "milho_micro_42002.json", "Chapecó 42002", "fora B3-3"),
    ("milho", "concordia", EXTRA, "milho_micro_42005.json", "Concórdia 42005", "fora B3-3"),
    ("cebola", "ituporanga", None, "cebola_micro_ituporanga.json", "Ituporanga 42014", "amostra B3-2"),
    ("cebola", "rio_do_sul", EXTRA, "cebola_micro_42011.json", "Rio do Sul 42011", "fora B3-3"),
    ("cebola", "alfredo_wagner", EXTRA, "cebola_micro_42017.json", "Tabuleiro 42017", "fora B3-3"),
]

if __name__ == "__main__":
    tab = []
    for cult, ponto, pasta, arq, nome, papel in REG:
        pw = Power(ponto, pasta)
        rel = rend_relativo(ibge(arq))
        for a in range(1990, 2026):
            if a not in rel: continue
            s = ind_milho(pw, a) if cult == "milho" else ind_cebola(pw, a)
            if not s: continue
            linha = dict(cultura=cult, regiao=nome, papel=papel, ponto=ponto, ano=a, rel=round(rel[a], 4))
            if cult == "milho":
                linha.update(ind=round(s["isna_dec"], 4), chuva=round(s["chuva_novdez"], 1))
            else:
                linha.update(ind=round(s["exced"], 1), chuva=round(s["chuva"], 1), isna=round(s["isna"], 4))
            tab.append(linha)
    json.dump(tab, open(V1 / "tabela_original.json", "w"), ensure_ascii=False, indent=0)

    # reprodução da tabela de B3-3
    regra = {"milho": lambda x: x < 0.75, "cebola": lambda x: x >= 360}
    for cult in ("milho", "cebola"):
        g = [t for t in tab if t["cultura"] == cult and t["papel"] == "fora B3-3"]
        al = [t for t in g if regra[cult](t["ind"])]
        base = sum(t["rel"] <= 0.85 for t in g) / len(g)
        print(cult, "anos", len(g), "base", round(base, 3), "alertas", len(al),
              "acertos", sum(t["rel"] <= 0.85 for t in al))
        for t in al: print("   ", t["regiao"], t["ano"], t["ind"], t["rel"])
    # valores perto do limiar
    print("\nPerto do limiar (milho 0,70-0,80; cebola 300-420):")
    for t in tab:
        if (t["cultura"] == "milho" and 0.70 <= t["ind"] <= 0.80) or (t["cultura"] == "cebola" and 300 <= t["ind"] <= 420):
            print("   ", t["regiao"], t["ano"], t["ind"], t["rel"])
