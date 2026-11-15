# Spec da solução: chance de colher, por WhatsApp, com auditoria

Atualizado em 14/11/2026. Versão 0.1, feita por mim a partir do grill (resolvido sem o time) e do [contexto.md](contexto.md). **As respostas abaixo são propostas, não decisões do time.** O Miro não foi relido para esta versão (limite diário de chamadas do plano gratuito); o board entra pelo resumo do contexto.md.

## 1. Promessa
> Usamos dados da NASA para transformar a incerteza do clima em probabilidades, para que o agricultor familiar escolha o que plantar, e quando, com menos risco de perder a safra.

- **Gancho:** a chance de colher esta safra, em "x de cada 10 anos".
- **Segunda promessa (solo melhor no ano seguinte):** fica como hipótese. O protótipo **não calcula** o efeito da rotação sobre o solo. Só aparece como texto marcado "a validar".
- "Qualidade" e "eficiência" saíram da frase por não terem medida. Se o time quiser mantê-las, precisa definir o indicador (ex.: água guardada, nitrogênio).

## 2. Grill resolvido

| # | Pergunta | Resposta adotada | Por quê |
|---|---|---|---|
| Q1 | Promessa principal | Risco de perda primeiro, solo depois | É o que o agricultor sente e o que dá para medir com os dados da aba |
| Q2 | Quem usa o frontend | Intermediário (ATER, sindicato, cooperativa) como usuário real; júri na demo | A informação chega ao agricultor por alguém de confiança |
| Q3 | Município da demo | Quixadá (CE) | Já temos o ZARC conferido e há vários tipos de solo no município |
| Q4 | ZARC entra? | Só como gabarito de validação, mais os dias de cada fase quando a FAO não tiver | Respeita a regra 1 no modelo; decisão final é do time |
| Q5 | Real ou simulado | Modelo real; WhatsApp simulado na demo, sandbox para vídeo | Número aprovado da Meta leva dias |
| Q6 | Formatos | Entrada: áudio, localização, foto (só como registro). Saída: áudio curto + imagem-cartão | Foto sem diagnóstico evita prometer o que a NASA não mede |
| Q7 | Como mostrar a chance | "x de cada 10 anos" com 10 sacos; percentual só na auditoria | Frequência em número inteiro é mais fácil de entender |
| Q8 | Horizonte | Safra atual, com 4 a 5 estratégias | Plano de anos fica fora do que dá para calcular |
| Q9 | Papel do LLM | Transcreve o áudio e lê em voz alta números que o modelo já calculou (templates) | Nenhuma probabilidade vem do LLM, então a auditoria é real |

Decisões novas do grill resolvido:
- **Definição de "colher":** rendimento relativo de pelo menos 60% (perda menor que 40%, o mesmo corte do Garantia-Safra, aplicado por talhão). É uma escolha minha; o time deve confirmar.
- **Quando plantar no cálculo "o de sempre":** primeira chuva que passa na regra de Sivakumar (20 mm em 3 dias, sem mais de 7 dias secos nos 30 seguintes).
- **Quando o sistema não sabe:** diz "não sei" e chama o intermediário (ver seção 7).

## 3. Arquitetura

```
 Agricultor (WhatsApp)                    Intermediário (web)
   áudio / localização / foto               tela de auditoria
          │                                        ▲
          ▼                                        │ lê
  [1] Entrada: áudio → texto (STT)          [5] Registro de cada resposta:
  [2] Entende: intenção, cultura, local         números, parâmetros, fontes
          │                                        ▲
          ▼                                        │ grava
  [3] Modelo de risco (determinístico) ───────────┘
       balanço hídrico por fase, 25 anos de dados NASA
          │
          ▼
  [4] Resposta: template + voz (TTS) + imagem-cartão (10 sacos)
```

- **Camada 3 é a única que calcula.** O LLM só atua em 1, 2 e 4.
- **Cada resposta grava** (camada 5): estratégia, parâmetros, anos simulados, fontes. A tela de auditoria só lê esse registro.

## 4. Dados NASA usados

