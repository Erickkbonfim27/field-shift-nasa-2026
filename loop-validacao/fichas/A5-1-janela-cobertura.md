# A5-1 · Quando semear a planta de cobertura

Sessão: A5 · Trilha: A · Região: ambas · Tentativa 1 de 4 · Data: 2026-11-14

## 1. Ideia (escrita antes do teste, às 19h22 de 14/11/2026, antes de rodar qualquer simulação)
- **Hipótese:** com chuva e temperatura diárias do NASA POWER (1984–2024), um balanço hídrico simples somado a graus-dia mostra uma janela de semeadura da cobertura que dá mais chance de "solo bem coberto antes do próximo plantio" do que a data habitual. Uma regra simples de "estado de agora" (semear depois de uma chuva que molhe o solo) reduz a falha de estabelecimento em relação à data fixa.
- **Problema que ataca (e para quem):** o agricultor familiar que, depois de colher a cebola (Ituporanga) ou o milho (São Miguel do Oeste), semeia a cobertura e às vezes perde a semente num veranico logo depois da germinação, ou semeia tarde e chega no próximo plantio com pouca palha e solo exposto à chuva.
- **Decisão que muda:** em que data (ou depois de qual chuva) semear a cobertura, e qual espécie escolher para a data que sobrou.
- **Casos testados:**
  | Caso | Região | Cobertura | Datas testadas | Prazo de "bem coberto" | Data habitual (linha de base) |
  |---|---|---|---|---|---|
  | I-MIL | Ituporanga | milheto (verão, após a cebola) | 20/nov a 31/jan | 30/abr | 15/dez |
  | I-MUC | Ituporanga | mucuna-preta (verão, após a cebola) | 20/nov a 31/jan | 30/abr | 15/dez |
  | I-AVE | Ituporanga | aveia-preta (inverno, antes da cebola) | 1/mar a 31/mai | 10/jul (dessecar antes do transplante) | 15/abr |
  | S-AVE | São Miguel do Oeste | aveia-preta (após o milho) | 14/fev a 31/mai | 15/ago (antes do milho) | 15/abr |
  As datas habituais são [INFERÊNCIA] a partir do calendário da cebola (colheita nov–dez, transplante jul–ago) e do milho no Oeste (colheita fev–mar); serão conferidas com Epagri/ZARC.
- **Critério de sucesso (definido antes):** "sucesso" num ano = a cobertura emerge, não morre num veranico nos primeiros 15 dias e acumula os graus-dia de "boa cobertura" (ajustados pelo estresse hídrico) até o prazo. Treino: 1984–2004. Teste: 2005–2024.
  - **C1 (janela fixa):** a melhor data fixa escolhida no treino tem, no teste, chance de sucesso **≥ 10 pontos percentuais acima** da data habitual.
  - **C2 (regra de estado de agora):** "a partir da data habitual, semear no primeiro dia com 3 dias de chuva ≥ 15 mm (limite de 20 dias)" corta a falha de estabelecimento **em pelo menos 1/3** e tem chance de sucesso **≥ 10 p.p. acima** da data habitual no teste.
  - **Plausibilidade externa:** a faixa de datas com chance ≥ 80% tem que se sobrepor à janela recomendada pela Epagri/ZARC para a espécie. Se não se sobrepuser, o modelo é considerado inválido.
  - A ideia "resolve de fato" se C1 ou C2 for atingido em pelo menos um caso. Se a data habitual já tiver ≥ 90% de sucesso e nada a superar, é resultado negativo.
- **Linha de base:** a data habitual fixa, todo ano.

