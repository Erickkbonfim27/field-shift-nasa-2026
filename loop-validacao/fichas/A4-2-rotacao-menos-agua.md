# A4-2 · Qual rotação usa menos água no Extremo Oeste

Sessão: A4 · Trilha: A · Região: São Miguel do Oeste · Tentativa 2 de 4 · Data: 2026-11-14

## 1. Ideia (escrita antes do teste)
Registrada antes de rodar dados em `sessoes/A4/00_criterios_pre_teste.md`.
- **Hipótese:** as rotações anuais típicas do Extremo Oeste diferem o bastante em água consumida, déficit e risco de perda para que a ferramenta recomende uma "rotação que poupa água".
- **Problema que ataca (e para quem):** o agricultor familiar de leite e grãos que sofre com as estiagens de verão (2019 a 2022).
- **Decisão que muda:** qual sequência verão/inverno usar no talhão.
- **Critério de sucesso (definido antes):** uma rotação com **déficit médio ≥ 20% menor** E **risco de perda ≥ 5 pontos percentuais menor** que a referência (R3), mantendo a ordem em ≥ 2 dos 3 solos. Se as rotações diferirem menos de 10% em ETa, a ideia de "usar menos água" não muda a decisão.
- **Linha de base:** R3, milho silagem / azevém, a rotação mais comum no leite [ESTIMATIVA].

## 2. Teste
- **Dados oficiais usados:** NASA POWER diário em SMO, de 1984 a 2025, grade de cerca de 50 km.
- **Método:**
  - Balanço hídrico contínuo de 1/jul/1984 a 30/jun/2025, com a água do solo passando de uma cultura para a outra. Entre as culturas, o solo fica em pousio com evaporação de 0,3 × ET0. Kc, fases e Ky vêm da FAO.
  - Solos: argiloso de 1 m (175 mm), médio (125 mm) e raso de 0,5 m (87 mm).
  - Rotações e datas [ESTIMATIVA]:
    - R1 milho grão (21/set, 140 dias) / aveia (1/abr)
    - R2 soja (11/nov) / trigo (11/jun)
    - R3 milho silagem (1/set) / azevém (1/mar, 180 dias)
    - R4 sorgo silagem (21/out) / aveia (1/abr)
    - R5 milho silagem (1/set) + sorgo safrinha (5/jan) / aveia (1/mai)
  - A geada só penaliza as culturas de verão.
  - Mudanças depois do teste: (a) na 1ª rodada, a regra de geada também cortava aveia, trigo e azevém, que toleram geada, e saíam perdas em 75% a 95% dos anos. Corrigi para valer só no verão. (b) A aveia de R5 ficou com 120 dias, não 100.

  Script: `sessoes/A4/a4_2_rotacoes_agua.py`.
- **Resultado** [CÁLCULO], médias anuais de 1984/85 a 2023/24 (n = 40):

  | Rotação | ETa das culturas, argiloso (mm) | Déficit: argiloso / médio / raso (mm) | Anos com perda: argiloso / médio / raso |
  |---|---|---|---|
  | R1 milho grão / aveia | 637 | 33 / 53 / 76 | 12% / 20% / 40% |
  | R2 soja / trigo | 698 | 29 / 50 / 77 | 10% / 17% / 23% |
  | **R3 milho silagem / azevém (ref.)** | 681 | **12 / 25 / 44** | **5% / 15% / 25%** |
  | R4 sorgo silagem / aveia | 532 | 11 / 23 / 38 | 0% / 0% / 3% |
  | R5 milho silagem + sorgo / aveia | 821 | 17 / 37 / 63 | 5% / 15% / 25% |

  - Chuva média de 1.860 mm/ano. Drenagem (água que sobra) de 1.040 a 1.260 mm/ano em todas as rotações. Em média, a chuva dentro do ciclo passa a ETc de todas as culturas. Exemplo: milho grão, ETc de 512 mm com 835 mm de chuva no ciclo.
  - O déficit vem quase todo da cultura de verão; o de inverno fica entre 0 e 13 mm.
- **Gráfico:** `sessoes/A4/fig_a4_2_rotacoes.svg`, com déficit e anos de perda por rotação e solo. O déficit é pequeno em todas as rotações; o risco depende da cultura de verão.

