# A2-2 · A umidade do solo em novembro prevê a seca de dezembro e janeiro?

Sessão: A2 · Trilha: A · Região: São Miguel do Oeste (Ituporanga como checagem) · Tentativa 2 de 4 · Data: 2026-11-14

## 1. Ideia (escrita antes do teste)
Critérios gravados antes de rodar dados em `sessoes/A2/CRITERIOS_ANTES_DO_TESTE.md`.
- **Hipótese:** um novembro com solo seco (GWETROOT no tercil inferior) indica um dezembro–janeiro seco. Isso daria uma probabilidade condicional ("em anos que começaram assim, deu seca em X de 10"), melhor que a média histórica.
- **Problema que ataca (e para quem):** o produtor de leite e milho do Extremo Oeste, que em novembro ainda decide o milho tardio e a silagem, a compra de ração e o seguro.
- **Decisão que muda:** em ano de alerta, reservar comida para o rebanho, não plantar milho tardio ou trocar por cultura mais curta.
- **Critério de sucesso (definido antes):** para o alvo agrícola (GWETROOT dez–jan no tercil inferior) **e** para o alvo meteorológico (P−ET0 dez–jan no tercil inferior), separadamente: (1) acerto do alerta ≥ 0,50 (base 0,33); (2) detecção ≥ 50% dos anos secos; (3) BSS LOO da logística > 0,05. Só aprova se passar no alvo agrícola **e** o milho simulado também mostrar ganho, para não ser só persistência do modelo MERRA-2.
- **Linha de base:** média de todos os anos (1 em 3).

## 2. Teste
- **Dados oficiais usados:** NASA POWER diário, ponto de SMO (-26,725; -53,518), 1981–2025: `GWETROOT`, `GWETTOP` e `GWETPROF` (umidade relativa 0–1, MERRA-2, ~50 km), `PRECTOTCORR` e as variáveis da ET0. **SMAP não foi testado:** pede login Earthdata, e só teria cerca de 10 safras (desde 2015).
- **Método:** preditor = média de GWETROOT de 1 a 30/nov (variantes: 1–15/nov, GWETTOP, GWETPROF e chuva de novembro). Alerta = preditor no tercil inferior. Pontuação: acerto, detecção, Fisher, Brier LOO da logística e de uma previsão por tercil do preditor. Script: `sessoes/A2/a2_2_umidade.py`. Saída: `sessoes/A2/resultados/a2_2_smo.json`.
- **Resultado (SMO, preditor = GWETROOT de novembro)** [CÁLCULO]:

| Alvo de dez–jan | Acerto do alerta | Detecção | Fisher p | BSS (LOO) | Spearman ρ |
|---|---|---|---|---|---|
| GWETROOT dez–jan (agrícola, do próprio modelo) | 9/15 = 60% | 60% | 0,012 | **+0,35** | +0,76 |
| Balanço P−ET0 dez–jan (meteorológico) | 4/14 = 29% | 29% | 0,81 | −0,02 | +0,15 |
| Chuva dez–jan | 27% | 27% | 0,86 | −0,03 | +0,11 |
| Milho simulado (perda, base 10%) | 2/14 = 14% | 2 de 4 | 0,42 | −0,03 | +0,28 |

  - GWETTOP de novembro: o mesmo quadro (agrícola: acerto 67%, BSS +0,38; meteorológico: 29%, BSS −0,03).
  - Ituporanga: persistência ainda maior no alvo agrícola (acerto 87%, BSS +0,67) e nada no meteorológico (BSS −0,05). Lá o GWETROOT de dez–jan quase não acompanha o balanço P−ET0 do mesmo período (ρ = 0,24).
- **Gráfico:** `sessoes/A2/a2_2_umidade_novembro.svg`. À esquerda, o solo de novembro "prevê" o solo do modelo em dez–jan (ρ = +0,76). À direita, não prevê o balanço de chuva (ρ = +0,15), e as safras com quebra no IBGE (laranja) se espalham em toda a faixa de novembro.

