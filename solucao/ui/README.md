# UI do Field Shift (WhatsApp simulado + auditoria)

HTML, CSS e JS puros. Sem build e sem biblioteca externa. Lê só o JSON do contrato v2.1 (`../contrato.schema.json`). Não calcula resultado.

## Como abrir
```bash
python3 -m http.server 8765 --directory solucao
```
Abra `http://localhost:8765/ui/escolher.html` (tela 2: local e pergunta) ou `http://localhost:8765/ui/index.html` (tela 1). Não abre por `file://`, porque a página busca o JSON com `fetch`.

## Telas
- `escolher.html`: escolhe o local (São Miguel do Oeste, Ituporanga, Quixadá) e a pergunta. Leva para `index.html?local=...&pergunta=...`.
- `index.html`: WhatsApp do agricultor (áudio com transcrição, localização, cartão de 10 sacos, texto) ao lado do painel do técnico (Mensagem, Estratégias, Gráficos, Validação, Limites, Rastro, Glossário). Os seletores de local e pergunta também ficam no topo.

## De onde vêm os dados
1. `../saida/<local>.json`, com `<local>` = `sao-miguel-do-oeste`, `ituporanga` ou `quixada`.
2. Se não existir (ou não for contrato v2), cai para `../exemplo_saida.json` e mostra a faixa "Dados de exemplo".

## Como a pergunta abre a mensagem
A pergunta só escolhe qual cartão (`template_id`) aparece primeiro. A lista de preferência está em `comum.js` (`LOCAIS`). Se a saída não tem cartão do WhatsApp para a pergunta, a UI avisa e não inventa resposta. Os outros cartões ficam atrás de "Ver mais". O teste `test_toda_pergunta_da_ui_tem_cartao` lê `LOCAIS` e confere que cada pergunta acha um cartão (a pergunta de chuva da primavera de Ituporanga saiu: o T09 é N1 e só vai à auditoria).

## Arquivos
- `comum.js`: locais, perguntas, rótulos dos enums, glossário (`GLOSSARIO`, `SIGLAS`, `rico()`), leitura do JSON, tema.
- `graficos.js`: SVG à mão (10 sacos, barras relativas, risco por decêndio com IC95 e ZARC, métricas de mistura, posição do alerta, faixa de indicador, calendário de plantio).
- `app.js`: WhatsApp, abas da auditoria, painel "de onde vem este número" (segue o ponteiro de `cartoes[].variaveis` até `rastro[]`).
- `escolher.js`, `app.css`.

## Limites desta versão
- As 3 saídas (`sao-miguel-do-oeste`, `ituporanga`, `quixada`) são geradas por `python3 solucao/motor/gerar.py`. Se faltar alguma, a UI cai no exemplo e avisa. Integração testada em 14/11/2026 com um DOM falso em Node (não em navegador): 3 locais, 9 perguntas, 7 abas, cada cartão. Sem "undefined", sem "NaN", toda variável do cartão achada no texto.
- Cartões com `imagem.tipo = nenhuma` (T05, T06, T07, T10, T12) saem só com áudio e texto. Isso é esperado. O T07 perdeu as barras: o índice sem unidade confundia.
- Siglas nos textos do técnico (IC95, ZARC, CAD, Ky, ISNA, decêndio, P10...) vêm com `abbr` e explicação ao passar o mouse; V1 a V7 ligam ao relatório da frente. O Glossário é uma aba.
- A aba Limites mostra, para os limites que vão ao produtor, a frase exata que está na mensagem (`limites[].trecho`).
- O áudio usa a voz do navegador (`speechSynthesis`, pt-BR) para ler `audio.roteiro`. Se o navegador não tiver voz, abre o texto do roteiro.
- A tela 6 da spec (fila do técnico) não foi feita.
- Nenhum teste com agricultor ou técnico.
