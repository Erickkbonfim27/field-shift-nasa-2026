# A2 · Critérios definidos antes de rodar qualquer dado (14/11/2026)

Região: São Miguel do Oeste (POWER, ponto -26,725; -53,518). Safra de verão: dezembro do ano Y + janeiro do ano Y+1.

## Definição de "dez–jan seco" (alvo), igual para A2-1 e A2-2
- **Alvo meteorológico (principal em A2-1):** balanço hídrico climático dez–jan = soma(PRECTOTCORR − ET0) de 1/dez a 31/jan. ET0 por Penman-Monteith FAO-56 (mesma função de `prototipo/modelo/risco.py`), com radiação do POWER, portanto safras 1984/85 a 2024/25 (41 safras). "Seco" = tercil inferior (frequência base = 1/3 por construção).
- **Alvo só de chuva (checagem, 44 safras 1981/82–2024/25):** chuva dez–jan no tercil inferior.
- **Alvo agrícola (principal em A2-2):** média de GWETROOT de 1/dez a 31/jan no tercil inferior.
- **Alvo de cultura (checagem):** milho simulado com o balanço hídrico de `risco.py` (Kc/Ky FAO-56/33, solo argiloso, plantio 1/out) com rendimento relativo < 0,6 ("perda").

## Linha de base
Climatologia: probabilidade = frequência de todos os anos (1/3 para os tercis). Pontuação: Brier score com validação cruzada deixando um ano de fora (LOO). Ganho real = Brier Skill Score (BSS) > 0 contra a climatologia.

## A2-1 · ENSO (El Niño / La Niña) e seca de dez–jan
Classificação dos anos pelo ONI da NOAA/CPC (fonte externa, **só para separar os anos**). Duas versões:
- ONI de **NDJ** (concomitante, limite superior do que o ENSO pode explicar).
- ONI de **JAS** (já conhecido no fim de agosto, antes do plantio do milho): é o que o agricultor poderia usar de fato.
Limiar: ±0,5 °C no trimestre (a regra de 5 trimestres seguidos da NOAA será aplicada para a fase NDJ).

**Critério de sucesso (todos):**
1. P(seco | La Niña) ≥ 0,50 **e** P(seco | El Niño) ≤ 0,20 (base 0,33).
2. Diferença La Niña × El Niño com Fisher exato unicaudal p < 0,10.
3. BSS (LOO) da previsão "probabilidade = frequência da fase" > 0,05 contra a climatologia, na versão JAS (a que dá para usar antes do plantio).
4. Mesmo sinal nas duas metades do período (1984–2004 e 2005–2024).
**Muda a decisão** se a chance de perda do milho simulado em anos de La Niña passar de ≤ 20% (todos os anos) para ≥ 30%, ou se a diferença La Niña × El Niño for ≥ 20 pontos percentuais.

## A2-2 · Umidade do solo de novembro prevê seca de dez–jan
Preditor: média de GWETROOT (e GWETTOP) de 1 a 30/nov (POWER/MERRA-2). Variante: 1–15/nov (dá tempo de decidir antes do fim do plantio). SMAP: pede login Earthdata; não será testado se não houver acesso (e só teria ~10 safras desde 2015).
Regra de alerta: novembro no tercil inferior de GWETROOT ⇒ "alerta de dez–jan seco".

**Critério de sucesso (todos), para o alvo agrícola E para o alvo meteorológico separadamente:**
1. Acerto do alerta (anos de alerta que de fato ficaram secos) ≥ 0,50 (base 0,33).
2. Detecção: o alerta pega ≥ 50% dos anos secos (base de um alerta aleatório com mesma frequência: 33%).
3. BSS (LOO) de uma regressão logística simples (preditor = GWETROOT nov) > 0,05 contra a climatologia.
Observação registrada antes: no alvo agrícola parte do ganho é persistência do próprio modelo MERRA-2 (o solo de dez–jan começa do solo de nov). Por isso o alvo meteorológico é a prova de que há previsão de chuva, e o alvo agrícola é a prova de utilidade para a planta. A ideia só é "aprovada" se passar no alvo agrícola e o alvo de cultura (milho simulado) também mostrar ganho, para não ser só um artefato do modelo.

---
# Acrescentado depois de A2-1 e A2-2 e ANTES de rodar A2-3 (14/11/2026)

