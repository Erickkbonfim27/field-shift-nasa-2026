# Spec v2 da solução: motor modular de risco para escolher a rotação

Atualizada em 14/11/2026 (revisada no mesmo dia). Substitui a [spec v1](../spec-solucao.md) (Semiárido). Base: 10 fichas do loop (`loop-validacao/fichas/`) e 7 frentes de validação (`solucao/validacao/V1` a `V7`). **Isto é uma proposta para o time, não decisão do time.**

Arquivos desta spec:
- `solucao/spec-v2.md` (este).
- `solucao/contrato.schema.json`: JSON Schema da saída do motor (contrato v2.1.0).
- `solucao/exemplo_saida.json`: exemplo válido. São Miguel do Oeste, talhão raso, replay de 25/01/2022. É cópia da saída do motor.

---

## 0. Resumo
- **Promessa (igual à do controle):** usamos dados da NASA para transformar a incerteza do clima em probabilidades, para a família escolher a rotação com menos risco.
- **Como cumprimos agora:** um motor modular. Cada módulo responde a uma decisão. A região liga os módulos que passaram no teste dela.
- **O balanço hídrico sozinho não é o produto em SC.** Ele empata com a chuva bruta (ρ 0,28 contra 0,23 no milho de SMO; B1-0). Em SC, quem decide é a geada e o ano extremo.
- **Região principal:** Santa Catarina. Primeiro São Miguel do Oeste (leite e milho), depois Ituporanga (cebola).
- **Segunda região:** Semiárido do CE, PE e PB, só milho. Na mesma escala, Quixadá dá ρ 0,50 (chuva bruta 0,46) contra 0,28 de SMO (chuva 0,23) (V5). O ρ mediano 0,615 do milho em 6 municípios é um recorte feito depois de ver a Bahia falhar; o critério pré-registrado, com 16 pares, deu 0,414. Bahia fica fora.
- **Nenhum módulo chega ao nível "validado" (N3).** O mais forte é a geada que tira agosto da janela do milho (V4, critério D1), hoje N2: um ponto só, sem amostra nova; o limiar de 2 °C vem do próprio ZARC, que usa o POWER na ET0; a forma bate com o ZARC (40% em 1 e 11/ago) mas a magnitude não (63% de geada). O resto entra "com ressalva" ou "em teste". Isso é dito no produto.
- **Regra de dados, com duas exceções declaradas:** o cálculo de validação do alerta lê o IBGE PAM, mas só para a auditoria; e três parâmetros vêm de literatura fora da aba Resources (R = 0,88; raiz de 0,6 m do solo raso; limiar de geada de 2 °C). O time decide se aceita (P12).
- **Canais:** WhatsApp sem app (áudio, cartão de 10 sacos, texto) para o produtor. Frontend de auditoria para o técnico, com o rastro de cada número.
- **O LLM só transcreve, extrai campos fixos e lê o texto pronto.** Nenhum número sai dele.

---

## 1. Promessa, região e o que mudou

### 1.1 Promessa
> Usamos dados da NASA para transformar a incerteza do clima em probabilidades, para que a família agricultora escolha a rotação com menos risco de perder a safra.

- A unidade é "em quantos anos de 10 deu errado" (V4: trocar "chance de colher" por "em quantos anos de 10 houve quebra forte").
- O cartão nunca diz "vai dar certo" nem "faça X agora". Diz "em cerca de X de cada 10 anos (entre A e B)" e mostra a faixa. Fala sempre de anos ruins.
- A melhoria do solo (palha, nitrogênio, erosão) fica como texto com fonte e o selo "a validar". Não calculamos (V7).

### 1.2 Decisão de região
| Região | Papel | Por quê | Fonte |
|---|---|---|---|
| Extremo Oeste de SC (SMO) | **Principal, abre a demo** | Tem 3 estratégias com número, **de tipos diferentes e que não se comparam**: a atual só tem a guarda de agosto (geada); o 2º milho tem a chance de geada antes do corte (sem a água); a mistura tem a variação do pior ano em 10 e quantos cenários ajudam. Não é um ranking. Nenhum par tem o mesmo evento em "x em 10" | V7 `relatorio.md`; B1-1; A4-3; V3 |
| Alto Vale de SC (Ituporanga) | Principal, 2º cartão | Tem o solo exposto medido (A3-1) e o histórico do lugar. Não tem 3 rotações com número | V7; V1; V4 |
| Semiárido CE/PE/PB (Quixadá) | **Segunda região, só milho** | Balanço hídrico: Quixadá ρ 0,50 contra 0,28 em SMO (na mesma escala); os 4 critérios pré-registrados passaram, por pouco (mediana de 16 pares: 0,414) | V5 `relatorio.md`, `resultado.json` |
| Bahia (Irecê, Senhor do Bonfim) | **Fora** | ρ 0,07; a regra de início de chuva não planta em 16 e 24 de 41 anos | V5 |

Ressalvas do Semiárido (V5): bootstrap dá 60% de chance de ρ ≥ 0,40; o balanço não supera a soma de chuva (+0,06; +0,016 com "-" da PAM como perda total); feijão fraco (ρ 0,31). O 0,615 é a mediana do milho em 6 municípios do CE, PE e PB, **recorte feito depois de ver a Bahia falhar**; não se compara com o 0,28 de um município de SC.

### 1.3 O que mudou da v1
1. A região principal passou do Semiárido para SC.
2. O balanço hídrico deixou de ser o motor único. Virou um módulo entre vários.
3. O alerta de ano extremo trocou o limiar fixo pelo percentil da própria célula (V1).
4. A data de plantio vem em faixa, não num dia (V2).
5. Entrou o recorte por talhão: a mistura com sorgo só liga em talhão declarado raso (V3, V6).
6. Entrou o nível de evidência em cada número, e o WhatsApp obedece a ele.
7. Entrou a pergunta de prioridade do produtor. Ela muda a ordem dos cartões, nunca o cálculo (V7).

---

## 2. Níveis de evidência

| Nível | Nome | Regra para entrar | O que o produtor vê | O que o técnico vê |
|---|---|---|---|---|
| **N3** | Validado | Passou critério escrito antes, fora da amostra, e bate com fonte externa **independente** (que não use o mesmo dado nem o mesmo limiar) | Número inteiro em "x em 10" | Número, IC, rastro |
| **N2** | Com ressalva | Passou em parte, ou só na amostra, e a direção bate com fonte externa | Número com faixa **no mesmo cartão** e uma frase de limite | Tudo, mais "quebra se" |
| **N1** | Em teste | Hipótese testada sem passar, ou ainda sem teste | Só o nome e "ainda em teste" | Números com selo "em teste" |
| **N0** | Fora | Falhou ou contradiz a fonte externa | Nada | Só na lista de módulos fora |

