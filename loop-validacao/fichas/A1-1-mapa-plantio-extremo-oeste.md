# A1-1 · Mapa "o que plantar e quando" no Extremo Oeste

Sessão: A1 · Trilha: A · Região: São Miguel do Oeste · Tentativa 1 de 4 · Data: 2026-11-14

## 1. Ideia (escrita antes do teste, 14/11/2026, antes de rodar qualquer dado)
- **Hipótese:** um balanço hídrico por fase (FAO-56/FAO-33) mais um risco de geada, ambos só com NASA POWER, dão para cada cultura (milho safra, milho safrinha, feijão das águas, feijão da seca, sorgo, pastagem de inverno) e cada decêndio de plantio a "chance de colher bem" em São Miguel do Oeste, e esse mapa concorda com o ZARC de SC.
- **Problema que ataca (e para quem):** o agricultor familiar de leite e milho do Extremo Oeste decide a data de plantio pelo calendário habitual ou pela primeira chuva, sem saber quanto o risco muda de um decêndio para outro (estiagem de dezembro/janeiro no milho safra, geada de maio/junho no milho safrinha).
- **Decisão que muda:** em qual decêndio plantar cada cultura e se vale a pena a safrinha (ou trocar por pastagem/sorgo) quando o plantio atrasa.
- **Critério de sucesso (definido antes):**
  - (a) **Concordância com o ZARC:** nos decêndios em que o ZARC avalia a cultura, nossa classe "indicado" (chance de colher bem ≥ 7 em 10 e geada no ciclo sensível ≤ 2 em 10) bate com "indicado pelo ZARC" (qualquer risco ≤ 40%) em **≥ 70% dos decêndios**, somando as culturas com tábua disponível.
  - (b) **Validade no tempo:** o rendimento relativo simulado do milho safra na data habitual tem correlação de Spearman **≥ 0,5** com a anomalia de produtividade do milho do IBGE (PAM) em São Miguel do Oeste e acerta **≥ 3 dos 5 piores anos** do IBGE.
  - (c) **Muda a decisão:** em pelo menos 2 culturas, o melhor decêndio tem chance de colher bem **≥ 1 em 10 maior** que o decêndio habitual.
  - Aprovada se (a) e (b) forem atingidos; (c) entra na nota de "muda a decisão".
- **Definições fixadas antes de rodar:**
  - "Colher bem" = rendimento relativo hídrico (FAO-33) ≥ 0,6 (perda < 40%, mesmo corte do protótipo de Quixadá). "Geada no ciclo" = algum dia com T2M_MIN do POWER ≤ 2 °C entre a emergência (dia 7) e 90% do ciclo, só para culturas sensíveis (milho, feijão, sorgo; a pastagem de inverno é tolerante).
  - Decêndio representado pelo dia do meio (5, 15, 25). Anos de plantio 1984–2024 (41 safras; radiação só existe desde 1984).
  - Decêndios habituais [ESTIMATIVA, a conferir com Epagri/ZARC]: milho safra 21–30/set; milho safrinha 21–31/jan; feijão das águas 11–20/set; feijão da seca 1–10/fev; sorgo 11–20/out; pastagem de inverno 1–10/abr.
  - Solo principal: "argiloso" (175 mm/m, Nitossolo/Latossolo do Oeste [INFERÊNCIA]); "médio" (125 mm/m) como sensibilidade. Fixado antes da comparação com o IBGE (o mapa do solo argiloso já tinha sido rodado; a comparação com IBGE e ZARC, não).
  - Para (b): anomalia do IBGE = produtividade ÷ mediana móvel centrada de 7 anos (tira o salto de tecnologia). Ano de colheita Y ↔ plantio em set/Y−1. "Acertar um pior ano" = o ano está entre os 8 menores rendimentos simulados (20% piores de 41).
- **Linha de base:** plantar no decêndio habitual de cada cultura (sem mapa) e, para (b), a média dos anos (prever sempre o rendimento médio, correlação zero).

