# A1-3 · Milho em duas épocas distantes (cedo + tarde) com penalidade de potencial

Sessão: A1 · Trilha: A · Região: São Miguel do Oeste · Tentativa 3 de 4 · Data: 2026-11-14

## 1. Ideia (escrita antes do teste, 14/11/2026)
- **Origem:** variação da A1-2 (descartada). Na A1-2, as secas que o IBGE mostra (2011/12 e 2021/22) pegaram todos os plantios de setembro a novembro (rendimento 0,2 a 0,5) e pouparam os de dezembro e janeiro (0,7 a 1,0). Escalonar dentro de set–nov não diversifica. Mas o modelo da A1-2 só olha a água e acha que janeiro é a "melhor data", o que ignora que o milho tardio tem menos potencial (menos radiação no enchimento).
- **Hipótese:** dividir o milho (grão ou silagem para o leite) entre uma época cedo (setembro) e uma tarde (dezembro/início de janeiro) reduz a perda no pior ano em relação a plantar tudo numa data só, mesmo descontando o menor potencial do plantio tardio.
- **Problema que ataca (e para quem):** o produtor de leite do Extremo Oeste que perde a silagem inteira numa estiagem de La Niña (nov a jan).
- **Decisão que muda:** plantar todo o milho em setembro contra guardar uma parte da área para plantar em dezembro/janeiro.
- **Critério de sucesso (definido antes):** contra a melhor data única (agora com a penalidade de potencial), a combinação cedo + tarde reduz a **perda no pior ano** (ou o P10 da perda) em **≥ 10 pontos percentuais** e custa **≤ 3 pontos percentuais** de rendimento médio. Mesmo teste fora da amostra da A1-2 (escolhe em 1984–2003, testa em 2004–2024).
- **Definições fixadas antes de rodar:**
  - Rendimento = potencial relativo × fator hídrico FAO-33 × 0,3 se houver geada.
  - Potencial relativo do decêndio = média (41 anos) da radiação ALLSKY_SFC_SW_DWN do POWER somada nas fases de floração e enchimento (mid + late) ÷ o maior valor entre os decêndios da janela. [ESTIMATIVA: eficiência de uso da radiação constante, ciclo em dias fixos.]
  - Combinações fixas: 15/set + 15/dez (dec 26+35) e 15/set + 5/jan (dec 26+1). Área meio a meio.
  - Solo argiloso; médio como sensibilidade. Janela = decêndios do ZARC (24 a 36 e 1 a 3).
- **Linha de base:** tudo numa data só (a melhor data única com penalidade, e a habitual 25/set).

## 2. Teste
- **Dados oficiais usados:** NASA POWER diário (AG), São Miguel do Oeste, 1984–2025: variáveis do balanço hídrico mais `ALLSKY_SFC_SW_DWN` para o potencial.
- **Método:** motor da A1-1; potencial relativo por decêndio pela radiação somada na floração e no enchimento; combinações fixas meio a meio; teste fora da amostra. Script: `sessoes/A1/cedo_tarde.py`. Saídas: `cedo_tarde_smo.json`, `series_milho_pot_*.json`.
- **Resultado:** [CÁLCULO]
  - Potencial relativo: 1,00 (5–15/set), 0,95 (15/out), 0,87 (15/nov), 0,75 (15/dez), 0,65 (5/jan), 0,56 (25/jan).
  - Solo argiloso:

| Estratégia | Média | Pior ano | P10 | Desvio | Anos perda > 40% |
|---|---|---|---|---|---|
| Melhor data única (5/set, dec 25) | 0,846 | 0,26 | 0,55 | 0,207 | 5 |
| Habitual (25/set) | 0,824 | 0,16 | 0,56 | 0,215 | 6 |
| 15/set + 15/dez | 0,746 | 0,45 | 0,49 | 0,136 | 7 |
| 15/set + 5/jan | 0,716 | 0,41 | 0,56 | 0,120 | 7 |
| Fora da amostra: combo (5/set + 5/nov + 25/nov), teste 2004–24 | 0,726 | 0,41 | 0,47 | 0,166 | 4 |
| Fora da amostra: data única (15/set), teste 2004–24 | 0,810 | 0,27 | 0,53 | 0,209 | 3 |

  - Solo médio: melhor data única 0,753 / pior 0,14; 15/set + 15/dez 0,667 / 0,30 (+16 pp no pior ano, −8,6 pp na média).
  - Ano a ano (argiloso): em 2021/22, set 0,27 e dez 0,75; mas em 2020/21, set 0,69 e dez 0,29, e em 2004/05, set 0,69 e dez 0,28. Cedo e tarde de fato perdem em anos diferentes, e isso é o que diminui o pior ano.
  - Ponto de equilíbrio: para o custo na média ficar ≤ 3 pp, o plantio de 15/dez precisaria ter ≥ 90% do potencial do de setembro; a estimativa por radiação dá 75%.
