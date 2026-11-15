# V1 · Alerta de ano extremo de água (B3-3): teste adversarial

Frente V1 · 14/11/2026 · Pasta: `solucao/validacao/V1/`

**Resumo em 4 linhas**
- A regra de B3-3, com os limiares fixos (ISNA < 0,75 no milho; excedente ≥ 360 mm na cebola), **não se sustenta** fora das regiões vizinhas.
- Em 8 células novas do POWER, o alerta fixo do milho quase não dispara: 5 alertas em 288 anos-região, 2 em ano ruim (40%, contra 13,5% de taxa-base), p = 0,24 por evento.
- B3-3 não tinha nenhum evento climático novo. Os "8 alertas fora da amostra" eram os mesmos 3 ou 4 anos da amostra, vistos em regiões vizinhas.
- O que sobra é mais fraco, mas é real: a regra relativa "10% mais secos da própria célula" no milho triplica a chance de ano ruim (44% contra 13,5%; IC 95% do ganho por ano: +11 a +46 pontos). Ainda assim, só acerta 4 dos 11 eventos e deixa passar 64% dos anos ruins.

## 1. Critério definido antes
O arquivo `criterios.md` foi escrito depois de só reproduzir B3-3 e antes de qualquer teste novo. Ele não mudou depois. Em resumo:
- **Parte A (ataques a B3-3):** A1 vazamento do limiar, A2 sensibilidade do limiar, A3 corte de "ano ruim", A4 dependência entre regiões, A5 intervalo por evento e A6 concorrente de chuva bruta. Cada ataque diz antes o que conta como "derrubou".
- **Parte B (extensão):** microrregiões não usadas. O ponto do POWER fica no município com mais área da cultura (escolhido sem olhar o rendimento). Uma célula é excluída se a chuva diária for igual à de uma célula já usada em mais de 50% dos dias.
  - C0: ≥ 3 eventos de alerta.
  - C1: acerto por evento ≥ 50% e ≥ 2× a taxa-base.
  - C2: p ≤ 0,10 na permutação conjunta dos anos.
  - C3: rendimento relativo médio com alerta ≤ 0,85.
- **Veredito da frente:** "não sustenta" se a extensão do milho der "não sustenta".

**Desvios (anotados, não escondidos):**
1. O ponto ficou no **centróide** do município (API de malhas do IBGE), não na sede. A diferença é pequena perto de uma célula de ~50 km.
2. Na cebola, acrescentei um recorte "microrregiões com ≥ 100 ha". Decidi isso depois de ver as áreas e antes de ver os rendimentos, porque 5 das 9 microrregiões têm de 4 a 48 ha. Ele vem como leitura extra; o veredito usa o conjunto pré-registrado.
3. 42002 ficou fora da cebola porque a microrregião já tinha sido usada em B3-3, como manda a regra.

## 2. Método
- **Modelo:** as mesmas funções de B3 (`loop-validacao/sessoes/B3/comum.py`, `teste1_estiagem_milho.py`, `teste2_excesso_cebola.py`). Importei sem alterar. ET0 FAO-56 e balde diário iguais ao `prototipo/modelo/risco.py`.
- **Dados da solução:** NASA POWER diário, comunidade AG, 1984–2025. Baixei 17 pontos novos com `curl` (`baixa_power.sh` → `power/`).
- **Conferência:** IBGE PAM, tabela 1612, rendimento por microrregião, 1990–2025 (`externo/milho_micro_sc.json`, `externo/cebola_micro_sc.json`). Áreas municipais 2015–2023 só para escolher o ponto. O IBGE nunca entra no modelo.
- **"Ano ruim":** rendimento ≤ 0,85 × a mediana de t−3 a t+3, sem t (igual a B3).
- **Evento** = ano de safra. Todas as regiões que alertam no mesmo ano formam **um** evento. O evento acerta se metade ou mais delas teve ano ruim.
- **Intervalos honestos:**
  - (a) Wilson sobre o número de eventos;
  - (b) bootstrap **por ano**: sorteia os 36 anos com reposição e leva todas as regiões do ano juntas (5 mil sorteios);
  - (c) permutação **conjunta** dos anos: o mesmo embaralhamento para todas as regiões, o que preserva o fato de a estiagem atingir o estado inteiro (10 mil sorteios).