## 2. Teste
- **Dados oficiais usados:** NASA POWER diário, comunidade AG, ponto -26,725; -53,518 (grade ~50 km, altitude da grade 533 m), 1984–2025: `PRECTOTCORR`, `T2M`, `T2M_MAX`, `T2M_MIN`, `RH2M`, `WS2M`, `ALLSKY_SFC_SW_DWN` (arquivo `dados/power_sao_miguel_do_oeste.json`).
- **Método:** ET0 Penman-Monteith FAO-56 diária; balanço hídrico tipo balde por fase (FAO-56 Kc, FAO-33 Ky), solo cheio 60 dias antes do plantio; geada = T2M_MIN ≤ 2 °C entre o dia 7 e 90% do ciclo (fator 0,3 no rendimento); 5 culturas × 36 decêndios × 41 safras. Scripts: `sessoes/A1/modelo_sc.py` (motor, adaptado de `prototipo/modelo/risco.py`), `sessoes/A1/mapa.py`, `sessoes/A1/validar_a1_1.py`, `sessoes/A1/sensib_a1_1.py`. Saída: `sessoes/A1/mapa_smo.json`.
- **Resultado (solo argiloso):** [CÁLCULO]
  - De setembro a janeiro, todas as culturas colhem bem em 8 a 10 de cada 10 anos; a água quase nunca derruba a chance abaixo de 8 em 10.
  - O que desenha o mapa é a geada: milho safra plantado em 1–10/ago colhe bem em 6 de 10, e em 21–31/ago em 8 de 10; milho safrinha cai de 10 (até 20/fev) para 8 (21–28/fev), 6 (1–10/mar) e 3 (21–31/mar); sorgo cai de 10 (até 10/fev) para 6 (21–28/fev).
  - Solo médio (sensibilidade): a chance do milho safra em out–nov cai para 6–7 em 10.
  - Geada no POWER: 5,2 dias por ano com T2M_MIN ≤ 2 °C; primeira geada mediana em 25/jun, última em 7/ago (P90: 6/set).
- **Gráfico:** `sessoes/A1/a1_1_mapa.svg`. Mostra a chance de colher bem por cultura e decêndio, com a faixa indicada pelo ZARC embaixo: o mapa é, na prática, o calendário da geada.

## 3. Validação
- **(a) ZARC 2026/27, São Miguel do Oeste (4217204), sequeiro, ciclo II/I, solo AD5 (argiloso) e tipo 3 (sorgo):** acerto de **102 de 108 decêndios (94%)** somando milho 1ª safra, feijão (1ª + 2ª safra) e sorgo granífero (1ª + 2ª safra). Kappa: milho 0,89; feijão 0,78; sorgo 1,00. Diferenças: o ZARC aceita milho em 1–20/ago com risco de 40% (nós não, por geada); nós aceitamos feijão até 10/mar e em 21–31/ago, o ZARC não (o T2M_MIN do POWER é a média de uma célula de ~50 km e parece subestimar a geada local). Solo médio (AD3): 86%. Aveia (grão) não é comparável com a pastagem: acerto de 6/36 (o ZARC só indica a aveia-grão de 11/mai a 30/jun). [CÁLCULO, DADO ZARC]
- **Contra a linha de base ingênua** ("plante de setembro a janeiro", sem modelo nenhum): também acerta **101 de 108 (94%)** no argiloso e 98/108 (91%) no médio. **O modelo não supera o calendário ingênuo na concordância com o ZARC.** [CÁLCULO]
- **(b) IBGE PAM, tabela 1612, milho em grão, São Miguel do Oeste, 1985–2025** (anomalia sobre a mediana móvel de 7 anos): Spearman **0,36** (meta 0,5; linha de base média dos anos = 0). Acertou **3 dos 5 piores anos** (2012, 2022, 2005; meta 3). Errou 1991 (IBGE 0,41; modelo 0,80) e apontou 1986 e 2009 como ruins, quando o IBGE não registrou quebra. Os dados do PAM antes de 2000 parecem arredondados (3000, 3600). Sensibilidade pós-teste: 2000–2025 dá 0,32; outros decêndios de plantio dão 0,25 a 0,40. [DADO IBGE, CÁLCULO]
- **(c) Muda a decisão:** milho safra no habitual (21–30/set) dá 8 em 10, contra 9 a 10 no melhor decêndio (+1 a +2); feijão de 8 (11–20/set) para 9 a 10 (+1 a +2). Atingido no papel, mas 1 em 10 equivale a 4 safras em 41, dentro do ruído do modelo. Milho safrinha, sorgo e pastagem: 0.
- **Conferência de contexto:** a Epagri/Cepa estimou em jan/2022 perda média de 43% no milho de SC, com o Oeste como região mais atingida; a quebra pegou todos os plantios de set–nov no modelo, o que concorda.
- **O critério de sucesso foi atingido?** **Em parte.** (a) sim (94% ≥ 70%), mas empata com o calendário ingênuo; (b) **não** (0,36 < 0,5), embora os 3 de 5 piores anos tenham sido atingidos; (c) sim no limite.

