# B1-4 · Clima favorável ao míldio da cebola

Sessão: B1 · Trilha: B · Região: Ituporanga · Tentativa 4 de 4 · Data: 2026-11-14

## 1. Ideia (escrita antes do teste)
Critérios escritos depois de descartar B1-3 e antes de rodar este teste (`sessoes/B1/CRITERIOS_ANTES_DO_TESTE.md`).
- **Hipótese:** dias úmidos e frescos (condição do míldio, *Peronospora destructor*) de agosto a outubro explicam os anos ruins da cebola melhor que o balanço hídrico. O risco muda com a data de transplante.
- **Problema que ataca (e para quem):** o agricultor familiar de cebola de Ituporanga, que perde lavoura para doença foliar em primaveras úmidas [INFERÊNCIA].
- **Decisão que muda:** a data de transplante, a cultivar e o plano de pulverização preventiva.
- **Critério de sucesso (definido antes):**
  - C1: ρ ≤ −0,35 entre os dias favoráveis (`RH2M` ≥ 85%, `T2M` entre 10 e 22 °C, chuva ≥ 1 mm, de 1/ago a 31/out) e a PAM sem tendência.
  - C2: ≥ 4 de 8 piores anos acertados.
  - C3: a chance de ano "muito favorável" varia ≥ 2 em 10 entre transplantes em 1/jun, 1/jul e 1/ago.
- **Linha de base:** média dos anos e o controle B1-0 na cebola (ρ = 0,13; 1 de 8).

## 2. Teste
- **Dados oficiais usados:** NASA POWER diário, `RH2M`, `T2M` e `PRECTOTCORR`, 1981–2025.
- **Método:** conta os dias favoráveis por ano e por janela de transplante (do dia 15 ao dia 105 após o transplante). Sensibilidade com `RH2M` ≥ 90%. Script: `sessoes/B1/b1_4_mildio_cebola.py`.
- **Resultado (n = 42)** [CÁLCULO]:
  - **Com `RH2M` ≥ 85%:** ρ = **−0,06** (p = 0,36). Acerta **3 de 8** (1996, 2008 e 2015). A média é de 35 dias favoráveis por ano (de 17 a 63).
  - **Com `RH2M` ≥ 90%:** ρ = −0,12 (p = 0,23). Acerta 3 de 8.
  - **C3 (85%):** a chance de ano "muito favorável" é de 1,3 em 10 com transplante em 1/jun, 2,9 em 1/jul e 4,7 em 1/ago. Com 90%, fica entre 2,4 e 3,1 (sem diferença).
- **Gráfico:** `sessoes/B1/b1_4_mildio_x_pam.svg` mostra a nuvem sem inclinação.

## 3. Validação
- **Contra a linha de base:** acerta mais piores anos que o controle (3 contra 1 de 8), mas a correlação não se distingue da média (p de 0,23 a 0,36).
- **Fonte externa:** IBGE PAM, tabela 5457, cebola de Ituporanga (4208500 / 40107) [DADO]. Não há série pública de incidência de míldio ano a ano para conferir.
- **O critério de sucesso foi atingido?** **Não.** C1 não (−0,06); C2 não (3 de 8); C3 só com 85%.

## 4. Régua (1 a 5)
| Critério | Nota | Por quê (uma frase) |
|---|---|---|
| Problema real | 3 | O míldio é uma doença importante da cebola em SC [INFERÊNCIA], mas aqui não aparece na PAM. |
| Tamanho do impacto | 3 | Município inteiro de cebola, mas sem número de perda por doença. |
| Resolve de fato | 1 | Não separa os anos ruins. |
| Validade | 1 | Não supera a média. |
| Muda a decisão | 2 | Só com o limiar de 85% a data de transplante muda o risco. |
| Simples e factível | 4 | Três variáveis do POWER. |
| Alinhamento com o desafio | 2 | É manejo de doença, longe de rotação. |
| Diferencial | 3 | Ninguém mais olha doença. |
| Cabe no hackathon | 4 | Simples. |
| **Total (máx. 45)** | **23** | |

Aprovada só com 3+ em problema real, resolve de fato e validade. **Não passa.**

## 5. Veredito
**Descartada.** O índice de clima de míldio do POWER não explica os anos ruins da cebola na PAM. Sem um gabarito de doença ano a ano, não há como provar o valor.

## 6. Relação com o controle
Não compete. É a terceira prova de que, na cebola de Ituporanga, o clima diário do POWER não explica a variação da PAM (ver B1-0 e B1-2).

## 7. Limites e o que não foi testado
- O `RH2M` diário é uma média do dia; o míldio depende das horas de molhamento foliar à noite, que o POWER diário não dá.
- A PAM é um gabarito ruidoso e não separa perda por doença.
- Os limiares da doença são estimativas de manual, não calibradas para SC.

## 8. Fontes
- NASA POWER (ver B1-0). Resultados: `sessoes/B1/b1_4_resultado.json`.
- IBGE SIDRA, tabela 5457 (ver B1-2).