Regras ligadas (contrato, seção 7): R4 amarra `nivel_evidencia` a `como_mostrar`. Um N1 nunca põe número no WhatsApp. Um número N2 que tem intervalo (`ic95` ou `faixa_parametros`) sai com a faixa no mesmo cartão (R4); o validador confere.

Número **medido** (um fato, não uma estimativa de risco) e sem intervalo, como o solo descoberto de Ituporanga (T10) e a fração de cenários da mistura (T07), sai sem faixa e com a frase do que não foi medido. A regra da faixa vale quando o número tem `ic95` ou `faixa_parametros`.

**Hoje nenhum módulo é N3.** A geada que tira agosto era N3 e foi rebaixada para N2 na revisão (ver seção 3).

---

## 3. Módulos: o que entra e com que evidência

| id | Módulo | Região | Dado (aba Resources) | Nível | Evidência (número e fonte) | Entra? |
|---|---|---|---|---|---|---|
| `agua_isna` | Água por fase (ISNA, FAO-56/33) | SC | POWER | **N1 em SC** (só insumo) | ρ 0,28 no milho de SMO, chuva dez–fev 0,23 (B1-0). Nenhum critério M1–M6 passou (V4) | Sim, só como insumo de outros módulos |
| `agua_isna` | Água por fase | Semiárido CE/PE/PB, milho | POWER | **N2** | Quixadá ρ 0,50 (chuva bruta 0,46), 5 de 8 piores anos; mediana de 16 pares 0,414; Garantia-Safra ρ −0,79, mas a chuva bruta dá −0,74 (V5). **O "16 de 18 decêndios do ZARC" é do caupi (N1), não entra como evidência do milho**: dentro da janela a ordem não bate (Spearman −0,07), a chuva média do decêndio bate mais (0,64) e um calendário ingênuo dá 12 de 18 | Sim, núcleo |
| `geada_janela_safra` | Geada no milho de verão (tira agosto) | SMO | POWER `T2M_MIN` | **N2** (era N3) | 6,3 e 4,6 falhas em 10 em 1 e 11/ago; só água daria 0,2 (V4, D1 pré-registrado, um ponto, veredito geral da V4: parcial). ZARC: 40% em 1 e 11/ago. **A forma bate com o ZARC, a magnitude não** (63% de geada contra 40% de risco total; V6). O limiar de 2 °C vem do ZARC (Portaria 236) e o ZARC usa o POWER na ET0. Calibrar o limiar: não feito (P11) | Sim, guarda |
| `geada_limite_2a_safra` | Data-limite de geada do 2º milho | SMO | POWER `T2M_MIN`, `T2M_MAX` | **N2** | Risco em 10: 21/jan 0,2; 1/fev 1,1 [0,5–2,3]; 11/fev 4,4 [3,1–5,9]. Limite 05/02 (risco no dia: 1,9 [1,0–3,2]), faixa 30/01 a 07/02 pelo limiar e 25/01 a 16/02 pelo ciclo. As mensagens dão a **data** ("até 5 de fevereiro"), não o terço do mês: "começo de fevereiro" cobre os dias 1 a 10, onde o risco vai de 1,1 a 4,0. Falha a estabilidade no espaço: Chapecó 30/01, Concórdia 07/01 (V2). ZARC: último milho 21/01 (V6) | Sim, por ponto e com faixa |
| `ano_extremo_seco` | Alerta de ano seco (10% mais secos da célula) | SC, milho | POWER | **N2** | **Regra que o motor roda (percentil só do passado, V1 passo 6):** 13 de 29 alertas em ano ruim (45%) contra 16%; 4 de 9 eventos, 2 de 6 novos; recall 48%; p = 0,078; **falha C1 e C3 da V1**. Com anos futuros no percentil (passo 4): 14 de 32, 4 de 11 eventos, 2 de 8 novos, recall 36%. A regra fixa ISNA < 0,75 caiu: 5 alertas em 288 anos-região, p = 0,24 (V1). O número de acerto usa o IBGE PAM: **só auditoria** | Sim, com o percentil só do passado e a ressalva de que pega pouco |
| `ano_extremo_excesso` | Alerta de excesso de chuva na cebola | Alto Vale | POWER | **N1** | Fora do Alto Vale: 11 de 49 = 22% contra 12,7%, p = 0,39. O 360 mm é o P90 de Ituporanga (V1) | Não como alerta. Só histórico medido (T09) |
| `mistura_talhao` | Metade da silagem em sorgo no talhão raso | SMO, talhão raso | POWER, GAEZ, SRTM (só "confirme") + literatura externa (R, raiz) | **N2** (CAD ≤ ~42 mm); N1 de 55 a 90 mm; desligado no fundo | **V3, CAD 42 mm:** P10 +39,6% (IC95 +30,7 a +57,1); média +7,3%; grade sobrevive em 68,5% (corte 70%); mediana da grade +14%, faixa −9% a +71%. **Motor, CAD 39 mm:** P10 central +46,9% (IC95 +31,1 a +60,8); média +8,0%; mediana da grade +15,4%, faixa −7,4% a +76,3%; grade sobrevive em 67,4%; ganho em 35 de 41 safras, perda de mais de 0,02 em 2. O central sobe cerca de 7 pontos com 39 mm. ZARC concorda só em AD2–AD3 (V6). O 65 mm/m é a classe areia do GAEZ aplicada ao raso, sem teste | Sim, só se o produtor declarar raso |
| `exposicao_solo` | Solo descoberto em mês de chuva forte | Ituporanga | Sentinel-2, SRTM, POWER | **N2 descritivo** (medido); benefício N1 | Erosividade do POWER: Spearman 0,85 com o pluviômetro; 64% dos talhões-ano com pico fora de out–fev; p90/p10 = 9 (A3-1) | Sim, como fato medido. Perda de solo evitada não é calculada |
| `enso_tipo_risco` | El Niño troca o tipo de risco | SMO | ERA5 (a fazer) | **N1** | Passou com folga pequena (BSS 0,060 contra 0,05), mas usou o ONI da NOAA, fora da aba (A2-4) | Não, até o Niño 3.4 vir do ERA5 |
| `preco_cebola` | Regra de venda pela chuva da primavera | Ituporanga | POWER (+ preço externo na calibração) | **N1** | Pré-registro falhou: ρ −0,11; preço IBGE −4% (B4-1). B4-3 passou em parte: \|ρ\| 0,397 | Não. Só auditoria, marcado "mercado" |
| `sorgo_2a_safra` | Sorgo forrageiro depois do milho | SMO | POWER | **N1** | Sem teste próprio. ZARC indica até 01/03 (grupo I) em SMO (V6) | Só como "em teste" |
| `data_transplante_cebola` | Data de transplante da cebola | Ituporanga | POWER | **N0** | O motor prefere setembro; o ZARC não dá 20% em nenhuma linha a partir de 11/set (V4, D2 falhou) | Não |

