# V4 · Motor composto (o controle reformulado)

Frente: V4 · Data: 14/11/2026 · Região: Santa Catarina (São Miguel do Oeste e Ituporanga, mais 4 microrregiões vizinhas).

## Resposta curta
- **Como explicador do rendimento ano a ano, o motor composto não passa.** No milho ele não supera nem a chuva bruta nem a água sozinha. Na cebola ele supera as duas na microrregião, mas não no município. [CÁLCULO, `v4_motor.py`]
- **O "x em 10 anos" composto passa (validade 3) só para três decisões:**
  1. **Data do milho safra:** tirar agosto da janela. A água sozinha manda plantar em agosto, e o motor não. O ZARC confirma.
  2. **Alerta de ano extremo:** o flag sozinho bate a climatologia nos 4 gabaritos principais.
  3. **"x em 10" da cebola:** o motor diz 1,1 a 1,2 falhas em 10 anos. A PAM mostra 1,1 a 1,7. A água sozinha diz de 0 a 0,2.
- **Não passa para:**
  - graduar os anos comuns;
  - escolher entre datas de setembro a dezembro (diferença menor que 1 em 10);
  - escolher a data de transplante da cebola (o motor contradiz o ZARC).

## 1. Critério definido antes
Escrito em `00_criterios_antes.md` antes de rodar o teste. Resumo:
- **Gabaritos (só conferência):**
  - **Milho:** IBGE PAM do município de SMO (4217204, safras 1985–2025) e da microrregião 42001 (1990–2025). Fora da região: Chapecó (42002) e Concórdia (42005).
  - **Cebola:** município de Ituporanga (4208500, 1984–2025) e microrregião 42014. Fora da região: Rio do Sul (42011). Tabuleiro (42017) está na mesma célula do POWER que Ituporanga.
- **Linhas de base:** (a) climatologia; (b) chuva bruta (milho de dez a fev, cebola de set a nov); (c) balanço hídrico sozinho (o controle B1-0).
- **Motor:**
  - **d1, fixo a priori:** água × geada × excesso, sem nenhum ajuste.
  - **d2, ridge (λ = 3 fixo):** 6 variáveis: ISNA vegetativo, ISNA floração ou bulbificação, ISNA maturação, dias de geada, excedente na fase sensível e flag de ano extremo.
- **Validação:** leave-one-out, bloco temporal (até 2004 contra 2005 em diante) e transferência para outra microrregião sem reajuste.
- **Validade 3** exige três coisas fora da amostra:
  - ρ mínimo: milho ≥ 0,40 no município e ≥ 0,35 na microrregião; cebola ≥ 0,30 e ≥ 0,25.
  - Δρ ≥ 0,10 contra a chuva e contra a água.
  - SS > 0 contra a climatologia (milho ≥ 0,10; cebola ≥ 0,05).

## 2. Método
- **Dados da solução:**
  - NASA POWER diário, comunidade AG: `PRECTOTCORR`, `T2M`, `T2M_MAX`, `T2M_MIN`, `RH2M`, `WS2M` e `ALLSKY_SFC_SW_DWN`, de 1984 a 2025.
  - Seis pontos: os 2 do protocolo e os 4 baixados pela B3 (`loop-validacao/sessoes/B3/power_extra/`).
- **Água:**
  - ET0 por Penman-Monteith FAO-56.
  - Balde e Ky por fase (FAO-33), com os parâmetros da B1-0: milho em 20/set em solo argiloso, cebola em 15/jul em solo médio.
- **Geada:** dias com `T2M_MIN` < 2 °C nas fases I a III do milho. Na cebola, < 0 °C nas fases I e II.
- **Excesso:**
  - Milho: excedente hídrico na maturação.
  - Cebola: excedente de 1/set a 30/nov, com a configuração da B3-2.
- **Flag de ano extremo** (regras fixas da B3-3):
  - milho: ISNA de 20/set a 10/jan < 0,75;
  - cebola: excedente de set a nov ≥ 360 mm.
