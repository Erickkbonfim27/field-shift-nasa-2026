# B3-2 · Excesso de chuva na cebola: alerta de doença e podridão

Sessão: B3 · Trilha: B · Região: Ituporanga · Tentativa 2 de 4 · Data: 2026-11-14

## 1. Ideia (escrita antes do teste)
- **Hipótese:** o excesso de água de setembro a novembro (bulbificação e colheita), medido com o NASA POWER, explica os anos de quebra da cebola no Alto Vale. Um alerta semanal desse excesso marca as semanas de risco de míldio e podridão.
- **Problema que ataca (e para quem):** o agricultor familiar de Ituporanga perde cebola em anos de muita chuva: míldio na folha, bulbo que apodrece na roça e na cura, colheita atrasada. Ele pulveriza no calendário, sem saber quando o risco subiu.
- **Decisão que muda:** nas semanas de alerta, antecipar a pulverização preventiva e a colheita e priorizar a cura em galpão. No ano seguinte, reservar os talhões mais drenados (camalhão, encosta) para a cebola e deixar as baixadas para outra cultura.
- **Critério de sucesso (definido antes):**
  - Indicador principal: excedente hídrico de 1/set a 30/nov (mm que o solo não segura, balanço FAO-56 com Kc da cebola, raiz 0,3 m, solo médio).
  - Indicador secundário: dias de molhamento (chuva ≥ 1 mm e umidade relativa média ≥ 90%) de 1/set a 30/nov, aproximação de condição para míldio.
  - "Ano ruim" = rendimento da cebola (IBGE PAM, microrregião 42014) ≤ 85% da mediana dos 6 anos vizinhos (t−3 a t+3, sem t).
  - Limiar escolhido por validação deixando um ano de fora (LOO).
  - **Sucesso se:** acerta ≥ 2/3 dos anos ruins, com no máximo 40% de alarmes falsos, e correlação de Spearman indicador × rendimento relativo ≤ −0,4.
- **Linha de base:** (a) "não fazer nada" (nunca alerta); (b) "média dos anos" (alerta ao acaso com a frequência de anos ruins). Comparação extra: chuva total de set–nov.

## 2. Teste
- **Dados oficiais usados:** NASA POWER diário, comunidade AG, ponto −27,414; −49,601 (~50 km), 1984–2025: `PRECTOTCORR`, `RH2M`, temperaturas, vento e radiação (ET0). Água do solo: GAEZ v5, 125 mm/m × 0,3 m = 37,5 mm.
- **Método:**
  1. ET0 FAO-56 (fórmulas de `risco.py`).
  2. Balde diário da cebola: transplante 1/ago, fases 15/25/70/40, Kc 0,70/1,05/0,75 (FAO-56), p = 0,3.
  3. Excedente = chuva que passa do balde cheio, somada de 1/set a 30/nov.
  4. 36 safras (1990–2025).
  - Scripts: `sessoes/B3/comum.py`, `sessoes/B3/teste2_excesso_cebola.py`. Saída: `sessoes/B3/teste2_resultado.json`.
  - **Atenção:** o código IBGE de Ituporanga é **4208500**. O 4208401 do protocolo é Itapiranga (conferido na API de localidades do IBGE).
- **Resultado [CÁLCULO]** (microrregião 42014, 5 anos ruins: 1998, 2008, 2015, 2017, 2023):

  | Indicador | Spearman ρ (p) | Acertos (LOO) | Alarmes falsos |
  |---|---|---|---|
  | **Excedente set–nov (principal)** | **−0,18 (0,29)** | **3/5** | **5 de 8 (62%)** |
  | Dias de molhamento set–nov | −0,26 (0,13) | 3/5 | 6 de 9 (67%) |
  | Chuva set–nov | −0,12 (0,48) | 3/5 | 7 de 10 (70%) |
  | Semanas com ≥ 4 dias de molhamento | −0,18 (0,29) | 4/5 | 6 de 10 (60%) |

  - Os 4 anos de maior excedente são 2023 (661 mm), 2008 (507), 1997 (447) e 2015 (369). Três tiveram quebra (rendimento relativo 0,69, 0,79 e 0,71); 1997 caiu 9%. A chance de os 2 primeiros e o 4º serem anos ruins por acaso é pequena, mas é uma leitura feita depois do teste.
  - 2015 é o ano com mais dias de molhamento (40).
  - **2017 (rendimento relativo 0,75) foi quebra por falta de água:** excedente de 101 mm e ISNA de 0,75. Um índice só de excesso não vê esse ano.
  - Município 4208500: ρ = −0,17; 2/7 acertos.
  - Mudar a janela (out–nov, set–out, 15/out–15/dez) não melhora: ρ entre −0,05 e −0,26.
- **Gráfico:** `sessoes/B3/teste2_excedente_x_rendimento.svg`. As quebras de 2008, 2015 e 2023 ficam isoladas à direita (excedente > 360 mm); o resto da nuvem não tem tendência.