**Parâmetros de literatura externa** (exceção à regra de dados, cada um com item `R-PARAM-*` no rastro): R = 0,88 (Embrapa Gado de Leite; Demarchi; V3 seção 2.1), raiz de 0,6 m do solo raso (ZARC, Portaria 236) e limiar de geada de 2 °C (ZARC, Portaria 236). O time decide se aceita (P12).

**Como os módulos se combinam.** Pesos fixos, escritos antes, sem ajuste. O motor ajustado (ridge, 6 variáveis) perdeu para a climatologia no milho (SS −0,08; V4). Cada módulo dá o seu número, com o seu evento. O motor não soma módulos num índice único.

**Região liga e desliga** (`regiao.modulos_ativos` no contrato):
- `sc_extremo_oeste`: `geada_janela_safra`, `geada_limite_2a_safra`, `ano_extremo_seco`, `mistura_talhao` (se raso), `agua_isna` (insumo), `sorgo_2a_safra` (em teste).
- `sc_alto_vale`: `exposicao_solo`, `ano_extremo_excesso` (só histórico), `agua_isna` (insumo).
- `semiarido_ce_pe_pb`: `agua_isna` (núcleo, milho).

---

## 4. Estratégias por caso (3 ou mais, com a atual)

Regra: toda comparação tem a atual. Quem não tem número aparece com o nome e "em teste".

### 4.1 São Miguel do Oeste: leite e milho (caso da demo)
Pergunta da família: "colhi a silagem em janeiro: 2º milho, pasto ou outra coisa?" (V7).

| # | Estratégia | Sequência | Número principal | Nível | Fonte |
|---|---|---|---|---|---|
| E1 | **O de sempre** | Milho silagem (set–out) → pasto de inverno | Guarda: não plantar em agosto (geada em 6,3 de 10 anos em 1/ago, IC95 4,8 a 7,6). De 21/set a 21/dez a data muda menos de 1 em 10. Na mensagem T01 aparece **sem número**, como ponto de partida | N2 (guarda; era N3) | V4 `v4_resultado.json` `decisao_D1_data_milho_SMO` |
| E2 | **Segundo milho** | Milho silagem → 2º milho até 5 de fevereiro | Geada antes do corte da silagem, **sem a falta de água**: 1,9 em 10 no dia-limite (5/fev; IC95 1,0 a 3,2); 1,1 em 10 em 1/fev; 4,4 em 10 em 11/fev | N2 | V2 `v2_resultado.json` `tabela_decendio` L3 |
| E3 | **Metade em sorgo** (só talhão raso) | 50% milho + 50% sorgo → pasto de inverno | **Um tipo de número diferente:** variação do pior ano em 10 (motor, 39 mm: mediana da grade +15,4%, faixa −7,4% a +76,3%; V3, 42 mm: +14%, −9% a +71%) e quantos cenários ajudam (67,4%, "7 em cada 10"). Só o segundo vai ao WhatsApp | N2 | V3 `res_02_central_grade.json` |
| E4 | Sorgo depois do milho | Milho silagem → sorgo forrageiro 2ª safra | Sem número | N1 | V6 |

**Os números das estratégias não se comparam.** E1 é uma guarda de data (geada em agosto, que o "de sempre" de set–out nem usa). E2 é a chance de geada, sem a água. E3 é a variação percentual do pior ano em 10. Não há um evento comum em "x em 10" para as três (por exemplo, falta de silagem). Dizer isso no pitch; não montar ranking.

O que não sabemos e dizemos: a falta de água do 2º milho não foi calculada (V2; as mensagens T01 e T04 dizem). O risco de geada é chance de evento, não perda. No solo raso de 87,5 mm da A4 a mistura rende menos em 15 de 41 safras (cerca de 1 em 3). **No talhão da demo (39 a 42 mm) rende menos em só 2 de 41** e mais em 35 (V3; motor com 39 mm).

### 4.2 Ituporanga: cebola
| # | Estratégia | Sequência | Número | Nível | Fonte |
|---|---|---|---|---|---|
| I1 | **O de sempre** | Preparo convencional no inverno, transplante jul–ago, venda na colheita | Solo descoberto: fração média de 0,29 dos dias de julho na lavoura do recorte. Histórico: o motor marca 5 primaveras de chuva extrema em 42 anos; 3 tiveram quebra (2008, 2015, 2023) | N2 (solo, medido); N1 (histórico) | A3-1 `a3_1_resultado.json`; V4 seção 3.4 |
| I2 | Milho no verão e cebola em plantio direto sobre a palha | Milho verão → cebola em plantio direto | Sem número de benefício. O motor não distingue o risco climático de I1 | N1 | A3-1; dissertação UDESC citada na A3-1 (só mecanismo) |
| I3 | Guardar parte para vender em mar–abr | I1 + venda escalonada | Alta ≥ 15% em 75% das safras, com preço da Epagri (externo) | N1, só auditoria, marcado "mercado" | B4-3 |

**Ituporanga não fecha 3 rotações com número.** Dizer isso no pitch. O cartão do produtor mostra o solo exposto (T10) e, na auditoria, o histórico.

### 4.3 Quixadá: milho no Semiárido (uma linha no pitch)
| # | Estratégia | Boa colheita em 10 anos (2001–2025) | **Quebra em 10 anos (o que a mensagem diz)** | Nível | Fonte |
|---|---|---|---|---|---|
| Q1 | **O de sempre:** milho na 1ª chuva firme | 6,4 [4,5–8,0] | 3,6 [2,0–5,5] → "4 de cada 10" | N2 | `prototipo/dados/resultado.json` (A) |
| Q2 | Milho em data fixa no 2º decêndio de fevereiro | 8,0 [6,1–9,1] | 2,0 [0,9–3,9] → "2 de cada 10" | N2 | idem, `janelas_milho` |
| Q3 | Caupi de ciclo curto na 1ª chuva | 7,6 | — | N1 (feijão fraco: ρ 0,30 em Quixadá) | idem (C); V5 |
| Q4 | Sorgo na 1ª chuva | 8,8 | — | N1 (Ky genérico; hipótese) | idem (D); `prototipo/README.md` |

**Polaridade:** o WhatsApp e o cartão de 10 sacos falam sempre de anos ruins ("quebra" = colher menos de 6 sacos em cada 10 possíveis). A coluna "boa colheita" é só da auditoria.

Q2 contra Q1 é 1,6 em 10 (cerca de 4 anos em 25), e os IC95 se sobrepõem. Com n = 25, a mensagem diz "tende a ser melhor, mas não é certo". O T12 (prioridade) não sai em Quixadá.

---

## 5. Canais

