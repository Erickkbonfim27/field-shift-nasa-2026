# V5 · Semiárido: o motor de água funciona lá?

Data: 14/11/2026. Pasta: `solucao/validacao/V5/`. Marcas: [DADO], [CÁLCULO], [INFERÊNCIA], [ESTIMATIVA].

## Resposta curta
**Parcial.** No Sertão do Ceará, de Pernambuco e da Paraíba, o balanço hídrico acompanha o milho da PAM bem melhor do que em SC (ρ mediano de 0,62 contra 0,28) [CÁLCULO]. Os quatro critérios definidos antes passaram, mas por pouco, e três limites pesam: o feijão fica fraco (ρ mediano 0,31), a Bahia não funciona (ρ 0,07) e o balanço **não supera a soma de chuva da estação** (diferença de +0,06, dentro do ruído). Vale como módulo principal de água para milho no Semiárido do CE/PE/PB. Não vale como motor único.

## 1. Critério definido antes
Arquivo: `CRITERIOS_ANTES_DO_TESTE.md` (escrito antes de cruzar qualquer modelo com a PAM). Resumo:
- C1: mediana de ρ ≥ 0,40 nos 16 pares município × cultura.
- C2: mediana de acerto dos 8 piores anos ≥ 4 de 8 (acaso: 1,6).
- C3: mediana de (ρ do modelo − ρ da chuva bruta) ≥ 0,05.
- C4: ρ ≥ 0,40 em pelo menos metade dos pares.
- "Sustenta" exige C1 a C4. "Parcial": C1 e C2 sem C3, ou só metade dos pares. "Não sustenta": C1 ou C2 falham.
- Mesmo teste da B1-0: PAM dividida pela mediana móvel centrada de 9 anos; 8 piores anos; 1985–2025.

## 2. Método
- **Modelo:** cópia fiel de `prototipo/modelo/risco.py` em `motor.py` (ET0 Penman-Monteith, balde com Ks, Ky por fase, regra de início de chuva de Sivakumar). Teste de fidelidade: `checa_fidelidade.py` reproduz o `risco.py` em Quixadá 2001–2025 sem nenhuma diferença (48 de 48 pares iguais) [CÁLCULO]. Parâmetros não foram ajustados depois de ver o resultado.
- **Dados da solução:** NASA POWER diário 1984–2025 (`PRECTOTCORR`, `T2M`, `T2M_MAX`, `T2M_MIN`, `RH2M`, `WS2M`, `ALLSKY_SFC_SW_DWN`), baixado por curl em `dados/` [DADO]. Solo médio (125 mm/m, tabela GAEZ do protótipo). Sequeiro.
- **Gabarito (só para conferir):** IBGE PAM, SIDRA tabela 5457, variável 112 (rendimento), milho (40122) e feijão (40112) [DADO]. O feijão foi simulado com os parâmetros do caupi do `risco.py` [ESTIMATIVA].
- **Municípios (8, escolhidos antes de ver resultado, nenhum retirado):** Quixadá (2311306), Quixeramobim (2311405), Crateús (2304103), Tauá (2313302) no CE; Serra Talhada (2613909) em PE; Patos (2510808) na PB; Irecê (2914604) e Senhor do Bonfim (2930105) na BA. Altitudes das sedes são aproximadas [ESTIMATIVA].
- **Plantio:** regra de início de chuva (jan–abr; na BA, nov–mar). Ano sem plantio vale y = 0, como no `risco.py`. **Linha de base:** soma de chuva da estação (jan–mai; nov–mar na BA).
- Scripts: `baixar.py`, `motor.py`, `v5_teste.py`, `v5_extra.py`, `v5_perda_total.py`, `graficos.py`.

## 3. Resultado
### 3.1 Teste principal (regra do critério)
Gráfico: `v5_rho_por_municipio.svg`. Dados: `resultado.json`.