## 4. Régua (1 a 5)
| Critério | Nota | Por quê (uma frase) |
|---|---|---|
| Problema real | 4 | Época de plantio e geada da safrinha são decisões reais no Oeste, e a estiagem de 2021/22 tirou 43% do milho de SC (Epagri/Cepa). |
| Tamanho do impacto | 2 | Dentro da janela usual, o mapa só muda a chance em ±1 de 10 em solo argiloso. |
| Resolve de fato | 2 | Repete o calendário de geada e o ZARC; não muda o que o agricultor faria na maioria dos anos. |
| Validade | 3 | Concorda com o ZARC (94%) e acerta 3 dos 5 piores anos do IBGE, mas não supera o calendário ingênuo e a correlação com o IBGE (0,36) fica abaixo da meta. |
| Muda a decisão | 2 | Só a data-limite da safrinha (≈ 20/fev) muda algo, e o ZARC já cobre isso. |
| Simples e factível | 4 | Roda só com POWER, em segundos, já pronto em Python. |
| Alinhamento com o desafio | 3 | Usa NASA POWER e risco de geada, como o desafio pede, mas fala de data, não de rotação. |
| Diferencial | 1 | É o que o ZARC já publica por município e decêndio. |
| Cabe no hackathon | 5 | Já está feito e validado. |
| **Total (máx. 45)** | **26** | |

## 5. Veredito
**Descartada** como ideia própria (falhou a meta de validade no tempo e "resolve de fato" ficou em 2). O motor (POWER + FAO-56/33 + geada) **reproduz o ZARC em SC (94%)** e pode ser reaproveitado pelo controle; o mapa em si não traz informação nova para o Extremo Oeste.

## 6. Relação com o controle
Complementa. Serve como **prova de validade do motor** do controle ("nosso modelo, só com dados da NASA, concorda com o ZARC em 94% dos decêndios em SC") e como camada de geada (data-limite da safrinha). Na demo entra como um slide de validação, não como a tela principal. Achado importante para o controle: no Extremo Oeste o risco não está na escolha do decêndio dentro da janela, e sim nos anos de estiagem que pegam a safra inteira (2012, 2022).

## 7. Limites e o que não foi testado
- Grade do POWER de ~50 km: geada e chuva locais (fundo de vale, encosta) não aparecem; o T2M_MIN da célula parece subestimar a geada.
- Parâmetros de cultura são da FAO, não das portarias do ZARC; ciclo em dias fixos (sem graus-dia), então a cultura não fica mais lenta no frio.
- O balanço não modela excesso de chuva, doença, calor na floração, nem o potencial de rendimento por data.
- Pastagem de inverno sem modelo de crescimento por temperatura: o mapa dá 10 em 10 o ano todo, o que não serve para decidir.
- O ZARC não tem milho 2ª safra para São Miguel do Oeste, então a safrinha não foi conferida.
- O PAM é por município e mistura safra e safrinha; os dados antes de 2000 têm baixa qualidade.
- **Códigos IBGE usados:** Ituporanga = **4208500** e São Miguel do Oeste = **4217204**. (A primeira versão do protocolo trazia 4208401, que é Itapiranga; já foi corrigido. Esta sessão nunca usou 4208401.)

## 8. Fontes
- NASA POWER, API diária, comunidade AG (arquivo local `dados/power_sao_miguel_do_oeste.json`).
- ZARC, Tábua de Risco, safra 2026/2027, MAPA (CC-BY): https://dados.agricultura.gov.br/dataset/tabua-de-risco-zoneamento-agricola-de-risco-climatico (recorte em `sessoes/A1/ext/zarc_2627_smo_itu.csv`). Portarias: milho 236/2026, feijão 21/2026, feijão 2ª safra 371/2026, sorgo 288/2026, aveia 384/2026.
- IBGE, PAM, tabela 1612: https://apisidra.ibge.gov.br/values/t/1612/n6/4217204/v/109,112/p/all/c81/2711,2702,2713 (em `sessoes/A1/ext/pam_smo.json`).
- IBGE, localidades: https://servicodados.ibge.gov.br/api/v1/localidades/estados/42/municipios
- Epagri/Cepa sobre a estiagem de 2021/22 (notícias): https://www.noticiasagricolas.com.br/noticia/307520 e https://www.agrolink.com.br/noticias/veja-como-a-seca-esta-afetando-a-producao-agricola-em-sc_442148.html
- FAO-56 (Allen et al., 1998) e FAO-33 (Doorenbos e Kassam, 1979) para Kc, fases e Ky.
