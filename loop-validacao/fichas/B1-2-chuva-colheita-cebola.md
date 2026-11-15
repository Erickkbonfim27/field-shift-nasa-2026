# B1-2 · Chuva na colheita e na cura da cebola

Sessão: B1 · Trilha: B · Região: Ituporanga · Tentativa 2 de 4 · Data: 2026-11-14

## 1. Ideia (escrita antes do teste)
Critérios copiados de `sessoes/B1/CRITERIOS_ANTES_DO_TESTE.md`, escritos antes de rodar os dados.
- **Hipótese:** o excesso de chuva na colheita (15/out a 31/dez) explica os anos ruins da cebola de Ituporanga melhor que a média e melhor que o balanço hídrico do controle. A chance de não haver dias secos para curar a cebola muda com a data de colheita.
- **Problema que ataca (e para quem):** o agricultor familiar de cebola, que perde volume e qualidade (bulbo podre, armazenagem curta) quando chove na colheita [INFERÊNCIA].
- **Decisão que muda:** escolher o ciclo (precoce, médio ou tardio) ou a data de transplante, para colher no período de menor risco de chuva.
- **Critério de sucesso (definido antes):**
  - C1: Spearman ρ ≤ −0,35 entre a chuva de out–dez e o rendimento da PAM sem tendência.
  - C2: ≥ 4 dos 8 piores anos entre os 8 mais chuvosos.
  - C3: a chance de "colheita sem janela de cura" (não há 4 dias seguidos com chuva < 2 mm nos 15 dias depois da colheita) varia ≥ 15 pontos entre colher em 1/nov e em 15/dez.
- **Linha de base:** média dos anos (ρ = 0) e o controle B1-0 na cebola (ρ = 0,13; 1 de 8).

## 2. Teste
- **Dados oficiais usados:** NASA POWER diário, `PRECTOTCORR`, 1981–2025, grade de ~50 km.
- **Método:** três índices pré-registrados:
  - chuva acumulada;
  - dias com chuva ≥ 10 mm;
  - fração das 4 datas de colheita (1/nov, 15/nov, 1/dez, 15/dez) sem janela de cura.

  O rendimento da PAM foi dividido pela mediana móvel de 9 anos. Script: `sessoes/B1/b1_2_chuva_colheita_cebola.py`.
- **Resultado (n = 42)** [CÁLCULO]:

| Índice | ρ com a PAM | p (permutação) | Piores anos acertados (de 8) |
|---|---|---|---|
| Chuva de 15/out a 31/dez | −0,16 | 0,16 | 2 (2008 e 2023) |
| Dias com chuva ≥ 10 mm | −0,17 | 0,13 | 2 |
| Fração sem janela de cura | −0,17 | 0,13 | 2 |
| Controle (balanço hídrico) | +0,13 | 0,21 | 1 |

  - **Chuva mês a mês contra o rendimento** (leitura extra, não pré-registrada): ρ entre −0,13 e +0,05 de junho a dezembro, sem nenhum mês com sinal.
  - **Colheita sem janela de cura, em 10 anos:** 3,1 (15/out), 3,6 (1/nov), 3,1 (15/nov), 4,4 (1/dez), 3,8 (15/dez) e 4,0 (fim de dez). A chuva média por quinzena fica entre 68 e 83 mm em todo o período.
- **Gráfico:** `sessoes/B1/b1_2_chuva_colheita_x_pam.svg` mostra uma nuvem sem inclinação. Só 2008 e 2023 (anos de enchente em SC) caem no canto "muita chuva, rendimento baixo".

## 3. Validação
- **Contra a linha de base:** fica um pouco melhor que o controle (ρ de −0,16 contra +0,13), mas não se distingue da média (p > 0,1).
- **Fonte externa:** IBGE PAM, tabela 5457, cebola de Ituporanga (município 4208500, produto 40107) [DADO]. Os 8 piores anos (1989, 1996, 2008, 2011, 2012, 2015, 2017 e 2023) incluem anos de enchente (2008, 2011 e 2023), mas o POWER só capta 2008 e 2023. https://apisidra.ibge.gov.br/values/t/5457/n6/4208500/v/112,216/p/all/c782/40107
- **O critério de sucesso foi atingido?** **Não.**
  - C1 não: ρ de −0,16, contra a meta de −0,35.
  - C2 não: 2 de 8, contra a meta de 4.
  - C3 não: a diferença entre 1/nov e 15/dez é de 2 pontos, contra a meta de 15.

## 4. Régua (1 a 5)
| Critério | Nota | Por quê (uma frase) |
|---|---|---|
| Problema real | 3 | Os anos de enchente (2008, 2011 e 2023) aparecem entre os piores da PAM, mas a perda de qualidade não está medida [INFERÊNCIA]. |
| Tamanho do impacto | 3 | Ituporanga tem cerca de 4.000 a 4.800 ha de cebola (PAM 2016–2025), quase toda familiar [INFERÊNCIA]. |
| Resolve de fato | 1 | A chance de colheita molhada é a mesma (3 a 4 em 10) em qualquer data, então não há data melhor para indicar. |
| Validade | 1 | O sinal não supera a média (p = 0,13 a 0,16). |
| Muda a decisão | 1 | Nenhuma data ou ciclo sai como melhor. |
| Simples e factível | 4 | Só chuva diária. |
| Alinhamento com o desafio | 3 | Clima e época, mas não é rotação. |
| Diferencial | 3 | Nenhuma outra sessão olha a colheita da cebola. |
| Cabe no hackathon | 4 | Simples de montar. |
| **Total (máx. 45)** | **23** | |

Aprovada só com 3+ em problema real, resolve de fato e validade. **Não passa.**

## 5. Veredito
**Descartada.** Com o POWER, a chuva da colheita não explica os anos ruins da cebola, e o risco de colheita molhada é o mesmo em qualquer data. Resultado negativo honesto: a chuva de ~50 km não basta para esse problema.

## 6. Relação com o controle
Não compete nem substitui. Mostra, junto com o B1-0, que na cebola de Ituporanga o clima diário do POWER não explica a variação da PAM.

## 7. Limites e o que não foi testado
- A chuva do POWER é suavizada (grade de ~50 km), com muitos dias de garoa e poucos dias "secos" de verdade, o que deixa o índice de cura pouco confiável. O IMERG (~10 km) poderia ser melhor, mas pede login Earthdata e não foi testado.
- A PAM da cebola é um gabarito fraco: valores redondos e repetidos (12.000 kg/ha de 1992 a 1995 e em 1997) e preço e manejo misturados ao clima.
- A perda de qualidade e de armazenagem (o problema de fato) não aparece no rendimento da PAM; a CEASA (preço e classificação) não foi testada.

## 8. Fontes
- NASA POWER (ver B1-0). Resultados: `sessoes/B1/b1_2_resultado.json`.
- IBGE SIDRA, tabela 5457 (link acima).
