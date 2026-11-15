# A4-1 · Quando trocar milho por sorgo (regra pelo clima no plantio)

Sessão: A4 · Trilha: A · Região: São Miguel do Oeste · Tentativa 1 de 4 · Data: 2026-11-14

## 1. Ideia (escrita antes do teste)
Registrada antes de rodar dados em `sessoes/A4/00_criterios_pre_teste.md`.
- **Hipótese:** em São Miguel do Oeste (SMO) existe uma regra objetiva, que o agricultor consegue checar no dia do plantio, que diz quando o sorgo dá mais segurança que o milho para silagem. As regras testadas foram a data de plantio, a umidade do solo (GWETROOT) no dia e a chuva dos 30 dias anteriores.
- **Problema que ataca (e para quem):** o produtor de leite do Extremo Oeste perde silagem de milho nas estiagens. Em 2021/22, SC deixou de colher 32% do milho silagem previsto, e o Oeste e o Extremo Oeste foram as regiões mais atingidas (Epagri/Cepa) [DADO].
- **Decisão que muda:** plantar sorgo em vez de milho naquele talhão e naquela data.
- **Critério de sucesso (definido antes):** a regra, com o limiar escolhido deixando um ano de fora, precisa cumprir as quatro condições:
  1. reduzir em ≥ 30% os casos de perda (rendimento relativo < 0,6) frente a "sempre milho";
  2. não baixar o rendimento médio ajustado;
  3. acertar ≥ 60% das vezes em que manda trocar;
  4. mandar trocar em ≥ 1 de cada 10 casos.
- **Linha de base:** "sempre milho", que é o que o agricultor faz hoje. Segunda referência: "sempre sorgo".

## 2. Teste
- **Dados oficiais usados:** NASA POWER diário (comunidade AG), ponto -26,725; -53,518, de 1984 a 2025, grade de cerca de 50 km. Variáveis: PRECTOTCORR, T2M, T2M_MAX, T2M_MIN, RH2M, WS2M, ALLSKY_SFC_SW_DWN e GWETROOT.
- **Método:**
  1. Calculei a ET0 pelo método de Penman-Monteith (FAO-56) e rodei um balanço hídrico diário tipo balde para milho e sorgo de silagem (110 dias cada). O rendimento relativo sai pelo Ky de cada fase (FAO-33), e a geada (T2M_MIN ≤ 2 °C no crescimento ou na floração) corta 70%.
  2. Simulei 41 safras × 19 decêndios de plantio (21/ago a 21/fev), num total de 779 casos, em três solos: argiloso profundo, médio e raso (0,5 m).
  3. "A troca compensou" quando sorgo × 0,85 > milho. O fator 0,85 é o valor da silagem de sorgo em relação à de milho [ESTIMATIVA]; a sensibilidade foi de 0,75 a 0,95.
  4. As três regras foram escolhidas com validação cruzada deixando um ano de fora.

  Scripts: `sessoes/A4/modelo_smo.py` e `sessoes/A4/a4_1_milho_sorgo.py`.
- **Resultado** [CÁLCULO]:

  | Solo | Perdas: sempre milho | Perdas: sempre sorgo | Média milho | Média sorgo × 0,85 | Casos em que a troca compensa |
  |---|---|---|---|---|---|
  | Argiloso | 42/779 (5%) | 5 | 0,923 | 0,822 | 16% |
  | Médio | 94 (12%) | 14 | 0,865 | 0,796 | 27% |
  | Raso | 169 (22%) | 35 | 0,796 | 0,763 | 37% |

  - **Nenhuma das três regras** (data, GWETROOT, chuva de 30 dias) supera "sempre milho" com o fator 0,85, em nenhum solo. No ano deixado de fora, a validação cruzada sempre escolhe "nunca trocar". A exceção é a regra de chuva de 30 dias no solo raso: ela troca em 14 casos e acerta 5 (36%).
  - Com o fator 0,95, a regra de GWETROOT no solo argiloso reduz as perdas de 42 para 37 (−12%), mas baixa a média e acerta só 21% das trocas.
  - **Em quantos anos a troca teria compensado** (plantio em 1/out, de 41 safras): 9 no solo argiloso, 15 no médio e 21 no raso. Os anos são os de estiagem: 1985/86, 2004/05, 2008/09, 2011/12, 2020/21, 2021/22 e 2024/25. Pelo histórico de clima, ninguém sabia no dia do plantio que esses anos seriam secos.
  - **Ponto de equilíbrio do fator** (o sorgo empata com o milho na média) [CÁLCULO]: 0,95 no solo argiloso, 0,92 no médio e 0,89 no raso. Quem decide é o **solo** e o **valor da silagem de sorgo**, não o clima do plantio.
