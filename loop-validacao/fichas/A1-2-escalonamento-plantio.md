# A1-2 · Escalonamento do plantio em várias datas

Sessão: A1 · Trilha: A · Região: São Miguel do Oeste (milho); Ituporanga (cebola, se fizer sentido) · Tentativa 2 de 4 · Data: 2026-11-14

## 1. Ideia (escrita antes do teste, 14/11/2026, antes de rodar qualquer dado)
- **Hipótese:** dividir a área de milho em 2 ou 3 datas de plantio (20 a 30 dias entre elas, dentro da janela indicada) faz a floração cair em períodos diferentes; como a estiagem costuma pegar só parte da safra, a perda no pior ano cai em relação a plantar tudo numa data só.
- **Problema que ataca (e para quem):** o agricultor familiar que planta todo o milho (grão ou silagem para o leite) numa data só e perde tudo quando o veranico pega a floração.
- **Decisão que muda:** plantar tudo de uma vez contra dividir a área em datas.
- **Critério de sucesso (definido antes):** contra a melhor data única, o escalonamento em 2 ou 3 datas
  - reduz a **perda no pior ano** (1 − rendimento relativo mínimo em 41 anos) **ou o P10 da perda** em **≥ 10 pontos percentuais**, e
  - custa **≤ 3 pontos percentuais** de rendimento relativo médio.
  - Também medimos o desvio-padrão (meta: −20%) e a fração de anos com perda > 40%.
- **Definições fixadas antes de rodar (14/11/2026):**
  - Modelo igual ao da A1-1 (`sessoes/A1/modelo_sc.py`), solo argiloso (médio como sensibilidade), 41 safras (plantio 1984–2024). Rendimento relativo = fator hídrico FAO-33 × 0,3 se houver geada (T2M_MIN ≤ 2 °C) no ciclo.
  - Área dividida em partes iguais; o rendimento do ano é a média das datas.
  - Datas candidatas: decêndios indicados pelo ZARC 2026/27 para milho 1ª safra em São Miguel do Oeste (dec 24 a 36 e 1 a 3), representados pelo dia do meio.
  - Combinações fixas (escolhidas sem olhar o resultado): 2 datas = 15/set + 15/out (dec 26+29) e 15/set + 5/nov (dec 26+31); 3 datas = 15/set + 15/out + 15/nov (dec 26+29+32).
  - "Melhor data única" = maior rendimento médio dentro da janela. Também comparamos com a data única de melhor pior-ano e com a habitual (25/set, dec 27).
  - Para evitar viés de escolha, a melhor combinação "de todas as possíveis" é escolhida em 1984–2003 e testada em 2004–2024.
  - **Cebola em Ituporanga (fixado depois de ver o milho, antes de rodar a cebola):** transplante de jun a ago (dec 16 a 24), ciclo de 130 dias após o transplante (fases 15/25/60/30, Kc 0,7/1,05/0,75, Ky 0,45/0,45/0,8/0,3, raiz 0,4 m, FAO-56/FAO-33 [ESTIMATIVA]), solo médio (Cambissolo [INFERÊNCIA]), sem geada (a cebola tolera). Habitual: 15/jul (dec 20) [ESTIMATIVA]. Combinações fixas: 15/jun+15/jul (dec 17+20) e 15/jun+15/jul+15/ago (dec 17+20+23). Mesmo critério do milho.
- **Linha de base:** tudo plantado numa data só (a melhor data única e a data habitual).

## 2. Teste
- **Dados oficiais usados:** NASA POWER diário (AG), 1984–2025, São Miguel do Oeste e Ituporanga (`dados/power_*.json`): chuva, temperaturas, umidade, vento e radiação para ET0.
- **Método:** mesmo motor da A1-1 (`sessoes/A1/modelo_sc.py`). Para cada decêndio da janela do ZARC, rendimento relativo de cada uma das 41 safras; combinações = média das datas em cada ano. Medidas: média, pior ano, P10, desvio-padrão e anos com perda > 40%. Teste fora da amostra (escolhe em 1984–2003, testa em 2004–2024). Scripts: `sessoes/A1/escalonamento.py` (milho) e `sessoes/A1/escalonamento_cebola.py` (cebola). Saídas: `escalonamento_smo.json`, `series_milho_*.json`, `series_cebola.json`.
- **Resultado, milho, solo argiloso:** [CÁLCULO]

