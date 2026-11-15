# V2 · Camada de geada (B1-1) refeita no Oeste de SC

Data: 14/11/2026. Frente V2. Veredito: **parcial**.

Marcas: [DADO] vem de arquivo ou fonte externa. [CÁLCULO] vem de `v2_geada.py`. [ESTIMATIVA] é suposição de agrônomo. [INFERÊNCIA] é leitura minha.

## 1. Critério definido antes
Escrito em `CRITERIOS_ANTES_DO_TESTE.md` antes de rodar `v2_geada.py`. Resumo:

| Critério | Passa se |
|---|---|
| C1 Eventos | o proxy a 3 °C marca >= 80% dos eventos com data e local conferidos em estação (janela de ±2 dias) |
| C2 Viés | média mensal de `T2M_MIN` (mai a ago) em Chapecó fica a <= 1,5 °C da normal INMET 1961-1990 |
| C3 Espaço | a data-limite (3 °C) dos pontos fica dentro de 20 dias entre si |
| C4 Limiar | de 2 a 4 °C, a data-limite de SMO se move <= 20 dias |
| C5 ZARC | a data-limite de SMO fica a ±20 dias do fim da janela do ZARC 2026/27 de sorgo forrageiro 2ª safra, ciclo médio |
| C6 Degrau | o risco sobe >= 30 pontos percentuais entre 1/jan e 28/fev em cada ponto |

Regra: "sustenta" se C1, C3, C5 e C6 passam. "Parcial" se C6 passa e falha C1, C3 ou C5.

Um desvio do plano: o critério falava em 4 pontos. Dionísio Cerqueira cai na mesma célula do POWER que SMO (0 de 16.436 dias diferentes em `T2M_MIN`) [CÁLCULO]. Xanxerê cai na de Chapecó (mesma grade, mesma altitude 589,74 m, mesmo `T2M_MIN` nas 2 datas que testei; apaguei o arquivo) [CÁLCULO]. Ficam **3 células independentes**: SMO, Chapecó e Concórdia.

## 2. Método
- **Dados:** NASA POWER diário 1981-2025, `T2M_MIN` e `T2M_MAX`. SMO vem de `loop-validacao/dados/`. Chapecó (-27,10; -52,62), Concórdia (-27,234; -52,027) e Dionísio Cerqueira (-26,26; -53,64) baixei com `curl` para `dados/`.
- **Grade:** o POWER dá altitude de grade de 533 m (SMO), 590 m (Chapecó) e 884 m (Concórdia) [DADO, campo `geometry` dos JSON]. A célula tem ~50 km.
- **Geada:** `T2M_MIN` <= L, com L = 2, 3 e 4 °C. A 2 °C é o critério do ZARC milho 1ª safra (mínima < 2 °C no abrigo, fases I a III), Portaria SPA/MAPA 236/2026, item 1.13c [DADO]. A relva fica mais fria que o ar a 2 m [ESTIMATIVA].
- **Ponto de silagem:** 1.250 °C·dia, base 10 °C, teto 30 °C, igual ao B1-1 [ESTIMATIVA]. Sensibilidade a 1.100 e 1.400.
- **Risco do decêndio de plantio:** anos (de 45) com ao menos um dia de geada entre o plantio e o ponto de silagem. Mostro em "anos em 10" e o intervalo de 95% de Wilson.
- **Data-limite:** primeiro dia de plantio em que o risco passa de 2 em 10, com média móvel de 5 dias no plantio diário (1/jan a 31/mar).
- **Scripts:** `v2_geada.py` (saída em `v2_saida.txt` e `v2_resultado.json`).

## 3. Resultado

### 3.1 Tabela "anos em 10 com geada antes do ponto de silagem" [CÁLCULO]
Entre colchetes, o intervalo de 95% do limiar de 3 °C.

**São Miguel do Oeste** (reproduz exatamente a tabela do B1-1)

