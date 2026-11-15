# A3-3 · Palhada ou solo exposto? (NDTI do Sentinel-2 no lugar do NDVI)

Sessão: A3 · Trilha: A · Região: Ituporanga · Tentativa 3 de 4 · Data: 2026-11-14

## 1. Ideia (escrita antes do teste)
- **Hipótese:** o NDVI baixo não diz se o solo está nu ou coberto de palha seca. O índice de palhada NDTI = (B11 − B12)/(B11 + B12), do Sentinel-2, separa as duas coisas. Com isso, a contagem de "dias de solo exposto de verdade" separa talhões em plantio direto na palha de talhões em preparo convencional, que é o que o A3-1 e o A3-2 precisavam e não tinham.
- **Problema que ataca (e para quem):** o mesmo do A3-1 e do A3-2: saber quais talhões de cebola e grãos em Ituporanga ficam de solo nu e quando. Também serve de "prova" de adoção do plantio direto na palha (SPDH), que a Epagri promove.
- **Decisão que muda:** o agricultor e o extensionista veem quais talhões ainda ficam de solo nu no preparo (maio a agosto) e priorizam cobertura, palhada ou plantio direto ali.
- **Regra fixada antes:** numa observação limpa com NDVI < 0,30: **solo exposto** se NDTI < 0,09; **palhada** se NDTI ≥ 0,09. Interpolação diária igual à do A3-1.
- **Critério de sucesso (definido antes):**
  - **T1, o índice separa:** nas observações de lavoura com NDVI < 0,30 entre maio e agosto, cada classe (palhada e solo exposto) fica com 20% a 80% (não degenera numa classe só).
  - **T2, conferência externa:** a fração de talhões de lavoura "tipo plantio direto" (≤ 30 dias de solo exposto por ano, média de 2019 a 2024) fica entre 6% e 40%. É a faixa de ±15 pontos percentuais em torno de 21% a 25%: área com plantio direto na palha (3.246 ha) sobre a área plantada (15.567 ha) e estabelecimentos com plantio direto (380 de 1.514), Censo 2017 e PAM 2017, Ituporanga, código 4208500.
  - **T3, supera a linha de base:** essa fração fica mais perto do Censo do que a fração só com NDVI (70%, no A3-2).
  - **T4, estabilidade:** ICC dos dias de solo exposto por talhão entre anos ≥ 0,5.
  - **Aprovada** se T1, T2, T3 e T4 passarem; **ajustar** se T1 e T3 passarem.
- **Linha de base:** a mesma conta só com NDVI (A3-2: 70% dos talhões com ≤ 60 dias descobertos).

## 2. Teste
- **Dados oficiais usados:** Sentinel-2 L2A B04, B08, SCL (10 m) e B11, B12 (20 m, reamostradas para 10 m), 259 datas de 2019 a 2024, mesmo recorte de 5 × 5 km em Ituporanga.
- **Método:**
  - Mesma máscara e mesmo filtro de picos do NDVI.
  - Em cada observação limpa: NDVI < 0,30 e NDTI < 0,09 = solo nu; NDVI < 0,30 e NDTI ≥ 0,09 = palhada.
  - Dia a dia, vale a classe da observação limpa mais próxima. A unidade é o talhão de 50 m.
  - Scripts: `sessoes/A3/s2_baixar_swir.py`, `sessoes/A3/a3_3_ndti.py` (o limiar entra como argumento).
- **Resultado** (`sessoes/A3/a3_3_resultado_0.09.json`):
  - NDTI nas observações de lavoura com NDVI baixo: p10, p50 e p90 = 0,045; 0,147; 0,223. Lavoura verde: mediana de 0,34. Urbano: mediana de 0,09 [CÁLCULO].
  - O histograma tem **um só pico** (0,12 a 0,18); não aparecem duas populações (solo nu e palha) [CÁLCULO].
  - Dias de solo nu por ano: p10, p50 e p90 = 4, 12 e 22.
  - Média da lavoura por ano: 25 (2019), 3, 4, 8, 14 e 27 (2024). O ano pesa mais que o talhão [CÁLCULO].
  - Perfil mensal de solo nu: quase zero de setembro a abril, 0,12 em junho e **0,19 em julho** [CÁLCULO].
