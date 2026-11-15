# V6 · ZARC como gabarito em Santa Catarina

Frente V6. Data: 14/11/2026. Municípios: São Miguel do Oeste (SMO, 4217204) e Ituporanga (4208500). Regra: o ZARC é gabarito para conferir a solução, nunca entrada do modelo.

## 1. Critério definido antes
Está em `CRITERIOS_ANTES.md`. Resumo:
- G1 cobertura: há ZARC para milho 1ª safra, milho 2ª safra, sorgo, aveia e cebola nos dois municípios? (Esperado: milho 2ª safra não existe em SC.)
- G2 qualidade: todo risco vale 0, 20, 30 ou 40.
- C-B1-0: o 1º decêndio com risco ZARC <= 20% (AD4–AD6, grupo I) fica a até 10 dias do 1º decêndio em que a B1 mede geada <= 2 em 10 anos (01/09).
- C-B1-1: o último plantio indicado pelo ZARC (milho no tronco de jan; sorgo 2ª safra) fica a até 20 dias da data-limite da B1-1 (01/02).
- C-A4-3: entre 11/09 e 21/10, o milho tem risco ZARC >= 10 pontos acima do sorgo na classe que a A4 chamou de "raso" (87,5 mm = AD5/AD6; ver nota de mapeamento).
- C-cebola: janela para cebola em Ituporanga em maio–outubro.
- Regra do veredito: "sustenta" se G1 e G2 passam e >= 2 das 3 comparações concordam.

Transparência: li o resumo do ZARC de SMO feito pela A4 antes de fixar o critério. Não tinha calculado nenhuma comparação.

## 2. Método
- Fonte: tábua de risco ZARC 2026/27 (SISZARC, portal dados.agricultura.gov.br), CSV baixado pela A1: `ext/zarc_2627_smo_itu.csv` (anuais) e `ext/zarc_perene_smo_itu.csv` (cebola, triticale, centeio). O arquivo da B1 (`zarc_smo_itu_full.csv`) tem 0 bytes e foi descartado. Tentei baixar o dicionário de dados: conexão recusada [DADO: `curl` devolveu "Connection reset by peer"].
- `gerar_gabarito.py` lê os CSV, filtra os dois municípios, converte cada linha em risco por decêndio de plantio (dec1 = 1/jan ... dec36 = 21/dez) e identifica as janelas (blocos de decêndios indicados). Saída: `zarc_gabarito_sc.json` (gabarito) e `resultados_comparacao.json`.
- `extras_e_graficos.py` faz os gráficos SVG; `tabelas_md.py` gera `tabelas.md`.
- Mapeamentos que usei e não consegui confirmar no dicionário [INFERÊNCIA]:
  - `dec1` = 1–10/jan. Sustento: aveia cai em maio–jul e cebola em maio–set, o que é agronomicamente certo; a A4 usou a mesma convenção.
  - Cod_Ciclo 20/21/22 = grupo I/II/III do milho (a portaria 236 define 3 grupos).
  - Cod_Solo 11–16 = AD1–AD6 (24; 31,8; 41,4; 54,6; 72,6; 95,4 mm, raiz de 60 cm; Portaria 236/2026, item 1.12 [DADO]). Sorgo usa solos 1–3 (textura), sem significado confirmado.
  - Cebola: códigos de ciclo 20–26; o significado não foi confirmado.
- Nível de risco do ZARC: só 20, 30 ou 40%. Decêndio ausente = não indicado.