## 3. Validação
- **Contra a linha de base:** 3 acertos contra 0,7 esperados ao acaso (86% de alarmes falsos); "não fazer nada" acerta 0. A chance de acertar 3 ou mais de 5 com 8 alertas ao acaso é de 6% [CÁLCULO, hipergeométrica]: no limite da significância.
- **Fonte externa:**
  - Epagri, estudo de set–out de 2015 (El Niño): a cebola foi das culturas mais atingidas, com redução de cerca de 55% da produção de SC. **Bate** com 2015. [Epagri, RAC](https://publicacoes.epagri.sc.gov.br/rac/article/download/10/37/407)
  - Epagri/Cepa, mar/2024: safra 2023/24 de cebola em SC com produtividade de 21,3 t/ha, contra 29,9 t/ha estimados (quebra de 27,5%), por chuva excessiva em out–nov. A umidade também afetou o pós-colheita. **Bate** com 2023 (PAM Ituporanga 21,4 t/ha). [Notícias Agrícolas](https://www.noticiasagricolas.com.br/noticia/371814)
  - Epagri/Cepa: na safra 2020/21, SC perdeu 100 mil t de cebola por estiagem e granizo. O excesso de água não explica esse tipo de perda. [Notícias Agrícolas](https://www.noticiasagricolas.com.br/noticia/282388)
  - O IBGE PAM de Ituporanga tem valores redondos e repetidos (12 t/ha de 1992 a 1995), o que é sinal de estimativa e deixa o rendimento relativo com ruído.
- **O critério de sucesso foi atingido?** **Não.** 3/5 (precisava ≥ 2/3), 62% de alarmes falsos (precisava ≤ 40%) e ρ = −0,18 (precisava ≤ −0,4). **Em parte** nos extremos.

## 4. Régua (1 a 5)
| Critério | Nota | Por quê (uma frase) |
|---|---|---|
| Problema real | 5 | A Epagri registra quebras de 55% (2015) e 27,5% (2023) da cebola de SC por excesso de chuva. |
| Tamanho do impacto | 4 | O Alto Vale (Rio do Sul e Ituporanga) tem mais da metade da área de cebola de SC (Epagri/Cepa) e é quase tudo agricultura familiar [INFERÊNCIA]. |
| Resolve de fato | 2 | Com 62% de alarmes falsos e cego para a perda por seca (2017), o alerta não mudaria bem a decisão na maioria dos anos. |
| Validade | 2 | Fica no limite contra o acaso (p = 0,06), com ρ = −0,18 e critério não atingido; só os extremos batem com a Epagri. |
| Muda a decisão | 3 | Pulverização, colheita e cura são decisões concretas, mas o teste não mediu o ganho de mudar o calendário. |
| Simples e factível | 4 | Só o POWER e o balde já feito. |
| Alinhamento com o desafio | 3 | Liga ao "excesso de chuva" do controle, e ao talhão da cebola só de forma indireta. |
| Diferencial | 3 | Não conferi se a Epagri já tem um aviso de míldio para a cebola; o ZARC não acompanha a safra. |
| Cabe no hackathon | 5 | Já está rodando. |
| **Total (máx. 45)** | **31** | |

Aprovada só com 3+ em problema real, resolve de fato e validade.

## 5. Veredito
**Ajustar.** O excesso de chuva explica os anos extremos (2008, 2015, 2023), não o ano a ano. A perda da cebola tem dois lados: excesso e seca (2017, 2020/21). A versão "só extremos" foi testada fora da amostra em B3-3.

**Hipótese para depois, não testada:** um índice com os dois lados (excesso OU seca).

## 6. Relação com o controle
**Complementa.** O controle já lista o "excesso de chuva" entre os riscos. Este é o primeiro número dele para o Sul, mas serve como alerta de ano extremo, não como probabilidade fina.

## 7. Limites e o que não foi testado
- A célula do POWER (~50 km) é grossa para a chuva de encosta do Alto Vale. IMERG (10 km) não foi testado (login Earthdata).
- "Dias de molhamento" usa a umidade relativa média diária, não horas de folha molhada. Não é um modelo de míldio validado.
- Não testei o ganho real de antecipar a pulverização (não há dado de aplicação nem de incidência de doença).
- Uma data de transplante fixa (1/ago); as cultivares superprecoces e as tardias têm janelas diferentes.
- O PAM é estimativa municipal, com valores repetidos.

## 8. Fontes
- NASA POWER diário: `loop-validacao/dados/power_ituporanga.json` [DADO].
- IBGE SIDRA, tabela 1612, cebola (c81 = 2697), microrregião 42014 e município 4208500: `sessoes/B3/externo/cebola_micro_ituporanga.json`, `cebola_ituporanga.json`. https://apisidra.ibge.gov.br/values/t/1612/n9/42014/v/112,216/p/all/c81/2697 [DADO].
- IBGE, API de localidades (código de Ituporanga): https://servicodados.ibge.gov.br/api/v1/localidades/municipios/4208500
- Epagri, set–out de 2015: https://publicacoes.epagri.sc.gov.br/rac/article/download/10/37/407
- Epagri/Cepa, safra 2023/24: https://www.noticiasagricolas.com.br/noticia/371814 e https://revistacultivar.com.br/noticias/epagri-aponta-queda-na-producao-de-alho-e-de-cebola-em-santa-catarina
- Epagri/Cepa, safra 2020/21: https://www.noticiasagricolas.com.br/noticia/282388
