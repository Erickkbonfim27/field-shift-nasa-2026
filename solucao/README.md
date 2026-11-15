# Field Shift: motor de risco para escolher a rotação

Desafio: *Field Shift: Adapting Farms with NASA Data*, NASA Space Apps 2026.
Estado: protótipo de hackathon, 14/11/2026 (revisado no mesmo dia, depois de uma rodada de revisão). Proposta do time, não produto pronto.

## O que é

Um motor que usa dados da NASA para transformar a incerteza do clima em probabilidades ("em quantos anos de 10 deu errado"). A família agricultora usa isso para escolher a rotação com menos risco.

O motor é **modular**. Cada módulo responde a uma decisão. A região liga os módulos que passaram no teste dela.

- **Santa Catarina** é a região principal. São Miguel do Oeste (leite e milho) abre a demo. Ituporanga (cebola) vem em seguida.
- **Semiárido** (Quixadá, CE) é a segunda região, só milho.
- O balanço hídrico sozinho **não** é o produto em SC. Ele empata com a chuva bruta (ρ 0,28 contra 0,23 no milho de SMO; ficha B1-0 e `spec-v2.md`, seção 0). Em SC pesam a geada e o ano extremo.

Duas saídas por local:

1. **WhatsApp simulado** para o produtor: áudio, cartão de 10 sacos e texto curto.
2. **Auditoria** para o técnico: cada número liga ao dado, ao parâmetro e ao script que o gerou.

O modelo de linguagem não faz conta. Só transcreve e lê texto pronto. Nenhum número sai dele.

## Como rodar

Da raiz do projeto (`nasa-space-apps/`). Precisa de Python 3. O `numpy` só é usado para ler o `.npz` do Sentinel-2 (Ituporanga). Não precisa de `pip install`.

```bash
# 1. Gera as 3 saídas e valida (cerca de 9 s)
python3 solucao/motor/gerar.py

# 2. Testes (79 testes, cerca de 16 s)
python3 -m unittest discover solucao/motor/tests

# 3. Valida qualquer saída contra o contrato e as regras R1 a R15
python3 solucao/motor/validador.py solucao/saida/*.json

# 4. Abre a UI (não abre por file://, a página usa fetch)
python3 -m http.server 8765 --directory solucao
```

Depois abra `http://localhost:8765/ui/escolher.html` (escolhe local e pergunta) ou `http://localhost:8765/ui/index.html?local=sao-miguel-do-oeste&pergunta=ano-seco`.

Locais: `sao-miguel-do-oeste`, `ituporanga`, `quixada`.

`gerar.py` sai com código 1 se alguma saída for inválida. A única diferença entre duas execuções é o campo `gerado_em` (conferido em 14/11/2026: o arquivo `saida/calculos/*.json` sai idêntico).

## Pastas

| Caminho | O que tem |
|---|---|
| `motor/` | Código do motor (Python, só biblioteca padrão). `gerar.py` é a entrada. |
| `motor/locais/` | Um arquivo por local da demo, mais `fora_da_area.py` (responde "não sei"). |
| `motor/tests/` | Testes: ET0, balanço, geada, alerta, contrato, aceitação, revisão (`TestRevisao`). |
| `motor/validador.py` | Valida o JSON contra o schema e as regras R1 a R15. |
| `contrato.schema.json` | Contrato v2.1.0 da saída do motor. A 2.1.0 acrescentou `fonte.categoria = literatura_externa`, `fonte.nome = Embrapa` e `limites[].trecho`. |
| `spec-v2.md` | Spec da solução (v2). Substitui a v1 do Semiárido. |
| `exemplo_saida.json` | Cópia da saída do motor para São Miguel do Oeste (era escrito à mão e ficou desatualizado). A UI cai nele se faltar a saída do motor. |
| `saida/<local>.json` | Saída do motor, no contrato. É o que a UI lê. |
| `saida/calculos/<local>.json` | Séries e tabelas intermediárias. Cada chave é citada no rastro. |
| `ui/` | HTML, CSS e JS puros. Sem build, sem biblioteca externa. |
| `validacao/V1` a `V7` | Frentes de validação, cada uma com critério escrito antes, scripts e relatório. A V1 ganhou o passo 6 (`v1_passo6_so_passado.py`), que valida o alerta com o percentil só do passado. |

