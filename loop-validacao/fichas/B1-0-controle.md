# B1-0 · Controle: balanço hídrico → "x de cada 10 anos" (ideia atual)

Sessão: B1 · Trilha: B · Região: ambas (foco em São Miguel do Oeste) · Tentativa: controle (fora da contagem de 4) · Data: 2026-11-14

## 1. Ideia (escrita antes do teste)
Critérios copiados de `sessoes/B1/CRITERIOS_ANTES_DO_TESTE.md`, escritos antes de rodar os dados.
- **Hipótese:** o balanço hídrico por fase (FAO-56/FAO-33) de `prototipo/modelo/risco.py`, alimentado com o NASA POWER, separa os anos ruins dos bons e mostra uma data ou cultura de menor risco que muda a decisão do agricultor em SC.
- **Problema que ataca (e para quem):** o agricultor familiar de leite e milho do Extremo Oeste (estiagens de 2005, 2012 e 2022) e o de cebola de Ituporanga não sabem a chance de perder a safra por falta de água.
- **Decisão que muda:** data de plantio, cultura ou ciclo.
- **Critério de sucesso (definido antes):**
  - C1: Spearman ρ ≥ 0,40 entre o rendimento simulado do milho (plantio 20/set, solo argiloso) e o rendimento da PAM sem tendência, nas safras 1985–2025.
  - C2: ≥ 4 dos 8 piores anos da PAM entre os 8 piores do modelo.
  - C3: a melhor data do modelo cai na janela do ZARC, e mudar a data reduz a perda em ≥ 2 de 10 anos frente ao plantio de 20/set.
  - Cebola em Ituporanga: ρ ≥ 0,30.
- **Linha de base:** média dos anos (ρ = 0; acerto de 1,6 em 8 por acaso). Linha de base dura: a chuva bruta de dezembro a fevereiro, que entra porque, se a chuva sozinha acertar igual, o balanço hídrico não agrega nada.

## 2. Teste
- **Dados oficiais usados:** NASA POWER diário (`PRECTOTCORR`, `T2M`, `T2M_MAX`, `T2M_MIN`, `RH2M`, `WS2M`, `ALLSKY_SFC_SW_DWN`), 1984–2025 para ET0 (o `ALLSKY` está vazio antes de 1984), grade de ~50 km. Água disponível do solo pela tabela GAEZ v5 do protótipo (65, 125 e 175 mm/m).
- **Método:** o `risco.py` adaptado está em `sessoes/B1/comum.py`. ET0 por Penman-Monteith FAO-56, balde com Ks e rendimento relativo pelo Ky da FAO-33. Milho de 130 dias com fases 25/35/40/30 (o ZARC SC usa 25/35/40/20 no grupo I) e solo partindo de 70% da água disponível. Cebola transplantada em 15/jul, 150 dias. O rendimento da PAM foi dividido pela mediana móvel centrada de 9 anos, para tirar a tendência tecnológica. Script: `sessoes/B1/b1_0_controle.py`. O teste de geada nas datas do controle está em `sessoes/B1/b1_0_geada_controle.txt`.
- **Resultado:**
  - **Milho, São Miguel do Oeste (n = 41 safras):** ρ = **0,28** (p = 0,036, permutação) [CÁLCULO]. Acerta **3 de 8** piores anos [CÁLCULO]:
    - 8 piores da PAM: 1985, 1991, 2002, 2005, 2012, 2021, 2022 e 2024.
    - 8 piores do modelo: 1986, 1996, 2005, 2006, 2009, 2012, 2022 e 2023.
  - **Onde o modelo erra:** não vê 1991 (simula 0,91, mas a PAM ficou em 0,40 da mediana), nem 2002 e 2021. Dá alarme falso em 1986 (simula 0,21, mas a PAM ficou normal), 1996 e 2009 [CÁLCULO].
  - **Sensibilidade:** com solo médio, ρ = 0,27 e 3 de 8; com solo arenoso, 0,23 e 2 de 8; com plantio em 1/out, 0,33 e 3 de 8 [CÁLCULO]. O resultado não depende de um ajuste fino.
  - **Janelas de plantio (só água):** a perda (y < 0,6) fica entre 0,7 e 1,2 em 10 anos de 1/set a 21/dez, e cai a 0,2 em 10 em agosto [CÁLCULO]. O modelo só de água manda plantar em agosto.
  - **A mesma janela, contando geada** (`T2M_MIN` < 2 °C nas fases I a III, o critério do ZARC SC): a geada atinge 6,3 em 10 anos no plantio de 1/ago, 4,6 em 11/ago, 3,2 em 21/ago e 1,7 em 1/set. Só zera a partir de 21/set [CÁLCULO]. Somando os dois riscos, a melhor janela fica em 11 a 21/set, que é a data que o agricultor já usa.
  - **Cebola, Ituporanga (n = 42):** ρ = **0,13** (p = 0,21), acerta **1 de 8**. O modelo só registra perda por falta de água em 1 dos 42 anos (rendimento simulado mediano de 0,89, mínimo de 0,58) [CÁLCULO]. Os anos ruins da cebola (1989, 1996, 2008, 2011, 2012, 2015, 2017 e 2023) não são anos secos.
