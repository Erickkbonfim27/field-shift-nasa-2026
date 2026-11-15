# B1-1 · Geada no milho safrinha (silagem): até quando dá para plantar o 2º milho

Sessão: B1 · Trilha: B · Região: São Miguel do Oeste · Tentativa 1 de 4 · Data: 2026-11-14

## 1. Ideia (escrita antes do teste)
Critérios copiados de `sessoes/B1/CRITERIOS_ANTES_DO_TESTE.md`, escritos antes de rodar os dados.
- **Hipótese:** com `T2M_MIN` e graus-dia do NASA POWER dá para calcular, ano a ano, a chance de geada antes do ponto de silagem do milho safrinha. A data-limite de plantio que sai daí é diferente da que se tira de médias.
- **Problema que ataca (e para quem):** o produtor de leite do Extremo Oeste que colhe o milho silagem de verão e decide se planta um 2º milho (mais silagem) ou uma pastagem de inverno (aveia/azevém). O milho plantado tarde pega geada antes do ponto e vira perda.
- **Decisão que muda:** plantar o 2º milho até a data-limite, ou trocar por pastagem de inverno quando a colheita do verão atrasa. É uma decisão de rotação.
- **Critério de sucesso (definido antes):**
  - C1: o proxy de geada marca ≥ 4 de 5 eventos de geada ampla conhecidos.
  - C2: a chance de geada antes do ponto de silagem varia ≥ 30 pontos percentuais entre plantar em 1/jan e em 28/fev.
  - C3: a data-limite (risco ≤ 20%) fica a ±20 dias da indicação do ZARC 2ª safra ou da Epagri para o Oeste de SC.
- **Linha de base:** "não fazer nada" = regra sem dado diário. Pode ser a média mensal de `T2M_MIN` ou a data da 1ª geada mediana.

## 2. Teste
- **Dados oficiais usados:** NASA POWER diário, `T2M_MIN` e `T2M_MAX`, 1981–2025, grade de ~50 km.
- **Método:**
  - Geada provável = `T2M_MIN` ≤ 3 °C; geada forte = ≤ 1 °C [ESTIMATIVA: a relva fica de 3 a 5 °C abaixo do ar a 2 m].
  - Ponto de silagem = 1.250 °C·dia, base 10 °C, com teto de 30 °C [ESTIMATIVA para híbrido precoce].
  - Para cada decêndio de plantio de 1/jan a 11/mar e cada ano, verifica se houve geada entre o plantio e o ponto de silagem. O ciclo alonga sozinho no outono: 93 dias no plantio de 1/jan e 159 dias no de 11/mar [CÁLCULO].
  - Script: `sessoes/B1/b1_1_geada_safrinha.py`.
- **Resultado (anos em 10 com geada antes do ponto de silagem, n = 45)** [CÁLCULO]:

| Plantio | 1/jan | 11/jan | 21/jan | 1/fev | 11/fev | 21/fev | 1/mar | 11/mar |
|---|---|---|---|---|---|---|---|---|
| Geada provável (≤ 3 °C) | 0,0 | 0,0 | 0,2 | 1,1 | **4,4** | 6,7 | 8,9 | 9,6 |
| Geada forte (≤ 1 °C) | 0,0 | 0,0 | 0,0 | 0,2 | 2,4 | 4,0 | 6,7 | 7,8 |
| Dias até a silagem (mediana) | 93 | 95 | 100 | 110 | 124 | 136 | 149 | 159 |

  - **Data-limite (risco ≤ 2 em 10): 1/fev.** Em só 10 dias, de 1/fev a 11/fev, o risco sobe de 1 para 4 em cada 10 anos.
  - **1ª geada do outono (`T2M_MIN` ≤ 3 °C):** em 1 de cada 10 anos já chega em 23/mai; a mediana é 17/jun e o percentil 90 é 13/jul [CÁLCULO].
- **Gráfico:** `sessoes/B1/b1_1_geada_safrinha.svg` mostra o "degrau" de risco entre 1/fev e 21/fev.

## 3. Validação
- **C1 (o proxy enxerga geada):**
  - Os 6 eventos de geada ampla no Sul do Brasil testados foram todos marcados com ≤ 3 °C, e 5 deles também com ≤ 1 °C: jun/1994 (−2,7 °C), jul/2000 (−3,0), jul/2013 (−2,1), jun/2021 (−1,9), jul/2021 (−0,3) e mai/2022 (2,9) [CÁLCULO].
  - Ao acaso, uma janela de 5 dias em jun–jul tem 24% de chance de passar de 3 °C; em maio, 4%. Acertar 6 de 6 por sorte teria chance de cerca de 0,02% [CÁLCULO].
  - Ressalva: a lista de eventos é da memória do agente [INFERÊNCIA], não foi conferida no Epagri/Ciram.
- **Contra a linha de base:**
  - A média mensal de `T2M_MIN` do POWER (mai 11,9 °C, jun 10,3 °C, jul 9,4 °C) nunca chega a 3 °C [CÁLCULO]. Uma regra por médias diria "sem risco de geada" em qualquer data.
  - A regra pela "1ª geada mediana" (17/jun) aceitaria plantar até cerca de 11/fev, onde o risco real é de 4,4 em 10 anos. O cálculo ano a ano antecipa a data-limite em cerca de 10 dias e mostra o degrau.
