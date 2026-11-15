# B2-1 · Detector de solo descoberto (plantio direto x convencional) por satélite

Sessão: B2 · Trilha: B · Região: ambas (Alto Vale da cebola e Extremo Oeste) · Tentativa 1 de 4 · Data: 2026-11-14

## 1. Ideia (escrita antes do teste)
- **Hipótese:** o Sentinel-2 separa o solo nu (preparo convencional, com aração e grade) do solo coberto de palha (plantio direto) pela banda do infravermelho de ondas curtas. O índice de palha NDTI = (B11 − B12) / (B11 + B12) fica baixo no solo nu e alto na palha. Contando quantas vezes a lavoura aparece de solo nu, dá para dizer se o talhão está em plantio direto ou convencional.
- **Problema que ataca (e para quem):** o agricultor familiar e o técnico da Epagri não têm como medir, talhão a talhão, quanto tempo o solo fica descoberto. Em Ituporanga, o Censo Agro 2017 mostra 855 de 1.514 estabelecimentos com cultivo convencional [DADO, IBGE tabela 6855]. Hoje a prova do plantio direto é a palavra do produtor.
- **Decisão que muda:** (a) o agricultor vê na própria roça, ano a ano, quantas vezes o solo ficou pelado, e onde na rotação isso acontece (por exemplo, entre a colheita da cebola e o milho ou fumo); (b) o técnico prioriza quem visitar; (c) o produtor tem uma prova para crédito e seguro que pedem manejo conservacionista (Plano ABC+, ZARC por níveis de manejo).
- **Critério de sucesso (definido antes):**
  - Teste no agregado do município, porque é onde existe gabarito: o Censo Agro 2017 diz a fração de estabelecimentos com cultivo convencional, C = convencional / (convencional + cultivo mínimo + plantio direto).
  - Indicador do satélite, I1: entre todas as observações sem nuvem de pontos de lavoura em que a planta não está verde (NDVI < 0,30), a fração com solo nu (NDTI < 0,07).
  - **Sucesso:** correlação de Spearman entre I1 e C de **ρ ≥ 0,6 com p < 0,05**, em 14 a 18 municípios dos dois polos (o Alto Vale e o Extremo Oeste), **e** I1 maior em Ituporanga que em São Miguel do Oeste.
  - Para contar como sinal próprio, ρ(I1, C) precisa superar em pelo menos 0,1 a correlação da linha de base.
  - Sensibilidade pré-definida: limiar do NDTI de 0,05 e 0,09.
- **Linha de base:** (1) "não fazer nada" = sem informação, todo município igual (ρ = 0); (2) um proxy ingênuo: a fração de pontos que são lavoura no município (regiões de grão tendem a ter mais plantio direto). Se o I1 não superar o proxy, o satélite não acrescenta nada.

### Regras fixadas antes de rodar
- **Municípios:**
  - Alto Vale: Ituporanga, Aurora, Alfredo Wagner, Petrolândia, Imbuia, Chapadão do Lageado, Leoberto Leal, Vidal Ramos, Atalanta e Agrolândia.
  - Extremo Oeste: São Miguel do Oeste, Guaraciaba, Descanso, Bandeirante, Paraíso, Barra Bonita, Romelândia e Anchieta.
  - Entra o que tiver dado no Censo (pelo menos 150 estabelecimentos com preparo do solo) e cair na quadrícula do Sentinel-2 usada para o polo.
- **Período:** anos agrícolas de out/2019 a set/2021, a coleção `sentinel-2-c1-l2a`. Antes de 2019, o acervo L2A dessa região é ralo: só 4 cenas de jun a ago de 2017.
- **Ponto de lavoura:** pelo menos 8 observações sem nuvem, pelo menos uma com NDVI ≥ 0,60 e pelo menos uma com NDVI < 0,30. Isso pega o ciclo de lavoura anual e tira a mata e a área urbana.
- **Nuvem:** máscara SCL, mantendo só as classes 4 (vegetação) e 5 (solo sem vegetação). Cenas com até 60% de nuvem na quadrícula.
- **Amostra:** grade de pontos a 40 m (leitura nas visões reduzidas do arquivo), recortada pelo polígono do município (IBGE).

