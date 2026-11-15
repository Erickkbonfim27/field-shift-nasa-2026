# B4-3 · Fugir do pico de oferta da cebola: vender na colheita ou guardar e vender em março–abril

Sessão: B4 · Trilha: B · Região: Ituporanga · Tentativa 3 de 4 · Data: 2026-11-14

## 1. Ideia (escrita antes do teste)
- **Hipótese:** o preço ao produtor da cebola em SC é mais baixo no pico da colheita (nov–dez) e sobe em mar–abr, quando o galpão é a única oferta do Sul. Escalonar a venda (guardar parte e vender depois) foge do pico. A parte NASA: a chuva de primavera no POWER (set–nov) diz em quais anos a alta de mar–abr vai ser maior (quebra → estoque curto → alta maior), para dizer quanto guardar.
- **Problema que ataca (e para quem):** o produtor familiar vende quase tudo na colheita, quando todo o Sul vende junto, e pega o preço mais baixo do ano.
- **Decisão que muda:** em dezembro, quanto da colheita guardar no galpão para vender em mar–abr.
- **Critério de sucesso (definido antes):**
  1. Preço real de mar–abr (ano t+1) supera o de nov–dez (ano t) em **pelo menos 15%** (o que cobre, por estimativa, a perda de peso e podridão no galpão) em **pelo menos 70%** das safras.
  2. A chuva set–nov do POWER explica o tamanho dessa alta: **|ρ| ≥ 0,40** (Spearman).
  - Se só o 1 passar, a ideia funciona, mas a entrada que decide é o preço (fonte externa) e a NASA não acrescenta: nota baixa em alinhamento e veredito "descartada para este desafio".
- **Linha de base:** vender tudo na colheita (nov–dez).
- **Aviso de regra:** esta ideia só funciona com preço como entrada. Pontuo alinhamento e validade de acordo.

## 2. Teste
- **Dados oficiais usados:** NASA POWER `PRECTOTCORR`, Ituporanga, soma de 1º/set a 30/nov, 1998–2025 (~50 km).
- **Dado externo usado para calibrar e conferir:** Epagri/Cepa, preço mensal recebido pelo produtor, cebola pera SC classe 3 a 5, corrigido pelo IPCA (dez/2025). A série só tem preço de nov a abr ou mai (os meses em que SC vende cebola); 2005–2008 têm buracos, então ficam 24 safras.
- **Método:** prêmio de guardar = média de mar–abr (t+1) ÷ média de nov–dez (t) − 1. Alarme = terço mais chuvoso do índice (≥ 464 mm). Simulação de regra com perda no galpão de 15% [ESTIMATIVA, não medida]: (a) vender tudo na colheita; (b) guardar 50% sempre; (c) regra NASA: guardar 50% só quando não há alarme; (d) guardar tudo. Scripts: `sessoes/B4/teste3_mensal.py`, `teste3_regra.py`.
- **Resultado:**
  - Prêmio ≥ 15% em **18 de 24 safras (75%)**; mediana +58%. [CÁLCULO]
  - Chuva set–nov × prêmio: **ρ = −0,397** (p = 0,055). O sinal é o **contrário** do que a hipótese dizia: depois de primavera chuvosa, o preço já começa alto na colheita e sobe pouco depois (prêmio mediano +16% nos anos de alarme contra +72% nos outros; prêmio ≥ 15% em 4 de 8 alarmes contra 14 de 16 nos outros). [CÁLCULO]
  - Regras (receita em múltiplos do preço da colheita, média de 24 safras): vender tudo 1,00; guardar 50% sempre 1,14 (pior ano 0,74; 6 anos abaixo de vender tudo); **regra NASA 1,14 (pior ano 0,87; 2 anos abaixo)**; guardar tudo 1,28 (pior ano 0,47; 6 anos abaixo). [CÁLCULO]
- **Gráfico:** `sessoes/B4/grafico3_cebola_preco_mensal.svg`, painel da direita: acima de ~464 mm de chuva na primavera, o prêmio de guardar quase some.

