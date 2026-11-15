<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/harvesty-logo-escuro.svg">
    <img src="assets/harvesty-logo.svg" width="460" alt="Harvesty">
  </picture>
</p>

# Harvesty

App do time para o NASA Space Apps 2026 (desafio Field Shift). O agricultor familiar do Oeste de Santa Catarina desenha a fazenda no mapa, conta o que tem, e o app mostra os riscos daquele lugar, as possibilidades com trade-offs e responde perguntas. Tudo é calculado com dados da NASA: **NASA POWER** (clima diário de 1981 a 2025) e **SRTM** (relevo).

- Versão publicada (artifact do Claude): https://claude.ai/artifact/BGkMxtrbkzzJPTdhyXsfMD
- Versão local: `dist/index.html` (como abrir, abaixo)

---

## Parte 1 · Como usar o app

O app tem 5 etapas. A barra do topo leva a cada uma.

### 1. Delimitar a fazenda
1. O mapa abre com um **sítio de exemplo** (fictício) em São Miguel do Oeste.
2. Clique em **Desenhar minha fazenda**.
3. Use a roda do mouse para dar zoom e arraste para mover até achar a sua área.
4. Clique em cada canto da fazenda. Errou? **Desfazer ponto**.
5. Feche com **Concluir área** ou com dois cliques.

A área fica **salva no seu navegador**: da próxima vez, ela já aparece. Para trocar, é só desenhar de novo.

**Camadas do mapa** (botões acima do mapa):
| Camada | O que mostra | Dado |
|---|---|---|
| Relevo | Sombreado do terreno | SRTM |
| Declive | Classes de relevo da Embrapa (plano a montanhoso) | SRTM, ~90 m |
| Geada no 2º milho | Última data para plantar o 2º milho com até 2 anos em 10 de geada antes da silagem | NASA POWER, por ponto da grade |
| Chuva dez–fev | Chuva do verão escolhido em % do normal (2022 mostra a estiagem) | NASA POWER |

Passe o mouse sobre um município para ver o nome e o valor da camada.

### 2. O que tenho
O app calcula sozinho a **área**, o **município** e o **% de morro** (declive acima de 20%). Você preenche:
- atividade, vacas em lactação, o que planta hoje;
- quando planta o milho de verão e o 2º milho;
- o ciclo do híbrido (precoce, normal, tardio);
- o solo que você vê (ou "não sei": o app estima pelo relevo);
- as 2 prioridades.

Tudo recalcula na hora quando você muda um campo.

### 3. Riscos deste lugar
Cada risco vem num cartão com:
- **nível** (alto, médio, baixo) e o número principal;
- **o dado da NASA diz:** o número e de onde vem;
- **o que fazer:** as mitigações;
- **quanto confiamos:** o resultado da validação, sem enfeite.

Riscos de hoje: geada no 2º milho, geada no milho de verão, verão seco, solo raso nos morros e erosão.

### 4. E se…?
Escolha uma possibilidade e veja a tabela de trade-off (ganha / arrisca / chance):
- **Plantar o 2º milho:** arraste a data e veja a chance de geada mudar.
- **Pôr sorgo na silagem:** quanto melhora o pior ano, conforme o solo.
- **Mudar a data do milho de verão:** chance de geada por mês.
- **Cobrir o solo no inverno:** meses de chuva mais erosiva.

### 5. Pergunte
- Escreva ou clique em **Falar a pergunta** (microfone).
- **Perguntar**: o Claude responde em linguagem simples, usando **só** os números calculados para a sua fazenda. Se a pergunta for sobre preço, praga ou adubo, ele diz que o app não calcula isso.
- **Ouvir a resposta** lê em voz alta. O **resumo por mensagem** embaixo é o que o agricultor receberia no celular, com botão de áudio.

Pergunta, microfone e áudio **só funcionam dentro do claude.ai** (no artifact publicado). Na primeira vez, o claude.ai pede permissão. Na versão local esses botões ficam escondidos ou avisam que não estão disponíveis.

### Dados NASA neste ponto
Embaixo do mapa: temperatura mínima diária do ano, chance de geada pela data de plantio e chuva por mês contra o normal. Troque o **ano** no seletor. O link **Abrir esta série na API da NASA** mostra o dado bruto daquele ponto.

---

## Parte 2 · Para o time (código)

### Estrutura
```
harvesty/
├── src/app.html            o app inteiro (HTML, CSS e JS); os dados entram nas marcas /*__PACOTE__*/ e /*__RELEVO__*/
├── scripts/
│   ├── build.sh            comando único de build
│   ├── baixar_power.sh     baixa o NASA POWER da grade (lista em dados/bruto/power/pontos.txt)
│   ├── gerar_clima.py      POWER -> dados/gerado/pacote.json; roda os módulos do motor de ../solucao/motor em cada célula
│   ├── alinhar_spec_v2.py  registro do patch que alinhou o app à spec v2 (já aplicado; não rodar de novo)
│   ├── gerar_relevo.py     SRTM -> dados/gerado/relevo.json (classes de declive e sombreado em PNG)
│   └── montar.py           injeta os dados no app -> dist/index.html
├── dados/
│   ├── bruto/              o que veio de fora: power/, srtm/, malha e nomes do IBGE (só desenho)
│   └── gerado/             o que os scripts calculam
└── dist/index.html         a página pronta (~4 MB, abre sem internet exceto fontes e D3)
```

