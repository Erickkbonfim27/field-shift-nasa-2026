# B5-2 · O que o produtor de leite de São Miguel do Oeste teria recebido

Simulação com o NASA POWER (1990–2024), plantio de referência em 1º/out, regra do alerta: água útil no solo abaixo de 40% por 10 dias seguidos entre os dias 45 e 80 após o plantio. Script: `modelo_milho.py` e `avaliar.py`. [CÁLCULO]

## Safra 2011/12 (IBGE: 50% da tendência, ano de perda)
- **07/12/2011:** o próprio agricultor já está há 15 dias sem chuva acima de 5 mm (regra "olho do agricultor").
- **20/12/2011, mensagem do alerta (dia 80):**
  > Seu Antônio, o solo da sua região está seco há 10 dias, bem na hora do pendão do milho. Em anos assim, o grão quebrou forte. Se o milho é para o gado, vale ensilar a planta inteira antes que seque. Quer falar com o técnico da Epagri? Responda 1.
- **Antecedência até a colheita do grão (dia ~130):** 50 dias. Mas **13 dias depois** do que ele já percebia sozinho.

## Safra 2021/22 (IBGE: 41% da tendência, ano de perda)
- **14/12/2021:** regra do olho dispara.
- **15/12/2021:** alerta do modelo. Um dia depois do olho.

## Safra 2020/21 (IBGE: 67% da tendência, ano de perda): **sem alerta**
- A seca forte foi na primavera (setembro a novembro de 2020), antes do dia 45, quando a regra ainda não olha. O milho plantado em setembro sofreu mais (y simulado 0,66 na média dos plantios contra 0,79 no de 1º/out).

## Safra 2022/23 (IBGE: 104% da tendência): **alarme falso**
- **19/12/2022:** alerta do modelo; o grão do município ficou na tendência. Quem ensilou cedo teria perdido o valor do grão.

## Contagem 1990–2024
- 8 alertas em 35 safras (0,23 mensagem por safra), 2 em anos de perda, 6 em anos sem perda; 3 dos 5 anos de perda sem alerta.
- Em **todos** os anos em que o modelo e o olho dispararam, o olho disparou **antes** (1 a 15 dias).
