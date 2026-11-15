# A5-2 · Estimar a área de cebola por satélite antes da colheita

Sessão: A5 · Trilha: A · Região: Ituporanga · Tentativa 2 de 4 · Data: 2026-11-14

## 1. Ideia (escrita antes do teste, às 19h22 de 14/11/2026, antes de baixar imagens)
- **Hipótese:** a curva de NDVI do Sentinel-2 (10 m, com máscara de nuvem SCL) até 31 de outubro, cerca de 4 a 6 semanas antes do pico da colheita, separa as lavouras de cebola das outras coberturas no município de Ituporanga. Isso vale porque a cebola fica baixa ou com solo exposto em jun–ago, transplantada em jul–ago, verde em set–out e madura em nov. O fumo, o milho e a soja verdejam mais tarde; o trigo e a aveia, mais cedo. A soma dos pixels classificados dá a área plantada.
- **Problema que ataca (e para quem):** o cebolicultor familiar vende na colheita sem saber se vai sobrar cebola na região. Uma estimativa cedo da área (oferta) ajudaria a decidir se armazena ou vende logo, e como negociar.
- **Decisão que muda:** vender na colheita ou guardar; quanto plantar no ano seguinte.
- **Critério de sucesso (definido antes):**
  - **(a) Erro:** os limiares são calibrados numa safra (2023) e testados em outras (2024, 2025 e, se der tempo, 2022). O erro absoluto contra a área plantada do IBGE PAM tem que ficar em **≤ 15%** em cada safra de teste.
  - **(b) Valor para preço:** o erro médio absoluto (%) nas safras de teste tem que ser **menor que o da linha de base de persistência** (repetir a área do ano anterior do PAM), e o satélite tem que acertar o **sinal da variação** entre as safras.
  - **(c) Antecedência:** usando só imagens até 31/out.
  - Aprovada só se (a), (b) e (c) forem atingidos.
- **Linha de base:** persistência, ou seja, "a área deste ano = a área do ano passado" (IBGE PAM). Conferência adicional: a estimativa de intenção de plantio da Epagri/Cepa, que já sai em junho.

## 2. Teste
- **Dados oficiais usados:**
  - **Sentinel-2 L2A**, tile 22JFQ, por STAC Earth Search (AWS, sem login). B04, B08 e SCL, recortados no município de Ituporanga (33.653 ha), de mai a dez de 2022, 2023, 2024 e 2025. Foram 115 cenas, ~10 s cada, ~680 MB de NDVI intermediário.
  - MODIS não entra aqui: o pixel de 250 m mistura talhões de 1 a 3 ha (ver A5-3).
- **Método:**
  1. `sessoes/A5/scripts/baixa_ndvi_s2.py`: NDVI com máscara SCL (vegetação, solo e água).
  2. `scripts/compostos_s2.py`: mediana por período (JUN, AGO, SET, OUT, NOV, DEZ), com filtro extra de névoa. A SCL deixa passar névoa: em 28/07 e 27/08/2022 a mata aparecia com NDVI ~0,1. O filtro usa pixels de mata como referência, por bloco de 500 m.
  3. `scripts/classifica_cebola.py`: pixel = cebola se AGO < 0,45, mín(JUN, AGO) < 0,40, OUT ≥ T e OUT − AGO ≥ 0,20. Um único parâmetro (T) é calibrado para bater o PAM numa safra. Área = fração classificada entre os pixels com dado × área do município.
  4. Também explorei agrupamentos (k-means) em `scripts/explora_clusters.py`, só para ver as curvas típicas.
- **Desvio do pré-registro (declarado):** a safra de calibração prevista (2023) **não tem nenhum pixel sem nuvem em outubro**. As 9 cenas de set–out de 2023 tinham 0% a 29% do município livre, e as de outubro foram todas descartadas por nuvem ou névoa. Por isso calibrei em 2024, a safra com o outubro mais limpo (97%), e testei em 2022 e 2025. Em 2023 não há estimativa possível até 31/out.
- **Resultado** [CÁLCULO] (`sessoes/A5/resultados/resultado_cebola_s2.json`):
  | Safra | Município visto em outubro | Satélite (até 31/out) | IBGE PAM plantada | Erro do satélite | Persistência (ano anterior) | Erro da persistência |
  |---|---|---|---|---|---|---|
  | 2022 (teste) | 55% | 3.296 ha | 4.000 ha | **−17,6%** | 4.000 ha | 0,0% |
  | 2023 | **0%** | sem estimativa | 4.200 ha | — | 4.000 ha | −4,8% |
  | 2024 (calibração, T = 0,57) | 97% | 4.637 ha | 4.500 ha | +3,0% (ajustado) | 4.200 ha | −6,7% |
  | 2025 (teste) | 83% | 3.220 ha | 4.800 ha | **−32,9%** | 4.500 ha | −6,2% |
  - **Sensibilidade ao limiar:** T ± 0,05 muda a área em −20% a +16% (2024: de 3.714 a 5.368 ha). O ajuste fino do limiar pesa mais que a variação real entre os anos (~7%).
  - **Variação 2024 → 2025:** o satélite diz −31%; o IBGE diz +6,7%. **O sinal está errado.** A causa provável é que as cenas limpas de outubro de 2025 caíram no começo do mês (5, 15 e 20/out), e as de 2024 no fim (20, 25 e 30/out), com a cebola mais verde. Ou seja, a data da imagem que a nuvem deixa passar muda a estimativa mais que a área. [INFERÊNCIA]
  - Usando novembro, depois do corte: 3.670, 4.085 e 5.623 ha. Ainda erra 2025 em +17%, agora para cima.
  - Os grupos do k-means de 2022 mostram uma curva com cara de cebola (baixa em jun–ago, NDVI ~0,64 em out, ~0,30 em dez) somando ~2.700 ha. Outra curva parecida, mas verde até dezembro (provavelmente fumo ou milho cedo), soma ~2.300 ha. **Até 31/out as duas são quase iguais**; só se separam em dezembro, depois da colheita.