### Rodar
```bash
bash harvesty/scripts/build.sh
```
Só remonta a página (segundos). Use depois de mexer em `src/app.html`.

```bash
bash harvesty/scripts/build.sh --dados
```
Recalcula clima e relevo e remonta. Use depois de mexer em `gerar_clima.py` ou `gerar_relevo.py`.

```bash
bash harvesty/scripts/build.sh --baixar
```
Baixa os pontos do POWER que faltarem, recalcula e remonta.

**Abrir localmente:** no Claude Code, peça "abre o harvesty" (servidor `harvesty` em `.claude/launch.json`, porta 8767) ou rode:
```bash
python3 -m http.server 8767 --directory harvesty/dist
```
e abra `http://localhost:8767`.

**Publicar de novo no mesmo link:** peça ao Claude "publica o harvesty". Ele roda o `montar.py` com o caminho do artifact e republica; quem tem o link vê a versão nova na hora.

### Onde mexer em `src/app.html`
| Quero mudar… | Procure |
|---|---|
| Regra de geada (limiar, graus-dia, janela) | `function safra`, `curvaDiaria` (corte de 2 em 10, média de 5 dias) |
| Riscos, textos, níveis e mitigações | `function riscos` |
| Possibilidades do "E se…?" e tabelas de trade-off | `function desenhaCenario` |
| Números do sorgo por solo (vêm da validação V3) | `const SORGO` |
| Mensagem curta para o agricultor | `function mensagem` |
| O que o Claude recebe e como deve responder | `function fatos` e `const prompt` |
| Camadas do mapa e legendas | `function desenhaCamada` |
| Fazenda de exemplo | `const EXEMPLO` |
| Cores e fontes | bloco `:root` no topo do `<style>` |

### Trocar ou ampliar a região
1. **Clima:** edite `dados/bruto/power/pontos.txt` (lat e lon dos centros da grade do POWER, passo 0,5° × 0,625°) e rode `build.sh --baixar`.
2. **Municípios:** troque o código da mesorregião (4201 = Oeste Catarinense) na URL do IBGE e salve em `dados/bruto/malha_oeste.json` e `municipios_oeste.json`.
3. **Relevo:** o `gerar_relevo.py` descobre sozinho as folhas SRTM que cobrem a malha. Baixe as que faltarem (o script avisa quais) de `https://s3.amazonaws.com/elevation-tiles-prod/skadi/S28/S28W053.hgt.gz` (troque o nome) para `dados/bruto/srtm/`.

### De onde vêm os números e quanto valem
O app segue a **spec v2** (`../solucao/spec-v2.md`). Os números de geada e de ano seco **não são reimplementados**: o `gerar_clima.py` importa o motor (`solucao/motor`) e roda os mesmos módulos em cada uma das 20 células. Em São Miguel do Oeste, o resultado é idêntico ao do motor e da spec (geada em 1/ago 6,3 em 10 [4,8–7,6]; 2º milho até 05/02, risco no dia 1,9 [1,0–3,2]; faixas 30/01–07/02 e 25/01–16/02).

| Módulo no app | Nível (spec v2) | Dado | Regra |
|---|---|---|---|
| Geada no 2º milho | N2 · com ressalva | POWER `T2M_MIN`, `T2M_MAX` | mínima ≤ 3 °C entre o plantio e o corte (graus-dia); limite = último dia com até 2 em 10 (média de 5 dias). V2 |
| Geada no milho de verão | N2 · com ressalva | POWER `T2M_MIN` | algum dia < 2 °C nos primeiros 100 dias. V4 |
| Aviso de ano seco | N2 · com ressalva | POWER (chuva, temperatura, umidade, vento, radiação) | balanço de água do milho de 20/set a 10/jan entre os 10% piores dos anos anteriores. V1 |
| Sorgo no talhão raso | N2 só com solo declarado raso; N1 no médio; desligado no fundo | POWER + GAEZ + parâmetros FAO/Embrapa | 7 em 10 cenários ajudam. V3 |
| Confirme o solo | confirme | SRTM (declive > 20%) | só pede para o agricultor confirmar |
| Chuva que arrasta solo | medido | POWER (Fournier) | A3-1 |
| Aveia, sorgo depois do milho | N1 · em teste | — | sem número |

Regras de texto da spec aplicadas: resposta primeiro, sempre anos ruins, "cerca de X de cada 10 anos (entre A e B)", arredondamento R7 ("menos de 1", "quase nunca"), N1 sem número, mensagem do agricultor com até 70 palavras (template T01). O que a spec manda não afirmar está nas instruções que o app manda ao Claude.

Relatórios completos: `../solucao/validacao/V1` a `V7` e `../loop-validacao/RANKING.md`.

### Limites conhecidos
- O clima vem de uma grade de ~55 km: não vê o talhão.
- O relevo cobre o Oeste catarinense inteiro (8 folhas SRTM, longitude −54 a −50, latitude −28 a −26), a ~90 m.
- Solo vem do declive e da resposta do agricultor.
- Sem teste com agricultor ou extensionista ainda.