## 3. Validação
- **Contra a linha de base:** só no alvo do próprio modelo há ganho (60% contra 33%). Nos três alvos independentes do GWET (P−ET0, chuva e milho simulado), o alerta acerta no máximo como a média, e o BSS é negativo.
- **Fonte externa:** IBGE PAM, tabela 1612, milho da microrregião de SMO, quebra < 80% do normal (6 colheitas: 1991, 2002, 2005, 2012, 2021 e 2022) [DADO + CÁLCULO]. O alerta de novembro pegou 2 de 6 quebras com 12 alertas (rendimento médio de 0,98 com alerta e 0,97 sem; ρ = 0,05). Para comparar: o GWETROOT **de dez–jan** (medido na hora, não previsto) pega 4 de 6 (rendimento médio de 0,89 com alerta e 1,02 sem). [Link](https://apisidra.ibge.gov.br/values/t/1612/n9/42001/v/112/p/all/c81/2711).
- **O critério de sucesso foi atingido?** **Em parte, e pela regra registrada antes isso conta como "não".** Passa no alvo agrícola, mas falha no meteorológico, no milho simulado e no IBGE. O ganho é a memória do próprio solo do modelo, não uma previsão da seca.

## 4. Régua (1 a 5)
| Critério | Nota | Por quê (uma frase) |
|---|---|---|
| Problema real | 4 | As secas de verão derrubam o milho e o pasto no Oeste de SC (quebras de 2005, 2012 e 2022 no IBGE). |
| Tamanho do impacto | 2 | O ganho só aparece no "solo do modelo"; nas perdas reais (IBGE) o alerta de novembro não separa os anos. |
| Resolve de fato | 2 | Dizer em dezembro que "o solo está seco" o agricultor já sente no campo; o alerta não antecipa a chuva nem a quebra. |
| Validade | 2 | Supera a média só no alvo que herda o próprio preditor (BSS +0,35); nos alvos independentes o BSS é < 0 e o IBGE não bate. |
| Muda a decisão | 2 | O milho simulado com perda é raro (4 de 41) e o alerta acerta 2 desses 4 anos, com 12 alarmes falsos. |
| Simples e factível | 4 | É um número do POWER, sem login e já baixado. |
| Alinhamento com o desafio | 4 | Usa só recurso oficial (POWER/MERRA-2). |
| Diferencial | 2 | Persistência de umidade do solo é o que qualquer modelo de balanço já carrega. |
| Cabe no hackathon | 4 | Rodou em pouco tempo. |
| **Total (máx. 45)** | **26** | |

## 5. Veredito
**Descartada como previsão.** A umidade de novembro não prevê a chuva nem a quebra de dez–jan. O uso honesto do GWETROOT é como **estado de agora**, durante a safra: medido em dez–jan, ele pega 4 de 6 quebras do IBGE. Isso já faz parte do controle (monitoramento) e não é previsão.

## 6. Relação com o controle
Complementa o controle no monitoramento durante a safra ("o solo do seu lugar está no pior terço dos últimos 40 anos"), e não como previsão de 1 a 2 meses. Na demo, pode aparecer como um "termômetro do solo" ao lado da probabilidade histórica, sem prometer o que vem.

## 7. Limites e o que não foi testado
- O GWETROOT do POWER é saída do modelo MERRA-2 (~50 km), não medição. Ele varia pouco (0,62 a 0,86 em dez–jan) e sua persistência pode ser maior que a do solo real.
- SMAP (medição por satélite, desde 2015) não testado: pede login Earthdata. GLDAS também não.
- O milho simulado começa com o solo cheio em 1/ago e não usa o GWET. Por isso é um alvo independente, mas grosseiro.
- Só 6 quebras do IBGE em 34 safras com dado. A conferência tem pouco poder.
- A anomalia do IBGE usa a mediana móvel de 7 anos para tirar a tendência tecnológica. Outro método mudaria os anos de quebra nas bordas.

## 8. Fontes
- NASA POWER diário, comunidade AG: `loop-validacao/dados/power_sao_miguel_do_oeste.json` e `power_ituporanga.json` [DADO].
- IBGE SIDRA, PAM, tabela 1612, milho em grão, rendimento médio, microrregião 42001: https://apisidra.ibge.gov.br/values/t/1612/n9/42001/v/112/p/all/c81/2711 [DADO externo, conferência].
- Método do balanço e ET0: `prototipo/modelo/risco.py` (FAO-56 e FAO-33).