- **Scripts, em ordem:**
  - `v1_passo1_reproduz.py` (tabela da amostra e de B3-3);
  - `v1_passo2_ataques.py` (A1–A6 → `resultado_ataques.json`);
  - `v1_passo3_celulas.py` (identidade das células → `celulas_identidade.json`);
  - `v1_passo4_extensao.py` (→ `resultado_extensao.json`, `tabela_extensao.json`);
  - `v1_passo5_ic_graficos.py` (→ `resultado_ic_por_evento.json` e os SVG).
  - Funções comuns: `v1_comum.py`.

## 3. Resultado

### 3.1 Reprodução
Igual à ficha [CÁLCULO, `v1_passo1_reproduz.py`]:
- milho: 4 alertas, 3 em ano ruim, taxa-base de 0,208;
- cebola: 8 alertas, 4 em ano ruim, taxa-base de 0,167.

### 3.2 Ataques a B3-3 [CÁLCULO, `resultado_ataques.json`]

| Ataque | Milho | Cebola |
|---|---|---|
| A1 Vazamento | O limiar que B3-1 escolheria pela regra objetiva é **0,881**, não 0,75 (`teste1_resultado.json`). Com 0,881: 9/19 = 47% → **falha** o critério de B3-3 (≥ 50%). | O limiar objetivo de B3-2 é **282 mm**, não 360. Com 282: 5/18 = 28% → **falha**. O 360 coincide com o 90º percentil de Ituporanga (360,5 mm), e a célula de Tabuleiro é a mesma. |
| A1 Regra neutra (10% extremos da célula) | 5/8 = 62% → passa; permutação p = 0,012 por evento. | Mesmos 8 alertas da regra fixa (4/8) → passa no limite. |
| A2 Sensibilidade | De 0,70 a 0,74 só sobram 2 alertas (1 evento: 2022) → **falha** o C0 de B3-3 a −0,01. De 0,76 a 0,80, acerto de 75 a 83%. O limiar está na borda de "quase nunca dispara". | **Só 360 passa.** 350 mm: 44%. 370 mm: 43%. 300–340 mm: 36–42%. **Derruba.** |
| A3 Corte de "ano ruim" | Passa com 0,80, com 0,90 e com t±5. | **Falha** com 0,80 (3/8) e com t±5 (3/8); passa com 0,90. **Derruba.** |
| A4 Dependência | ISNA de SMO × Chapecó ρ = 0,88; × Concórdia ρ = 0,82. O rendimento relativo entre as microrregiões tem ρ = 0,89 a 0,92. **Nenhum evento novo:** os anos de alerta de B3-3 (2009, 2012, 2022) já alertavam na amostra. | Excedente de Ituporanga × Rio do Sul ρ = 0,98; × Tabuleiro ρ = 1,00. **Nenhum evento novo** (1997, 2008, 2015, 2023). |
| A5 Por evento | 2 de 3 eventos (2009 erra). Wilson de 21% a 94%. Permutação conjunta: p = 0,12 (evento), 0,076 (precisão). Bootstrap por ano: IC da precisão de 0 a 100%; ganho sobre a base de −18 a +86 pontos. | 3 de 4 eventos (2008 e 2023 com só metade das regiões ruins). Wilson de 30% a 95%. p = 0,054 (evento), 0,037 (precisão). Ganho de −7 a +79 pontos. |
| A6 Chuva bruta (10% mais secos ou úmidos) | 5/8 = 62%, p = 0,058: **empata** com o ISNA. | Os mesmos 8 alertas do excedente: **empata.** |

O gráfico `v1_sensibilidade_limiar_b33.svg` mostra as duas curvas. Na cebola, o pico de acerto cai exatamente em 360 mm.

**Leitura:**
- A cebola de B3-3 cai em A1, A2 e A3. O resultado depende de um limiar escolhido olhando a amostra e de um corte de ano ruim específico.
- O milho de B3-3 não cai pela sensibilidade, e até melhora com limiar mais alto. Mas com 3 eventos o intervalo vai de 0 a 100%, e o p por evento é 0,12.
- O "2,7% / 2,3%" da ficha contava cada ano-região como independente. Não é.

### 3.3 Extensão fora da amostra [CÁLCULO, `resultado_extensao.json`, `resultado_ic_por_evento.json`]