| Plantio | 1/jan | 11/jan | 21/jan | 1/fev | 11/fev | 21/fev | 1/mar | 11/mar | 21/mar |
|---|---|---|---|---|---|---|---|---|---|
| ≤ 2 °C | 0,0 | 0,0 | 0,0 | 0,2 | 3,8 | 6,2 | 8,2 | 9,3 | 9,3 |
| **≤ 3 °C** | 0,0 | 0,0 | 0,2 | **1,1** [0,5-2,3] | **4,4** [3,1-5,9] | 6,7 | 8,9 | 9,6 | 9,6 |
| ≤ 4 °C | 0,0 | 0,0 | 0,2 | 2,4 | 6,4 | 8,2 | 9,6 | 10,0 | 10,0 |
| Dias até a silagem (mediana) | 93 | 95 | 100 | 110 | 124 | 136 | 149 | 159 | 165 |

**Chapecó**

| Plantio | 1/jan | 11/jan | 21/jan | 1/fev | 11/fev | 21/fev | 1/mar | 11/mar | 21/mar |
|---|---|---|---|---|---|---|---|---|---|
| ≤ 2 °C | 0,0 | 0,0 | 0,2 | 1,3 | 4,2 | 6,9 | 8,4 | 9,1 | 9,1 |
| **≤ 3 °C** | 0,0 | 0,0 | 0,9 | **2,4** [1,4-3,9] | 5,3 | 7,6 | 8,7 | 9,3 | 9,3 |
| ≤ 4 °C | 0,0 | 0,0 | 1,6 | 4,0 | 7,3 | 8,7 | 9,3 | 10,0 | 10,0 |
| Dias até a silagem | 96 | 100 | 104 | 115 | 129 | 144 | 154 | 163 | 170 |

**Concórdia** (grade a 884 m)

| Plantio | 1/jan | 11/jan | 21/jan | 1/fev | 11/fev | 21/fev | 1/mar | 11/mar | 21/mar |
|---|---|---|---|---|---|---|---|---|---|
| ≤ 2 °C | 0,7 | 2,4 | 5,6 | 8,0 | 9,3 | 9,8 | 9,8 | 9,7 | 9,4 |
| **≤ 3 °C** | 0,9 | 3,1 | 6,4 | 8,4 | 9,8 | 10,0 | 10,0 | 10,0 | 10,0 |
| ≤ 4 °C | 2,0 | 4,4 | 8,0 | 9,1 | 10,0 | 10,0 | 10,0 | 10,0 | 10,0 |
| Dias até a silagem | 117 | 123 | 138 | 155 | 169 | 180 | 187 | 186 | 187 |

Leitura:
- Em SMO e Chapecó o risco é quase zero até 21/jan e depois sobe como degrau. Em SMO, de 1/fev a 11/fev o risco vai de 1,1 para 4,4 em 10 anos.
- Em Concórdia o degrau começa em janeiro. O ciclo é mais longo (117 dias já no plantio de 1/jan) e a madrugada é mais fria.
- Os intervalos são largos (n = 45). No limite de SMO o risco de 1/fev tem intervalo de 0,5 a 2,3. Trate a data-limite como "± um decêndio".

### 3.2 Data-limite (risco <= 2 em 10), plantio diário [CÁLCULO]

| Ponto | ≤ 2 °C | ≤ 3 °C | ≤ 4 °C |
|---|---|---|---|
| SMO | 07/02 | **05/02** | 30/01 |
| Chapecó | 03/02 | **30/01** | 24/01 |
| Concórdia | 09/01 | **07/01** | já em 1/jan |

- **Ciclo (SMO, 3 °C):** 1.100 °C·dia dá 16/02; 1.250 dá 05/02; 1.400 dá 25/01. Variação de 22 dias só por trocar o híbrido [CÁLCULO]. No decêndio de 11/fev o risco é 0,9, 4,4 e 7,1 em 10.
- **1ª geada do outono (≤ 3 °C):** em SMO, p10 = 23/mai, mediana = 17/jun, p90 = 13/jul. Em Chapecó, 09/mai, 14/jun e 07/jul. Em Concórdia, 29/abr, 27/mai e 03/jul [CÁLCULO].
- **Dias por ano com `T2M_MIN` ≤ 3 °C:** SMO 7,9; Chapecó 8,8; Concórdia 13,5 [CÁLCULO].
- **Tendência (SMO, 3 °C):** em 11/fev o risco foi 5,0 em 10 em 1981-2002 e 3,9 em 2003-2025. Em 21/fev, 7,7 e 5,7. Em Chapecó o sinal é misto (11/fev: 6,4 e 4,3; 1/fev: 2,3 e 2,6). Com 22 e 23 anos por metade, não testei se a queda é real [CÁLCULO].