## De onde vem cada dado

Regra do desafio: na **solução** entram só recursos da aba Resources. Fontes externas servem para entender o problema ou **conferir** o resultado. O validador faz valer isso de dois jeitos (regra R2):

1. Nenhum cálculo do produto tem fonte externa nas entradas, direta ou indireta.
2. Nenhuma variável de cartão do WhatsApp chega, **pelos ponteiros até o rastro**, a uma fonte externa nem a um cálculo de validação.

Há **duas exceções declaradas**. Elas existem hoje e o time precisa aceitar ou trocar:

- **Cálculo de validação** `R-CALC-ALERTA-VALID`. Lê o IBGE PAM para medir se o alerta de ano seco acerta. Fica marcado `parametros.so_auditoria = true`. A frase de probabilidade ("em anos assim, 4 em 10") ficou **só na auditoria**. O WhatsApp não a leva mais (antes levava, e o validador não pegava).
- **Três parâmetros de literatura externa** (categoria `literatura_externa`, tipo `parametro`): R = 0,88 (silagem do sorgo vale 88% da de milho; Embrapa Gado de Leite e Demarchi), raiz de 0,6 m do solo raso (ZARC, Portaria 236) e limiar de geada de 2 °C (ZARC, Portaria 236). Cada um tem item no rastro.

### Entrada (cálculo)

| Dado | Origem | Onde no código |
|---|---|---|
| Chuva, temperatura, umidade, vento, radiação diários | NASA POWER, 1981–2025 (Quixadá 2001–2025) | `motor/power.py`; arquivos em `loop-validacao/dados/` e `prototipo/dados/` |
| Relevo e declive | SRTM 30 m | `validacao/V3/res_06_srtm.json`, `motor/exposicao.py` |
| Cobertura do solo (exposição) | Sentinel-2 | `loop-validacao/sessoes/A3/a3_1_blocos.npz`, lido com `numpy` |
| Água disponível do solo por textura | GAEZ: 65, 125 e 175 mm/m. **O talhão "raso ou com pedra" usa os 65 mm/m da classe areia**, sem teste (o GAEZ não mede profundidade; V3) | `motor/config.py`, `motor/locais/` |
| Coeficientes fixos | Método publicado: FAO-56 (ET0, balanço) e FAO-33 (Ky) | `motor/balanco.py` |
| Respostas do produtor (solo, prioridade, talhão) | Pergunta no WhatsApp | campo `produtor` e `talhao` |
| **Parâmetros de literatura externa (exceção)** | R = 0,88; raiz 0,6 m do solo raso; limiar de geada 2 °C | `R-PARAM-R-SORGO`, `R-PARAM-RAIZ-RASO`, `R-PARAM-LIMIAR-GEADA` no rastro |

### Só conferência (nunca entrada)

ZARC (MAPA), IBGE PAM, Epagri, Garantia-Safra. Aparecem na UI com o selo "conferência, não entrada" e em `conferencias[]` do JSON.

### Dados baixados fora do motor

- `loop-validacao/dados/power_*.json` e `prototipo/dados/power_quixada.json` foram baixados com `curl` da API do POWER.
- O motor lê arquivos de `loop-validacao/` e `prototipo/`. A pasta `solucao/` sozinha não roda. Mova o projeto inteiro.

## O que o motor entrega

Os números abaixo vêm de `saida/<local>.json`. Cada um tem rastro. Cada estratégia tem **um número de tipo diferente**. Não é um ranking.

