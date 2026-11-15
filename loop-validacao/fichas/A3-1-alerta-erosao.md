# A3-1 · Alerta mensal de erosão (chuva × declive × solo descoberto)

Sessão: A3 · Trilha: A · Região: Ituporanga · Tentativa 1 de 4 · Data: 2026-11-14

## 1. Ideia (escrita antes do teste)
- **Hipótese:** cruzar a erosividade da chuva mês a mês (NASA POWER), o declive do talhão (SRTM) e os meses em que o solo fica descoberto (NDVI do Sentinel-2) mostra quando e onde cada talhão está mais exposto à erosão, melhor que o calendário de chuva sozinho.
- **Problema que ataca (e para quem):** perda de solo na cebola em encosta no Alto Vale do Itajaí, com preparo convencional (aração, gradagem, enxada rotativa) e solo descoberto. Serve ao agricultor familiar de Ituporanga e ao extensionista.
- **Decisão que muda:** em que mês semear a cobertura (aveia, centeio, nabo) ou deixar a palhada, quais talhões passar primeiro para plantio direto ou terraço, e quando evitar revolver o solo.
- **Critério de sucesso (definido antes):**
  - **C1, validade da chuva:** a erosividade mensal estimada só com o POWER diário tem Spearman ≥ 0,7 com a tabela mensal de Back et al. (2023) para Ituporanga e acerta ≥ 3 dos 4 meses mais erosivos dessa tabela (jan, out, set, fev).
  - **C2, viabilidade do satélite:** o Sentinel-2 dá ≥ 1 observação limpa por mês no recorte em ≥ 75% dos meses de 2019 a 2024.
  - **C3, informação além da linha de base:** em ≥ 50% dos talhões-ano de lavoura anual, o mês de maior exposição (erosividade × solo descoberto) é diferente do mês de pico da linha de base.
  - **C4, separa talhões:** entre os pixels de lavoura, a exposição anual tem razão p90/p10 ≥ 3. Sanidade: a mediana da lavoura anual é ≥ 3 vezes a da mata.
  - **Aprovada** se C1, C2, C3 e C4 passarem; **em parte** se C1 e C2 passarem e só um entre C3 e C4.
- **Linha de base:** o calendário só de chuva, igual para todo talhão e todo ano ("outubro a fevereiro é crítico", que é a recomendação atual da Epagri a partir da erosividade). Ele não separa talhões nem anos.

## 2. Teste
- **Dados oficiais usados:**
  - NASA POWER `PRECTOTCORR` diário de 1981 a 2025 (grade de ~50 km), arquivo `dados/power_ituporanga.json`.
  - Sentinel-2 L2A (B04, B08, SCL; B11 e B12 só na checagem de robustez), 259 datas de 2019 a 2024, 10 m, recorte de 5 × 5 km centrado em -27,414; -49,601, via STAC Earth Search.
  - SRTM 1″ (~30 m), tile S28W050.
- **Método:**
  1. Erosividade mensal R: comparei dois métodos com o pluviômetro (C1). O índice de Fournier por mês e ano (p_mês² / P_ano) ganhou do método diário (EI = 0,41·P^1,81 em dias com ≥ 12,7 mm). Script: `sessoes/A3/erosividade_power.py`.
  2. Solo descoberto: NDVI por pixel com máscara SCL (classes 4 e 5), sem cenas com menos de 30% limpas e com filtro de picos de nuvem residual. Interpolei dia a dia e calculei a fração de dias do mês com NDVI < 0,30. Script: `sessoes/A3/ndvi_processar.py`.
  3. Declive em % (SRTM) e fator S de McCool (USLE), com L fixo. Script: `sessoes/A3/declive_srtm.py`.
  4. Exposição E = R × descoberto × S, por mês e por talhão. O talhão é um bloco de 50 × 50 m com ≥ 60% de pixels de lavoura anual. Uso do solo pela série de NDVI: lavoura anual = p95 ≥ 0,65 e p05 < 0,30. Script: `sessoes/A3/a3_1_alerta.py`. Gráficos: `sessoes/A3/graficos.py`.
- **Resultado** (`sessoes/A3/a3_1_resultado.json`):
  - O recorte tem 2.302 talhões de lavoura e 1.540 blocos de mata [CÁLCULO].
  - Fração descoberta média da lavoura por mês, de jan a dez: 0,06 0,08 0,07 0,10 0,13 0,21 **0,29** 0,20 0,15 0,09 0,10 0,08. O pico é em junho e julho, no preparo e transplante da cebola [CÁLCULO].
  - Mês de maior exposição por talhão e ano: varia com o ano. Na média dos talhões, o pico foi em julho em 2019 e 2024, junho em 2021, outubro em 2023, novembro em 2022 e dezembro em 2020 [CÁLCULO].
  - Julho de 2024 domina a média: R = 15,5 contra 0,5 a 8,6 nos outros julhos [CÁLCULO].
  - A exposição anual varia muito entre talhões. Na lavoura, p10, p50 e p90 = 6,8; 20,4; 60,8 (p90/p10 = 9). A mediana da lavoura é 20 vezes a da mata [CÁLCULO].
