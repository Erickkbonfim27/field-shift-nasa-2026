# V3 · Sorgo como seguro da silagem (A4-3) com parâmetros da literatura

Frente V3, 14/11/2026. Região: São Miguel do Oeste (SMO). Dados da solução: só NASA POWER e SRTM (aba Resources). ZARC, Embrapa, IBGE, UDESC entram só para conferir.
Marcas: [DADO] vem de fonte, [CÁLCULO] vem dos scripts desta pasta, [ESTIMATIVA] é escolha minha, [INFERÊNCIA] é leitura.

## Resumo

- A afirmação "metade da silagem em sorgo no solo raso melhora o pior ano em 10 sem baixar a média" **sobrevive em parte**. Veredito: **parcial**.
- No cenário central (Ky da FAO-33 por estágio, R = 0,88), o pior ano em 10 sobe **+14%** no raso da A4 (CAD 87,5 mm; faixa de amostragem +6% a +31%) e **+40%** no raso pelo ZARC (CAD 42 mm; +31% a +57%). A média fica em **+0,4%** e **+7,3%** [CÁLCULO].
- Em 270 combinações de parâmetros definidas antes, a afirmação sobrevive em **56%** (raso A4) e **68,5%** (raso ZARC). O corte para "sustenta" era 70%.
- Dois fatores quebram o resultado: **Ky do sorgo ≥ 1,5 vezes o da FAO** e **valor da silagem de sorgo (R) abaixo de 0,85**. Se milho e sorgo respondem igual à seca (Ky = 1 nos dois, lógica de biomassa), o ganho some em todos os solos.
- O "raso" da A4 (87,5 mm) **não é raso pelo ZARC**. O ZARC de SC usa 24 a 95 mm para o milho (raiz de 60 cm) e **exclui solos com menos de 50 cm**. O solo realmente raso (42 mm ou menos) é onde o efeito é maior, e onde o modelo está menos validado.
- Solo raso por talhão só com a aba: o **declive do SRTM sozinho não basta**. Ele errou o Neossolo Litólico, que está em topo de encosta com declive baixo. Declive mais posição no relevo funciona nos 3 perfis conhecidos, mas o limiar foi escolhido depois de ver os perfis. Não é validação.

## 1. Critério definido antes

Texto completo em `00_criterio_antes.md`. Declaro lá que já conhecia o resultado da A4-3 ao escrevê-lo. Ele foi fixado antes das simulações novas.

| Item | Regra |
|---|---|
| Ponto central | P10 sobe ≥ 10% e a média cai no máximo 3% |
| Amostragem | bootstrap por safra, 2.000 repetições: ≥ 90% com ganho de P10 > 0 e ≥ 80% com média ≥ −3% |
| Parâmetros | grade de 270 combinações (Ky do sorgo, R, cenário de Ky, data do sorgo, Kc). Sustenta ≥ 70%; parcial 40 a 70%; não sustenta < 40% |
| Controle negativo | solo fundo (175 mm): P10 não sobe ≥ 10% |
| Solo raso | duas definições: V3-a CAD 87,5 mm (A4) e V3-b CAD 42 mm (tipo 1 do ZARC do sorgo; AD3 do milho = 41,4 mm) |
| Solo raso por SRTM | declive em 10% a 60% da área; bate com a literatura de solos de SMO |

Marcado como **pós-teste** neste relatório: o cenário "misto" de Ky, o recorte "plausível" da grade, as regras de declive com TPI e a conta por propriedade.

## 2. Método

### 2.1 Parâmetros de sorgo forrageiro e milho silagem

