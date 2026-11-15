# A5-3 · Vigor da cebola por satélite antecipa a quebra de produtividade (variação da A5-2)

Sessão: A5 · Trilha: A · Região: Ituporanga · Tentativa 3 de 4 · Data: 2026-11-14

## 1. Ideia (escrita antes do teste, às 19h49 de 14/11/2026, antes de baixar qualquer dado do MODIS)
- **Por que esta variação:** na A5-2 apareceu, com o IBGE PAM, que a área de cebola muda pouco de um ano para o outro. Em SC, 2000–2025, a variação média é de 4,5% ao ano, e só ~10% da variação da produção vem da área; o resto vem da produtividade. Se o objetivo é saber cedo se vai sobrar ou faltar cebola, o satélite deveria medir o **vigor da lavoura**, não a área.
- **Hipótese:** o NDVI do MODIS (MOD13Q1, 250 m, 16 dias), na média de 1º/out a 15/nov e só nos pixels com mais cebola, fica abaixo do normal nos anos de quebra de produtividade da cebola em Ituporanga. Esses pixels são escolhidos pelo mapa de cebola do Sentinel-2 feito na A5-2. Assim dá um aviso 2 a 6 semanas antes do pico da colheita, com série de 2000 a 2025.
- **Problema que ataca (e para quem):** o mesmo da A5-2 (vender ou guardar, negociar), agora pelo lado da produtividade, que é o que move a oferta.
- **Decisão que muda:** num ano marcado como "quebra", não fechar venda antecipada a preço de ano normal; num ano "cheio", vender cedo ou guardar.
- **Critério de sucesso (definido antes):**
  1. Spearman entre a anomalia de NDVI (1º/out–15/nov) e a produtividade da cebola de Ituporanga (IBGE PAM, sem tendência linear), 2000–2025 (n = 26): **ρ ≥ +0,40**.
  2. Os anos no terço mais baixo do NDVI pegam **pelo menos 60%** dos anos de quebra (produtividade ≥ 15% abaixo da tendência), contra 33% do acaso.
  3. Supera o índice de chuva da sessão B4-1 (chuva set–nov do POWER), calculado da mesma forma para a mesma produtividade de Ituporanga: o |ρ| do NDVI é maior.
  - Aprovada se 1 e 2 passarem.
- **Pixels (definidos antes):** células MOD13Q1 de 250 m cuja fração de pixels "cebola" do Sentinel-2 (classificação da A5-2, média das safras disponíveis) seja ≥ 30%. Se houver menos de 10 células assim, usar as 20 células com maior fração.
- **Linha de base:** "todo ano é normal" (prever a produtividade da tendência), o acaso (33%) para o item 2 e o índice de chuva da B4-1 para o item 3.

## 2. Teste
- **Dados oficiais usados:**
  - **MODIS MOD13Q1** (Terra, NDVI de 16 dias, 250 m) pela API da ORNL DAAC: bloco de 129 × 129 células (~30 km), composições de 30/set, 16/out e 1º/nov de 2000 a 2025, banda de NDVI e de confiabilidade do pixel. O bloco cobre 94% do município.
  - **Sentinel-2**: máscara de cebola da A5-2 (safras 2022, 2024 e 2025), usada só para escolher os pixels.
  - **NASA POWER**: chuva set–nov, para a linha de base da B4-1.
- **Método:**
  1. `sessoes/A5/scripts/baixa_modis.sh`.
  2. `scripts/analisa_modis.py`: fração de cebola do Sentinel-2 em cada célula MODIS. Pela regra pré-registrada (fração ≥ 30%) saíram **414 células**, com 43% de cebola em média. Indicador por ano = média da anomalia relativa do NDVI dessas células (só pixels com confiabilidade 0 ou 1).
  3. Spearman contra a produtividade de Ituporanga (IBGE PAM, sem tendência linear) e teste do terço mais baixo.
  4. `scripts/base_chuva_b41.py`: linha de base de chuva.
  5. `scripts/sensibilidade_modis.py`: sensibilidade, **não** pré-registrada.
- **Resultado** [CÁLCULO] (`sessoes/A5/resultados/resultado_modis_vigor.json`):
  - **ρ = −0,00** (p = 0,99; n = 26). No município todo, sem escolher pixels: ρ = −0,06.
  - Quebras (≥ 15% abaixo da tendência): 2008, 2011, 2012, 2015, 2017 e 2023. O terço mais baixo do NDVI pega **2 de 6** (33%, igual ao acaso).
  - **As três piores quebras (2023: −28%; 2015: −23%; 2008: −22%) tiveram NDVI acima do normal** em out–meados de nov. Na data do aviso, a lavoura estava verde e vigorosa. O dano veio depois (chuva na bulbificação e na colheita, doença, perda na cura) ou o NDVI não enxerga o tamanho do bulbo. [INFERÊNCIA, que bate com a B4-1: quebras em primaveras de El Niño]
  - O NDVI tem tendência de alta de +0,75% ao ano, 2000→2025 (mais lavoura nesses pixels, ou mudança de uso do solo). Sensibilidade não pré-registrada: sem tendência, ρ = −0,06 (2000–2025) e +0,26 (2010–2025, p = 0,33). Nada significativo.
  - Linha de base da chuva (B4-1, mesma produtividade de Ituporanga): ρ = −0,25 (p = 0,23), com 3 de 6 quebras.
