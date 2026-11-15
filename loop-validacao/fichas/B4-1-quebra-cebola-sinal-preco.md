# B4-1 · Sinal climático de quebra da cebola (oferta curta, preço alto, e o tombo do ano seguinte)

Sessão: B4 · Trilha: B · Região: Ituporanga · Tentativa 1 de 4 · Data: 2026-11-14

## 1. Ideia (escrita antes do teste)
- **Hipótese:** primavera muito chuvosa em Ituporanga (set–nov, fase de bulbificação) derruba a produtividade da cebola de Santa Catarina. Como SC é o maior produtor e colhe junto com o resto do Sul (nov–jan), essa quebra encurta a oferta e sobe o preço. No ano seguinte, a área cresce e o preço cai. Um índice só com chuva do NASA POWER, fechado no fim de novembro, antecipa a quebra e o tombo do ano seguinte.
- **Problema que ataca (e para quem):** o produtor familiar de cebola do Alto Vale vê o preço alto de um ano de quebra e aumenta a área no ano seguinte, junto com todo mundo; a cebola sobra e o preço desaba (ex.: 2023 caro, 2024 e 2025 baratos, a conferir).
- **Decisão que muda:** (a) no fim de novembro, num ano marcado como "quebra": não fechar venda antecipada a preço de ano normal; (b) em abril–maio do ano seguinte (semeadura das mudas): não aumentar a área de cebola por causa do preço alto, porque ele veio do clima e tende a voltar.
- **Critério de sucesso (definido antes):**
  1. Índice = chuva total de set–nov (POWER, Ituporanga). Correlação de Spearman com a produtividade de SC sem tendência, 1985–2025: **ρ ≤ −0,40**.
  2. Anos de alarme (terço mais chuvoso do índice) pegam **pelo menos 60%** dos anos de quebra (produtividade ≥ 15% abaixo da tendência), contra 33% do acaso.
  3. Preço real (IBGE, valor ÷ quantidade, corrigido pelo IPCA), 1995–2025: média nos anos de alarme **≥ 20% acima** dos outros anos.
  4. Ano seguinte a um alarme: preço real cai em **pelo menos 70%** dos casos, contra a taxa de queda de um ano qualquer.
  - Aprovada se 1, 2 e pelo menos um de 3 ou 4 passarem.
- **Linha de base:** "não fazer nada" = tratar todo ano como normal (prever a produtividade da tendência e o preço médio). Para o item 2, o acaso (33%). Para o item 4, a frequência de queda do preço de um ano para o outro em todos os anos.

## 2. Teste
- **Dados oficiais usados:** NASA POWER (comunidade AG), `PRECTOTCORR` diário, ponto -27,414; -49,601 (Ituporanga), 1985–2025, grade de ~50 km. Arquivo `dados/power_ituporanga.json`.
- **Método:** (1) índice = soma da chuva de 1º/set a 30/nov de cada ano; (2) produtividade da cebola de SC e de Ituporanga (IBGE PAM, ano = ano da colheita) sem tendência (quadrática 1985–2025 e linear 1995–2025); (3) Spearman; (4) alarme = terço mais chuvoso; quebra = ≥ 15% abaixo da tendência; (5) preço real = valor ÷ quantidade da PAM, corrigido pelo IPCA. Scripts: `sessoes/B4/teste1_cebola.py`, `teste1_exploratorio.py`, `teste1_epagri_split.py`.
- **Resultado (pré-registrado):**
  - Produtividade SC × chuva: ρ = −0,11 (p = 0,49; n = 41) e −0,12 (linear 1995–2025). [CÁLCULO]
  - Quebras pegas pelo alarme: 4 de 5 (80%) em 1995–2025 e 4 de 6 (67%) em 1985–2025, mas com 6 alarmes falsos em 10. As quebras pegas (1997, 1998, 2015, 2023) são todas primaveras de El Niño. [CÁLCULO] [INFERÊNCIA]
  - Preço real IBGE: anos de alarme R$ 1,54/kg contra R$ 1,60/kg nos outros (−4%). O preço anual implícito do IBGE nem acompanha a quantidade colhida em SC (ρ = +0,16). [CÁLCULO]
  - Ano seguinte a um alarme: o preço IBGE caiu em 4 de 10, contra 50% de um ano qualquer. [CÁLCULO]
- **Conferência extra, depois do teste (troca só a fonte do preço, não o índice):** preço mensal recebido pelo produtor da Epagri/Cepa (cebola pera SC classe 3 a 5), média de nov–dez da safra, corrigido pelo IPCA, 1997–2025 (n = 28):
  - Chuva set–nov × preço da colheita sem tendência: **ρ = +0,60 (p = 0,001)**; estável nas duas metades (1997–2010: +0,63; 2011–2025: +0,50) e sem 2023 (+0,56). [CÁLCULO]
  - Anos de alarme: preço da colheita 27% acima da tendência; outros anos, 13% abaixo. [CÁLCULO]
  - Safra seguinte a um alarme: preço menor em 6 de 9 (67%), contra 44% de um ano qualquer. [CÁLCULO]
- **Gráficos:** `sessoes/B4/grafico1_cebola.svg` (com o preço do IBGE, nada aparece) e `sessoes/B4/grafico3_cebola_preco_mensal.svg`, painel da esquerda (com o preço mensal da Epagri, o preço da colheita sobe com a chuva de primavera).