## 3. Resultado
### 3.1 Gabarito (o que o ZARC diz)
- Cobertura (G1): para os dois municípios há milho 1ª safra, sorgo forrageiro 1ª e 2ª safra, sorgo granífero, aveia, triticale, centeio e cebola (sequeiro, irrigada e com bulbinho). **Não há milho 2ª safra** [DADO: ausente da tábua 2026/27 de SC].
- Qualidade (G2): 12.996 valores, nenhum fora de 0/20/30/40 [CÁLCULO].
- Milho 1ª safra tem plantio indicado de 01/08 (SMO) ou 21/08 (Ituporanga) até 21/01. Em SMO, 01/08 e 11/08 são sempre 40%. De 21/08 em diante, solos AD5–AD6 ficam em 20% o tempo todo [CÁLCULO].
- Solo raso (AD1) quase não tem janela de milho em SMO: 0 dos 5 decêndios de 11/09 a 21/10 estão indicados [CÁLCULO].
- Sorgo forrageiro 1ª safra: 20% de 11/09 a 11/12 em SMO, igual em todos os solos e grupos. Sorgo forrageiro 2ª safra: 20% de 21/12 até 01/03 (grupo I), 11/02 (II) ou 21/01 (III) em SMO; até 11/03, 21/02 e 01/02 em Ituporanga [CÁLCULO].
- Aveia: janela estreita. SMO: 11/05 a 01/07 (20–40%). Ituporanga: 01/06 a 21/07 (20%).
- Cebola: em SMO nenhuma combinação chega a 20% (mediana do melhor risco = 30%). Em Ituporanga a mediana do melhor risco é 20%, e 31% dos decêndios sequeiro estão em 20%. Janelas de 01/05 a 21/09 [CÁLCULO: `resultados_comparacao.json`].
- Gráficos: `v6_janelas_zarc.svg` (calendário por cultura e município).

Tabelas completas por município, grupo e classe de solo: `tabelas.md` (copiadas abaixo). Dados decêndio a decêndio: `zarc_gabarito_sc.json`.


### Sao Miguel do Oeste — milho 1ª safra (sequeiro, Port.236_de_10-07-2026)

| Grupo | AD1 | AD2 | AD3 | AD4 | AD5 | AD6 |
|---|---|---|---|---|---|---|
| I | 01/08 a 01/09 (20–40%) | 01/08 a 11/09 (20–40%); 21/10 a 21/01 (30–40%) | 01/08 a 21/01 (20–40%) | 01/08 a 21/01 (20–40%) | 01/08 a 21/01 (20–40%) | 01/08 a 21/01 (20–40%) |
| II | 01/08 a 11/08 (40%); 11/01 a 21/01 (40%) | 01/08 a 21/01 (30–40%) | 01/08 a 21/01 (20–40%) | 01/08 a 21/01 (20–40%) | 01/08 a 21/01 (20–40%) | 01/08 a 21/01 (20–40%) |
| III | 01/08 a 01/08 (40%); 11/01 a 11/01 (40%) | 01/08 a 11/08 (40%); 21/09 a 21/01 (30–40%) | 01/08 a 21/01 (20–40%) | 01/08 a 21/01 (20–40%) | 01/08 a 21/01 (20–40%) | 01/08 a 21/01 (20–40%) |

**Sorgo forrageiro 1ª safra (Port.315_de_23-07-2026)**

| Grupo | solo_tipo_1 | solo_tipo_2 | solo_tipo_3 |
|---|---|---|---|
| I | 01/09 a 11/12 (20–40%) | 01/09 a 11/12 (20–40%) | 01/09 a 11/12 (20–40%) |
| II | 01/09 a 11/12 (20–40%) | 01/09 a 11/12 (20–40%) | 01/09 a 11/12 (20–40%) |
| III | 01/09 a 11/12 (20–40%) | 01/09 a 11/12 (20–40%) | 01/09 a 11/12 (20–40%) |

**Sorgo forrageiro 2ª safra (Port.315_de_23-07-2026)**

| Grupo | solo_tipo_1 | solo_tipo_2 | solo_tipo_3 |
|---|---|---|---|
| I | 21/12 a 01/03 (20%) | 21/12 a 01/03 (20%) | 21/12 a 01/03 (20%) |
| II | 21/12 a 11/02 (20%) | 21/12 a 11/02 (20%) | 21/12 a 11/02 (20%) |
| III | 21/12 a 21/01 (20%) | 21/12 a 21/01 (20%) | 21/12 a 21/01 (20%) |