- **Gráficos:**
  - `sessoes/A4/fig_a4_1_ano_a_ano.svg`: milho contra sorgo × 0,85 safra a safra. O sorgo só fica acima nos anos secos.
  - `sessoes/A4/fig_a4_1_por_decendio.svg`: em quantas safras a troca compensa, por data. Só o solo raso, com plantio em outubro, chega a cerca de metade das safras.

## 3. Validação
- **Contra a linha de base:** em casos de perda, 42 com a regra (validação cruzada) contra 42 com "sempre milho" no solo argiloso; 94 contra 94 no médio; 169 contra 167 no raso. Não há ganho.
- **Fontes externas:**
  - **IBGE/PAM, tabela 1612, produtividade do milho grão em SMO (4217204):** comparei com o modelo plantando de 11/set a 21/out. O IBGE mostra 6 quedas ≥ 20% (1991, 2002, 2005, 2012, 2021 e 2022). No solo argiloso, o modelo acerta 2: 2012 e 2022, as duas maiores (−62% e −59%). Erra 4 e dá 2 alarmes falsos (1986 e 2009). A correlação é r = 0,31 (n = 41). No solo médio acerta 3 de 6; no raso, 6 de 6, mas com 10 alarmes falsos. Bate em parte. A área de milho grão no PAM caiu de 25 mil ha (1989) para 700 ha (2025) [DADO], porque o milho para silagem não entra nessa série. Por isso a conferência é indireta.
  - **ZARC 2026/27 de SMO** (extrato da sessão A1, `sessoes/A1/ext/zarc_2627_smo_itu.csv`):
    - Milho 1ª safra: risco de 20% em solos AD4–AD6 de 21/ago a 21/jan, e de 30–40% em AD2–AD3.
    - Sorgo forrageiro: 20% de 11/set a 11/dez em todos os solos; na 2ª safra, 20% de 21/dez a 21/fev.
    - **O ZARC não zoneia milho 2ª safra em SMO.**

    Isso bate com "o sorgo é mais seguro em solo de pouca água". Não bate com o modelo no plantio tardio: o ZARC exclui o milho depois de 21/jan, e o modelo não vê risco ali porque não trata frio nem radiação.
  - **Epagri/Cepa:** perda de 32% do milho silagem em SC em 2021/22 e de 29% em 2019/20, com o Oeste mais atingido. O modelo pega 2021/22 (rendimento de 0,41 a 0,50). Em 2019/20 e 2020/21 ele só mostra queda parcial (0,73 a 1,00).
- **O critério de sucesso foi atingido?** **Não.** Nenhuma condição de regra foi cumprida.

## 4. Régua (1 a 5)
| Critério | Nota | Por quê (uma frase) |
|---|---|---|
| Problema real | 4 | Estiagens de 2019 a 2022 tiraram cerca de 30% da silagem de SC, com o Oeste no centro (Epagri/Cepa). |
| Tamanho do impacto | 3 | A troca compensa em 16% a 37% dos casos, conforme o solo, mas só nos anos secos. |
| Resolve de fato | 2 | Nenhuma regra que se pode ver no plantio antecipa esses anos, então a ferramenta não mudaria a escolha. |
| Validade | 2 | Testado com dado oficial e validação cruzada, mas o sinal não supera a linha de base. |
| Muda a decisão | 2 | A regra ótima é "nunca trocar"; o que muda a decisão é o tipo de solo, não o clima. |
| Simples e factível | 4 | O balanço hídrico é o mesmo do protótipo, com dados POWER já baixados. |
| Alinhamento com o desafio | 4 | Compara estratégias de cultura com dados da NASA. |
| Diferencial | 2 | O ZARC já diz que o sorgo tem menos risco em solo de pouca água. |
| Cabe no hackathon | 4 | Já está rodando. |
| **Total (máx. 45)** | **27** | |