| Município | Milho ρ (acerto de 8) | Chuva bruta ρ | Feijão ρ (acerto de 8) | Chuva bruta ρ |
|---|---|---|---|---|
| Quixadá | **+0,50** (5) | +0,46 | +0,30 (5) | +0,34 |
| Quixeramobim | +0,59 (5) | +0,37 | +0,32 (4) | +0,09 |
| Crateús | +0,64 (4) | +0,50 | +0,43 (5) | +0,25 |
| Tauá | +0,67 (5) | +0,57 | +0,40 (4) | +0,49 |
| Serra Talhada | +0,67 (5) | +0,54 | +0,48 (4) | +0,41 |
| Patos | +0,55 (6) | +0,40 | +0,17 (4) | +0,37 |
| Irecê | +0,30 (2) | +0,38 | +0,13 (1) | +0,56 |
| Senhor do Bonfim | −0,08 (2) | +0,17 | 0,00 (2) | +0,27 |

n entre 34 e 41 anos por par [CÁLCULO]. Referência de SC (B1-0): ρ = 0,28 e 3 de 8 [DADO, ficha B1-0].

### 3.2 Critérios
| Critério | Meta | Resultado | Passou |
|---|---|---|---|
| C1 mediana de ρ | ≥ 0,40 | 0,414 | sim, por pouco |
| C2 acerto dos 8 piores | ≥ 4 | 4 (milho 5, feijão 4) | sim |
| C3 modelo − chuva | ≥ +0,05 | +0,058 | sim, por pouco |
| C4 pares com ρ ≥ 0,40 | ≥ 8 de 16 | 9 de 16 (milho 6 de 8, feijão 3 de 8) | sim |

Bootstrap dos anos (600 sorteios, todos os pares juntos): mediana de ρ com intervalo de 90% de 0,28 a 0,55, e chance de 60% de ficar ≥ 0,40. Diferença para a chuva: −0,04 a +0,14, e só 47% de chance de ficar ≥ +0,05 [CÁLCULO]. **C1 e C3 não são estatisticamente firmes.**

### 3.3 Onde funciona e onde não
- **CE, PE e PB (12 pares):** ρ mediano 0,49. Milho 0,62, feijão 0,36. Acerto mediano dos 8 piores: 4,5 [CÁLCULO].
- **Bahia (4 pares):** ρ mediano 0,07. A regra de início de chuva falha: Irecê fica sem plantio em 16 de 41 anos e Senhor do Bonfim em 24, o que não é realista. Com plantio em data fixa (15/dez) o ρ mediano da Bahia sobe para 0,33 [CÁLCULO]. O problema é a regra de plantio, não o balanço.
- **Quixadá (comparação direta com SC):** milho ρ = 0,50, acerto 5 de 8; feijão ρ = 0,30, acerto 5 de 8. Contra SC, o milho tem ρ quase o dobro e 2 acertos a mais. Gráfico: `v5_quixada_milho.svg`.

### 3.4 Sensibilidade (todas as 16 combinações, ρ mediano)
| Variante | ρ mediano |
|---|---|
| Principal (mediana móvel de 9 anos, regra de chuva) | 0,414 |
| Plantio em data fixa (15/fev; 15/dez na BA) | 0,439 |
| Tendência log-linear em vez de mediana móvel | 0,394 (falha C1 por 0,006) |
| PAM sem tirar tendência | 0,429 |
| Só os anos em que houve plantio (sem y = 0) | 0,391 |
| Só "plantou ou não plantou" (a regra de início, sem balanço) | 0,242 |
| Chuva bruta da estação (linha de base) | 0,394 |
| Chuva do ciclo após o plantio | 0,288 |

[CÁLCULO] `resultado.json`, `resultado_extra.json`. Leitura: parte do sinal vem de a regra de início de chuva zerar os anos sem plantio. O balanço acrescenta o resto, mas a chuva simples chega perto.