- **Gráficos:**
  - `sessoes/B1/b1_0_milho_modelo_x_pam.svg`: a nuvem é larga, e 1991 e 2012 caem baixo na PAM com o modelo dizendo "ano bom".
  - `sessoes/B1/b1_0_janelas_agua_x_geada.svg`: a curva de água indica agosto, e a de geada mostra que agosto é a pior data.

## 3. Validação
- **Contra a linha de base:**
  - O modelo supera a média: ρ de 0,28 contra 0, e 3 de 8 contra 1,6 por acaso.
  - Não supera a chuva bruta de dez–fev: ρ de 0,23 contra 0,28 (diferença dentro do ruído), e a chuva acerta **4 de 8** contra 3 do modelo [CÁLCULO].
  - Na cebola, nem a média é superada com clareza (p = 0,21).
- **Fontes externas:**
  - **IBGE PAM, tabela 5457:** milho de São Miguel do Oeste (código 4217204) e cebola de Ituporanga (código **4208500**; a versão inicial do protocolo dizia 4208401, que é Itapiranga, e já foi corrigida; todos os dados da B1 foram puxados com 4208500). O código da cebola é **40107**; o protocolo diz 40281. O gabarito ano a ano está acima. [DADO] https://apisidra.ibge.gov.br/values/t/5457/n6/4217204,4208500/v/112,216/p/all/c782/40122,40107
  - **ZARC milho 1ª safra SC 2026/27 (Portaria SPA/MAPA nº 236, de 30/06/2026):** o próprio ZARC usa o mesmo princípio (ISNA pelo modelo SARRA, ET0 com variáveis do NASA POWER). Mas em SC ele também conta geada (Tmin < 2 °C nas fases I a III), frio na floração (Tmed < 18 °C) e excesso de água na maturação, e usa raiz de 60 cm, com água disponível de 24 a 95 mm [DADO]. Os decêndios de São Miguel do Oeste não foram obtidos: o CSV do SISZARC no dados.agricultura.gov.br não respondeu em três tentativas. Texto da portaria em `sessoes/B1/externo/zarc_portaria_236_2026_milho1_SC.txt`. https://www.gov.br/agricultura/pt-br/assuntos/riscos-seguro/programa-nacional-de-zoneamento-agricola-de-risco-climatico/portarias/safra-vigente/santa-catarina/POD8691.PDF
  - **Epagri/UFPel (estudo de épocas de semeadura no Extremo Oeste, estação de São Miguel do Oeste):** a deficiência de água no Oeste de SC costuma cair de novembro a janeiro, no pendoamento [DADO]. Isso bate com o mecanismo do modelo, mas não com a força do sinal. https://cti.ufpel.edu.br/siepe/arquivos/2013/CA_00078.pdf