- **Gráfico:** `sessoes/A5/A5-2_area_cebola_s2.png`.
  - Os mapas mostram os talhões classificados como cebola (vermelho) e a nuvem de outubro (azul).
  - A curva mostra a área contra o limiar.
  - As barras comparam satélite, IBGE e persistência.

## 3. Validação
- **Contra a linha de base:**
  - Erro médio absoluto nas safras de teste (2022 e 2025): satélite **25,3%** contra persistência **3,1%**.
  - Em 2023 o satélite não dá número; a persistência erra 4,8%.
  - O satélite perde em todas as safras e erra o sinal da variação 2024→2025.
- **Fonte externa:**
  - **IBGE PAM** (t. 5457, Ituporanga = 4208500): área plantada 4.000, 4.200, 4.500 e 4.800 ha em 2022–2025.
  - **IBGE PAM, SC 2000–2025:** a área de cebola varia em média só 4,5% ao ano, enquanto a produção varia 16,9%. Só ~10% da variância da variação anual da produção vem da área; ~90% vem da produtividade. Em Ituporanga, 2015–2025: 6,8% contra 26,8%. [CÁLCULO]
  - **Epagri/Cepa** já publica em junho a intenção de plantio de SC (safra 2025/26: 19,5 mil ha, +1%; revista em outubro para +1,2%), ou seja, a área sai antes do satélite. A PAM 2025 de SC deu 18.395 ha de área colhida. [DADO, via Revista Cultivar; conferir no boletim]
  - O código IBGE de Ituporanga no protocolo estava errado (4208401 é Itapiranga). Usei 4208500 e avisei as outras sessões na pasta de notas.
- **O critério de sucesso foi atingido?** **Não.**
  - (a) Erro ≤ 15%: falhou (−17,6% e −32,9%; 2023 sem dado).
  - (b) Bater a persistência: falhou (25,3% contra 3,1%), com o sinal errado.
  - (c) Antecedência até 31/out: só em 3 de 4 safras houve imagem utilizável.

## 4. Régua (1 a 5)
| Critério | Nota | Por quê (uma frase) |
|---|---|---|
| Problema real | 3 | O vaivém do preço da cebola é real (ver B4-1), mas a área quase não explica a oferta. |
| Tamanho do impacto | 1 | Mesmo perfeita, a área explicaria só ~10% da variação da produção. |
| Resolve de fato | 1 | O erro de 18% a 33% é maior que a variação real entre os anos (~7%), e o sinal da mudança sai errado. |
| Validade | 2 | Testada com Sentinel-2 e conferida no IBGE; perde feio para a persistência. |
| Muda a decisão | 1 | Nenhum agricultor mudaria a venda com uma estimativa pior que "igual ao ano passado". |
| Simples e factível | 2 | 115 cenas, filtro de névoa feito à mão e calibração frágil; a nuvem de primavera tira outubro inteiro em alguns anos. |
| Alinhamento com o desafio | 2 | É oferta e mercado, longe da rotação de culturas. |
| Diferencial | 2 | A Epagri/Cepa já dá a área (intenção de plantio) em junho, antes do satélite. |
| Cabe no hackathon | 2 | Coube como teste, mas um produto confiável pediria rótulos de campo e mais anos. |
| **Total (máx. 45)** | **16** | |

## 5. Veredito
**Descartada.** A estimativa por satélite antes da colheita erra mais (18% a 33%) que simplesmente repetir a área do ano anterior (~3% a 7%), e a nuvem de primavera apagou o outubro inteiro em 2023. Pior: a área é a parte pequena da história. Cerca de 90% da variação da oferta vem da produtividade, o que levou à variação A5-3.

## 6. Relação com o controle
**Não entra.** Compete por tempo e não complementa o controle. Fica a lição útil para o time: em SC, **qualquer coisa que dependa de imagem óptica limpa em set–out é frágil**. Vale para o Sentinel-2 e para o Landsat.

## 7. Limites e o que não foi testado
- Não temos rótulos de campo (talhões de cebola conhecidos). A regra é por fenologia, com um limiar calibrado no total do IBGE, que também é uma estimativa arredondada em centenas de hectares.
- Não testei classificação supervisionada, radar (Sentinel-1, que vê através da nuvem, mas não está na aba Resources) nem Landsat junto com Sentinel-2 (HLS) para ter mais datas.
- O fumo (3.000 ha em Ituporanga, IBGE 2023) e o milho cedo se confundem com a cebola até 31/out.
- O filtro de névoa descarta cenas boas também (ex.: 06/08/2024).
- A Epagri/Cepa por município não foi conferida; só o número estadual, via reportagem.

## 8. Fontes
- Sentinel-2 L2A, Earth Search STAC (Element 84/AWS): https://earth-search.aws.element84.com/v1
- IBGE PAM, tabela 5457 (SIDRA), Ituporanga 4208500 e SC: https://apisidra.ibge.gov.br/values/t/5457/n6/4208500/v/214,216,8331/p/2015-2025/c782/40107
- IBGE, malha municipal (API de malhas v3) e localidades.
- Epagri/Cepa, previsão da safra de cebola 2025/26: https://revistacultivar.com.br/noticias/producao-de-cebola-deve-crescer-6-9-em-sc-na-safra-2025-26
