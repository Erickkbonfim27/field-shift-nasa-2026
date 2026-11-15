# B2-2 · Calendário de pisoteio no leite (compactação do solo)

Sessão: B2 · Trilha: B · Região: São Miguel do Oeste · Tentativa 2 de 4 · Data: 2026-11-14

## 1. Ideia (escrita antes do teste)
- **Hipótese:** no Extremo Oeste, o gado de leite pasteja a aveia e o azevém de inverno (maio a setembro) na mesma área que recebe o milho em seguida. Pisoteio com o solo encharcado compacta a camada de cima. A umidade relativa do solo superficial do NASA POWER (GWETTOP) mostra quantos dias de cada inverno são de risco, e esse número muda muito de ano para ano. Por isso um calendário fixo erra, e invernos com muitos dias de risco derrubam o milho seguinte.
- **Problema que ataca (e para quem):** o produtor de leite familiar com integração lavoura-pecuária, que precisa decidir quantos piquetes e quanta área de descanso ou de sacrifício reservar no inverno, e quando tirar o gado da área do milho.
- **Decisão que muda:**
  - Antes do inverno: planejar a área de sacrifício e a lotação pela chance de um inverno encharcado ("em 3 de cada 10 invernos, mais de X dias de risco").
  - No dia a dia: tirar o gado da área do milho nos dias de risco.
- **Critério de sucesso (definido antes):** três partes.
  1. **Variação:** o número de dias de risco no inverno (maio a setembro) varia com coeficiente de variação ≥ 0,30 entre anos (1985–2024).
  2. **Sinal próprio:** a regra do POWER discorda da regra só de chuva em ≥ 25% dos dias de risco. Se concordar quase sempre, o dado não acrescenta nada ao que o agricultor já vê.
  3. **Efeito no milho:** correlação parcial de Spearman ≤ −0,30 (p < 0,10) entre os dias de risco do inverno do ano t e o rendimento do milho da safra colhida em t+1 (IBGE PAM, São Miguel do Oeste, sem tendência). O controle é a chuva de novembro a fevereiro da mesma safra.
  - **Aprovada** se as três passarem; **ajustar** se passarem 1 e 2 mas não a 3.
- **Linha de base:** (a) calendário fixo, que é a média dos anos; (b) a regra só de chuva: dia de risco se a chuva somar ≥ 30 mm em 3 dias, que é o que o agricultor vê sem satélite.
- **Definições fixadas antes:**
  - Dia de risco: GWETTOP ≥ 0,80, com sensibilidade em 0,75 e 0,85.
  - Inverno: 1º de maio a 30 de setembro.
  - Dado: NASA POWER diário no ponto (−26,725; −53,518), arquivo `dados/power_sao_miguel_do_oeste.json`.
  - Rendimento: IBGE PAM tabela 1612, milho em grão, município 4217204 (conferência externa).

## 2. Teste
- **Dados oficiais usados:** NASA POWER diário (MERRA-2), `GWETTOP` (umidade relativa do solo na camada de cima, 0 a 1) e `PRECTOTCORR` (chuva), de 1985 a 2024, ponto de São Miguel do Oeste, grade de ~50 km.
- **Método:**
  1. Contei os dias de risco (GWETTOP ≥ 0,80) de 1º de maio a 30 de setembro de cada ano.
  2. Comparei com a regra só de chuva (≥ 30 mm somados em 3 dias).
  3. Testei a correlação parcial com o rendimento do milho da safra seguinte (PAM, sem tendência), controlando a chuva de novembro a fevereiro.
  4. Rodei a sensibilidade em 0,75 e 0,85.
  - Script: `sessoes/B2/pisoteio.py`. Saída: `sessoes/B2/pisoteio_resultado.json`.
- **Resultado (limiar 0,80):**
  - **Quantos dias:** em média 70 dias de risco por inverno, com desvio de 46. O coeficiente de variação é 0,66, e 0,60 depois de tirar a tendência. Vai de 3 dias (2006) a 153 (1990 e 1998, o inverno todo) [CÁLCULO].
  - **Regra do POWER contra a regra de chuva:** a regra do POWER marca 46% dos dias de inverno como risco. Em 71% deles não houve chuva forte nos 3 dias anteriores. A regra de chuva sozinha marca muito menos: 25 dias por ano em média [CÁLCULO].
  - **Tendência forte:** os dias de risco caem de 98 por inverno (1985–1999) para 61 (2000–2012) e 45 (2013–2024), com ρ = −0,44 contra o ano (p = 0,005). Nesses três períodos, a chuva de inverno do próprio POWER foi de 5,15, 4,13 e 3,97 mm/dia. A chuva caiu 23% e depois ficou estável, mas o GWETTOP continuou caindo. Isso aponta deriva do modelo, não do clima [CÁLCULO, INFERÊNCIA].
  - **Efeito no milho seguinte:** correlação parcial de −0,15 (p = 0,37, n = 40). A regra de chuva dá o mesmo: −0,15 (p = 0,35). Com o limiar de 0,75 dá −0,02; com 0,85, −0,15 [CÁLCULO].
  - **Poder do teste:** a própria chuva do verão quase não explica o rendimento da PAM no município (ρ = 0,14, p = 0,38), embora os anos ruins da PAM (1991, 2005, 2012 e 2022) sejam estiagens conhecidas. Ou seja, o rendimento municipal anual é um gabarito fraco para efeitos pequenos [CÁLCULO].
- **Gráfico:** `sessoes/B2/pisoteio.svg`. As barras mostram os dias de risco por inverno, com a média tracejada (o calendário fixo) e os pontos laranja da regra de chuva. Dá para ver a variação grande e a queda ao longo das décadas.