- **Gráficos:**
  - `sessoes/A3/a3_1_calendario.png`: a chuva é mais erosiva de outubro a fevereiro, mas o solo da lavoura fica descoberto em junho e julho. A exposição junta os dois e tem picos em julho e em outubro a novembro.
  - `sessoes/A3/a3_1_mapa.png`: mapa de uso, declive e exposição anual. A exposição se concentra em poucas manchas de lavoura em encosta.

## 3. Validação
- **C1, erosividade (fonte externa):** o pluviômetro da ANA em Ituporanga (02749002, 1941–2021, Back et al. 2023, Tab. 3) dá EI30 anual de 7.549 MJ mm ha⁻¹ h⁻¹ ano⁻¹, e 61% das chuvas erosivas caem de outubro a fevereiro [DADO].
  - **Índice de Fournier com o POWER:** Spearman 0,85 com a distribuição mensal de Back; acerta 3 dos 4 meses mais erosivos (jan, fev, out; erra set e põe dez) [CÁLCULO]. Passa.
  - **Método diário com o POWER:** Spearman 0,64 (abaixo de 0,7) e acerta 3 de 4 [CÁLCULO]. Não passa. Motivo provável: a grade de 50 km suaviza a chuva intensa (p99 diário de 35 mm; máximo de 106 mm em 45 anos) [DADO].
  - A chuva mensal do POWER bate com o pluviômetro (Spearman 0,86), mas o POWER dá 1.621 mm/ano contra 1.523 mm de Back [DADO]. **C1 em parte:** a forma passa; o método por intensidade, que era o mais natural, não passa.
- **C2, viabilidade do satélite:** 85% dos meses têm ao menos uma cena com ≥ 50% do recorte limpo; 77% dos pares pixel-mês de lavoura têm ao menos uma observação limpa; só 6% ficam a mais de 30 dias de uma observação [CÁLCULO]. Faltam 11 meses, a maioria de inverno (por exemplo 2021-06, 2023-07). **Passa.** Atenção: de 2022 a 2024 o Earth Search tem cerca de 40 cenas por ano, contra 70 a 105 antes.
- **C3, além da linha de base:** a linha de base (Fournier climatológico) põe o pico em janeiro e o top 3 em jan, fev e dez. Em **94%** dos talhões-ano o mês de maior exposição não é janeiro, e em **64%** cai fora de outubro a fevereiro, a época que a Epagri chama de crítica [CÁLCULO]. **Passa.**
  - Robustez: trocando "NDVI < 0,30" por "solo nu pelo NDTI" (A3-3), os números ficam em 99% e 90% (`a3_1_robustez_ndti.json`) [CÁLCULO].
- **C4, separa talhões:** p90/p10 = 9 (≥ 3) e lavoura / mata = 20 (≥ 3) [CÁLCULO]. **Passa.**
- **O que a validação não mostra:** não há dado de erosão observada por talhão e por mês. C3 e C4 mostram que o alerta acrescenta informação de tempo e lugar, não que acerta onde e quando houve perda de solo.
  - O pico de solo descoberto em junho e julho bate com o calendário usual da cebola no Alto Vale (preparo e transplante no inverno) [INFERÊNCIA; não achei a tabela oficial da Epagri com as datas].
  - A literatura confirma o mecanismo: o preparo convencional da cebola no Alto Vale degrada o solo e o plantio direto com resíduo reduz a perda (dissertação UDESC com chuva simulada; Back et al. 2023 citando Pinto dos Santos et al. 2022) [DADO].
- **O critério de sucesso foi atingido?** **Em parte.** C2, C3 e C4 passam. C1 passa só pelo método de Fournier.

