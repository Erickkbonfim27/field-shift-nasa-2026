# B5-1 · Laudo de perda com dado de satélite para o Proagro e o seguro

Sessão: B5 · Trilha: B · Região: São Miguel do Oeste (milho); Ituporanga (cebola) como checagem · Tentativa 1 de 4 · Data: 2026-11-14

## 1. Ideia (escrita antes do teste)
- **Hipótese:** um indicador montado só com dado da NASA (balanço hídrico do milho com o NASA POWER e NDVI do MODIS) separa os anos de perda dos anos normais no município, a ponto de servir de pré-laudo para o pedido de cobertura do Proagro ou do seguro rural.
- **Problema que ataca (e para quem):** o agricultor familiar que perde a safra depende da vistoria do perito e de provar a perda; o agente do banco e a seguradora precisam decidir rápido e com menos briga. Um pré-laudo com a série de 40 anos ("seu ano está entre os 3 piores desde 1984") dá prova objetiva.
- **Decisão que muda:** comunicar a perda e pedir a cobertura logo (antes de colher ou destruir a lavoura), em vez de esperar; para o banco, priorizar vistorias.
- **Critério de sucesso (definido antes):**
  - Ano de perda = rendimento do milho no IBGE/PAM abaixo de 70% da tendência linear de 1990–2024 (queda de 30% ou mais).
  - O indicador acerta pelo menos **75% dos anos de perda** com **precisão de 60% ou mais**, e supera a linha de base em pelo menos 1 acerto a mais ou 1 alarme falso a menos.
  - Conferência externa: os anos que ele marca batem com os anos de indenização alta do seguro rural ou do Proagro no município ou no estado.
- **Linha de base:** regra ingênua "chuva de outubro a fevereiro abaixo do 1º quartil" (o que qualquer um calcula com um pluviômetro) e o acaso (marcar ao acaso a mesma quantidade de anos).

## 2. Teste
- **Dados oficiais usados:**
  - NASA POWER diário (comunidade AG), ponto -26,725; -53,518 (~50 km): chuva, temperatura, umidade, vento e radiação (para a ET0 FAO-56) e `GWETROOT`, safras 1985–2025. [DADO]
  - MODIS MOD13Q1 (NDVI, 250 m, 16 dias) pelo ORNL DAAC, 9 × 9 km em volta do ponto, composições de dezembro a fevereiro, safras 2001–2025. [DADO]
- **Método:**
  1. Balanço hídrico diário do milho de verão (FAO-56 e FAO-33, CAD de 125 mm), com 4 datas de plantio (1º/set, 15/set, 1º/out, 15/out) para representar o município. Indicador = rendimento relativo simulado médio (y). Laudo marca a safra se y < 0,70 (o mesmo corte de 30% de perda). Script: `sessoes/B5/modelo_milho.py`; avaliação: `sessoes/B5/avaliar.py`.
  2. NDVI de janeiro nos pixels não urbanos que mais variam entre os anos; marca se ficar no 1º quartil. Script: `sessoes/B5/ndvi_smo.py`.
  3. Comparação com o IBGE/PAM (critério) e com o Proagro por município (conferência). Script: `sessoes/B5/validar_proagro.py`.
- **Resultado (contra o IBGE/PAM, 1990–2024):** [CÁLCULO]
  - Anos de perda: 1991, 2002, 2012, 2021 e 2022 (5 de 35).
  - **Laudo (balanço hídrico):** marca 8 safras, **acerta 3 de 5 (60%)**, 5 alarmes falsos, **precisão de 38%**. Errou 1991 e 2002; alarmes falsos em 1996, 2005, 2006, 2009 e 2023.
  - **Base (chuva out–fev no 1º quartil):** marca 8, acerta **4 de 5 (80%)**, precisão de **50%**.
  - Na ordenação dos anos, o laudo segue melhor o rendimento do que a chuva (Spearman 0,41 contra 0,12; na microrregião, 0,53 contra 0,29).
  - Sensibilidade: com solo argiloso (CAD de 175 mm) o laudo marca só 4 safras (2 acertos, precisão de 50%); na microrregião e na mesorregião do IBGE o laudo não supera a base.
  - **NDVI do MODIS (safras 2001–2025, 520 pixels de lavoura e pasto em 9 × 9 km):** o NDVI de janeiro fica perto de 0,71 em quase todo ano e só cai forte em seca grande: 2022 (−0,14), 2012 (−0,08) e 2002 (−0,06). Contra o IBGE/PAM em 2001–2024 (perdas: 2002, 2012, 2021, 2022), marca 6 safras, **acerta 3 de 4**, precisão de **50%** (falsos: 2008, 2009, 2020; perdeu 2021). Na mesma janela, a chuva acerta 4 de 4 com 50%, e o balanço hídrico, 3 de 4 com 43%. Juntando balanço **e** NDVI: 2 de 4 com 67%. Script: `sessoes/B5/ndvi_smo.py`; saída: `ndvi_smo.csv` e `resultado_ndvi_smo.txt`.