| Estratégia | Média | Pior ano | P10 | Desvio | Anos perda > 40% |
|---|---|---|---|---|---|
| Melhor data única (15/jan, dec 2) | 0,945 | 0,47 | 0,76 | 0,124 | 1 |
| Habitual (25/set, dec 27) | 0,832 | 0,16 | 0,57 | 0,218 | 6 |
| 2 datas 15/set + 15/out | 0,836 | 0,23 | 0,57 | 0,196 | 5 |
| 2 datas 15/set + 5/nov | 0,847 | 0,30 | 0,59 | 0,174 | 5 |
| 3 datas 15/set + 15/out + 15/nov | 0,845 | 0,31 | 0,58 | 0,177 | 5 |
| Fora da amostra: combo (5/nov + 15/jan), teste 2004–24 | 0,844 | 0,52 | 0,65 | 0,145 | 1 |
| Fora da amostra: data única (15/jan), teste 2004–24 | 0,919 | 0,47 | 0,71 | 0,146 | 1 |

  - Solo médio: mesma figura (melhor data única: pior ano 0,25; combinações fixas: 0,11 a 0,19).
  - **Por que não funciona:** nos anos de seca que o IBGE registra, a falta de água pega todos os plantios de set a nov ao mesmo tempo. Em 2011/12: 0,53 (15/set), 0,30 (15/out), 0,40 (15/nov); em 2021/22: 0,27, 0,20, 0,48. Só os plantios de dez–jan escapam (0,7 a 1,0). As datas de set–nov são muito correlacionadas.
  - A "melhor data única" em janeiro é em parte um artefato: o modelo só mede água e não desconta o menor potencial do milho tardio. Isso levou à variação A1-3.
- **Resultado, cebola em Ituporanga (solo médio):** melhor data única (5/jun) média 0,942, pior ano 0,65; habitual (15/jul) 0,938 e 0,76; 2 datas (15/jun + 15/jul) 0,940 e 0,72; 3 datas (jun + jul + ago) 0,929 e 0,72. Nenhum ano com perda > 40% em data nenhuma. Os 6 piores anos da cebola no IBGE (2023, 1989, 2008, 2017, 2011, 2012) têm rendimento hídrico simulado de 0,79 a 1,0: **a falta de água não explica as quebras da cebola**, que vêm de excesso de chuva e doença [INFERÊNCIA].
- **Gráfico:** `sessoes/A1/a1_23_risco_retorno.svg` (painel da esquerda): média × pior ano. As combinações (quadrados) ficam abaixo e à esquerda da melhor data única.

## 3. Validação
- **Contra a linha de base (melhor data única):** o pior ano piora de 0,47 para 0,23–0,31 (−16 a −24 pp) e a média cai de 0,945 para 0,84 (−10 pp). Fora da amostra: +5 pp no pior ano, −7,5 pp na média. **Não atinge.**
- **Contra a data habitual (25/set), só como informação:** 2 datas (15/set + 5/nov) melhora o pior ano em +14 pp (0,16 para 0,30) e o desvio em −20%, sem custo na média (+1,5 pp). Mas o ganho grande é em 1985/86 (0,16 para 0,52); nos anos de quebra do IBGE, 2021/22 e 2011/12, o ganho é de só +5 e +6 pp (0,25 para 0,30; 0,36 para 0,43), e o P10 sobe só 2 pp.
- **Cebola:** contra a melhor data única, +7 pp no pior ano (meta 10), custo de 0,2 pp. **Não atinge.**
- **Fonte externa:** a Epagri/Cepa relatou que, na estiagem de 2021/22, o Oeste foi a região mais atingida e que o milho plantado em setembro foi quase todo perdido; o modelo mostra a mesma coisa para todos os plantios de set–nov. IBGE PAM (A1-1): 2012 e 2022 são os anos de quebra, e o modelo os marca em todas as datas de set–nov.
- **O critério de sucesso foi atingido?** **Não.**

