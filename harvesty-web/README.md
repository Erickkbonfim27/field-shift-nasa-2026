# Harvesty web

Versão full-stack do Harvesty em Next.js 15 (App Router). Faz o mesmo que o app estático em `../harvesty`, mas com os cálculos no servidor, as fazendas guardadas em um banco e a pergunta livre respondida pela API do Claude.

## Como rodar

Requisitos: Node 22.13 ou mais novo (o banco usa o `node:sqlite`, que já vem no Node).

```bash
npm install
npm run dev
```

Abra `http://localhost:3000`.

A aba **Pergunte** usa o Claude. Para ligar, copie `.env.example` para `.env.local` e preencha `ANTHROPIC_API_KEY`. Sem a chave, o resto do app funciona e a pergunta avisa que não está configurada.

Para produção: `npm run build` e `npm start`.

## Como usar

1. **Delimitar a fazenda.** Clique em “Desenhar minha fazenda”, marque os cantos no mapa e feche com dois cliques ou “Concluir área”. O app abre com um sítio fictício em São Miguel do Oeste.
2. **O que tenho.** Preencha atividade, culturas, datas de plantio, ciclo do híbrido e o solo que você vê. Dê um nome e clique em “Salvar fazenda”: ela fica no banco e volta na próxima visita.
3. **Riscos.** Cada risco mostra o nível de evidência (N2, N1, medido, confirme), o que o dado da NASA diz, o que fazer e o que não sabemos.
4. **E se…?** Compare caminhos: 2º milho (com régua de data), sorgo na silagem, data do milho de verão e cobertura do solo no inverno.
5. **Pergunte.** Escreva ou fale a pergunta (o ditado e a leitura em voz alta usam o próprio navegador; o ditado funciona no Chrome e no Edge). O Claude recebe só os números que o motor calculou para a sua área e explica; ele não calcula nada.

No mapa, as camadas se acumulam: relevo e declive (SRTM), geada no 2º milho (quadrado) e chuva de dez–fev do ano escolhido (círculo).

## Como está montado

```
src/app/page.tsx                 página (servidor) que entrega o app
src/components/                  interface: mapa, perfil, fazendas, riscos, cenários, gráficos, pergunta
src/lib/mapa-d3.ts               mapa em D3 (zoom, desenho, camadas)
src/lib/server/                  só no servidor
  dados.ts                       lê a grade do NASA POWER (data/celulas.json)
  modelo.ts                      contas de geada e chuva, as mesmas do motor em Python
  relevo.ts                      classes de declive do SRTM dentro da área
  analise.ts                     junta tudo: riscos, cenários e a mensagem curta (até 70 palavras)
  db.ts                          banco SQLite das fazendas (data/harvesty.db, criado sozinho)
src/app/api/
  analise                        POST { poligono, perfil } -> análise completa
  camadas                        GET ?ano&gdd -> valores por ponto da grade para o mapa
  celulas/[id]/ano/[ano]         GET -> séries do ano para os gráficos
  fazendas, fazendas/[id]        listar, criar, abrir, alterar e apagar fazendas
  perguntar                      POST { pergunta, poligono, perfil } -> resposta do Claude em texto contínuo
```

Os números que vêm do motor em Python (data-limite do 2º milho, faixas, curva de geada, aviso de ano seco) já estão em `data/celulas.json`. As contas que dependem da escolha do agricultor (data de plantio, ciclo, ano) são refeitas no servidor com as mesmas regras.

## Atualizar os dados

Os arquivos em `data/` e `public/` são gerados a partir do pipeline do app estático:

```bash
# na raiz do repositório
bash harvesty/scripts/build.sh --baixar     # baixa NASA POWER e SRTM e recalcula (demora)
python3 harvesty/scripts/exportar_web.py    # escreve data/ e public/ deste app
```

## Limites

Os mesmos do app estático: a grade do clima tem cerca de 55 km e não vê o talhão; o solo vem do relevo e da resposta do agricultor, não de análise; nenhum módulo é N3 (validado). É chance, não garantia.
