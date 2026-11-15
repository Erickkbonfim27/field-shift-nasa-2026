# B2 · Solo e conservação: ideias geradas

Sessão B2 (Trilha B). 14/11/2026. Fora de escopo por já estarem na Trilha A: alerta de erosão e nota de saúde do solo (A3), planta de cobertura (A5).

| # | Ideia | Região | Dado oficial | Escolhida? | Por quê |
|---|---|---|---|---|---|
| 1 | **Detector de solo descoberto (plantio direto x convencional) por satélite:** contar quantas vezes o talhão aparece de solo nu, sem palha, na entressafra | ambas | Sentinel-2 (NDVI e índice de palha NDTI, bandas SWIR) | **Sim, 1ª** | Dá para testar com o Censo Agro 2017, que traz quem usa plantio convencional por município; é o manejo que mais pesa na conservação do solo em SC e vira prova para crédito e seguro (ABC+, ZARC por níveis de manejo) |
| 2 | **Calendário de pisoteio no leite:** dias de solo encharcado demais para pôr o gado na aveia de inverno (ou entrar com máquina na silagem), para evitar compactação | São Miguel do Oeste | NASA POWER (GWETTOP, chuva) | **Sim, 2ª** | Ataca a região do leite e a integração lavoura-pecuária (aveia no inverno, milho no verão); usa só dado já baixado. Risco conhecido: o agricultor vê o barro, então o ganho pode ser pequeno |
| 3 | **Rotação por declive (SRTM):** decidir quais talhões recebem cebola (lavoura revolvida) e quais ficam com pasto ou perene | Ituporanga | SRTM 30 m + Sentinel-2 | Reserva | Muda a rotação no espaço, mas encosta muito no alerta de erosão da A3 (declive é a mesma entrada) |
| 4 | **Palhada na cebola:** medir a palha que cobre o solo no transplante (jun–ago), base do plantio direto de hortaliças da Epagri | Ituporanga | Sentinel-2 (NDTI) | Não, vira parte da 1 | É o mesmo sinal da ideia 1 recortado para a cebola; entra como resultado da 1 |
| 5 | **Perda de matéria orgânica pela cor do solo nu** | ambas | Sentinel-2 / Landsat | Não | Sem dado de campo para validar na regra 1, e encosta na nota de saúde do solo da A3 |
| 6 | **APP e nascentes com SRTM:** linhas de drenagem e faixa de 30 m que não deve ser plantada | ambas | SRTM | Não | O CAR já faz isso; quase não muda a rotação e o SRTM de 30 m erra nascente pequena |

## O que foi testado (resultado)
| Ficha | Ideia | Veredito | Problema real / Resolve / Validade | Total |
|---|---|---|---|---|
| B2-1 | Solo descoberto, 18 municípios | Ajustar | 4 / 2 / 2 | 27 |
| B2-2 | Calendário de pisoteio | Descartada | 3 / 2 / 2 | 25 |
| B2-3 | Solo descoberto, máscara ajustada | Descartada | 4 / 1 / 2 | 24 |
| B2-4 | Solo descoberto, replicação em 32 municípios do Oeste | Descartada | 4 / 1 / 1 | 23 |

- **Por que a ideia 3 (declive SRTM) não foi testada:** a A3 já usa o declive do SRTM no alerta de erosão e na nota de saúde do solo. As tentativas 3 e 4 foram gastas para fechar a pergunta da ideia 1, que estava "em parte".
- **Achado colateral:** o GWETTOP do POWER tem deriva entre décadas (ficha B2-2). O aviso está na pasta de notas.
