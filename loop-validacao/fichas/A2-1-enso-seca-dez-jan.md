# A2-1 · El Niño e La Niña ajudam a prever a seca de dez–jan no Extremo Oeste?

Sessão: A2 · Trilha: A · Região: São Miguel do Oeste (Ituporanga como checagem) · Tentativa 1 de 4 · Data: 2026-11-14

## 1. Ideia (escrita antes do teste)
Critérios gravados antes de rodar dados em `sessoes/A2/CRITERIOS_ANTES_DO_TESTE.md`.
- **Hipótese:** em anos de La Niña o risco de dezembro–janeiro seco em São Miguel do Oeste (SMO) é bem maior que a média, e em anos de El Niño é bem menor.
- **Problema que ataca (e para quem):** o produtor de leite e milho do Extremo Oeste decide o plantio do milho (silagem e grão) sem saber se o verão vai ser seco; as quebras de 2005, 2012 e 2022 vieram de verões secos.
- **Decisão que muda:** em ano de La Niña, plantar mais cedo, reservar silagem, contratar seguro ou reduzir a área de milho.
- **Critério de sucesso (definido antes):** todos: (1) P(seco | La Niña) ≥ 0,50 e P(seco | El Niño) ≤ 0,20 (base 0,33); (2) Fisher unicaudal p < 0,10; (3) BSS com validação cruzada (LOO) > 0,05 contra a climatologia, usando o ONI de JAS (sabido antes do plantio); (4) mesmo sinal nas duas metades do período.
- **Linha de base:** média de todos os anos (climatologia, 1 em 3 por construção do tercil).

## 2. Teste
- **Dados oficiais usados:** NASA POWER diário (comunidade AG, grade de ~50 km), ponto -26,725; -53,518: `PRECTOTCORR`, e `T2M`, `T2M_MAX`, `T2M_MIN`, `RH2M`, `WS2M` e `ALLSKY_SFC_SW_DWN` para a ET0; `GWETROOT`. Safras dez/1984–jan/1985 a dez/2024–jan/2025 (41) para o balanço; 44 safras (desde 1981/82) só para a chuva.
- **Fonte externa só para separar os anos:** ONI da NOAA/CPC. NDJ com a regra da NOAA (5 trimestres seguidos ≥ 0,5) e JAS/ASO com ±0,5 no trimestre.
- **Método:** ET0 Penman-Monteith FAO-56 (função de `prototipo/modelo/risco.py`); alvo = soma de (chuva − ET0) de 1/dez a 31/jan no tercil inferior. Checagens: chuva dez–jan, GWETROOT dez–jan e milho simulado (balanço hídrico de `risco.py`, solo argiloso, plantio em 1/out, perda = rendimento relativo < 0,6). Brier com validação cruzada (LOO), sempre recalculando o tercil sem o ano previsto. Scripts: `sessoes/A2/base.py` e `sessoes/A2/a2_1_enso.py`. Saída: `sessoes/A2/resultados/a2_1_smo.json` e `a2_1_itu.json`.
- **Resultado (SMO, balanço P−ET0 dez–jan)** [CÁLCULO]:

| Fase | ONI de NDJ (na própria safra) | ONI de JAS (sabido antes do plantio) |
|---|---|---|
| La Niña | 7 de 15 = 47% | 3 de 8 = 38% |
| Neutro | 4 de 12 = 33% | 10 de 25 = 40% |
| El Niño | 3 de 14 = 21% | 1 de 8 = 12% |
| Todos os anos | 34% | 34% |
| Fisher (La Niña > El Niño) | p = 0,15 | p = 0,29 |
| BSS (LOO) contra a climatologia | −0,05 | −0,04 |

  - Metades (NDJ): La Niña seca em 1 de 6 em 1984–2004 e em 6 de 9 em 2005–2024. O sinal da La Niña só existe na segunda metade.
  - Milho simulado: perda em 3 de 15 La Niñas (20%), 0 de 14 El Niños e 4 de 41 no total (10%) (NDJ); com JAS, 1 de 8 contra 0 de 8.
  - Ituporanga (checagem): o oposto. La Niña com **menos** dez–jan seco (3 de 15 = 20%; com JAS, 0 de 8) que os neutros (50%).
- **Gráfico:** `sessoes/A2/a2_1_fases_enso.svg`. Ele mostra que só com o ONI da própria safra a La Niña fica acima da média (47%), e que com o ONI sabido antes do plantio La Niña e neutro ficam iguais. Só o El Niño fica abaixo.