## 3. Validação
- **Contra a linha de base (vender tudo na colheita):** guardar parte rende em média 14% a mais por kg; a regra NASA mantém esse ganho médio e corta os anos ruins de 6 para 2 (o pior ano passa de 0,74 para 0,87).
- **Fonte externa:** a própria série da Epagri/Cepa (é a conferência e a calibração). O padrão "preço baixo em nov–dez, alto em mar–abr" aparece em 19 de 24 safras da série da Epagri/Cepa; as 5 exceções (1998, 2004, 2009, 2016, 2022) incluem 3 anos (1998, 2009, 2022) em que o preço da colheita já começou alto. [CÁLCULO]
- **O critério de sucesso foi atingido?** **Em parte.** O item 1 passou (75%). O item 2 ficou em |ρ| = 0,397, por um fio abaixo de 0,40, e no sentido oposto ao da hipótese; ainda assim, a regra que sai dele reduz o risco.

## 4. Régua (1 a 5)
| Critério | Nota | Por quê (uma frase) |
|---|---|---|
| Problema real | 4 | Vender tudo no pico da colheita do Sul é comum entre pequenos produtores [INFERÊNCIA], e o preço de mar–abr foi maior em 19 de 24 safras. |
| Tamanho do impacto | 3 | +14% de receita média por kg guardado é bom, mas depende de galpão, que nem todo familiar tem. |
| Resolve de fato | 3 | A parte NASA muda a decisão em 1 ano de cada 3 (alarme: vender na colheita) e corta os anos de prejuízo de 6 para 2. |
| Validade | 3 | Calculado com 24 safras e conferido com preço oficial da Epagri, mas o critério 2 ficou no limite e a perda no galpão é estimada. |
| Muda a decisão | 4 | "Quanto guardar" é decisão de todo ano, e a resposta muda com a chuva da primavera. |
| Simples e factível | 4 | Uma soma de chuva do POWER e um limiar; o limiar foi calibrado com preço histórico. |
| Alinhamento com o desafio | 3 | Na hora de usar, a entrada é só NASA; mas a regra (limiar e o próprio "guardar vale a pena") vem de preço externo, e não é rotação de culturas. |
| Diferencial | 4 | Liga clima a mercado de um jeito que o ZARC e o controle não fazem. |
| Cabe no hackathon | 5 | Já calculado; vira um cartão a mais na demo. |
| **Total (máx. 45)** | **33** | |

## 5. Veredito
**Ajustar.** Passa nas três notas obrigatórias (4/3/3), mas o pré-registro só passou em parte e a direção do sinal foi a oposta da hipótese. Ajuste: fundir com a B4-1 numa regra única de venda ("primavera chuvosa: venda na colheita e não aumente a área; primavera normal: guarde parte para mar–abr"), pré-registrar o limiar de 464 mm e conferir na safra 2026/27.

## 6. Relação com o controle
**Complementa.** O controle diz se a lavoura vai dar; esta diz o que fazer com a cebola que deu. Na demo, entra como cartão de novembro para o produtor de Ituporanga, com a mesma chuva do POWER que o controle já baixa.

## 7. Limites e o que não foi testado
- Perda de peso e podridão no galpão fixadas em 15% sem medir; essa perda deve ser maior em verão quente e úmido (dá para estimar com `T2M` e `RH2M` do POWER, não testado).
- Preço da Epagri é média estadual de praças; o preço do talhão varia com classe e comprador.
- Não testei colheita precoce ou tardia (mudar a data de transplante), que era a outra metade da ideia 3 da lista: não há preço da cebola de SC em out ou jun para comparar, e a parte de clima repete A1/B1.
- 24 safras, 8 alarmes; ρ no limite de significância (p = 0,055).

## 8. Fontes
- NASA POWER, API diária, comunidade AG: https://power.larc.nasa.gov/ (arquivo `dados/power_ituporanga.json`).
- Epagri/Cepa, preços recebidos pelos produtores 1998–2026: https://docweb.epagri.sc.gov.br/website_cepa/precos/Precos_recebidos_1998_2026.xlsx (página: https://cepa.epagri.sc.gov.br/index.php/mercado-agricola/).
- IBGE SIDRA, IPCA t.1737: https://apisidra.ibge.gov.br/values/t/1737/n1/all/v/2266/p/all