## 2. Teste
- **Dados oficiais usados:** NASA POWER diário, comunidade AG (`dados/power_ituporanga.json`, `dados/power_sao_miguel_do_oeste.json`). Chuva (`PRECTOTCORR`) e temperaturas (`T2M`, `T2M_MAX`, `T2M_MIN`); ET0 Penman-Monteith FAO-56 com `RH2M`, `WS2M` e `ALLSKY_SFC_SW_DWN` (a mesma fórmula de `prototipo/modelo/risco.py`). Safras 1984–2024 (41 ou 42 por caso). Grade de ~50 km.
- **Método:** script `sessoes/A5/scripts/cobertura.py`.
  1. Data de semeadura a cada 5 dias na janela.
  2. Emergência: graus-dia somados só nos dias com o solo de 0–10 cm úmido. Sem emergência em 30 dias = falha.
  3. Morte da plântula: 6 dias seguidos de solo seco nos 15 dias após a emergência.
  4. Crescimento: graus-dia × Ks (estresse hídrico FAO-56, 150 mm/m de água disponível).
  5. Geada (Tmin ≤ 1 °C) mata milheto e mucuna. Calor (Tmax média > 30 °C na emergência) reduz a aveia.
  6. Graus-dia até a "boa cobertura" [ESTIMATIVA, sem calibração local]: milheto 550 °Cd (base 10), mucuna 900 °Cd (base 10), aveia 900 °Cd (base 0).
  - Sensibilidade (`scripts/sensibilidade_cobertura.py`): graus-dia alvo −20% e +25%, outros prazos, critério de morte mais duro e uma checagem sem modelo (veranico de 10 dias ou mais nos 20 dias após semear).
- **Resultado** [CÁLCULO] (`sessoes/A5/resultados/resultado_cobertura.json` e `sensibilidade_cobertura.txt`):
  | Caso | Chance na data habitual (teste 2005–2024) | Melhor data fixa (treino) → chance no teste | Regra "semear após chuva" no teste | Última data com chance ≥ 80% (alvo −20% / base / +25%) |
  |---|---|---|---|---|
  | I-MIL milheto | 100% (15/dez) | 20/nov → 100% (C1 = 0 p.p.) | 100% (C2 = 0) | 29/jan / 29/jan / 29/jan |
  | I-MUC mucuna | 100% (15/dez) | 20/nov → 100% (0 p.p.) | 100% (0) | 29/jan / 14/jan / 25/dez |
  | I-AVE aveia | 90,5% (15/abr) | 1/mar → 100% (+9,5 p.p.) | 66,7% (−23,8 p.p.) | 30/abr / 20/abr / 10/abr |
  | S-AVE aveia | 100% (15/abr) | 14/fev → 100% (0 p.p.) | 100% (0) | 30/mai / 30/mai / 15/mai |
  - **A água quase nunca é o problema.** A falha de emergência ficou entre 0% e 7% dos anos em todas as datas, e a morte de plântula por veranico em 0%. Mesmo com um critério mais duro, a data habitual ficou com 83% a 100% de sucesso.
  - Pela checagem sem modelo, veranicos de 10 dias ou mais logo após a semeadura acontecem em 0% dos anos em dez–jan e em 22% (Ituporanga) e 12% (SMO) em 15/abr. A semente espera a chuva sem morrer, então o efeito é atrasar, não perder.
  - **O que limita é o tempo e o frio.** A mucuna semeada depois de ~10/jan e a aveia semeada em Ituporanga depois de ~20/abr chegam no prazo sem cobrir bem o solo.
  - A regra "esperar chuva" piora o resultado da aveia em Ituporanga, porque atrasa a semeadura numa janela limitada pela temperatura.
  - Mediana de dias da semeadura habitual até a boa cobertura: milheto 56, mucuna 90, aveia 68 (Ituporanga) e 60 (SMO).
- **Gráfico:** `sessoes/A5/A5-1_chance_cobertura.png`. A chance fica perto de 100% em quase toda a janela e só cai no fim da janela da mucuna e da aveia de Ituporanga. A faixa azul mostra que o ponto onde a chance cai se move 2 a 3 semanas com a incerteza dos graus-dia.

## 3. Validação
- **Contra a linha de base:**
  - C1 (melhor data fixa contra a habitual, no teste 2005–2024): +0, +0, +9,5 e +0 p.p. Nenhum caso chega aos +10 p.p.
  - C2 (regra de estado de agora): 0, 0, −23,8 e 0 p.p.; a falha de estabelecimento já era quase 0 (0–4,8%), então não havia 1/3 a cortar.
- **Fonte externa:**
  - A Epagri (Krunwald e Wildner, via Agrolink, 2020) recomenda semear as coberturas de verão de meados de setembro a dezembro, estendendo até o fim do verão onde não gela, e as de inverno do início de março a junho.
  - As faixas do modelo com chance ≥ 80% se sobrepõem a essas janelas: milheto até o fim de jan, mucuna até ~meados de jan, aveia de mar até ~20/abr em Ituporanga e até o fim de mai em SMO. Isso **bate** em termos qualitativos.
  - O modelo é mais restritivo para a aveia em Ituporanga só porque exigimos cobertura até 10/jul (transplante da cebola). Com prazo 31/jul, a data-limite vai a 5/mai.
  - Não achamos dado de campo de biomassa por data de semeadura em Ituporanga para calibrar. O artigo da Epagri encontrado era de aveia-branca para grão, em Campos Novos, e não serve.
