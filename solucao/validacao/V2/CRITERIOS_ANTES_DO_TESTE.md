# V2 · Critérios definidos antes de rodar a nova análise

Escritos em 14/11/2026, depois de baixar o POWER dos pontos novos e de ler as fontes externas, mas antes de rodar `v2_geada.py`.
(Já se sabia do B1-1 o resultado de São Miguel do Oeste: limite 1/fev com 3 °C. Isso não é cegueira total. Os critérios abaixo testam o que o B1-1 não testou.)

Definições
- Proxy de geada: `T2M_MIN` do NASA POWER <= L, com L em {2, 3, 4} °C. Caso-base: 3 °C.
- Risco do decêndio = anos com geada entre o plantio e o ponto de silagem / 45 anos (1981-2025), em "anos em 10".
- Ponto de silagem: 1.250 °C·dia base 10 (teto 30 °C), igual ao B1-1. Sensibilidade: 1.100 e 1.400.
- Data-limite = último decêndio de plantio com risco <= 2 em 10.
- Pontos: São Miguel do Oeste, Chapecó (célula do POWER igual à de Xanxerê), Concórdia, Dionísio Cerqueira.

Critérios (cada um passa ou falha)
- C1 Eventos: dos eventos de geada com data e local conferidos em fonte externa (estação INMET/Epagri, não a memória), o proxy a 3 °C marca >= 80% (janela de +-2 dias, no ponto mais próximo).
- C2 Viés do POWER: média mensal de `T2M_MIN` (mai a ago) do POWER em Chapecó fica a <= 1,5 °C da normal 1961-1990 da estação INMET de Chapecó.
- C3 Estabilidade no espaço: a data-limite (3 °C) dos 4 pontos fica dentro de 20 dias entre si.
- C4 Sensibilidade ao limiar: entre 2 e 4 °C, a data-limite de SMO se move <= 20 dias. Se mover mais, a camada depende do limiar e isso entra no veredito.
- C5 ZARC: a data-limite (3 °C) de SMO fica a +-20 dias do fim da janela do ZARC 2026/27 de sorgo forrageiro 2ª safra, ciclo médio (21), em SMO. Não existe ZARC de milho 2ª safra para SC, então é um substituto indireto.
- C6 Degrau: o risco sobe >= 30 pontos percentuais entre 1/jan e 28/fev em cada ponto (3 °C).

Regra do veredito
- "sustenta": C1, C3, C5 e C6 passam, e C4 passa ou a dependência do limiar fica declarada com faixa.
- "parcial": C6 passa, mas falha C1 (por falta de eventos conferidos), C5 ou C3.
- "nao_sustenta": C6 falha, ou o proxy não enxerga as geadas conferidas.
