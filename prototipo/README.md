# Protótipo: duas abordagens de layout

Município: Quixadá (CE). Dados reais do NASA POWER (2001–2025). Spec em [../spec-solucao.md](../spec-solucao.md).

## Como abrir
```bash
python3 -m http.server 8765 --directory prototipo
```
Depois abra `http://localhost:8765/a.html` e `b.html`. Para recalcular o modelo: `python3 prototipo/modelo/risco.py`.

## Arquivos
- `modelo/risco.py`: balanço hídrico e chance de colher. Gera `dados/resultado.json`.
- `dados/power_quixada.json`: série diária baixada da API do NASA POWER.
- `a.html`: **A · Conversa primeiro**. Simulação do WhatsApp à esquerda, painel de auditoria à direita.
- `b.html`: **B · Calendário primeiro**. Resposta em forma de janela de plantio, com a auditoria recolhida embaixo.

## O que foi testado
- **Funcional:** as duas páginas abrem sem erro no console; cliques nas opções, abas e escolha de cultura funcionam; layout de 375 px de largura (celular) sem rolagem horizontal.
- **Cálculos na tela:** o "16 de 18 decêndios consistentes" é calculado no navegador e bate com a conta feita à mão.
- **Legibilidade:** avaliada por mim com os critérios abaixo. **Não foi feito teste com agricultor nem com técnico.** Esse é o teste que falta.

## Comparação

| Critério | A · Conversa | B · Calendário |
|---|---|---|
| Responde "planto agora ou espero?" | **Não.** Responde qual cultura é melhor, não quando plantar | **Sim.** A janela (11 de fev a 20 de mar) é o título |
| Cartão simples para quem tem pouca escolaridade | Sim: número grande e 10 sacos por opção | O título e os sacos servem; o gráfico de 18 barras é denso |
| Mostra o canal real (áudio, localização, WhatsApp) | Sim | Só a prévia da mensagem |
| Auditoria rastreável | Sim: painel fixo, com cada número da mensagem ligado à tabela de 25 anos | Sim, mas escondida em "Auditoria" recolhida |
| Compara 3 ou mais estratégias (pedido do desafio) | Sim, no cartão | Sim, em lista |
| Mostra a divergência com o ZARC | Só na aba Validação | **Sim, em aviso na própria janela** |
| Serve de demo para o júri | Sim, conta uma história | Sim, mostra o raciocínio |

## Achados do teste
1. **A resposta do WhatsApp da abordagem A erra a pergunta.** O agricultor pergunta se planta agora; a mensagem fala de cultura. Corrigir: a mensagem deve começar pela janela.
2. **A janela do modelo difere da do ZARC.** Para o caupi, o modelo vê chance de 8 em 10 de 11/fev a 20/mar. O ZARC dá o menor risco só em 11 a 31/mar. Como o crédito e o seguro seguem o ZARC, a tela precisa avisar (a B já avisa).
3. **A "primeira chuva" é arriscada.** Milho e caupi plantados na chuva de janeiro dão 6 em 10; a janela de meados de fevereiro dá 8 em 10. É o "falso começo" medido pela primeira vez neste projeto.
4. **Esperar não serve para tudo.** Milho plantado em 11/mar (ciclo de 100 dias) não melhora (6,4 em 10), porque a chuva acaba antes da maturação. O caupi (70 dias) ganha com a espera (8,0 contra 7,6).
5. **O sorgo aparece como mais seguro (9 em 10).** Isso vem em parte dos parâmetros genéricos (Ky baixo na floração), então é uma hipótese, não um achado. Conferir com a portaria do ZARC.

## Recomendação: juntar as duas
- **WhatsApp (de A):** áudio e cartão de sacos, mas a mensagem abre com a janela de B ("plante entre 11/fev e 20/mar") e depois compara as culturas.
- **Auditoria (de A):** painel fixo ao lado, com o gráfico de janelas de B e o aviso do ZARC no topo.
- **Cartão de sacos de B** no cabeçalho da auditoria, para o técnico ver a mesma resposta que o agricultor ouviu.

## Limites
Ver a seção 8 da [spec](../spec-solucao.md). Os principais: chuva de grade grossa, solo informado e não medido, parâmetros genéricos, rotação não calculada e nenhum teste com usuário.