### 5.1 WhatsApp sem app, para o produtor
**Entrada:**
- Áudio curto (principal). Texto também vale.
- Localização (pin). Define a célula do POWER.
- Foto: só registro, com data e lugar (`talhao.fotos_registro[].uso = "registro"`). Sem diagnóstico.
- Respostas a perguntas fechadas: solo (T15) e prioridade (T12).

**Saída, nesta ordem:**
1. Imagem-cartão (10 sacos, barras ou janela).
2. Áudio curto (até 30 a 35 s), lendo `cartoes[].audio.roteiro`.
3. Texto (`cartoes[].texto`, até 70 palavras).

**Fluxo:**
```
áudio ─► [1] STT (transcrição pt-BR)
        [2] Extração para campos fixos (JSON com enums):
            intencao, cultura, data_colheita, solo, prioridade
        [3] Motor (determinístico) ─► JSON do contrato v2
        [4] Renderizador (código): template + variáveis do JSON
        [5] Verificador de números (regra R8)
        [6] TTS lê o roteiro; gerador desenha o cartão
        [7] Envia imagem + áudio + texto; grava o id da saída
```

**O que o LLM faz:** passos 1 e 2 (transcrever e encaixar em enums) e a leitura em voz (6).
**O que o LLM não faz:** calcular, escolher número, reescrever cartão, responder fora dos templates.
- No passo 2, temperatura 0 e saída validada por schema. Campo que falta vira pergunta fechada (T12, T15).
- Se o verificador do passo 5 achar um número sem origem, a mensagem é bloqueada e sai T14 ("não sei").
- Pergunta sobre praga, doença, adubo ou preço: T14 e encaminha ao técnico.

**Demo:** WhatsApp simulado numa página. O número oficial da Meta leva dias (spec v1, Q5). O WhatsApp não é diferencial: RAImundo (Embrapa) e JoIA (CNA/Senar) já usam áudio e foto (V7). O motor pode responder dentro desses bots por API.

**Ordem dos cartões pela prioridade** (`produtor.prioridade`; regra R9, só ordem):
- `silagem_garantida`: alerta ativo → estratégia que melhora o pior ano → estratégia que dá mais silagem → atual → em teste.
- `renda`: alerta ativo → estratégia que dá mais área colhida no ano (2º milho) → atual → mistura → em teste.
- `solo`: alerta ativo → estratégias com `solo_texto` → atual → resto.
- `nao_informado`: ordem de `estrategias[].ordem` do motor, e manda T12.

### 5.2 Frontend de auditoria, para o técnico e extensionista
Lê só o JSON do contrato. Não calcula nada.

Telas:
1. **Conversa espelhada.** A mensagem que o produtor recebeu, com cada número sublinhado.
2. **Painel do número** (clique no número). Mostra:
   - valor, IC95 (amostragem), faixa de parâmetros, n de anos, período;
   - nível de evidência e módulo;
   - premissas e "quebra se";
   - cadeia de rastro: dado → parâmetro → cálculo (`script.caminho`, `script.funcao`, `resultado.arquivo`, `resultado.chave`);
   - conferências em outra cor, com o selo "conferência, não entrada".
3. **Estratégia por decêndio.** Tabela e gráfico de `risco_por_decendio.linhas`, com a coluna do ZARC ao lado. ZARC na escala 20/30/40% = 2/3/4 em 10 anos (V6).
4. **Módulos da região.** Ativo, nível, validação e "o que não vê".
5. **Limites.** `limites[]`, com os de `gravidade = alta` no topo.
6. **Fila do técnico.** Mensagens "não sei", fotos e o pedido "confirme o solo" do SRTM.

O que o técnico pode fazer: confirmar ou trocar o solo declarado. Isso pede um novo cálculo ao motor. Ele **não edita números**.

---

## 6. Templates do WhatsApp

Regras para todos:
- pt-BR simples, até 70 palavras, frases curtas.
- `{variavel}` vem de `cartoes[].variaveis`, que aponta (JSON Pointer) para o campo de origem.
- Números do próprio template (o "10" de "em 10", o "1 vez a cada 10", o "6 sacos" de Quixadá, as opções 1 a 3 do T12) ficam numa lista de constantes do template. Qualquer outro número precisa de variável (R8).
- **A pergunta vem primeiro.** Cada mensagem abre com a resposta curta ("Sim, este ano está seco", "Ainda não", "Segundo milho (aveia não calculada): plante até 5 de fevereiro").
- **Sempre anos ruins.** A frequência é "x de cada 10 anos" de quebra, geada ou seca; nunca "boa colheita" num lugar e "quebra" em outro. O número de cada saco rasgado aparece no texto (R7).
- **Termos do campo.** "Corte da silagem" (milho pronto para cortar), "semente de ciclo longo (que demora mais)", "quebra é colher menos de 6 sacos em cada 10 possíveis". Sem "SC", "ponto de silagem", "excedente", "mar-abr". Sem sigla nem porcentagem de modelo (88%, 15%, 76%).
- Arredondamento (R7): "x em 10" vai para inteiro, meio para cima. Entre 0 e 0,5: "menos de 1 em 10". Zero: "quase nunca" (nunca "nunca"). Porcentagem vai para inteiro; negativo vira "X% a menos". Número N2 com intervalo leva "em cerca de X de cada 10 anos (entre A e B)". A data-limite do 2º milho vai como data ("5 de fevereiro"). "Começo (1–10), meados (11–20) ou fim (21–31) de {mês}" só vale para um decêndio inteiro (Quixadá).
- Sacos: `rasgados = round(em10)`, `cheios = 10 − rasgados`. N1 sem sacos.
- Frases opcionais, só se couberem em 70 palavras: "Dados de satélite, área de {km} km." (limite X-GRADE) e "Fale com o técnico da assistência técnica do seu município antes de decidir." (T01 com caminhos em teste). Quando não cabem, a variável sai do cartão.

