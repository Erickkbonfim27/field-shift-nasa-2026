"""Módulos de ano extremo.

ano_extremo_seco (SC, milho; N2): índice = ISNA do milho de 20/set a 10/jan (B3-1). Dispara se o
    ano fica entre os 10% mais secos da PRÓPRIA célula, contando só anos passados (regra R6;
    pendência P2 da spec). A regra relativa foi a que resistiu na V1; a regra fixa 0,75 caiu.
ano_extremo_excesso (Alto Vale, cebola; N1): excedente hídrico de 1/set a 30/nov (B3-2). Só
    histórico: lista as primaveras >= P90 dos anos passados. Não é alerta (V1: p = 0,39 fora do
    Alto Vale).
"""
import datetime as dt
import statistics as st
from . import balanco as B
from . import config as C

LIMIAR_PCT = 10
ANO_INICIO_PERCENTIL = 1990  # mesmo início da janela validada na V1 (resultado_extensao.json)


def percentil_passado(valor, passados):
    """% dos anos passados com índice <= valor (0 a 100). Dispara (seco) se <= 10."""
    if valor is None or not passados:
        return None
    return round(100 * sum(1 for x in passados if x <= valor) / len(passados), 1)


def alerta_seco(pw, data_ref, ano_inicio=ANO_INICIO_PERCENTIL):
    """Estado do alerta na data de referência. Usa a janela até min(10/jan, data_ref) em todos os anos."""
    ano_safra = data_ref.year + 1 if data_ref.month >= 7 else data_ref.year  # ano da colheita
    pl = dt.date(ano_safra - 1, *B.MILHO_B31["plantio"])
    dec = dt.date(ano_safra, *B.MILHO_B31["decisao"])
    janela = dict(de=pl.isoformat(), ate=dec.isoformat())
    passados_anos = list(range(ano_inicio, ano_safra))
    if data_ref < pl + dt.timedelta(30):
        corte = None
        estado = "fora_da_janela"
    else:
        corte = min(dec, data_ref)
        estado = None
    serie = {}
    for a in passados_anos:
        c = None if corte is None else dt.date(a - (1 if corte.month >= 7 else 0), corte.month, corte.day)
        v = B.isna_milho_b31(pw, a, ate=c)
        if v is not None:
            serie[a] = v
    if corte is None:
        valor = pct = None
    else:
        valor = B.isna_milho_b31(pw, ano_safra, ate=corte)
        if valor is None:
            estado = "sem_dado"
            pct = None
        else:
            pct = percentil_passado(valor, list(serie.values()))
            estado = "ativo" if pct <= LIMIAR_PCT else "inativo"
    anos_ok = sorted(serie)
    return dict(estado=estado, ano_safra=ano_safra, janela=janela, ate=corte.isoformat() if corte else None,
                indice=valor, percentil=pct, limiar=LIMIAR_PCT, n_anos_passados=len(anos_ok),
                periodo_passado=f"{anos_ok[0]}-{anos_ok[-1]}", serie_passada={str(a): round(v, 4) for a, v in serie.items()},
                minimo_passado=dict(ano=min(serie, key=serie.get), valor=round(min(serie.values()), 4)),
                parametros=dict(B.MILHO_B31, fases=list(B.MILHO_B31["fases"]), kc=list(B.MILHO_B31["kc"]),
                                balde="cheio 60 dias antes do plantio, Kc 0,5 antes do plantio"))


def validacao_v1(caminho_passado, caminho_futuro=None):
    """Números da validação fora da amostra (V1, 8 células novas), lidos dos resultados salvos.

    O resultado principal (`passado`) vem do passo 6 da V1: percentil calculado SÓ com anos
    passados, que é a regra que o motor roda. O passo 4 (`com_futuro`) usou 1990-2025 inteiro e
    fica só para comparação. Este é um cálculo de VALIDAÇÃO (usa o IBGE PAM): fica só na
    auditoria, nunca no cálculo do índice (regra R2) nem no WhatsApp (R2 segue os ponteiros)."""
    R = C.ler_json(caminho_passado)["so_anos_com_historico"]
    out = dict(alertas=R["alertas"], acertos=R["acertos"], precisao=R["precisao"], taxa_base=R["taxa_base"],
               recall=R["recall"], eventos=R["eventos"], eventos_acerto=R["eventos_acerto"],
               eventos_novos=R["acerto_eventos_novos"], rel_medio_alerta=R["rel_medio_alerta"],
               p_evento=R["permutacao"]["p_evento"], anos_regiao=R["anos_regiao"],
               criterios=R["criterios"], ic95_evento=R["ic95_evento"],
               anos_assim_ruins_em_10=round(10 * R["acertos"] / R["alertas"], 1),
               ano_qualquer_ruim_em_10=round(10 * R["taxa_base"], 1),
               recall_pct=round(100 * R["recall"]))
    if caminho_futuro:
        F = C.ler_json(caminho_futuro)["milho (todas)"]["regra_neutra_10pct"]
        out["com_futuro"] = dict(alertas=F["alertas"], acertos=F["acertos"], taxa_base=F["taxa_base"], recall=F["recall"],
                                 eventos=F["eventos"], eventos_acerto=F["eventos_acerto"], eventos_novos=F["acerto_eventos_novos"],
                                 rel_medio_alerta=F["rel_medio_alerta"], p_evento=F["permutacao"]["p_evento"],
                                 criterios=F["criterios"])
    return out


def historico_excesso(pw, ano_ref, ano_inicio=1984, pct=90):
    """Excedente set-nov por ano (anos < ano_ref) e as primaveras >= P90 desses anos."""
    serie = {}
    for a in range(ano_inicio, ano_ref):
        v = B.excedente_cebola_b32(pw, a)
        if v is not None:
            serie[a] = v
    vals = list(serie.values())
    p90 = st.quantiles(vals, n=10, method="inclusive")[-1]
    anos = sorted(a for a, v in serie.items() if v >= p90)
    return dict(serie={str(a): round(v, 1) for a, v in serie.items()}, p90_mm=round(p90, 1), anos_extremos=anos,
                n_anos=len(serie), periodo=f"{min(serie)}-{max(serie)}",
                parametros=dict(B.CEBOLA_B32, fases=list(B.CEBOLA_B32["fases"]), kc=list(B.CEBOLA_B32["kc"])))
