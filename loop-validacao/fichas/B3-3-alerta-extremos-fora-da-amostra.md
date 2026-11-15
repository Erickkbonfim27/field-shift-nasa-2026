# B3-3 · Alerta só de ano extremo de água (versão ajustada de B3-1 e B3-2), testado fora da amostra

Sessão: B3 · Trilha: B · Região: microrregiões vizinhas (Chapecó e Concórdia para o milho; Rio do Sul e Tabuleiro para a cebola) · Tentativa 3 de 4 · Data: 2026-11-14

## 1. Ideia (escrita antes do teste)
- **Hipótese:** B3-1 e B3-2 mostraram que o balanço hídrico do POWER não separa bem os anos médios, mas parece pegar os **extremos**. Se isso for real, os mesmos limiares, **fixos e sem recalibrar**, devem funcionar em outras microrregiões, com outro ponto do POWER e outro rendimento do IBGE.
- **Problema que ataca (e para quem):** o mesmo de B3-1 (estiagem no milho do leite, Extremo Oeste) e B3-2 (excesso de chuva na cebola, Alto Vale). Aqui a ferramenta só fala nos anos fora da curva: "este ano está entre os 10% mais secos (ou úmidos) dos últimos 40".
- **Decisão que muda:** milho → silagem antes do grão, comida extra para as vacas; cebola → pulverização e colheita antecipadas, cura em galpão.
- **Regras fixas (tiradas de B3-1 e B3-2, não mudam):**
  - Milho: alerta de seca severa se ISNA de 20/set a 10/jan < **0,75** (plantio 20/set, solo médio, mesmos parâmetros de B3-1).
  - Cebola: alerta de excesso se o excedente hídrico de 1/set a 30/nov ≥ **360 mm** (transplante 1/ago, mesmos parâmetros de B3-2).
- **Dados novos:** NASA POWER diário (mesmos parâmetros) em Chapecó (−27,10; −52,62), Concórdia (−27,23; −52,03), Rio do Sul (−27,21; −49,64) e Alfredo Wagner (−27,70; −49,33). Rendimento do IBGE PAM (tabela 1612) das microrregiões 42002, 42005, 42011 e 42017. Uma microrregião só entra se tiver cebola (ou milho) plantada em pelo menos 20 anos.
- **Critério de sucesso (definido antes), por cultura, juntando as microrregiões:**
  - pelo menos 3 anos com alerta (senão: inconclusivo);
  - **≥ 50% dos anos com alerta são anos ruins** (rendimento ≤ 85% da mediana dos 6 vizinhos), e isso é pelo menos o dobro da frequência de anos ruins;
  - rendimento relativo médio dos anos com alerta ≤ 0,85.
- **Linha de base:** "média dos anos": alertar ao acaso acerta na frequência histórica de anos ruins de cada microrregião.

## 2. Teste
- **Dados oficiais usados:**
  - NASA POWER diário, comunidade AG, 1984–2025, mesmos parâmetros, em 4 pontos novos. Baixados com `curl` para `sessoes/B3/power_extra/`, porque não estavam em `dados/`.
  - Conferi as células: Chapecó, Concórdia e Rio do Sul são células diferentes das originais (a chuva coincide em só 7 a 17% dos dias). **Alfredo Wagner cai na mesma célula de Ituporanga** (chuva igual em 100% dos dias). Na microrregião de Tabuleiro, só o rendimento é independente.
- **Método:** as mesmas funções de B3-1 e B3-2, com os limiares fixos acima, sem recalibrar nada. Uma microrregião por ponto, 36 safras cada (1990–2025). Script: `sessoes/B3/teste3_extremos_fora_amostra.py`. Saída: `sessoes/B3/teste3_resultado.json`.
- **Resultado [CÁLCULO]:**

  | Microrregião | Anos ruins / anos | Anos com alerta (indicador; rendimento relativo) |
  |---|---|---|
  | Milho, Chapecó (42002) | 8/36 | 2009 (0,75; 0,87), **2012 (0,74; 0,60)**, **2022 (0,65; 0,73)** |
  | Milho, Concórdia (42005) | 7/36 | **2022 (0,69; 0,78)** |
  | Cebola, Rio do Sul (42011) | 6/36 | 1997 (474 mm; 1,00), 2008 (550; 0,90), **2015 (438; 0,56)**, **2023 (592; 0,78)** |
  | Cebola, Tabuleiro (42017) | 6/36 | 1997 (447; 0,86), **2008 (507; 0,84)**, **2015 (369; 0,77)**, 2023 (661; 0,90) |

  | Juntando | Frequência de anos ruins (base) | Alertas | Alertas em ano ruim | Rendimento relativo médio: com alerta / sem alerta |
  |---|---|---|---|---|
  | **Milho** | 0,21 (15/72) | 4 | **3 (75%)** | **0,75** / 1,01 |
  | **Cebola** | 0,17 (12/72) | 8 | **4 (50%)** | **0,82** / 1,03 |

- **Gráficos:**
  - `sessoes/B3/teste3_milho_fora_amostra.svg`: só os pontos à esquerda do limiar de 0,75 caem abaixo da linha de ano ruim.
  - `sessoes/B3/teste3_cebola_fora_amostra.svg`: os anos à direita de 360 mm ficam quase todos abaixo de 1,0, mas só metade passa a linha de 0,85.