## 5. Veredito
**Descartada.** Com dados históricos, não há regra de plantio (data, umidade do solo, chuva recente) que diga em que anos trocar milho por sorgo. A troca compensa em 1 a 4 de cada 10 safras, mas são os anos de estiagem, que ninguém prevê no plantio. A informação útil que sobra vai para a A4-3: o ponto de equilíbrio por solo (fator de 0,89 a 0,95).

## 6. Relação com o controle
Não compete com o controle. Mostra um limite dele: **sem previsão sazonal (fora da aba Resources), a probabilidade histórica não escolhe a cultura ano a ano.** Ela serve para escolher por talhão (solo), não por ano. Na demo, entra como o resultado negativo honesto que leva à A4-3.

## 7. Limites e o que não foi testado
- **Parâmetros do sorgo genéricos (FAO-33/FAO-56), sem calibração para híbridos de SC.** A sensibilidade mostra que **a vantagem de segurança do sorgo depende quase toda do Ky** [CÁLCULO, solo argiloso]:
  - Ky × 1,5: o sorgo perde em 25 casos, contra 42 do milho.
  - Ky × 2: 39 contra 42, e a vantagem some.
  - Kc × 1,15: a troca compensa em 4% dos casos, contra 16% no padrão.
  - Raiz de 1,4 m: muda pouco (20%).

  A conclusão "nenhuma regra funciona" vale em todos esses cenários. O tamanho da vantagem do sorgo não está provado.
- O fator de valor de 0,85 é estimativa. A literatura da Embrapa cita de 72% a 92% (Demarchi et al., 1995) e diferença de cerca de 10% em híbridos modernos. Com 0,90, o sorgo já empata ou ganha na média no solo raso.
- Grade POWER de cerca de 50 km; GWETROOT é do MERRA-2, sem calibração local. O balde é simplificado e não trata frio, radiação, fotoperíodo, pragas nem acamamento.
- O ZARC foi lido do extrato da sessão A1 (portal do MAPA), não baixado por mim. O download direto falhou nesta máquina: conexão encerrada pelo servidor.
- SMAP e IMERG não foram testados (pedem login no Earthdata).

## 8. Fontes
- NASA POWER diário, comunidade AG: `loop-validacao/dados/power_sao_miguel_do_oeste.json`.
- IBGE SIDRA, tabela 1612, município 4217204: https://apisidra.ibge.gov.br/values/t/1612/n6/4217204/v/109,112/p/all/c81/2711,2713 (cópia em `sessoes/A4/externo/`).
- ZARC 2026/27, tábua de risco (MAPA): https://dados.agricultura.gov.br/dataset/tabua-de-risco-zoneamento-agricola-de-risco-climatico. Portarias: milho 236, sorgo forrageiro 315, sorgo granífero 288. Resumo em `sessoes/A4/zarc_smo_resumo.txt`.
- Epagri/Cepa via Notícias Agrícolas: [perda de 32% do milho silagem em 2021/22](https://www.noticiasagricolas.com.br/noticia/309922); [perdas de 43% no milho e cerca de 30% na soja em SC](https://www.noticiasagricolas.com.br/noticia/307520); [avaliação da estiagem de 2019/20](https://www.noticiasagricolas.com.br/noticia/272995).
- Valor da silagem de sorgo: [Revista Cultivar com Embrapa Milho e Sorgo](https://www.revistacultivar.com.br/noticias/producao-de-silagem-de-alta-qualidade-de-sorgo); [RBMS/Embrapa citando Demarchi et al. (1995), 72% a 92%](https://rbms.sede.embrapa.br/ojs/article/download/121/pdf_388/6059).
- FAO-56 (Allen et al., 1998) e FAO-33 (Doorenbos & Kassam, 1979) para Kc, fases e Ky.