**Aveia (Port.384_de_10-11-2026)**

| Grupo | AD1 | AD2 | AD3 | AD4 | AD5 | AD6 |
|---|---|---|---|---|---|---|
| I | 11/05 a 01/07 (30–40%) | 11/05 a 01/07 (30–40%) | 11/05 a 01/07 (20–40%) | 11/05 a 01/07 (20–40%) | 11/05 a 01/07 (20–40%) | 11/05 a 01/07 (20–40%) |
| II | 11/05 a 01/07 (20–40%) | 11/05 a 01/07 (20–30%) | 11/05 a 01/07 (20–30%) | 11/05 a 01/07 (20–30%) | 11/05 a 01/07 (20–30%) | 11/05 a 01/07 (20–30%) |
| III | 11/05 a 01/07 (20–30%) | 11/05 a 01/07 (20–30%) | 11/05 a 01/07 (20–30%) | 11/05 a 01/07 (20–30%) | 11/05 a 01/07 (20–30%) | 11/05 a 01/07 (20–30%) |

**Triticale (Port. 439_de_28-12-2023)**

| Grupo | AD1 | AD2 | AD3 | AD4 | AD5 | AD6 |
|---|---|---|---|---|---|---|
| I | 11/05 a 01/07 (30–40%) | 11/05 a 01/07 (30–40%) | 11/05 a 01/07 (20–40%) | 11/05 a 01/07 (20–40%) | 11/05 a 01/07 (20–40%) | 11/05 a 01/07 (20–40%) |
| II | 11/05 a 01/07 (20–40%) | 11/05 a 01/07 (20–30%) | 11/05 a 01/07 (20–30%) | 11/05 a 01/07 (20–30%) | 11/05 a 01/07 (20–30%) | 11/05 a 01/07 (20–30%) |
| III | 01/05 a 21/06 (20–30%) | 01/05 a 21/06 (20–30%) | 01/05 a 21/06 (20–30%) | 01/05 a 21/06 (20–30%) | 01/05 a 21/06 (20–30%) | 01/05 a 21/06 (20–30%) |

**Centeio (Port.10_de_14-01-2025)**

| Grupo | AD1 | AD2 | AD3 | AD4 | AD5 | AD6 |
|---|---|---|---|---|---|---|
| I | 11/05 a 01/07 (30–40%) | 11/05 a 01/07 (30–40%) | 11/05 a 01/07 (20–40%) | 11/05 a 01/07 (20–40%) | 11/05 a 01/07 (20–40%) | 11/05 a 01/07 (20–40%) |
| II | 11/05 a 01/07 (20–30%) | 11/05 a 01/07 (20–30%) | 11/05 a 01/07 (20–30%) | 11/05 a 01/07 (20–30%) | 11/05 a 01/07 (20–30%) | 11/05 a 01/07 (20–30%) |
| III | 01/05 a 21/06 (20–30%) | 01/05 a 21/06 (20–30%) | 01/05 a 21/06 (20–30%) | 01/05 a 21/06 (20–30%) | 01/05 a 21/06 (20–30%) | 01/05 a 21/06 (20–30%) |

**Cebola sequeiro (Port.4_de_09-02-2024)**, solo AD5 (AD1–AD6 variam; ver JSON)

| Ciclo | Janelas (plantio) |
|---|---|
| ciclo_20 | 01/06 a 01/06 (40%); 11/08 a 11/09 (30–40%) |
| ciclo_21 | 21/07 a 01/09 (30–40%) |
| ciclo_22 | 01/07 a 11/08 (30–40%) |
| ciclo_24 | 11/06 a 01/08 (30–40%) |
| ciclo_25 | 21/05 a 21/07 (30–40%) |
| ciclo_26 | 11/05 a 01/07 (30–40%) |