| id | Quando | Texto (com variáveis) | Imagem |
|---|---|---|---|
| **T01_COMPARA_ESTRATEGIAS** | Pedido de comparação, ou depois da colheita do verão | "{quantos} caminhos para a {talhao}. {e_a}: {frase_a}. {e_b}: {frase_b}. … Em teste: {nomes}." `quantos` por extenso. Cada `frase_*` sai da tabela de frases abaixo. Máximo de 4 caminhos; o resto só na auditoria | 10 sacos (SMO, Quixadá) |
| **T02_GEADA_JANELA_SAFRA** | Planejamento do milho de verão (vale qualquer data; a UI mostra na pergunta de data) | "Milho de verão: aqui, não plante em agosto. Plantando em 1º de agosto, a geada pegou a lavoura nova em cerca de {r_ago} de cada 10 anos (entre {lo} e {hi}). A partir de {data_segura}, quase nunca. Do fim de setembro a dezembro, para o clima, a data quase não muda o risco." | Janela por decêndio |
| **T03_TANTO_FAZ_DATA** | Pergunta de data quando as linhas diferem menos de 1 em 10 | "Entre {de} e {ate}, para o clima, a data de plantio quase não muda o risco: a diferença é menor que 1 ano em 10. Escolha pela mão de obra e pela máquina." | Nenhuma |
| **T04_GEADA_LIMITE_2A_SAFRA** | Pergunta do 2º milho | "Segundo milho (aveia não calculada): plante até {limite}. Nesse dia, a geada chega antes do corte da silagem em cerca de {r_lim} de cada 10 anos (entre {lo} e {hi}). Em {data_tarde}, em cerca de {r_tarde} de cada 10 anos (entre {lo_t} e {hi_t}). Semente de ciclo longo (que demora mais): plante antes. Não calculamos a falta de água. Dados de satélite, área de {km} km." | 10 sacos |
| **T05_ANO_SECO_ATIVO** | `alertas[].estado = ativo` (seco) | "Sim, este ano está seco. De {inicio} a {fim}, a água para o milho ficou entre os 10% piores dos últimos {n_anos} anos aqui. Não é certeza, e o aviso não pega todos os anos ruins. Vale conferir o estoque de silagem e falar com o técnico da assistência técnica. Dados de satélite, área de {km} km." `fim` é o fim que o índice usou (a data de referência, se vier antes de 10/jan). **Sem número de acerto**: o "4 em 10" vem do IBGE PAM e fica na auditoria | Nenhuma |
| **T06_ANO_SECO_SILENCIO** | Alerta inativo e o produtor pergunta | "Ainda não. Até agora, a água para o milho está dentro do normal dos últimos {n_anos} anos aqui. Mas o aviso não pega todos os anos ruins: nos testes, ele deixou passar muitas quebras. Continue de olho na lavoura. Dados de satélite, área de {km} km." | Nenhuma |
| **T07_MISTURA_TALHAO_RASO** | `mistura_talhao` ativo | "Na {talhao}, que você disse ser rasa: plantar metade da silagem com sorgo pode ajudar no ano ruim, desses que vêm 1 vez a cada 10. A conta não é firme: a mistura ajudou em {s} de cada 10 cenários que testamos. Em ano bom, ela pode render um pouco menos. Fale com o técnico antes de decidir." `s` = cenários da grade em que o ganho se mantém (67,4% → 7). Sem porcentagem de silagem | Nenhuma (as barras saíram: índice sem unidade) |
| **T08_EM_TESTE** | Não sai mais sozinho. Os caminhos em teste vão dentro do T01 ("Em teste: …") | "{nome}: ainda estamos testando. Por enquanto não temos um número confiável para o seu lugar. Fale com o técnico da assistência técnica do seu município antes de decidir." | Nenhuma |
| **T09_CEBOLA_HISTORICO** | Só auditoria (N1) | "Cebola em {municipio}. Nos últimos {n} anos, as primaveras com mais chuva aqui foram {anos}. Chuva demais na formação do bulbo prejudica a cebola. Isso é o histórico do lugar, calculado com dados de satélite. Não é previsão para este ano." | Nenhuma |
| **T10_SOLO_EXPOSTO** | Ituporanga, fim do inverno | "No último inverno, o solo do talhão {talhao} ficou descoberto em {pct}% dos dias de {meses}, quando a chuva já é forte. Palha ou cobertura nessa época protege o solo. Quanto solo isso salva, ainda não medimos. A chuva é medida numa área de {km} km." | Nenhuma |
| **T11_SEMIARIDO_JANELA_MILHO** | Quixadá, milho | "Milho em {municipio}. Na primeira chuva firme, deu quebra em cerca de {q_atual} de cada 10 anos (entre {lo_a} e {hi_a}). Plantando em {janela}, deu quebra em cerca de {q_janela} de cada 10 anos (entre {lo_j} e {hi_j}). Só {n} anos de dados: tende a ser melhor, mas não é certo. Se a chuva não firmar, espere. Quebra é colher menos de 6 sacos em cada 10 possíveis." | 10 sacos |
| **T12_PRIORIDADE** | Prioridade não informada (SC; **não sai no Semiárido**) | "Para organizar as opções: o que pesa mais para você agora? Responda 1 para colheita mais segura, 2 para renda, 3 para cuidar do solo." | Nenhuma |
| **T13_FOTO_REGISTRO** | Chegou foto | "Recebi a foto do talhão {talhao}. Ela fica guardada como registro, com data e lugar. Eu não analiso doença nem praga pela foto. Para isso, fale com o técnico." | Nenhuma |
| **T14_NAO_SEI** | `nao_sei.ativo`, ou o verificador bloqueou | "Isso eu não sei responder com segurança: {motivo}. Vou avisar o técnico para falar com você." | Nenhuma |
| **T15_PEDE_SOLO** | `solo_declarado = nao_sei`, ou SRTM pede "confirme" | "Para calcular, preciso saber como é a terra do talhão {talhao}. Responda: 1 arenosa, 2 média, 3 argilosa, 4 rasa ou com pedra, 5 não sei." | Nenhuma |

Frases do T01 por módulo (uma por caminho, sempre anos ruins):
| Módulo | Frase |
|---|---|
| `mistura_talhao` | "ajudou em {s} de cada 10 cenários testados" |
| `geada_limite_2a_safra` | "plantando até {limite}, a geada chega antes do corte em cerca de {r} de cada 10 anos (entre {lo} e {hi}); não calculamos a falta de água" |
| atual (SMO) | "{nome_falado}, sem número" |
| atual (Ituporanga) | "no último inverno, o solo ficou descoberto em {pct}% dos dias de {meses}" |
| `agua_isna` (Semiárido) | "quebra em cerca de {q} de cada 10 anos (entre {lo} e {hi})"; o atual leva "({nome_falado})" |
| N1 | entra na lista final "Em teste: …", sem número |

Variáveis dos templates usados no exemplo (`exemplo_saida.json`, `cartoes[]`):
| Template | Variável | Ponteiro |
|---|---|---|
| T05 | `inicio`, `fim` | `/alertas/0/janela/de` e `/alertas/0/janela/ate` |
| T05 | `n_anos` | `/alertas/0/percentil_local/n_anos_passados` |
| T05, T04 | `km` | `/local/ponto_power/resolucao_km` |
| T04 | `limite` | `/estrategias/1/indicadores/0/valor` |
| T04 | `r_lim`, `lo`, `hi` | `/estrategias/1/indicadores/1/valor` e `/ic95/0`, `/ic95/1` |
| T04 | `r_tarde`, `lo_t`, `hi_t` | `/estrategias/1/risco_por_decendio/linhas/4/em10` e `/ic95/0`, `/ic95/1` |
| T07 | `s` | `/estrategias/2/indicadores/3/valor` (cenários que sobrevivem, 67,4) |