## 3. Validação
- **Contra a linha de base:**
  - Milho: 75% dos alertas em ano ruim, contra 21% ao acaso (3,6 vezes).
  - Cebola: 50% contra 17% (2,9 vezes).
  - Contando os anos-região como independentes, a chance de esse resultado sair por sorte é de 2,7% (milho) e 2,3% (cebola) [CÁLCULO, hipergeométrica]. **Mas os anos-região não são independentes:** os alertas são os mesmos 2 a 4 eventos climáticos (2012 e 2022 no milho; 2008, 2015 e 2023 na cebola) vistos em microrregiões vizinhas. Só Rio do Sul, com célula própria, dá 2 de 4 (p = 0,12).
- **Fonte externa:** os eventos com alerta e quebra são os mesmos que a Epagri registra: estiagem de 2021/22 no Extremo Oeste (até 50% de perda prevista), cebola em 2015 (−55% em SC) e cebola em 2023/24 (−27,5% em SC). Links em B3-1 e B3-2. **Bate.**
- **O critério de sucesso foi atingido?** **Sim, por pouco na cebola.**
  - Milho: 4 alertas (≥ 3), 75% (≥ 50% e ≥ 2 × 21%), média de 0,75 (≤ 0,85).
  - Cebola: 8 alertas, 50% (exatamente no limite e ≥ 2 × 17%), média de 0,82.

## 4. Régua (1 a 5)
| Critério | Nota | Por quê (uma frase) |
|---|---|---|
| Problema real | 5 | As mesmas perdas documentadas pela Epagri em B3-1 e B3-2 (milho do leite e cebola). |
| Tamanho do impacto | 3 | Só fala em cerca de 1 a cada 10 anos, mas são os anos que mais doem (quebras de 25 a 50%). |
| Resolve de fato | 3 | Nos anos extremos (2012, 2022, 2015, 2023), muda a decisão (silagem; manejo e colheita da cebola), e isso se manteve fora da amostra. |
| Validade | 3 | Supera a linha de base fora da amostra e bate com a Epagri, mas a amostra é pequena: 2 a 4 eventos independentes, e a célula de Tabuleiro é a mesma de Ituporanga. |
| Muda a decisão | 3 | Ação clara nos anos de alerta; nos outros anos a ferramenta fica em silêncio, o que é honesto mas pouco visível. |
| Simples e factível | 5 | Dois limiares sobre o balanço que já existe. |
| Alinhamento com o desafio | 3 | Acompanhamento da safra e estratégia alternativa no ano extremo; não é a rotação em si. |
| Diferencial | 3 | O ZARC não acompanha a safra; os boletins da Epagri/Ciram já falam de estiagem, mas não por talhão nem com o histórico de 40 anos. |
| Cabe no hackathon | 5 | Pronto; vira um cartão "ano fora da curva" no WhatsApp. |
| **Total (máx. 45)** | **33** | |

Aprovada só com 3+ em problema real, resolve de fato e validade.

## 5. Veredito
**Aprovada, com ressalva.** Usar o balanço hídrico do POWER em SC só como **alerta de ano extremo**: o milho com ISNA < 0,75 até 10/jan e a cebola com excedente ≥ 360 mm em set–nov. Não usar para graduar os anos comuns. A ressalva é a amostra: poucos eventos e regiões vizinhas.

## 6. Relação com o controle
**Complementa e calibra o controle.** O controle dá a chance de colher antes do plantio. Em SC, essa chance fica alta quase todo ano, e o balanço não separa os anos comuns (B3-1, B3-2). O que o dado sustenta aqui é um segundo momento: durante a safra, "este ano está entre os 10% mais secos (ou mais úmidos) dos últimos 40; nesses anos a quebra foi de x%; faça y".

**Na demo:** um cartão de alerta para o produtor de leite em janeiro de 2022 ("faça silagem agora") e outro para o de cebola em outubro de 2023, cada um com a frase do histórico real do ponto [CÁLCULO, B3-1 e B3-2, 1990–2025]:
- milho no Extremo Oeste: "em 36 anos, o ISNA ficou abaixo de 0,75 até 10/jan em 4 anos (1996, 2009, 2012, 2022); em 2 deles o milho quebrou mais de 15%, e nos outros 2 caiu cerca de 9%";
- cebola em Ituporanga: "em 36 anos, passou de 360 mm de excedente em set–nov em 4 anos (1997, 2008, 2015, 2023); em 3 deles a cebola quebrou mais de 15%".

## 7. Limites e o que não foi testado
- Os limiares foram tirados de B3-1 e B3-2 e só testados em microrregiões vizinhas, com os mesmos eventos climáticos. Não há teste em anos novos (2026 ainda não tem PAM).
- Alfredo Wagner tem a mesma célula do POWER que Ituporanga.
- Não testei a seca na cebola (2017, 2020/21) junto com o excesso, nem o excesso no milho.
- Os mesmos limites de B3-1 e B3-2: POWER a ~50 km, PAM estimado, parâmetros FAO-56, IMERG e SMAP não testados.
- Não medi o ganho econômico da ação no ano de alerta.

## 8. Fontes
- NASA POWER diário, pontos de Chapecó, Concórdia, Rio do Sul e Alfredo Wagner: `sessoes/B3/power_extra/` [DADO].
- IBGE SIDRA, tabela 1612, microrregiões 42002, 42005 (milho) e 42011, 42017 (cebola): `sessoes/B3/externo/` [DADO].
- Epagri: as mesmas fontes de B3-1 e B3-2.