## 3. Validação
- **Contra a linha de base:**
  - **Calendário fixo:** erra muito em qualquer ano, porque o desvio é de 46 dias sobre uma média de 70. Mas parte dessa "variação" é a deriva do GWETTOP.
  - **Regra de chuva:** a regra do POWER discorda dela em 71% dos dias de risco. Não há gabarito de solo encharcado para dizer qual das duas acerta.
  - **Milho:** nem a regra do POWER (−0,15) nem a de chuva (−0,15) prevê o rendimento do milho.
- **Fonte externa:** os experimentos de integração lavoura-pecuária no Sul mostram o mesmo.
  - Em Latossolo com aveia e azevém, o pisoteio muda a física do solo, mas não reduz o rendimento da soja seguinte com manejo adequado ([Ciência Rural/Redalyc](https://www.redalyc.org/pdf/331/33113643030.pdf); [Embrapa Alice](https://www.alice.cnptia.embrapa.br/alice/bitstream/doc/1090880/1/JamirLuisSilvaGabrielaCientifRuralSIPAsobre.pdf)).
  - Um estudo em SC não achou efeito da altura de manejo do pasto sobre a resistência à penetração ([Redalyc](https://www.redalyc.org/pdf/1802/180214032014.pdf)).
  - O risco de compactação se concentra no inverno e na primavera úmidos, o que bate com a hipótese. Mas o efeito no rendimento depende mais da altura do pasto do que dos dias de chuva.
  - Sobre a deriva: há estudo apontando viés de tendência na umidade do solo do MERRA-2 ligado à chuva corrigida ([HESS 2025](https://hess.copernicus.org/articles/29/397/2025/hess-29-397-2025.pdf)).
  - **Bate com o resultado negativo.**
- **O critério de sucesso foi atingido?** **Não.**
  - O critério 1 passou: CV de 0,66.
  - O critério 2 passou no número (71% de discordância), mas a discordância vem em boa parte da deriva do GWETTOP. Na pré-definição, eu tinha dito que o critério 2 serviria para medir sinal próprio, e sem gabarito não dá para chamar isso de sinal.
  - O critério 3 falhou.

## 4. Régua (1 a 5)
| Critério | Nota | Por quê (uma frase) |
|---|---|---|
| Problema real | 3 | A compactação por pisoteio no inverno úmido existe e é estudada no Sul, mas o efeito no rendimento aparece pouco quando o pasto é bem manejado. |
| Tamanho do impacto | 2 | Nem a literatura nem a PAM mostram perda de milho ligada a invernos úmidos. |
| Resolve de fato | 2 | No dia a dia, o agricultor vê o barro melhor que uma grade de 50 km; o número para planejar o inverno vem contaminado pela deriva. |
| Validade | 2 | Não supera a linha de base no milho (−0,15 contra −0,15 da regra de chuva) e não há gabarito de solo encharcado. |
| Muda a decisão | 2 | Mudaria a reserva de área de sacrifício em poucos anos, mas sem evidência de que isso paga. |
| Simples e factível | 4 | Só o POWER, já baixado; a conta é trivial. |
| Alinhamento com o desafio | 3 | Usa dado da NASA e toca a integração lavoura-pecuária, mas é mais manejo do pasto que rotação. |
| Diferencial | 2 | É uma regra de chuva com outra roupa; os técnicos já recomendam tirar o gado com solo encharcado. |
| Cabe no hackathon | 5 | Pronto em uma hora. |
| **Total (máx. 45)** | **25** | |

## 5. Veredito
**Descartada.** O número de dias de risco varia, mas não prevê o milho, não supera a regra só de chuva e carrega uma deriva de décadas no GWETTOP do POWER. A literatura de integração lavoura-pecuária no Sul confirma que o pisoteio de inverno, com pasto bem manejado, quase não tira rendimento.

## 6. Relação com o controle
Não compete. No máximo, entra como aviso dentro do controle ("solo encharcado: evite pôr o gado ou a máquina") usando chuva. Não justifica uma ideia própria.

## 7. Limites e o que não foi testado
- **Escala:** a grade do POWER é de ~50 km. O SMAP (9 km, desde 2015) seria o dado certo para o estado do solo, mas pede login Earthdata e não foi testado.
- **Limiar:** o 0,80 não foi calibrado com a capacidade de campo do Latossolo e Nitossolo do Oeste.
- **Gabarito:** a PAM é o rendimento do milho em grão do município. Não separa a área pastejada no inverno nem o milho para silagem, que é o do leite.
- **Deriva:** o GWETTOP do MERRA-2 cai entre décadas mais que a chuva. Quem usar o GWETTOP em outra sessão deve olhar isso (vale também para a nota de saúde do solo da A3, que usa o GWETTOP).
- **Não testado:** a máquina na colheita da silagem em solo úmido (jan–fev).

## 8. Fontes
- NASA POWER, `dados/power_sao_miguel_do_oeste.json` [DADO].
- IBGE PAM, tabela 1612, milho em grão, São Miguel do Oeste (4217204): `https://apisidra.ibge.gov.br/values/t/1612/n6/4217204/v/109,216,214,112/p/all/c81/2711` [DADO, conferência].
- Ciência Rural, pastejo de aveia e azevém e a soja seguinte: https://www.redalyc.org/pdf/331/33113643030.pdf
- Embrapa Alice, sistemas integrados no Sul: https://www.alice.cnptia.embrapa.br/alice/bitstream/doc/1090880/1/JamirLuisSilvaGabrielaCientifRuralSIPAsobre.pdf
- Resistência à penetração em SC: https://www.redalyc.org/pdf/1802/180214032014.pdf
- Viés de tendência na umidade do solo de reanálises: https://hess.copernicus.org/articles/29/397/2025/hess-29-397-2025.pdf
