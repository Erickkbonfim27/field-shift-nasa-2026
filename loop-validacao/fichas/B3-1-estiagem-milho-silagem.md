# B3-1 · Alerta de estiagem na floração do milho: grão ou silagem?

Sessão: B3 · Trilha: B · Região: São Miguel do Oeste · Tentativa 1 de 4 · Data: 2026-11-14

## 1. Ideia (escrita antes do teste)
- **Hipótese:** um balanço hídrico diário com dados do NASA POWER, rodado do plantio (20/set) até 10/jan, identifica a tempo os anos em que a estiagem derruba o milho de verão no Extremo Oeste.
- **Problema que ataca (e para quem):** o produtor de leite e milho do Extremo Oeste planta milho pensando em grão. Na estiagem, ele perde o grão e só depois decide salvar a lavoura como silagem, quando a planta já secou e a silagem sai pior. Faltam comida para as vacas e dinheiro.
- **Decisão que muda:** com o alerta em 10/jan (antes do enchimento de grão terminar), ele colhe como silagem de planta inteira em vez de esperar o grão, compra ou planta comida extra (sorgo forrageiro, milheto) e ajusta o lote de vacas.
- **Critério de sucesso (definido antes):**
  - Indicador principal: ISNA (ETa/ETc) do milho acumulado de 20/set a 10/jan, solo médio.
  - "Ano ruim" = rendimento do milho (IBGE PAM, microrregião 42001) ≤ 85% da mediana dos 6 anos vizinhos (t−3 a t+3, sem o ano t).
  - Limiar escolhido por validação deixando um ano de fora (LOO).
  - **Sucesso se:** acerta ≥ 2/3 dos anos ruins, com no máximo 40% de alarmes falsos entre os alertas, e correlação de Spearman ISNA × rendimento relativo ≥ +0,4.
- **Linha de base:** (a) "não fazer nada" (nunca alerta: 0 acertos); (b) "média dos anos" (alerta ao acaso com a frequência histórica de anos ruins). Comparação extra: chuva acumulada de nov–dez (só pluviômetro, sem balanço).

## 2. Teste
- **Dados oficiais usados:** NASA POWER diário, comunidade AG, ponto −26,725; −53,518 (célula de ~50 km), 1984–2025: `PRECTOTCORR`, `T2M`, `T2M_MAX`, `T2M_MIN`, `RH2M`, `WS2M`, `ALLSKY_SFC_SW_DWN` (para a ET0) e `GWETROOT` (comparação). Água do solo: GAEZ v5, solo médio, 125 mm/m × raiz 1,0 m = 125 mm.
- **Método:**
  1. ET0 Penman-Monteith FAO-56, com as mesmas fórmulas de `prototipo/modelo/risco.py`.
  2. Balde diário do milho: plantio 20/set, fases 25/40/45/30 dias, Kc 0,30/1,20/0,60 (FAO-56), p = 0,5.
  3. ISNA de 20/set a 10/jan, 36 safras (1990–2025; a série da microrregião no IBGE começa em 1990).
  4. Limiar por LOO (maximiza acertos menos alarmes falsos).
  - Scripts: `sessoes/B3/comum.py`, `sessoes/B3/teste1_estiagem_milho.py`. Saída: `sessoes/B3/teste1_resultado.json`.
- **Resultado [CÁLCULO]** (microrregião 42001, 7 anos ruins: 1991, 2002, 2004, 2005, 2012, 2021, 2022):

  | Indicador | Spearman ρ (p) | Acertos (LOO) | Alarmes falsos |
  |---|---|---|---|
  | **ISNA até 10/jan (principal)** | **+0,28 (0,11)** | **4/7** | **7 de 11 alertas (64%)** |
  | Chuva nov–dez | +0,21 (0,22) | 3/7 | 6 de 9 (67%) |
  | GWETROOT dez (MERRA-2) | +0,17 (0,33) | 3/7 | 4 de 7 (57%) |
  | Rendimento simulado do ciclo todo | +0,32 (0,07) | 5/7 | 9 de 14 (64%) |

  - Os 3 anos mais secos pelo ISNA são 2022 (0,62), 2009 (0,68) e 2012 (0,69); 2012 e 2022 tiveram quebra (rendimento relativo 0,52 e 0,66) e 2009, queda de 9%.
  - Alarmes falsos fortes: 2023 (ISNA 0,81, rendimento relativo 1,26), 2025 (0,86; 1,55), 2006 (0,79; 0,99).
  - Perdas que o POWER não vê: 1991 (ISNA 0,94; rendimento relativo 0,47) e 2004 (1,00; 0,83).
  - No município (4217204, 10 anos ruins), o resultado é pior: ρ = +0,19, 3/10 acertos.
  - Sensibilidade (microrregião, ISNA): mudar a data de decisão para 31/dez ou 31/jan dá ρ de 0,35 a 0,37 e 5/7 acertos, com 5 ou 6 alarmes falsos. Mudar o plantio para 1/set ou 10/out piora (ρ = 0,22). Nenhuma variante passa de ρ = 0,4.
- **Gráfico:** `sessoes/B3/teste1_isna_x_rendimento.svg`. Os pontos vermelhos (anos ruins) só se separam no canto de ISNA < 0,75; entre 0,80 e 0,95 há anos bons e ruins misturados.

