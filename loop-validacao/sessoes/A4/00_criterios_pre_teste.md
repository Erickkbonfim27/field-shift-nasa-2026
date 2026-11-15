# A4 · Critérios escritos ANTES de rodar qualquer dado (14/11/2026)

Nada abaixo foi ajustado depois de ver resultado. Se algo mudar, a mudança vai marcada como "pós-teste" na ficha.

## Configuração comum
- Ponto: São Miguel do Oeste (SMO), -26,725; -53,518; 533 m (POWER). Anos de plantio 1984–2024 (ET0 precisa de radiação, que falta em 1981–83).
- Balanço hídrico diário tipo balde (FAO-56) com rendimento relativo por fase (FAO-33, Ky multiplicativo), reaproveitado de `prototipo/modelo/risco.py`.
- Solo padrão: argiloso profundo (175 mm/m, GAEZ, como no protótipo). Sensibilidade: solo médio (125 mm/m) e raso (raiz limitada a 0,5 m), porque o Extremo Oeste tem muito Neossolo raso em encosta.
- Água inicial: balde cheio 60 dias antes do plantio, gasto como solo nu até o plantio (inverno em SMO é úmido).
- Geada: T2M_MIN ≤ 2 °C nas fases de crescimento ou floração/enchimento corta o rendimento em 70% (vale para as duas culturas).
- "Perda" = rendimento relativo < 0,6 (mesmo corte do protótipo).

## A4-1 · Quando trocar milho por sorgo
- **Hipótese:** existe uma regra objetiva (data de plantio, umidade do solo GWETROOT no dia do plantio, ou chuva dos 30 dias anteriores) que aponta quando o sorgo dá mais segurança que o milho em SMO.
- **Comparação:** milho silagem (110 d) contra sorgo silagem (110 d), por decêndio de plantio de 21/ago a 21/fev, ano a ano.
- **"A troca compensou" no ano:** rendimento do sorgo × 0,85 > rendimento do milho (0,85 = sorgo rende cerca de 85% do valor da silagem de milho em ano sem estresse [ESTIMATIVA]; sensibilidade 0,75–0,95).
- **Linha de base:** "sempre milho" (o que o agricultor faz hoje). Segunda referência: "sempre sorgo".
- **Critério de sucesso (todos):**
  1. A regra, com limiar escolhido deixando um ano de fora (validação cruzada), reduz em **≥ 30%** os casos de perda frente a "sempre milho";
  2. sem baixar o rendimento ajustado médio frente a "sempre milho";
  3. quando a regra manda plantar sorgo, a troca compensa em **≥ 60%** dos casos (e acima da taxa-base de anos em que a troca compensa sem regra);
  4. a regra manda trocar em pelo menos 1 de cada 10 casos (senão não muda decisão).
- **Conferência externa:** (a) anos de perda do milho no modelo (plantio set/out) contra quedas de produtividade do milho no IBGE/PAM de SMO (queda ≥ 20% abaixo da mediana móvel): acertar ≥ 2 de 3 anos de queda; (b) janela do ZARC milho e sorgo em SMO, se der para baixar.

## A4-2 · Qual rotação usa menos água
- **Sequências anuais (julho a junho), datas típicas do Extremo Oeste [ESTIMATIVA]:**
  - R1 milho grão (21/set, 140 d) / aveia (1/abr, 120 d)
  - R2 soja (11/nov, 120 d) / trigo (11/jun, 130 d)
  - R3 milho silagem (1/set, 110 d) / azevém (1/mar, 180 d) ← **referência (o mais comum no leite)**
  - R4 sorgo silagem (21/out, 110 d) / aveia (1/abr, 120 d)
  - R5 milho silagem (1/set, 110 d) + sorgo silagem safrinha (5/jan, 110 d) / aveia (1/mai, 100 d)
- **Métricas por ano:** ETc (demanda), ETa (água consumida), déficit = ETc − ETa, e se alguma cultura da sequência teve perda.
- **Linha de base:** R3 (referência) e a média das rotações.
- **Critério de sucesso:** alguma rotação tem **déficit médio ≥ 20% menor** E **risco de perda ≥ 5 pontos percentuais menor** que R3, com o mesmo ordenamento em ≥ 2 dos 3 solos. Se as rotações diferirem < 10% em ETa, a ideia "usar menos água" não muda decisão em SMO.
- **Conferência externa:** ZARC (risco por cultura e decêndio em SMO), Embrapa/Epagri (consumo de água típico das culturas, estiagens 2019–2022 no Oeste).

---
## A4-3 · Variação após A4-1 ser descartada (escrito depois do resultado de A4-1, antes de rodar A4-3)
- **Por que:** A4-1 mostrou que nenhuma regra de plantio (data, GWETROOT, chuva de 30 dias) acerta os anos em que a troca compensa. Mas o sorgo perde muito menos vezes. Para quem tira leite, faltar silagem custa caro (compra de volumoso). Então a pergunta vira: **plantar parte da área com sorgo funciona como seguro?**
- **Hipótese:** em solo médio ou raso, plantar 25% ou 50% da área de silagem com sorgo sobe o "pior ano em 10" da silagem colhida, perdendo pouco na média.
- **Métrica:** silagem total da propriedade por safra = (1 − f) × y_milho + f × 0,85 × y_sorgo, plantio de 11/set a 21/out, 41 safras.
- **Linha de base:** 100% milho.
- **Critério de sucesso:** para f = 25% ou 50%, em solo médio e raso: (1) o 10º percentil (pior ano em 10) sobe **≥ 10%**; (2) os casos com silagem total < 0,6 caem **≥ 50%**; (3) a média cai **≤ 3%**. Em solo argiloso profundo, espera-se que não valha (controle negativo).
- **Conferência externa:** ZARC 2026/27 de SMO (risco do milho 1ª safra contra sorgo forrageiro por classe de solo); Embrapa Milho e Sorgo sobre tolerância do sorgo e valor da silagem.