- **Gráfico:** `sessoes/A1/a1_23_risco_retorno.svg` (painel da direita): as combinações cedo + tarde sobem no pior ano, mas andam ~10 pontos para a esquerda na média.

## 3. Validação
- **Contra a linha de base (melhor data única):** pior ano de 0,26 para 0,45 (**+19 pp**, meta ≥ 10: atingido); média de 0,846 para 0,746 (**−10 pp**, meta ≤ 3: **não atingido**). P10 piora (0,55 para 0,49) e os anos com perda > 40% sobem de 5 para 7. Fora da amostra: +14 pp no pior ano e −8,4 pp na média. **Não atinge.**
- **Fonte externa:** Epagri/Cepa (jan/2022) sobre a estiagem de 2021/22: o Oeste foi o mais atingido, e o milho plantado em setembro foi quase todo perdido; isso concorda com o modelo (set 0,27, dez 0,75). Não achamos número público do rendimento do milho tardio por data para conferir o potencial de 75%. IBGE PAM não separa por data.
- **O critério de sucesso foi atingido?** **Não** (atingiu a redução do pior ano, falhou o custo).

## 4. Régua (1 a 5)
| Critério | Nota | Por quê (uma frase) |
|---|---|---|
| Problema real | 4 | Perder a silagem inteira numa estiagem de La Niña é real para o leite do Oeste (2021/22: milho de setembro quase todo perdido, Epagri/Cepa). |
| Tamanho do impacto | 3 | Corta a perda do pior ano de 74% para 55%, o que, para quem depende da silagem, é a diferença entre ter ou não comida para o rebanho. |
| Resolve de fato | 2 | Funciona como um seguro de prêmio alto: paga ~10% da produção média todo ano para ganhar 19 pp no pior ano. |
| Validade | 2 | Testado com dado oficial e coerente com a Epagri em 2021/22, mas não passa a linha de base no critério definido, e o potencial por radiação é uma estimativa grosseira. |
| Muda a decisão | 2 | Mudaria só para quem aceita trocar média por segurança; para os outros, a resposta continua "plante tudo cedo". |
| Simples e factível | 4 | Uma conta a mais sobre o mesmo motor. |
| Alinhamento com o desafio | 3 | Compara estratégias com dados da NASA e conversa com a sucessão (milho tardio ocupa a área antes da pastagem de inverno), mas não é rotação de culturas. |
| Diferencial | 3 | Nem o ZARC nem o calendário mostram como os anos ruins de cada data se combinam (o retrato de risco e retorno). |
| Cabe no hackathon | 5 | Pronto. |
| **Total (máx. 45)** | **28** | |

## 5. Veredito
**Descartada** pelo critério definido (o custo na média é de 10 pp, contra 3 pp aceitos). O que fica de útil: a **troca entre média e pior ano** é real e mensurável com POWER, e poderia virar uma tela "quanto você aceita perder na média para não perder tudo no pior ano?", mas isso é mais uma forma de mostrar do que uma ideia aprovada.

## 6. Relação com o controle
Complementa. O controle fala em "probabilidade de colher" por estratégia; este teste mostra que, no Extremo Oeste, o retrato que importa é **média × pior ano**, porque o risco vem de anos inteiros de estiagem. Na demo, pode ser um gráfico de risco e retorno com 3 estratégias (tudo em setembro, tudo em dezembro, metade e metade), que é o formato "comparar 3+ estratégias" que o desafio pede.

## 7. Limites e o que não foi testado
- Potencial só pela radiação (eficiência constante, ciclo fixo em dias): não considera temperatura, graus-dia, calor nem a resposta real do híbrido; os 75% em dezembro podem estar subestimados ou superestimados.
- Não contei o valor da sucessão: o milho de dezembro atrasa a pastagem de inverno, e o de setembro libera a área antes.
- Grade do POWER de ~50 km; sem excesso de chuva, doença ou custo da operação em duas épocas.
- Escolher a combinação olhando os dados enviesa para cima; por isso as combinações fixas e o teste fora da amostra.

## 8. Fontes
- NASA POWER (arquivo local `dados/power_sao_miguel_do_oeste.json`), incluindo `ALLSKY_SFC_SW_DWN`.
- ZARC 2026/27, milho 1ª safra, São Miguel do Oeste (janela): https://dados.agricultura.gov.br/dataset/tabua-de-risco-zoneamento-agricola-de-risco-climatico
- Epagri/Cepa sobre a estiagem de 2021/22: https://www.noticiasagricolas.com.br/noticia/307520 e https://www.agrolink.com.br/noticias/veja-como-a-seca-esta-afetando-a-producao-agricola-em-sc_442148.html
- IBGE PAM, tabela 1612 (`sessoes/A1/ext/pam_smo.json`).