**Células novas, conferidas:**
- Nenhuma tem chuva igual à de uma célula já usada. O máximo foi 14% dos dias (Campos Novos × Concórdia) e 11% (São Pedro de Alcântara × Ituporanga) [`celulas_identidade.json`].
- **Milho:** 8 células e 8 microrregiões: 42003 Xanxerê (Abelardo Luz), 42004 Joaçaba (Fraiburgo), 42006 Canoinhas (Itaiópolis), 42009 Curitibanos (Campos Novos), 42010 Campos de Lages (São José do Cerrito), 42018 Tubarão (Treze de Maio), 42019 Criciúma (Içara), 42020 Araranguá (Turvo).
- **Cebola:** 9 microrregiões: 42003, 42004, 42006, 42007, 42009, 42010, 42016, 42018 e 42019.

| Caso | Anos-região | Alertas | Em ano ruim | Taxa-base | Eventos (acertos) | IC 95% da precisão (bootstrap por ano) | Permutação, p por evento | Critério |
|---|---|---|---|---|---|---|---|---|
| **Milho, regra fixa (ISNA < 0,75)** | 288 | 5 | 2 (40%) | 13,5% | 3 (1) | 0–100% | 0,24 | **não sustenta** (C1, C2, C3 falham) |
| Milho, 10% mais secos da célula | 288 | 32 | 14 (44%) | 13,5% | 11 (4) | 22–60%; ganho de +11 a +46 pontos | 0,021 (precisão: 0,001) | não sustenta (C1: 36% dos eventos < 50%) |
| Milho, chuva bruta nov–dez, 10% | 288 | 32 | 11 (34%) | 13,5% | 11 (2) | — | 0,42 | não sustenta |
| **Cebola, regra fixa (≥ 360 mm), 9 microrregiões** | 315 | 49 | 11 (22%) | 12,7% | 14 (2) | 8–42% | 0,39 | **não sustenta** |
| Cebola, 10% mais úmidos, 9 microrregiões | 315 | 36 | 9 (25%) | 12,7% | 9 (2) | 9–43% | 0,24 | não sustenta |
| Cebola ≥ 100 ha, regra fixa | 144 | 25 | 8 (32%) | 16% | 10 (3) | 6–60% | 0,21 | não sustenta |
| Cebola ≥ 100 ha, 10% mais úmidos | 144 | 16 | 7 (44%) | 16% | 7 (4) | 11–80% | 0,020 | parcial (C3: 0,90 > 0,85) |
| SC inteira (11 microrregiões), milho, 10% mais secos | 396 | 44 | 21 (48%) | 15,4% | 12 (4) | 22–65%; ganho de +11 a +48 pontos | — | (leitura extra) |

**O que os números dizem:**
- **O limiar absoluto não viaja.** As células do Planalto e do Litoral são mais úmidas: o ISNA fica abaixo de 0,75 em só 1,7% dos anos-região (5/288). Na cebola acontece o contrário: o Planalto Norte e o Meio-Oeste chovem mais em set–nov, e ≥ 360 mm dispara em 16% dos anos-região, quase sempre em ano bom (rendimento relativo médio com alerta: 0,98).
- **O balanço não vê a maioria das quebras.** No milho das células novas, 37 dos 39 anos ruins tiveram ISNA ≥ 0,75, e boa parte ficou acima de 0,9 (`v1_extensao_milho.svg`). O recall da regra fixa é de 5%; o da regra relativa, de 36%.
- **O sinal que sobra é relativo e estadual.** A regra "10% mais secos da célula" triplica a chance de ano ruim, e isso resiste à dependência entre regiões (bootstrap por ano e permutação conjunta).
  - Os acertos se concentram em 2 grandes estiagens: **2006** (7 regiões em alerta, 71% ruins) e **2022** (7 regiões, 57% ruins), mais 2005 e 2012 em uma região cada.
  - **2006 é um evento novo de verdade:** na amostra (SMO), 2006 tinha sido alarme falso.
- **Erros que pesam:** em **2020**, o alerta disparou em 6 regiões e só 1 teve quebra no PAM. A Epagri, porém, registrou a estiagem de 2019/20 como "a mais severa desde 2005" (fonte em B3-1). Ou o PAM não registra bem, ou a seca não derrubou o grão.

