#!/usr/bin/env python3
"""Passo 6 (revisão de 14/11/2026): a regra "10% mais secos da célula" com o percentil calculado
SÓ com anos passados, como o motor faz (motor/ano_extremo.py). O passo 4 usou 1990-2025 inteiro
(inclui anos futuros). Aqui, para cada região e ano, o alerta dispara se o ISNA daquele ano está
entre os 10% menores dos anos ANTERIORES da mesma região (percentil = 100 x n(<= valor) / n(passados) <= 10).

Escolha feita ANTES de rodar: mínimo de 15 anos passados para a região poder alertar (1990-2004
ficam sem alerta). Mesmos dados, mesmo "ano ruim" (rel <= 0,85) e mesmas funções do passo 4.
Saída: resultado_so_passado.json. Rodar de dentro de solucao/validacao/V1."""
import json
from v1_comum import *

MIN_PASSADOS = 15
VISTOS_MILHO = {1996, 2009, 2012, 2022}  # anos de alerta já vistos em B3-1/B3-3 (igual ao passo 4)
tab = [t for t in json.load(open(V1 / "tabela_extensao.json")) if t["cultura"] == "milho"]
por_reg = {}
for t in tab:
    por_reg.setdefault(t["regiao"], []).append(t)
for reg, linhas in por_reg.items():
    linhas.sort(key=lambda r: r["ano"])
    for r in linhas:
        passados = [x["ind"] for x in linhas if x["ano"] < r["ano"]]
        r["pct_passado"] = None if len(passados) < MIN_PASSADOS else 100 * sum(1 for p in passados if p <= r["ind"]) / len(passados)
        r["alerta_passado"] = r["pct_passado"] is not None and r["pct_passado"] <= 10

# amostra comparável: só os anos que PODEM alertar (>= MIN_PASSADOS anos passados)
elegiveis = [t for t in tab if t["pct_passado"] is not None]
saida = {}
for rotulo, g in (("todos_os_anos_1990_2025 (anos sem historico nao alertam)", tab), ("so_anos_com_historico", elegiveis)):
    R = resumo(aplica(g, lambda r: r["alerta_passado"]))
    perm = permutacao_conjunta(g, lambda r: r["alerta_passado"])
    R["permutacao"] = perm
    R["eventos_novos"] = [e for e in R["lista_eventos"] if e["ano"] not in VISTOS_MILHO]
    R["acerto_eventos_novos"] = f'{sum(e["acerto"] for e in R["eventos_novos"])}/{len(R["eventos_novos"])}'
    c0 = R["eventos"] >= 3
    c1 = R["acerto_evento"] is not None and R["acerto_evento"] >= 0.5 and R["acerto_evento"] >= 2 * R["taxa_base"]
    c2 = perm["p_evento"] <= 0.10
    c3 = R["rel_medio_alerta"] is not None and R["rel_medio_alerta"] <= 0.85
    R["criterios"] = dict(C0=c0, C1=c1, C2=c2, C3=c3,
                          veredito="inconclusivo" if not c0 else ("sustenta" if c1 and c2 and c3 else ("parcial" if c1 else "não sustenta")))
    saida[rotulo] = R
saida["parametros"] = dict(min_passados=MIN_PASSADOS, regioes=sorted(por_reg), corte_ano_ruim=0.85, limiar_percentil=10)
json.dump(saida, open(V1 / "resultado_so_passado.json", "w"), ensure_ascii=False, indent=1)
for k, R in saida.items():
    if k == "parametros":
        continue
    print("=" * 8, k)
    print({x: R[x] for x in ("anos_regiao", "ruins", "taxa_base", "alertas", "acertos", "precisao", "recall", "rel_medio_alerta",
                              "eventos", "eventos_acerto", "acerto_evento", "ic95_evento")}, R["permutacao"], R["criterios"])
