# V3 · Critério escrito ANTES de rodar qualquer simulação nova (14/11/2026)

Disclosure: eu já tinha lido o resultado da A4-3 (ficha) antes de escrever isto. Então o critério não é cego ao que a A4 achou. Ele é fixado antes de eu rodar os parâmetros novos, a grade de sensibilidade e o bootstrap. Qualquer mudança depois vai marcada como "pós-teste" no relatório.

## Afirmação testada
"No solo raso, metade da silagem em sorgo melhora o pior ano em 10 sem baixar a média."

## Definições
- Ponto: São Miguel do Oeste, NASA POWER diário, safras de plantio 1984 a 2024 (41). Datas de plantio do milho: 11/set, 21/set, 1/out, 11/out, 21/out (as mesmas da A4).
- Silagem da propriedade = (1 − f) × y_milho + f × R × y_sorgo, com f = 0,5. R = valor relativo da silagem de sorgo.
- "Pior ano em 10" = percentil 10 (P10) dos 205 casos (41 safras × 5 datas). Também reporto por data.
- "Perda" = silagem total < 0,6.
- "Solo raso" tem duas definições, as duas reportadas:
  - V3-a, raso da A4: água disponível na zona de raiz (CAD) = 87,5 mm.
  - V3-b, raso pelo ZARC: CAD = 42 mm (tipo 1 do ZARC do sorgo; AD3 do milho = 41,4 mm).

## Cenário central (fixado antes)
- Parâmetros da literatura (FAO-33 por estágio, FAO-56, ZARC SC), definidos no relatório. Ky do sorgo = FAO (total 0,9). R = 0,88 (meio da faixa de 85 a 90% da Embrapa). Sorgo plantado na mesma data do milho. Kc e raiz da FAO.

## Critério de sucesso (todos, para "sustenta")
1. **Ponto central:** P10 sobe ≥ 10% e a média cai no máximo 3%.
2. **Amostragem (bootstrap por safra, 2.000 repetições, reamostrando as 41 safras com as 5 datas juntas):** em ≥ 90% das repetições o ganho de P10 é > 0, e em ≥ 80% a média não cai mais que 3%.
3. **Parâmetros (grade pré-definida):** Ky do sorgo × {0,5; 0,75; 1; 1,5; 2}; R ∈ {0,75; 0,88; 1,0}; cenário de Ky ∈ {A4 original, FAO-33 por estágio, biomassa (Ky = 1 nos dois)}; sorgo plantado na mesma data ou 30 dias depois; Kc do sorgo × {0,85; 1; 1,15}. Uma combinação "sobrevive" se o ganho de P10 for > 0 e a média cair no máximo 3%. O Ky do milho fica na versão do cenário.
   - Sustenta: ≥ 70% das combinações sobrevivem.
   - Parcial: 40% a 70%, ou o ponto central passa mas o bootstrap falha.
   - Não sustenta: < 40%, ou o ponto central falha.
4. **Controle negativo:** no solo fundo (CAD 175 mm), f = 0,5 não deve subir o P10 em ≥ 10%.

## Faixa de incerteza que vou reportar
Intervalo do bootstrap no cenário central e faixa (mínimo, mediana, máximo) do ganho de P10 e da variação da média na grade. Também o Ky do sorgo de equilíbrio (ganho de P10 = 0) e o R de equilíbrio (média igual).

## Solo raso por talhão (só com a aba Resources)
- Proposta: declive do SRTM (30 m) + prior regional do GAEZ (5 arc-min, que só serve para a região, não para o talhão).
- Teste: (i) o declive separa o município em classes não triviais (entre 10% e 60% da área com declive ≥ 20%, o limite "forte ondulado" da Embrapa); (ii) o resultado bate com a descrição dos solos do Extremo Oeste na literatura (conferência externa).
- Não há mapa de profundidade real por talhão na aba. Então a regra será uma hipótese com risco de erro, não um achado validado. O relatório diz isso.

## Conferência externa pré-definida
- ZARC 2026/27 de SMO (milho 1ª safra por AD1 a AD6; sorgo forrageiro por tipo de solo 1 a 3). Recalculo o ISNA com os critérios do ZARC (milho: fase I ≤ 0,70 e fase III ≤ 0,55; sorgo: 0,70, 0,60 e 0,40) e comparo a ordem de risco milho × sorgo por CAD.
- Anos de seca conhecidos (2004/05, 2011/12, 2021/22): o ganho da mistura deve aparecer neles.
- Embrapa e FAO para os parâmetros e para R.
