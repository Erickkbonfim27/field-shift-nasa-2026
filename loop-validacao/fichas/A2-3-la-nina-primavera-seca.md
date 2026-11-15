# A2-3 · La Niña sabida em agosto prevê primavera seca (out–nov)?

Sessão: A2 · Trilha: A · Região: São Miguel do Oeste (Ituporanga como replicação) · Tentativa 3 de 4 (variação de A2-1) · Data: 2026-11-14

## 1. Ideia (escrita antes do teste)
Critério gravado depois de A2-1 e A2-2 e antes de olhar qualquer dado de out–nov (`sessoes/A2/CRITERIOS_ANTES_DO_TESTE.md`).
- **Hipótese:** a literatura diz que o sinal do ENSO no Sul do Brasil é mais forte na primavera. Então a La Niña sabida no fim de agosto (ONI de JAS) deveria prever uma primavera seca (out–nov), a época do plantio e do arranque do milho. A quebra de 2020/21 no Oeste veio da primavera seca.
- **Problema que ataca (e para quem):** o produtor de milho e leite de SMO, na decisão de data de plantio (ago–nov).
- **Decisão que muda:** em ano de La Niña, mudar a data de plantio do milho.
- **Critério de sucesso (definido antes):** todos: (1) P(seco | La Niña JAS) ≥ 0,50 e P(seco | El Niño JAS) ≤ 0,20; (2) Fisher p < 0,10; (3) BSS LOO > 0,05; (4) mesmo sinal nas duas metades; (5) mesmo sentido em Ituporanga. **Muda a decisão** se a melhor data de plantio do milho simulado (5 datas, de 21/ago a 11/nov) em anos de La Niña for diferente da melhor data de todos os anos, com ≥ 10 p.p. de diferença na chance de perda.
- **Linha de base:** média de todos os anos (1 em 3).

## 2. Teste
- **Dados oficiais usados:** NASA POWER diário, SMO e Ituporanga, 1981–2025: `PRECTOTCORR`, variáveis da ET0 e `GWETROOT`. ONI de JAS da NOAA (fonte externa, só para separar os anos).
- **Método:** alvo = soma de (chuva − ET0) de 1/out a 30/nov no tercil inferior (41 safras). Checagens: chuva out–nov (44 safras) e GWETROOT em 30/nov. Milho simulado (`risco.py`, solo argiloso) plantado em 21/ago, 11/set, 1/out, 21/out e 11/nov. Script: `sessoes/A2/a2_3_enso_primavera.py`. Saída: `sessoes/A2/resultados/a2_3_smo.json` e `a2_3_itu.json`.
- **Resultado (SMO, P−ET0 out–nov)** [CÁLCULO]: La Niña 3 de 8 = 38%; neutro 10 de 25 = 40%; **El Niño 1 de 8 = 12%**; todos os anos 34%. Fisher p = 0,29; BSS −0,04. O ONI contínuo, porém, correlaciona com a primavera úmida (ρ = +0,49, p < 0,01). Metades: La Niña seca em 3 de 4 em 1981–2002 e em 0 de 4 em 2003–2024.
  - Ituporanga: La Niña 38%, neutro 44%, **El Niño 0 de 8**; ρ = +0,43.
  - GWETROOT em 30/nov (SMO): La Niña 5 de 8 = 62%, El Niño 1 de 9 = 11% (p = 0,04), mas BSS +0,02.
  - Data de plantio: em todos os grupos a melhor data simulada é 21/ago (0% de perda). Só no El Niño ela empata com 11/set. A melhor data não muda com a fase.
- **Gráfico:** `sessoes/A2/a2_3_primavera_enso.svg`. A La Niña não se separa do neutro; só o El Niño fica bem abaixo da média.

## 3. Validação
- **Contra a linha de base:** 38% contra 34%; BSS −0,04. Não supera.
- **Fonte externa:** IBGE PAM, milho da microrregião 42001, por fase do ONI de JAS: quebras em 1 de 7 La Niñas, 4 de 20 neutros e 1 de 7 El Niños; rendimento médio de 1,00, 0,96 e 0,99 [DADO + CÁLCULO]. Não há diferença. A literatura (Grimm et al.) põe o sinal mais forte na primavera e mais claro no El Niño: bate com a assimetria, não com a hipótese da La Niña. [Link do IBGE](https://apisidra.ibge.gov.br/values/t/1612/n9/42001/v/112/p/all/c81/2711).
- **O critério de sucesso foi atingido?** **Não.** Falha nos itens 1 a 4. O item 5 vale só no sentido do El Niño. A decisão de data também não muda.

## 4. Régua (1 a 5)
| Critério | Nota | Por quê (uma frase) |
|---|---|---|
| Problema real | 4 | A primavera seca de 2020 levou à quebra da colheita de 2021 no IBGE da microrregião (rendimento 0,52 do normal). |
| Tamanho do impacto | 2 | La Niña não desloca a chance (38% contra 34%). |
| Resolve de fato | 2 | A melhor data de plantio simulada é a mesma em todas as fases. |
| Validade | 2 | Não supera a climatologia, inverte entre as metades e o IBGE não mostra diferença. |
| Muda a decisão | 1 | Critério de mudança de data não atingido. |
| Simples e factível | 3 | O cálculo é simples, mas depende do ONI externo. |
| Alinhamento com o desafio | 3 | Previsibilidade para a data de plantio, com um índice de fora do Resources. |
| Diferencial | 2 | Igual ao boletim de ENSO que a Epagri/Ciram já divulga. |
| Cabe no hackathon | 4 | Rápido de rodar. |
| **Total (máx. 45)** | **23** | |

## 5. Veredito
**Descartada.** A La Niña não é um sinal estável de primavera seca nesses 41 anos de POWER. De novo, só o El Niño se destaca (1 de 8 e 0 de 8 primaveras secas), e isso foi para o teste confirmatório A2-4.

## 6. Relação com o controle
Não compete. Reforça que, no Oeste de SC, o controle não deve pôr peso maior em "ano de La Niña" sem base nos dados.

## 7. Limites e o que não foi testado
- Só 8 La Niñas em JAS. Com o limiar de −0,5, as La Niñas de 2020 e 2021 (ONI de JAS −0,43 e −0,46) contam como neutras. Um limiar mais baixo mudaria a contagem, mas não foi definido antes e não foi testado.
- O milho simulado não tem risco de geada em ago–set nem dano por excesso de chuva. Por isso o plantio em 21/ago parece sempre o melhor, o que é irreal.
- POWER com ~50 km; ONI é fonte externa.

## 8. Fontes
- NASA POWER diário: `loop-validacao/dados/power_sao_miguel_do_oeste.json` e `power_ituporanga.json` [DADO].
- NOAA CPC, ONI: https://www.cpc.ncep.noaa.gov/data/indices/oni.ascii.txt [DADO externo, só para separar os anos].
- IBGE SIDRA, tabela 1612, microrregião 42001: https://apisidra.ibge.gov.br/values/t/1612/n9/42001/v/112/p/all/c81/2711 [conferência].
- Grimm et al. (1998, 2000), *J. Climate* [citados de memória, conferir].
