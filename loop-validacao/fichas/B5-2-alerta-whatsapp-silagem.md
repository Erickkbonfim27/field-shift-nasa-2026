# B5-2 · Alerta de veranico por WhatsApp: ensilar cedo ou esperar o grão

Sessão: B5 · Trilha: B · Região: São Miguel do Oeste (leite e milho) · Tentativa 2 de 4 · Data: 2026-11-14

## 1. Ideia (escrita antes do teste)
- **Hipótese:** um alerta por WhatsApp (áudio curto + cartão), calculado com a umidade do solo e a chuva do NASA POWER, avisa o produtor de leite que o milho de verão vai quebrar a tempo de ele mudar o destino da lavoura (ensilar a planta inteira antes que ela seque, ou garantir volumoso), e acerta mais do que a percepção dele mesmo.
- **Problema que ataca (e para quem):** no Extremo Oeste, o milho é a comida do rebanho leiteiro. Numa estiagem, quem espera o grão perde o grão e a silagem. A família descobre tarde e compra volumoso caro ou vende vaca.
- **Decisão que muda:** no aviso, ensilar o milho (ou parte dele) para não perder a massa verde, e reservar/comprar volumoso cedo; sem aviso, esperar o grão.
- **Critério de sucesso (definido antes):**
  - Plantio de referência em 1º de outubro (milho de verão, ciclo de ~130 dias); data de decisão até o dia 80 após o plantio (cerca de 20 de dezembro), quando ainda dá para ensilar.
  - Ano de perda = rendimento do milho do IBGE/PAM abaixo de 70% da tendência de 1990–2024.
  - O alerta, emitido até o dia 80, acerta pelo menos **70% dos anos de perda** com **no máximo 1 alarme falso a cada 10 anos** e com **30 dias ou mais de antecedência** em relação à colheita do grão.
  - No máximo **3 mensagens por safra** em média (para não virar ruído).
  - Tem de superar a linha de base "olho do agricultor" (15 dias seguidos sem chuva relevante até o dia 80) em precisão ou acerto.
- **Linha de base:** (1) não ter alerta: ele descobre na colheita, antecedência zero; (2) a regra "15 dias sem chuva", que ele percebe sozinho.

## 2. Teste
- **Dados oficiais usados:** NASA POWER diário (comunidade AG), ponto -26,725; -53,518 (~50 km): `PRECTOTCORR`, `T2M`, `T2M_MAX`, `T2M_MIN`, `RH2M`, `WS2M`, `ALLSKY_SFC_SW_DWN` (para a ET0 de Penman-Monteith FAO-56) e `GWETROOT`; safras 1985–2025, avaliadas em 1990–2024. [DADO]
- **Método:** Script `sessoes/B5/modelo_milho.py` (reaproveita o balanço hídrico de `prototipo/modelo/risco.py`) e `sessoes/B5/avaliar.py`.
  1. Balanço hídrico diário do milho (Kc e fases da FAO-56, Ky da FAO-33, CAD de 125 mm, balde cheio 60 dias antes do plantio).
  2. **Alerta** = água útil no solo abaixo de 40% por 10 dias seguidos entre os dias 45 e 80 após o plantio (pré-pendão até o início do enchimento). Uma mensagem por episódio.
  3. **Olho do agricultor** = 15 dias seguidos com chuva abaixo de 5 mm/dia entre o plantio e o dia 80.
  4. Comparação com os anos de perda do IBGE/PAM. Simulação das mensagens em `sessoes/B5/mensagens_simuladas.md`.
- **Resultado:** [CÁLCULO]
  - Anos de perda no IBGE/PAM: 1991, 2002, 2012, 2021 e 2022 (5 de 35).
  - **Alerta do modelo:** 8 safras com alerta; **acerta 2 dos 5 anos de perda (40%)**, com **6 alarmes falsos (precisão de 25%)**, ou 1,7 alarme falso a cada 10 anos.
  - **Olho do agricultor:** 11 safras; acerta os mesmos 2 (40%), com 9 falsos (18%).
  - **Antecedência:** nos anos acertados, o alerta sai 50 a 55 dias antes da colheita do grão; mas, em todos os anos em que os dois dispararam, **o olho do agricultor disparou antes** (1 a 13 dias; em 2012, 07/12 contra 20/12).
  - **Mensagens:** 0,23 por safra (bem abaixo do limite de 3).
  - Sensibilidade com solo argiloso (CAD de 175 mm): 3 alertas, 1 acerto, 2 falsos; o resultado não melhora.
- **Gráfico:** `sessoes/B5/grafico_b5_2_alerta.svg`. As marcas do alerta e do olho caem nos mesmos anos ruins (2012 e 2022) e erram juntas em 1996, 1999, 2000, 2009 e 2019.