O exemplo (SMO) traz T01 a T05 e T07. T09, T10 e T11 estão nas saídas de Ituporanga e Quixadá; T06 e T12 a T15 aparecem nos testes. O T08 não sai mais sozinho. O renderizador deve tratá-los todos do mesmo jeito.

---

## 7. Contrato de dados do motor

### 7.1 Quem escreve e quem lê
- **Motor:** escreve um JSON por (local, talhão, data de referência). Valida contra `contrato.schema.json` antes de entregar.
- **WhatsApp:** lê `cartoes[]` com `destino = whatsapp`, na ordem de `ordem`.
- **Auditoria:** lê tudo.
- Os dois times começam agora pelo `exemplo_saida.json`. O motor substitui o exemplo pela saída real, sem mudar a forma.

### 7.2 Estrutura (resumo do schema)
| Campo | O que guarda |
|---|---|
| `versao_contrato`, `gerado_em`, `modo`, `data_referencia`, `safra`, `motor` | Cabeçalho. `modo = replay` para safra passada (demo) |
| `local` | Município, código IBGE, coordenada, célula do POWER (~50 km) e municípios na mesma célula |
| `talhao` | Solo declarado, CAD (mm) com fonte, SRTM ("confirme", N1), ciclo em °C·dia, data da colheita do verão, fotos (só registro) |
| `produtor` | Id pseudônimo (sem nome, sem telefone), prioridade, atividade |
| `regiao` | Região e módulos ativos |
| `modulos[]` | Cada módulo: ativo, nível, papel, motivo, validação (ficha e caminho), o que não vê |
| `estrategias[]` | 3 ou mais; uma `e_atual`. Sequência de culturas, indicadores, risco por decêndio, premissas, "quebra se", o que não foi calculado, texto de solo "a validar" |
| `estrategias[].risco_por_decendio.linhas[]` | Decêndio, `em10`, IC95, k/n, componentes (água, geada, ano extremo), métricas extras, ZARC (só conferência) |
| `alertas[]` | Estado, janela (vai até o corte que o índice usou), índice, percentil local (só anos passados), frase de probabilidade (**só auditoria**), recall, `silencio_nao_e_seguranca = true` |
| `cartoes[]` | Template, variáveis com ponteiro, texto pronto, contagem de palavras, imagem, roteiro do áudio |
| `rastro[]` | Itens de dado, parâmetro, cálculo, pergunta e conferência. Cálculo tem script, entradas e arquivo de resultado |
| `conferencias[]` | Comparação com ZARC, PAM, Epagri, Garantia-Safra |
| `limites[]` | Texto, gravidade, o que afeta, se vai ao produtor e, se vai, o `trecho` exato que está num cartão (v2.1.0) |
| `nao_sei` | Se a resposta é "não sei", por quê e para quem encaminhar |

### 7.3 Regras que o schema garante
- Fonte com `categoria = externo_conferencia` (ZARC, IBGE, Epagri…) só pode ter `tipo = conferencia`. Não entra como dado nem parâmetro.
- Fonte com `categoria = literatura_externa` (v2.1.0) só pode ter `tipo = parametro`. É a exceção declarada para R, raiz do solo raso e limiar de geada.
- Item de rastro `tipo = calculo` exige `script`, `entradas` e `resultado`.
- `em10` entre 0 e 10. Decêndio no formato `dd/mm` com dia 01, 11 ou 21.
- No mínimo 3 estratégias. Cartão com no máximo 75 palavras declaradas (o limite de produto é 70; R11). Limite com `trecho` opcional (obrigatório quando vai ao produtor, R14).
- Produtor sem nome, só `P-` + 8 hexadecimais.

### 7.4 Regras que o validador do motor precisa checar (fora do schema)
| Regra | O que checa |
|---|---|
| R1 | Todo id em `rastro`, `entradas`, `estrategia_ids` e todo ponteiro de variável existe no documento |
| R2 | (a) ZARC, PAM e afins nunca aparecem nas `entradas` de um cálculo do produto, direta ou indiretamente. Exceção: cálculo de validação marcado `parametros.so_auditoria = true` (ex.: `R-CALC-ALERTA-VALID`). (b) Nenhuma variável de cartão do WhatsApp chega, **seguindo o ponteiro e os campos `rastro` de todos os nós do caminho**, a uma fonte externa nem a um cálculo de validação. (Antes a regra pulava todo id com "-VALID" e não seguia os ponteiros: o T05 levava um número do IBGE PAM ao WhatsApp e passava.) (c) `literatura_externa` só como `parametro` |
| R3 | Exatamente uma estratégia com `e_atual = true` |
| R4 | N3 → `com_numero` ou `com_faixa`; N2 → `com_faixa`; N1 → `so_nome_em_teste`; N0 → `oculto`. Mais: variável de cartão do WhatsApp que aponta para um número N2 com `ic95` ou `faixa_parametros` exige, no mesmo cartão, variáveis que apontem para esse intervalo (o texto traz "entre A e B") |
| R5 | Em todo intervalo, inferior ≤ superior |
| R6 | `percentil_local` usa só anos anteriores à safra da `data_referencia` |
| R7 | Arredondamento e sacos como na seção 6; `cheios + rasgados = 10`; o número de cada saco rasgado aparece nas variáveis do texto (mesma polaridade) |
| R8 | Todo número do `texto` vem de uma variável ou da lista de constantes do template |
| R9 | `produtor.prioridade` só muda `ordem`; os números são iguais para qualquer prioridade |
| R10 | `regiao.modulos_ativos` = módulos com `ativo = true` |
| R11 | `palavras` = contagem real do `texto`, e no máximo 70 |
| R12 | Fora da área testada (`local.dentro_da_area_testada = false`) → `nao_sei.ativo = true` e nenhum cartão com número |
| R13 | Vírgula decimal em todo texto de módulos, estratégias, limites e conferências (nada de "39.0 mm" ou "1.6 em 10") |
| R14 | Limite com `mostrar_ao_agricultor = true` tem `trecho`, e o trecho aparece, igual, no texto de um cartão do WhatsApp |
| R15 | Alerta ativo ou inativo: o fim da janela (`janela.ate`) é o fim que o índice usou (a data aparece em `indice.nome`) |

O validador está em `solucao/motor/validador.py` (schema e R1 a R15) e tem testes negativos para cada regra (`motor/tests/test_contrato.py`). O exemplo e as 3 saídas passam.

### 7.5 API mínima
- `POST /motor/v2/avaliar` com `{local: {lat, lon}, talhao: {solo_declarado, ciclo_gdd?, colheita_verao?}, produtor: {prioridade, atividade}, data_referencia, modo}`. Devolve o JSON do contrato.
- `GET /motor/v2/saidas/{id}` devolve uma saída gravada. A auditoria usa esta rota.