### 3.5 Análise posterior (não pré-registrada)
Na PAM, o valor "-" (zero no SIDRA) caía fora do teste, como em SC. No Semiárido esses "-" são justamente 1993, 1998, 2012 e 2013, anos de seca e perda total [DADO]. Isso tira da conta os piores anos. Refeito com "-" = rendimento 0 (`v5_perda_total.py`, `resultado_perda_total.json`): ρ mediano 0,44; CE/PE/PB 0,54; milho 0,62; feijão 0,36; Bahia 0,14; acerto de 8 mediano 4. A diferença para a chuva cai para **+0,016**: com as secas dentro, a soma de chuva acompanha o balanço quase igual [CÁLCULO]. Esta versão foi feita depois de ver o problema; o critério oficial continua o da seção 3.2.

## 4. Conferência externa
### 4.1 Anos de seca conhecidos (6 municípios CE/PE/PB × 2 culturas)
`resultado_extra.json`. "Falha" = rendimento simulado < 0,6; PAM = rendimento relativo < 0,6.

| Ano | Pares com falha no modelo | Pares abaixo de 0,6 na PAM | Garantia-Safra (municípios aderidos com perda) |
|---|---|---|---|
| 1993 | 9 de 9 | 8 de 9 | sem dado |
| 1998 | 7 de 7 | 4 de 7 (a PAM zera os demais) | sem dado |
| 2010 | 11 de 12 | 8 de 12 | 93% |
| 2012 | 6 de 6 | 4 de 6 (6 pares sem PAM, "-") | 98% |
| 2015 | 12 de 12 | 7 de 12 | 81% |
| 2016 | 12 de 12 | 8 de 12 | 85% |
| 2014 | 5 de 12 | 0 de 12 | 71% |
| 2017 | 5 de 12 | 3 de 12 | 64% |
| 2005 | 9 de 12 | 2 de 12 | 67% |

- **Acerta:** 1993, 1998, 2010, 2012, 2015 e 2016. A FUNCEME registra a quadra de 2016 em −45,2% (329,3 mm contra 600,7 mm; 8ª pior desde 1951) e a de 2015 em −30,3% [DADO, Diário do Nordeste, reportagem sobre a seca de 2016]. O modelo falha em 12 de 12 pares nos dois anos.
- **Erra ou fica fraco:** 2014 e 2017 (Garantia-Safra alto, modelo ao redor de 0,6 a 0,7); 2005 (alarme que a PAM não confirma, mas o Garantia-Safra paga 67%).
- A PAM de 2014 aparece normal (relativo 1,51) porque a mediana móvel de 9 anos absorve a seca de 2012–2017. Em Quixadá a PAM bruta do milho é 450, 483, 238 e 60 kg/ha em 2013 a 2016, contra 1.800 em 2008 e 1.000 em 2017–2019 [DADO]. **O gabarito esconde a seca longa**, o que subestima o modelo.

### 4.2 Garantia-Safra (série oficial, independente da PAM)
Fonte: MDA/SPA, "Relatório Geral 2019", Tabelas 3 e 4 (`externo/mda_garantia_safra_dados_consolidados.pdf`), pagamento com perda ≥ 50% por seca ou excesso de chuva [DADO]. Calculei a parte dos municípios aderidos com perda comprovada por safra e liguei à colheita no ano de término (safra 2011-2012 = colheita 2012) [INFERÊNCIA]. Gráfico: `v5_garantia_safra.svg`.
- Rendimento simulado médio de 6 municípios (CE/PE/PB) contra a parte com perda, 2003–2018 (n = 16): **ρ = −0,79** (p = 0,0003). PAM mediana: −0,78. Chuva bruta: −0,74 [CÁLCULO].
- Conclusão: o modelo concorda com a série oficial do seguro. A chuva bruta concorda quase igual.
- Limites: o Garantia-Safra cobre todo o Semiárido e muda de adesão; só cobre até a safra 2017/2018; não obtive o pagamento por município, só o total nacional, então a comparação é regional.