- **Fonte externa:**
  - **Estudo de sucessão soja–milho safrinha em Chapecó (~150 km de São Miguel do Oeste):** usou o mesmo limiar (mínima no abrigo ≤ 3 °C) e risco < 20%. Indica o safrinha desde que o ciclo não chegue ao 3º decêndio de junho [DADO, mas **não verificado**: o trecho veio do resumo de uma busca; os PDFs do core.ac.uk devolveram 403, e não confirmei título, autores nem qual dos dois links é o estudo]. No nosso modelo, o ciclo até a silagem chega a 21/jun com plantio por volta de 11/fev, a **cerca de 10 dias** da nossa data-limite (1/fev). Bate dentro dos ±20 dias. Links candidatos: https://core.ac.uk/download/524940844.pdf e https://core.ac.uk/download/84613725.pdf.
  - **ZARC 2ª safra de milho para SC:** não achei portaria de milho 2ª safra para SC. A de 1ª safra 2026/27 usa geada com Tmin < 2 °C nas fases I a III [DADO], que é coerente com o limiar adotado aqui.
  - **IBGE, tabela 839:** o milho 2ª safra **em grão** em São Miguel do Oeste é zero até 2022 e tem só 80 a 100 ha de 2023 a 2025 [DADO]. A silagem não entra na PAM. https://apisidra.ibge.gov.br/values/t/839/n6/4217204/v/all/p/all/c81/all
- **O critério de sucesso foi atingido?** **Sim, com ressalvas.**
  - C1 sim: 6 de 6, mas com eventos da memória.
  - C2 sim: varia 67 pontos, de 0 em 1/jan a 6,7 em 21/fev.
  - C3 em parte: bate com o estudo de Chapecó, cujo texto não consegui abrir, e não com o ZARC (não há ZARC 2ª safra para SC).

## 4. Régua (1 a 5)
| Critério | Nota | Por quê (uma frase) |
|---|---|---|
| Problema real | 3 | A safrinha de grão quase não existe no município (PAM); a de silagem em propriedades de leite é plausível, mas não está medida [INFERÊNCIA]. |
| Tamanho do impacto | 2 | Vale só para quem planta 2º milho depois de 1/fev; a área é pequena. |
| Resolve de fato | 3 | Muda a decisão nos anos em que o milho de verão atrasa: depois de ~1/fev, o risco passa de 4 em 10 e a pastagem de inverno vira a melhor rotação. |
| Validade | 3 | Supera a regra por médias e o proxy acerta 6 de 6 eventos, mas a única fonte externa (Chapecó) não foi aberta, não há ZARC 2ª safra e os eventos não foram conferidos no Ciram. |
| Muda a decisão | 3 | Dá uma data-limite clara e um aviso de "degrau" que a média não mostra. |
| Simples e factível | 5 | Duas variáveis do POWER e uma soma térmica. |
| Alinhamento com o desafio | 4 | É uma escolha de rotação (2º milho x pastagem) com dado NASA. |
| Diferencial | 2 | A A1 já inclui a geada do milho safrinha no mapa de época, e o ZARC usa critério parecido na 1ª safra. |
| Cabe no hackathon | 5 | Já está pronto. |
| **Total (máx. 45)** | **30** | |

Aprovada só com 3+ em problema real, resolve de fato e validade. **Passa** (3 / 3 / 3).

## 5. Veredito
**Aprovada, como camada e não como produto.** O sinal é forte e simples (risco quase zero até 21/jan, 1 em 10 em 1/fev, 4 em 10 em 11/fev), mas o público é pequeno e a ideia se sobrepõe a A1. Recomendo juntá-la ao mapa de época da A1 e ao controle como a "camada de geada".

## 6. Relação com o controle
**Complementa.** O controle sem geada daria conselho errado em SC: mandaria plantar o milho safra em agosto, que tem 6 em 10 anos de geada (ver B1-0). Com esta camada, a ferramenta passa a responder a pergunta de rotação do leite: "colhi a silagem em 25/jan; ainda dá para plantar outro milho ou vou de aveia?". Na demo, entra como um cartão de "data-limite do 2º milho".

## 7. Limites e o que não foi testado
- O `T2M_MIN` é a temperatura do ar a 2 m, numa grade de ~50 km. Baixadas e encostas mudam muito o risco no talhão, e o SRTM poderia ajustar isso (não testado).
- **A conferir antes do pitch:** abrir o estudo de Chapecó e conferir os eventos de geada no Epagri/Ciram; isso pode subir a validade para 4.
- Os limiares de 3 °C e 1 °C e a soma de 1.250 °C·dia são estimativas; cada híbrido tem a sua.
- Não testado: a falta de água na safrinha de fevereiro a abril (a A1 cobre) e o frio que atrasa o enchimento sem chegar a geada.
- Não há gabarito de perdas de milho silagem por geada no município.

## 8. Fontes
- NASA POWER (ver B1-0). Resultados: `sessoes/B1/b1_1_resultado.json`.
- IBGE SIDRA, tabela 839 (link acima).
- Estudo de época de milho safrinha em Chapecó: trecho lido via busca, PDF não aberto (403). Links candidatos: https://core.ac.uk/download/524940844.pdf e https://core.ac.uk/download/84613725.pdf.
- MAPA, Portaria SPA/MAPA nº 236/2026 (critério de geada do ZARC milho SC).
