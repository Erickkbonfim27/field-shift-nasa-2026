# B5-3 · Painel semanal do extensionista: semanas de risco de doença na cebola

Sessão: B5 · Trilha: B · Região: Ituporanga (cebola) · Tentativa 3 de 4 · Data: 2026-11-14

## 1. Ideia (escrita antes do teste)
- **Hipótese:** um painel semanal para o extensionista da Epagri, que marca as semanas de tempo úmido e ameno (favorável ao míldio e a outras doenças de folha da cebola), concentra os anos de quebra da cebola em Ituporanga e ajuda o técnico a escolher quando visitar e reforçar a orientação de manejo.
- **Problema que ataca (e para quem):** um extensionista atende centenas de famílias; a cebola do Alto Vale perde produtividade em primaveras muito úmidas. O técnico não consegue estar em todas as lavouras na semana certa.
- **Decisão que muda:** a agenda do técnico (que semana fazer reunião ou visita, quando mandar o aviso de manejo no grupo de WhatsApp) e, para o agricultor, quando reforçar a proteção da lavoura.
- **Critério de sucesso (definido antes):**
  - Dia de risco = chuva (PRECTOTCORR) de 2 mm ou mais, umidade relativa (RH2M) de 85% ou mais e temperatura média (T2M) entre 10 e 24 °C. Semana de risco = 4 ou mais dias de risco em 7 (semanas fixas de 1º de agosto a 30 de novembro).
  - Ano de quebra = rendimento da cebola no IBGE/PAM abaixo de 70% da tendência linear de 1990–2024; se der menos de 3 anos, usar 80%.
  - O índice da safra (número de semanas de risco, no quartil de cima) acerta pelo menos **2 de cada 3 anos de quebra** com **precisão de 50% ou mais**, e supera a linha de base.
  - O painel fica vermelho em **no máximo 6 semanas por safra** em média (senão não serve para priorizar).
- **Linha de base:** chuva total de agosto a novembro no quartil de cima (a regra "ano chuvoso") e o acaso.

## 2. Teste
- **Dados oficiais usados:** NASA POWER diário (comunidade AG), ponto -27,414; -49,601, variáveis `PRECTOTCORR`, `RH2M`, `T2M`, 1990–2024, grade de ~50 km. [DADO]
- **Método:** (1) marca cada dia de risco; (2) conta as semanas com 4+ dias de risco em 17 semanas fixas de agosto a novembro; (3) compara com os anos de quebra do IBGE/PAM. Script: `sessoes/B5/painel_cebola.py`; saída: `sessoes/B5/indicadores_cebola_itu.csv` e `resultado_cebola_itu.txt`.
- **Resultado:** [CÁLCULO]
  - Com o corte de 70% só sobrou 1 ano (1996), então valeu a regra de reserva (80%): **6 anos de quebra**, que são 1996, 1997, 1998, 2015, 2017 e 2023.
  - O painel marca 11 safras (empates no limiar de 5 semanas) e **acerta 5 dos 6 anos de quebra (83%)**, com **precisão de 45%** (6 alarmes falsos: 1990, 2001, 2008, 2009, 2014, 2021). Só 2017 escapou.
  - Média de **4,1 semanas vermelhas por safra** (de 17). Nos anos de quebra são **7,2**; nos anos normais, **3,5**.
  - Correlação de Spearman entre as semanas de risco e o rendimento relativo: **0,45** (a chuva total dá 0,16).
- **Gráfico:** `sessoes/B5/grafico_b5_3_cebola.svg`. As barras vermelhas (quebra) de 1996–98, 2015 e 2023 caem quase todas sob as marcas do painel; a regra da chuva pega só 3 delas.