- **Gráfico:** `sessoes/A3/a3_2_a3_3_dias_descobertos.png` (laranja). Quase todos os talhões ficam com menos de 30 dias de solo nu.

## 3. Validação
- **T1, o índice separa:** de maio a agosto, 55% das observações de NDVI baixo saem como palhada [CÁLCULO]. **Passa** (fica entre 20% e 80%), mas a distribuição não tem dois picos, então o corte é arbitrário.
- **T2, conferência com o Censo 2017:** **97%** dos talhões ficam com ≤ 30 dias de solo nu, contra a faixa de 6% a 40% (Censo: 21–25% em plantio direto) [CÁLCULO; DADO]. **Não passa.**
- **T3, contra a linha de base:** 97% fica mais longe do Censo que os 70% do NDVI. **Não passa.**
- **T4, estabilidade:** ICC = **0,07** [CÁLCULO]. **Não passa.**
- **Sensibilidade ao limiar** (feita depois e não vale para o veredito):

  | Limiar de NDTI | Talhões ≤ 30 dias de solo nu | ICC |
  |---|---|---|
  | 0,12 | 89% | 0,18 |
  | 0,15 | 69% | 0,32 |

  Nenhum limiar chega perto do Censo, e ajustar o limiar para bater com o Censo seria circular.
- **Subproduto útil:** confirma de forma independente que o solo nu de verdade da lavoura se concentra em junho e julho. Esse é o achado de tempo do A3-1, que continua de pé com o NDTI (C3: 99% e 90%).
- **O critério de sucesso foi atingido?** **Não.** Passou T1; falharam T2, T3 e T4.

## 4. Régua (1 a 5)
| Critério | Nota | Por quê (uma frase) |
|---|---|---|
| Problema real | 3 | Saber se o talhão está com palha ou com solo nu é o ponto que trava o A3-1 e o A3-2. |
| Tamanho do impacto | 2 | É uma peça técnica, não um produto para o agricultor. |
| Resolve de fato | 1 | Não separa plantio direto de convencional nem fica estável entre anos. |
| Validade | 1 | Falha na conferência com o Censo e na estabilidade (ICC 0,07). |
| Muda a decisão | 2 | Sem separar talhões de forma confiável, não muda a decisão de ninguém. |
| Simples e factível | 2 | Exige SWIR, máscara e limiar sensível à umidade do solo, sem dado de campo para calibrar. |
| Alinhamento com o desafio | 3 | Usa Sentinel-2 da aba para medir manejo e cobertura, que são parte da rotação. |
| Diferencial | 3 | Índice de palhada por satélite é pouco usado em hortaliças no Brasil. |
| Cabe no hackathon | 3 | O código roda, mas calibrar o limiar sem campo não cabe. |
| **Total (máx. 45)** | **20** | |

Aprovada só com 3+ em problema real, resolve de fato e validade: **não atende.**

## 5. Veredito
**Descartada.** O NDTI do Sentinel-2 não mostra duas populações (palhada e solo nu) nos solos de Ituporanga, o resultado depende mais do ano que do talhão e nenhum limiar razoável chega à adoção de plantio direto do Censo. Serviu só para confirmar o calendário de exposição do A3-1.

## 6. Relação com o controle
Não entra na demo. Fica como limite declarado: "o satélite vê quando o solo está descoberto, mas ainda não diferencia palha de solo nu".

## 7. Limites e o que não foi testado
- O NDTI cai com o solo úmido (o inverno de Santa Catarina é úmido), o que pode explicar a variação entre anos.
- Não tive pontos de campo com palhada conhecida para calibrar. Não testei índices com mais bandas (por exemplo, o NBR2 ou a razão SWIR com textura) nem o Landsat.
- O B11 e o B12 têm 20 m; em talhões pequenos, a borda mistura classes.

## 8. Fontes
- Van Deventer et al. (1997), *Photogrammetric Engineering & Remote Sensing* 63(1), que define o NDTI (citado de memória como referência de método).
- IBGE, Censo Agropecuário 2017, tabela 6855, e PAM 2017, tabela 5457, Ituporanga 4208500 (`sessoes/A3/conferencia/`).
- Dados: Sentinel-2 L2A COG, Earth Search (AWS).
