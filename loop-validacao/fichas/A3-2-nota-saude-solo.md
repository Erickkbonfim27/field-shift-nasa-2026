# A3-2 · Nota de saúde do solo do talhão

Sessão: A3 · Trilha: A · Região: Ituporanga · Tentativa 2 de 4 · Data: 2026-11-14

## 1. Ideia (escrita antes do teste)
- **Hipótese:** uma nota de 0 a 100 por talhão e por ano, feita de dias de solo descoberto (série de NDVI do Sentinel-2, peso 60%), declive (SRTM, 25%) e umidade do solo (GWETTOP do NASA POWER, 15%), separa de forma coerente talhões bem manejados (plantio direto com palhada) de mal manejados (preparo convencional).
- **Problema que ataca (e para quem):** o agricultor e o extensionista não têm um número simples para acompanhar se o manejo melhora ou degrada o solo de cada talhão.
- **Decisão que muda:** que talhão priorizar para cobertura ou plantio direto e se a mudança de manejo está aparecendo ano a ano.
- **Critério de sucesso (definido antes):**
  - **S1, estabilidade:** a nota de um mesmo pixel de lavoura é estável entre anos. A parte da variância explicada pela diferença entre pixels (ICC) é ≥ 0,5 em 2019–2024.
  - **S2, sanidade de uso:** mediana da nota na mata > lavoura anual, com diferença ≥ 20 pontos (teste de sanidade, parcialmente circular).
  - **S3, conferência externa:** a fração de pixels de lavoura anual com padrão "tipo plantio direto" (≤ 60 dias descobertos por ano) fica a ±15 pontos percentuais da parcela de plantio direto em Ituporanga no Censo Agropecuário 2017 (IBGE).
  - **S4, além da linha de base:** a ordem dos talhões pela nota completa difere da ordem só por declive (Spearman < 0,7). Se não diferir, o satélite não acrescenta nada.
  - **Aprovada** se S1, S3 e S4 passarem e S2 não falhar.
- **Linha de base:** "não fazer nada" (todo talhão recebe a média do município) e a nota só com declive (SRTM), que não muda com o manejo.

## 2. Teste
- **Dados oficiais usados:**
  - Sentinel-2 L2A (B04, B08, SCL), 2019–2024, 10 m, recorte de 5 × 5 km em Ituporanga (o mesmo do A3-1).
  - SRTM 1″.
  - NASA POWER `GWETTOP` diário de 2019 a 2024 (umidade relativa da camada superficial, MERRA-2, ~50 km).
- **Método:**
  - `nota = 100 − [60·min(dias_descobertos/180, 1) + 25·min(declive/45, 1) + 15·(1 − umidade_normalizada)]`, por talhão (bloco de 50 m) e por ano.
  - Dias descobertos = dias com NDVI interpolado < 0,30.
  - Script: `sessoes/A3/a3_2_nota.py`; série de NDVI de `sessoes/A3/ndvi_processar.py`.
- **Resultado** (`sessoes/A3/a3_2_resultado.json`):
  - Dias descobertos por ano na lavoura: p10, p50 e p90 = 12, 35 e 101 [CÁLCULO].
  - Nota média da lavoura por ano: 68,7 (2019), 60,9 (2020), 69,2, 72,6, 71,1 e 66,9 (2024) [CÁLCULO].
  - A queda de 2020 vem da umidade: o GWETTOP de 2020 foi o mais baixo da série (0,565, contra 0,68 a 0,77 nos outros anos) [DADO], e esse termo pesa igual para todos os talhões.
- **Gráfico:** `sessoes/A3/a3_2_a3_3_dias_descobertos.png`. A distribuição dos dias descobertos por talhão tem um só pico perto de 20 a 40 dias; não aparecem dois grupos (direto contra convencional).

## 3. Validação
- **S1, estabilidade:** ICC da nota = **0,39** (< 0,5); só os dias descobertos dão 0,47. A correlação de um ano para o seguinte vai de 0,51 a 0,70 [CÁLCULO]. **Não passa.**
- **S2, sanidade:** mediana da mata = 79,2 e da lavoura = 70,6, diferença de **8,6 pontos** (< 20) [CÁLCULO]. **Não passa.** O declive pesa demais (a mata fica nas encostas mais íngremes) e a lavoura passa pouco tempo com NDVI < 0,30.
- **S3, conferência externa:** **70%** dos talhões de lavoura ficam com ≤ 60 dias descobertos ("tipo plantio direto") [CÁLCULO]. No Censo Agropecuário 2017 (IBGE, tabela 6855, Ituporanga, 4208500):
  - 380 de 1.514 estabelecimentos que preparam o solo declaram plantio direto na palha (25%), 855 cultivo convencional e 736 cultivo mínimo (um estabelecimento pode ter mais de um) [DADO];
  - a área com plantio direto é de 3.246 ha, sobre 15.567 ha plantados na PAM 2017 (21%) [DADO; CÁLCULO].
  - A faixa aceita era de 6% a 40%. **Não passa.**
