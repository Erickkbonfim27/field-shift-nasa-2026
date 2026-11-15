# A2-4 · El Niño sabido em agosto muda o tipo de risco de out–jan (menos seca, mais excesso de chuva)

Sessão: A2 · Trilha: A · Região: Oeste de SC (4 células novas do POWER; SMO e Ituporanga só como referência) · Tentativa 4 de 4 (teste confirmatório do padrão visto em A2-1 e A2-3) · Data: 2026-11-14

## 1. Ideia (escrita antes do teste)
Critério gravado antes de olhar a chuva de out–jan em qualquer ponto (`sessoes/A2/CRITERIOS_ANTES_DO_TESTE.md`, seção A2-4, com a correção de desenho feita antes de rodar).
- **Hipótese:** o padrão de A2-1 e A2-3 foi assimétrico. A La Niña não dá sinal, mas nas safras de El Niño quase não há seca. Se for real, o El Niño sabido no fim de agosto (ONI de JAS ≥ +0,5) não "prevê ano bom": ele **troca o tipo de risco**, com menos seca e mais excesso de chuva em out–jan.
- **Problema que ataca (e para quem):** o produtor de milho e leite do Oeste de SC, que monta o plano da safra de verão (ago–out). Em ano de El Niño, o risco a gerenciar muda.
- **Decisão que muda:** a recomendação passa de "proteger contra seca" para "preparar para excesso": colheita da silagem na janela seca, controle de doença, conservação do solo contra erosão e drenagem.
- **Critério de sucesso (definido antes):** todos: (1) em ≥ 3 de 4 células novas, P(seco | El Niño) ≤ 0,20 **e** P(chuvoso | El Niño) ≥ 0,50 (base 0,33 cada); (2) BSS LOO médio do "seco" > 0,05; (3) IBGE: safras de El Niño com menos quebras de milho que as outras em ≥ 3 de 4 microrregiões. Muda a decisão se o risco seco cair para ≤ 20% e o de excesso subir para ≥ 50%.
- **Linha de base:** média de todos os anos (1 em 3 para cada tercil).
- **Por que é confirmatório:** o padrão foi visto em SMO e Ituporanga, então esses dois pontos não contam. Baixei 4 células novas do POWER, que eu não tinha olhado.

## 2. Teste
- **Dados oficiais usados:** NASA POWER diário, comunidade AG, 1981–2025, `PRECTOTCORR`, baixado em 14/11/2026 para Chapecó/Xanxerê (-27,10; -52,62), Concórdia (-27,23; -52,03), Itapiranga (-27,17; -53,71) e Palmitos (-27,07; -53,16). Arquivos em `sessoes/A2/dados_novos/`. Correção feita antes de rodar: Dionísio Cerqueira caiu na mesma célula de SMO (chuva idêntica) e Chapecó na mesma de Xanxerê, por isso troquei por Itapiranga e Palmitos.
- **Fonte externa só para separar os anos:** ONI de JAS (NOAA). Safras de El Niño: 1982, 1987, 1991, 1997, 2002, 2004, 2009, 2015 e 2023 (9 de 44).
- **Método:** chuva de 1/out a 31/jan, tercis inferior ("seco") e superior ("chuvoso"); Fisher; Brier LOO (previsão = frequência na fase El Niño / não El Niño, tercis recalculados sem o ano). Script: `sessoes/A2/a2_4_elnino_confirmatorio.py`. Saída: `sessoes/A2/resultados/a2_4.json`.
- **Resultado** [CÁLCULO]:

| Célula nova | Seco, safras de El Niño | Seco, outras safras | Chuvoso, safras de El Niño | Chuvoso, outras safras | Fisher seco / chuvoso | BSS seco / chuvoso |
|---|---|---|---|---|---|---|
| Chapecó/Xanxerê | 1/9 = 11% | 40% | 7/9 = 78% | 23% | 0,11 / 0,004 | +0,04 / +0,18 |
| Concórdia | 0/9 = 0% | 43% | 6/9 = 67% | 26% | 0,01 / 0,03 | +0,13 / +0,07 |
| Itapiranga | 1/9 = 11% | 40% | 6/9 = 67% | 26% | 0,11 / 0,03 | +0,04 / +0,07 |
| Palmitos | 1/9 = 11% | 40% | 6/9 = 67% | 26% | 0,11 / 0,03 | +0,04 / +0,07 |
| *SMO (já visto)* | *11%* | *40%* | *67%* | *26%* | | *+0,04 / +0,07* |
| *Ituporanga (já visto)* | *11%* | *40%* | *56%* | *29%* | | *+0,04 / +0,01* |

  - A única safra de El Niño seca foi 1991/92 nas células do oeste e 2004/05 em Itapiranga e Ituporanga.
  - **Exploratório (não definido antes):** nos 4 El Niños fortes (ONI de JAS ≥ 1,0: 1987, 1997, 2015 e 2023), out–jan foi chuvoso em 3 de 4 (SMO: 1.000 a 1.145 mm, contra 770 mm do limite do tercil superior) e normal em 1987. O ONI de JAS de **2026 é +2,16**, mais forte que todos os anos da série.
- **Gráfico:** `sessoes/A2/a2_4_el_nino_tipo_de_risco.svg`. Em todas as células, as safras de El Niño quase não têm out–jan seco (0% a 11% contra ~40%) e em dois terços ou mais têm out–jan chuvoso (contra ~25%).