| Parâmetro | Milho silagem | Sorgo forrageiro | Fonte e status |
|---|---|---|---|
| Ciclo usado | 110 d | 110 d (teste 95 e 125 d) | A4. ZARC SC grupo I: milho 130 d, sorgo 110 d até a maturação, e a silagem é colhida antes [DADO]. Embrapa: sorgo para silagem com ciclo de 90 a 100 d até grão pastoso [DADO]. |
| Fases ZARC (só para ISNA) | 25/35/40/20 d | 20/30/25/35 d | Portaria SPA/MAPA 236/2026 (milho) e 128/2023 (sorgo forrageiro SC) [DADO]. |
| Kc (ini / meio / fim) | 0,30 / 1,20 / 0,90 | 0,30 / 1,05 / 0,80 | FAO-56 tab. 12. Valores já usados na A4; **não reabri a tabela nesta sessão**. O Kc final de silagem (colhida verde) é escolha minha [ESTIMATIVA]. |
| Ky por estágio (veg / floração / formação / maturação) | 0,40 / 1,50 / 0,50 / 0,20; total 1,25 | 0,20 / 0,55 / 0,45 / 0,20; total 0,9 | Milho: FAO-33, no capítulo 2 da FAO-66 (https://fao.org/4/i2800e/i2800e02.pdf) [DADO]. Sorgo: total 0,9 no mesmo capítulo [DADO]; os valores por estágio vieram do trecho de busca da página de culturas da FAO, que não consegui abrir. |
| Janela de cada estágio | 0–55 / 55–70 / 70–95 / 95–110 d | idem | [ESTIMATIVA]. A A4 aplicava o Ky 1,5 do milho por 40 dias (dias 55–95). Aqui a floração dura 15 dias. |
| Raiz e depleção p | 1,0 m; p = 0,55 | 1,0 m; p = 0,55 | FAO-56 [DADO]. O sorgo pode ir a 2 m em solo fundo; testei CAD do sorgo ×1,25 e ×1,5. |
| CAD do raso | ZARC milho AD1–AD6: 24; 31,8; 41,4; 54,6; 72,6; 95,4 mm | ZARC sorgo tipos 1–3: 42; 66; 90 mm | Raiz de 60 cm [DADO]. Solos < 50 cm **não são indicados** em nenhuma das duas culturas [DADO]. |
| R (valor da silagem de sorgo / milho) | — | 0,88 central; 0,75 a 1,0 | Embrapa Gado de Leite: 85 a 90%; Demarchi et al. 1995: 72 a 92% (via ficha A4-3). Paziani et al. (RBMS): milho 17 e sorgo 18 t MS/ha, e **10 t de MS digestível/ha nos dois** (R ≈ 1,0 por esse critério; digestibilidade 59% contra 53%) [DADO]. |

Embrapa (folder de 2008, https://www.infoteca.cnptia.embrapa.br/infoteca/bitstream/doc/491736/1/Sorgoforrageiro.pdf): no Sul o sorgo para silagem deve ser semeado em outubro e novembro. Cerca de 15 t MS/ha num corte. Custo da silagem menor que o do milho. Rebrota possível [DADO]. O custo e a rebrota não entram no modelo.

### 2.2 Simulação

- Balanço hídrico diário FAO-56 + Ky multiplicativo por estágio (FAO-33), com ET0 e chuva do NASA POWER em SMO, 1984 a 2024 (41 safras), 5 datas de plantio do milho (11/set a 21/out) = 205 casos por solo [CÁLCULO].
- `modelo_v3.py` reaproveita a ET0 da A4 e reproduz os casos da A4 com diferença máxima de 1e-16 no cenário "A4" (`v3_01_replica_a4.py`, `res_01_replica_a4.json`).
- Silagem da propriedade = (1 − f) × milho + f × R × sorgo.
- Quatro cenários de Ky:
  - **A4**: o Ky por fase da A4.
  - **FAO33** (central): Ky por estágio.
  - **BIOMASSA**: Ky = 1 nos dois. Biomassa de planta inteira proporcional à água transpirada, sem penalidade especial de floração [INFERÊNCIA].
  - **MISTO** (pós-teste): Ky = w × Ky(FAO) + (1 − w) × 1, com w = fração de grão na MS da silagem, 35% no milho e 39% no sorgo (Paziani et al.: 6 de 17 e 7 de 18 t/ha) [CÁLCULO].
- Bootstrap: reamostra as 41 safras, mantendo as 5 datas juntas (`v3_02_central_grade.py`). Ele cobre só o erro de amostragem de 41 anos, não o erro dos parâmetros.
- Frequência de geada (Tmin ≤ 2 °C entre os dias 20 e 95): **zero** em todas as datas e safras. O POWER não tem Tmin abaixo de 3,96 °C de 1/out a 31/dez. A diferença entre sorgo na mesma data e sorgo 30 dias depois **não vem de geada** (`res_03_extras.json`).

### 2.3 Solo raso por talhão

- Tile SRTM 1 arc-s S27W054 baixado com curl (https://s3.amazonaws.com/elevation-tiles-prod/skadi/S27/S27W054.hgt.gz), declive pelo método de Horn, TPI (elevação menos média de janela de 7 × 7 pixels, ~190 m) (`v3_06_srtm_solo_raso.py`).
- Verdade de campo: dissertação da UDESC (Müller, 2020), levantamento detalhado de 210 ha em SMO e 3 perfis com coordenadas. Área: 61,8% Latossolo Vermelho profundo; o resto é Neossolo Regolítico associado a Litólico, ambos com contato lítico até 50 cm [DADO] (https://www.udesc.br/arquivos/cav/id_cpmenu/2480/Disserta__o__2__16177239688583_2480.pdf).
- A elevação do SRTM nos 3 perfis (644, 602 e 636 m) bate com a descrita (640, 600 e 624 m), então as coordenadas estão certas [CÁLCULO].
- GAEZ: **não testado**. O GAEZ v4 tem 5 arc-min (~9 km), um pixel para o município. Só serviria de prior regional. Não achei o caminho direto do raster.

## 3. Resultado

### 3.1 Cenário central e bootstrap (f = 50%, R = 0,88) [CÁLCULO]

| Solo (CAD) | P10 só milho → mistura | Ganho do P10 (IC 95% da amostragem) | Média (IC 95%) | Casos < 0,6 | Passa o ponto central? |
|---|---|---|---|---|---|
| **Raso ZARC 42 mm** | 0,246 → 0,344 | **+39,6%** (+30,7 a +57,1) | +7,3% (+4,9 a +10,3) | 108 → 92 | sim |
| **Raso A4 87,5 mm** | 0,438 → 0,501 | **+14,3%** (+6,1 a +31,4) | +0,4% (−1,2 a +2,2) | 43 → 32 | sim |
| Médio 125 mm | 0,599 → 0,629 | +5,0% (+0,3 a +15,4) | −2,4% (−3,4 a −1,1) | 21 → 16 | não (P10 < 10%) |
| Fundo 175 mm (controle) | 0,753 → 0,762 | +1,2% (−2,4 a +4,4) | −4,2% (−4,8 a −3,4) | 8 → 6 | não, como esperado |

- Bootstrap: nos dois solos rasos, 100% das repetições têm ganho de P10 > 0 e 100% têm média ≥ −3%. O critério de amostragem passa.
- O controle negativo se comporta como esperado: o ganho de P10 fica em +1,2%.
- Com f = 25%: P10 +9,8% (raso A4) e +20,8% (raso ZARC). Com f = 100%: +32,8% e +80,5%. A média continua perto de zero no raso A4 (+0,7%) e sobe no raso ZARC (+14,6%).
- Gráfico: `fig_v3_1_ganho_por_cad.svg`. O ganho cai quando a água do solo sobe, e o P10 passa de 10% perto de 125 mm só em alguns cenários.

### 3.2 Sensibilidade do Ky do sorgo e de R [CÁLCULO]

Ky do sorgo (cenário FAO-33, R = 0,88), ganho de P10 e variação da média:

| Ky do sorgo | Raso A4 (87,5 mm) | Raso ZARC (42 mm) |
|---|---|---|
| ×0,5 | +32,7% / +4,1% | +79,4% / +17,1% |
| ×0,75 | +23,1% / +2,2% | +58,4% / +12,0% |
| ×1 (FAO) | +14,3% / +0,4% | +39,6% / +7,3% |
| ×1,5 | −0,8% / −3,0% | +7,0% / −1,3% |
| ×2 | −14,0% / −5,8% | −13,8% / −7,7% |

- **Ky de equilíbrio** (ganho de P10 = 0): ×1,47 (raso A4) e ×1,64 (raso ZARC) no cenário FAO-33. No cenário misto: ×1,48 e ×1,21. No cenário biomassa: ×0,83 e ×0,91, ou seja, o sorgo teria de ser menos sensível que o milho para valer a pena.
- **R de equilíbrio** (média igual à do milho puro): 0,875 (raso A4) e 0,77 (raso ZARC) no FAO-33. Para a média cair no máximo 3%: 0,825 e 0,725. A "média não cai" no raso A4 só vale porque R = 0,88 está colado no limite.
- O valor da literatura para R vai de 0,72 a 1,0. A conclusão sobre a média é sensível a isso.
- Ky do milho (FAO-33, Ky do sorgo ×1): ×0,6 deixa o raso A4 em +3,2% de P10 e −3,2% de média. O milho de silagem é de planta inteira, e o Ky de grão da FAO pode exagerar a perda do milho [INFERÊNCIA]. Se o Ky do milho for menor, a vantagem do sorgo diminui.
- Outros testes no FAO-33 (raso A4 / raso ZARC): sorgo com CAD ×1,25 (raiz mais funda): +20,8% / +45,3%. Sorgo com ciclo de 95 d: +18,9% / +41,4%; com 125 d: +14,3% / +45,1%.
- Gráfico: `fig_v3_2_ky_sorgo.svg`.

### 3.3 Grade pré-definida de 270 combinações [CÁLCULO]

| Solo | Sobrevivem | Ganho do P10 (p10 / mediana / p90) | Média (p10 / mediana / p90) | Mín. e máx. do P10 |
|---|---|---|---|---|
| Raso A4 | **152 de 270 (56%)** | −8% / +10% / +37% | −10% / −1,4% / +9% | −27% e +55% |
| Raso ZARC | **185 de 270 (68,5%)** | −9% / +14% / +71% | −10% / +3,2% / +19% | −26% e +125% |
| Médio 125 mm | 133 de 270 (49%) | −9% / +5% / +23% | −11% / −2,8% / +5% | −26% e +39% |
| Fundo 175 mm | 100 de 270 (37%) | −9% / +1,5% / +15% | −12% / −4,2% / +3% | −22% e +25% |

Por fator (raso A4 / raso ZARC): R = 0,75: 11% / 41%; R = 0,88: 67% / 76%; R = 1,0: 91% / 89%. Ky ×0,5: 78% / 89%; ×1: 59% / 76%; ×1,5: 44% / 59%; ×2: 33% / 30%. Cenário A4: 64% / 76%; FAO-33: 53% / 77%; biomassa: 51% / 53%. Gráfico: `fig_v3_3_grade.svg`.

- **Aplicando o critério**: raso A4 = 56%, **parcial**. Raso ZARC = 68,5%, **parcial** (a 1,5 ponto do corte de 70%).
- A grade tem ruído que não vem do sorgo. No fundo, 37% sobrevivem, e a mediana do ganho é +1,5%. Isso é o controle negativo e mostra que parte das combinações "passa" por acaso de parâmetro, não por mecanismo.
- Sorgo plantado 30 dias depois do milho eleva o ganho central de P10 de +14% para +29% (raso A4) e de +40% para +63% (raso ZARC), com a média igual. Como não há geada, o ganho vem do deslocamento da data no calendário de chuva, não só da cultura [INFERÊNCIA]. Por isso a comparação principal usa a mesma data.
- **Pós-teste, subjetivo**: se eu limitar a grade ao que tem apoio na literatura (cenários FAO-33 e misto, R de 0,88 a 1,0, Ky ×0,75 a ×1,5, mesma data), sobrevivem 78% (raso A4) e 86% (raso ZARC). Isso depende de uma escolha que fiz depois de ver o resultado. Não uso para o veredito.

### 3.4 O que a mistura faz ano a ano [CÁLCULO]

- No raso A4, a mistura rende mais silagem em **18 de 41 safras** e rende mais de 0,02 **menos** em **15 safras**. É um seguro de verdade: paga prêmio em ano bom (queda de até ~0,06) e recebe em ano seco. Gráfico: `fig_v3_4_ano_a_ano.svg`.
- No raso ZARC, a mistura ganha em 35 de 41 safras e perde em 2. Ali o sorgo é melhor na média, não só no pior ano.
- Estiagens conhecidas (safra de plantio): **2021/22** é a 3ª de 41 em ganho da mistura nos dois solos rasos (4ª no solo de 125 mm). **2011/12** é a 11ª (raso A4) e a 12ª (raso ZARC). **2004/05** é a 12ª e a 15ª.

### 3.5 Por propriedade, não por talhão (pós-teste, exploratório) [CÁLCULO]

Propriedade com 38,2% de solo raso (a fatia mapeada como Neossolo na área da UDESC) e 61,8% de solo fundo. R = 0,88. FAO-33:

| Estratégia | Δ P10 (raso 42 mm) | Δ média | Δ P10 (raso 87,5 mm) | Δ média |
|---|---|---|---|---|
| Tudo milho (base) | P10 0,562 | média 0,788 | P10 0,634 | média 0,862 |
| 50% sorgo em todos os talhões | +9,9% | −1,1% | +4,4% | −2,7% |
| 50% sorgo só nos talhões rasos (19% da área) | +6,3% | +2,0% | +3,1% | +0,1% |
| 100% sorgo só nos talhões rasos (38% da área) | +13,4% | +4,0% | +8,1% | +0,2% |

- O ganho de **+14% a +40%** vale **dentro do talhão raso**. No nível da propriedade, onde os talhões fundos pesam mais no pior ano, o ganho cai para +3% a +13% se o sorgo ficar só nos talhões rasos.
- No cenário biomassa, as três estratégias **perdem** (P10 de −0,9% a −2,9%).

## 4. Solo raso por talhão com a aba [CÁLCULO]

Declive do SRTM (IBGE): no entorno de 15 km de SMO, 40% da área tem declive ≥ 20%; mediana 16,6%. Isso passa no critério pré-definido (10% a 60%). Já na área de 210 ha da UDESC, só 11% tem declive ≥ 20%, e o mapa de solos marca 38,2% de solo raso. O critério "bate com a literatura" **falha** para declive ≥ 20%.

| Perfil UDESC | Solo | Campo | SRTM 30 m |
|---|---|---|---|
| P5 (terço médio) | Latossolo profundo | declive 9% | 10,5%; TPI −0,1 m |
| P6 (terço inferior) | Neossolo Regolítico, contato lítico < 50 cm | 38% | 21,3%; TPI −7,6 m |
| P7 (topo de encosta, pedregoso) | Neossolo Litólico, < 50 cm | 19% | **9,6%**; TPI **+4,9 m** |

| Regra (post hoc, n = 3 perfis) | Acerta P5 / P6 / P7 | Área marcada na UDESC (mapa: 38%) |
|---|---|---|
| declive ≥ 20% | sim / sim / **não** | 11% |
| declive ≥ 12% | sim / sim / **não** | 36% |
| TPI ≥ 2 m | sim / **não** / sim | 21% |
| declive ≥ 15% ou TPI ≥ 2 m | sim / sim / sim | 37% |

- O SRTM de 30 m **subestima o declive** (10,5% / 21,3% / 9,6% contra 9% / 38% / 19% no campo). O Litólico mais raso está no topo, com declive baixo. Só a posição convexa (TPI) o revela.
- A regra "declive ≥ 15% ou TPI ≥ 2 m" acerta os 3 perfis e marca 37% da área contra 38% do mapa. **Os limiares foram escolhidos depois de ver esses dados**, com uma área e 3 pontos. Não é validação. No entorno de 15 km, essa regra marca 67% da área, o que parece alto.
- O mapa da UDESC é uma figura, sem polígonos. Não dá para medir acerto pixel a pixel.
- Gráfico: `fig_v3_6_solo_raso_srtm.svg`.

**Proposta de identificação de solo raso por talhão** (usa só a aba, mas com limite claro):
1. Pergunta ao produtor, como já previsto no contexto: "arenoso, médio, argiloso ou raso/pedregoso". É a fonte principal.
2. SRTM como alerta: marca o talhão quando declive ≥ 15% ou TPI ≥ 2 m. O sistema mostra "pode ser raso, confirme".
3. GAEZ só como prior regional, nunca por talhão (um pixel de 9 km).
4. Calibração futura: Sentinel-2/Landsat, comparando o NDVI de talhões marcados e não marcados em anos secos. **Não feito aqui.**

## 5. Conferência externa

- **ZARC 2026/27 de SMO** (`v3_04_zarc.py`, `res_04_zarc.json`) [CÁLCULO + DADO]. Recalculei o ISNA com os limites do ZARC. Resultado:
  - Milho: a chance de evento por CAD é 30% no AD2 (31,8 mm), 23% no AD3, 18% no AD4, 14% no AD5 e 10% no AD6. O ZARC diz 40% ou não indicado no AD2, 30% no AD3, 20% a 30% no AD4 e 20% no AD5 e AD6. A correlação de Spearman é 0,90 (n = 22, mas as datas dentro de cada AD são correlacionadas, então a amostra efetiva é de 4 a 6).
  - Sorgo: chance de evento de 7% (42 mm), 3% (66 mm) e 1,5% (90 mm); o ZARC dá 20% nos três.
  - Ordem milho × sorgo no mesmo CAD (42 contra 41,4 mm): nosso sorgo 7% contra milho 23%; ZARC sorgo 20% contra milho 30%. **A ordem bate.**
  - Limite: o ZARC usa limites de ISNA diferentes por cultura (fase III: 0,55 no milho e 0,40 no sorgo). Parte da vantagem do sorgo já está nesses limites. Esta conferência valida o balanço hídrico e a ordem, **não o Ky nem o rendimento da silagem**. Gráfico: `fig_v3_5_zarc.svg`.
- **Anos secos**: a mistura dá mais ganho em 2021/22 (3º de 41) e em 2011/12 (11º), menos em 2004/05 (12º). Bate em parte.
- **PAM/IBGE** (milho em grão de SMO, sem tendência): Spearman do milho simulado contra a PAM de +0,10 (raso 42 mm), +0,24 (87,5 mm), +0,31 (125 mm) e +0,33 (175 mm) [CÁLCULO]. Isso repete o resultado fraco da B1-0 (ρ = 0,28). **O balanço hídrico não prevê o rendimento do ano em SMO.** E a correlação é a menor no solo mais raso, onde o ganho é maior. A PAM não separa silagem nem sorgo, então não confere o sorgo.
- **Embrapa**: o sorgo é descrito como mais tolerante a veranico, mas há também resultado oposto. Em trecho de busca, um estudo da Embrapa com sorgo de grão achou Ky acima de 1,4 e acima de 1,9 na floração (https://www.alice.cnptia.embrapa.br/alice/bitstream/doc/133189/1/AgriculturalWaterManagementv.11n.2p.1691801986.pdf), e um estudo de sorgo forrageiro (Maydica) não achou efeito até 60% da irrigação plena (https://journals-crea.4science.it/index.php/maydica/article/download/2317/1363/7652). Li só os resumos desses dois. A faixa de Ky na literatura é larga e **inclui o valor que quebra o resultado**.
- **Silagem real**: no trabalho de Paziani et al., o sorgo e o milho deram a mesma MS digestível (10 t/ha), então R ≈ 1,0 em MS digestível. Com R = 1,0, a afirmação sobrevive em 91% (raso A4) e 89% (raso ZARC) da grade. Com R = 0,75, em 11% e 41%.

## 6. Veredito

**Parcial.**

- Pelo critério pré-definido, os dois solos rasos passam no ponto central e no bootstrap, e ficam em 56% e 68,5% na grade (40 a 70%). O controle negativo passa.
- **O que sobrevive**: em solo com pouca água (CAD de 42 a 90 mm), trocar parte da silagem por sorgo sobe o pior ano em 10 se o sorgo for menos sensível à seca que o milho (como a FAO-33 e o ZARC supõem) e se o valor da silagem for pelo menos ~0,85 do milho.
- **O que não sobrevive**: "sem baixar a média" como garantia. No raso A4, a média está no limite (R de equilíbrio 0,875). E a afirmação inteira cai se o Ky do sorgo for 1,5 vez o da FAO, ou se milho e sorgo responderem igual (Ky = 1).
- **Faixa de incerteza para mostrar** (solo raso, f = 50%):
  - raso A4 (87,5 mm): P10 de +6% a +31% pela amostragem; de −8% a +37% pelos parâmetros (p10 a p90, mediana +10%). Média de −10% a +9% (mediana −1,4%).
  - raso ZARC (42 mm): P10 de +31% a +57% pela amostragem; de −9% a +71% pelos parâmetros (mediana +14%). Média de −10% a +19% (mediana +3,2%).
- A ficha A4-3 propunha mostrar "de 0% a 14%". Com parâmetros da literatura, a faixa fica de **−8% a +37%** no raso A4. O ponto central sobe um pouco, mas o intervalo abre para valores negativos.
- **Nota de validade**: o modelo reproduz o ZARC, mas o balanço não acompanha a PAM do ano (ρ de 0,10 a 0,33). O "pior ano em 10" simulado **não foi confirmado contra produtividade observada**. Não há dado de silagem de sorgo em SMO.

## 7. Implicações para a solução

1. **Módulo "mistura de culturas por talhão (silagem)"** no motor modular, ativo em SMO, só para talhão que o produtor declara raso, pedregoso ou de encosta. Não ligar no solo fundo (controle negativo).
2. **Mostrar faixa e premissa, nunca um número só.** Frase sugerida: "No talhão raso, metade em sorgo melhora o pior ano em 10 em torno de +10%, com faixa de −8% a +37%, desde que a silagem de sorgo valha pelo menos 85% da de milho". Mostrar também que em cerca de 1 safra em 3 (15 de 41 no raso A4) a mistura rende um pouco menos.
3. **O prêmio e o risco fazem parte da mensagem.** O sorgo só ganha com R ≥ 0,85. O produtor ou o técnico informa o valor da silagem de sorgo na dieta e o custo. A conta de custo e preço de volumoso comprado não está no modelo.
4. **Solo raso**: pergunta ao produtor como entrada principal; SRTM (declive ≥ 15% ou TPI ≥ 2 m) como alerta "confirme"; GAEZ só como prior regional. Para a demo, **não dizer** que o SRTM mede a profundidade.
5. **Usar o CAD do ZARC (24 a 95 mm)** nas classes de solo do módulo, não os 175 mm/m do protótipo com raiz de 1 m. O "raso" da A4 (87,5 mm) fica perto do AD6 do ZARC (95,4 mm), o melhor solo.
6. **Calibrar o Ky do sorgo antes do pitch**, com NDVI de Sentinel-2 ou Landsat em talhões de sorgo e milho de SMO em safras secas e normais (2021/22 contra uma safra boa). É o teste que decide se o resultado sustenta. Se o Ky real do sorgo for ≥ 1,5 vez o da FAO, o módulo sai.
7. Para o júri: o resultado forte é o recorte "o balanço hídrico reproduz o ZARC em SMO (ρ = 0,90) e mostra, por talhão, onde o sorgo ajuda". Evitar "validado com produtividade", porque a PAM não confirma.

## 8. Limites

- O Ky do sorgo e do milho vem de fonte genérica de grão (FAO-33). A silagem é planta inteira. Não há calibração local.
- O valor de R (0,72 a 1,0) e o custo não são modelados com dados de SMO.
- O sorgo não foi comparado a dado de rendimento de SMO. A PAM não traz sorgo forrageiro.
- Os 41 anos geram erro de amostragem. O bootstrap mede só isso. A grade mede o erro de parâmetro. Os dois juntos não viraram um intervalo único.
- A grade de 270 combinações tem pesos iguais para todos os valores, inclusive os pouco plausíveis. O recorte "plausível" é pós-teste e subjetivo.
- Grade POWER de ~50 km. O raso é uma classe de CAD, não um mapa. O balanço usa a mesma chuva para o talhão raso e o fundo.
- A frequência de geada é zero nos dados do POWER. O ZARC trata geada e frio na floração, e o modelo não. O sorgo é sensível ao frio na emergência; não está no modelo.
- Kc do sorgo e do milho: valores da FAO-56 usados desde a A4. Não reabri a tabela. Kc de fim de ciclo é escolha minha.
- A conferência do ZARC não valida o Ky. O SRTM e a regra de solo raso têm 1 área e 3 perfis. O GAEZ não foi testado. SMAP, IMERG e NDVI não foram usados.
- Rebrota do sorgo (até 60% do 1º corte, segundo a Embrapa) e custo menor da semente não entram. Os dois favorecem o sorgo [INFERÊNCIA].

## 9. Arquivos (todos em `solucao/validacao/V3/`)

| Arquivo | Conteúdo |
|---|---|
| `00_criterio_antes.md` | critério escrito antes das simulações novas |
| `modelo_v3.py` | modelo (Ky por estágio, CAD em mm, cenários) |
| `v3_01_replica_a4.py`, `res_01_replica_a4.json` | confere que o modelo reproduz a A4 |
| `v3_02_central_grade.py`, `res_02_central_grade.json` | central, bootstrap, grade, curva por CAD |
| `v3_03_extras.py`, `res_03_extras.json` | Ky e R de equilíbrio, Ky do milho, raiz, ciclo, geada, datas |
| `v3_04_zarc.py`, `res_04_zarc.json` | conferência com o ZARC |
| `v3_05_anos_secos_pam.py`, `res_05_anos_secos_pam.json` | anos secos e PAM |
| `v3_06_srtm_solo_raso.py`, `res_06_srtm.json` | SRTM e solo raso (o tile .hgt, de 26 MB, ficou fora da pasta) |
| `v3_07_graficos.py`, `fig_v3_1` a `fig_v3_6` (SVG) | gráficos |
| `v3_08_propriedade_por_talhao.py`, `res_08_propriedade.json` | conta por propriedade (pós-teste) |

Para rodar: `python3 -I v3_0X_*.py` (o 06 recebe o caminho do `S27W054.hgt`).

## 10. Fontes

- NASA POWER diário: `loop-validacao/dados/power_sao_miguel_do_oeste.json`. Modelo e casos da A4: `loop-validacao/sessoes/A4/` e `loop-validacao/fichas/A4-3-sorgo-seguro-silagem.md`.
- FAO-66, cap. 2 (Smith e Steduto; Ky do FAO-33): https://fao.org/4/i2800e/i2800e02.pdf. FAO-56 (Allen et al., 1998) para Kc, raiz e p, sem reabrir a tabela.
- ZARC sorgo forrageiro SC, Portaria 128/2023: https://www.gov.br/agricultura/pt-br/assuntos/riscos-seguro/programa-nacional-de-zoneamento-agricola-de-risco-climatico/portarias/2023-2024/santa-catarina-sc/PORTN128SORGOFORRAGEIROSC.pdf. Portaria 315/2026 (CAD 42/66/90 mm; ISNA 0,7/0,6/0,4): https://atlaspublico.com.br/regulacao/dou/portaria-spa-mapa-n-315-de-20-de-julho-de-2026-651394.
- ZARC milho 1ª safra SC, Portaria 236/2026: `loop-validacao/sessoes/B1/externo/zarc_portaria_236_2026_milho1_SC.txt`. Risco por município: `loop-validacao/sessoes/A4/zarc_smo_resumo.txt`.
- Embrapa, folder Sorgo forrageiro (2008): https://www.infoteca.cnptia.embrapa.br/infoteca/bitstream/doc/491736/1/Sorgoforrageiro.pdf. Embrapa, potencial nutritivo da silagem de sorgo: https://www.alice.cnptia.embrapa.br/alice/bitstream/doc/900608/1/Potencialnutritivodasilagem.pdf.
- Paziani et al., Correlações entre variáveis quantitativas e qualitativas de milho e de sorgo para silagem, RBMS: https://rbms.sede.embrapa.br/ojs/article/download/1136/pdf/9911.
- Müller, S. F. (2020), Levantamento pedológico detalhado em Chapecó e São Miguel do Oeste, UDESC: https://www.udesc.br/arquivos/cav/id_cpmenu/2480/Disserta__o__2__16177239688583_2480.pdf.
- SRTM 1 arc-s: https://s3.amazonaws.com/elevation-tiles-prod/skadi/S27/S27W054.hgt.gz.
- IBGE SIDRA 5457 (PAM, milho 40122, SMO 4217204): `loop-validacao/sessoes/B1/externo/pam_5457.json`.