## 4. Régua (1 a 5)
| Critério | Nota | Por quê (uma frase) |
|---|---|---|
| Problema real | 3 | Perder a lavoura inteira numa estiagem é real, mas o escalonamento usual (set–nov) não é o que separa quem perde de quem não perde. |
| Tamanho do impacto | 2 | No melhor caso (contra a data habitual), o pior ano melhora 14 pp graças a uma safra só. |
| Resolve de fato | 1 | Dividir a área dentro de set–nov não protege nos anos de La Niña, quando todas as datas secam juntas. |
| Validade | 2 | Testado com dado oficial e conferido com o IBGE e a Epagri, mas o sinal não supera a linha de base. |
| Muda a decisão | 1 | Não há razão, pelos dados, para mudar de "tudo numa data boa" para "várias datas próximas". |
| Simples e factível | 4 | É uma conta simples sobre o mesmo motor. |
| Alinhamento com o desafio | 3 | Compara estratégias de manejo com dados da NASA, mas não é rotação. |
| Diferencial | 2 | O ZARC não mostra a correlação entre datas, mas o resultado é negativo. |
| Cabe no hackathon | 5 | Já está pronto. |
| **Total (máx. 45)** | **23** | |

## 5. Veredito
**Descartada.** Escalonar em 2 ou 3 datas próximas não reduz a perda no pior ano contra a melhor data única, nem no milho (Extremo Oeste) nem na cebola (Ituporanga). Resultado negativo útil: em SC, as estiagens de La Niña pegam set–nov inteiro.

## 6. Relação com o controle
Não compete. O achado ajuda o controle a **não prometer** "plante em etapas" como mitigação genérica (está na tabela de "caminhos de ação" do `contexto.md`). Se o controle mostrar uma estratégia de datas, que seja cedo contra tarde (ver A1-3), não datas vizinhas.

## 7. Limites e o que não foi testado
- Rendimento relativo só pela água (FAO-33) e pela geada: sem potencial por data, sem calor, sem excesso de chuva ou doença (decisivo na cebola).
- Ciclo em dias fixos; grade POWER de ~50 km; as datas de um mesmo talhão recebem a mesma chuva (no campo, a chuva de verão varia entre talhões, o que daria um pouco mais de diversificação).
- Custos de dividir o plantio (mais idas à lavoura, semente, silagem em duas vezes) não foram contados.
- Parâmetros da cebola da FAO-56/33, não de portaria (o ZARC só tem cebola irrigada para Ituporanga).

## 8. Fontes
- NASA POWER (arquivos locais `dados/power_sao_miguel_do_oeste.json`, `dados/power_ituporanga.json`).
- ZARC 2026/27, milho 1ª safra, São Miguel do Oeste (janela dec 22–36 e 1–3): https://dados.agricultura.gov.br/dataset/tabua-de-risco-zoneamento-agricola-de-risco-climatico
- IBGE PAM, tabela 1612, milho em São Miguel do Oeste (`sessoes/A1/ext/pam_smo.json`) e cebola em Ituporanga 4208500 (arquivo baixado pela sessão B4, `sessoes/B4/ext/pam_cebola_ituporanga.json`, só leitura).
- Epagri/Cepa sobre a estiagem de 2021/22: https://www.noticiasagricolas.com.br/noticia/307520 e https://www.agrolink.com.br/noticias/veja-como-a-seca-esta-afetando-a-producao-agricola-em-sc_442148.html
- FAO-56 e FAO-33.
