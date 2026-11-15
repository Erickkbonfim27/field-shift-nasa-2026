# Critérios de sucesso fixados antes de rodar qualquer dado (B1, 14/11/2026)

Estes critérios são copiados para a seção 1 de cada ficha. Não foram mudados depois do teste.

## B1-0 Controle: balanço hídrico → "x de cada 10 anos"
- **Teste principal (milho, São Miguel do Oeste):** balanço hídrico FAO-56 de `prototipo/modelo/risco.py` adaptado (POWER 1984–2025, solo argiloso/médio, milho de 130 dias, plantio padrão 20/set).
- **C1:** correlação de Spearman ρ ≥ 0,40 entre o rendimento relativo simulado e o rendimento do milho na PAM/IBGE sem tendência (safras 1984/85 a 2022/23).
- **C2:** dos 8 piores anos da PAM (sem tendência), o modelo coloca ≥ 4 entre os seus 8 piores (acaso: ~1,6).
- **C3:** a data de menor risco do modelo cai dentro da janela do ZARC milho para São Miguel do Oeste, e mudar a data reduz a perda (y < 0,6) em ≥ 2 de cada 10 anos frente ao plantio padrão. Se a diferença entre datas for < 1 de 10, a ferramenta não muda a decisão.
- **Linha de base:** média dos anos (prever sempre a média: ρ = 0; acerto por acaso de 1,6 em 8). Linha de base dura extra: chuva acumulada de dezembro a fevereiro (se a chuva bruta acertar igual, o balanço hídrico não agrega).
- **Teste secundário (cebola, Ituporanga):** mesmo modelo com cebola (FAO-56, transplante 15/jul, 150 dias). Critério: ρ ≥ 0,30 com a PAM sem tendência.

## B1-1 Geada no milho safrinha (São Miguel do Oeste)
- **Proxy de geada:** `T2M_MIN` ≤ 3 °C no POWER (temperatura do ar a 2 m; a relva costuma ficar 3–5 °C abaixo) [ESTIMATIVA]. Geada que mata o milho: `T2M_MIN` ≤ 1 °C [ESTIMATIVA].
- **Ciclo:** soma térmica base 10 °C do plantio até o ponto de silagem = 1.250 °C·dia (híbrido precoce) [ESTIMATIVA].
- **C1 (o proxy enxerga geada):** dos invernos com geada ampla documentada no Oeste de SC (Epagri/Ciram, INMET), o proxy marca ≥ 4 de 5.
- **C2 (a data importa):** a chance de geada antes do ponto de silagem varia ≥ 30 pontos percentuais entre plantar em 1/jan e em 28/fev (se variar menos, a data não muda a decisão).
- **C3 (bate com fora):** a data-limite do modelo (risco ≤ 20%) fica a ±20 dias da data final do ZARC milho 2ª safra ou da recomendação da Epagri para o Extremo Oeste.
- **Linha de base:** "não fazer nada" = regra fixa sem dado diário (plantar até 15/fev, ou a data da 1ª geada média por média mensal). A ideia só agrega se a curva por ano disser algo que a média não diz (ex.: chance de 1 em 10 x 4 em 10).

## B1-2 Chuva na colheita e cura da cebola (Ituporanga)
- **Índice:** "colheita sem janela de cura" = nos 15 dias após a data de colheita não há 4 dias seguidos com chuva < 2 mm [ESTIMATIVA do manejo]. Também: chuva acumulada e dias com chuva ≥ 10 mm de 15/out a 31/dez.
- **C1:** Spearman ρ ≤ −0,35 entre a chuva de colheita (out–dez) e o rendimento da cebola na PAM sem tendência (1984–2023).
- **C2:** dos 8 piores anos da PAM, o índice coloca ≥ 4 entre os seus 8 anos mais chuvosos na colheita (acaso ~1,6).
- **C3 (a data muda a decisão):** a chance de colheita sem janela de cura difere ≥ 15 pontos entre colher no início de novembro (ciclo precoce) e em meados de dezembro (ciclo tardio).
- **Linha de base:** média dos anos (ρ = 0) e o índice do controle (déficit hídrico da cebola). A ideia só agrega se superar o controle na cebola.

## B1-3 Calor na floração do milho (São Miguel do Oeste) — escrito depois de descartar B1-2 e antes de rodar B1-3
- **Índice:** dias com `T2M_MAX` ≥ 32 °C na janela de floração (dias 55 a 80 após o plantio, milho de 130 dias). A grade do POWER (~50 km) suaviza os picos: 32 °C na grade ≈ 34–35 °C na estação [ESTIMATIVA]. Sensibilidade: 34 °C.
- **C1:** Spearman ρ ≤ −0,35 entre os dias de calor (plantio 20/set) e o rendimento PAM sem tendência (safras 1985–2025).
- **C2 (agrega ao controle):** correlação parcial do calor com o rendimento, descontado o rendimento simulado do controle, ≤ −0,25; e o índice combinado (controle × penalidade de calor) acerta ≥ 5 dos 8 piores anos (controle sozinho: 3).
- **C3 (a data muda a decisão):** a chance de ≥ 3 dias de calor na floração varia ≥ 2 em 10 entre as datas de plantio de agosto a dezembro.
- **Linha de base:** média dos anos (ρ = 0) e o controle B1-0 (ρ = 0,28; 3 de 8).

## B1-4 Clima favorável ao míldio da cebola (Ituporanga) — escrito depois de descartar B1-3 e antes de rodar B1-4
- **Índice:** "dias favoráveis ao míldio" = `RH2M` ≥ 85%, `T2M` entre 10 e 22 °C e chuva ≥ 1 mm, contados de 1/ago a 31/out (crescimento e início da bulbificação) [ESTIMATIVA a partir das condições descritas para *Peronospora destructor*]. Sensibilidade: `RH2M` ≥ 90%.
- **C1:** Spearman ρ ≤ −0,35 entre os dias favoráveis e o rendimento da cebola na PAM sem tendência (1984–2025).
- **C2:** acerta ≥ 4 dos 8 piores anos da PAM (acaso ~1,6; controle: 1).
- **C3 (a data muda a decisão):** a chance de ano "muito favorável" (acima do percentil 70 dos dias favoráveis) varia ≥ 2 em 10 entre transplantes em 1/jun, 1/jul e 1/ago (janela de 90 dias a partir do transplante + 15 dias).
- **Linha de base:** média dos anos (ρ = 0) e o controle B1-0 na cebola (ρ = 0,13; 1 de 8).