### Ituporanga — milho 1ª safra (sequeiro, Port.236_de_10-07-2026)

| Grupo | AD1 | AD2 | AD3 | AD4 | AD5 | AD6 |
|---|---|---|---|---|---|---|
| I | 21/08 a 21/01 (20–30%) | 21/08 a 21/01 (20–30%) | 21/08 a 21/01 (20–30%) | 21/08 a 21/01 (20–30%) | 21/08 a 21/01 (20–30%) | 21/08 a 21/01 (20–30%) |
| II | 21/08 a 21/01 (20–40%) | 21/08 a 21/01 (20–30%) | 21/08 a 21/01 (20–30%) | 21/08 a 21/01 (20–30%) | 21/08 a 21/01 (20–30%) | 21/08 a 21/01 (20–30%) |
| III | 21/08 a 21/01 (20–40%) | 21/08 a 21/01 (20–40%) | 21/08 a 21/01 (20–40%) | 21/08 a 21/01 (20–40%) | 21/08 a 21/01 (20–40%) | 21/08 a 21/01 (20–40%) |

**Sorgo forrageiro 1ª safra (Port.315_de_23-07-2026)**

| Grupo | solo_tipo_1 | solo_tipo_2 | solo_tipo_3 |
|---|---|---|---|
| I | 21/08 a 11/12 (20–40%) | 21/08 a 11/12 (20–40%) | 21/08 a 11/12 (20–40%) |
| II | 21/08 a 11/12 (20–40%) | 21/08 a 11/12 (20–40%) | 21/08 a 11/12 (20–40%) |
| III | 21/08 a 11/12 (20–40%) | 21/08 a 11/12 (20–40%) | 21/08 a 11/12 (20–40%) |

**Sorgo forrageiro 2ª safra (Port.315_de_23-07-2026)**

| Grupo | solo_tipo_1 | solo_tipo_2 | solo_tipo_3 |
|---|---|---|---|
| I | 21/12 a 11/03 (20%) | 21/12 a 11/03 (20%) | 21/12 a 11/03 (20%) |
| II | 21/12 a 21/02 (20%) | 21/12 a 21/02 (20%) | 21/12 a 21/02 (20%) |
| III | 21/12 a 01/02 (20%) | 21/12 a 01/02 (20%) | 21/12 a 01/02 (20%) |

**Aveia (Port.384_de_10-11-2026)**

| Grupo | AD1 | AD2 | AD3 | AD4 | AD5 | AD6 |
|---|---|---|---|---|---|---|
| I | 01/06 a 21/07 (20%) | 01/06 a 21/07 (20%) | 01/06 a 21/07 (20%) | 01/06 a 21/07 (20%) | 01/06 a 21/07 (20%) | 01/06 a 21/07 (20%) |
| II | 01/06 a 21/07 (20%) | 01/06 a 21/07 (20%) | 01/06 a 21/07 (20%) | 01/06 a 21/07 (20%) | 01/06 a 21/07 (20%) | 01/06 a 21/07 (20%) |
| III | 01/06 a 21/07 (20%) | 01/06 a 21/07 (20%) | 01/06 a 21/07 (20%) | 01/06 a 21/07 (20%) | 01/06 a 21/07 (20%) | 01/06 a 21/07 (20%) |

**Triticale (Port. 439_de_28-12-2023)**

| Grupo | AD1 | AD2 | AD3 | AD4 | AD5 | AD6 |
|---|---|---|---|---|---|---|
| I | 01/06 a 21/07 (20%) | 01/06 a 21/07 (20%) | 01/06 a 21/07 (20%) | 01/06 a 21/07 (20%) | 01/06 a 21/07 (20%) | 01/06 a 21/07 (20%) |
| II | 01/06 a 21/07 (20%) | 01/06 a 21/07 (20%) | 01/06 a 21/07 (20%) | 01/06 a 21/07 (20%) | 01/06 a 21/07 (20%) | 01/06 a 21/07 (20%) |
| III | 21/05 a 11/07 (20%) | 21/05 a 11/07 (20%) | 21/05 a 11/07 (20%) | 21/05 a 11/07 (20%) | 21/05 a 11/07 (20%) | 21/05 a 11/07 (20%) |