- **Gráfico:** `sessoes/A5/A5-3_vigor_modis.png`.
  - À esquerda, a anomalia de NDVI contra a produtividade; as quebras em vermelho ficam espalhadas, várias com NDVI alto.
  - À direita, a fração de cebola na grade MODIS e as 414 células usadas.

## 3. Validação
- **Contra a linha de base:**
  - "Todo ano normal" e o acaso: o NDVI pega 2 de 6 quebras, contra 2 de 6 esperadas ao acaso.
  - Índice de chuva da B4-1: |ρ| 0,25 contra 0,00 do NDVI. **O NDVI perde até para a chuva.**
- **Fonte externa:**
  - IBGE PAM (t. 5457, Ituporanga 4208500), produtividade 2000–2025 (de 17 a 35 t/ha).
  - A Epagri/Cepa registrou queda de ~27% na safra 2023/24 de SC (via ficha B4-1), o que bate com a quebra de 2023 no PAM. Só que o NDVI de out–nov de 2023 estava +5% acima do normal.
- **O critério de sucesso foi atingido?** **Não.** Item 1: ρ = 0,00 < 0,40. Item 2: 33% < 60%. Item 3: perde para a chuva.

## 4. Régua (1 a 5)
| Critério | Nota | Por quê (uma frase) |
|---|---|---|
| Problema real | 3 | A quebra de produtividade move a oferta e o preço da cebola (~90% da variação da produção, IBGE). |
| Tamanho do impacto | 2 | Se funcionasse, afetaria uma decisão de venda a cada 4 ou 5 anos. |
| Resolve de fato | 1 | Correlação nula; as piores quebras aparecem com NDVI alto. |
| Validade | 2 | 26 anos com dado oficial e conferência no IBGE, mas o sinal não supera nem o acaso. |
| Muda a decisão | 1 | Um aviso que não acerta não muda venda nenhuma. |
| Simples e factível | 3 | MODIS pela ORNL é simples, mas o servidor falhou em metade dos pedidos e a escolha dos pixels depende do Sentinel-2. |
| Alinhamento com o desafio | 2 | É oferta e mercado, não rotação. |
| Diferencial | 3 | Ninguém faz isso para a cebola de SC, mas não funciona. |
| Cabe no hackathon | 3 | Rodou em ~1 h, contando as falhas do servidor. |
| **Total (máx. 45)** | **20** | |

## 5. Veredito
**Descartada.** O vigor visto pelo MODIS antes da colheita não antecipa a quebra da cebola em Ituporanga: ρ = 0,00, e as três piores quebras tiveram NDVI acima do normal. O risco da cebola em SC está no fim do ciclo (bulbificação e colheita), depois do que o satélite consegue ver a tempo.

## 6. Relação com o controle
**Não entra.** O achado reforça o controle por outro caminho. A quebra da cebola parece decidida pelo clima do fim do ciclo (chuva em nov–dez), então o que pode ajudar é a probabilidade climática (o controle) e as sessões B1-2, B3-2 e B4-1, não o NDVI.

## 7. Limites e o que não foi testado
- A máscara de cebola vem de 2022–2025 e é imperfeita (A5-2). Nos anos 2000, esses pixels podiam ter outro uso, o que explica parte da tendência do NDVI.
- 250 m mistura talhões, estradas e mata: as células têm 43% de cebola em média, então o NDVI mede também o vizinho.
- Não usei o Aqua (MYD13Q1), as composições de 17/nov e dez nem o EVI. Não testei o NDVI depois da colheita (que seria tarde demais para a decisão de venda, mas poderia confirmar a perda).
- A produtividade do IBGE é municipal e arredondada; a produtividade do talhão não existe em série.

## 8. Fontes
- MODIS MOD13Q1 v6.1, ORNL DAAC MODIS Web Service: https://modis.ornl.gov/rst/api/v1/MOD13Q1/subset
- IBGE PAM, tabela 5457, Ituporanga 4208500, 2000–2025: https://apisidra.ibge.gov.br/values/t/5457/n6/4208500/v/214,216,8331,112/p/2000-2025/c782/40107
- Ficha B4-1 (índice de chuva e quebra de 2023), `fichas/B4-1-quebra-cebola-sinal-preco.md`.
- NASA POWER, `dados/power_ituporanga.json`.