- **Tendência:** rendimento dividido pela mediana móvel centrada de 9 anos, como na B1-0. Sensibilidade com a regra da B3.
- **Script e saída:** `v4_motor.py` → `v4_resultado.json`. Gráficos: `graficos.py`.

## 3. Resultado

### 3.1 Quem explica o rendimento (Spearman ρ) [CÁLCULO]
Chuva, água e d1 não têm nenhum parâmetro ajustado aos dados. O d2 foi avaliado em leave-one-out. Nas linhas "fora", o d2 foi treinado na microrregião de origem.

| Gabarito | n | (b) chuva | (c) só água | (d1) motor fixo | (d2) motor ajustado | SS d2 | 8 piores (d2) |
|---|---|---|---|---|---|---|---|
| Milho SMO, município | 41 | 0,23 | **0,28** | 0,20 | 0,08 | −0,08 | 2 (acaso 1,6) |
| Milho SMO, microrregião | 36 | 0,38 | **0,41** | 0,36 | 0,11 | −0,08 | 3 |
| Milho Chapecó (fora) | 36 | 0,22 | 0,40 | **0,41** | 0,31 | — | — |
| Milho Concórdia (fora) | 36 | 0,36 | **0,43** | 0,26 | 0,40 | — | — |
| Cebola Itu, município | 42 | −0,08 | 0,13 | 0,13 | **0,14** | +0,05 | 3 (acaso 1,5) |
| Cebola Itu, microrregião | 36 | −0,06 | 0,12 | 0,23 | **0,27** | +0,18 | 3 |
| Cebola Rio do Sul (fora) | 36 | −0,08 | 0,01 | **0,45** | 0,40 | — | — |
| Cebola Tabuleiro (mesma célula) | 36 | −0,20 | −0,06 | 0,20 | **0,31** | — | — |

Gráfico: `fig1_rho_por_preditor.svg`.

**Leitura:**
- **Milho:** a água sozinha é o melhor preditor em 3 de 4 gabaritos. Somar módulos não ajuda. Motivo: no plantio de 20/set a geada é **zero em todos os 41 anos** em SMO [CÁLCULO], e o excesso na maturação não tem sinal.
- **Cebola:** os módulos de excesso e de flag fazem o sinal aparecer onde a água sozinha não vê nada. O motor fica acima da água sozinha em 4 de 4 gabaritos com d1 ou d2. A diferença vai de +0,01 (município) a +0,44 (Rio do Sul).
- **Achado lateral:** na escala de microrregião, a água sozinha chega a ρ de 0,40 a 0,43 no milho (SMO, Chapecó e Concórdia), sem nenhum ajuste. No município é 0,28. O gabarito municipal é mais ruidoso.

### 3.2 Ganho sobre a climatologia e ablação (SS, leave-one-out) [CÁLCULO]
| Gabarito | só água | só flag | água + flag | motor completo |
|---|---|---|---|---|
| Milho SMO, município | −0,09 | **+0,08** | −0,06 | −0,08 |
| Milho SMO, microrregião | +0,01 | **+0,09** | −0,05 | −0,08 |
| Cebola Itu, município | −0,22 | **+0,13** | −0,02 | +0,05 |
| Cebola Itu, microrregião | −0,02 | **+0,22** | +0,22 | +0,18 |

Gráfico: `fig2_ganho_sobre_climatologia.svg`.

**Leitura:**
- O flag de ano extremo sozinho é o único módulo que bate a climatologia nos 4 gabaritos.
- Ajustar 6 pesos com 36 a 42 anos de PAM piora a previsão (sobreajuste).
- Ressalva: os limiares do flag foram escolhidos na B3 com os gabaritos de microrregião (42001 e 42014). Por isso, o SS do flag nesses dois gabaritos é otimista. O teste fora da amostra do flag é o da B3-3 (aprovado).