## 4. Conferência externa

### 4.1 A lista de geadas do B1-1 (veio da memória)
Cada evento foi buscado em fonte externa. Só consegui **dados de estação** do Oeste em 2 eventos abertos e 3 em trechos de busca.

| Evento | Status | O que achei | POWER (menor `T2M_MIN` em ±2 d) |
|---|---|---|---|
| 19/06/1981 | **Estação** | Chapecó, mínima absoluta de junho 1961-90: -2,8 °C, em 19/06/1981. Tabela INMET da Embrapa Clima Temperado (`externo/temp_min_absoluta_1_6_SC.pdf`) [DADO] | Chapecó -0,7; SMO -2,0 |
| 31/05/1988 | **Estação** | Chapecó, mínima de maio: -0,6 °C, em 31/05/1988. Mesma tabela [DADO] | Chapecó -0,7 |
| 14/07/2000 | Estação, só trecho de busca | Chapecó -4,5 °C e SMO -3 °C em 14/07/2000, segundo Epagri/Ciram via NSC Total. A página devolveu 403 e **não abri** [INFERÊNCIA] | Chapecó -4,5; SMO -3,4 |
| 15/08/2009 | Estação, só trecho de busca | SMO -3 °C em 15/08/2009, mesma fonte, **não aberta** | SMO **+9,4** (o dia 15 teve 14,3 °C). Miss |
| 26/06/1994 | **Não confirmado** | Só achei geada de jun/1994 no Sudeste (café). Para o Sul, nada | SMO -2,7 |
| 17/07/2000 | **Data errada** | O dado datado é 14/07/2000. O frio de jul/2000 existe (Embrapa: julho de 2000 foi o mês mais frio da série da estação deles desde 1991) | SMO -3,0 |
| 22-25/07/2013 | Regional | Epagri/Ciram: neve de 22 a 25/07/2013. INMET Major Vieira -4,1 °C em 24/07. Oeste não citado | SMO -2,1; Chapecó -2,8 |
| 30/06/2021 | Regional | Epagri/Ciram: 3º dia seguido de neve em 30/06/2021. Oeste não citado | SMO -1,9 |
| 29/07/2021 | Regional | INMET: -8,6 °C em Bom Jardim da Serra em 29/07/2021. Oeste não citado | SMO -0,3; Chapecó -1,6 |
| 17-20/05/2022 | Regional | Epagri/Ciram: neve em 17/05 e -5,1 °C em Urupema em 20/05/2022. Oeste não citado | SMO **2,9**; Chapecó **4,4**; Concórdia 1,9 |
| 25/06/2025 (novo) | Regional | Epagri/Ciram: 49 municípios negativos em 25/06/2025; o frio forte ficou na Serra e no Meio-Oeste | SMO -1,4; Chapecó -2,0 |

Resumo [CÁLCULO]:
- **Eventos com estação aberta (2):** 2 de 2 marcados com 2, 3 ou 4 °C.
- **Com os 3 trechos de busca (5 eventos):** 4 de 5 marcados (80%). O erro é 15/08/2009 em SMO, e a data pode estar errada na fonte.
- **Regionais (7 datas, contando 1994 e 17/07/2000):** a 3 °C, 6 de 7 marcam nos 3 pontos. 17-20/05/2022 marca em SMO e Concórdia, mas não em Chapecó.
- **Acerto ao acaso:** uma janela de 5 dias tem, a 3 °C, 6,7% de chance de passar do limiar em maio, 21% em junho e 29% em julho em Chapecó. Acertar os 2 eventos abertos por sorte tem cerca de 1,4% de chance [CÁLCULO, supondo independência].