**São Miguel do Oeste** (replay de 25/01/2022): 4 estratégias, 1 alerta ativo, 6 cartões do WhatsApp.
- Alerta de ano seco ativo: ISNA 0,618 em 2021/22, percentil 0 entre 32 anos passados (1990–2021). No WhatsApp: "entre os 10% piores dos últimos 32 anos", sem número de acerto.
- Segundo milho (geada): plantando até **5 de fevereiro**, a geada chega antes do corte da silagem em cerca de 2 de cada 10 anos (média de 5 dias 1,9; IC95 1,0 a 3,2). Em 11/fev, 4,4 em 10 (3,1 a 5,9). A falta de água do 2º milho **não foi calculada**, e as mensagens dizem isso.
- Metade em sorgo no talhão raso (CAD 39 mm): a mistura ajuda o ano ruim em 67,4% dos 270 cenários (7 em cada 10), abaixo do corte de 70%. Mediana da grade +15,4% no pior ano em 10 (de −7,4% a +76,3%); central do motor +46,9% (IC95 31,1 a 60,8). **O WhatsApp só diz "7 em cada 10 cenários"**. As porcentagens ficam na auditoria. Fica N2.

**Ituporanga** (replay de 02/09/2024): só a estratégia atual tem número. O solo ficou 97% descoberto em julho de 2024 (média do recorte: 65%). O talhão é de **demonstração**, não de produtor real. As outras 2 estratégias saem "em teste", dentro do cartão de comparação (T01).

**Quixadá** (operação em 05/01/2026): milho na 1ª chuva firme, quebra em cerca de 4 de cada 10 anos (IC95 2,0 a 5,5). Milho em meados de fevereiro, 2 de cada 10 (0,9 a 3,9). Os IC95 se sobrepõem, então a mensagem diz "tende a ser melhor, mas não é certo". Caupi e sorgo saem "em teste". O caupi bate com o ZARC em 16 de 18 decêndios, mas isso é do caupi (N1), não do milho; ver "O que foi validado".

**Fora da área testada:** responde "não sei" sem número (testado com Irecê e Passo Fundo).

## O que foi validado

Cada frente escreveu o critério antes de rodar. Relatórios em `validacao/V*/relatorio.md`.

| Frente | Pergunta | Veredito |
|---|---|---|
| V1 | Alerta de ano extremo (B3-3) segura fora da amostra? | O limiar fixo **não sustenta**. A regra relativa ("10% mais secos da própria célula") com o percentil só do passado (a que o motor roda, passo 6): 13 de 29 alertas em ano ruim (45%) contra 16% de base, mas só **4 de 9 eventos** (2 de 6 novos), recall 48%. **Falha C1** (44% dos eventos, abaixo de 50%) e **C3** (rendimento relativo médio 0,884, acima de 0,85); passa C2 (p = 0,078 com o corte do passo 6). Com anos futuros no percentil (passo 4) eram 14 de 32 e 4 de 11 eventos, 2 de 8 novos. O motor usa a regra relativa, com a ressalva de que pega pouco. |
| V2 | Camada de geada no Oeste de SC | **Parcial.** |
| V3 | Sorgo como seguro da silagem | **Parcial.** Sobrevive em 68,5% da grade com CAD 42 mm (corte 70%). Com o CAD de 39 mm, o motor mede 67,4%. Com 39 mm a mistura rende mais em 35 de 41 safras e menos de 0,02 em 2 (com 87,5 mm eram 18 e 15). |
| V4 | Motor composto como explicador do rendimento | **Não passa** como explicador. O "x em 10" passa só para 3 decisões: tirar agosto da janela do milho, alerta de ano extremo (a regra relativa, com as ressalvas da V1), "x em 10" da cebola. |
| V5 | Balanço hídrico no Semiárido | **Parcial.** Critério pré-registrado, 16 pares: mediana 0,414 (corte 0,40). **Na mesma escala:** Quixadá 0,50 (chuva bruta 0,46) contra SMO 0,28 (chuva 0,23). A mediana 0,615 do milho em 6 municípios é um **recorte feito depois de ver a Bahia falhar** e não deve ser comparada com o 0,28 de um só município. Não supera a soma de chuva. Bahia fica fora (ρ 0,07). |
| V6 | ZARC como gabarito em SC | Serve de conferência. A forma bate, a magnitude da geada não (63% do POWER contra 40% do ZARC em 1/ago). |
| V7 | Aderência ao desafio e concorrentes | Ver relatório. |

**Nenhum módulo chega a N3 (validado).** O mais forte é a geada que tira agosto da janela do milho de verão, hoje **N2**: o teste D1 da V4 foi num ponto só (SMO), sem amostra nova, com o critério escrito já com os 40% do ZARC na mão; o limiar de 2 °C vem do próprio ZARC, que também usa o POWER na ET0, então a concordância não é independente; e a magnitude discorda. A V6 propôs calibrar o limiar contra o ZARC. Isso não foi feito.