### 3.3 Critérios
| Critério | Resultado | Passou? |
|---|---|---|
| M1 ρ(d2) ≥ 0,40 e ≥ 0,35 | 0,08 e 0,11 | Não |
| M2 Δρ ≥ 0,10 contra chuva e água | município: −0,00 e −0,21; microrregião: −0,19 e −0,30 | Não |
| M3 SS ≥ 0,10 | −0,08 | Não |
| M4 ≥ 4 de 8 piores | 2 de 8 | Não |
| M5 fora da região: ρ ≥ 0,30 e ≥ água | 0,36 em média, contra 0,42 da água | Não |
| M6 ρ ≥ 0,25 nos dois blocos | 0,31 e −0,27 | Não |
| C1 ρ(d2) ≥ 0,30 e ≥ 0,25 | 0,14 e 0,27 | Não (só a microrregião) |
| C2 Δρ ≥ 0,10 contra chuva e água | município: +0,20 e **+0,01**; microrregião: +0,35 e +0,15 | Não (falha contra a água no município) |
| C3 SS ≥ 0,05 | +0,054 | Sim, por pouco |
| C4 ≥ 3 de 8 piores | 3 de 8 | Sim |
| C5 Rio do Sul ρ ≥ 0,20 | 0,40 | Sim |
| C6 ρ ≥ 0,20 nos dois blocos | −0,02 e 0,07 | Não |
| S1 d1 ≥ água + 0,05 | milho 0,20 contra 0,28; cebola 0,13 contra 0,13 | Não |
| D1 data do milho bate com o ZARC | ver 3.5 | **Sim** |
| D2 transplante da cebola bate com o ZARC | ver 3.5 | Não |

**Bootstrap pareado (2.000 reamostras), fração com Δρ > 0** [CÁLCULO]:
- Milho, município: d2 contra a água = 3%. O motor ajustado é pior.
- Cebola, microrregião: d2 contra a chuva = 96%; contra a água = 72%.
- Cebola, município: contra a chuva = 83%; contra a água = 53%.

**Sensibilidade** [CÁLCULO, `v4_resultado.json`]:
- Com a regra de tendência da B3, as conclusões não mudam (milho: d2 entre −0,06 e −0,05; cebola: 0,20 e 0,29).
- Com o transplante da cebola em 1/ago, o d1 do município sobe para 0,30 e o d2 para 0,24, com SS de 0,09.

### 3.4 O "x em 10" do motor contra a PAM (d1, plantio padrão) [CÁLCULO]
Falha = rendimento do motor < 0,6, ou flag, ou geada no ciclo. Ano ruim na PAM = rendimento ≤ 0,85 da mediana.

| Gabarito | Falha do motor (em 10) | Falha da água sozinha (em 10) | Ano ruim na PAM (em 10) | Precisão do motor | Quebras vistas |
|---|---|---|---|---|---|
| Milho SMO, município | 1,2 | 1,0 | 2,0 | 40% | 2 de 8 (2012, 2022) |
| Milho SMO, microrregião | 1,1 | 0,8 | 1,9 | 50% | 2 de 7 |
| Milho Chapecó | 1,1 | 0,6 | 1,9 | 75% | 3 de 7 |
| Milho Concórdia | 0,6 | 0,6 | 1,7 | 50% | 1 de 6 |
| Cebola Itu, município | 1,2 | **0,2** | 1,7 | 60% | 3 de 7 (2008, 2015, 2023) |
| Cebola Itu, microrregião | 1,1 | **0,0** | 1,1 | 75% | 3 de 4 |
| Cebola Rio do Sul | 1,1 | **0,0** | 1,4 | 50% | 2 de 5 |
| Cebola Tabuleiro | 1,1 | **0,0** | 1,1 | 25% | 1 de 4 |

**Leitura:**
- **Milho:** o motor vê só cerca de 1 a cada 3 quebras. Não vê 1991, 2002, 2005 nem 2021, que o POWER não registra como anos secos ou de geada.
- **Cebola:** o "x em 10" do motor fica perto da frequência real. A água sozinha diz que a cebola quase nunca falha, o que é falso.

