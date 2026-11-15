# B4-2 · Quebra regional de milho como aviso de comida cara para o leite

Sessão: B4 · Trilha: B · Região: São Miguel do Oeste · Tentativa 2 de 4 · Data: 2026-11-14

## 1. Ideia (escrita antes do teste)
- **Hipótese:** a seca de dezembro–janeiro (pendoamento e enchimento do milho de verão) no Extremo Oeste derruba a safra de milho da região inteira. Quando isso acontece, o milho e a silagem ficam escassos e caros para quem tem vaca de leite. Um índice do NASA POWER fechado em 31 de janeiro, antes da colheita (fev–mar), avisa isso com 1 a 2 meses de folga.
- **Problema que ataca (e para quem):** o produtor familiar de leite de São Miguel do Oeste depende do milho (silagem e grão). Em ano de estiagem regional ele descobre tarde que a silagem não fecha o ano e compra ração cara ou vende vacas.
- **Decisão que muda:** em ano de alarme, no fim de janeiro: ensilar todo o milho próprio em vez de vender grão; comprar ou contratar milho e ração antes da alta; plantar logo uma forrageira de segunda safra (sorgo, milheto) e antecipar a pastagem de inverno; não aumentar o rebanho.
- **Critério de sucesso (definido antes):**
  1. Índice principal = umidade relativa da zona das raízes (`GWETROOT`) média de 1º de dezembro a 31 de janeiro, POWER em São Miguel do Oeste. Secundário = chuva de dez–jan. Correlação de Spearman com a produtividade do milho da microrregião de São Miguel do Oeste sem tendência, 1985–2025: **ρ ≥ 0,50**.
  2. Anos de alarme (terço mais seco do índice) pegam **pelo menos 70%** dos anos de quebra (produtividade ≥ 20% abaixo da tendência), com **no máximo 30%** de alarmes falsos.
  3. Preço real do milho em SC (IBGE, valor ÷ quantidade, IPCA), 1995–2025: média nos anos de alarme **≥ 10% acima** dos outros anos.
  - Aprovada se 1 e 2 passarem. O 3 é conferência extra (o preço do milho é nacional, então espero sinal fraco).
- **Linha de base:** "não fazer nada" = tratar todo ano como normal (pega 0 quebras). Acaso: 33% das quebras com alarme em um terço dos anos.

## 2. Teste
- **Dados oficiais usados:** NASA POWER (AG), `GWETROOT` (umidade relativa da zona das raízes, MERRA-2, 0–1) e `PRECTOTCORR`, ponto -26,725; -53,518 (São Miguel do Oeste), dez (ano anterior) a jan, 1985–2025, grade de ~50 km. Arquivo `dados/power_sao_miguel_do_oeste.json`.
- **Método:** índice do ano da colheita t = média de `GWETROOT` (ou soma da chuva) de 1º/dez de t−1 a 31/jan de t; produtividade do milho da microrregião de São Miguel do Oeste (IBGE 42001; o município perdeu área em 1997 e repete valores, por isso a microrregião) sem tendência linear 1995–2025 (a microrregião não tem dado antes de 1990, então a versão 1985–2025 não roda); alarme = terço mais seco; quebra = ≥ 20% abaixo da tendência. Scripts: `sessoes/B4/teste2_milho.py`, `teste2_exploratorio.py`, `teste3_mensal.py` (parte do preço mensal).
- **Resultado (pré-registrado):**
  - `GWETROOT` dez–jan × produtividade: **ρ = +0,26** (p = 0,15; n = 31). Chuva dez–jan: ρ = +0,38 (p = 0,03). [CÁLCULO]
  - Quebras pegas: 4 de 6 (67%) com os dois índices; **7 alarmes falsos em 11 (64%)**. Quebras: 2002, 2005, 2012, 2021, 2022, 2024. [CÁLCULO]
  - Preço real do milho em SC (IBGE, valor ÷ quantidade): anos de alarme +28% acima dos outros, mas só +9% depois de tirar a tendência (o preço real subiu muito em 2020–2022 em todo o país). [CÁLCULO]
- **Exploratório (depois do teste, não conta):** varri 5 janelas × 2 variáveis. Nenhuma passou de ρ = 0,50; a chuva de nov–dez e de dez–jan dá ρ ≈ 0,4 nas duas metades da série (treino 1995–2010 e teste 2011–2025), o que indica sinal real, mas fraco. `GWETROOT` é pior que a chuva. Tirando 2021 (ano da cigarrinha-do-milho, perda que não é de clima [INFERÊNCIA]), ρ cai para +0,20 a +0,33.
- **Conferência do lado "mercado" com preço mensal (Epagri/Cepa, milho amarelo SC, 1999–2026):** em ano de alarme, o preço de mai–jun ficou 9% a 12% **abaixo** do de jan–fev, contra 2% a 3% abaixo nos outros anos. Ou seja, o aviso "compre antes da alta" não se confirma: o preço do milho em SC segue a safra nacional, não a do Extremo Oeste. [CÁLCULO]
- **Gráfico:** `sessoes/B4/grafico2_milho.svg`: a nuvem é larga; só 2012 e 2022 são secos e de quebra ao mesmo tempo.

