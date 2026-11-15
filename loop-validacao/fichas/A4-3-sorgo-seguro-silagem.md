# A4-3 · Parte da área com sorgo como seguro de silagem (por tipo de solo)

Sessão: A4 · Trilha: A · Região: São Miguel do Oeste · Tentativa 3 de 4 · Data: 2026-11-14

## 1. Ideia (escrita antes do teste)
Variação da A4-1 (descartada). O critério foi escrito depois do resultado da A4-1 e antes de rodar esta tentativa, em `sessoes/A4/00_criterios_pre_teste.md`.
- **Hipótese:** em solo médio ou raso, plantar 25% ou 50% da área de silagem com sorgo sobe o "pior ano em 10" da silagem colhida, com pouca perda na média. O sorgo funciona como seguro, e a decisão passa a ser por talhão (solo), não por ano.
- **Problema que ataca (e para quem):** o produtor de leite que fica sem volumoso no ano seco e precisa comprar. Em 2021/22, SC perdeu 32% do milho silagem (Epagri/Cepa) [DADO].
- **Decisão que muda:** quanto da área de silagem vai para o sorgo, conforme o solo do talhão.
- **Critério de sucesso (definido antes):** com 25% ou 50% de sorgo, em solo médio E raso, três condições:
  1. o 10º percentil (pior ano em 10) sobe ≥ 10%;
  2. os casos com silagem total abaixo de 0,6 caem ≥ 50%;
  3. a média cai no máximo 3%.

  No solo argiloso profundo, espera-se que não valha (controle negativo).
- **Linha de base:** 100% milho.

## 2. Teste
- **Dados oficiais usados:** NASA POWER diário em SMO, de 1984 a 2025.
- **Método:** usei os mesmos casos da A4-1, com plantio de 11/set a 21/out: 41 safras × 5 decêndios, 205 casos. A silagem total da propriedade é (1 − f) × milho + f × 0,85 × sorgo. Scripts: `sessoes/A4/a4_3_sorgo_seguro.py` e `sessoes/A4/a4_1_milho_sorgo.py`.
- **Resultado** [CÁLCULO], com os parâmetros FAO do sorgo:

  | Solo | % sorgo | Média | Pior ano em 10 (P10) | Casos < 0,6 | Pior caso |
  |---|---|---|---|---|---|
  | Argiloso | 0 | 0,894 | 0,661 | 16 | 0,35 |
  | Argiloso | 50 | 0,853 (−4,5%) | 0,688 (+4,0%) | 11 | 0,43 |
  | Médio | 0 | 0,817 | 0,536 | 29 | 0,25 |
  | Médio | 25 | 0,808 (−1,2%) | 0,561 (+4,6%) | 26 | 0,30 |
  | Médio | 50 | 0,798 (−2,3%) | 0,579 (+7,9%) | 24 | 0,35 |
  | **Raso** | 0 | 0,732 | 0,441 | 57 | 0,19 |
  | **Raso** | 25 | 0,733 (+0,2%) | 0,473 (+7,3%) | 51 | 0,25 |
  | **Raso** | **50** | **0,734 (+0,3%)** | **0,505 (+14,4%)** | 44 (−23%) | 0,30 |
  | Raso | 100 | 0,737 (+0,7%) | 0,555 (+25,9%) | 31 (−46%) | 0,41 |

  - **Com o Ky do sorgo × 1,5** (sorgo menos tolerante que a FAO supõe), o ganho some em todos os solos. No raso, com 50% de sorgo, o P10 cai 1,0% e a média cai 3,2%.
  - Ponto de equilíbrio do fator de valor (sorgo empata com milho na média): 0,95 no argiloso, 0,92 no médio e 0,89 no raso.
- **Gráficos:** `sessoes/A4/fig_a4_1_ano_a_ano.svg` (solo médio, mostra que os anos ruins do milho são os de estiagem) e `sessoes/A4/fig_a4_1_por_decendio.svg` (a troca compensa mais vezes quanto mais raso o solo).

## 3. Validação
- **Contra a linha de base** (raso, 50% de sorgo): P10 de 0,505 contra 0,441 (+14%); média de 0,734 contra 0,732; casos abaixo de 0,6, 44 contra 57 (−23%). No solo médio: P10 +7,9%, abaixo do limiar. No argiloso, perde-se média (−4,5%), como esperado no controle negativo.
- **Fontes externas:**
  - **ZARC 2026/27 de SMO.** Sorgo forrageiro: 20% de risco em todos os solos, de 11/set a 11/dez. Milho 1ª safra: 20% só em solos AD4–AD6, e 30–40% em AD2–AD3. **Bate:** o ZARC também diz que a vantagem do sorgo aparece no solo de pouca água e some no solo bom.
  - **Embrapa.** Segundo a Embrapa Gado de Leite e a Embrapa Milho e Sorgo, o sorgo é mais tolerante a veranicos, e o valor da silagem de sorgo fica de 72% a 92% do da silagem de milho (Demarchi et al., 1995), ou cerca de 10% abaixo em híbridos modernos. O fator de 0,85 está dentro da faixa. Com 0,90, o sorgo já passa o milho na média do solo raso.
  - **IBGE/PAM** não tem sorgo em SMO, então não dá para conferir o rendimento do sorgo.