### 3.5 Decisões ("x em 10" por data de plantio) [CÁLCULO + conferência ZARC]
**Milho em SMO** (`fig3_decisao_data_milho.svg`):

| Plantio | 1/ago | 11/ago | 21/ago | 1/set | 11/set | 21/set | 1/out a 21/dez |
|---|---|---|---|---|---|---|---|
| Só água (em 10) | 0,2 | 0,2 | 0,2 | 0,7 | 1,0 | 1,2 | 0,7 a 1,2 |
| Motor (em 10) | **6,3** | **4,6** | 3,4 | 2,7 | 1,5 | 1,2 | 0,7 a 1,5 |
| ZARC 2026/27, solos AD4–AD6 | 40% | 40% | 20–30% | 20–30% | 20–30% | 20–30% | 20–30% |

- A água sozinha aponta agosto como a melhor data, e o ZARC dá 40% de risco nesse mês. O motor marca 1/ago e 11/ago com 5,1 e 3,4 falhas em 10 a mais que 21/set. A melhor data do motor (1/nov e 21/dez, 0,7 em 10) cai dentro da faixa do ZARC. **D1 passa.**
- **De 21/set a 21/dez, as datas diferem em menos de 1 em 10.** Ali a data não muda a decisão.

**Cebola em Ituporanga** (`fig4_decisao_transplante_cebola.svg`):
- O motor dá de 1,2 a 2,4 em 10 de jun a 1/ago e de 0,5 a 1,0 de 11/ago a 21/set. A melhor data do motor é 11/set e 21/set (0,5 em 10).
- O ZARC cebola sequeiro não dá risco de 20% em nenhuma linha a partir de 11/set. **D2 não passa.**
- A diferença entre 11/ago e 21/set é de só 0,2 em 10. O motor não tem os riscos de fim de ciclo que o ZARC conta.

## 4. Conferência externa
- **IBGE PAM, tabelas 5457 e 1612:** é o próprio gabarito. Arquivos em `loop-validacao/sessoes/B1/externo/` e `loop-validacao/sessoes/B3/externo/` [DADO].
- **ZARC 2026/27:**
  - Milho 1ª safra, Portaria SPA/MAPA 236/2026, SMO: 40% em 1/ago e 11/ago; 20–30% de 21/ago a 21/dez nos solos AD4–AD6.
  - Cebola: Portaria 4/2026, sequeiro, Ituporanga.
  - Arquivo: `loop-validacao/sessoes/A1/ext/zarc_2627_smo_itu.csv` e `zarc_perene_smo_itu.csv` [DADO]. O `B1/externo/zarc_smo_itu_full.csv` citado na tarefa está vazio (0 bytes); usei o da A1.
  - **Bate na data do milho. Não bate no transplante da cebola.**
- **Epagri** (citada nas fichas B3-1, B3-2 e B3-3): as quebras que o motor vê (milho em 2012 e 2022; cebola em 2008, 2015 e 2023) são as estiagens e os excessos de chuva registrados pela Epagri. **Bate nos extremos.**

## 5. Veredito
**Parcial.**
- **Como "motor que explica o rendimento":** não passa. Validade 2 no milho (supera a média, mas não a água sozinha nem a chuva) e 2 a 3 na cebola (supera a chuva e a água na microrregião e fora da região, mas não no município nem nos blocos temporais).
- **Como "x em 10 por decisão":** passa com validade 3 em três usos:
  1. **Data do milho:** a geada tira agosto da janela, e o ZARC bate.
  2. **Ano extremo:** o flag bate a climatologia em 4 de 4 gabaritos, e a B3-3 já testou fora da amostra.
  3. **Chance de quebra da cebola:** o "x em 10" calibrado dá 1,1 a 1,2 falhas em 10, contra 1,1 a 1,7 na PAM.

