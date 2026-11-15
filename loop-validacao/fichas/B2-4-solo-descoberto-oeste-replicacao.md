# B2-4 · Solo descoberto no Extremo Oeste do leite e do grão: replicação fora da amostra

Sessão: B2 · Trilha: B · Região: Extremo Oeste (São Miguel do Oeste e entorno) · Tentativa 4 de 4 · Data: 2026-11-14

## 1. Ideia (escrita antes do teste)
- **Hipótese:**
  - Na B2-1 e na B2-3, o indicador de solo nu do Sentinel-2 ordenou os 8 municípios do Extremo Oeste quase igual ao Censo 2017 (ρ = 0,81 e 0,90). Mas esse foi um subgrupo achado depois.
  - Se o sinal for real, ele se repete em **outros** municípios do Oeste que não entraram no teste.
  - **Por que importa no leite:** o milho para silagem sai inteiro da roça e não deixa palha. O "plantio direto" do produtor de leite pode ficar de solo nu até a pastagem de inverno pegar. O indicador mostraria isso no talhão.
- **Problema que ataca (e para quem):** o produtor de leite e grão do Extremo Oeste, e o técnico que precisa saber quem está de fato em plantio direto com palha (crédito ABC+, ZARC por níveis de manejo) e onde a silagem deixa o solo exposto.
- **Decisão que muda:**
  - Para o agricultor: semear a cobertura ou a pastagem logo depois da silagem nos talhões que aparecem nus.
  - Para o técnico: quem visitar primeiro.
- **Critério de sucesso (definido antes, sem olhar o Sentinel-2 desses municípios):**
  - **Amostra, por regra automática:** todos os municípios de SC com ≥ 95% do polígono dentro da quadrícula 22JBR, fora dos 8 já usados e com ≥ 150 estabelecimentos com preparo do solo no Censo. Deu **32 municípios** (`sessoes/B2/dados/ids_replicacao.txt`).
  - **Método congelado:** a máscara da B2-3 sem nenhuma mudança (`s2v2_analise.py`), NDTI < 0,07, o mesmo período (out/2019 a set/2021) e a mesma coleção.
  - **Sucesso:** ρ de Spearman(I1, C) ≥ 0,6 com p < 0,05 nos 32, **e** pelo menos 0,1 acima da linha de base "fração de lavoura".
  - **Ajustar** se 0,3 ≤ ρ < 0,6 com p < 0,05. **Descartada** se ρ < 0,3.
- **Linha de base:** "não fazer nada" (ρ = 0) e o proxy "fração de lavoura do município".

## 2. Teste
- **Dados oficiais usados:** Sentinel-2 L2A C1, quadrícula 22JBR, 180 datas de out/2019 a set/2021, lidas a 40 m, com a máscara SCL. São 32 municípios novos.
- **Método:**
  1. `sessoes/B2/s2_extrair_rep.py`: a mesma extração da B2-1, em 4 lotes.
  2. `sessoes/B2/s2v2_rep_analise.py`: a análise da B2-3 sem nenhuma mudança.
  - Saída: `sessoes/B2/s2v2_rep_resultado.json`.
- **Resultado (n = 32):**

| NDTI < | ρ(I1, C) | p | Linha de base (fração de lavoura) |
|---|---|---|---|
| 0,05 | 0,14 | 0,46 | −0,17 |
| **0,07 (principal)** | **0,11** | **0,56** | −0,17 (p = 0,35) |
| 0,09 | 0,12 | 0,50 | −0,17 |

  - O I2 (fração de pixels com 2 ou mais datas de solo nu) dá −0,07 [CÁLCULO].
  - **Exemplos que não batem:**
    - Riqueza (C = 0,17) tem o maior I1 (0,23), mas Belmonte (C = 0,26) tem I1 de 0,06.
    - Bom Jesus do Oeste (C = 0,00) e Cunhataí (C = 0,02) têm I1 de 0,04 e 0,10.
- **Gráfico:** `sessoes/B2/s2v2_rep_solo_nu_x_censo.svg`, uma nuvem de pontos sem ordem.

## 3. Validação
- **Contra a linha de base:** ρ = 0,11 contra |−0,17| do proxy. Não supera, nem é diferente de zero.
- **Fonte externa:** Censo Agro 2017, tabela 6855 (IBGE). **Não bate.**
  - No Oeste, a fração de convencional é baixa e estreita: de 0 a 0,26 nos 32 municípios. A diferença entre os municípios é pequena demais para o satélite, a 40 m e com o limiar não calibrado, separar.
  - Os 0,81 e 0,90 da B2-1 e da B2-3 vieram de 8 municípios e foram acaso.
- **O critério de sucesso foi atingido?** **Não.** ρ < 0,3, o que pela regra pré-definida dá "descartada".

## 4. Régua (1 a 5)
| Critério | Nota | Por quê (uma frase) |
|---|---|---|
| Problema real | 4 | A silagem tira a palha, e há demanda por prova de plantio direto (ZARC por níveis de manejo, ABC+). |
| Tamanho do impacto | 3 | Pega todo o leite e o grão do Oeste, mas o ganho é indireto. |
| Resolve de fato | 1 | O indicador não ordena os municípios por manejo fora da amostra. |
| Validade | 1 | Replicação com n = 32: ρ = 0,11, p = 0,56, sem ganho sobre a linha de base. |
| Muda a decisão | 1 | Sem sinal, não muda nada. |
| Simples e factível | 3 | O pipeline roda (32 municípios em ~40 min), mas falta calibração de campo. |
| Alinhamento com o desafio | 4 | É conservação do solo com Sentinel-2 da aba Resources. |
| Diferencial | 3 | O SWIR separa a palha do solo nu na teoria, mas não se provou. |
| Cabe no hackathon | 3 | Cabe, mas não há resultado para mostrar. |
| **Total (máx. 45)** | **23** | |

## 5. Veredito
**Descartada.** O sinal do Extremo Oeste não se repetiu fora da amostra (ρ = 0,11, n = 32). Com o que testei (40 m, dois anos e o limiar de NDTI da literatura), o Sentinel-2 não separa o plantio direto do convencional no agregado do município em SC. Um teste de verdade pediria talhões com manejo conhecido (gabarito de campo), que a aba Resources não tem.

## 6. Relação com o controle
Nenhuma. Não entra na demo como indicador de manejo. A sazonalidade (solo nu em jun–ago na cebola, ficha B2-1) pode aparecer só como ilustração, sem número de acerto.

## 7. Limites e o que não foi testado
- **Gabarito:** o Censo é de estabelecimentos, de 2016/17, e não de área de lavoura. Um teste justo pediria talhões conhecidos (Epagri ou propriedades de referência).
- **Resolução:** 40 m e não 10 m; não testei 10 m.
- **Limiar:** o NDTI não foi calibrado no solo vermelho e argiloso do Oeste, que tem cor e umidade diferentes.
- **Outro sensor:** não testei Landsat nem HLS para ter mais datas.
- **Silagem:** a hipótese de que a silagem deixa o solo nu não foi testada no talhão, só no agregado.

## 8. Fontes
- Sentinel-2 L2A C1, Earth Search [DADO].
- IBGE, Censo Agropecuário 2017, tabela 6855 [DADO, conferência].
- IBGE, malhas municipais [DADO].
