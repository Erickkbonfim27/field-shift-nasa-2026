# V5 · Critérios definidos antes de rodar os dados

Escrito em 14/11/2026, antes de calcular qualquer correlação no Semiárido. Os dados de PAM e POWER já estavam baixados, mas nenhum modelo foi cruzado com a PAM.

## Pergunta
O balanço hídrico de `prototipo/modelo/risco.py` (FAO-56 + FAO-33, ISNA por fase) separa os anos ruins dos bons no Semiárido, melhor do que em SC (ρ = 0,28 no milho de São Miguel do Oeste)?

## Teste (mesma lógica da B1-0)
- Rendimento simulado por ano (1985–2025) contra o rendimento da PAM/IBGE (tabela 5457, variável 112) dividido pela mediana móvel centrada de 9 anos.
- Milho (produto 40122) e feijão (40112; simulado com os parâmetros do caupi do `risco.py`).
- Plantio pela regra de início de chuva do `risco.py` (20 mm em 3 dias e sem veranico longo). Sem plantio no ano: y = 0, como no `risco.py`.
- Solo médio (125 mm/m). Parâmetros de cultura iguais aos do `risco.py`, sem ajuste depois de ver o resultado.
- Municípios: Quixadá e mais 7 (Quixeramobim, Crateús, Tauá, Irecê, Serra Talhada, Patos, Senhor do Bonfim). Escolhidos por serem do Semiárido com milho e feijão na PAM, antes de ver os resultados. Nenhum foi retirado depois.

## Critérios de sucesso (valem para "o Semiárido sustenta o motor só de água")
- C1: mediana do Spearman ρ ≥ 0,40 entre os pares município × cultura (16 pares).
- C2: mediana de acerto dos 8 piores anos ≥ 4 de 8 (acaso = 1,6).
- C3: o balanço hídrico supera a chuva bruta da estação chuvosa: mediana de (ρ do modelo − ρ da chuva) ≥ 0,05. Se não, o balanço não agrega nada à soma de chuva.
- C4: ρ ≥ 0,40 em pelo menos metade dos 16 pares.
- Conferência externa: os anos de seca conhecidos (2012–2017 e outros) aparecem entre os piores anos do modelo, e a PAM concorda com eles.
- Resultado "sustenta": C1, C2, C3 e C4 todos atendidos. "Parcial": C1 e C2 atendidos, mas não C3, ou só metade dos pares. "Não sustenta": C1 ou C2 falham.

## Linhas de base
- Média dos anos (ρ = 0; acerto 1,6 de 8 por acaso).
- Chuva bruta da estação chuvosa (jan–mai no CE, PE e PB; nov–mar na BA).

## Análises de sensibilidade (declaradas antes)
- Plantio em data fixa (15/fev; 15/dez na BA) em vez da regra de início de chuva.
- Tendência removida por regressão log-linear em vez da mediana móvel (a mediana móvel de 9 anos pode esconder a seca de 2012–2017, que dura 6 anos seguidos).
- PAM sem remover tendência.
O critério principal é o da mediana móvel de 9 anos, para comparar de igual para igual com SC.