## 3. Validação
- **Contra a linha de base:** painel 5 de 6 acertos e precisão de 45%; chuva de agosto a novembro no quartil de cima, 3 de 6 e 33%; acaso, precisão esperada de 17% (6 em 35). [CÁLCULO]
- **Fonte externa:**
  - A Epagri estimou perda de 25% a 30% na cebola de SC em 2023 pelo excesso de chuva de outubro no Alto Vale do Itajaí, que concentra cerca de 70% do cultivo. **Bate** com 2023 marcado (7 semanas vermelhas). [DADO] ([NSC Total](https://www.nsctotal.com.br/?p=6998374), [NSC Total](https://www.nsctotal.com.br/?p=6661249))
  - Os três anos de quebra mais marcados (1997, 2015 e 2023) são primaveras de El Niño forte, que traz chuva acima da média ao Sul. [INFERÊNCIA] ([NOAA CPC, ONI](https://origin.cpc.ncep.noaa.gov/products/analysis_monitoring/ensostuff/ONI_v5.php))
  - **Proagro da cebola em Ituporanga (BCB), 2013–2024:** a cebola tem indenização frequente (média alta), então usei o corte de 40% dos contratos com cobertura deferida, escolhido depois de ver a tabela: 2015, 2017, 2018, 2020, 2021, 2023 e 2024. O painel marca 4 desses 12 anos e **acerta 3 (precisão de 75%)**; a chuva total acerta 1. Em 2021 e 2022, **chuva excessiva** foi o evento com mais coberturas deferidas (343 e 226), à frente de seca e granizo. [DADO/CÁLCULO] (`sessoes/B5/resultado_proagro.txt`, `sessoes/B5/externo/proagro_mdpro_eventos_SC_SMO_Ituporanga_2020-2022.csv`)
  - No seguro rural (PSR), a cebola de Ituporanga é indenizada quase só por **granizo**, que o painel não vê. [DADO]
  - **A Epagri/Ciram já tem um sistema de alerta de míldio da cebola** (plataforma Agroconnect), usado em ensaio na Estação Experimental de Ituporanga para decidir as pulverizações. [DADO] ([Anais Unicruz 2019](https://unicruz.edu.br/seminario/anais/anais-2019/XXIV%20SEMINARIO%20INTERINSTITUCIONAL/Mostra%20de%20Pos-graduacao/Ciencias%20Exatas,%20agrarias%20e%20engenharias/RESUMO/INTEGRA%C3%87%C3%83O%20DE%20CULTIVAR%20RESISTENTE%20E%20SISTEMA%20DE%20ALERTA%20PARA%20O%20MANEJO%20DO%20M%C3%8DLDIO%20DA%20CEBOLA%20-%208576.pdf))
- **O critério de sucesso foi atingido?** **Em parte.** Acerto (83%), limite de semanas (4,1) e vitória sobre a linha de base, sim; precisão de 45%, abaixo dos 50% combinados. O corte de 70% teve de ser trocado pelo de reserva (80%), como previsto.

## 4. Régua (1 a 5)
| Critério | Nota | Por quê (uma frase) |
|---|---|---|
| Problema real | 4 | Primavera muito úmida derruba a cebola do Alto Vale (perda de 25% a 30% em 2023, segundo a Epagri). |
| Tamanho do impacto | 3 | O Alto Vale tem cerca de 70% da cebola de SC, mas o painel só muda a agenda do técnico, não o rendimento diretamente. |
| Resolve de fato | 2 | O sinal separa bem os anos ruins, mas a ação (visita, fungicida) já é coberta pelo alerta diário de míldio da Epagri/Ciram e não testamos se o painel reduziria a perda. |
| Validade | 3 | Supera a linha de base com dado oficial (5 de 6 contra 3 de 6) e bate com a perda de 2023 relatada pela Epagri, mas a precisão ficou em 45% e a amostra é de 6 anos. |
| Muda a decisão | 2 | Em anos ruins, o painel dobra as semanas vermelhas (7,2 contra 3,5), mas o técnico já recebe o alerta de míldio por outro canal. |
| Simples e factível | 4 | Três variáveis do POWER e uma regra de contagem. |
| Alinhamento com o desafio | 2 | É manejo sanitário e agenda de assistência, longe da escolha de rotação. |
| Diferencial | 1 | O Agroconnect da Epagri/Ciram já emite o alerta de míldio da cebola. |
| Cabe no hackathon | 4 | Já está pronto; vira uma aba do painel em poucas horas. |
| **Total (máx. 45)** | **25** | |

Aprovada só com 3+ em problema real, resolve de fato e validade.

## 5. Veredito
**Descartada como produto.** O sinal é bom (melhor que a chuva total), mas o alerta de doença da cebola já existe na Epagri/Ciram, e "resolve de fato" ficou em 2. O achado de que as primaveras úmidas explicam a quebra da cebola serve ao controle.

## 6. Relação com o controle
Complementa. No controle, a cebola de Ituporanga deveria ter um risco de **excesso de chuva** na primavera, e não só de falta de água: o índice de semanas úmidas acertou 5 dos 6 anos de quebra. Na demo, entra como uma linha no cartão da cebola ("em 10 primaveras parecidas, 4 tiveram muitas semanas úmidas"), com link para o Agroconnect no lugar de um alerta próprio.

## 7. Limites e o que não foi testado
- Grade do POWER de ~50 km: a umidade e a chuva do ponto não são as do talhão no fundo do vale.
- A umidade relativa média diária não é o molhamento foliar; o míldio depende das horas de folha molhada e da temperatura noturna.
- O IBGE/PAM municipal é estimativa, com valores repetidos (12.000 kg/ha de 1992 a 1995); o corte de 70% deu só 1 ano, e foi preciso usar o de 80%.
- Granizo, preço e qualidade de armazenagem também derrubam a renda da cebola e não aparecem aqui.
- Não testamos com extensionista: se ele usaria um painel semanal a mais, além do Agroconnect e do WhatsApp que já usa.

## 8. Fontes
- NASA POWER, API diária, comunidade AG (arquivo `dados/power_ituporanga.json`).
- IBGE, PAM, tabela 5457, Ituporanga 4208500, cebola 40107: https://apisidra.ibge.gov.br/values/t/5457/n6/4208500/v/112,216,8331/p/1990-2024/c782/40107
- Perdas de 2023 (Epagri): https://www.nsctotal.com.br/?p=6998374 e https://www.nsctotal.com.br/?p=6661249
- Alerta de míldio da Epagri/Ciram (Agroconnect), ensaio em Ituporanga: anais Unicruz 2019 (link na seção 3).
- Proagro, Matriz de Dados do Proagro (BCB): https://www.bcb.gov.br/estabilidadefinanceira/proagro
- Seguro rural, SISSER/PSR (MAPA): https://dados.agricultura.gov.br/dataset/sisser3
- ONI, NOAA CPC: https://origin.cpc.ncep.noaa.gov/products/analysis_monitoring/ensostuff/ONI_v5.php