## 3. Validação
- **Contra a linha de base:** "todo ano normal" erra todas as quebras; o alarme pega 4 de 5 (contra 33% do acaso), mas com 60% de alarmes falsos. No preço da colheita (Epagri), o alarme separa os anos +27% dos −13%; a linha de base não separa nada.
- **Fonte externa:** IBGE PAM t.5457 (produtividade e valor) e IPCA t.1737; Epagri/Cepa, série de preços recebidos 1998–2026. A Epagri/Cepa registrou queda de cerca de 27% na safra 2023/24 de SC, com preço em mar/2024 de R$ 3,82/kg, o maior nominal desde nov/2019 (bate com o alarme de 2023, o mais chuvoso da série, 886 mm). [DADO, via reportagem da Epagri; conferir no boletim]
- **O critério de sucesso foi atingido?** **Não** no pré-registro: passou o item 2; falharam o 1 (ρ = −0,11), o 3 com o preço do IBGE (−4%) e o 4 (4 de 10). Com o preço mensal da Epagri, o 3 passaria com folga e o 4 ficaria em 67%, perto do limiar de 70%; mas essa troca foi feita depois de ver o resultado.

## 4. Régua (1 a 5)
| Critério | Nota | Por quê (uma frase) |
|---|---|---|
| Problema real | 4 | O vaivém de preço da cebola é real: R$ 3,26/kg em 2023 e R$ 0,88/kg em 2025 (IBGE, reais de 2025), e a área plantada de SC subiu 3,5% no ano seguinte à quebra de 2023 (IBGE). |
| Tamanho do impacto | 3 | Mexe na venda e na área de cerca de 1 ano em 3; o ganho por ano não foi medido. |
| Resolve de fato | 3 | Muda a venda antecipada nos anos de alarme e dá argumento para não expandir área, mas o "não expanda" só acerta 6 de 9 (Epagri). |
| Validade | 3 | O sinal no preço da colheita é forte e estável (ρ = +0,60), mas veio de uma conferência fora do pré-registro; o pré-registro falhou. |
| Muda a decisão | 3 | Só atua em anos de primavera muito chuvosa; nos outros, a resposta é "ano normal". |
| Simples e factível | 5 | Uma soma de chuva do POWER por ponto. |
| Alinhamento com o desafio | 4 | A entrada é só NASA; preço entra só para validar; a ligação com rotação é fraca (é decisão de área e de venda). |
| Diferencial | 4 | Ninguém no time usa clima como sinal de mercado; o ZARC não fala de preço. |
| Cabe no hackathon | 5 | Já está calculado, com dados baixados. |
| **Total (máx. 45)** | **34** | |

## 5. Veredito
**Ajustar.** Como sinal de produtividade, a chuva de primavera falha (só pega os extremos de El Niño). Como sinal do **preço da colheita** em SC, funciona bem com o preço mensal da Epagri, mas isso precisa ser repetido como teste pré-registrado (ou fora da amostra, ex.: safra 2026) antes de ir para o pitch. Fundir com a B4-3 numa só regra de venda.

## 6. Relação com o controle
**Complementa.** O controle usa a chuva para dizer "quanto risco de perder a lavoura"; esta usa a mesma chuva para dizer "o que isso faz com o preço da sua cebola". Na demo: depois do cartão "chance de colher", um segundo cartão em novembro: "primavera muito chuvosa no Sul: preço da colheita tende a ficar alto; não feche venda antecipada; não aumente a área no ano que vem só por esse preço".

## 7. Limites e o que não foi testado
- Um ponto do POWER (~50 km) para representar a oferta do Sul; não somei pontos do PR e do RS nem a Argentina (que entra no mercado em dez–mar).
- A produtividade municipal e estadual do IBGE é estimativa arredondada (Ituporanga repete 12.000, 20.000, 30.000 kg/ha); isso pode ter escondido o sinal na produtividade.
- Preço anual implícito do IBGE é ruim para este uso: mistura safras e meses. O preço mensal da Epagri é melhor, mas só existe em nov–abr (meses de venda da cebola de SC) e 2007–2008 é trimestral.
- Teste extra fora do pré-registro; amostra de 28 safras; 9 anos de alarme.
- Bate com a B3-2 (excesso de chuva na cebola): a chuva explica os anos extremos (2008, 2015, 2023), não o ano a ano da produtividade.
- O código IBGE do protocolo (4208401) é Itapiranga; usei Ituporanga = 4208500.

## 8. Fontes
- NASA POWER, API diária, comunidade AG: https://power.larc.nasa.gov/ (arquivo `dados/power_ituporanga.json`).
- IBGE SIDRA, PAM t.5457, cebola (c782/40107), Ituporanga 4208500 e SC: https://apisidra.ibge.gov.br/values/t/5457/n3/42/v/112,214,215,216,8331/p/all/c782/40107 (cópia em `sessoes/B4/ext/`).
- IBGE SIDRA, IPCA t.1737: https://apisidra.ibge.gov.br/values/t/1737/n1/all/v/2266/p/all
- Epagri/Cepa, preços recebidos pelos produtores 1998–2026: https://docweb.epagri.sc.gov.br/website_cepa/precos/Precos_recebidos_1998_2026.xlsx (página: https://cepa.epagri.sc.gov.br/index.php/mercado-agricola/).
- Epagri/Cepa, safra 2023/24 e preço de mar/2024, via Revista Cultivar: https://revistacultivar.com.br/noticias/baixa-oferta-faz-precos-do-alho-e-da-cebola-subirem-aponta-boletim-agropecuario-de-abril