- **S4, além da linha de base:** Spearman entre a nota completa e a nota só de declive = **0,18** (< 0,7) [CÁLCULO]. **Passa**: o satélite muda a ordem dos talhões. Isso só mostra que a ordem é diferente, não que está certa (S1 e S3 falharam).
- **Termo de umidade:** o GWETTOP do POWER é um número só para a grade de ~50 km. Ele não separa talhões e faz a nota cair num ano seco (2020) sem que o solo tenha piorado. O termo é incoerente com "saúde do solo" e deveria sair. O SMAP (9 km) não resolveria a escala do talhão, e o acesso dele pede login (não testei).
- **O critério de sucesso foi atingido?** **Não.** Passou S4; falharam S1, S2 e S3.

## 4. Régua (1 a 5)
| Critério | Nota | Por quê (uma frase) |
|---|---|---|
| Problema real | 3 | Acompanhar se o manejo melhora o solo é uma necessidade real da extensão em Ituporanga, mas o agricultor não pediu uma nota. |
| Tamanho do impacto | 2 | Mesmo funcionando, uma nota não muda o manejo sozinha; o efeito seria indireto. |
| Resolve de fato | 2 | A nota não separa mata de lavoura com folga nem bate com a adoção de plantio direto do Censo. |
| Validade | 1 | Falha na conferência externa (70% contra 21–25%) e na estabilidade (ICC 0,39). |
| Muda a decisão | 2 | Com essa instabilidade, um talhão muda de faixa de um ano para outro sem mudar de manejo. |
| Simples e factível | 3 | Os dados existem e o cálculo é simples, mas o NDVI não vê palhada. |
| Alinhamento com o desafio | 4 | Saúde do solo e efeito da rotação ao longo dos anos estão no centro do desafio. |
| Diferencial | 2 | Notas de saúde do solo por satélite já existem em plataformas comerciais, com o mesmo problema da palhada. |
| Cabe no hackathon | 4 | Sai do mesmo fluxo do A3-1. |
| **Total (máx. 45)** | **23** | |

Aprovada só com 3+ em problema real, resolve de fato e validade: **não atende** (resolve de fato 2, validade 1).

## 5. Veredito
**Descartada.** Com NDVI, declive e a umidade do POWER, a nota não fica estável entre anos, mal separa mata de lavoura e diz que 70% dos talhões são "tipo plantio direto", quando o Censo dá 21–25%. Testei uma variação com índice de palhada no A3-3, e ela também falhou.

## 6. Relação com o controle
Competiria pelo mesmo espaço na tela do "efeito no 2º ano" da rotação, sem evidência. Não entra na demo. O que sobra de útil (dias descobertos por talhão) já está dentro do A3-1.

## 7. Limites e o que não foi testado
- O NDVI < 0,30 conta palhada seca como solo descoberto, e cebola recém-transplantada também.
- O "talhão" é um bloco de 50 m. Não tive talhões reais com manejo conhecido (por exemplo, as áreas experimentais da Estação Experimental de Ituporanga) para uma conferência direta.
- O Censo conta estabelecimentos e área declarada, não pixels. A comparação é de ordem de grandeza, e o "plantio direto" declarado na cebola pode não ser o sistema completo.
- Os pesos (60/25/15) e os limites (180 dias, 45%) foram escolhidos por mim, sem calibração.
- Não testei SMAP (login), nem carbono do solo (nenhum recurso da aba mede isso no talhão), nem São Miguel do Oeste.

## 8. Fontes
- IBGE, Censo Agropecuário 2017, tabela 6855 (sistema de preparo do solo), Ituporanga 4208500: `sessoes/A3/conferencia/ibge_6855_ituporanga_4208500.json` (API servicodados.ibge.gov.br/api/v3/agregados/6855).
- IBGE, PAM 2017, tabela 5457 (área plantada): `sessoes/A3/conferencia/pam_5457_ituporanga_4208500.json`.
- Back et al. (2023), *Agropecuária Catarinense* 36(3), sobre a promoção do SPDH em Ituporanga. https://doi.org/10.52945/rac.v36i3.1766
- **Aviso:** o código IBGE 4208401 do PROTOCOLO é de Itapiranga; o de Ituporanga é 4208500 (conferido na API de localidades do IBGE).