- **Gráfico:** `sessoes/B5/grafico_b5_1_laudo.svg`. Barras = rendimento do IBGE/PAM em % da tendência; marcas = anos que cada regra apontou.

## 3. Validação
- **Contra a linha de base (IBGE/PAM):** laudo 3 de 5 e precisão de 38%, contra chuva 4 de 5 e 50%. **O laudo perde da base no corte combinado.** Acaso: precisão esperada de 14%. [CÁLCULO]
- **Fonte externa (Proagro, BCB, por município):** coberturas deferidas ÷ adesões no milho de São Miguel do Oeste, safras 2014–2025 (contrato emitido no ano Y = safra colhida em Y+1). [DADO] (arquivo `sessoes/B5/externo/proagro_mdpro_SMO_Ituporanga_por_ano_produto.csv`; fonte na seção 8)
  - Indenização alta (10% ou mais dos contratos): 2021 (50%), 2022 (48%), 2023 (15%), 2024 (29%). Em 2021 e 2022 o evento registrado foi **seca** (32 e 51 coberturas deferidas por seca, contra 1 por chuva excessiva).
  - **Laudo:** acerta **3 de 4 com precisão de 75%** (2021, 2022, 2023; alarme falso em 2025, cujo Proagro ainda pode estar incompleto). **Base da chuva:** 2 de 4, precisão de 40%. O laudo **bate** com o Proagro.
  - O laudo não vê 2024 (safra 2023/24, El Niño, perdas mais por excesso de chuva): o balanço hídrico só enxerga falta de água.
  - O NDVI sozinho acerta 1 de 4 contra o Proagro (2022); balanço **e** NDVI juntos, 1 de 4 sem falso.
  - O corte de 10% foi escolhido depois de ver a tabela do Proagro, e são só 12 safras. [INFERÊNCIA]