| Dado | Para quê | Status no protótipo |
|---|---|---|
| NASA POWER (chuva `PRECTOTCORR`, temperatura, umidade, vento, radiação) | Chuva diária e evapotranspiração de referência (Penman-Monteith FAO-56) | **Usado de verdade**, Quixadá, 2001–2025 |
| GPM IMERG | Chuva mais fina e alerta durante a safra | Não usado: o POWER diário voltou vazio e o acesso direto pede login Earthdata |
| SMAP | Umidade do solo no plantio e na safra | Não usado (login Earthdata). No protótipo o solo inicial vem do próprio balanço |
| FAO GAEZ v5 | Água disponível por textura e profundidade de raiz | Valores copiados da tabela (areia 65, médio 125, argila 175 mm/m) |
| Sentinel-2 / Landsat | NDVI do talhão: lavoura nasceu? anos ruins? | Não usado. É a validação mais forte que falta |

## 5. O que o protótipo calcula

Para cada ano de 2001 a 2025 e cada estratégia: balanço hídrico diário do plantio à maturação, com ETc = Kc × ET0, solo como um balde (CAD = água por metro × raiz), relação ETa/ETc por fase e rendimento relativo pelo método FAO-33 (Ky por fase). A "chance de colher" é a fração dos 25 anos com rendimento relativo de 60% ou mais.

Código: [prototipo/modelo/risco.py](prototipo/modelo/risco.py). Resultado: `prototipo/dados/resultado.json`.

**Parâmetros são aproximações da FAO-56 e FAO-33, não os do ZARC.** Sorgo e caupi ainda precisam ser conferidos nas portarias.

## 6. Validação (feita na primeira rodada, sem ajuste de parâmetros depois do resultado)

1. **Contra o ZARC** (caupi, grupo I, sequeiro, solo médio, Quixadá, 2026/27): no ZARC, "risco de 20%" significa que a perda passa do limite em até 20% dos anos. Nosso modelo é consistente em **16 de 18 decêndios** de plantio. Os dois que discordam ficam no fim da janela (21–31/mar e 1–10/abr), onde somos mais pessimistas.
2. **Contra anos de seca conhecidos no Ceará** (2001, 2010, 2012 a 2017, 2019): o rendimento médio simulado cai bastante nesses anos em relação aos demais (por exemplo, milho na 1ª chuva: 0,50 contra 0,84).
3. **Divergência a tratar:** para o caupi, o modelo vê chance de 8 em 10 de 11/fev a 20/mar, e o ZARC dá o menor risco só em 11 a 31/mar. Como crédito e seguro seguem o ZARC, a ferramenta deve avisar quando a data sugerida ficar fora da janela do ZARC.
4. **Ainda falta:** NDVI do Sentinel-2/Landsat no mesmo município, Garantia-Safra pago por ano e rendimento do IBGE PAM.

## 7. Quando o sistema diz "não sei"
- Local fora da área testada, ou sem dado.
- Cultura que não está no modelo (hoje: milho, caupi, sorgo).
- Pergunta sobre praga, doença, adubo ou preço: a ferramenta responde que não calcula isso e **encaminha ao intermediário**.
- Foto: só guarda como registro, sem diagnóstico.

## 8. Limites que o pitch precisa assumir
1. **Chuva em grade grossa.** O POWER diário usa uma grade de cerca de 50 km. O IMERG (10 km) ainda não entrou. Um município pode ter chuva local bem diferente.
2. **Solo não medido no talhão.** Vem da resposta do agricultor (arenoso, médio, argiloso), não de medição.
3. **Kc e Ky são genéricos.** A forma da curva da cultura no Semiárido não foi calibrada.
4. **Rotação ainda não modelada.** O efeito no solo do ano seguinte é hipótese.
5. **Chance, não garantia.** Praga, semente, mão de obra e mercado ficam de fora. O sorgo, por exemplo, só vale se houver comprador.
6. **Sem teste com agricultor.** Os layouts foram avaliados por critérios de legibilidade, não com usuários reais.
7. **2025 sem plantio no modelo.** Pela chuva da reanálise (405 mm de janeiro a maio), nenhuma chuva firmou. Isso deve ser conferido com pluviômetro da Funceme antes de ser mostrado.

## 9. Decisões que ficam para o time
1. A definição de "colher" (60% do rendimento) serve?
2. ZARC só como validação, ou também como parâmetro?
3. Entra SMAP/IMERG com login Earthdata? (Fortalece o uso de NASA; custa tempo.)
4. Persona e público: agricultor sozinho, ou com intermediário na tela?
5. Qual abordagem de layout seguir. O teste sugere juntar as duas: WhatsApp da abordagem A com a mensagem abrindo pela janela de plantio da B (ver [prototipo/README.md](prototipo/README.md)).
6. A ferramenta pode sugerir uma data fora da janela do ZARC? Se sim, com qual aviso?
