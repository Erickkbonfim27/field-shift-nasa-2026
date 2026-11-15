# B5-4 · Boletim mensal de estiagem para a prefeitura e a Defesa Civil

Sessão: B5 · Trilha: B · Região: São Miguel do Oeste · Tentativa 4 de 4 · Data: 2026-11-14

## 1. Ideia (escrita antes do teste)
- **Hipótese:** um boletim mensal com a umidade do solo da zona das raízes do NASA POWER (GWETROOT, MERRA-2) avisa a Secretaria de Agricultura e a Defesa Civil que a estiagem está instalada antes de o município decretar situação de emergência. O decreto destrava a prorrogação de parcelas do Pronaf, o Proagro e a ajuda de água e silagem para as famílias.
- **Problema que ataca (e para quem):** o decreto costuma sair quando a perda já está feita; a prefeitura reúne laudos da Epagri e da Defesa Civil às pressas. Para o agricultor familiar, o decreto atrasado atrasa a prorrogação da dívida e a ajuda.
- **Decisão que muda:** a prefeitura começa o levantamento de perdas e o pedido de decreto mais cedo; a Epagri organiza a vistoria; a família sabe que a ajuda vem.
- **Critério de sucesso (definido antes de ver as datas dos decretos):**
  - Mês em alerta = GWETROOT médio do mês abaixo de (média − 1 desvio-padrão) daquele mês do calendário em 1991–2020. Boletim de estiagem = 2 meses seguidos em alerta.
  - Ano marcado = houve boletim de estiagem no ano.
  - Acerta pelo menos **70% dos anos com decreto de emergência por estiagem** em São Miguel do Oeste, com **precisão de 60% ou mais**, e o 1º boletim sai **antes do decreto** na maioria dos anos acertados.
  - Supera a linha de base.
- **Linha de base:** a mesma regra com a chuva acumulada em 3 meses (abaixo de média − 1 desvio, tipo SPI-3), que qualquer posto de chuva calcula; e o acaso.

## 2. Teste
- **Dados oficiais usados:** NASA POWER diário, ponto -26,725; -53,518 (~50 km): `GWETROOT` (umidade relativa da zona das raízes, MERRA-2) e `PRECTOTCORR`, 1991–2025, agregados por mês. [DADO]
- **Método:** Script `sessoes/B5/boletim_estiagem.py`. (1) Limiar mensal com a normal de 1991–2020; (2) boletim no fim do 2º mês seguido em alerta; (3) comparação com os registros de estiagem do município no Atlas Digital de Desastres (base do S2iD), 2005–2025, em `sessoes/B5/decretos_smo.csv`. Saída: `resultado_boletim.txt`.
- **Resultado:** [CÁLCULO]
  - Registros de estiagem no S2iD: fev/2005, abr/2008, abr/2009, dez/2011, fev/2014 (só registro), abr/2020 (só registro) e dez/2021, ou 7 anos. [DADO]
  - **Boletim GWETROOT:** marca 11 anos, **acerta 5 de 7 (71%)**, 6 alarmes falsos, **precisão de 45%**. Errou 2011 (o boletim só saiu em fev/2012) e 2014.
  - **Antes do decreto:** em 3 dos 5 acertos (2008: 1 dia; 2020: 76 dias; 2021: 234 dias, mas o boletim de abril de 2021 é de outro pico seco). Em 2005 e 2009 saiu 41 e 22 dias **depois**.
  - **Base (chuva de 3 meses):** marca 15 anos, acerta 5 de 7, 10 alarmes falsos, precisão de 33%.
  - Vários "alarmes falsos" são a mesma estiagem atravessando o ano: 2012 (continuação de dez/2011), 2019 (início da seca de 2019/20) e 2022 (continuação de dez/2021). Contando por episódio (regra criada depois do critério), o boletim fica perto de 5 dos 7 decretos, igual à base.
- **Gráfico:** `sessoes/B5/grafico_b5_4_boletim.svg`. Linha do tempo dos meses com boletim (umidade do solo e chuva) e dos decretos; os blocos longos de 2019–2022 cobrem os dois decretos mais caros.

