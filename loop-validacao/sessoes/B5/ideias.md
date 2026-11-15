# B5 · Outra persona ou canal: ideias geradas

Sessão B5 (Trilha B) · 14/11/2026. Frente: quem recebe a informação e por onde (agrônomo, extensionista da Epagri, cooperativa, crédito e seguro, WhatsApp).

| # | Ideia | Persona e canal | Escolhida? | Por quê (uma linha) |
|---|---|---|---|---|
| 1 | **Laudo de perda com dado de satélite para o Proagro e o seguro rural** | Agricultor + agente do banco/perito, PDF ou link no WhatsApp | **Sim (1ª)** | O dinheiro do Proagro e do seguro é a proteção que o agricultor já tem, e dá para testar se o sinal da NASA "vê" os anos de perda contra o IBGE e contra as indenizações públicas. |
| 2 | **Alerta de veranico por WhatsApp (áudio) com a decisão "ensilar cedo ou esperar o grão"** | Produtor de leite e milho do Extremo Oeste, WhatsApp, via extensionista | **Sim (2ª)** | Dá para simular o que ele teria recebido em 40 safras e medir se o aviso chega antes e acerta mais do que o próprio olho dele ("tá sem chover há 15 dias"). |
| 3 | Painel semanal do extensionista com as comunidades e talhões mais em risco | Extensionista da Epagri, painel web | Reserva (3ª) | Bom para escala (um técnico atende muitas famílias), mas com 2 pontos do POWER de ~50 km não há o que ranquear dentro do município; precisaria de Sentinel-2 por talhão. |
| 4 | Ranking de risco pré-safra para a cooperativa planejar insumo e assistência | Cooperativa, planilha ou painel | Não | Sem previsão sazonal na aba Resources, o ranking pré-safra é a climatologia, que é igual todo ano e não muda a decisão de um ano para o outro. |
| 5 | Checagem "estou dentro da janela do ZARC?" antes de pegar o Pronaf | Agente de crédito e agricultor | Não | Usaria o ZARC como entrada, o que quebra a regra 1; e o banco já faz essa checagem no sistema. |
| 6 | Boletim municipal de estiagem para a prefeitura e a Defesa Civil anteciparem o decreto de emergência (que destrava a prorrogação do Pronaf) | Secretaria de Agricultura, e-mail ou painel | Reserva (4ª) | Reaproveita o detector da ideia 1, mas a persona fica longe do agricultor e o decreto depende de política, não só de dado. |

## Ordem de teste
1. Ideia 1 (laudo de perda) → ficha `fichas/B5-1-laudo-perda.md`
2. Ideia 2 (alerta WhatsApp, silagem) → ficha `fichas/B5-2-alerta-whatsapp-silagem.md`
3. Se alguma for descartada: ideia 3, depois a 6.

## Achado de passagem
O código IBGE 4208401 do protocolo é Itapiranga. Ituporanga é 4208500 e São Miguel do Oeste é 4217204. No SIDRA 5457, cebola é o produto 40107 (não 40281). Usei os códigos corretos em `pam_ibge.csv`.

## Resultado (14/11/2026)
| Tentativa | Ideia | Veredito | Problema / Resolve / Validade | Total | Ficha |
|---|---|---|---|---|---|
| 1 | Laudo de perda (Proagro/seguro) | Descartada | 4 / 2 / 2 | 24 | `fichas/B5-1-laudo-perda.md` |
| 2 | Alerta WhatsApp, silagem | Descartada | 4 / 1 / 2 | 23 | `fichas/B5-2-alerta-whatsapp-silagem.md` |
| 3 | Painel do extensionista, cebola | Descartada como produto | 4 / 2 / 3 | 25 | `fichas/B5-3-painel-extensionista-cebola.md` |
| 4 | Boletim de estiagem, prefeitura | Descartada como produto | 3 / 2 / 3 | 27 | `fichas/B5-4-boletim-estiagem-prefeitura.md` |

Achados que servem ao controle: (1) na cebola, o risco é excesso de chuva na primavera, não falta (5 de 6 anos de quebra); (2) o GWETROOT erra menos que a chuva para dizer "estiagem instalada"; (3) durante a safra, o POWER de ~50 km não sabe mais do que o agricultor vê; o valor está antes do plantio; (4) o Proagro já usa satélite e segue o ZARC.
