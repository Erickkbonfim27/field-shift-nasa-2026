# B2-3 · Detector de solo descoberto, versão ajustada (máscara com confirmação no tempo)

Sessão: B2 · Trilha: B · Região: ambas (Alto Vale e Extremo Oeste) · Tentativa 3 de 4 · Data: 2026-11-14

## 1. Ideia (escrita antes do teste)
- **Hipótese:** é a mesma da B2-1. O ajuste é só na limpeza: a B2-1 falhou porque nuvem fina e sombra, que a SCL não pega, criaram quedas falsas de NDVI na mata. Uma observação "não verde" de verdade (solo nu ou palha) dura semanas; a de nuvem, uma data. Exigindo a confirmação no tempo e tirando a mata, o indicador deve ordenar os municípios também dentro do Alto Vale.
- **Problema que ataca, decisão que muda:** iguais aos da B2-1.
- **Mudanças, fixadas antes de rodar e sem olhar o resultado novo:**
  1. **Observação não verde:** NDVI < 0,30 só conta se a observação válida anterior ou a seguinte, dentro de 30 dias, também tiver NDVI < 0,40.
  2. **Ponto de lavoura:** pelo menos 8 observações válidas, pelo menos uma com NDVI ≥ 0,60, pelo menos 2 observações não verdes confirmadas e NDVI mediano < 0,70. O NDVI mediano tira a mata, que fica verde quase sempre.
  3. **I1:** a mesma conta da B2-1, só com as observações confirmadas. O limiar principal continua NDTI < 0,07, com sensibilidade em 0,05 e 0,09.
  - Mesmos 18 municípios, mesmo período, mesmos dados extraídos (`sessoes/B2/dados/s2/`).
- **Critério de sucesso (definido antes):** o mesmo da B2-1, para que a régua não mude.
  - Spearman ρ(I1, C) ≥ 0,6 com p < 0,05;
  - ρ(I1, C) pelo menos 0,1 acima do proxy "fração de lavoura", recalculado com a máscara nova;
  - I1 maior em Ituporanga que em São Miguel do Oeste.
  - Critério extra, também fixado antes: dentro do Alto Vale (n = 10), ρ > 0,3. Se não passar, a ideia fica no máximo "ajustar", porque não serve onde a cebola está.
- **Linha de base:** a mesma da B2-1.
- **Aviso de honestidade:** este é o segundo teste com os mesmos 18 municípios. Mesmo que passe, conta como resultado com amostra pequena e uma rodada de ajuste (validade no máximo 3, salvo conferência externa nova).

## 2. Teste
- **Dados oficiais usados:** os mesmos da B2-1 (Sentinel-2 L2A C1, 84 cenas no Alto Vale e 180 no Extremo Oeste, out/2019 a set/2021, 40 m).
- **Método:** `sessoes/B2/s2v2_analise.py` aplica as três mudanças fixadas na seção 1. Saída: `sessoes/B2/s2v2_resultado.json`.
- **A máscara ficou realista:** Ituporanga caiu de 90% para 37% de lavoura; o Alto Vale vai de 8% a 41%, e o Extremo Oeste de 12% a 31%.
- **Resultado (NDTI < 0,07):**

| Teste | ρ | p |
|---|---|---|
| **I1 × C, todos (n = 18)** | **−0,18** | 0,47 |
| Linha de base: fração de lavoura × C | −0,01 | 0,98 |
| I1 × C, só Alto Vale (n = 10) | −0,04 | 0,91 |
| I1 × C, só Extremo Oeste (n = 8) | **0,90** | 0,002 |

  - **Sensibilidade:** com NDTI < 0,05, ρ = 0,13; com 0,09, ρ = −0,59. Só no Extremo Oeste o resultado se mantém: 0,88 e 0,90 [CÁLCULO].
  - **Ituporanga contra São Miguel do Oeste:** I1 = 0,071 contra 0,056. A direção é certa, mas a diferença é pequena [CÁLCULO].
- **Leitura:** a separação entre os polos na B2-1 (ρ = 0,55) vinha em boa parte da nuvem residual, mais comum no Alto Vale. Limpando, o Alto Vale não aparece mais "nu" que o Oeste. No Oeste, onde há 2 vezes mais cenas limpas e os talhões são maiores, o indicador ordena os municípios quase igual ao Censo, nas duas versões da máscara (0,81 e 0,90) [INFERÊNCIA].
- **Gráfico:** `sessoes/B2/s2v2_solo_nu_x_censo.svg`, com os dois polos misturados no eixo vertical.

## 3. Validação
- **Contra a linha de base:** ρ = −0,18 contra −0,01. Não supera.
- **Fonte externa:** Censo Agro 2017, tabela 6855 (IBGE). No Alto Vale não bate; no Extremo Oeste bate (ρ = 0,90, n = 8, com C de só 0,09 a 0,24).
- **O critério de sucesso foi atingido?** **Não.** Falhou o ρ geral, o ganho sobre a linha de base e o ρ > 0,3 dentro do Alto Vale.

## 4. Régua (1 a 5)
| Critério | Nota | Por quê (uma frase) |
|---|---|---|
| Problema real | 4 | O mesmo da B2-1: o preparo convencional domina na cebola, e há demanda por prova de manejo (ZARC por níveis de manejo). |
| Tamanho do impacto | 3 | O mesmo da B2-1. |
| Resolve de fato | 1 | Na cebola do Alto Vale, o indicador não separa os municípios de mais e de menos convencional. |
| Validade | 2 | Não supera a linha de base no conjunto; o sinal do Oeste é de subgrupo, com n = 8. |
| Muda a decisão | 1 | Não dá para usar no Alto Vale. |
| Simples e factível | 3 | O mesmo pipeline, mas a nuvem no inverno do Alto Vale é estrutural. |
| Alinhamento com o desafio | 4 | É conservação do solo com Sentinel-2. |
| Diferencial | 3 | O SWIR separa a palha, mas sem prova no lugar que importa. |
| Cabe no hackathon | 3 | Roda, mas não convence. |
| **Total (máx. 45)** | **24** | |

## 5. Veredito
**Descartada para o Alto Vale (cebola).** Com 84 cenas em dois anos, a nuvem de inverno e talhões pequenos a 40 m, o Sentinel-2 não reproduz o Censo. O sinal do Extremo Oeste (ρ = 0,90) é uma pista, não um resultado: é de subgrupo e com amostra pequena. Ele é testado fora da amostra na tentativa 4 (`fichas/B2-4-solo-descoberto-oeste-replicacao.md`).

## 6. Relação com o controle
Nenhuma, enquanto não funcionar na cebola.

## 7. Limites e o que não foi testado
- **Resolução:** usei 40 m, e o talhão de cebola (1 a 3 ha) pede 10 m. Ler a 10 m custa 4 vezes mais dados.
- **Período:** só 2019–2021. Mais anos dariam mais observações limpas no inverno.
- **Outro sensor:** Landsat 8/9 e o HLS (30 m) somariam passagens, mas não foram testados.
- **Ajuste:** esta é a segunda rodada de ajuste com os mesmos municípios. Não ajustei mais para não pescar resultado.

## 8. Fontes
- As mesmas da B2-1.