## 3. Validação
- **Contra a linha de base:** pega 4 de 6 quebras contra 0 de "todo ano normal" e 33% do acaso, mas erra 7 de 11 alarmes.
- **Fonte externa:** IBGE PAM t.5457 (microrregião 42001); Epagri/Cepa, preço recebido do milho. Epagri/Cepa projetou em dez/2021 perda de até 50% do milho no Extremo Oeste (bate com 2022: −33% na PAM). Para a estiagem de 2019/20, a Epagri/Cepa citou quebra média de −19% no Extremo Oeste, mas a PAM da microrregião mostra 2020 **+21%**: não bate. [DADO, via reportagens; conferir nos boletins]
- **O critério de sucesso foi atingido?** **Não.** ρ = 0,26 (meta 0,50); acerto 67% (meta 70%) com 64% de alarmes falsos (meta ≤ 30%). O preço mensal vai no sentido contrário ao esperado.

## 4. Régua (1 a 5)
| Critério | Nota | Por quê (uma frase) |
|---|---|---|
| Problema real | 4 | Estiagens de 2012 e 2022 derrubaram o milho do Extremo Oeste em mais de 30%, e o leite depende dele. |
| Tamanho do impacto | 3 | Afeta a comida do rebanho de quase todo produtor de leite da região, mas só em 2 a 3 anos por década. |
| Resolve de fato | 2 | Com 64% de alarmes falsos e preço que cai depois do alarme, a ação "compre antes" erraria na maioria dos anos. |
| Validade | 2 | Supera o acaso de leve, mas não passa no critério e não bate com a estiagem de 2019/20. |
| Muda a decisão | 2 | O produtor vê a lavoura secando no próprio talhão; o índice regional pouco acrescenta. |
| Simples e factível | 4 | Uma média do POWER por ponto. |
| Alinhamento com o desafio | 4 | Entrada só NASA; preço só para conferir. |
| Diferencial | 2 | É o balanço hídrico do controle visto de longe, com menos resolução. |
| Cabe no hackathon | 4 | Pronto, mas não vale a pena levar. |
| **Total (máx. 45)** | **27** | |

## 5. Veredito
**Descartada.** O sinal de seca de dezembro–janeiro existe (chuva, ρ ≈ 0,4, estável), mas é fraco para um aviso de quebra regional, e o preço do milho em SC não sobe depois do alarme: é nacional. O pedaço útil (chuva de dez–jan como fase crítica do milho no Oeste) já cabe no controle.

## 6. Relação com o controle
**Compete pouco e acrescenta pouco.** O controle faz a mesma conta (água na fase crítica) com mais detalhe, por talhão. Não entra na demo como ideia própria.

## 7. Limites e o que não foi testado
- Um ponto do POWER (~50 km) para uma microrregião inteira; chuva de verão no Oeste é muito localizada.
- A janela dez–jan foi escolhida sem conferir o calendário local (o milho do Oeste é plantado cedo, ago–set); a varredura posterior não achou janela melhor que ρ ≈ 0,4.
- Produtividade da PAM é estimativa; 2021 tem a cigarrinha-do-milho misturada.
- Silagem não tem preço publicado; usei o preço do milho grão, que é mercado nacional.
- SMAP e GLDAS (umidade do solo melhor) não testados: pedem login Earthdata.

## 8. Fontes
- NASA POWER, API diária, comunidade AG: https://power.larc.nasa.gov/ (arquivo `dados/power_sao_miguel_do_oeste.json`).
- IBGE SIDRA, PAM t.5457, milho em grão (c782/40122), microrregião 42001, município 4217204 e SC: https://apisidra.ibge.gov.br/values/t/5457/n9/42001/v/112,214,215,216,8331/p/all/c782/40122
- Epagri/Cepa, preços recebidos 1998–2026 (milho amarelo, sc 60 kg): https://docweb.epagri.sc.gov.br/website_cepa/precos/Precos_recebidos_1998_2026.xlsx
- Epagri/Cepa sobre a estiagem 2021/22 e 2019/20, via reportagens: https://www.noticiasagricolas.com.br/noticia/305869 e https://www.noticiasagricolas.com.br/noticia/255924 (conferir nos boletins da Epagri/Cepa).
