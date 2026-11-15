# B1-3 · Calor na floração do milho

Sessão: B1 · Trilha: B · Região: São Miguel do Oeste · Tentativa 3 de 4 · Data: 2026-11-14

## 1. Ideia (escrita antes do teste)
Critérios escritos depois de descartar B1-2 e antes de rodar este teste (`sessoes/B1/CRITERIOS_ANTES_DO_TESTE.md`).
- **Hipótese:** dias de calor na floração derrubam o milho além do que a falta de água explica. Um índice de calor somado ao controle acerta mais anos ruins.
- **Problema que ataca (e para quem):** o produtor de milho e silagem do Extremo Oeste, nos verões quentes.
- **Decisão que muda:** a data de plantio, para deslocar a floração para fora do pico de calor.
- **Critério de sucesso (definido antes):**
  - C1: ρ ≤ −0,35 entre os dias com `T2M_MAX` ≥ 32 °C nos dias 55 a 80 após o plantio (20/set) e a PAM sem tendência.
  - C2: correlação parcial (descontado o controle) ≤ −0,25, e o índice combinado acerta ≥ 5 de 8.
  - C3: a chance de ≥ 3 dias de calor varia ≥ 2 em 10 entre as datas de plantio.
- **Linha de base:** média dos anos e o controle B1-0 (ρ = 0,28; 3 de 8).

## 2. Teste
- **Dados oficiais usados:** NASA POWER diário, `T2M_MAX`, 1984–2025, grade de ~50 km.
- **Método:**
  - Conta os dias com calor na janela de floração.
  - Calcula a correlação parcial descontando o rendimento simulado do controle.
  - Índice combinado = controle × (1 − 5% por dia de calor).
  - Sensibilidade com o limiar de 34 °C.
  - Script: `sessoes/B1/b1_3_calor_floracao.py`.
- **Resultado (n = 41)** [CÁLCULO]:
  - **Com 32 °C:** ρ = **+0,20** (sinal ao contrário: mais calor, rendimento maior); parcial = +0,33. Acerta 2 de 8 sozinho e 2 de 8 combinado com o controle (ρ do combinado = 0,09). Há calor em 16 de 41 anos, com média de 2,3 dias.
  - **Com 34 °C:** ρ = +0,12; parcial = +0,26; acerta 2 de 8 sozinho e 3 de 8 combinado.
  - **C3:** a chance de ≥ 3 dias de calor (≥ 32 °C) vai de 0,5 em 10 (plantio em agosto) a 4,6 em 10 (plantio em 11/nov).
  - O calor anda junto com a falta de água do modelo (ρ de −0,34 com o controle), mas não com o rendimento real.
- **Gráfico:** `sessoes/B1/b1_3_calor_x_pam.svg` mostra que os anos ruins da PAM (1991, 2005 e 2012) tiveram poucos dias de calor na janela.

## 3. Validação
- **Contra a linha de base:** pior que a média (sinal invertido) e pior que o controle (2 de 8 contra 3 de 8).
- **Fonte externa:** IBGE PAM, tabela 5457, milho de São Miguel do Oeste [DADO]. A portaria do ZARC milho SC 2026/27 avalia frio (e não calor) como risco térmico [DADO], o que é coerente com o calor não ser o fator limitante ali.
- **O critério de sucesso foi atingido?** **Não.** C1 não; C2 não; só o C3 passou (a data muda a exposição ao calor, mas o calor não muda o rendimento).

## 4. Régua (1 a 5)
| Critério | Nota | Por quê (uma frase) |
|---|---|---|
| Problema real | 2 | Nos dados, o calor na floração não aparece como causa de quebra em São Miguel do Oeste. |
| Tamanho do impacto | 2 | Mesmo se existisse, viria junto com a seca, que o controle já cobre. |
| Resolve de fato | 1 | Não separa anos bons de ruins. |
| Validade | 1 | O sinal vai na direção contrária e não supera a média. |
| Muda a decisão | 2 | A data muda a exposição ao calor (C3), mas sem efeito no rendimento. |
| Simples e factível | 5 | Uma variável do POWER. |
| Alinhamento com o desafio | 3 | Clima e época. |
| Diferencial | 2 | Quase uma parte do controle. |
| Cabe no hackathon | 5 | Trivial. |
| **Total (máx. 45)** | **23** | |

Aprovada só com 3+ em problema real, resolve de fato e validade. **Não passa.**

## 5. Veredito
**Descartada.** No Extremo Oeste de SC, o calor na floração medido pelo POWER não explica as quebras do milho; o sinal é até invertido.

## 6. Relação com o controle
Não agrega ao controle (o índice combinado ficou pior). Não entra na demo.

## 7. Limites e o que não foi testado
- A grade suaviza os picos: o `T2M_MAX` de dez–fev tem p90 de 33,1 °C e p99 de 37,1 °C [CÁLCULO]; a estação pode registrar 2 a 3 °C a mais.
- A janela de floração é fixa (dias 55–80) e não acompanha o ciclo do híbrido; não usamos graus-dia.
- Não testado: o ECOSTRESS (temperatura da folha), que seria a medida certa de estresse por calor.

## 8. Fontes
- NASA POWER (ver B1-0). Resultados: `sessoes/B1/b1_3_resultado.json`.
- IBGE SIDRA, tabela 5457; MAPA, Portaria SPA/MAPA nº 236/2026 (ver B1-0).