## 3. Validação
- **Contra a linha de base:** a previsão por fase erra **mais** que a média de todos os anos (Brier LOO pior em 4% a 5%). Com JAS: 38% em La Niña contra 34% na média.
- **Fonte externa:**
  - IBGE PAM, tabela 1612, rendimento de milho da microrregião de SMO (42001), anomalia sobre a mediana móvel de 7 anos, quebra < 0,8 [DADO + CÁLCULO]. Com NDJ, quebras em 3 de 13 La Niñas (colheitas 2012, 2021 e 2022), 1 de 12 El Niños (2005) e 2 de 9 neutros. Rendimento médio de 0,95 em La Niña, 1,03 em El Niño e 0,94 em neutro. Com JAS: 1 de 7, 1 de 7 e 4 de 20. A direção bate com NDJ, mas a diferença é pequena e some com o ONI sabido antes do plantio. [Link](https://apisidra.ibge.gov.br/values/t/1612/n9/42001/v/112/p/all/c81/2711).
  - Literatura (Grimm et al., 1998 e 2000) [INFERÊNCIA, citado de memória, conferir]: o sinal do ENSO no Sul do Brasil é mais forte na primavera (out–nov) e no El Niño, e mais fraco e variável em dez–jan. Isso **bate** com o resultado fraco aqui.
- **O critério de sucesso foi atingido?** **Não.** Falha nos 4 itens: 0,47 < 0,50; p = 0,15; BSS < 0; sinal instável entre as metades.

## 4. Régua (1 a 5)
| Critério | Nota | Por quê (uma frase) |
|---|---|---|
| Problema real | 4 | Os verões secos de 2004/05, 2011/12 e 2021/22 aparecem como quebra de milho no IBGE da microrregião. |
| Tamanho do impacto | 2 | No melhor caso a chance passa de 34% para 47%, e com informação disponível a tempo não muda. |
| Resolve de fato | 2 | Com o ONI de agosto, La Niña e neutro têm a mesma chance de seca (38% e 40%), então o conselho não muda. |
| Validade | 2 | Não supera a climatologia (BSS −0,04 a −0,05), o sinal inverte entre as metades e Ituporanga dá o oposto. |
| Muda a decisão | 1 | O milho simulado com JAS dá 1 de 8 contra 0 de 8; nada que justifique mudar o plantio. |
| Simples e factível | 3 | O cálculo é simples, mas o ONI é fonte externa; para entrar na solução, teria de ser calculado com a TSM do ERA5. |
| Alinhamento com o desafio | 3 | É previsibilidade climática para escolher estratégia, mas depende de um índice de fora da aba Resources. |
| Diferencial | 2 | A Epagri/Ciram e a imprensa agrícola já falam de La Niña e seca; não acrescenta nada. |
| Cabe no hackathon | 4 | Rodou em poucas horas com os dados já baixados. |
| **Total (máx. 45)** | **23** | |

## 5. Veredito
**Descartada.** A La Niña não prevê dez–jan seco em SMO de forma útil. O único padrão estável é assimétrico: o **El Niño** tem poucos verões secos. Isso foi testado de novo, com critério novo e dados novos, em A2-3 e A2-4.

## 6. Relação com o controle
Não compete com o controle. Mostra que, para dez–jan, a probabilidade histórica (climatologia) do controle não fica pior que uma "previsão por La Niña". Isso dá ao pitch o argumento de que não prometemos previsão onde ela não existe.

## 7. Limites e o que não foi testado
- Amostra pequena: 8 a 16 anos por fase. Fisher e BSS têm pouco poder estatístico.
- POWER com grade de ~50 km. A chuva do POWER (MERRA-2 corrigida) não é pluviômetro.
- ONI é fonte externa (NOAA), usado só para separar os anos. Não testei um índice calculado com dado do Resources (TSM do ERA5).
- Com o limiar de ±0,5 em JAS, safras de La Niña que se formaram tarde (2020, ONI −0,43; 2021, −0,46) contam como neutras. Isso dilui a La Niña em JAS (efeito pequeno, mas existe).
- O milho simulado é grosseiro (solo argiloso cheio em 1/ago, Kc/Ky FAO). Ele não vê excesso de chuva, doença nem geada.

## 8. Fontes
- NASA POWER, API diária, comunidade AG: `loop-validacao/dados/power_sao_miguel_do_oeste.json` e `power_ituporanga.json` [DADO].
- NOAA CPC, ONI v5: https://www.cpc.ncep.noaa.gov/data/indices/oni.ascii.txt (baixado em 14/11/2026, `sessoes/A2/externo/oni.ascii.txt`) [DADO externo, só para separar os anos].
- IBGE SIDRA, PAM, tabela 1612, milho em grão, rendimento médio, microrregião 42001: https://apisidra.ibge.gov.br/values/t/1612/n9/42001/v/112/p/all/c81/2711 [DADO externo, conferência].
- Grimm, A. M.; Ferraz, S. E. T.; Gomes, J. (1998). Precipitation anomalies in Southern Brazil associated with El Niño and La Niña events. *J. Climate* 11, 2863–2880. Grimm, A. M.; Barros, V. R.; Doyle, M. E. (2000). Climate variability in southern South America associated with El Niño and La Niña events. *J. Climate* 13, 35–58 [citados de memória, conferir].