## A2-3 · Variação de A2-1: La Niña conhecida antes do plantio (ONI de JAS) prevê primavera seca (out–nov)?
Motivo (escrito antes de rodar): a literatura diz que o sinal do ENSO no Sul do Brasil é mais forte na primavera (out–nov) do que em dez–jan, e a quebra de 2020/21 em SMO veio da primavera seca. Ainda não olhei nenhum dado de out–nov.
- **Alvo:** balanço P−ET0 de 1/out a 30/nov no tercil inferior (SMO, 1984–2024, 41 safras). Checagem: chuva out–nov (1981–2024).
- **Preditor:** fase do ONI de JAS (±0,5), sabida no fim de agosto. Também ONI de JAS contínuo.
- **Critério de sucesso (todos):** (1) P(seco | La Niña JAS) ≥ 0,50 e P(seco | El Niño JAS) ≤ 0,20; (2) Fisher unicaudal p < 0,10; (3) BSS LOO > 0,05; (4) mesmo sinal nas duas metades; (5) replicação: o mesmo sentido em Ituporanga (não precisa ser significativo).
- **Muda a decisão:** com o milho simulado (risco.py, solo argiloso) em 5 datas de plantio (21/ago, 11/set, 1/out, 21/out, 11/nov), a melhor data (menor % de anos com rend. < 0,6, desempate pela média) em anos de La Niña JAS é diferente da melhor data em todos os anos, com diferença ≥ 10 p.p. na chance de perda.
- **Conferência externa:** anomalia do rendimento de milho IBGE PAM (microrregião SMO) por fase JAS; e a literatura (Grimm et al.).

---
# Acrescentado depois de A2-3 e ANTES de rodar A2-4 (14/11/2026)

## A2-4 · Teste confirmatório: El Niño (ONI de JAS) muda o TIPO de risco de out–jan (menos seca, mais excesso)?
Por que: em A2-1 e A2-3 o sinal que apareceu foi assimétrico: El Niño com poucos anos secos, La Niña sem sinal estável. Isso foi visto **depois** de olhar os dados de SMO e Ituporanga, então não vale como prova. Para confirmar, uso pontos **novos** do NASA POWER no Oeste de SC, que não olhei: Chapecó (-27,10; -52,62), Concórdia (-27,23; -52,03), Dionísio Cerqueira (-26,26; -53,64) e Xanxerê (-26,88; -52,40). Mesmo baixando só os parâmetros do POWER, a chuva do POWER (MERRA-2, ~50 km) é espacialmente correlacionada com SMO: a replicação não é independente. A conferência independente é o IBGE.
- **Alvo:** chuva de 1/out a 31/jan (safras 1981/82–2024/25, 44), tercil inferior ("seco") e tercil superior ("chuvoso").
- **Preditor:** ONI de JAS ≥ +0,5 (El Niño sabido no fim de agosto).
- **Critério de sucesso (todos):**
  1. Em ≥ 3 dos 4 pontos novos: P(seco | El Niño) ≤ 0,20 **e** P(chuvoso | El Niño) ≥ 0,50 (base 0,33 cada).
  2. Média dos 4 pontos: BSS LOO > 0,05 para o "seco" (previsão = frequência na fase El Niño / não El Niño).
  3. IBGE PAM milho (anomalia do rendimento, razão para a mediana móvel de 7 anos) nas microrregiões de SMO, Chapecó, Concórdia e Xanxerê: anos de El Niño JAS com menos quebras (< 0,8) que os outros anos em ≥ 3 de 4 microrregiões.
- **Muda a decisão:** se o risco de out–jan seco cair de ~33% para ≤ 20% (mudança de faixa como as do ZARC, 20/30/40%) e o de excesso subir para ≥ 50%, a recomendação muda de "proteger contra seca" para "preparar para excesso de chuva" (colheita da silagem, doença, erosão).
- **Correção do desenho, antes de rodar A2-4:** ao baixar, Dionísio Cerqueira veio com a chuva idêntica à de SMO (mesma célula MERRA-2) e Chapecó idêntica a Xanxerê. As 4 "células novas distintas" passam a ser: Chapecó/Xanxerê (-27,10; -52,62), Concórdia (-27,23; -52,03), Itapiranga (-27,17; -53,71) e Palmitos (-27,07; -53,16). O critério 1 vale para essas 4 células (≥ 3 de 4). Nenhum resultado de out–jan foi olhado antes desta correção.