**Centeio (Port.10_de_14-01-2025)**

| Grupo | AD1 | AD2 | AD3 | AD4 | AD5 | AD6 |
|---|---|---|---|---|---|---|
| I | 01/06 a 21/07 (20%) | 01/06 a 21/07 (20%) | 01/06 a 21/07 (20%) | 01/06 a 21/07 (20%) | 01/06 a 21/07 (20%) | 01/06 a 21/07 (20%) |
| II | 01/06 a 21/07 (20%) | 01/06 a 21/07 (20%) | 01/06 a 21/07 (20%) | 01/06 a 21/07 (20%) | 01/06 a 21/07 (20%) | 01/06 a 21/07 (20%) |
| III | 21/05 a 11/07 (20%) | 21/05 a 11/07 (20%) | 21/05 a 11/07 (20%) | 21/05 a 11/07 (20%) | 21/05 a 11/07 (20%) | 21/05 a 11/07 (20%) |

**Cebola sequeiro (Port.4_de_09-02-2024)**, solo AD5 (AD1–AD6 variam; ver JSON)

| Ciclo | Janelas (plantio) |
|---|---|
| ciclo_20 | 21/06 a 21/09 (20–40%) |
| ciclo_21 | 11/06 a 21/09 (20–40%) |
| ciclo_22 | 21/05 a 21/09 (20–40%) |
| ciclo_24 | 01/05 a 21/09 (20–40%) |
| ciclo_25 | 01/05 a 21/09 (20–40%) |
| ciclo_26 | 01/05 a 21/09 (20–40%) |


### 3.2 Conferência com as fichas
**B1-0 e B1-1 (geada).** `v6_b1_geada_x_zarc.svg`.

| Plantio SMO | Geada B1 (anos em 100) | ZARC milho gr. I, AD4 | ZARC AD6 |
|---|---|---|---|
| 01/08 | 63 | 40% | 40% |
| 11/08 | 46 | 40% | 40% |
| 21/08 | 32 | 20% | 20% |
| 01/09 | 17 | 20% | 20% |
| 11/09 | 5 | 20% | 20% |
| 21/09 em diante | 0 | 30% | 20% |

Fontes: geada em `loop-validacao/sessoes/B1/b1_0_geada_controle.txt`; ZARC em `resultados_comparacao.json`.
- **Concorda no formato.** Os dois dizem que agosto é a pior época e que o risco cai até setembro. O ZARC confirma que o controle só de água, que mandava plantar em agosto, estava errado [INFERÊNCIA: o ZARC conta geada, mas não separei o peso dela do peso da água].
- **C-B1-0 passa por pouco.** Primeiro decêndio <= 20%: 21/08 no ZARC e 01/09 na B1, 10 dias de diferença (limite do critério).
- **Discorda na magnitude.** A geada do POWER (T2M_MIN < 2 °C) é mais frequente que o risco total do ZARC: 63% contra 40% em 01/08 e 32% contra 20% em 21/08. O risco do ZARC reúne água, geada e frio. Então a geada medida pelo POWER parece superestimar [INFERÊNCIA; causa não testada: grade de ~50 km contra estações em abrigo e interpolação].
- **B1-1, C-B1-1 passa.** Último plantio de milho no ZARC: 21/01 (SMO e Ituporanga). A B1-1 pôs o limite em 01/02: 11 dias de diferença. Para o sorgo 2ª safra o ZARC termina em 11/02 (grupo II, 10 dias depois de 01/02), 21/01 (grupo III, 11 dias antes) e 01/03 (grupo I, 28 dias depois; fora do ±20).
- **Ressalva da B1-1.** O ZARC tem ciclo de grão (130 dias ou mais), a B1-1 mira silagem (cerca de 100–110 dias). Parte da coincidência pode ser acaso [INFERÊNCIA]. A ficha disse que não havia ZARC de 2ª safra para SC: está confirmado para milho.
- **Novo.** Depois de 21/01, o ZARC ainda indica sorgo forrageiro 2ª safra a 20%, até 21/01–01/03 em SMO (conforme o grupo) e 01/02–11/03 em Ituporanga. A B1-1 só oferecia "aveia" depois de 01/02. O sorgo é uma terceira opção para a rotação [INFERÊNCIA: não testei geada nem água do sorgo nessas datas].