- **O critério de sucesso foi atingido?** **Não.** Plausibilidade externa: sim. C1: não. C2: não. A data habitual já tem ≥ 90% de sucesso em todos os casos.

## 4. Régua (1 a 5)
| Critério | Nota | Por quê (uma frase) |
|---|---|---|
| Problema real | 2 | O solo descoberto depois da colheita é real, mas a falha da cobertura por causa do clima na semeadura quase não aparece nos dados (0–7% dos anos). |
| Tamanho do impacto | 2 | Só muda algo em anos de colheita atrasada (mucuna depois de ~10/jan, aveia depois de ~20/abr em Ituporanga). |
| Resolve de fato | 2 | A data habitual já dá ≥ 90% de chance; a ferramenta não melhora a decisão na maioria dos anos. |
| Validade | 2 | Testada com dado oficial, mas não supera a linha de base, e o limite depende de parâmetros de planta não calibrados (±2–3 semanas). |
| Muda a decisão | 2 | Só a escolha da espécie quando a semeadura atrasa ("passou de 10/jan, troque mucuna por milheto"). |
| Simples e factível | 4 | Graus-dia mais um balanço hídrico com POWER rodam em segundos por ponto. |
| Alinhamento com o desafio | 4 | Cobertura de solo é parte central da rotação que o desafio pede. |
| Diferencial | 2 | A Epagri já publica janelas por estação; a novidade seria só a data-limite por local. |
| Cabe no hackathon | 5 | Pronto e reaproveitável. |
| **Total (máx. 45)** | **25** | |

## 5. Veredito
**Descartada** como "otimizar a janela de semeadura". Em SC úmido a chuva quase nunca derruba a cobertura, e a data habitual já fica dentro da janela segura. Sobra um subproduto pequeno e honesto: a **data-limite por espécie** para os anos de colheita atrasada, com a ressalva de ±2–3 semanas de incerteza.

## 6. Relação com o controle
**Complementa, pouco.** A data-limite por espécie pode virar uma linha no cartão de rotação do controle ("depois da cebola: milheto até o fim de janeiro; mucuna só até ~10/jan"). Não vale tempo de demo próprio. O resultado reforça que, em SC, o risco climático da rotação está menos na semeadura e mais no frio e no excesso de chuva.

## 7. Limites e o que não foi testado
- Os graus-dia até a boa cobertura são [ESTIMATIVA] de literatura geral, sem calibração local. A sensibilidade de −20% a +25% move as datas-limite em 2 a 3 semanas.
- A grade do POWER (~50 km) suaviza a geada. Ituporanga real gela mais que o `T2M_MIN` do POWER (1–2 dias/mês em jun–jul no POWER). Isso deixaria as coberturas de verão mais restritas no outono.
- A chuva do POWER (MERRA-2 corrigido) tem muitos dias de garoa e pode subestimar os veranicos no talhão. IMERG diário não foi testado (pede login Earthdata).
- Não modelamos excesso de chuva na semeadura (encharcamento, semente arrastada em encosta), que em SC pode pesar mais que a seca.
- Não testamos biomassa (t/ha), só o tempo até a boa cobertura. Também não validamos com NDVI de lavouras de cobertura reais.

## 8. Fontes
- NASA POWER, API diária, comunidade AG (arquivos do loop, baixados em 14/11/2026).
- FAO-56 (Allen et al., 1998): ET0 e coeficiente Ks.
- Epagri, dicas de escolha de plantas de cobertura (Krunwald e Wildner): https://www.agrolink.com.br/noticias/como-escolher-as-plantas-de-cobertura--confira-dicas-da-epagri_439687.html
- Epagri, folder de plantio direto na palha de cebola (coberturas de verão e inverno usadas em Ituporanga): https://ciram.epagri.sc.gov.br/ciram_arquivos/cebola/acervo/Folder_plantio_direto_na_palha_tripes.pdf
- Lido e descartado como fonte (aveia-branca para grão, Campos Novos): Alves e Ramos, Agropec. Catarin. v.14 n.3, 2001, https://publicacoes.epagri.sc.gov.br/rac/article/download/1400/1246