- **O critério de sucesso foi atingido?** **Em parte.** No solo raso, o P10 e a média passam, mas os casos abaixo de 0,6 caem só 23% (precisava de 50%). No solo médio, não passa. O controle negativo (argiloso) se comportou como esperado. O ganho depende do Ky do sorgo, que não está calibrado.

## 4. Régua (1 a 5)
| Critério | Nota | Por quê (uma frase) |
|---|---|---|
| Problema real | 4 | Faltar silagem no ano seco é o prejuízo que o produtor de leite do Oeste mais sente (−32% em 2021/22). |
| Tamanho do impacto | 3 | No solo raso, o pior ano em 10 melhora 14% sem perder média; no solo bom, não vale. |
| Resolve de fato | 3 | Muda o que o agricultor faria nos talhões de solo raso: metade da silagem em sorgo. |
| Validade | 3 | Supera a linha de base com dado oficial no solo raso e bate com o ZARC por classe de solo, mas é sensível ao Ky do sorgo, que é genérico. |
| Muda a decisão | 3 | A pergunta muda de "qual cultura este ano?" para "quanto de sorgo neste talhão?", e a resposta depende do solo. |
| Simples e factível | 4 | Mesmo modelo; falta só saber o solo do talhão (GAEZ/SRTM). |
| Alinhamento com o desafio | 4 | Estratégia de cultura e rotação com dados da NASA e foco em risco. |
| Diferencial | 3 | O ZARC dá o risco por cultura; ele não diz quanto da área diversificar, nem o ganho no pior ano. |
| Cabe no hackathon | 4 | Já está rodando; o gráfico do pior ano em 10 é fácil de mostrar. |
| **Total (máx. 45)** | **31** | |

## 5. Veredito
**Ajustar.** É o melhor resultado da sessão, mas o critério só foi cumprido em parte e o ganho depende do Ky do sorgo. Antes de entrar no pitch, faltam três coisas:
1. Usar Kc e Ky de híbrido de sorgo forrageiro do Sul, por exemplo da Embrapa Milho e Sorgo, ou calibrar com NDVI de safras passadas.
2. Identificar o solo raso pelo talhão (declive no SRTM, GAEZ).
3. Mostrar o resultado como faixa: "de 0% a 14% a mais no pior ano em 10, conforme o sorgo".

## 6. Relação com o controle
**Complementa.** É o controle aplicado ao leite: usa a probabilidade histórica para escolher a mistura de culturas por talhão, não a cultura do ano. Na demo: "No seu talhão de solo raso, com metade da silagem em sorgo, o pior ano em 10 rende 14% a mais e a média não cai. No talhão de solo fundo, fique no milho."

## 7. Limites e o que não foi testado
- **Parâmetros do sorgo genéricos.** Com Ky × 1,5 a vantagem some. Não testei sorgo com Ky menor que o da FAO no solo médio (no solo raso, Ky × 0,7 deixa o sorgo quase sem perdas: 4 casos).
- Silagem tratada como rendimento relativo, sem matéria seca absoluta. Não entram custo de semente, ensilagem e manejo (a Cultivar cita o sorgo 5% a 15% mais barato), nem preço de compra de volumoso no ano seco. Tudo isso tende a favorecer o sorgo [INFERÊNCIA].
- O solo raso foi simulado como raiz limitada a 0,5 m, sem mapa real dos talhões. Grade POWER de cerca de 50 km.
- O modelo não trata frio e radiação: o ZARC exclui milho depois de 21/jan e o modelo não vê isso.
- SMAP, IMERG e NDVI não foram usados para calibrar.

## 8. Fontes
- NASA POWER diário: `loop-validacao/dados/power_sao_miguel_do_oeste.json`.
- ZARC 2026/27 (MAPA), portarias 236 (milho) e 315 (sorgo forrageiro): https://dados.agricultura.gov.br/dataset/tabua-de-risco-zoneamento-agricola-de-risco-climatico. Resumo em `sessoes/A4/zarc_smo_resumo.txt`.
- [Revista Cultivar, silagem de sorgo (Embrapa Milho e Sorgo)](https://www.revistacultivar.com.br/noticias/producao-de-silagem-de-alta-qualidade-de-sorgo); [RBMS/Embrapa, Demarchi et al. (1995)](https://rbms.sede.embrapa.br/ojs/article/download/121/pdf_388/6059); [Embrapa, sorgo forrageiro](https://www.infoteca.cnptia.embrapa.br/infoteca/bitstream/doc/491736/1/Sorgoforrageiro.pdf).
- Epagri/Cepa via Notícias Agrícolas: [estiagem de 2021/22](https://www.noticiasagricolas.com.br/noticia/309922).
- FAO-33 e FAO-56.