### 4.2 Viés do POWER contra a estação INMET de Chapecó
Normal 1961-1990 de `T2M_MIN`, Embrapa Clima Temperado (`externo/embrapa_temp_minima_SC.pdf`) [DADO]. POWER é 1981-2025, a 590 m de grade; a estação fica a 679 m.

| Mês | Mar | Abr | Mai | Jun | Jul | Ago | Set | Out |
|---|---|---|---|---|---|---|---|---|
| Normal INMET | 17,4 | 14,6 | 11,8 | 9,9 | 10,3 | 11,5 | 12,1 | 14,3 |
| POWER 1981-2025 | 17,4 | 14,8 | 11,4 | 9,7 | 8,9 | 10,2 | 12,0 | 14,6 |
| Viés | 0,0 | +0,2 | -0,4 | -0,2 | **-1,4** | **-1,3** | -0,1 | +0,3 |

- Pela regra do C2 (período todo), passa: o maior viés é 1,4 °C. Se eu comparasse só 1981-1990 (mesma década da normal), jul e ago dariam -1,8 e -1,6 °C, acima de 1,5. O C2 passa por pouco.
- O POWER é **mais frio na média** que a estação em jul-ago. Mas nos extremos é **menos frio**: a mínima de junho de 1981-90 no POWER é -1,9 °C e a da estação é -2,8 °C; a de maio é -0,5 e -0,6 [CÁLCULO]. Os dois efeitos podem se cancelar no limiar de 3 °C, mas não medi isso.

### 4.3 ZARC
- Não há ZARC de milho 2ª safra para SC no extrato 2026/27 que a A1 baixou (`loop-validacao/sessoes/A1/ext/zarc_2627_smo_itu.csv`, 500 linhas de SMO e Ituporanga). Só existe "Milho 1ª Safra". O arquivo completo da B1 está vazio (0 bytes) e não tentei baixar os 161 MB de novo [DADO].
- **Substituto indireto:** sorgo forrageiro 2ª safra em SMO, Portaria 315/2026. Plantio com risco de 20%: ciclo 22 até 31/jan, ciclo 21 até 20/fev, ciclo 20 até 10/mar [DADO; decêndio 1 = 1-10/jan, confere com os outros cultivos do CSV]. Sorgo granífero 2ª safra (Portaria 288/2026): ciclo 22 até 20/jan, ciclo 21 até 10/fev, ciclo 20 até 28/fev [DADO].
- **Nossa data-limite de SMO a 3 °C é 05/02.** Fica 15 dias antes do fim do ciclo médio (20/fev). A 2 °C é 07/02 (13 dias). A 4 °C é 30/01 (21 dias, passa do limite).
- **Cuidado:** o ZARC dá o risco de água e de frio juntos, e para o sorgo não li o critério de frio. A coincidência pode vir da água. O milho 1ª safra usa `Tmin < 2 °C` até a fase III, que é o limiar de 2 °C aqui [DADO, Portaria 236/2026].
- O estudo de Chapecó (Arakaki e Minuzzi, trecho de busca: risco de geada de 20%) continua **sem abrir**: o core.ac.uk devolveu uma página HTML, não o PDF, de novo [INFERÊNCIA].

## 5. Critérios

| Critério | Resultado | Nota |
|---|---|---|
| C1 Eventos | **Passa, no limite**: 2 de 2 (abertos); 4 de 5 (80%) com os trechos de busca | 3 dos 5 eventos vêm de trecho não aberto |
| C2 Viés | **Passa, no limite**: máximo -1,4 °C (período todo) | Em 1981-90 jul e ago dão -1,8 e -1,6 |
| C3 Espaço | **Falha**: SMO 05/02, Chapecó 30/01, Concórdia 07/01 (29 dias de diferença) | SMO e Chapecó ficam a 6 dias |
| C4 Limiar | **Passa**: 07/02 a 30/01, 8 dias | O ciclo move 22 dias |
| C5 ZARC | **Passa**: 15 dias do fim do ciclo médio | Substituto indireto, mistura água |
| C6 Degrau | **Passa**: de 1/jan a 28/fev o risco sobe 82 pp (SMO), 87 pp (Chapecó) e 91 pp (Concórdia) | — |