## 5. Veredito
**Parcial.**
1. Passou nos quatro critérios pré-definidos (seção 3.2), mas C1 e C3 passam por margem pequena e o bootstrap não os confirma.
2. Em relação a SC, o Semiárido do CE/PE/PB é claramente melhor para o motor de água: milho ρ = 0,62 contra 0,28, e 4 a 5 acertos de 8 contra 3. A razão faz sentido: lá a água é o fator limitante dominante e não há geada [INFERÊNCIA].
3. Não sustenta o motor só de água em três casos: feijão (ρ 0,31), Bahia (0,07, por causa da regra de plantio) e superar a chuva bruta (+0,06; +0,016 na versão com perda total).
4. O Garantia-Safra e as secas de 1993, 1998, 2010, 2012, 2015 e 2016 confirmam o alarme de ano extremo.

## 6. Implicações para a solução
- **Região:** manter o Semiárido (CE central e Sertão de PE/PB) como segunda região do motor modular, com o módulo de água como núcleo, para **milho**. Dizer "x em 10 anos" de seca é defensável ali.
- **Feijão:** usar o módulo de água só como alerta de ano extremo, não como ranking fino entre datas. O ρ de 0,31 não sustenta mais que isso.
- **Bahia (Irecê, Senhor do Bonfim):** não ofertar até trocar a regra de início de chuva (nov–mar) por data de plantio escolhida pelo usuário. Com data fixa o ρ sobe a 0,33.
- **Valor agregado:** como a soma de chuva quase empata com o balanço, o ganho do motor não está em prever melhor o ano, e sim em traduzir o risco para o talhão (solo, ciclo, data de plantio, fase crítica). Mostrar isso ao júri, em vez de prometer precisão que a chuva simples já entrega.
- **Mensagem honesta ao agricultor:** probabilidade de ano de seca e de perda, com o alerta em anos extremos (testado contra Garantia-Safra), sem promessa de rendimento.
- **Conferência no produto:** manter a comparação com o ZARC por decêndio (16 de 18 em Quixadá) e adicionar a série do Garantia-Safra como segundo gabarito.
- **Dados:** não usar PAM "-" como falta; é perda total.

## 7. Limites
- A PAM municipal é estimativa de extensionistas, com valores repetidos (Patos: 12–14% dos anos iguais ao anterior; demais 0–6%) e, em 2023–2025, pode ser revisada [DADO, `v5_teste.py`].
- A mediana móvel de 9 anos reduz o contraste em secas longas (2012–2017). O teste de tendência log-linear dá resultado parecido (0,394).
- Os 6 municípios do CE/PE/PB não são independentes (chuva compartilhada); o bootstrap por ano considera isso, o teste por município não.
- Grade do POWER de ~50 km; altitudes e latitudes de sede; parâmetros FAO, não do ZARC; feijão da PAM misturado (carioca e caupi) simulado como caupi.
- Só sequeiro e solo médio. Não testado: irrigação, rotação entre anos, SMAP/IMERG/GLDAS (pedem login Earthdata), decêndios do ZARC para os 7 municípios novos.
- A análise da seção 3.5 foi feita depois de ver os dados.

## 8. Fontes
- NASA POWER, API diária, comunidade AG, 1984–2025: `dados/power_*.json`.
- IBGE SIDRA, tabela 5457 (PAM): `dados/pam_*.json`.
- MDA/SPA, Garantia-Safra, Relatório Geral 2019: `externo/mda_garantia_safra_dados_consolidados.pdf` (https://www.gov.br/mda/pt-br/acesso-a-informacao/acoes-e-programas/programas-projetos-acoes-obras-e-atividades/programa-garantia-safra/arquivos/dados-consolidados.pdf).
- Diário do Nordeste, "Seca de 2016 no Ceará está entre as piores da história" (FUNCEME, 2016 e 2015): https://diariodonordeste.verdesmares.com.br/regiao/seca-de-2016-no-ceara-esta-entre-as-piores-da-historia-veja-a-lista-1.1565486
- Ficha `loop-validacao/fichas/B1-0-controle.md` (ρ = 0,28 de SC).
