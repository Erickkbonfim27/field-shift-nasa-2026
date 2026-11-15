# Protocolo comum do loop de validação (Field Shift, NASA Space Apps 2026)

Todas as 10 sessões seguem este arquivo. Não mude este arquivo; se discordar de algo, anote na sua ficha.

## Por que
Saber se a ideia atual do time é a melhor e se entrega valor real, testando ideias com o mesmo processo e a mesma régua.

**Ideia atual (o "controle"):** usar dados da NASA para transformar a incerteza do clima em probabilidades, para que o agricultor familiar escolha a rotação que reduz o risco de perdas e melhora a qualidade, a eficiência e a sustentabilidade da terra.

Contexto do projeto: `../contexto.md` (seções 0 a 0.3), `../spec-solucao.md` e `../prototipo/` (balanço hídrico já feito para Quixadá, em `../prototipo/modelo/risco.py`, reaproveitável). **Atenção:** o protótipo anterior foi para o Semiárido. Este loop testa em **Santa Catarina**.

## Regiões de teste
| Região | Coordenada usada | Atividade | Código IBGE |
|---|---|---|---|
| Ituporanga (Alto Vale do Itajaí) | -27,414; -49,601 | cebola | 4208500 |
| São Miguel do Oeste (Extremo Oeste) | -26,725; -53,518 | leite e milho | 4217204 |

> **Correção (14/11, aviso da sessão A3):** a primeira versão deste arquivo trazia 4208401, que é **Itapiranga**, não Ituporanga. Quem já puxou IBGE com esse código precisa refazer.

## O loop (igual para todas)
1. **Ideia:** hipótese, problema que ataca e **critério de sucesso definido antes do teste** (escreva na ficha antes de rodar qualquer dado).
2. **Teste:** com os dados oficiais do desafio.
3. **Validação:** comparar com uma linha de base ("não fazer nada" ou a média dos anos) e conferir com fonte externa (IBGE, Epagri, ZARC, Embrapa, CEASA).
4. **Avaliação:** aplicar a régua.
5. **Documentação:** ficha padrão (`FICHA_MODELO.md`).
6. **Veredito:** aprovada, ajustar ou descartada. Se for descartada, teste a próxima ideia (até 4 tentativas por sessão).

## Régua (nota de 1 a 5, com uma frase de justificativa em cada)
1. Problema real
2. Tamanho do impacto
3. Resolve de fato
4. Validade
5. Muda a decisão
6. Simples e factível
7. Alinhamento com o desafio
8. Diferencial
9. Cabe no hackathon

**Aprovada só com nota 3 ou mais em "problema real", "resolve de fato" e "validade".** Resultado negativo honesto também vale e deve ser documentado.

Guia para as notas:
- **Validade 1–2:** sem teste com dado, ou o sinal não supera a linha de base. **3:** supera a linha de base com dado oficial, mas sem conferência externa ou com amostra pequena. **4–5:** supera a linha de base e bate com fonte externa.
- **Resolve de fato 3:** o resultado muda o que o agricultor faria em pelo menos alguns anos ou talhões.

## Regras de dados
- **Na solução:** só os recursos oficiais da aba Resources do desafio: NASA POWER, GPM/IMERG, SMAP, Landsat, MODIS/VIIRS, SRTM, ECOSTRESS, NLDAS/GLDAS, GEDI, FAO GAEZ, Sentinel-2, ERA5 (e os dos EUA, que não servem aqui).
- **Fontes externas** (IBGE, Epagri/Cepa, Epagri/Ciram, Embrapa, ZARC, CEASA, Conab): **só para entender o problema ou conferir resultados**, nunca como entrada da solução.
- Toda afirmação com número leva fonte. Marque: [DADO], [CÁLCULO], [ESTIMATIVA], [INFERÊNCIA].

## Dados já baixados (use estes, não baixe de novo)
- `dados/power_ituporanga.json` e `dados/power_sao_miguel_do_oeste.json`: NASA POWER diário, 1981–2025, comunidade AG. Parâmetros: `PRECTOTCORR` (chuva, mm/dia), `T2M`, `T2M_MAX`, `T2M_MIN`, `RH2M`, `WS2M`, `ALLSKY_SFC_SW_DWN` (MJ/m²/dia; **vazio de 1981 a 1983**, use 1984+ para ET0), `GWETTOP`, `GWETROOT`, `GWETPROF` (umidade do solo relativa, 0–1, MERRA-2), `EVPTRNS`. Valor faltante = -999. Formato: `d["properties"]["parameter"][PARAM]["AAAAMMDD"]`.
- A grade do POWER é grossa (~50 km). Diga isso nos limites.

## Rotas de acesso testadas em 14/11/2026
- **Python `urllib` falha com SSL nesta máquina.** Use `curl` (funciona) para baixar.
- **NASA POWER:** `https://power.larc.nasa.gov/api/temporal/daily/point?parameters=...&community=AG&longitude=..&latitude=..&start=AAAAMMDD&end=AAAAMMDD&format=JSON`. O parâmetro `IMERG_PRECTOT` volta vazio no diário.
- **MODIS (ORNL DAAC, sem login):** `https://modis.ornl.gov/rst/api/v1/MOD13Q1/dates?latitude=..&longitude=..` e `.../subset?latitude=..&longitude=..&startDate=A2020001&endDate=A2020100&kmAboveBelow=0&kmLeftRight=0` (pode ser lento; peça no máximo ~10 datas por chamada).
- **Sentinel-2 L2A (STAC Earth Search, AWS, sem login):** `https://earth-search.aws.element84.com/v1/search?collections=sentinel-2-l2a&intersects=...`.
- **SRTM:** tiles públicos `https://s3.amazonaws.com/elevation-tiles-prod/skadi/S28/S28W050.hgt.gz` (OpenTopography pede chave).
- **IBGE SIDRA (conferência):** `https://apisidra.ibge.gov.br/values/t/5457/n6/4208500/v/214,112/p/2015-2023/c782/40107` (tabela 5457 = PAM; produto 40107 = cebola, aviso da B5; ajuste produto e município).
- **ZARC (conferência):** tábua de risco em CSV no portal `dados.agricultura.gov.br` (161 MB a safra 2026/27; pode dar timeout).
- **SMAP, IMERG, GLDAS direto:** pedem login Earthdata. Se não tiver, diga que não testou.

## Onde escrever
- Sua pasta: `sessoes/<ID>/` (scripts, dados intermediários, gráficos PNG ou SVG).
- Suas fichas: `fichas/<ID>-<n>-<nome-curto>.md`, seguindo `FICHA_MODELO.md`.
- **Não edite** arquivos de outras sessões, nem `../contexto.md`, nem este protocolo.
- Não escreva no Miro.

## Relatório final da sessão (sua última mensagem)
Até 250 palavras: para cada ideia testada, uma linha com nome, veredito, as três notas obrigatórias (problema real / resolve de fato / validade), a nota total (soma das 9) e o caminho da ficha. Depois, uma frase sobre se a ideia complementa ou compete com o controle.