## 2. Teste
- **Dados oficiais usados:** Sentinel-2 L2A, coleção C1 (Earth Search/AWS).
  - Bandas: B04 e B08 (NDVI), B11 e B12 (NDTI) e a máscara SCL. Lidas em 40 m nas visões reduzidas do arquivo.
  - Período: out/2019 a set/2021.
  - Cenas: 84 na quadrícula 22JFQ (Alto Vale) e 180 na 22JBR (Extremo Oeste), com até 60% de nuvem.
  - Polígonos dos municípios: malhas do IBGE.
- **Método:**
  1. `sessoes/B2/s2_extrair.py`: lê os pixels de cada município, um por um.
  2. `sessoes/B2/s2_analise.py`: calcula os indicadores (regras na seção 1) e compara com o Censo.
  - Saída: `sessoes/B2/s2_resultado.json`.
  - Censo 2017: tabela 6855, salva em `sessoes/B2/dados/censo2017_6855_preparo_solo_SC.json`.
- **Resultado (18 municípios, NDTI < 0,07):**

| Teste | ρ de Spearman | p |
|---|---|---|
| **I1 × C, todos** | **0,55** | 0,017 |
| I2 × C, todos | 0,40 | 0,10 |
| Linha de base: fração de lavoura × C | 0,58 | 0,013 |
| I1 × C, só Alto Vale (n = 10) | −0,03 | 0,93 |
| I1 × C, só Extremo Oeste (n = 8) | 0,81 | 0,015 |

  - **Sensibilidade:** com NDTI < 0,05, ρ = 0,69 (p = 0,002), mas ainda só 0,11 acima da linha de base. Com NDTI < 0,09, ρ = 0,24 (p = 0,35) [CÁLCULO].
  - **Ituporanga contra São Miguel do Oeste:** I1 = 0,17 em Ituporanga e 0,08 em São Miguel do Oeste. A direção bate com o Censo, que dá 43% contra 11% de convencional [CÁLCULO].
  - **Por mês, em Ituporanga** (lavoura estrita, fração de observações com solo nu): pico em junho (0,17) e agosto (0,10), quase zero de outubro a março. Bate com o preparo do solo e o transplante da cebola (jun–ago). Em São Miguel do Oeste fica ≤ 0,02 em todos os meses, coerente com o plantio direto [CÁLCULO].
  - **Problema achado:**
    - Em Ituporanga, 43% dos pixels têm NDVI mediano > 0,70 (cara de mata), mas 48% dos pixels caem abaixo de 0,30 em 4 datas ou mais. A máscara SCL deixa passar nuvem fina e sombra, e a regra de "lavoura" pegou mata. No Alto Vale, a fração de lavoura saiu de 82% a 90%, o que não é real.
    - O Alto Vale tem 84 cenas contra 180 no Oeste, então o ruído pesa mais lá.
- **Gráfico:** `sessoes/B2/s2_solo_nu_x_censo.svg`, com I1 contra a fração de convencional do Censo, município a município. Os dois polos se separam, mas dentro do Alto Vale não há ordem.