**A4-3 (sorgo como seguro em solo raso).** `v6_a4_milho_x_sorgo.svg`. Milho grupo I, SMO, plantio de 11/09 a 21/10:

| Classe | Água (mm) | Risco ZARC do milho (5 decêndios) | Sorgo |
|---|---|---|---|
| AD1 | 24 | nenhum indicado | 20% |
| AD2 | 31,8 | 40%, 2 de 5 indicados | 20% |
| AD3 | 41,4 | 30% nos 5 | 20% |
| AD4 | 54,6 | 20–30% | 20% |
| AD5 | 72,6 | 20% nos 5 | 20% |
| AD6 | 95,4 | 20% nos 5 | 20% |

- **Concorda no sentido.** Quanto menos água no solo, mais o milho perde frente ao sorgo (sorgo é 20% em todos os solos, nos três grupos).
- **Discorda onde a A4 aplicou.** A4 chamou de "raso" 175 mm/m x 0,5 m = 87,5 mm. No ZARC isso é AD5–AD6, onde milho e sorgo têm o mesmo risco (diferença de 0 ponto). O critério C-A4-3 **falha**. O ganho de 14% do P10 que a A4 achou em "raso" não aparece no ZARC. A A4 escreveu que o ZARC "bate"; isso vale só para solos de 41 mm ou menos.
- **O que isso muda.** Com os valores do GAEZ do protótipo (65, 125 e 175 mm/m) e raiz de 60 cm, a classe baixa dá 39 mm, que é AD2–AD3 [CÁLCULO: 65 x 0,6]. Aí o ZARC concorda (diferença de 10 a 20 pontos). Falta testar o modelo da A4 nessa definição de solo.
- Sorgo no ZARC não varia com o solo (as 3 classes são idênticas): o ZARC não prova que o sorgo é mais tolerante, só que não é limitado por água nas datas de setembro a dezembro.

**Cebola em Ituporanga (C-cebola passa).** Janela de 01/05 a 21/09, risco 20–40%. Ituporanga é melhor que SMO (mediana do melhor risco 20% contra 30%). O padrão de risco por ciclo muda a janela (ex.: ciclo 22 começa em 21/05, ciclo 20 em 21/06). Não consegui ver se o risco da cebola no ZARC vem de água ou de frio: só 5 de 18 pares sequeiro/irrigado em SMO e 6 de 35 em Ituporanga são idênticos [CÁLCULO: `extras_cebola_seq_irr.json`], então o manejo importa, mas a causa fica sem prova.

### 3.3 Conta final
- G1: passa (milho 2ª safra ausente, como esperado). G2: passa.
- C-B1-0: passa (10 dias, no limite). C-B1-1: passa (11 dias). C-A4-3: falha.
- Cebola: passa.

