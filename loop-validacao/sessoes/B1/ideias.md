# B1 · Clima e época: lista de ideias (escrita em 14/11/2026, antes de rodar dados)

Sessão B1 · Trilha B. Fora do escopo (já com a Trilha A): mapa de época e escalonamento (A1), ENSO e umidade do solo (A2), erosão e saúde do solo (A3), milho x sorgo e rotação com menos água (A4), cobertura e área de cebola (A5).

| # | Ideia | Região | Escolhida? | Por quê (uma linha) |
|---|---|---|---|---|
| 0 | **Controle:** balanço hídrico por fase vira "x de cada 10 anos" e escolhe a rotação de menor risco | ambas | testar (B1-0) | É a ideia atual; serve de régua para o ranking. |
| 1 | **Geada no milho safrinha (2ª safra, silagem):** data-limite de plantio depois da colheita do milho de verão, com risco de geada antes do ponto de silagem | São Miguel do Oeste | **sim (B1-1)** | Decide a rotação de verdade (2º milho x pastagem de inverno), usa só `T2M_MIN` e graus-dia do POWER e tem gabarito externo (ZARC 2ª safra, Epagri/Ciram). |
| 2 | **Chuva na colheita e cura da cebola:** chance de não haver dias secos para curar a cebola no campo, por data de colheita (ciclo precoce, médio ou tardio) | Ituporanga | **sim (B1-2)** | Ataca a perda de qualidade e de armazenagem que o controle (só falta de água) não vê; dá para conferir com a produtividade da PAM ano a ano. |
| 3 | Calor na floração do milho (dias com `T2M_MAX` ≥ 32–35 °C no pendoamento) | São Miguel do Oeste | reserva 1 | Sinal plausível, mas no Oeste de SC o calor vem junto da seca e tende a repetir o controle. |
| 4 | Clima favorável a doença foliar da cebola (míldio: umidade alta e 10–20 °C) por data de transplante | Ituporanga | reserva 2 | Problema real, mas falta gabarito público ano a ano para validar; viraria modelo sem prova. |
| 5 | Janela de semeadura da pastagem de inverno (aveia/azevém) após o milho silagem: risco de outono seco | São Miguel do Oeste | reserva 3 | Bom para o leite, mas encosta em A4 (água) e A5 (cobertura). |
| 6 | Granizo na cebola e no milho | ambas | não | O POWER (~50 km, diário) não registra granizo, e IMERG/GPM direto pede login; sem dado não há teste. |

## Resultado (14/11/2026)
| Ficha | Ideia | Veredito | Problema real / Resolve / Validade | Total |
|---|---|---|---|---|
| `fichas/B1-0-controle.md` | Controle (balanço hídrico) | Ajustar (não aprovado em SC) | 4 / 2 / 2 | 28 |
| `fichas/B1-1-geada-milho-safrinha.md` | Geada no milho safrinha | Aprovada como camada | 3 / 3 / 3 | 30 |
| `fichas/B1-2-chuva-colheita-cebola.md` | Chuva na colheita da cebola | Descartada | 3 / 1 / 1 | 23 |
| `fichas/B1-3-calor-floracao-milho.md` | Calor na floração do milho (reserva 1) | Descartada | 2 / 1 / 1 | 23 |
| `fichas/B1-4-clima-mildio-cebola.md` | Clima de míldio da cebola (reserva 2) | Descartada | 3 / 1 / 1 | 23 |

Nota: depois de escolher a ideia 1, vi que a A1 já inclui a geada do milho safrinha no mapa de época. Por isso B1-1 tem nota 2 em Diferencial e deve ser fundida com A1.
