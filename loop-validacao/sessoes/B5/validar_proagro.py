#!/usr/bin/env python3
"""B5: confere os indicadores com o Proagro (BCB, MDPRO) por município. Só conferência.

Ano de indenização alta = coberturas deferidas / adesões >= 10%.
Milho (SMO): contrato emitido no ano Y vale para a safra colhida em Y+1 (plantio ago-out).
Cebola (Ituporanga): contrato emitido no ano Y vale para a safra colhida em Y (transplante jul-ago, colheita nov-dez).
"""
import csv
from pathlib import Path

AQUI = Path(__file__).resolve().parent
EXT = AQUI / "externo/proagro_mdpro_SMO_Ituporanga_por_ano_produto.csv"

razao = {}
for r in csv.DictReader(open(EXT), delimiter=";"):
    key = (r["municipio"], r["produto"])
    if key in [("SÃO MIGUEL DO OESTE", "MILHO"), ("ITUPORANGA", "CEBOLA")]:
        ano = int(r["ano_emissao"]) + (1 if r["produto"] == "MILHO" else 0)
        razao.setdefault(r["produto"], {})[ano] = float(r["cop_deferidas_qtde"]) / float(r["adesao_qtde"])


def placar(nome, marcados, alto, anos):
    m = {a for a in marcados if a in anos}
    tp, fp = len(m & alto), len(m - alto)
    print(f"  {nome:48s} marca {len(m):2d} acertos {tp}/{len(alto)} falsos {fp} precisão {tp/max(1,len(m)):.0%} {sorted(m)}")


# ---- milho SMO ----
mi = razao["MILHO"]; anos = sorted(mi); alto = {a for a in anos if mi[a] >= 0.10}
ind = {int(r["safra"]): r for r in csv.DictReader(open(AQUI / "indicadores_smo.csv"))}
todos = [a for a in ind if 1990 <= int(a) <= 2024]
q1 = sorted(float(ind[a]["chuva_out_fev"]) for a in todos)[len(todos) // 4]
print("Milho, São Miguel do Oeste · safras", anos[0], "-", anos[-1])
print("  razão deferidas/adesões:", {a: f"{mi[a]:.0%}" for a in anos})
print("  anos de indenização alta (>=10%):", sorted(alto))
placar("laudo: y_mun < 0,70", {a for a in anos if float(ind[a]["y_mun"]) < 0.70}, alto, anos)
placar("base: chuva out-fev < 1º quartil (1990-2024)", {a for a in anos if float(ind[a]["chuva_out_fev"]) < q1}, alto, anos)
placar("alerta B5-2 até o dia 80", {a for a in anos if ind[a]["alerta_dia"]}, alto, anos)
placar("olho do agricultor", {a for a in anos if ind[a]["olho_dia"]}, alto, anos)

# ---- cebola Ituporanga ----
ce = razao["CEBOLA"]; anos = sorted(ce); alto = {a for a in anos if ce[a] >= 0.40}
L = {int(r["ano"]): r for r in csv.DictReader(open(AQUI / "indicadores_cebola_itu.csv"))}
qs = sorted(int(L[a]["semanas_risco"]) for a in L)[(3 * len(L)) // 4]
qc = sorted(float(L[a]["chuva_ago_nov"]) for a in L)[(3 * len(L)) // 4]
print("\nCebola, Ituporanga · safras", anos[0], "-", anos[-1], "(corte de indenização alta: 40%, porque a média já é alta)")
print("  razão deferidas/adesões:", {a: f"{ce[a]:.0%}" for a in anos})
print("  anos de indenização alta (>=40%):", sorted(alto))
placar("painel: semanas de risco no quartil de cima", {a for a in anos if a in L and int(L[a]["semanas_risco"]) >= qs}, alto, anos)
placar("base: chuva ago-nov no quartil de cima", {a for a in anos if a in L and float(L[a]["chuva_ago_nov"]) >= qc}, alto, anos)