## 3. Validação
- **Contra a linha de base:** mesmo acerto (5 de 7); o GWETROOT erra menos (6 contra 10 alarmes falsos; precisão de 45% contra 33%). Acaso: 7 de 21 anos têm registro, então a precisão esperada seria de 33%. [CÁLCULO]
- **Fonte externa:** o próprio Atlas Digital de Desastres (MIDR/S2iD) é o gabarito. Os dois maiores prejuízos registrados (R$ 45,4 mi em dez/2021 e R$ 21,6 mi em fev/2005) foram pegos pelo boletim. [DADO] O Proagro do milho no município também bate com 2020–2022 (coberturas deferidas por seca: 32 em 2020 e 51 em 2021, por ano de emissão). [DADO]
- **O critério de sucesso foi atingido?** **Em parte.** Acerto de 71% e vitória sobre a base, sim; precisão de 45% (meta de 60%), não; boletim antes do decreto em 3 de 5, sim por pouco, e com antecedência que não se repete (de −41 a +234 dias).

## 4. Régua (1 a 5)
| Critério | Nota | Por quê (uma frase) |
|---|---|---|
| Problema real | 3 | O decreto destrava prorrogação do Pronaf e ajuda; mas não medimos se ele atrasa de fato (os decretos saíram de fevereiro a abril, no meio da safra). |
| Tamanho do impacto | 3 | Pega o município inteiro (R$ 45,4 mi de prejuízo privado registrado em 2021), mas é um efeito indireto para a família. |
| Resolve de fato | 2 | Chega antes do decreto em só 3 de 5 casos, sem regularidade, e não muda o que o agricultor faz. |
| Validade | 3 | Supera a base com dado oficial e bate com o Atlas S2iD e o Proagro, mas com precisão de 45% e 7 eventos. |
| Muda a decisão | 2 | Pode adiantar o trabalho da prefeitura em alguns anos (2020), não a decisão de plantio. |
| Simples e factível | 5 | Uma variável do POWER e uma conta mensal. |
| Alinhamento com o desafio | 2 | É gestão de crise municipal, longe da rotação de culturas. |
| Diferencial | 2 | O Monitor de Secas (ANA) e a Defesa Civil já acompanham a estiagem; o ganho é usar a umidade do solo em vez da chuva. |
| Cabe no hackathon | 5 | Já está pronto. |
| **Total (máx. 45)** | **27** | |

Aprovada só com 3+ em problema real, resolve de fato e validade.

## 5. Veredito
**Descartada como produto.** A umidade do solo do POWER reconhece as estiagens oficiais tão bem quanto a chuva e com menos alarmes falsos, mas não avisa antes de forma regular, e a persona (prefeitura) fica longe da decisão do agricultor.

## 6. Relação com o controle
Complementa. O achado útil é que o **GWETROOT erra menos do que a chuva** para dizer "estiagem instalada" (6 contra 10 alarmes falsos). No controle, ele pode ser o "estado de agora" na hora do plantio, quando não houver SMAP: "o solo está tão seco quanto em 2020 e 2021". Na demo, cabe uma frase no painel do técnico, não um produto à parte.

## 7. Limites e o que não foi testado
- Grade do POWER de ~50 km; o GWETROOT é de reanálise (MERRA-2), não medição de satélite. SMAP (9 km, desde 2015) pede login Earthdata e não foi testado.
- O Atlas registra o reconhecimento federal e o registro no S2iD, não a data do decreto municipal; a data pode ser posterior ao decreto.
- Só 7 eventos em 21 anos; o casamento "por ano do calendário" corta estiagens que atravessam o ano (2011/12, 2021/22).
- Não conversamos com a Defesa Civil nem com a Secretaria de Agricultura sobre como decidem o decreto e se usariam um boletim.

## 8. Fontes
- NASA POWER, API diária, comunidade AG (arquivo `dados/power_sao_miguel_do_oeste.json`).
- Atlas Digital de Desastres no Brasil (MIDR, base do S2iD): https://atlasdigital.mdr.gov.br/paginas/downloads.xhtml (recorte em `sessoes/B5/externo/atlas_desastres_S2iD_SMO_Ituporanga_2005-2025.csv`).
- Proagro, Matriz de Dados do Proagro (BCB), por município e evento: https://www.bcb.gov.br/estabilidadefinanceira/proagro (recortes em `sessoes/B5/externo/`).
