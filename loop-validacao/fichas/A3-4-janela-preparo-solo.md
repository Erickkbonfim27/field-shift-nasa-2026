# A3-4 · Janela de preparo do solo com menor chance de chuva forte

Sessão: A3 · Trilha: A · Região: Ituporanga · Tentativa 4 de 4 · Data: 2026-11-14

## 1. Ideia (escrita antes do teste)
- **Hipótese:** o A3-1 mostrou que o solo da lavoura fica mais exposto em junho e julho (preparo e transplante da cebola). Se a chance de chuva forte nos 45 dias depois do preparo muda bastante de uma quinzena para outra, o agricultor pode escolher a quinzena de preparo com menos risco de erosão, dentro da janela agronômica da cebola. É a mesma lógica do controle ("em x de cada 10 anos"), aplicada ao solo.
- **Problema que ataca (e para quem):** perda de solo no preparo convencional da cebola em encosta (Ituporanga). Serve ao agricultor e ao extensionista.
- **Decisão que muda:** a data de preparo e transplante (1º de maio a 1º de agosto) e se vale a pena antecipar a cobertura ou a palhada naquele ano.
- **Critério de sucesso (definido antes):**
  - **J1, o risco muda com a data:** entre 7 datas de preparo (1/mai, 15/mai, 1/jun, 15/jun, 1/jul, 15/jul, 1/ago), a chance de ≥ 1 dia com chuva ≥ 25 mm nos 45 dias seguintes (NASA POWER, 1981–2025) varia ≥ 15 pontos percentuais entre a melhor e a pior data.
  - **J2, conferência externa:** a ordem das 7 janelas pela chuva do POWER bate com a ordem pela erosividade mensal do pluviômetro da ANA em Ituporanga (Back et al. 2023, Tab. 3, ponderada pelos dias da janela): Spearman ≥ 0,7.
  - **J3, robustez:** a melhor e a pior data são as mesmas na 1ª metade (1981–2003) e na 2ª metade (2004–2025) da série.
  - **Aprovada** se J1, J2 e J3 passarem.
- **Linha de base:** "não fazer nada", ou seja, preparar na data de costume, sem diferença de risco entre datas (diferença = 0).

## 2. Teste
- **Dados oficiais usados:** NASA POWER `PRECTOTCORR` diário de 1981 a 2025 (~50 km), Ituporanga.
- **Método:**
  - Para cada ano e cada data de preparo, olhei se houve ≥ 1 dia com chuva ≥ 25 mm nos 45 dias seguintes e calculei a frequência entre os 45 anos.
  - Também somei P² da janela, que tem forma de erosividade.
  - Para a conferência, ponderei o EI30 mensal do pluviômetro (Back et al. 2023) pelos dias de cada mês na janela.
  - Script: `sessoes/A3/a3_4_janela.py`.
- **Resultado** (`sessoes/A3/a3_4_resultado.json`). Chance de ≥ 1 dia com ≥ 25 mm em 45 dias [CÁLCULO]:

  | Preparo em | 1/mai | 15/mai | 1/jun | 15/jun | 1/jul | 15/jul | 1/ago |
  |---|---|---|---|---|---|---|---|
  | Chance | 0,60 | 0,64 | 0,67 | 0,69 | 0,67 | 0,53 | 0,60 |

  - Diferença entre a melhor e a pior data: 15,6 pontos, com IC de 95% de −4,3 a 35,4 [CÁLCULO].
  - A chance subiu de uma metade da série para a outra: de 0,48–0,65 (1981–2003) para 0,59–0,77 (2004–2025) [CÁLCULO].
- **Gráfico:** `sessoes/A3/a3_4_janelas.png`. As curvas das duas metades da série têm formas diferentes, e o EI30 do pluviômetro sobe de maio para agosto sem acompanhar o POWER.

## 3. Validação
- **J1:** 15,6 pontos (≥ 15). Passa por pouco, mas o intervalo de confiança inclui zero, então a diferença pode ser ruído [CÁLCULO].
- **J2:** Spearman entre a chance pelo POWER e o EI30 da janela pelo pluviômetro = **−0,27**; com a soma de P², 0,04 [CÁLCULO]. **Não passa.** O pluviômetro diz que a erosividade sobe de maio (660) para agosto (965) [CÁLCULO sobre DADO de Back et al. 2023]; o POWER não mostra isso.
- **J3:** a melhor data é 15/jul nas duas metades, mas a pior muda (1/jul contra 15/mai) [CÁLCULO]. **Não passa.**
- **Fonte externa:** Back et al. (2023) dizem que a chuva em Ituporanga é "uniforme" ao longo do ano (índice de concentração ICP = 8,6). Isso explica por que trocar a data dentro do inverno muda pouco o risco [DADO].
- **O critério de sucesso foi atingido?** **Não.**

## 4. Régua (1 a 5)
| Critério | Nota | Por quê (uma frase) |
|---|---|---|
| Problema real | 3 | Preparar o solo na véspera de chuva forte causa erosão, mas a data da cebola depende mais da muda e da cultivar. |
| Tamanho do impacto | 2 | A diferença entre datas é pequena e incerta. |
| Resolve de fato | 1 | A diferença entre janelas não é distinguível de ruído, então não justifica mudar a data. |
| Validade | 1 | A ordem das janelas não bate com o pluviômetro (Spearman −0,27) e muda entre metades da série. |
| Muda a decisão | 2 | Um aviso de "melhor quinzena" sem sinal real faria o agricultor mudar à toa. |
| Simples e factível | 4 | Só precisa do POWER diário. |
| Alinhamento com o desafio | 4 | É a lógica de probabilidade do controle aplicada ao solo. |
| Diferencial | 2 | É uma climatologia simples; sem sinal, não diferencia. |
| Cabe no hackathon | 5 | Roda em segundos. |
| **Total (máx. 45)** | **24** | |

Aprovada só com 3+ em problema real, resolve de fato e validade: **não atende.**

## 5. Veredito
**Descartada.** No inverno de Ituporanga, a chance de chuva forte nos 45 dias depois do preparo é parecida em todas as quinzenas (53% a 69%), e a ordem entre elas não se sustenta. Resultado negativo honesto: o risco no preparo vem de deixar o solo nu, não da data escolhida.

## 6. Relação com o controle
Usa a mesma lógica do controle, mas aqui o clima não dá sinal útil. O recado para a demo é que, no preparo do inverno, a proteção que funciona é a cobertura ou a palhada (estratégia D), não mudar a data.

## 7. Limites e o que não foi testado
- O POWER (~50 km) suaviza a chuva intensa; 25 mm/dia no POWER não é o mesmo que 25 mm no pluviômetro.
- Não testei o IMERG (login), o ERA5, nem a chuva sub-diária.
- A janela de 45 dias e o limiar de 25 mm são escolhas minhas, fixadas antes do teste.

## 8. Fontes
- Back, Justen e Guadagnin (2023), *Agropecuária Catarinense* 36(3), Tab. 3 e ICP. https://doi.org/10.52945/rac.v36i3.1766
- NASA POWER, `dados/power_ituporanga.json`.