## 3. Validação
- **Contra a linha de base:** a melhor rotação, R4, tem déficit 8%, 8% e 14% menor que R3, abaixo do limiar de 20%. O risco de perda é 5, 15 e 22 pontos menor, acima do limiar de 5. R4 tem déficit menor que R3 em só 12 a 19 de 40 anos. R3 já é a 2ª rotação de menor déficit, porque o milho silagem plantado em 1/set fecha o ciclo antes do pico de calor. As diferenças de ETa passam de 10% (R4 532 mm contra R5 821 mm), mas a água "poupada" vai embora pela drenagem. Ela não sobra para a cultura seguinte, porque o solo enche de novo todo inverno.
- **Fontes externas:**
  - **ZARC 2026/27 de SMO:** sorgo forrageiro com 20% de risco em todos os solos; milho 1ª safra e soja com 20% em solos AD4–AD6 e 30–40% em AD1–AD3. **A ordem de risco do modelo (sorgo < milho silagem cedo ≈ soja < milho grão) bate com o ZARC**, inclusive no ponto de que o solo muda o risco do milho e da soja, mas não o do sorgo.
  - **FAO-33**, faixas de necessidade de água por ciclo: milho 500 a 800 mm (modelo: 512, bate); soja 450 a 700 mm (479, bate); sorgo 450 a 650 mm (386, abaixo); trigo 450 a 650 mm (247, abaixo, porque a ET0 de inverno em SMO é baixa). Bate em parte.
  - **Epagri/Cepa:** as perdas de verão em 2019/20 e 2021/22 confirmam que o risco está na cultura de verão, não na de inverno.
- **O critério de sucesso foi atingido?** **Não.** O risco ficou abaixo do limiar, mas o déficit não caiu 20%.

## 4. Régua (1 a 5)
| Critério | Nota | Por quê (uma frase) |
|---|---|---|
| Problema real | 2 | Em SMO falta água em alguns verões, mas não no ano: chove 1.860 mm e sobram mais de 1.000 mm. |
| Tamanho do impacto | 2 | As diferenças de déficit entre rotações são de 10 a 40 mm/ano. |
| Resolve de fato | 2 | "Poupar água" não muda a escolha; o que muda é trocar a cultura de verão, que já é a A4-3. |
| Validade | 3 | Dado oficial contra linha de base, e a ordem de risco bate com o ZARC, mas o critério não passou e o sorgo não está calibrado. |
| Muda a decisão | 2 | A rotação de referência já está entre as de menor déficit. |
| Simples e factível | 4 | Mesmo modelo, rodando contínuo. |
| Alinhamento com o desafio | 3 | Compara rotações com dados da NASA, mas a métrica de água é fraca no clima úmido. |
| Diferencial | 2 | Não acrescenta muito ao ZARC por cultura. |
| Cabe no hackathon | 4 | Já está rodando. |
| **Total (máx. 45)** | **24** | |

## 5. Veredito
**Descartada.** No Extremo Oeste, a pergunta "qual rotação usa menos água" não é a que o agricultor precisa responder. A água do ano sobra. O que pesa é a sensibilidade da cultura de verão ao veranico e a água que o solo guarda, e nisso o sorgo se destaca. Esse caminho segue na A4-3.

## 6. Relação com o controle
Complementa, mas com peso pequeno. Na demo, um gráfico de déficit por rotação mostraria barras parecidas e pouco ajudaria. O que vale levar é **"o risco está no verão, e o seu solo muda o risco"**, que bate com o ZARC. Fica melhor contado como "perda por cultura de verão" do que como "água usada".

## 7. Limites e o que não foi testado
- **Sorgo com Kc e Ky genéricos.** A ETa menor de R4 vem em parte do Kc de 1,05 do sorgo (milho: 1,20) e do plantio mais tardio. Com Kc × 1,15, o sorgo chegaria a cerca de 1,21 e a diferença de ETa para o milho quase sumiria [INFERÊNCIA, não rodei A4-2 com Kc alterado]. O risco quase zero de R4 depende do Ky (ver a sensibilidade na A4-1).
- Não modelei o efeito da palhada (aveia, azevém) na evaporação e na infiltração, nem o ganho de nitrogênio. Também não modelei o pastejo do azevém (o Kc é fixo) nem a geada na floração do trigo.
- Água distribuída por igual no perfil; não há escoamento superficial (relevante em encosta, ver SRTM nas sessões A3/B2). Grade POWER de cerca de 50 km.
- Datas e ciclos são típicos estimados, não levantados com a Epagri local.

## 8. Fontes
- NASA POWER diário: `loop-validacao/dados/power_sao_miguel_do_oeste.json`.
- ZARC 2026/27, tábua de risco (MAPA): https://dados.agricultura.gov.br/dataset/tabua-de-risco-zoneamento-agricola-de-risco-climatico (extrato da sessão A1; resumo em `sessoes/A4/zarc_smo_resumo.txt`).
- FAO-33 (Doorenbos & Kassam, 1979), necessidade de água por cultura; FAO-56 (Allen et al., 1998).
- Epagri/Cepa via Notícias Agrícolas: [estiagem de 2021/22](https://www.noticiasagricolas.com.br/noticia/309922); [estiagem de 2019/20](https://www.noticiasagricolas.com.br/noticia/272995).