## 6. Veredito: parcial
- **O que se sustenta:** a camada de geada funciona onde foi testada. O proxy `T2M_MIN` do POWER enxerga as geadas conferidas em estação, o degrau de risco é forte e a data-limite de SMO fica perto da janela do ZARC do sorgo forrageiro 2ª safra. A tabela do B1-1 foi reproduzida sem diferença.
- **O que não se sustenta:** uma data única para "o Oeste". A data-limite varia 29 dias entre SMO e Concórdia, e 22 dias com a escolha do ciclo da cultivar. Isso falha o C3.
- **Lista de eventos do B1-1:** 1 evento sem confirmação (jun/1994), 1 data errada (jul/2000 é 14/07) e só 2 com estação aberta. Os outros 5 estão confirmados como frio regional, mas não no Oeste.
- **Limite de dados:** não achei série de estação do Oeste depois de 2000 para conferir. A série seria o histórico do Ciram/Agroconnect ou do INMET (não testei).

## 7. Implicações para a solução
1. **Manter a camada, calculada por ponto.** O módulo de geada roda com o `T2M_MIN` do POWER da localização do talhão. Não dá para dar uma data para a região inteira.
2. **Mostrar faixa, não dia.** Para SMO: "plantar até ~30/jan a 07/fev (limiar 4 a 2 °C)". O cartão deve trazer o risco do decêndio em "anos em 10", com o intervalo (ex.: 1/fev = 1 [0,5-2,3]; 11/fev = 4 [3,1-5,9]).
3. **Pedir o ciclo da cultivar.** É o parâmetro que mais move a data (22 dias). O módulo precisa do ciclo em °C·dia como entrada do produtor.
4. **Altitude pede correção.** Concórdia (grade a 884 m) tem a data-limite no início de janeiro. Dentro de uma célula de 50 km a altitude do talhão muda o risco. O SRTM (da lista de recursos do desafio) é o candidato a ajustar isso. Não testei.
5. **Papel no motor modular.** É um módulo regional do Oeste de SC, para a decisão "2º milho x pastagem de inverno", em propriedade de leite. A área é pequena (a PAM, tabela 839, tem 0 a 100 ha de milho 2ª safra em grão em SMO [DADO, segundo o B1-1]). Não é o argumento principal da demo.
6. **O que falta antes do pitch:** (a) abrir os trechos da Epagri/Ciram (14/07/2000 e 15/08/2009) e achar séries de estação do Oeste pós-2000; (b) abrir o estudo de Chapecó; (c) conferir o ZARC de milho 2ª safra de SC se existir (o CSV completo); (d) medir se a queda de risco 2003-2025 é real.
7. **Não vender o que não se mediu:** a perda de silagem por geada não tem gabarito de campo. A camada dá a **chance** de geada, não a perda.

## 8. Arquivos
- `CRITERIOS_ANTES_DO_TESTE.md`: critérios definidos antes.
- `v2_geada.py`, `v2_saida.txt`, `v2_resultado.json`: script, saída e números.
- `v2_1_smo_limiares.svg`: risco por limiar em SMO com as janelas do ZARC do sorgo.
- `v2_2_pontos.svg`: risco nos 3 pontos (3 °C).
- `v2_3_eventos.svg`: menor `T2M_MIN` por evento.
- `dados/`: POWER de Chapecó, Concórdia e Dionísio Cerqueira. `externo/`: tabelas Embrapa/INMET e outros PDFs baixados.

## 9. Fontes
- NASA POWER, API diária, comunidade AG, 1981-2025 (via `curl`).
- Embrapa Clima Temperado, Laboratório de Agrometeorologia, Normais Climatológicas 1961-1990 (INMET), SC: temperatura mínima e mínima absoluta (agromet.cpact.embrapa.br/tab/).
- MAPA, Portaria SPA/MAPA 236/2026 (milho 1ª safra SC, critério de geada) e tábua de risco ZARC 2026/27 (Portarias 288 e 315/2026), extrato em `loop-validacao/sessoes/A1/ext/`.
- Eventos: Epagri/Ciram via Rio Times, NSC Total e Climatempo (trechos de busca de 14/11/2026; páginas do NSC Total devolveram 403).