## 3. Validação
- **Contra a linha de base:** seco, 11% contra 33% da média (40% nas outras safras); chuvoso, 67% a 78% contra 33%. BSS do "seco" médio de +0,06 (passa raspando), e do "chuvoso" entre +0,07 e +0,18.
- **Fonte externa:**
  - IBGE PAM, tabela 1612, milho, quebra < 80% do normal, por microrregião (safras de El Niño contra as outras) [DADO + CÁLCULO]: SMO 14% contra 19%; Chapecó 14% contra 15%; Xanxerê 0% contra 19%; Concórdia 14% contra 19%. São 4 de 4 na direção esperada, mas por margem pequena: é sempre a mesma colheita de 2005 (seca de 2004/05, um El Niño fraco), contra 7 safras. O rendimento médio em El Niño é quase igual ao dos outros anos (0,95 a 1,04 contra 0,97 a 0,99). Ou seja, o IBGE não mostra "ano melhor": mostra menos quebra por seca, o que é coerente com a "troca de risco", e não um ganho. Links: [42001](https://apisidra.ibge.gov.br/values/t/1612/n9/42001/v/112/p/all/c81/2711), [42002](https://apisidra.ibge.gov.br/values/t/1612/n9/42002/v/112/p/all/c81/2711), [42003](https://apisidra.ibge.gov.br/values/t/1612/n9/42003/v/112/p/all/c81/2711), [42005](https://apisidra.ibge.gov.br/values/t/1612/n9/42005/v/112/p/all/c81/2711).
  - Literatura: Grimm et al. (1998, 2000) descrevem chuva acima do normal na primavera do Sul do Brasil em anos de El Niño [INFERÊNCIA, citado de memória, conferir]. **Bate.**
- **O critério de sucesso foi atingido?** **Sim, nos três itens definidos antes, mas com folga pequena.** C1: 4 de 4 células. C2: BSS 0,060 contra o limiar de 0,05. C3: 4 de 4 microrregiões, por 1 colheita.

## 4. Régua (1 a 5)
| Critério | Nota | Por quê (uma frase) |
|---|---|---|
| Problema real | 4 | Seca e excesso de chuva derrubam milho, silagem e pasto no Oeste, e a safra 2026/27 começa sob um El Niño forte (ONI de JAS +2,16). |
| Tamanho do impacto | 3 | Vale para cerca de 1 safra em 5 (9 de 44), mas nelas o risco seco cai de ~40% para ~11% e o chuvoso sobe de ~25% para ~70%. |
| Resolve de fato | 3 | Muda o conselho nos anos de El Niño ("o risco deste ano é excesso, não seca"), o que vale para a safra atual. |
| Validade | 3 | Passou nos critérios definidos antes em células novas, mas as células são correlacionadas (mesmo campo MERRA-2), n = 9, o BSS do seco passa raspando e o IBGE confirma por margem pequena. |
| Muda a decisão | 3 | Passa o limiar definido (≤ 20% seco e ≥ 50% chuvoso), mas o efeito do excesso de chuva na cultura não foi modelado. |
| Simples e factível | 3 | O cálculo é trivial; para obedecer à regra de dados, o índice Niño 3.4 precisa ser calculado com a TSM do ERA5 (Resources), o que pede conta no Copernicus. |
| Alinhamento com o desafio | 3 | Dá previsibilidade para escolher a estratégia, mas hoje depende de um índice externo (NOAA). |
| Diferencial | 3 | O boletim de ENSO já existe; o novo é traduzir o ENSO em "chance de seca e de excesso por estratégia, no seu lugar". |
| Cabe no hackathon | 4 | O dado é leve (uma série mensal de TSM) e entra como filtro dos anos no motor que já existe. |
| **Total (máx. 45)** | **29** | |

## 5. Veredito
**Ajustar** (passa no mínimo de 3 em problema real, resolve de fato e validade). O El Niño não prevê "ano bom": ele **troca o tipo de risco** de out–jan no Oeste de SC, com menos seca e mais excesso. Ajustes antes de usar no produto:
1. Calcular o índice Niño 3.4 com a TSM do ERA5, para cumprir a regra de dados.
2. Mostrar sempre a probabilidade dos anos parecidos ("em 9 safras de El Niño, 1 seca e 6 chuvosas"), nunca uma previsão.
3. Modelar ou ao menos sinalizar o dano por excesso de chuva, que o balanço hídrico atual não vê.

A La Niña continua sem sinal útil (A2-1 e A2-3).

## 6. Relação com o controle
**Complementa** o controle. É um filtro de "anos parecidos com este" em cima da probabilidade histórica que o controle já calcula: em vez de "em 10 anos", fica "em 10 anos **de El Niño**". Na demo: "Safra 2026/27, El Niño forte. Nos 9 El Niños desde 1981, out–jan foi seco em 1 e chuvoso em 6. O risco deste ano é excesso de chuva: planeje a colheita da silagem e a proteção do solo." Junto, mostrar que para a La Niña o histórico não autoriza um conselho diferente.

## 7. Limites e o que não foi testado
- **As células não são independentes.** A chuva diária do POWER entre elas tem correlação de 0,76 a 0,97, e três delas deram o mesmo resultado. Na prática, é um sinal regional com n = 9 El Niños.
- Usei o padrão depois de vê-lo em SMO e Ituporanga. As células novas reduzem, mas não eliminam, o viés de escolha (o campo de chuva é o mesmo).
- O efeito do excesso de chuva na produção não foi testado. O IBGE mostra só que não há mais quebra; não mostra ganho.
- El Niño forte (2026, ONI de JAS +2,16) não tem análogo na série. O resultado exploratório (3 de 4 fortes chuvosos) tem n = 4.
- ONI é fonte externa (NOAA). A versão com a TSM do ERA5 não foi testada.
- Ituporanga e cebola: o excesso de chuva em out–dez é o período de bulbificação e colheita da cebola, mas isso não foi testado aqui.

## 8. Fontes
- NASA POWER diário, AG, 1981–2025: `sessoes/A2/dados_novos/power_{chapeco,concordia,itapiranga,palmitos}.json` (baixados em 14/11/2026) e `loop-validacao/dados/` [DADO].
- NOAA CPC, ONI: https://www.cpc.ncep.noaa.gov/data/indices/oni.ascii.txt [DADO externo, só para separar os anos].
- IBGE SIDRA, PAM, tabela 1612, milho em grão, rendimento médio, microrregiões 42001, 42002, 42003 e 42005 (links acima) [DADO externo, conferência].
- Grimm, Ferraz e Gomes (1998), *J. Climate* 11; Grimm, Barros e Doyle (2000), *J. Climate* 13 [citados de memória, conferir].