## 3. Validação
- **Contra a linha de base:** alerta 2 de 5 e precisão de 25%, contra olho do agricultor 2 de 5 e 18%; acaso, 14%. O alerta só ganha em alarmes falsos (6 contra 9) e **chega depois** do olho. Contra "não ter alerta" ganha 50 dias de antecedência, mas essa antecedência o agricultor já tem sozinho. [CÁLCULO]
- **Fonte externa:**
  - **Proagro do milho no município (BCB), safras 2014–2025:** anos de indenização alta (10% ou mais dos contratos) foram 2021, 2022, 2023 e 2024. O alerta acerta 2 de 4 (1 falso, em 2019); o olho do agricultor, 1 de 4 (2 falsos). Aqui o alerta vai um pouco melhor, mas em 12 safras e com o corte escolhido depois de ver a tabela. [CÁLCULO] (`sessoes/B5/resultado_proagro.txt`)
  - **O canal alcança a família?** Em SC, 50,5% dos estabelecimentos tinham internet em 2017 (São Miguel do Oeste: 55,2%) [DADO, IBGE Censo Agro 2017, tab. 6962]; 77% da população rural do Brasil usa internet em 2025 [DADO, Cetic.br TIC Domicílios 2025]; 59% dos agricultores ouvidos usam WhatsApp ou Facebook para informação [DADO, Embrapa/Sebrae/INPE 2020, 504 entrevistas]. A Epagri tem cerca de 635 extensionistas para ~120 mil famílias (≈190 famílias por técnico) [DADO, Epagri 2019], e 47,9% dos estabelecimentos de São Miguel do Oeste recebem orientação técnica [DADO, Censo Agro 2017, tab. 6779]. O canal existe; o que falha é o conteúdo.
  - As três safras perdidas sem alerta (1991, 2002, 2021) tiveram a seca forte fora da janela dos dias 45 a 80: em 2020/21 a estiagem foi na primavera, antes do pendão. [INFERÊNCIA]
- **O critério de sucesso foi atingido?** **Não.** Acerto de 40% (meta 70%) e 1,7 alarme falso a cada 10 anos (meta: 1). Antecedência e número de mensagens, sim, mas sem vantagem sobre o olho do agricultor.

## 4. Régua (1 a 5)
| Critério | Nota | Por quê (uma frase) |
|---|---|---|
| Problema real | 4 | A estiagem de 2021/22 derrubou o milho do município a 41% da tendência, e o milho é o volumoso do leite. |
| Tamanho do impacto | 3 | Pega a renda do leite de muitas famílias do Oeste, mas a decisão de ensilar cedo é de poucos dias e de parte da área. |
| Resolve de fato | 1 | O alerta não acerta mais e chega depois do que o agricultor já percebe olhando o céu. |
| Validade | 2 | Testado com dado oficial em 35 safras, mas o sinal não supera a linha de base do olho do agricultor. |
| Muda a decisão | 1 | Na simulação, nenhuma safra em que ele teria decidido diferente por causa da mensagem e não por conta própria. |
| Simples e factível | 4 | O balanço hídrico já existe; o WhatsApp do protótipo do Semiárido serve de casca. |
| Alinhamento com o desafio | 2 | É acompanhamento na safra; não compara estratégias de rotação. |
| Diferencial | 2 | Alertas de estiagem por mensagem já existem (Epagri/Ciram, cooperativas); o nosso não é melhor. |
| Cabe no hackathon | 4 | Pronto em poucas horas com o protótipo existente. |
| **Total (máx. 45)** | **23** | |

Aprovada só com 3+ em problema real, resolve de fato e validade.

## 5. Veredito
**Descartada.** Com a grade de ~50 km e só o POWER, o alerta não sabe mais do que o agricultor sabe sozinho: acerta os mesmos anos, chega depois e erra mais do que a meta.

## 6. Relação com o controle
Não compete. Mostra um limite que vale para o controle: **durante a safra**, o dado da NASA de grade grossa não dá vantagem sobre a percepção local. O valor do dado está **antes do plantio** (comparar estratégias com a série de 40 anos) e não no alerta em tempo real. O canal (WhatsApp, áudio) continua bom para entregar a resposta do controle; o conteúdo do alerta é que não se sustenta.

## 7. Limites e o que não foi testado
- Grade do POWER de ~50 km; a chuva de verão no Oeste é de pancada e muda de uma comunidade para outra.
- O IBGE/PAM mede o milho grão do município, não a silagem; a decisão testada é sobre silagem. A PAM municipal tem valores repetidos e estimados.
- Um só plantio de referência (1º/out); quem planta em agosto ou setembro teria outra janela.
- Sem SMAP nem IMERG (pedem login Earthdata); com chuva de ~10 km e solo de 9 km o alerta talvez ficasse melhor. Não testado.
- Não testado com produtor de leite: se ele ensilaria cedo por causa de uma mensagem, e quanto vale a silagem salva.

## 8. Fontes
- NASA POWER, API diária, comunidade AG (arquivo `dados/power_sao_miguel_do_oeste.json`).
- IBGE, PAM, tabela 5457, São Miguel do Oeste 4217204, milho 40122: https://apisidra.ibge.gov.br/values/t/5457/n6/4217204/v/112,216,8331/p/1990-2024/c782/40122
- FAO-56 (Kc, ET0) e FAO-33 (Ky), como parâmetros fixos, iguais aos do protótipo.
- Proagro, Matriz de Dados do Proagro (BCB): https://www.bcb.gov.br/estabilidadefinanceira/proagro (recorte em `sessoes/B5/externo/proagro_mdpro_SMO_Ituporanga_por_ano_produto.csv`).
- IBGE, Censo Agro 2017, tabelas 6962 (internet) e 6779 (orientação técnica): https://sidra.ibge.gov.br/tabela/6962 e https://sidra.ibge.gov.br/tabela/6779
- Cetic.br, TIC Domicílios 2025: https://cetic.br/media/analises/tic_domicilios_2025_principais_resultados.pdf
- Embrapa/Sebrae/INPE, Agricultura Digital no Brasil (2020): https://eventos.telesintese.com.br/wp-content/uploads/2020/09/joaci-medeiros.pdf
- Epagri, balanço social 2019: https://docweb.epagri.sc.gov.br/pub/DOC_45529.pdf
