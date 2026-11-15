"""Leitura de fontes EXTERNAS, só para conferir (ZARC, IBGE PAM, V5/PAM, Garantia-Safra).

Nada daqui entra em cálculo do motor. Os itens de rastro que apontam para cá têm
fonte.categoria = 'externo_conferencia' e tipo = 'conferencia' (o schema e a regra R2 obrigam).
"""
from . import config as C

AD_MM = {"AD1": 24.0, "AD2": 31.8, "AD3": 41.4, "AD4": 54.6, "AD5": 72.6, "AD6": 95.4}
MUN_ZARC = {"sao_miguel_do_oeste": "Sao Miguel do Oeste", "ituporanga": "Ituporanga"}

_zarc = None


def _gabarito():
    global _zarc
    if _zarc is None:
        _zarc = C.ler_json(C.ZARC_SC)
    return _zarc


def classe_ad(cad_mm):
    """Classe AD do ZARC mais próxima do CAD do talhão (só para escolher a linha de conferência)."""
    return min(AD_MM, key=lambda k: abs(AD_MM[k] - cad_mm))


def zarc_milho(local, ad, grupo="grupo_I"):
    g = _gabarito()["dados"][MUN_ZARC[local]]["milho_1safra"]["Sequeiro"]["ciclos"][grupo][ad]
    return g["risco_por_decendio"]


def zarc_sorgo_forrageiro(local, safra="1safra", grupo="grupo_I", solo="solo_tipo_2"):
    g = _gabarito()["dados"][MUN_ZARC[local]][f"sorgo_forrageiro_{safra}"]["Sequeiro"]["ciclos"][grupo][solo]
    return g["risco_por_decendio"]


def zarc_linha(tabela, decendio):
    r = tabela.get(decendio)
    return dict(risco_pct=r, indicado=r is not None)


def pam_rel(regiao, ano):
    for x in C.ler_json(C.PAM_V1):
        if x["regiao"] == regiao and x["ano"] == ano:
            return x["rel"]
    return None


def pam_serie(regiao):
    return {x["ano"]: x["rel"] for x in C.ler_json(C.PAM_V1) if x["regiao"] == regiao}


def zarc_caupi_quixada():
    """ZARC 2026/27, caupi grupo I, sequeiro, solo tipo 2, Quixadá: dict decêndio do ano -> risco %.
    Tirado do CSV do MAPA pela sessão do protótipo e gravado em prototipo/dados/resultado.json."""
    r = C.ler_json(C.RAIZ / "prototipo" / "dados" / "resultado.json")
    return {int(k): v for k, v in r["zarc_caupi_medio"].items()}


def v5_quixada():
    r = C.ler_json(C.V5_RESULTADO)
    q = r["quixada"]
    ex = C.ler_json(C.V5_EXTRA)
    return dict(rho_milho=q["milho"]["chuva"]["principal"]["rho"],
                rho_chuva=q["milho"]["chuva"]["principal"]["rho_chuva"],
                acerto8=q["milho"]["chuva"]["principal"]["acerto8"],
                n=q["milho"]["chuva"]["principal"]["n"],
                garantia_safra=ex.get("garantia_safra_vs_regiao"))