## 3. Validação
- **Contra a linha de base:** 4 acertos contra 1,4 esperados ao acaso (com 81% de alarmes falsos); "não fazer nada" acerta 0. A chance de acertar 4 ou mais de 7 com 11 alertas ao acaso é de 11% [CÁLCULO, hipergeométrica]: **não é significativo**.
- **Fonte externa:**
  - Epagri/Ciram (dez/2021): o Extremo Oeste poderia perder até 50% do milho na estiagem de 2021/22. **Bate** com o PAM 2022 (rendimento relativo 0,66) e com o ISNA mais baixo da série (0,62). [Notícias Agrícolas](https://www.noticiasagricolas.com.br/noticia/305869)
  - Epagri/Cepa (2020): estiagem 2019/20 "a mais severa desde 2005", com a maior perda de milho silagem no Extremo Oeste (cerca de 13,8%). **Não bate:** o PAM 2020 da microrregião mostra rendimento acima do normal (1,15) e o ISNA fica em 0,89. Ou a seca veio depois de 10/jan, ou o PAM municipal não registra bem. [Notícias Agrícolas](https://www.noticiasagricolas.com.br/noticia/272995)
  - Os números do IBGE PAM por município são estimativas, com valores repetidos de ano para ano. A série de leite (PPM, tabela 74) é quase plana e não serve para validar.
- **O critério de sucesso foi atingido?** **Não.** 4/7 (precisava ≥ 2/3), 64% de alarmes falsos (precisava ≤ 40%) e ρ = 0,28 (precisava ≥ 0,4).

## 4. Régua (1 a 5)
| Critério | Nota | Por quê (uma frase) |
|---|---|---|
| Problema real | 5 | A Epagri registra perdas de milho grão e silagem no Extremo Oeste em 2019/20 e 2021/22, e a região faz cerca de 80% do leite de SC. |
| Tamanho do impacto | 4 | Uma quebra de 30 a 50% do milho tira o volumoso do ano inteiro do rebanho leiteiro. |
| Resolve de fato | 2 | Com 64% de alarmes falsos, mandaria fazer silagem à toa em 7 anos para acertar 4. |
| Validade | 2 | Supera o acaso no número de acertos, mas não é significativo (p = 0,11; ρ = 0,28) e falha no critério definido antes. |
| Muda a decisão | 3 | Grão ou silagem em 10/jan é uma decisão concreta e com data, mas o alerta só é confiável nos extremos. |
| Simples e factível | 4 | Reusa o balanço do protótipo e só precisa do POWER. |
| Alinhamento com o desafio | 3 | É manejo da safra (destino do milho), não rotação. |
| Diferencial | 3 | O ZARC não acompanha a safra, mas a Epagri/Ciram já publica boletins de estiagem. |
| Cabe no hackathon | 5 | Já está rodando. |
| **Total (máx. 45)** | **31** | |

Aprovada só com 3+ em problema real, resolve de fato e validade.

## 5. Veredito
**Ajustar.** Na célula de 50 km do POWER, o balanço hídrico não separa os anos comuns. Só os extremos (ISNA < 0,75: 2012, 2022) ficam claros. A versão "só extremos" foi testada fora da amostra em B3-3.

## 6. Relação com o controle
**Complementa.** O controle dá "x de cada 10 anos" antes do plantio. Este alerta funcionaria durante a safra, mas só para dizer "este ano está entre os mais secos" (ver B3-3).

**Aviso para o controle:** em SC, o mesmo balanço explica pouco da variação do rendimento ano a ano (ρ = 0,2 a 0,3). A "chance de colher" do controle vai ficar perto de 9 ou 10 em 10 na maioria dos anos e decisões de plantio.

## 7. Limites e o que não foi testado
- A célula do POWER (~50 km) mistura o Vale do Uruguai com o planalto; a chuva é reanálise (MERRA-2 corrigida), não IMERG (que pede login Earthdata). SMAP também não foi testado.
- O IBGE PAM mede o milho grão, não a silagem nem o leite. A série de leite do PPM é plana e não serve.
- Uma data de plantio fixa (20/set) e um solo único. O Extremo Oeste tem muito solo raso em encosta, que seca mais rápido.
- Os parâmetros da cultura são da FAO-56, não da portaria do ZARC para SC.
- Não medi o ganho em reais da silagem antecipada.

## 8. Fontes
- NASA POWER diário: `loop-validacao/dados/power_sao_miguel_do_oeste.json` [DADO].
- IBGE SIDRA, tabela 1612, milho (c81 = 2711), microrregião 42001 e município 4217204: `sessoes/B3/externo/milho_micro_smo.json`, `milho_smo.json`. https://apisidra.ibge.gov.br/values/t/1612/n9/42001/v/112,216/p/all/c81/2711 [DADO].
- IBGE SIDRA, tabela 74, leite, município 4217204 e microrregião 42001 [DADO].
- Epagri/Ciram, estiagem 2021/22: https://www.noticiasagricolas.com.br/noticia/305869
- Epagri/Cepa, estiagem 2019/20: https://www.noticiasagricolas.com.br/noticia/272995
- FAO-56 (Kc, ET0), GAEZ v5 (água por textura), como em `prototipo/modelo/risco.py`.