### 7.6 O exemplo (`exemplo_saida.json`)
- São Miguel do Oeste, talhão "Encosta de cima", declarado raso. CAD de 42 mm.
- Replay de 25/01/2022, safra 2021/22, logo depois da colheita do verão.
- 4 estratégias (E1 atual, E2, E3, E4 em teste), 1 alerta ativo, 6 cartões, 29 itens de rastro, 5 conferências e 17 limites. O arquivo é **cópia da saída do motor** (`saida/sao-miguel-do-oeste.json`); a versão escrita à mão ficou desatualizada.
- Alerta: o ISNA de 20/set a 10/jan de 2021/22 é 0,618. Fica abaixo de todos os 32 anos de 1990 a 2021 (mínimo 0,677, em 2009). O percentil só do passado tem script (`motor/ano_extremo.py`, `percentil_passado`).
- Conferência: a PAM da microrregião 42001 dá 0,658 da mediana em 2022 (`V1/tabela_original.json`, campo `rel`). A safra 2021/22 já estava na amostra da B3: não conta como teste novo. A Epagri/Cepa estimou perda média de 43% no milho de SC (ficha A1-1).

---

## 8. Ordem de construção e aceitação

O prazo é 15/11 às 23h59 locais. A demo tem até 7 slides ou 30 s, em inglês (V7, guia de submissão).

**Motor (em paralelo com a UI):**
1. Embrulhar os scripts que já existem em módulos que devolvem pedaços do contrato:
   - `geada_janela_safra` ← `V4/v4_motor.py` (`safra_milho`);
   - `geada_limite_2a_safra` ← `V2/v2_geada.py` (`curva`, `limite_diario`);
   - `ano_extremo_seco` ← `V1/v1_comum.py` (`ind_milho`) + percentil só do passado (novo);
   - `mistura_talhao` ← `V3/modelo_v3.py` (`casos`, `mistura`, `resumo`);
   - `agua_isna` Semiárido ← `V5/motor.py` (cópia fiel de `risco.py`).
2. Montar o JSON, gerar os cartões pelos templates e validar (R1–R15).
3. Gravar cada saída com id.

**UI (começa já, com o exemplo):**
1. WhatsApp simulado: cartão (10 sacos ou barras), áudio (TTS do roteiro) e texto.
2. Auditoria: telas 1 a 5 da seção 5.2. A tela 6 pode ficar para depois.

**Testes de aceitação:**
| # | Teste | Passa se |
|---|---|---|
| A1 | Schema e R1–R15 | O exemplo e toda saída real passam |
| A2 | Reproduz as frentes | E2 = `V2/v2_resultado.json` L3; E1 geada = `V4` D1; E3 = `V3` central; ISNA 2021/22 = 0,618 |
| A3 | Gabarito ZARC de SC (`V6/zarc_gabarito_sc.json`) | 1º decêndio com risco ≤ 2 em 10 até 1 decêndio do 1º com 20% no ZARC (hoje: 01/09 contra 21/08); último plantio do 2º milho até 20 dias do último do ZARC (hoje: 05/02 contra 21/01, 15 dias) |
| A4 | Semiárido | Reproduz o `risco.py` (V5: 48 de 48 pares). O "16 de 18 decêndios do ZARC" é do caupi (N1) e vem com a linha de base ingênua (12 de 18) e a ordem dentro da janela (Spearman −0,07); não é critério do milho |
| A5 | Testes negativos | Fonte externa como `dado` falha; N1 com número no WhatsApp falha; número solto no texto falha |
| A6 | Não sei | Ponto fora de SC e do CE/PE/PB, ou na Bahia, devolve T14 sem número |
| A7 | UI | Toda pergunta de `ui/comum.js` acha um cartão do WhatsApp na saída do local (`test_toda_pergunta_da_ui_tem_cartao`) |
| A8 | Rastro dos cartões | Nenhuma variável de cartão do WhatsApp chega a fonte externa nem a cálculo de validação (R2b) |

---

## 9. O que NÃO afirmar no pitch

1. **"O alerta de ano extremo foi validado fora da amostra."** A V1 derrubou a B3-3: os limiares 0,75 e 360 mm vieram dos extremos da amostra, e B3-3 não tinha evento novo. A regra relativa, com o percentil só do passado (a que roda), dá 13 de 29 alertas em ano ruim (45% contra 16%), mas só 4 de 9 eventos e 2 de 6 novos, e **falha C1 e C3 da V1**. Pega pouco (recall 48%).
2. **"O motor prevê a produtividade do ano."** ρ 0,28 no milho de SMO, igual à chuva bruta (B1-0). O motor ajustado perde da climatologia (SS −0,08; V4).
3. **"Nosso balanço hídrico é melhor que olhar a chuva."** Em SC empata. No Semiárido a diferença é +0,06, dentro do ruído (V5).
4. **"Usamos IMERG e SMAP."** Não usamos. Pedem login Earthdata e não foram testados. Nos módulos que passaram, os dados da aba são POWER, SRTM e Sentinel-2, e só os dois primeiros são da NASA (V7). A tabela de água por textura do GAEZ entra como parâmetro.
5. **"Damos a data exata de plantio para a região."** A data-limite muda 29 dias entre SMO e Concórdia e 22 dias com o ciclo (V2).
6. **"O risco de geada é o risco de perder a silagem."** É a chance de geada antes do ponto (V2).
7. **"O sorgo é um seguro comprovado" ou "validado com produtividade".** A PAM não confirma (Spearman 0,10 a 0,33), não há dado de sorgo em SMO e o ganho some se o Ky do sorgo for 1,5 a 1,64 vez o da FAO (V3).
8. **"O satélite mede a profundidade do solo."** O SRTM só pede para confirmar. Erra o Neossolo Litólico de topo (V3).
9. **"Prevemos o clima da safra" ou "2026/27 é ano de El Niño".** A aba Resources não tem previsão sazonal. O módulo de El Niño está em teste e usou dado da NOAA, fora da aba (A2-4).
10. **"Calculamos o ganho da rotação no solo."** Palha, nitrogênio e erosão evitada não foram medidos (A3-1, V7).
11. **"A regra de venda da cebola funciona."** O pré-registro falhou (B4-1) e o preço é fonte externa.
12. **"Dizemos a melhor data de transplante da cebola."** O motor contradiz o ZARC (V4, D2).
13. **"O alerta de cebola vale para SC."** Fora do Alto Vale: 22% contra 12,7%, p = 0,39 (V1).
14. **"Se não teve alerta, o ano é seguro."** O alerta perde cerca de metade dos anos ruins (52%, percentil só do passado; V1 passo 6).
15. **"Concordar com o ZARC prova que o motor é bom."** Os 94% da A1-1 empatam com o calendário ingênuo (94%). O ZARC é norma de seguro, e usa o próprio POWER na ET0 (V6).
16. **"Funciona em todo o Semiárido."** Bahia: ρ 0,07 (V5).
17. **"O Garantia-Safra prova o modelo."** A chuva bruta dá quase o mesmo (−0,74 contra −0,79), e a série é agregada nacional (V5).
18. **"A IA decide" ou "o LLM calcula".** O LLM só transcreve, extrai campos e lê o texto pronto. A ideia veio do time; declarar o uso de IA no código, na pesquisa e no TTS (regras do Space Apps, V7).
19. **"Resolução de talhão no clima."** A grade do POWER tem cerca de 50 km.
20. **"Usamos ZARC ou IBGE como entrada."** Só como conferência.
21. **"Ganho em reais."** Não calculamos dinheiro.
22. **"Testado com agricultores."** Não houve teste com usuário.
23. **"Nossa novidade é o WhatsApp."** RAImundo e JoIA já fazem (V7). A novidade é compor a sequência por talhão, com nível de evidência e rastro de cada número.
24. **"Ituporanga tem 3 rotações comparadas com número."** Não tem (V7).
25. **"A geada que tira agosto é validada (N3)."** É N2: um ponto, limiar do ZARC, magnitude que discorda, limiar não calibrado.
26. **"Concordar com o ZARC em 16 de 18 decêndios prova o milho do Semiárido."** O número é do caupi, e um calendário ingênuo dá 12 de 18.
27. **"O Semiárido tem ρ 0,615 contra 0,28 de SC."** O 0,615 é um recorte feito depois de ver a Bahia falhar. Na mesma escala é 0,50 contra 0,28.
28. **"As três estratégias de SMO se comparam."** Cada uma tem um tipo de número (guarda de data, chance de geada sem água, variação do pior ano). Não há ranking.
29. **"Só usamos dados da aba Resources."** Três parâmetros vêm de literatura externa (R = 0,88; raiz 0,6 m; limiar 2 °C), uma exceção que o time ainda não decidiu.

