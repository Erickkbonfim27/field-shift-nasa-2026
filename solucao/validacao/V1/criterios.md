# V1 · Critérios definidos ANTES de rodar

Escrito em 14/11/2026, depois de só reproduzir B3-3 (`v1_passo1_reproduz.py`, deu os mesmos números da ficha) e antes de qualquer teste novo. Não mudo este arquivo depois de rodar. Se algo mudar, anoto como desvio no `relatorio.md`.

## O que estou testando
A regra da ficha B3-3, **sem mexer**:
- Milho: alerta de seca se ISNA de 20/set a 10/jan < 0,75 (plantio 20/set, solo de 125 mm).
- Cebola: alerta de excesso se o excedente de 1/set a 30/nov ≥ 360 mm (transplante 1/ago, raiz 0,3 m).
- "Ano ruim": rendimento da microrregião (IBGE PAM, tabela 1612) ≤ 85% da mediana de t−3 a t+3 (sem t).
- Safras 1990–2025.

## Parte A: ataques à ficha B3-3 (dados que ela já usou)
Cada ataque diz antes o que conta como "derrubou".

| # | Ataque | Como | Derruba se |
|---|---|---|---|
| A1 | Vazamento do limiar | Comparar 0,75 e 360 mm com o limiar que o próprio B3-1/B3-2 escolheria pela regra objetiva (Peirce, todos os anos). Rodar B3-3 com esse limiar objetivo e com uma regra neutra que não olha o rendimento: "10% mais secos (ou úmidos) da própria célula, 1990–2025". | Com o limiar objetivo ou com a regra neutra, B3-3 deixa de passar no próprio critério (≥ 50% dos alertas em ano ruim e ≥ 2× a taxa-base). |
| A2 | Sensibilidade do limiar | Varrer ISNA de 0,70 a 0,80 (passo 0,01) e excedente de 300 a 420 mm (passo 10). | O critério de B3-3 falha em algum vizinho imediato (±0,02 ou ±20 mm). |
| A3 | Corte de "ano ruim" | Repetir com corte de 0,80 e 0,90, e com mediana de t−5 a t+5. | O critério falha em 2 ou mais das 3 variantes. |
| A4 | Dependência | (a) Spearman ano a ano do indicador entre as células de B3-3 e as da amostra (SMO, Ituporanga). (b) Spearman do rendimento relativo entre microrregiões. (c) Quantos anos de alerta de B3-3 são anos que **não** eram de alerta na amostra (eventos novos). | Não derruba sozinho. Se (c) = 0, B3-3 vale como "outra região", não como "outro evento", e o intervalo tem de ser por evento. |
| A5 | Intervalo por evento | Contar cada ano de safra com alerta como **um** evento, juntando as regiões. Acerto do evento = metade ou mais das regiões que alertaram naquele ano tiveram ano ruim. IC 95% de Wilson sobre os eventos. Valor-p por permutação conjunta dos anos (o mesmo sorteio de anos para todas as regiões, o que preserva a dependência espacial), 10 mil sorteios. | Não derruba sozinho; é a medida honesta que vai no veredito. |
| A6 | Concorrente simples | A mesma regra neutra (10% extremos da célula) aplicada à chuva bruta (nov–dez no milho; set–nov na cebola). | Não derruba o alerta. Se a chuva bruta empatar ou ganhar, o "módulo de água" não agrega sobre a chuva. |

## Parte B: extensão fora da amostra (células novas)
**Escolha das regiões (regra fixa, sem olhar rendimento):**
- Microrregiões de SC que **não** foram usadas (usadas: 42001, 42002, 42005, 42011, 42014, 42017).
- Milho, candidatas: 42003 Xanxerê, 42004 Joaçaba, 42006 Canoinhas, 42009 Curitibanos, 42010 Campos de Lages, 42018 Tubarão, 42019 Criciúma, 42020 Araranguá.
- Cebola, candidatas: todas as microrregiões não usadas com cebola plantada em ≥ 20 dos anos 1990–2025.
- Ponto do POWER: sede do município com maior área plantada da cultura na microrregião (média 2015–2023, IBGE PAM). Isso só escolhe o lugar; o rendimento não é olhado.
- Uma região só entra se: tem rendimento em ≥ 20 safras de 1990–2025; e a chuva diária do POWER não é igual (diferença < 0,01 mm) em mais de 50% dos dias a nenhuma célula já usada (SMO, Ituporanga, Chapecó, Concórdia, Rio do Sul) nem a outra candidata já aceita (a de maior área fica).
- Mínimo: 4 células novas no milho. Se não der, digo.

**Critério de sucesso por cultura (só células novas):**
- C0: pelo menos 3 eventos de alerta (anos distintos). Senão: **inconclusivo**.
- C1: acerto por evento ≥ 50% e ≥ 2× a taxa-base (fração de anos-região ruins nas mesmas regiões).
- C2: valor-p da permutação conjunta dos anos ≤ 0,10 (unilateral).
- C3: rendimento relativo médio dos anos-região com alerta ≤ 0,85.
- Veredito da cultura: **sustenta** se C0 a C3 passam; **parcial** se C1 passa e C2 ou C3 falha; **não sustenta** se C1 falha.

**Leituras extras (não mudam o veredito, só informam):**
- Mesmas contas com a regra neutra (10% extremos da célula).
- Recall: fração dos anos-região ruins que tiveram alerta.
- Separar eventos "já vistos" (anos que alertavam na amostra B3-1/B3-2/B3-3) de eventos novos.

## Veredito da frente V1
- **sustenta**: B3-3 não cai em A1–A3 e a extensão do milho dá "sustenta" (e a da cebola não dá "não sustenta", se houver).
- **parcial**: cai em algum ataque, mas a extensão mostra acerto acima da taxa-base (C1) em pelo menos uma cultura.
- **não sustenta**: a extensão dá "não sustenta" no milho, ou o sinal some com a regra neutra e com o limiar objetivo.