**O 16 de 18 do ZARC não é evidência do milho.** É do caupi, que sai "em teste". A métrica é frouxa (conta como acerto toda falha menor ou igual ao nível do ZARC). Dentro dos 8 decêndios que o ZARC indica a ordem do motor não bate com a do ZARC (Spearman −0,07; a chuva média do decêndio dá 0,64). Um calendário ingênuo (os 8 decêndios mais chuvosos do POWER) acerta 12 de 18. Está em `K-ZARC-CAUPI`.

### Testes desta integração (14/11/2026, depois da revisão)

- `gerar.py`: 3 saídas válidas contra o contrato e R1 a R15, rastro conferido (cada script e arquivo citado existe).
- 79 testes unitários e de aceitação passam (19 testes novos, 18 deles em `TestRevisao`: R2 pelos ponteiros, faixa N2, polaridade dos sacos, vírgula decimal, trecho dos limites, fim da janela do alerta, parâmetros externos, toda pergunta da UI com cartão).
- `validador.py` passa nas 3 saídas e no `exemplo_saida.json`.
- Validador testado ao contrário: campo faltando, tipo errado, campo extra e enum inválido são recusados; cada regra nova tem um teste que a faz falhar.
- `node --check` em `app.js`, `comum.js`, `graficos.js`, `escolher.js`: sem erro de sintaxe.
- UI com **DOM falso em Node** (não em navegador): 3 locais × 9 perguntas × 7 abas × cada cartão. Nenhum "undefined", "NaN" ou "null", toda variável do cartão achada no texto, palavras declaradas = contadas, toda pergunta com cartão. Isso **não** substitui o navegador. A rodada anterior fez 165 cliques em navegador e conferiu duas capturas; **esta rodada não repetiu isso** (o servidor local novo foi bloqueado). A tela larga e o tema claro continuam sem conferência visual.
- O texto dos cartões foi relido a olho, mas **nunca testado com agricultor**.

## O que não foi validado

Leia antes de apresentar.