O que **pode** ser dito, com número:
- A geada tira agosto da janela que a água sozinha indicaria (6,3 contra 0,2 em 10 em 1/ago). A forma bate com o ZARC (40%); a magnitude do POWER é maior. N2, não validado. (V4, V6)
- O 2º milho tem degrau de risco: até 5 de fevereiro, cerca de 2 em 10; em 11/fev, 4 em 10 (sem a falta de água). (V2)
- No talhão raso, metade em sorgo ajudou o ano ruim em 7 de cada 10 cenários testados, e a conta não é firme. (V3)
- O alerta de ano seco existe e pega parte dos anos ruins; a frase "em anos assim, 4 em 10 regiões tiveram quebra" é da auditoria (usa o IBGE PAM) e **não vai ao produtor**. (V1)
- Cada número do cartão tem rastro até o dado e o script.

---

## 10. Pendências

| # | Pendência | Por quê |
|---|---|---|
| P1 | ~~Escrever o validador R1–R12~~ Feito: `motor/validador.py`, R1 a R15 | — |
| P2 | ~~Percentil do alerta só com anos passados, em script~~ Feito no motor e na validação (V1 passo 6) | — |
| P3 | ~~Rodar V3 com CAD de 39 mm~~ Feito no motor (central +46,9%, grade 67,4%). Falta repetir o relatório da V3 com 39 mm | Os números da V3 são de 42 mm |
| P4 | Calibrar o Ky do sorgo com NDVI de Sentinel-2 ou Landsat em safra seca e normal | Se o Ky real for ≥ 1,5 vez o da FAO, o módulo sai (V3) |
| P5 | Água do 2º milho | Hoje só a geada é calculada (V2) |
| P6 | Correção de altitude pelo SRTM na geada | Concórdia (884 m) tem o limite no começo de janeiro (V2) |
| P7 | Niño 3.4 pela TSM do ERA5 | Para religar `enso_tipo_risco` dentro da regra de dados |
| P8 | Login Earthdata para IMERG ou SMAP, ao menos como camada | Reforça o dado NASA visível (V7) |
| P9 | Abrir os trechos da Epagri/Ciram (14/07/2000, 15/08/2009) e o estudo de Chapecó | Conferência da geada ficou em trecho de busca (V2) |
| P10 | Teste com 2 a 3 produtores ou técnicos | Os cartões nunca foram testados com gente |
| P11 | Calibrar o limiar de geada do POWER contra o ZARC (ou contra estação) | O POWER dá 63% contra 40% do ZARC em 1/ago (V6) |
| P12 | Decidir a exceção dos parâmetros de literatura (R = 0,88; raiz 0,6 m; limiar 2 °C) | Regra de dados do desafio |
| P13 | Contato real da assistência técnica (nome ou telefone) nas mensagens | Hoje só "o técnico da assistência técnica do seu município" |
| P14 | Evento comum em "x em 10" para as 3 estratégias de SMO (por exemplo, falta de silagem) | Hoje os números têm tipos diferentes |

---

## 11. Fontes (scripts e resultados)
- Controle e fichas: `loop-validacao/fichas/B1-0-controle.md`, `B1-1-geada-milho-safrinha.md`, `A4-3-sorgo-seguro-silagem.md`, `A3-1-alerta-erosao.md`, `A2-4-el-nino-tipo-de-risco.md`, `B4-1-quebra-cebola-sinal-preco.md`, `B4-3-guardar-cebola-fugir-pico.md`, `A1-1-mapa-plantio-extremo-oeste.md`, `B3-3-alerta-extremos-fora-da-amostra.md`.
- V1 (ano extremo): `solucao/validacao/V1/relatorio.md`, `resultado_extensao.json`, `tabela_original.json`, `v1_passo4_extensao.py`.
- V2 (geada): `solucao/validacao/V2/relatorio.md`, `v2_geada.py`, `v2_resultado.json`.
- V3 (mistura): `solucao/validacao/V3/relatorio.md`, `modelo_v3.py`, `res_02_central_grade.json`, `res_03_extras.json`, `res_06_srtm.json`.
- V4 (motor composto): `solucao/validacao/V4/relatorio.md`, `v4_motor.py`, `v4_resultado.json`.
- V5 (Semiárido): `solucao/validacao/V5/relatorio.md`, `motor.py`, `resultado.json`.
- V6 (ZARC): `solucao/validacao/V6/relatorio.md`, `zarc_gabarito_sc.json`.
- V7 (desafio, concorrentes, pitch): `solucao/validacao/V7/relatorio.md`, `resultado_v7.json`.
- Quixadá: `prototipo/modelo/risco.py`, `prototipo/dados/resultado.json`.
- Dados NASA: `loop-validacao/dados/power_sao_miguel_do_oeste.json`, `power_ituporanga.json`, `prototipo/dados/power_quixada.json`.