## 4. Conferência externa
- **2004/05:** a Epagri/Cepa registra perda de milho de cerca de 32% em SC na safra 2004/05, com perdas "especialmente severas" na microrregião de Curitibanos. A regra relativa alerta em Curitibanos em 2005 (ISNA 0,82; rendimento relativo 0,70) e acerta; a regra fixa (0,75) não alerta. Fontes: [Epagri RAC](https://publicacoes.epagri.sc.gov.br/rac/issue/download/127/258), [Epagri RAC](https://publicacoes.epagri.sc.gov.br/rac/issue/download/127/255). Li só o resumo da busca, não o documento inteiro.
- **2006:** a imprensa de SC, citando a Epagri, usa 2006 como referência de estiagem severa ([NSC Total](https://www.nsctotal.com.br/?p=2689420)). Bate com o evento 2006 da regra relativa.
- **2021/22 e 2019/20:** as mesmas fontes de B3-1. 2022 bate. 2020 é o conflito entre Epagri e PAM descrito acima.
- **Cebola 2015 e 2023:** as mesmas fontes de B3-2. Fora do Alto Vale, 2015 foi ruim nas 3 microrregiões grandes com alerta, e 2023 em 3 de 4. **1997** alertou em 4 regiões com ≥ 100 ha e nenhuma quebrou.

## 5. Veredito
**Não sustenta**, pela regra escrita antes: a extensão do milho com a regra fixa deu "não sustenta".
- B3-3 também cai nos ataques na cebola (A1, A2, A3).
- No milho, B3-3 tinha só 3 eventos já vistos, com IC de 0 a 100%.
- **O que resiste** (leitura extra pré-registrada, não o critério principal): no milho, um alerta **relativo à própria célula** ("10% mais secos em 36 anos") eleva a chance de ano ruim de ~14% para ~44%, com IC do ganho por evento acima de zero. Mas acerta só 4 de 11 eventos e perde 64% das quebras.

## 6. Implicações para a solução
1. **Não usar limiar absoluto** (ISNA < 0,75, 360 mm) no módulo de ano extremo de SC. Ele não transfere entre células.
2. **Usar o percentil da própria célula** do POWER ("entre os 10% mais secos dos últimos 36 anos aqui"). É o que o cartão de B3-3 já diz em palavras, e foi o que resistiu.
3. **Mudar a frase do cartão** para probabilidade, não ordem: "em anos assim, cerca de 4 em 10 regiões de SC tiveram quebra de 15% ou mais no milho; num ano qualquer, 1 a 2 em 10" [CÁLCULO, SC inteira: 48% contra 15%]. Não usar "faça silagem agora".
4. **O silêncio não quer dizer ano seguro.** A regra perde 64% dos anos ruins. A interface tem de dizer isso.
5. **O módulo de água em SC não ganha da chuva bruta** (A6). O balanço pode ficar por coerência com o Semiárido, mas não dá para vendê-lo como superior em SC.
6. **Cebola:** o excesso de chuva só tem os eventos do Alto Vale (2008, 2015, 2023). O limiar foi ajustado na amostra e não se sustenta fora. Na demo, mostrar o caso de Ituporanga como **histórico do lugar**, não como alerta validado.
7. **Contar eventos, não anos-região,** em toda validação do motor. Microrregiões vizinhas repetem o mesmo ano: ρ de 0,89 a 0,92 no rendimento do milho do Oeste.

## 7. Limites
- O "ano ruim" vem do PAM por microrregião, que é estimativa e tem ruído (2020). O PAM mede milho grão, não silagem.
- Os parâmetros da cebola (transplante em 1/ago) são do Alto Vale. No Planalto, o calendário é outro, e isso pode explicar parte da falha.
- A grade do POWER tem ~50 km. Pontos de microrregiões diferentes caem às vezes na mesma célula (para culturas diferentes: Fraiburgo e Lebon Régis; Curitibanos e São José do Cerrito).
- Os percentis "10% da célula" usam a série 1990–2025 inteira, inclusive anos futuros em relação a cada safra. Em operação, o percentil viria só do passado.
- IMERG e SMAP não testados (login Earthdata).

## 8. Arquivos
- `criterios.md`, `relatorio.md`
- Scripts: `v1_comum.py`, `v1_passo1_reproduz.py` a `v1_passo5_ic_graficos.py`, `baixa_power.sh`
- Resultados: `tabela_original.json`, `tabela_extensao.json`, `resultado_ataques.json`, `celulas_identidade.json`, `resultado_extensao.json`, `resultado_ic_por_evento.json`
- Gráficos: `v1_sensibilidade_limiar_b33.svg`, `v1_acerto_ic_por_evento.svg`, `v1_extensao_milho.svg`, `v1_extensao_cebola.svg`
- Dados: `power/` (17 pontos NASA POWER), `externo/` (IBGE: PAM, municípios, centróides)