- **O critério de sucesso foi atingido?** **Não.**
  - C1 não: ρ de 0,28, contra a meta de 0,40.
  - C2 não: 3 de 8, contra a meta de 4.
  - C3 não: a diferença entre datas de setembro a dezembro é menor que 1 em 10, e a única data "melhor" (agosto) é a pior quando se conta a geada.
  - Cebola não: ρ de 0,13.

## 4. Régua (1 a 5)
| Critério | Nota | Por quê (uma frase) |
|---|---|---|
| Problema real | 4 | As estiagens de 2012 e 2022 derrubaram o milho de São Miguel do Oeste para 40% e 45% da mediana (PAM). |
| Tamanho do impacto | 3 | As quebras são grandes, mas vêm em cerca de 1 de cada 5 anos e só no milho; na cebola de Ituporanga a falta de água quase não pesa. |
| Resolve de fato | 2 | Em SC a data habitual (20/set) já é a de menor risco, e o modelo só de água sugeriria agosto, com 6 em 10 anos de geada. |
| Validade | 2 | Supera a média, mas não a chuva bruta de dez–fev, e não atinge nenhum dos critérios fixados antes. |
| Muda a decisão | 2 | A diferença entre datas viáveis é menor que 1 ano em 10; na cebola, o modelo diz "sem risco" quase todo ano. |
| Simples e factível | 4 | Já está pronto e roda em segundos com o POWER. |
| Alinhamento com o desafio | 4 | Usa dados NASA para comparar estratégias de plantio, que é o pedido do desafio. |
| Diferencial | 2 | O ZARC já faz o mesmo cálculo (ISNA com ET0 do POWER) por município, e em SC ainda inclui geada e frio. |
| Cabe no hackathon | 5 | Já existe. |
| **Total (máx. 45)** | **28** | |

Aprovada só com 3+ em problema real, resolve de fato e validade. **Não passa** (resolve de fato 2, validade 2).

## 5. Veredito
**Ajustar (não aprovado na forma atual para SC).** O balanço hídrico sozinho tem sinal fraco em São Miguel do Oeste (ρ = 0,28, igual à chuva bruta), nenhum na cebola, e sem a camada de geada daria um conselho errado (plantar em agosto). A promessa "x de cada 10 anos" continua boa, mas em SC precisa somar geada e frio (como o próprio ZARC faz) e mirar decisões em que a data realmente mude o risco.

## 6. Relação com o controle
É o próprio controle. Serve de régua: na Trilha B, nenhuma ideia de clima e época superou o controle na validação ano a ano contra a PAM. A geada (B1-1) é a camada que falta ao controle em SC.

## 7. Limites e o que não foi testado
- A grade do POWER (~50 km) mistura vales e chapadas; a chuva de verão no Oeste é convectiva e muito local.
- A PAM é um rendimento municipal estimado, com valores arredondados (ex.: 3.000 kg/ha de 1992 a 1994) e área em queda forte (16.000 ha em 1974 e 700 ha em 2025), o que deixa o gabarito ruidoso.
- Parâmetros de cultura da FAO, não os do ZARC; o solo parte de 70% da água disponível [ESTIMATIVA].
- Não testado: SMAP, IMERG e GLDAS (pedem login Earthdata); NDVI do Landsat como gabarito no talhão; decêndios do ZARC para o município (download falhou).
- O teste só cobre a data; não cobre a troca de cultura (A4) nem o efeito da rotação no ano seguinte.

## 8. Fontes
- NASA POWER, API diária, comunidade AG: `loop-validacao/dados/power_*.json`.
- IBGE SIDRA, tabela 5457 (PAM) e tabela 839 (milho 1ª/2ª safra): `sessoes/B1/externo/`.
- MAPA, Portaria SPA/MAPA nº 236/2026, ZARC milho 1ª safra SC 2026/27 (link acima).
- Estudo de épocas de semeadura de milho no Extremo Oeste de SC, SIEPE/UFPel 2013 (link acima; trecho lido pela busca, o PDF não abriu).
- Resultados: `sessoes/B1/b1_0_resultado.json`.
