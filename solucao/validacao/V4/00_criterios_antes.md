# V4 · Critérios definidos ANTES de rodar o teste

Escrito em 14/11/2026, antes de rodar `v4_motor.py`. Não mudar depois do resultado. Se algo mudar, anotar como desvio no relatório.

## Pergunta
Um motor composto (água por fase + geada + excesso de chuva na fase sensível + flag de ano extremo) explica o rendimento do IBGE PAM melhor que:
- (a) a climatologia (média dos anos);
- (b) a chuva bruta da estação;
- (c) o balanço hídrico sozinho (o controle B1-0)?

## Gabaritos (só conferência, nunca entrada da solução)
| Código | Cultura | Unidade | Ponto POWER | Safras | Papel |
|---|---|---|---|---|---|
| G1 | milho | município 4217204 (SMO), PAM 5457 | SMO | 1985–2025 | principal |
| G2 | milho | microrregião 42001 (SMO), PAM 1612 | SMO | 1990–2025 | principal |
| G3 | milho | microrregiões 42002 (Chapecó) e 42005 (Concórdia) | Chapecó, Concórdia | 1990–2025 | fora da região |
| G4 | cebola | município 4208500 (Ituporanga), PAM 5457 | Ituporanga | 1984–2025 | principal |
| G5 | cebola | microrregião 42014 (Ituporanga) | Ituporanga | 1990–2025 | principal |
| G6 | cebola | microrregião 42011 (Rio do Sul) | Rio do Sul | 1990–2025 | fora da região |

Tendência tecnológica: rendimento dividido pela mediana móvel centrada de 9 anos (igual à B1-0). Sensibilidade: mediana dos vizinhos ±3 anos sem o próprio ano (igual à B3).

## Preditores
- **(a) Climatologia:** média do rendimento relativo nos anos de treino.
- **(b) Chuva bruta:** milho = chuva de 1/dez a 28/fev (a linha de base da B1-0); cebola = chuva de 1/set a 30/nov (a janela da B3-2). Regressão linear no treino.
- **(c) Balanço hídrico sozinho:** rendimento relativo FAO-33 com Ky por fase, parâmetros da B1-0 (milho 20/set, solo argiloso; cebola, solo médio). Duas formas: c1 = índice cru, sem ajuste; c2 = ridge só com o ISNA das fases (mesmo λ do motor).
- **(d) Motor composto.** Duas formas:
  - **d1, mecanístico, pesos fixados a priori (zero ajuste):** y = y_água × f_geada × f_excesso.
    - Milho: f_geada = max(0; 1 − 0,20 × dias com T2M_MIN < 2 °C nas fases I–III); f_excesso = max(0,5; 1 − 0,10 × excedente da fase IV / 100 mm).
    - Cebola: f_geada = max(0; 1 − 0,05 × dias com T2M_MIN < 0 °C nas fases I–II); f_excesso = max(0,4; 1 − 0,15 × max(0; excedente set–nov − 200) / 100 mm).
    - Os coeficientes são [ESTIMATIVA]. O da cebola foi pensado olhando a B3-2, que usou Ituporanga: em G4/G5 ele não é fora da amostra; G6 é.
  - **d2, estatístico (principal):** ridge com λ = 3 fixo, nas variáveis padronizadas com média e desvio do treino.
    - Milho: ISNA vegetativo (fases I+II), ISNA floração (III), ISNA maturação (IV), dias de geada (T2M_MIN < 2 °C, fases I–III), excedente na fase IV (mm), flag de ano extremo (ISNA 20/set–10/jan < 0,75, configuração exata da B3-1).
    - Cebola: ISNA vegetativo (I+II), ISNA bulbificação (III), ISNA maturação (IV), dias de geada (T2M_MIN < 0 °C, fases I–II), excedente set–nov (mm), flag (excedente set–nov ≥ 360 mm, regra da B3-3).
- Todo peso estimado é estimado só nos anos de treino.

## Validação
- **Principal:** leave-one-out (LOO) dentro de cada gabarito.
- **Bloco temporal:** treino 1985–2004 → teste 2005–2025, e o contrário.
- **Fora da região:** d2 treinado em G2 (ou G5), aplicado sem reajuste em G3 (ou G6).

## Métricas (sempre nas previsões fora da amostra)
- Spearman ρ entre previsto e observado.
- SS = 1 − EQM/EQM_climatologia (ganho sobre a climatologia).
- Acerto dos 8 piores anos (G1 e G4, como a B1-0).
- Δρ do motor contra (b) e (c), com bootstrap pareado (2.000 reamostras): fração de reamostras com Δρ > 0.

## Critérios de sucesso
### Milho
- **M1:** ρ(d2) ≥ 0,40 em G1 e ≥ 0,35 em G2.
- **M2:** ρ(d2) − ρ(b) ≥ 0,10 e ρ(d2) − ρ(c1) ≥ 0,10, em G1 e em G2; e SS(d2) > SS(c2).
- **M3:** SS(d2) ≥ 0,10 em G1 (bate a climatologia).
- **M4:** ≥ 4 dos 8 piores anos de G1.
- **M5 (fora da região):** ρ médio em G3 ≥ 0,30 e ≥ ρ(c1) em G3.
- **M6 (bloco temporal):** ρ(d2) ≥ 0,25 nos dois blocos de G1.

### Cebola
- **C1:** ρ(d2) ≥ 0,30 em G4 e ≥ 0,25 em G5.
- **C2:** ρ(d2) − ρ(b) ≥ 0,10 e ρ(d2) − ρ(c1) ≥ 0,10, em G4 e G5; e SS(d2) > SS(c2).
- **C3:** SS(d2) ≥ 0,05 em G4.
- **C4:** ≥ 3 dos 8 piores anos de G4.
- **C5 (fora da região):** ρ em G6 ≥ 0,20.
- **C6 (bloco temporal):** ρ(d2) ≥ 0,20 nos dois blocos de G4.

### Secundário (d1, o motor que a ferramenta mostraria)
- **S1:** ρ(d1) ≥ ρ(c1) + 0,05 em G1 e G4 (somar módulos fixos a priori não piora e ajuda um pouco).

## Leitura para a régua (validade)
- **Validade 3** para uma cultura: M1, M2 e M3 (ou C1, C2 e C3) passam. Ou seja, supera as três linhas de base fora da amostra.
- **Validade 4:** além disso, M5/C5 passam e a conferência externa bate (ZARC, abaixo).
- **Validade ≤ 2:** M2/C2 falham (o motor não supera a chuva bruta ou a água sozinha).

## Decisões ("x em 10 anos") e conferência externa
Com d1 (o motor mostrado ao agricultor), frequência de "falha" por decêndio. Falha = y_d1 < 0,6, ou flag de ano extremo, ou (milho) qualquer dia com T2M_MIN < 2 °C nas fases I–III.
- **D1, data do milho (1/ago a 21/dez), SMO, solo argiloso:** passa se o motor marca 1/ago e 11/ago com ≥ 2 em 10 a mais de falha que 21/set (o ZARC 2026/27 dá 40% de risco em 1–11/ago e 20% de 21/ago a 21/dez em SMO, solos AD4–AD6), e se a melhor data do motor cai entre 21/ago e 21/dez.
- **D2, transplante da cebola (1/jun a 21/set), Ituporanga:** passa se a melhor data do motor cai no intervalo de risco 20% do ZARC cebola sequeiro de Ituporanga.
- Em SC a diferença entre datas aceitáveis pode ser pequena. Se for < 1 em 10, registrar que a decisão de data não muda.