1. **Nenhum teste com produtor nem com técnico.** A legibilidade foi avaliada só por nós. Contraste WCAG e leitor de tela não foram testados. As mensagens foram reescritas para responder a pergunta primeiro e definir os termos, mas isso também não foi testado com gente.
2. **O balanço hídrico não passou em SC** como explicador do rendimento (V4). O motor não o vende como tal.
3. **Nenhum módulo é N3.** A geada que tira agosto é N2 (um ponto, limiar do ZARC, magnitude discorda; limiar não calibrado). Os módulos de água do milho e o ISNA em SC são N1/N2.
4. **A mistura com sorgo no solo raso está abaixo do corte de 70%** (67,4% com CAD 39 mm). Fica N2 porque a spec manda. O WhatsApp só diz "7 em cada 10 cenários" e "a conta não é firme". Se isso basta para o pitch é decisão do time.
5. **O alerta de ano seco só aparece depois que a seca já começou.** Com data de referência 1/dez/2021 ele ficaria inativo (percentil 28,1). Em 25/01/2022 está ativo. É um resultado negativo sobre antecedência. A conferência `K-PAM-A` de 2022 usa uma safra que **já estava na amostra** da B3: não é teste novo.
6. **O alerta falha C1 e C3 da V1** (4 de 9 eventos; rendimento relativo médio 0,884). Os números de acerto (45%, "4 em 10") vêm do IBGE PAM e **não vão mais ao WhatsApp**. Ficam na auditoria. O T06 (sem aviso) diz só que o aviso "deixou passar muitas quebras".
7. **Replay usa anos posteriores à data de referência** nas tabelas de geada (1981–2025) e na mistura. Só o percentil do alerta usa apenas anos passados. Está declarado no limite `X-REPLAY`.
8. **Área testada é uma caixa de latitude e longitude** (`motor/config.py`, `REGIOES`). Concórdia cai dentro do Extremo Oeste, mas tem data-limite de geada muito diferente (V2). Falta a correção de altitude pelo SRTM.
9. **Ituporanga:** uma estratégia com número. O histórico de primaveras extremas (1997, 2008, 2015, 2023) vai só para a auditoria como N1 (T09). A pergunta "Como foram as chuvas da primavera?" saiu da demo.
10. **Semiárido:** só 25 anos de dados. Feijão fraco (ρ 0,31). O T12 (prioridade) tem opções de SC e **não sai** em Quixadá (limite `X-T12-SC`). Os IC95 do milho se sobrepõem.
11. **Parâmetros de literatura externa** (R = 0,88, raiz de 0,6 m, limiar de 2 °C, mais o fator 0,3 de perda por geada da A4, sem fonte própria) são uma **exceção à regra de dados**. O time decide se aceita. Se não aceitar, a mistura e a geada da janela de verão precisam ser refeitas.
12. **O IC95 do bootstrap da mistura** usa o gerador da biblioteca padrão e difere um pouco da V3 (que usou numpy). O valor central é igual. Com 39 mm o central sobe cerca de 7 pontos contra os 42 mm da V3 (46,9% contra 39,6%).
13. **Pacote `jsonschema` não está instalado.** O validador é nosso e cobre só as palavras do schema que o contrato usa. Não foi comparado com um validador independente.
14. **Voz do áudio** é a do navegador (`speechSynthesis`). A qualidade não foi testada. O roteiro troca "km" por "quilômetros".
15. **Canal do técnico:** as mensagens mandam "falar com o técnico da assistência técnica do seu município", sem nome nem telefone. Falta o contato real da ATER de cada lugar.
16. **Não implementado:** API `POST /motor/v2/avaliar` e `GET /saidas/{id}` (spec 7.5), tela da fila do técnico (spec, tela 6), gravação do ponto "fora da área" em `saida/`, `motor.commit` (a pasta não é repositório git).
17. **Pendências abertas da spec:** P4 (Ky do sorgo por NDVI), P5 (água do 2º milho), P7 (Niño 3.4 do ERA5), P8 (IMERG e SMAP), P10 (teste com produtores), P11 (calibrar o limiar de geada contra o ZARC), P12 (decidir a exceção dos parâmetros de literatura), P13 (contato da ATER). Um arquivo de ZARC da B1 (`zarc_smo_itu_full.csv`) veio com 0 bytes e foi descartado pela V6; a conferência usa o CSV da A1.
18. **Atalhos do contrato:** o T06 e o T10 apontam para o rótulo do indicador em vez de um campo próprio (`meses`). O T09 também.

## Regras de produto que o motor impõe

- **R2:** fonte externa não entra em cálculo do produto, e nenhuma variável de cartão do WhatsApp chega a ela pelo rastro. Só o cálculo de validação (`so_auditoria`) pode ler a PAM.
- **R4:** o nível de evidência decide como o número aparece. N1 nunca põe número no WhatsApp. Número N2 que tem intervalo sai **com a faixa no mesmo cartão** ("entre 1 e 3"); o validador confere. Número medido sem intervalo (solo descoberto, fração de cenários) sai sem faixa, com a frase do que não foi medido.
- **R6:** o percentil do alerta usa só anos passados.
- **R7:** "x em 10" e sacos como na spec; o número de cada saco rasgado aparece no texto (mesma polaridade: sempre anos ruins).
- **R8:** todo número do texto tem variável e ponteiro no JSON. Sem ponteiro, o validador recusa.
- **R9:** a prioridade do produtor muda só a ordem dos cartões, nunca o cálculo (testado gerando duas vezes).
- **R13:** vírgula decimal em todo texto de módulos, estratégias, limites e conferências.
- **R14:** limite que "vai ao produtor" traz o `trecho` exato num cartão do WhatsApp.
- **R15:** o fim da janela do alerta é o fim que o índice usou (o aviso de 15/12 não diz "até 10 de janeiro").
- Toda comparação inclui a estratégia atual ("o de sempre").
- O WhatsApp diz sempre "anos ruins" ("quebra", "geada antes do corte"), nunca "boa colheita" em um lugar e "quebra" em outro.
- Texto com vírgula decimal. O roteiro do áudio sai com os números por extenso.