## 4. Régua (1 a 5)
| Critério | Nota | Por quê (uma frase) |
|---|---|---|
| Problema real | 4 | Em 90% dos anos a chuva de Ituporanga tem erosividade alta ou muito alta, e o preparo convencional da cebola em encosta já degradou parte do Alto Vale (Back et al. 2023; Epagri). |
| Tamanho do impacto | 3 | São cerca de 4.000 ha de cebola em Ituporanga (PAM 2017–2023), mas a perda de solo é lenta e o ganho aparece em anos, não numa safra. |
| Resolve de fato | 3 | Mostra que talhões e meses ficam expostos em cada ano (64% dos talhões-ano têm pico fora do calendário de chuva), o que muda onde pôr cobertura, mas não mede a perda evitada. |
| Validade | 3 | Supera a linha de base com dado oficial e a parte da chuva bate com o pluviômetro, mas falta conferência externa da exposição por talhão. |
| Muda a decisão | 3 | Aponta quais talhões priorizar e em que mês proteger o solo naquele ano; a forma de proteger (cobertura, palhada, plantio direto) o agricultor já conhece. |
| Simples e factível | 3 | O fluxo roda (POWER + Sentinel-2 + SRTM, cerca de 1 min de processamento para 25 km²), mas exige máscara de nuvem cuidadosa e tem meses sem imagem no inverno. |
| Alinhamento com o desafio | 4 | Usa 3 recursos da aba e trata da sustentabilidade da terra e da cobertura na rotação, que o desafio pede. |
| Diferencial | 3 | Já existem mapas de risco de erosão (RUSLE) da Embrapa e da academia; o diferencial é ser mês a mês, por talhão e com o uso real do ano pelo satélite. |
| Cabe no hackathon | 4 | Os scripts já funcionam num recorte; falta só a tela. |
| **Total (máx. 45)** | **30** | |

Aprovada só com 3+ em problema real, resolve de fato e validade: **atende ao mínimo.**

## 5. Veredito
**Ajustar.** As três notas mínimas são 3 ou mais e o alerta acrescenta informação real de onde e quando. Mas o critério registrado não passou inteiro (C1 em parte), e ninguém conferiu com erosão observada. Antes de virar peça principal, falta:
1. separar palhada de solo nu (o NDTI do A3-3 não resolveu);
2. conferir com algum dado de campo, como fotos de erosão da Epagri ou um evento conhecido, por exemplo julho de 2024.

## 6. Relação com o controle
**Complementa.** O controle fala do risco de perder a safra pelo clima; este alerta fala do risco de perder o solo, que é a "sustentabilidade da terra" da frase do controle. Na demo, ele entra como camada da estratégia D (rotação ou cobertura): um mapa do talhão com "neste inverno seu talhão ficou X dias descoberto, em mês de chuva forte" e o ganho de semear cobertura antes do preparo.

## 7. Limites e o que não foi testado
- Não há verdade de campo de erosão. O índice é relativo (E sem unidade física) e não é perda de solo em t/ha.
- O NDVI < 0,30 junta solo nu, palhada seca e cebola recém-transplantada.
- A chuva do POWER (~50 km) é a mesma para o recorte todo e suaviza os eventos intensos. O IMERG (~10 km, meia hora) seria melhor, mas o diário pelo POWER veio vazio e o acesso direto pede login no Earthdata (não testei).
- O fator L (comprimento de rampa) ficou fixo; o SRTM de 30 m não vê terraço nem curva de nível.
- O "talhão" é um bloco de 50 m, não o polígono real.
- Testei um só recorte de 5 × 5 km e 6 anos. Não testei São Miguel do Oeste.
- Escolhi o índice de Fournier depois de ver o C1 (é o que passou), não antes.

## 8. Fontes
- Back, Á. J.; Justen, J. G. K.; Guadagnin, C. A. (2023). Caracterização da agressividade e erosividade das chuvas em Ituporanga, SC. *Agropecuária Catarinense* 36(3). https://doi.org/10.52945/rac.v36i3.1766 (PDF: https://publicacoes.epagri.sc.gov.br/rac/article/download/1766/1627/13577)
- Back, Á. J.; Poleto, C. (2018). Distribuição espacial e temporal da erosividade das chuvas no estado de Santa Catarina. *Revista Brasileira de Climatologia* 22 (só contexto). https://ojs.ufgd.edu.br/rbclima/article/download/14157/7388/45309
- Dissertação UDESC/CAV (2019) sobre perda de solo na cebola com chuva simulada em Ituporanga: o plantio direto sobre resíduo de milho foi o manejo mais eficaz. https://www.udesc.br/arquivos/cav/id_cpmenu/1470/Disserta__o_VENESA_PPGCS_15693552053206_1470.pdf
- IBGE, PAM, tabela 5457 (área de cebola em Ituporanga, código 4208500): `sessoes/A3/conferencia/pam_5457_ituporanga_4208500.json`
- Métodos: Richardson et al. (1983), erosividade diária; McCool et al. (1987), fator S; Arnoldus (1980), índice de Fournier modificado. Citados de memória como referência de método.
- Dados: NASA POWER (power.larc.nasa.gov); Sentinel-2 L2A COG (earth-search.aws.element84.com); SRTM (s3.amazonaws.com/elevation-tiles-prod/skadi).