- **Fonte externa (norma do Proagro):** o Banco Central **já usa sensoriamento remoto** no Proagro. A Res. CMN 4.796/2020 aceita imagem de satélite na comprovação remota de perdas; a Res. CMN 4.902/2021 obriga o beneficiário a informar as coordenadas do perímetro da lavoura; a Res. CMN 5.127/2024 manda o agente verificar por sensoriamento remoto se a lavoura emergiu e se o ZARC foi respeitado. [DADO] (https://www.bcb.gov.br/api/conteudo/app/normativos/exibenormativo?p1=Resolução%20CMN&p2=4902 e p2=5127)
- **Escala do problema:** o Proagro deferiu R$ 483 mi em SC em 2021 (12.282 coberturas) e R$ 830 mi em 2023; em São Miguel do Oeste, 51 das 52 coberturas deferidas de 2021 foram por seca. [DADO, MDPRO/BCB]
- **O critério de sucesso foi atingido?** **Não** no critério principal (IBGE/PAM): o balanço hídrico deu 60% de acerto e 38% de precisão, e o NDVI deu 3 de 4 com 50%; nenhum dos dois supera a regra da chuva. A conferência com o Proagro foi favorável ao balanço hídrico (3 de 4, 75%), mas com corte escolhido depois e 12 safras.

## 4. Régua (1 a 5)
| Critério | Nota | Por quê (uma frase) |
|---|---|---|
| Problema real | 4 | O Proagro deferiu R$ 483 mi em SC em 2021, e provar a perda é a etapa que trava o pagamento. |
| Tamanho do impacto | 4 | O dinheiro do Proagro e do seguro é a maior proteção que a família já tem contra a estiagem. |
| Resolve de fato | 2 | O BCB já exige coordenadas da lavoura e usa satélite na verificação; um indicador municipal de ~50 km não chega à gleba e não muda o que o agricultor faz. |
| Validade | 2 | Com dado oficial, nem o balanço hídrico nem o NDVI superaram a regra da chuva contra o IBGE; o bom resultado contra o Proagro tem corte escolhido depois e 12 safras. |
| Muda a decisão | 2 | Ele comunica a perda de qualquer jeito num ano como 2022; o laudo só adiantaria a conversa com o banco. |
| Simples e factível | 3 | O balanço hídrico é simples; o NDVI do MODIS demora (cerca de 1 minuto por safra na API do ORNL) e o laudo de verdade precisaria do polígono da gleba. |
| Alinhamento com o desafio | 2 | É comprovação de perda depois do fato, não escolha de rotação. |
| Diferencial | 2 | O BCB já usa sensoriamento remoto no Proagro desde 2020–2024, e há empresas que vendem esse laudo. |
| Cabe no hackathon | 3 | Dá para mostrar a série do município, mas não um laudo por gleba. |
| **Total (máx. 45)** | **24** | |

## 5. Veredito
**Descartada.** O sinal da NASA de grade grossa não separa os anos de perda melhor que a chuva total, e o Banco Central já faz a verificação por satélite na gleba. O único resultado bom (3 de 4 contra o Proagro) é pequeno e foi medido com corte escolhido depois; vale anotar, não vale construir o produto.

## 6. Relação com o controle
Não compete; dá dois recados ao controle.
1. **O crédito e o seguro seguem o ZARC e já usam satélite.** A ferramenta do controle deve conversar com isso: mostrar se a estratégia escolhida fica dentro da janela do ZARC (para não perder o Proagro), em vez de tentar ser laudo.
2. **O NDVI de janeiro do MODIS só enxerga seca grande** (2002, 2012, 2022). Serve para a demo como "foto da perda" de um ano marcante, não como validação ano a ano.

## 7. Limites e o que não foi testado
- Grade do POWER de ~50 km; a seca de um talhão pode não aparecer no ponto.
- O IBGE/PAM municipal é estimado (valores repetidos, como 3.000 kg/ha de 1992 a 1994) e mistura milho grão de agricultores muito diferentes; é um gabarito ruidoso para um laudo por lavoura.
- O Proagro tem só 12 safras por município, e o número de contratos de milho caiu de 274 para 41; o corte de "indenização alta" foi escolhido depois de ver os números.
- O laudo real é por gleba: precisaria de NDVI do Sentinel-2 (10 m) no polígono do contrato, que não foi testado aqui.
- Só falta de água: excesso de chuva, granizo e geada ficam de fora.
- Não testado com agente de crédito, perito ou seguradora: se aceitariam um pré-laudo e se isso encurta o prazo de pagamento.

## 8. Fontes
- NASA POWER, API diária, comunidade AG (arquivo `dados/power_sao_miguel_do_oeste.json`).
- MODIS MOD13Q1 v6.1, ORNL DAAC: https://modis.ornl.gov/rst/api/v1/MOD13Q1/subset
- IBGE, PAM, tabela 5457, São Miguel do Oeste 4217204, milho 40122: https://apisidra.ibge.gov.br/values/t/5457/n6/4217204/v/112,216,8331/p/1990-2024/c782/40122
- Proagro, Matriz de Dados do Proagro (BCB), por município, produto e evento: https://www.bcb.gov.br/estabilidadefinanceira/proagro (recortes em `sessoes/B5/externo/`).
- Relatório Circunstanciado do Proagro 2019–2022 (BCB): https://www.bcb.gov.br/content/estabilidadefinanceira/proagro_docs/relatorios_proagro/Relat%C3%B3rio%20Circunstanciado%202019-2022.pdf
- Resoluções CMN 4.796/2020, 4.902/2021 e 5.127/2024 (busca de normativos do BCB).
- Seguro rural, SISSER/PSR (MAPA): https://dados.agricultura.gov.br/dataset/sisser3. Em São Miguel do Oeste quase não há apólice de milho (11 em 2021), então o Proagro é o gabarito certo.
- IBGE, PAM, microrregião 42001 e mesorregião 4201 (checagem de escala): https://apisidra.ibge.gov.br/values/t/5457/n9/42001/n8/4201/v/112/p/1990-2024/c782/40122