### Régua (motor composto como produto, 1 a 5)
| Critério | Nota | Por quê |
|---|---|---|
| Problema real | 4 | As quebras de 2012 e 2022 (milho) e de 2008, 2015 e 2023 (cebola) estão na PAM e na Epagri. |
| Tamanho do impacto | 3 | O motor fala em cerca de 1 a cada 10 anos, mas são os anos de quebra de 25 a 60%. |
| Resolve de fato | 3 | Muda a decisão em agosto (milho) e nos anos extremos; nos anos comuns, não. |
| Validade | 3 nas 3 decisões / 2 no geral | Supera as linhas de base só nos usos restritos; como explicador ano a ano, não. |
| Muda a decisão | 3 | A janela do milho e o alerta, sim; a data entre setembro e dezembro, não. |
| Simples e factível | 4 | O d1 tem 3 fatores fixos e roda em segundos com o POWER. |
| Alinhamento com o desafio | 4 | Probabilidade por estratégia com dados NASA. |
| Diferencial | 3 | O ZARC já faz geada mais água; o flag durante a safra e a cebola calibrada são nossos. |
| Cabe no hackathon | 5 | Pronto. |
| **Total** | **32** | Passa com 3/3/3 só no escopo restrito. |

## 6. Implicações para a solução
1. **Motor modular com pesos fixos a priori (d1), não pesos ajustados.** Com 36 a 42 anos de PAM, ajustar 6 pesos piora (SS de −0,08 no milho). Os módulos devem ser regras físicas simples, cada uma com o seu teste.
2. **A região liga e desliga os módulos.**
   - **SC milho:** a geada define a janela de plantio, e a água só entra como alerta de ano extremo.
   - **SC cebola:** o excesso de chuva e o flag carregam o sinal. A água quase não pesa: sozinha, diz 0 a 0,2 falhas em 10, e a PAM mostra 1,1 a 1,7.
3. **Mudar a frase do "x em 10":** de "chance de colher" para "em quantos anos de 10 houve quebra forte". E dizer o que o motor não vê: no milho de SC ele pega cerca de 1 a cada 3 quebras da PAM.
4. **Não vender ranking de datas onde a diferença é menor que 1 em 10** (milho de setembro a dezembro, cebola de julho a setembro). Nesses casos, dizer "tanto faz para o clima".
5. **Não usar o motor para a data de transplante da cebola** até ter um módulo de fim de ciclo. Hoje ele contradiz o ZARC.
6. **Mostrar o resultado na escala de microrregião.** O sinal é mais forte que no município: água no milho com ρ de 0,40 a 0,43, contra 0,28.
7. **Para o pitch:** "o mesmo motor, com módulos diferentes por região". O exemplo é a fig. 3: a água sozinha manda plantar milho em agosto, e o motor com geada não manda.

## 7. Limites
- **Escala:** o POWER tem grade de ~50 km. A PAM é uma estimativa municipal, com valores repetidos.
- **Amostra pequena:** os extremos são 2 a 4 eventos por cultura.
- **Leave-one-out com sinal fraco:** o ρ fica viesado para baixo. O efeito de recentrar a média puxa as previsões contra o observado. Exemplo: a água crua tem ρ de 0,41 na microrregião, e a regressão de 1 variável em leave-one-out cai para 0,18. Isso pesa contra o d2; por isso reporto também o d1 e a água crus, que não têm ajuste.
- **Penalidades do d1:** as de geada e de excesso são [ESTIMATIVA]. A da cebola foi pensada olhando a B3-2.
- **Fora da região:** Tabuleiro usa a mesma célula do POWER que Ituporanga.
- **Não testado:** IMERG, SMAP e GLDAS (pedem login Earthdata); NDVI como gabarito; a mistura de culturas por talhão; o Semiárido.

## 8. Arquivos
- `00_criterios_antes.md`: critérios escritos antes do teste.
- `v4_motor.py`: motor, validação e decisões. `v4_resultado.json`: todos os números.
- `graficos.py`: gera `fig1_rho_por_preditor.svg`, `fig2_ganho_sobre_climatologia.svg`, `fig3_decisao_data_milho.svg` e `fig4_decisao_transplante_cebola.svg`.