## 4. Conferência externa
O ZARC é a própria conferência externa. Para a pergunta "o ZARC é um bom gabarito?", conferi a consistência interna:
- A portaria 236/2026 (texto em `loop-validacao/sessoes/B1/externo/zarc_portaria_236_2026_milho1_SC.txt`) descreve 3 grupos de ciclo e 6 classes AD com os mesmos números que usei. O critério de geada é Tmin < 2 °C nas fases 1 a 3, o mesmo da B1 [DADO].
- O ZARC é calibrado com séries de 30 anos e estações em abrigo (chuva) e interpolação de 735 estações (temperatura); o NASA POWER é grade de ~50 km. As duas fontes não são independentes por completo: o ZARC usa o POWER para a ET0 em parte do país [DADO: B1-0 cita o ZARC; não reabri a portaria].
- Não conferi o ZARC contra produtividade real (PAM). O ZARC é uma norma de seguro (risco de perda de 20/30/40%), não uma medida de safra. Concordar com ele é bom sinal, não prova de acerto agronômico.

## 5. Veredito
**Sustenta.** O ZARC serve como gabarito em SC para as janelas de milho, sorgo, aveia e cebola, e concorda com a B1 (geada) e com o sentido da A4-3. Não valida o ganho da A4-3 em "raso" na definição que a A4 usou, e não tem milho 2ª safra nem rendimento ano a ano. É um gabarito de calendário e de nível de risco, não de perda.

## 6. Implicações para a solução
1. **Teste de aceitação do motor.** Para cada cultura, município, grupo e classe AD, o motor modular deve achar o mesmo primeiro decêndio ≤ 20% e o mesmo último decêndio indicado, com folga de 1 decêndio. Use `zarc_gabarito_sc.json`. Medida simples: acerto do nível (20/30/40/não indicado) por decêndio.
2. **Módulo de geada obrigatório em SMO.** Sem ele, o motor indica agosto (40% no ZARC, 63% de geada no POWER). Calibrar o limiar contra o ZARC, porque o POWER parece mais frio.
3. **Aveia só em maio–julho.** Não oferecer aveia fora da janela do ZARC (SMO 11/05–01/07; Ituporanga 01/06–21/07).
4. **Sorgo como seguro: só em solo realmente raso.** Ligar a regra à classe de água do talhão (AD1–AD3, até 41 mm em 60 cm). Para solos acima de 72 mm, o ZARC diz que o milho está no mesmo nível. Refazer a A4-3 com solo de 39 mm (GAEZ 65 mm/m x 0,6 m).
5. **2º milho: a regra de 01/02 está ao lado do ZARC.** Acrescentar sorgo forrageiro 2ª safra como opção quando a janela do milho fecha (até 21/01–01/03 em SMO e 01/02–11/03 em Ituporanga, conforme o grupo), depois de testar geada e água do sorgo.
6. **Cebola: o ZARC dá só calendário.** O motor pode checar a data de transplante contra a janela, mas o sinal de preço (B4) segue sendo a camada que muda decisão.
7. **Comunicar o nível em "x em 10".** Os 20/30/40% do ZARC viram 2/3/4 em 10; o motor deve usar a mesma escala para o agricultor reconhecer.

## 7. Limites
- Dicionário de dados do ZARC não baixou: dec1 = jan, grupos I/II/III = ciclos 20/21/22 e AD = solos 11–16 são inferências.
- Só a safra 2026/27 e só dois municípios; sem séries anteriores.
- ZARC tem 3 níveis. Isso limita testes finos de correlação.
- Sorgo e cebola: portarias de 315/2026 e 4/2024 não lidas; não sei os critérios de geada deles.
- Não verifiquei diferença de altitude do talhão nem de solo real; AD vem do mapa de solos do ZARC por município.
- Os gráficos são SVG simples feitos à mão.

## 8. Arquivos
- `CRITERIOS_ANTES.md`, `relatorio.md`, `tabelas.md`
- `zarc_gabarito_sc.json` (gabarito), `resultados_comparacao.json`, `extras_cebola_seq_irr.json`
- `gerar_gabarito.py`, `extras_e_graficos.py`, `tabelas_md.py`
- `v6_janelas_zarc.svg`, `v6_b1_geada_x_zarc.svg`, `v6_a4_milho_x_sorgo.svg`
- `ext/` (CSVs de entrada copiados da A1)
