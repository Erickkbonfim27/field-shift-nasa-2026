"""Caminhos, versão e regiões do motor.

Regra de dados do desafio:
- ENTRADA da solução: só recursos da aba Resources (NASA POWER, SRTM, Sentinel-2, GAEZ) e
  coeficientes fixos de método publicado (FAO-56, FAO-33).
- Fontes externas (ZARC, IBGE PAM, Epagri, Garantia-Safra) só entram em `conferencia.py`,
  e só para conferir. Nenhum cálculo do motor lê esses arquivos.
"""
from pathlib import Path

MOTOR = Path(__file__).resolve().parent
SOLUCAO = MOTOR.parent
RAIZ = SOLUCAO.parent
SAIDA = SOLUCAO / "saida"
CALCULOS = SAIDA / "calculos"
SCHEMA = SOLUCAO / "contrato.schema.json"
EXEMPLO = SOLUCAO / "exemplo_saida.json"

VERSAO_MOTOR = "0.2.0"
VERSAO_CONTRATO = "2.1.0"

LOOP = RAIZ / "loop-validacao"
VAL = SOLUCAO / "validacao"

# ---------------- dados da aba Resources (entrada) ----------------
POWER = {
    "sao_miguel_do_oeste": LOOP / "dados" / "power_sao_miguel_do_oeste.json",
    "ituporanga": LOOP / "dados" / "power_ituporanga.json",
    "quixada": RAIZ / "prototipo" / "dados" / "power_quixada.json",
    # só para conferir se a célula do POWER é a mesma (mesma_celula_que)
    "dionisio_cerqueira": VAL / "V2" / "dados" / "power_dionisio_cerqueira.json",
    "chapeco": VAL / "V2" / "dados" / "power_chapeco.json",
    "concordia": VAL / "V2" / "dados" / "power_concordia.json",
    "rio_do_sul": LOOP / "sessoes" / "B3" / "power_extra" / "power_rio_do_sul.json",
    "alfredo_wagner": LOOP / "sessoes" / "B3" / "power_extra" / "power_alfredo_wagner.json",
}
NOME_PONTO = {
    "dionisio_cerqueira": "Dionísio Cerqueira", "chapeco": "Chapecó", "concordia": "Concórdia",
    "rio_do_sul": "Rio do Sul", "alfredo_wagner": "Alfredo Wagner",
}
SRTM_V3 = VAL / "V3" / "res_06_srtm.json"            # SRTM 30 m processado na V3 (perfis de SMO)
S2_BLOCOS = LOOP / "sessoes" / "A3" / "a3_1_blocos.npz"  # Sentinel-2 + SRTM processados na A3-1

# ---------------- resultados de validação já feitos (lidos, não recalculados) ----------------
V1_EXTENSAO = VAL / "V1" / "resultado_extensao.json"          # percentil com anos futuros (passo 4)
V1_SO_PASSADO = VAL / "V1" / "resultado_so_passado.json"      # percentil só com anos passados (passo 6)

# ---------------- só conferência (externo) ----------------
ZARC_SC = VAL / "V6" / "zarc_gabarito_sc.json"
PAM_V1 = VAL / "V1" / "tabela_original.json"
V5_RESULTADO = VAL / "V5" / "resultado.json"
V5_EXTRA = VAL / "V5" / "resultado_extra.json"
FICHA_A1_1 = LOOP / "fichas" / "A1-1-mapa-plantio-extremo-oeste.md"

# ---------------- regiões e área testada ----------------
# Caixa (lat_min, lat_max, lon_min, lon_max). É uma aproximação grosseira da área em que as
# frentes testaram os módulos (SMO, Chapecó, Concórdia; Ituporanga e vizinhos; 6 municípios
# do CE/PE/PB da V5). A Bahia fica fora (V5: rho 0,07).
REGIOES = {
    "sc_extremo_oeste": dict(nome="Extremo Oeste de SC (leite e milho)", papel="principal",
                             caixa=(-27.5, -26.0, -54.0, -51.9)),
    "sc_alto_vale": dict(nome="Alto Vale do Itajaí, SC (cebola)", papel="principal",
                         caixa=(-27.9, -27.0, -50.0, -49.3)),
    "semiarido_ce_pe_pb": dict(nome="Semiárido do CE, PE e PB (milho)", papel="segunda",
                               caixa=(-8.3, -4.5, -41.0, -36.5)),
}


def rel(p):
    """Caminho relativo à raiz do projeto, para o rastro."""
    return str(Path(p).resolve().relative_to(RAIZ))


def regiao_do_ponto(lat, lon):
    for rid, r in REGIOES.items():
        a, b, c, d = r["caixa"]
        if a <= lat <= b and c <= lon <= d:
            return rid
    return None


def regiao_mais_proxima(lat, lon):
    def dist(r):
        a, b, c, d = r["caixa"]
        return ((lat - (a + b) / 2) ** 2 + (lon - (c + d) / 2) ** 2) ** 0.5
    return min(REGIOES, key=lambda k: dist(REGIOES[k]))


def ler_json(p):
    import json
    with open(p) as f:
        return json.load(f)