## 3. Validação
- **Contra a linha de base:** ρ = 0,55 do I1 contra 0,58 do proxy "fração de lavoura". **Não supera.** O satélite separa os dois polos (Oeste de grão em plantio direto e Alto Vale de cebola com convencional), mas isso o proxy já faz.
- **Fonte externa:** IBGE, Censo Agropecuário 2017, tabela 6855 (estabelecimentos por sistema de preparo do solo), `https://apisidra.ibge.gov.br/values/t/6855/n6/in%20n3%2042/p/all`.
  - A sazonalidade bate com o calendário da cebola da Epagri (preparo e transplante em jun–ago).
  - A Epagri diz que o preparo convencional ainda domina na cebola do Alto Vale, e que o plantio direto de hortaliças (SPDH) cresce desde 2010 ([Epagri, publicações](https://publicacoes.epagri.sc.gov.br/BD/issue/download/71/89)).
  - Bate na direção, não no detalhe.
- **O critério de sucesso foi atingido?** **Não.** ρ = 0,55 (< 0,6) e sem ganho sobre a linha de base. Só a parte "Ituporanga > São Miguel do Oeste" passou.

## 4. Régua (1 a 5)
| Critério | Nota | Por quê (uma frase) |
|---|---|---|
| Problema real | 4 | 855 de 1.514 estabelecimentos de Ituporanga usam o convencional (Censo 2017), e o ZARC por níveis de manejo já pede sensoriamento remoto para provar palha e tempo sem revolver. |
| Tamanho do impacto | 3 | Pesa na conservação do solo de toda a cebola do Alto Vale e no acesso a crédito e seguro, mas o ganho por família é indireto. |
| Resolve de fato | 2 | Com a máscara atual, o sinal não ordena os municípios do Alto Vale, que é onde a decisão importa. |
| Validade | 2 | Não supera a linha de base (0,55 contra 0,58), embora bata com o Censo na direção. |
| Muda a decisão | 2 | Ainda não dá para dizer a um agricultor "seu talhão foi convencional" com segurança. |
| Simples e factível | 3 | Os dados são abertos e leves (40 m), mas a máscara de nuvem é o gargalo. |
| Alinhamento com o desafio | 4 | É saúde do solo na rotação, com Sentinel-2 da aba Resources. |
| Diferencial | 4 | Separa a palha do solo nu (SWIR), o que o NDVI das ideias da A3 não faz. |
| Cabe no hackathon | 3 | O pipeline roda em ~10 minutos, mas a calibração falta. |
| **Total (máx. 45)** | **27** | |

## 5. Veredito
**Ajustar.** Há sinal físico: a sazonalidade da cebola e a separação dos polos. Mas a máscara de lavoura foi contaminada por nuvem residual, e o indicador não superou a linha de base. A versão ajustada, com confirmação temporal do "não verde" e sem a mata, está pré-registrada e testada como tentativa 3 (`fichas/B2-3-solo-descoberto-ajustado.md`).

## 6. Relação com o controle
Complementa. O controle escolhe a rotação pelo risco climático; este indicador mostra se a rotação escolhida deixa o solo nu e quando. Na demo, entraria como "seu talhão ficou X vezes de solo nu entre a cebola e o milho".

## 7. Limites e o que não foi testado
- **Tempo:** o Censo é de 2016/17; o satélite, de 2019–2021.
- **Gabarito:** o Censo conta estabelecimentos, não área; um estabelecimento pode usar mais de um sistema.
- **Resolução:** 40 m mistura talhões pequenos de cebola com bordas.
- **Limiar:** o NDTI não foi calibrado em campo. Solo úmido sobe o NDTI e pode parecer palha.
- **Amostra:** n = 18 municípios.

## 8. Fontes
- Sentinel-2 L2A C1, Earth Search: https://earth-search.aws.element84.com/v1 [DADO].
- IBGE, Censo Agropecuário 2017, tabela 6855 [DADO, conferência].
- IBGE, malhas municipais: https://servicodados.ibge.gov.br/api/v3/malhas/municipios/ [DADO].
- ZARC níveis de manejo: https://revistacultivar.com.br/noticias/governo-cria-nova-classificacao-de-manejo-agricola e Embrapa: https://ainfo.cnptia.embrapa.br/digital/bitstream/doc/1148652/1/DOCUMENTO-447-final.pdf
- Epagri, SPDH na cebola: https://publicacoes.epagri.sc.gov.br/BD/issue/download/71/89
