"""São Miguel do Oeste (SC): leite e milho. Caso da demo (spec-v2 seção 4.1).

Módulos ativos (spec-v2 seção 3): geada_janela_safra (N2; a forma bate com o ZARC, a magnitude não),
geada_limite_2a_safra (N2),
ano_extremo_seco (N2), mistura_talhao (N2, só talhão declarado raso), agua_isna (N1, só insumo),
sorgo_2a_safra (N1, em teste). enso_tipo_risco fica desligado (dado fora da aba Resources).
"""
import datetime as dt
from .. import config as C
from .. import documento as D
from .. import textos as T
from .. import geada as G
from .. import ano_extremo as A
from .. import mistura as M
from .. import conferencia as K
from ..power import Power, mesma_celula
from ..estat import wilson

SLUG = "sao-miguel-do-oeste"
LOCAL = dict(id="L-sao-miguel-do-oeste", municipio="São Miguel do Oeste", uf="SC", codigo_ibge="4217204",
             lat=-26.725, lon=-53.518)
VIZINHOS = ("dionisio_cerqueira", "chapeco", "concordia")
SOLO_MM_M = {"arenoso": 65, "medio": 125, "argiloso": 175, "raso_ou_pedregoso": 65, "nao_sei": 125}
RAIZ_M = {"arenoso": 1.0, "medio": 1.0, "argiloso": 1.0, "raso_ou_pedregoso": 0.6, "nao_sei": 1.0}
CAD_N2_MAX = 42.0  # V3: N2 até ~42 mm; N1 de 55 a 90 mm; desligado no fundo

_cache = {}


def _calc_pesado(solo):
    """Cálculos que não dependem da data nem da prioridade (cache para R9 e testes)."""
    if "base" not in _cache:
        pw = Power(C.POWER["sao_miguel_do_oeste"])
        viz = {n: mesma_celula(pw, Power(C.POWER[n])) for n in VIZINHOS}
        _cache["base"] = dict(pw=pw, viz=viz, janela=G.tabela_janela_safra(pw), curva=G.curva_2m(pw),
                              limites=G.limites_2m(pw))
    b = dict(_cache["base"])
    cad = round(SOLO_MM_M[solo] * RAIZ_M[solo], 1)
    b["cad"] = cad
    if solo == "raso_ou_pedregoso":
        if ("mistura", cad) not in _cache:
            if "serie" not in _cache:
                _cache["serie"] = M.Serie(C.POWER["sao_miguel_do_oeste"])
            _cache[("mistura", cad)] = M.avaliar(_cache["serie"], cad)
        b["mistura"] = _cache[("mistura", cad)]
    return b


def _srtm_talhao():
    """Perfil 7 da UDESC (Neossolo Litólico de topo), SRTM 30 m processado na V3.
    Regra 'confirme' da V3: declive >= 15% ou TPI >= 2 m (limiar escolhido depois de ver os perfis)."""
    r = C.ler_json(C.SRTM_V3)["perfis_udesc"]["perfil7_Neossolo_Litolico_topo"]
    dec, tpi = round(r["srtm_declive_pct"], 1), round(r["tpi_90m_m"], 1)
    return dict(declive_pct=dec, tpi_m=tpi, marca_confirme=bool(dec >= 15 or tpi >= 2))


def avaliar(data_referencia="2022-01-25", modo="replay", solo_declarado="raso_ou_pedregoso",
            prioridade="silagem_garantida", colheita_verao="2022-01-20", nome_talhao="Encosta de cima",
            id_produtor="P-3fa9c210", fotos=None):
    dref = dt.date.fromisoformat(data_referencia)
    b = _calc_pesado(solo_declarado)
    pw = b["pw"]
    raso = solo_declarado == "raso_ou_pedregoso"
    mist = b.get("mistura")
    cad = b["cad"]
    ad = K.classe_ad(cad)
    zm = K.zarc_milho("sao_miguel_do_oeste", ad)
    al = A.alerta_seco(pw, dref)
    val = A.validacao_v1(C.V1_SO_PASSADO, C.V1_EXTENSAO)
    fut = val["com_futuro"]
    crit = val["criterios"]
    safra = f"{al['ano_safra'] - 1}/{str(al['ano_safra'])[2:]}"
    arq_calc = C.CALCULOS / f"{SLUG}.json"
    me = C.MOTOR
    srtm = _srtm_talhao() if raso else None

    # ------------------------------------------------------------------ cálculos gravados
    calculos = dict(
        local=LOCAL, data_referencia=data_referencia, mesma_celula=b["viz"],
        geada_janela_safra=b["janela"], geada_2a_safra=b["curva"], limite_2a_safra=b["limites"],
        alerta_seco=al, validacao_alerta_v1=val, cad=dict(solo=solo_declarado, mm_m=SOLO_MM_M[solo_declarado],
                                                          raiz_m=RAIZ_M[solo_declarado], cad_mm=cad))
    if mist:
        calculos["mistura"] = mist

    # ------------------------------------------------------------------ módulos
    lim = b["limites"]
    curva = {l["decendio"]: l for l in b["curva"]["linhas"]}
    jan = {l["decendio"]: l for l in b["janela"]["linhas"]}
    seguro = G.primeiro_seguro(b["janela"])
    modulos = [
        dict(id="agua_isna", nome="Água por fase (ISNA, FAO-56/FAO-33)", ativo=True, nivel_evidencia="N1", papel="insumo",
             motivo="Em SC não explica o rendimento do ano (rho 0,28, igual à chuva bruta). Só alimenta o alerta de ano seco e a mistura por talhão.",
             validacao=[dict(ref="B1-0", caminho="loop-validacao/fichas/B1-0-controle.md", resultado="rho 0,28 contra a PAM do milho de SMO; chuva dez-fev 0,23"),
                        dict(ref="V4", caminho="solucao/validacao/V4/relatorio.md", resultado="nenhum critério M1-M6 passou no milho")],
             nao_ve=["quebras de 1991, 2002, 2005 e 2021 no milho de SMO", "doença, praga, manejo"]),
        dict(id="geada_janela_safra", nome="Geada no milho de verão (tira agosto da janela)", ativo=True, nivel_evidencia="N2", papel="guarda",
             motivo=(f"Sem ele, a água sozinha manda plantar em agosto. Geada em {jan['01/08']['em10']} de 10 anos com plantio em 1/ago (motor). "
                     "É N2 e não N3: teste em um ponto só, sem amostra nova; o limiar de 2 °C vem do ZARC; a forma bate com o ZARC, a magnitude não."),
             validacao=[dict(ref="V4", caminho="solucao/validacao/V4/relatorio.md", resultado="critério D1 pré-registrado passou em SMO: 6,3 e 4,6 falhas em 10 em 1 e 11/ago. Um ponto, sem amostra nova; veredito geral da V4: parcial"),
                        dict(ref="V6", caminho="solucao/validacao/V6/relatorio.md", resultado="1º decêndio com risco <= 20%: ZARC 21/08, nosso 01/09 (10 dias). Magnitude discorda: 63% de geada contra 40% do ZARC em 1/ago; o POWER parece exagerar. Calibrar o limiar não foi feito")],
             nao_ve=["geada de baixada dentro da célula de 50 km", "a magnitude: o POWER parece exagerar a geada contra o ZARC"]),
        dict(id="geada_limite_2a_safra", nome="Data-limite de geada para o 2º milho de silagem", ativo=True, nivel_evidencia="N2", papel="principal",
             motivo="Passa em SMO, mas a data muda 29 dias entre SMO e Concórdia e 22 dias com o ciclo (V2). Calculado por ponto e mostrado com faixa.",
             validacao=[dict(ref="B1-1", caminho="loop-validacao/fichas/B1-1-geada-milho-safrinha.md", resultado="degrau de 67 pontos entre 1/jan e 21/fev"),
                        dict(ref="V2", caminho="solucao/validacao/V2/relatorio.md", resultado="parcial: 2 de 2 eventos com estação marcados; falha a estabilidade no espaço"),
                        dict(ref="V6", caminho="solucao/validacao/V6/relatorio.md", resultado="último milho no ZARC 21/01 contra 01/02 da B1 (11 dias, dentro de 20)")],
             nao_ve=["falta de água do 2º milho", "perda de silagem (só a chance de geada)"]),
        dict(id="ano_extremo_seco", nome="Alerta de ano seco (10% mais secos da própria célula)", ativo=True, nivel_evidencia="N2", papel="alerta",
             motivo=(f"A regra fixa ISNA < 0,75 caiu na V1. A regra relativa passou em parte: {val['acertos']} de {val['alertas']} alertas em ano ruim contra taxa-base "
                     f"{round(100 * val['taxa_base'], 1)}%, mas só {val['eventos_acerto']} de {val['eventos']} eventos (C1 e C3 falham). Vira alerta com a ressalva de que pega pouco."),
             validacao=[dict(ref="V1", caminho="solucao/validacao/V1/relatorio.md",
                             resultado=(f"regra do motor (percentil só do passado, passo 6): {val['acertos']} de {val['alertas']} alertas em ano ruim; {val['eventos_acerto']} de {val['eventos']} eventos "
                                        f"({val['eventos_novos']} novos); recall {val['recall_pct']}%; p = {val['p_evento']}; C1 e C3 falham. "
                                        f"Com anos futuros no percentil (passo 4): {fut['acertos']} de {fut['alertas']}, {fut['eventos_acerto']} de {fut['eventos']}, recall {round(100 * fut['recall'])}%")),
                        dict(ref="V1-passo6", caminho="solucao/validacao/V1/v1_passo6_so_passado.py", resultado="mínimo de 15 anos passados escolhido antes de rodar; resultado_so_passado.json")],
             nao_ve=[f"cerca de {100 - val['recall_pct']}% dos anos ruins", "quebra por geada, doença ou manejo"]),
    ]
    if raso:
        modulos.append(dict(
            id="mistura_talhao", nome="Metade da silagem em sorgo no talhão raso", ativo=True,
            nivel_evidencia="N2" if cad <= CAD_N2_MAX else "N1", papel="principal",
            motivo=f"Ativo porque o produtor declarou o talhão raso (CAD {cad} mm). Sobrevive em {round(mist['grade']['sobrevive_pct'], 1)}% da grade de parâmetros (corte da V3: 70%). Desligado em solo fundo.",
            validacao=[dict(ref="A4-3", caminho="loop-validacao/fichas/A4-3-sorgo-seguro-silagem.md", resultado="P10 +14% no raso de 87,5 mm (a mistura rende menos em 15 de 41 safras)"),
                       dict(ref="V3", caminho="solucao/validacao/V3/relatorio.md", resultado="raso de 42 mm: P10 +39,6% (IC95 +30,7 a +57,1); média +7,3%; ganho em 35 de 41 safras, perda em 2. O motor reproduz esses números com CAD 42 e usa 39 mm"),
                       dict(ref="V6", caminho="solucao/validacao/V6/relatorio.md", resultado="ZARC concorda só em solo de pouca água (AD2-AD3)")],
            nao_ve=["valor real da silagem de sorgo na dieta", "custo e rebrota do sorgo", "rendimento observado de sorgo (não há PAM em SMO)"]))
    else:
        modulos.append(dict(
            id="mistura_talhao", nome="Metade da silagem em sorgo no talhão raso", ativo=False, nivel_evidencia="N1", papel="em_teste",
            motivo=f"Desligado: o talhão não foi declarado raso (CAD {cad} mm). A V3 só sustenta o ganho em solo de pouca água.",
            validacao=[dict(ref="V3", caminho="solucao/validacao/V3/relatorio.md", resultado="ganho some em solo fundo (CAD 125 e 175 mm)")],
            nao_ve=["talhões rasos não declarados"]))
    modulos += [
        dict(id="sorgo_2a_safra", nome="Sorgo forrageiro depois do milho, quando a janela do 2º milho fecha", ativo=True, nivel_evidencia="N1", papel="em_teste",
             motivo="Sugerido pela V6. Geada e água do sorgo de 2ª safra ainda não foram calculadas.",
             validacao=[dict(ref="V6", caminho="solucao/validacao/V6/relatorio.md", resultado="ZARC 2026/27 indica sorgo forrageiro 2ª safra até 01/03 (grupo I) em SMO; não testado por nós")],
             nao_ve=["tudo: módulo sem cálculo próprio"]),
        dict(id="enso_tipo_risco", nome="El Niño troca o tipo de risco", ativo=False, nivel_evidencia="N1", papel="em_teste",
             motivo="A A2-4 usou o ONI da NOAA, fora da aba Resources. Volta quando o Niño 3.4 vier da TSM do ERA5.",
             validacao=[dict(ref="A2-4", caminho="loop-validacao/fichas/A2-4-el-nino-tipo-de-risco.md", resultado="passou os 3 critérios com folga pequena (BSS 0,060 contra 0,05)")],
             nao_ve=["La Niña (sem sinal)"]),
    ]

    # ------------------------------------------------------------------ estratégias
    def linha_geada(l, zarc_tab, extra=None):
        z = K.zarc_linha(zarc_tab, l["decendio"])
        out = dict(decendio=l["decendio"], em10=l["em10"], ic95=l["ic95"], k=l["k"], n=l["n"],
                   componentes=dict(agua=None, geada=l["em10"], ano_extremo=None))
        if extra:
            out["metricas_extra"] = extra
        out["zarc"] = dict(risco_pct=z["risco_pct"], indicado=z["indicado"], rastro=["R-ZARC"])
        return out

    jl = b["janela"]
    per_v4 = jl["anos_plantio"]
    plantio_verao = dict(de="21/09", ate="21/10")
    E1_ind = []
    if mist:
        c = mist["central"]
        E1_ind += [
            dict(id="I-E1-P10", tipo="p10_relativo", rotulo="Silagem no pior ano em 10, relativa ao potencial (só água, 100% milho)",
                 valor=round(c["base_p10"], 3), unidade="fracao", ic95=None, faixa_parametros=None, n_anos=c["n_safras"],
                 periodo=mist["parametros"]["safras"], nivel_evidencia="N1", modulo_id="mistura_talhao", rastro=["R-CALC-MISTURA"]),
            dict(id="I-E1-MEDIA", tipo="media_relativa", rotulo="Silagem média relativa ao potencial (só água, 100% milho)",
                 valor=round(c["base_media"], 3), unidade="fracao", ic95=None, faixa_parametros=None, n_anos=c["n_safras"],
                 periodo=mist["parametros"]["safras"], nivel_evidencia="N1", modulo_id="mistura_talhao", rastro=["R-CALC-MISTURA"]),
            dict(id="I-E1-CASOS60", tipo="casos_abaixo_60_em_10",
                 rotulo=f"Casos com silagem abaixo de 60% do potencial ({c['base_perda']} de {c['n_casos']})",
                 valor=round(10 * c["base_perda"] / c["n_casos"], 1), unidade="anos_em_10", ic95=None, faixa_parametros=None,
                 n_anos=c["n_safras"], periodo=mist["parametros"]["safras"], nivel_evidencia="N1", modulo_id="mistura_talhao",
                 rastro=["R-CALC-MISTURA"])]
    E1_ind.append(dict(id="I-E1-GEADA-AGO", tipo="geada_em_10", rotulo="Geada nas fases I a III com plantio em 1/ago",
                       valor=jan["01/08"]["em10"], unidade="anos_em_10", ic95=jan["01/08"]["ic95"], faixa_parametros=None,
                       n_anos=jan["01/08"]["n"], periodo=per_v4, nivel_evidencia="N2", modulo_id="geada_janela_safra",
                       rastro=["R-CALC-GEADA-SAFRA"]))
    E1 = dict(id="E1", nome_curto="O de sempre", nome_falado="milho para silagem no verão e pasto de inverno depois",
              e_atual=True, nivel_evidencia="N2", como_mostrar="com_faixa", ordem=1,
              sequencia=[dict(cultura="milho_silagem", estacao="verao", fracao_area=1.0, plantio=plantio_verao, manejo=None),
                         dict(cultura="pastagem_inverno", estacao="inverno", fracao_area=1.0, plantio=dict(de=None, ate=None),
                              manejo="aveia ou azevém; sem módulo próprio")],
              modulos=["geada_janela_safra", "ano_extremo_seco", "agua_isna"], indicadores=E1_ind,
              risco_por_decendio=dict(cultura_alvo="milho_silagem",
                                      evento="geada nas fases I a III (T2M_MIN < 2 °C), critério do ZARC SC; água não incluída nesta tabela",
                                      modulo_id="geada_janela_safra", rastro=["R-CALC-GEADA-SAFRA"],
                                      linhas=[linha_geada(l, zm) for l in jl["linhas"]]),
              premissas=["milho de 130 dias, fases 25/35/40/30 para a geada", "pastagem de inverno tolerante à geada (A1-1)"],
              quebra_se=[], nao_calculado=["risco da pastagem de inverno", f"falta de água por decêndio neste solo de {cad} mm"],
              solo_texto=None)

    dec_lim = G.decendio_de(G.ddmm_para_data(lim["central"]))
    # risco no dia-limite: média móvel de 5 dias da curva diária (limite = último dia com risco <= 2 em 10)
    i_lim = (G.ddmm_para_data(lim["central"]) - dt.date(2001, 1, 1)).days
    sm_lim = lim["risco_suavizado_3c"][i_lim]
    n_lim = curva[dec_lim]["n"]
    lo_w, hi_w = wilson(sm_lim * n_lim, n_lim)
    risco_lim = dict(valor=round(10 * sm_lim, 1), ic95=[round(10 * lo_w, 1), round(10 * hi_w, 1)])
    dec_tarde = G.decendio_seguinte(dec_lim)
    colh = dt.date.fromisoformat(colheita_verao) if colheita_verao else None
    de2 = G.decendio_seguinte(G.decendio_de(colh)) if colh else "21/01"
    if G.ddmm_para_data(de2) > G.ddmm_para_data(dec_lim):
        de2 = dec_lim
    E2 = dict(id="E2", nome_curto="Segundo milho",
              nome_falado=f"milho de verão e um segundo milho para silagem, plantado até o {T.fmt_data_limite(lim['central'])}",
              e_atual=False, nivel_evidencia="N2", como_mostrar="com_faixa", ordem=2,
              sequencia=[dict(cultura="milho_silagem", estacao="verao", fracao_area=1.0, plantio=plantio_verao, manejo=None),
                         dict(cultura="milho_silagem", estacao="segunda_safra", fracao_area=1.0, plantio=dict(de=de2, ate=dec_lim),
                              manejo=f"colheita do verão em {T.fmt_data_iso(colheita_verao)}" if colheita_verao else None)],
              modulos=["geada_limite_2a_safra"],
              indicadores=[
                  dict(id="I-E2-LIMITE", tipo="data_limite",
                       rotulo=(f"Último dia com geada antes da silagem em até 2 de 10 anos (3 °C). Faixa por limiar: "
                               f"{lim['por_limiar_c']['4']} (4 °C) a {lim['por_limiar_c']['2']} (2 °C); por ciclo: "
                               f"{lim['por_ciclo_gdd']['1400']} (1.400 °C·dia) a {lim['por_ciclo_gdd']['1100']} (1.100)"),
                       valor=lim["central"], unidade="dia_mes", ic95=None, faixa_parametros=None, n_anos=curva[dec_lim]["n"],
                       periodo=b["curva"]["periodo"], nivel_evidencia="N2", modulo_id="geada_limite_2a_safra", rastro=["R-CALC-LIMITE-2M"])]
              + [dict(id="I-E2-RISCO-LIMITE", tipo="geada_em_10",
                      rotulo=(f"Geada antes do ponto de silagem com plantio no dia-limite ({T.fmt_dia_mes(lim['central'])}): média móvel de 5 dias da curva diária; "
                              f"IC de Wilson tratando a média como k/{n_lim}"),
                      valor=risco_lim["valor"], unidade="anos_em_10", ic95=risco_lim["ic95"], faixa_parametros=None, n_anos=n_lim,
                      periodo=b["curva"]["periodo"], nivel_evidencia="N2", modulo_id="geada_limite_2a_safra", rastro=["R-CALC-LIMITE-2M"])]
              + [dict(id=f"I-E2-GEADA-{d[:2]}{d[3:]}", tipo="geada_em_10", rotulo=f"Geada antes do ponto de silagem, plantio em {T.fmt_dia_mes(d)}",
                      valor=curva[d]["em10"], unidade="anos_em_10", ic95=curva[d]["ic95"], faixa_parametros=None, n_anos=curva[d]["n"],
                      periodo=b["curva"]["periodo"], nivel_evidencia="N2", modulo_id="geada_limite_2a_safra", rastro=["R-CALC-GEADA-2M"])
                 for d in (dec_lim, dec_tarde)],
              risco_por_decendio=dict(cultura_alvo="milho_silagem (2ª safra)",
                                      evento="geada (T2M_MIN <= 3 °C) entre o plantio e o ponto de silagem (1.250 °C·dia, base 10 °C, teto 30 °C)",
                                      modulo_id="geada_limite_2a_safra", rastro=["R-CALC-GEADA-2M"],
                                      linhas=[linha_geada(l, zm) for l in b["curva"]["linhas"]]),
              premissas=["geada = T2M_MIN <= 3 °C no ar a 2 m (a relva fica 3 a 5 °C mais fria)", "ponto de silagem em 1.250 °C·dia, híbrido precoce"],
              quebra_se=[f"a cultivar tiver ciclo longo: com 1.400 °C·dia o limite vai para {lim['por_ciclo_gdd']['1400']}",
                         "o talhão estiver em baixada mais fria que a célula do POWER"],
              nao_calculado=["falta de água do 2º milho", "perda de silagem: o número é chance de geada, não de perda"],
              solo_texto=None)
    estrategias = [E1, E2]
    papel = {"E1": "atual", "E2": "mais_area"}
    if mist:
        c, g = mist["central"], mist["grade"]
        r1 = lambda x: round(x, 1)
        E3 = dict(id="E3", nome_curto="Metade em sorgo",
                  nome_falado="no talhão raso, metade da silagem em milho e metade em sorgo, e pasto de inverno depois",
                  e_atual=False, nivel_evidencia=modulos[4]["nivel_evidencia"], como_mostrar="com_faixa" if cad <= CAD_N2_MAX else "so_nome_em_teste",
                  ordem=3,
                  sequencia=[dict(cultura="milho_silagem", estacao="verao", fracao_area=0.5, plantio=dict(de="11/09", ate="21/10"), manejo=None),
                             dict(cultura="sorgo_silagem", estacao="verao", fracao_area=0.5, plantio=dict(de="11/09", ate="21/10"), manejo="mesma data do milho"),
                             dict(cultura="pastagem_inverno", estacao="inverno", fracao_area=1.0, plantio=dict(de=None, ate=None), manejo="aveia ou azevém; sem módulo próprio")],
                  modulos=["mistura_talhao", "agua_isna"],
                  indicadores=[
                      dict(id="I-E3-GANHO-P10", tipo="ganho_p10_pct", rotulo="Ganho no pior ano em 10 contra 100% milho, cenário central (FAO-33, R 0,88)",
                           valor=r1(c["ganho_p10"]), unidade="pct", ic95=[r1(x) for x in c["ic95_ganho_p10"]],
                           faixa_parametros=[r1(x) for x in g["ganho_p10_p10_p90"]], n_anos=c["n_safras"], periodo=mist["parametros"]["safras"],
                           nivel_evidencia="N2", modulo_id="mistura_talhao", rastro=["R-CALC-MISTURA"]),
                      dict(id="I-E3-GANHO-P10-GRADE", tipo="ganho_p10_pct", rotulo=f"Ganho no pior ano em 10, mediana da grade de {g['n']} combinações de parâmetros",
                           valor=r1(g["ganho_p10_mediana"]), unidade="pct", ic95=None, faixa_parametros=[r1(x) for x in g["ganho_p10_p10_p90"]],
                           n_anos=c["n_safras"], periodo=mist["parametros"]["safras"], nivel_evidencia="N2", modulo_id="mistura_talhao",
                           rastro=["R-CALC-MISTURA-GRADE"]),
                      dict(id="I-E3-VAR-MEDIA", tipo="var_media_pct", rotulo="Variação da silagem média contra 100% milho",
                           valor=r1(c["var_media"]), unidade="pct", ic95=[r1(x) for x in c["ic95_var_media"]],
                           faixa_parametros=[r1(x) for x in g["var_media_p10_p90"]], n_anos=c["n_safras"], periodo=mist["parametros"]["safras"],
                           nivel_evidencia="N2", modulo_id="mistura_talhao", rastro=["R-CALC-MISTURA", "R-CALC-MISTURA-GRADE"]),
                      dict(id="I-E3-SOBREVIVE", tipo="sobrevivencia_grade_pct", rotulo="Combinações da grade em que a afirmação sobrevive (corte pré-registrado: 70%)",
                           valor=r1(g["sobrevive_pct"]), unidade="pct", ic95=None, faixa_parametros=None, n_anos=c["n_safras"],
                           periodo=mist["parametros"]["safras"], nivel_evidencia="N2", modulo_id="mistura_talhao", rastro=["R-CALC-MISTURA-GRADE"])],
                  risco_por_decendio=dict(cultura_alvo="silagem total do talhão (50% milho + 50% sorgo)",
                                          evento="sem em10: a tabela mostra o pior ano em 10 por data de plantio (metricas_extra)",
                                          modulo_id="mistura_talhao", rastro=["R-CALC-MISTURA-DATA"],
                                          linhas=[dict(decendio=l["decendio"], em10=None, ic95=None, k=None, n=l["n"],
                                                       componentes=dict(agua=None, geada=round(10 * l["safras_com_geada"] / l["n"], 1), ano_extremo=None),
                                                       metricas_extra=dict(p10_base=round(l["p10_base"], 3), p10_mistura=round(l["p10_mistura"], 3),
                                                                           ganho_p10_pct=r1(l["ganho_p10_pct"]), var_media_pct=r1(l["var_media_pct"])),
                                                       zarc=dict(**K.zarc_linha(zm, l["decendio"]), rastro=["R-ZARC"]))
                                                  for l in mist["por_data"]]),
                  premissas=[f"silagem de sorgo vale {round(100 * M.CENTRAL['R'])}% da de milho (R = {M.CENTRAL['R']}; literatura externa: Embrapa e Demarchi)",
                             "Ky e Kc da FAO para grão aplicados à silagem",
                             f"CAD do talhão {cad} mm = 65 mm/m (classe areia do GAEZ, aplicada ao raso sem teste) x 0,6 m de raiz (ZARC)"],
                  quebra_se=["Ky do sorgo for 1,64 vez o da FAO ou mais (V3, CAD 42 mm)",
                             "milho e sorgo responderem igual à seca (Ky = 1 nos dois)",
                             "R abaixo de 0,77: aí a média cai (V3, CAD 42 mm)"],
                  nao_calculado=["custo e rebrota do sorgo", "rendimento observado de sorgo em SMO"], solo_texto=None)
        estrategias.append(E3)
        papel["E3"] = "melhora_pior_ano"
    E4 = dict(id=f"E{len(estrategias) + 1}", nome_curto="Sorgo depois do milho", nome_falado="milho de verão e sorgo forrageiro na segunda safra",
              e_atual=False, nivel_evidencia="N1", como_mostrar="so_nome_em_teste", ordem=4,
              sequencia=[dict(cultura="milho_silagem", estacao="verao", fracao_area=1.0, plantio=plantio_verao, manejo=None),
                         dict(cultura="sorgo_forrageiro", estacao="segunda_safra", fracao_area=1.0, plantio=dict(de=None, ate=None), manejo="sem data calculada")],
              modulos=["sorgo_2a_safra"], indicadores=[], risco_por_decendio=None, premissas=[], quebra_se=[],
              nao_calculado=["geada do sorgo de 2ª safra", "água do sorgo de 2ª safra"], solo_texto=None)
    estrategias.append(E4)
    D.ordenar(estrategias, prioridade, papel)

    # ------------------------------------------------------------------ alerta
    aid = f"A-SECO-{str(al['ano_safra'] - 1)[2:]}{str(al['ano_safra'])[2:]}"
    # a janela do alerta é a que o índice usou de verdade: vai até o corte (data de referência ou 10/jan)
    fim_efetivo = al["ate"] or al["janela"]["ate"]
    ate_txt = dt.date.fromisoformat(fim_efetivo).strftime("%d/%m")
    alerta = dict(id=aid, modulo_id="ano_extremo_seco", estado=al["estado"], nivel_evidencia="N2",
                  janela=dict(de=al["janela"]["de"], ate=fim_efetivo),
                  indice=dict(nome=f"ISNA do milho de 20/set a {ate_txt} (solo médio 125 mm, regra da B3-1)",
                              valor=None if al["indice"] is None else round(al["indice"], 3), unidade="fracao"),
                  percentil_local=dict(valor=al["percentil"], limiar=A.LIMIAR_PCT, n_anos_passados=al["n_anos_passados"],
                                       periodo_passado=al["periodo_passado"]),
                  frase_probabilidade=dict(anos_assim_ruins_em_10=val["anos_assim_ruins_em_10"],
                                           ano_qualquer_ruim_em_10=val["ano_qualquer_ruim_em_10"],
                                           definicao_ruim="rendimento da PAM <= 85% da mediana móvel (quebra de 15% ou mais), por microrregião; percentil só do passado; só auditoria",
                                           eventos_testados=val["eventos"], rastro=["R-CALC-ALERTA-VALID", "R-PAM-SC"]),
                  recall_pct=val["recall_pct"], silencio_nao_e_seguranca=True, rastro=["R-CALC-ISNA-SECO", "R-CALC-PERCENTIL"])

    # ------------------------------------------------------------------ rastro
    viz_txt = "; ".join(f"{C.NOME_PONTO[n]}: {v['dias_diferentes']} de {v['de']} dias diferentes" for n, v in b["viz"].items())
    mesma = [C.NOME_PONTO[n] for n, v in b["viz"].items() if v["dias_diferentes"] == 0]
    rastro = [D.dado_power("R-POWER-SMO", pw, "Série diária do NASA POWER no ponto de SMO, comunidade AG.",
                           "PRECTOTCORR, T2M, T2M_MAX, T2M_MIN, RH2M, WS2M, ALLSKY_SFC_SW_DWN")]
    for n in VIZINHOS:
        p2 = Power(C.POWER[n])
        rastro.append(D.dado_power(f"R-POWER-{n.upper().replace('_', '-')}", p2,
                                   f"Série diária do NASA POWER em {C.NOME_PONTO[n]}, só para conferir se a célula é a mesma de SMO.", "T2M_MIN"))
    rastro += [
        D.calculo("R-CALC-CELULA", f"Dias com T2M_MIN diferente entre SMO e vizinhos. {viz_txt}.", me / "power.py", "mesma_celula",
                  dict(variavel="T2M_MIN", tolerancia_c=0.005), ["R-POWER-SMO"] + [f"R-POWER-{n.upper().replace('_', '-')}" for n in VIZINHOS],
                  arq_calc, "mesma_celula", periodo=pw.periodo),
        D.item("R-PROD-SOLO", "pergunta", f"Resposta do produtor no WhatsApp (T15): talhão '{solo_declarado}'.", "produtor", "produtor", variavel="solo_declarado"),
        D.item("R-PROD-COLHEITA", "pergunta", f"Resposta do produtor: colheita do verão em {colheita_verao}.", "produtor", "produtor", variavel="colheita_verao"),
        D.item("R-PROD-PRIORIDADE", "pergunta", f"Resposta do produtor (T12): prioridade '{prioridade}'. Só muda a ordem dos cartões.", "produtor", "produtor", variavel="prioridade"),
        D.GAEZ(C.RAIZ / "prototipo" / "modelo" / "risco.py"),
        D.RAIZ_RASO(), D.LIMIAR_GEADA(), D.R_SORGO(),
        D.calculo("R-CALC-CAD", f"CAD = {SOLO_MM_M[solo_declarado]} mm/m (GAEZ{', classe areia aplicada ao raso' if raso else ''}) x {RAIZ_M[solo_declarado]} m de raiz{' (ZARC)' if raso else ''} = {cad} mm.",
                  me / "locais" / "sao_miguel_do_oeste.py", "avaliar", dict(mm_por_m=SOLO_MM_M[solo_declarado], raiz_m=RAIZ_M[solo_declarado]),
                  ["R-PROD-SOLO", "R-GAEZ-CAD"] + (["R-PARAM-RAIZ-RASO"] if raso else []), arq_calc, "cad"),
        D.FAO56(), D.FAO33(),
        D.calculo("R-CALC-GEADA-SAFRA", f"Geada (T2M_MIN < 2 °C) nas fases I a III do milho de verão, por decêndio de plantio, {jan['01/08']['n']} safras. Reproduz V4 D1.",
                  me / "geada.py", "tabela_janela_safra", dict(limiar_c=G.LIMIAR_SAFRA, fases_dias=list(G.FASES_MILHO_V4), anos_plantio=per_v4),
                  ["R-POWER-SMO", "R-PARAM-LIMIAR-GEADA"], arq_calc, "geada_janela_safra.linhas", periodo=per_v4, variavel="em10"),
        D.calculo("R-CALC-GEADA-2M", f"Chance de geada antes do ponto de silagem do 2º milho, por decêndio de plantio, {curva[dec_lim]['n']} anos, IC de Wilson. Reproduz V2.",
                  me / "geada.py", "curva_2m", dict(limiar_c=3.0, gdd_alvo=G.GDD_PADRAO, base_c=10, teto_c=30),
                  ["R-POWER-SMO"], arq_calc, "geada_2a_safra.linhas", periodo=b["curva"]["periodo"], variavel="em10"),
        D.calculo("R-CALC-LIMITE-2M", "Último dia de plantio com risco <= 2 em 10 (média móvel de 5 dias), por limiar (2, 3, 4 °C) e por ciclo (1.100, 1.250, 1.400 °C·dia).",
                  me / "geada.py", "limites_2m", dict(corte_em10=2, limiar_c=3.0, gdd_alvo=G.GDD_PADRAO, media_movel_dias=5),
                  ["R-POWER-SMO"], arq_calc, "limite_2a_safra", periodo=b["curva"]["periodo"], variavel="limite"),
        D.calculo("R-CALC-ISNA-SECO", (f"ISNA do milho de 20/set até {ate_txt} por safra (solo médio 125 mm, fases 25/40/45/30, p 0,5; balde da B3). "
                                       f"Safra {safra} = {alerta['indice']['valor']}."),
                  me / "balanco.py", "isna_milho_b31", dict(plantio="20/09", decisao="10/01", cad_mm=125.0, p_depl=0.5, kc=[0.3, 1.2, 0.6],
                                                           et0=dict(alt_m=pw.alt, piso_mm=pw.piso)),
                  ["R-POWER-SMO", "R-FAO56"], arq_calc, "alerta_seco.indice e alerta_seco.serie_passada", periodo=pw.periodo, variavel="isna"),
        D.calculo("R-CALC-PERCENTIL", (f"Posição do ISNA {safra} entre {al['n_anos_passados']} anos passados da célula ({al['periodo_passado']}). "
                                       f"Mínimo passado: {al['minimo_passado']['valor']} em {al['minimo_passado']['ano']}."),
                  me / "ano_extremo.py", "percentil_passado", dict(limiar_percentil=A.LIMIAR_PCT, so_anos_passados=True, ano_inicio=A.ANO_INICIO_PERCENTIL),
                  ["R-CALC-ISNA-SECO"], arq_calc, "alerta_seco.percentil", periodo=al["periodo_passado"], variavel="percentil_local"),
        D.item("R-POWER-V1", "dado", "NASA POWER diário de 8 células novas de SC usadas na validação do alerta (V1).", "NASA_POWER", "resources",
               variavel="PRECTOTCORR, T2M, T2M_MAX, T2M_MIN, RH2M, WS2M, ALLSKY_SFC_SW_DWN", periodo="1984-2025", resolucao="~50 km",
               arquivo=C.VAL / "V1" / "power"),
        D.calculo("R-CALC-ALERTA-VALID", (f"Validação da regra '10% mais secos da célula', percentil só do passado, em 8 células novas: {val['acertos']} de {val['alertas']} alertas em ano ruim "
                                          f"contra taxa-base {val['taxa_base']}; {val['eventos_acerto']} de {val['eventos']} eventos ({val['eventos_novos']} novos); recall {val['recall']}. Só auditoria."),
                  C.VAL / "V1" / "v1_passo6_so_passado.py", None,
                  dict(corte_ano_ruim=0.85, limiar_percentil=10, min_anos_passados=15, so_auditoria=True,
                       lido_por="solucao/motor/ano_extremo.py validacao_v1", perde_em_10=round(10 * (1 - val["recall"]), 1)),
                  ["R-POWER-V1", "R-PAM-SC"], C.V1_SO_PASSADO, "so_anos_com_historico", periodo="1990-2025"),
    ]
    if srtm:
        rastro.append(D.item("R-SRTM-T", "dado", "Declive e TPI (90 m) do SRTM de 30 m no ponto do perfil P7 da UDESC (Neossolo Litólico, topo). Regra 'confirme': declive >= 15% ou TPI >= 2 m (limiar escolhido depois de ver os perfis).",
                             "SRTM", "resources", variavel="elevação 1 arco-segundo", url="https://s3.amazonaws.com/elevation-tiles-prod/skadi/S27/S27W054.hgt.gz",
                             resolucao="30 m", arquivo=C.SRTM_V3))
    if mist:
        c = mist["central"]
        rastro += [
            D.calculo("R-CALC-MISTURA", (f"Silagem do talhão com 0% e 50% de sorgo, CAD {cad} mm, Ky FAO-33, R {M.CENTRAL['R']}; bootstrap por safra "
                                         f"({c['nb']} sorteios, semente {c['semente']}). Cópia de V3/modelo_v3.py."),
                      me / "mistura.py", "central", dict(cad_mm=cad, fracao_sorgo=M.CENTRAL["fracao_sorgo"], R=M.CENTRAL["R"], cenario=M.CENTRAL["scen"],
                                                         et0=dict(alt_m=533.0, piso_mm=0.3)),
                      ["R-POWER-SMO", "R-FAO56", "R-FAO33", "R-CALC-CAD", "R-PARAM-R-SORGO", "R-PARAM-LIMIAR-GEADA"], arq_calc, "mistura.central", periodo=mist["parametros"]["safras"]),
            D.calculo("R-CALC-MISTURA-GRADE", f"Grade pré-definida da V3 ({mist['grade']['n']} combinações: cenário, Ky e Kc do sorgo, deslocamento, R), CAD {cad} mm.",
                      me / "mistura.py", "grade", dict(cad_mm=cad, grade={k: list(v) for k, v in M.GRADE.items()}, regra_ok="ganho P10 > 0 e média >= -3%"),
                      ["R-POWER-SMO", "R-FAO56", "R-FAO33", "R-CALC-CAD", "R-PARAM-R-SORGO", "R-PARAM-LIMIAR-GEADA"], arq_calc, "mistura.grade", periodo=mist["parametros"]["safras"]),
            D.calculo("R-CALC-MISTURA-DATA", f"Pior ano em 10 por data de plantio, CAD {cad} mm, FAO-33, R {M.CENTRAL['R']}. Cópia de V3/v3_03_extras.py (por_data).",
                      me / "mistura.py", "por_data", dict(cad_mm=cad, fracao_sorgo=0.5),
                      ["R-POWER-SMO", "R-FAO56", "R-FAO33", "R-CALC-CAD", "R-PARAM-R-SORGO", "R-PARAM-LIMIAR-GEADA"], arq_calc, "mistura.por_data", periodo=mist["parametros"]["safras"]),
        ]
    rastro += [
        D.item("R-ZARC", "conferencia", f"ZARC 2026/27, SMO, sequeiro: milho 1ª safra grupo I {ad} ({K.AD_MM[ad]} mm, a classe mais perto do CAD {cad} mm); sorgo forrageiro 1ª safra. Não há milho 2ª safra no ZARC de SC.",
               "ZARC", "externo_conferencia", variavel="risco por decêndio", url="https://dados.agricultura.gov.br", periodo="safra 2026/27",
               resolucao="município", arquivo=C.ZARC_SC),
        D.item("R-PAM-SC", "conferencia", "IBGE PAM, rendimento do milho por microrregião de SC, relativo à mediana móvel (t-3 a t+3).",
               "IBGE_PAM", "externo_conferencia", variavel="rendimento (kg/ha)", url="https://apisidra.ibge.gov.br/values/t/1612/n9/42001/v/112/p/all/c81/2711",
               periodo="1990-2025", resolucao="microrregião", arquivo=C.PAM_V1),
    ]

    # ------------------------------------------------------------------ conferências
    conferencias = []
    dias = lambda a, b_: (G.ddmm_para_data(b_) - G.ddmm_para_data(a)).days
    z20 = next((d for d, r in zm.items() if r == 20), None)
    if seguro and z20:
        dd = G.indice_decendio(seguro) - G.indice_decendio(z20)
        conferencias.append(dict(id="K-ZARC-E1", contra="ZARC_2026_27", o_que="Milho de verão: 1º decêndio de baixo risco",
                                 resultado="bate" if abs(dd) <= 1 else "nao_bate",
                                 detalhe=(f"ZARC {ad}: 1º decêndio com 20% em {z20}; motor, em {seguro} ({abs(dd)} decêndio(s) de diferença; critério A3: até 1). "
                                          f"A forma bate, a magnitude não: em 01/08 e 11/08 o ZARC dá {zm.get('01/08')}% e {zm.get('11/08')}%; o motor, {jan['01/08']['em10']} e {jan['11/08']['em10']} em 10. O POWER parece exagerar a geada (V6)."),
                                 rastro=["R-ZARC", "R-CALC-GEADA-SAFRA"]))
    ult = max((d for d in zm if d[3:] == "01"), key=lambda d: int(d[:2]), default=None)
    if ult:
        dd = dias(ult, lim["central"])
        conferencias.append(dict(id="K-ZARC-E2", contra="ZARC_2026_27", o_que="Último plantio do 2º milho",
                                 resultado="bate" if abs(dd) <= 20 else "nao_bate",
                                 detalhe=f"Último decêndio de milho no ZARC: {ult}. Limite do motor: {lim['central']} ({dd} dias depois; critério A3 da spec: até 20 dias).",
                                 rastro=["R-ZARC", "R-CALC-LIMITE-2M"]))
    if mist:
        zs = K.zarc_sorgo_forrageiro("sao_miguel_do_oeste")
        decs = [l["decendio"] for l in mist["por_data"]]
        menor = [d for d in decs if zs.get(d) is not None and (zm.get(d) is None or zs[d] < zm[d])]
        conferencias.append(dict(id="K-ZARC-E3", contra="ZARC_2026_27", o_que="Sorgo mais seguro que milho em solo de pouca água",
                                 resultado="bate" if len(menor) == len(decs) else ("bate_em_parte" if menor else "nao_bate"),
                                 detalhe=(f"De {decs[0]} a {decs[-1]}: sorgo forrageiro com risco menor que o milho {ad} em {len(menor)} de {len(decs)} decêndios "
                                          f"(sorgo {sorted({zs.get(d) for d in decs}, key=str)}%, milho {sorted({zm.get(d) for d in decs}, key=str)}%). Em AD5-AD6 o ZARC põe os dois iguais (V6)."),
                                 rastro=["R-ZARC", "R-CALC-MISTURA"]))
    rel = K.pam_rel("SMO 42001", al["ano_safra"])
    if rel is not None and al["estado"] in ("ativo", "inativo"):
        ruim = rel <= 0.85
        bate = (al["estado"] == "ativo") == ruim
        conferencias.append(dict(id="K-PAM-A", contra="IBGE_PAM", o_que=f"A safra {safra} foi de quebra?",
                                 resultado="bate" if bate else "nao_bate",
                                 detalhe=(f"Microrregião 42001 em {al['ano_safra']}: rendimento a {round(rel, 3)} da mediana ({'quebra de 15% ou mais' if ruim else 'sem quebra forte'}). "
                                          f"Alerta: {al['estado']}. Esta safra já estava na amostra da B3: não conta como teste novo."),
                                 rastro=["R-PAM-SC"]))
    if safra == "2021/22":
        rastro.append(D.item("R-EPAGRI-2022", "conferencia", "Epagri/Cepa, jan/2022: perda média estimada de 43% no milho de SC, com o Oeste como região mais atingida (citado na ficha A1-1).",
                             "Epagri", "externo_conferencia", periodo="2022", resolucao="estado", arquivo=C.FICHA_A1_1))
        conferencias.append(dict(id="K-EPAGRI-A", contra="Epagri", o_que="A estiagem de 2021/22 no Oeste", resultado="bate" if al["estado"] == "ativo" else "nao_bate",
                                 detalhe="Perda média estimada de 43% no milho de SC, com o Oeste como região mais atingida.", rastro=["R-EPAGRI-2022"]))

    # ------------------------------------------------------------------ documento (sem cartões)
    doc = dict(versao_contrato=C.VERSAO_CONTRATO, gerado_em=D.agora(), modo=modo, data_referencia=data_referencia, safra=safra,
               motor=dict(versao=C.VERSAO_MOTOR, commit=None),
               local=dict(LOCAL, ponto_power=dict(lat=pw.lat_grade, lon=pw.lon, alt_grade_m=pw.alt_grade, resolucao_km=50, mesma_celula_que=mesma),
                          dentro_da_area_testada=C.regiao_do_ponto(LOCAL["lat"], LOCAL["lon"]) == "sc_extremo_oeste"),
               talhao=dict(id=D.slug_talhao(nome_talhao),
                           nome=nome_talhao, area_ha=None, solo_declarado=solo_declarado,
                           cad_mm=dict(valor=cad, fonte="pergunta+gaez" if solo_declarado != "nao_sei" else "padrao_regiao",
                                       nota=(f"{SOLO_MM_M[solo_declarado]} mm/m (classe areia do GAEZ, aplicada ao solo raso: o GAEZ não mede profundidade e isso não foi testado) "
                                             f"x {RAIZ_M[solo_declarado]} m (raiz do ZARC) = {cad} mm. A V3 validou com 42 mm; o motor reproduz a V3 com 42 mm nos testes.") if raso else None,
                                       rastro=["R-PROD-SOLO", "R-GAEZ-CAD", "R-CALC-CAD"]),
                           srtm=dict(srtm, nivel_evidencia="N1", rastro=["R-SRTM-T"]) if srtm else None,
                           ciclo_gdd=dict(valor=G.GDD_PADRAO, fonte="padrao"), colheita_verao=colheita_verao, fotos_registro=fotos or []),
               produtor=dict(id_pseudonimo=id_produtor, prioridade=prioridade, atividade="leite_milho"),
               regiao=dict(id="sc_extremo_oeste", nome=C.REGIOES["sc_extremo_oeste"]["nome"], papel="principal",
                           modulos_ativos=[m["id"] for m in modulos if m["ativo"]]),
               modulos=modulos, estrategias=estrategias, alertas=[alerta], cartoes=[], rastro=rastro,
               conferencias=conferencias, limites=[], nao_sei=dict(ativo=False, motivos=[], encaminhar_para="tecnico_ater"))

    # ------------------------------------------------------------------ cartões
    D.virgula_decimal(doc)
    P = D.Ptr(doc)
    KM = D.var(doc, "/local/ponto_power/resolucao_km", T.fmt_int)
    cart = []
    if alerta["estado"] == "ativo":
        cart.append(("T05_ANO_SECO_ATIVO", dict(
            inicio=D.var(doc, P.alerta(aid, "janela", "de"), T.fmt_data_iso),
            fim=D.var(doc, P.alerta(aid, "janela", "ate"), T.fmt_data_iso),
            n_anos=D.var(doc, P.alerta(aid, "percentil_local", "n_anos_passados"), T.fmt_int),
            km=KM), None, [aid], None))
    elif alerta["estado"] == "inativo":
        cart.append(("T06_ANO_SECO_SILENCIO", dict(
            n_anos=D.var(doc, P.alerta(aid, "percentil_local", "n_anos_passados"), T.fmt_int), km=KM), None, [aid], None))
    # planejamento do milho de verão (T02/T03): vale para qualquer data, a UI mostra quando a pergunta é essa
    lin0 = next(l for l in E1["risco_por_decendio"]["linhas"] if l["em10"] == 0)
    cart.append(("T02_GEADA_JANELA_SAFRA", dict(
        r_ago=D.var(doc, P.linha("E1", "01/08", "em10"), T.fmt_em10),
        **D.faixa(doc, P.linha("E1", "01/08", "ic95"), "lo", "hi"),
        data_segura=D.var(doc, P.linha("E1", lin0["decendio"], "decendio"), T.fmt_dia_mes),
        r_seguro=D.var(doc, P.linha("E1", lin0["decendio"], "em10"), T.fmt_em10)), ["E1"], None,
        dict(tipo="janela_decendios", legenda="Anos em 10 com geada nas fases I a III, por decêndio de plantio")))
    resto = [l for l in E1["risco_por_decendio"]["linhas"] if G.ddmm_para_data(l["decendio"]) >= G.ddmm_para_data(lin0["decendio"])]
    if max(l["em10"] for l in resto) - min(l["em10"] for l in resto) < 1:
        cart.append(("T03_TANTO_FAZ_DATA", dict(
            de=D.var(doc, P.linha("E1", resto[0]["decendio"], "decendio"), T.fmt_dia_mes),
            ate=D.var(doc, P.linha("E1", resto[-1]["decendio"], "decendio"), T.fmt_dia_mes)), ["E1"], None, None))
    # T01: compara, na ordem da prioridade
    ordem_est = sorted(estrategias, key=lambda e: e["ordem"])[:4]
    v01 = dict(talhao=D.var(doc, "/talhao/nome", str), km=KM)
    sacos = []
    for i, e in enumerate(ordem_est, 1):
        eid = e["id"]
        v01[f"nome_{i}"] = D.var(doc, P.est(eid, "nome_curto"), str)
        if e["nivel_evidencia"] in ("N1", "N0"):
            sacos.append(D.saco(e["nome_curto"], None, "N1"))
        elif eid == "E3" and mist:
            v01[f"s_{i}"] = D.var(doc, P.ind("E3", "I-E3-SOBREVIVE"), lambda x: T.fmt_em10(x / 10))
        elif eid == "E2":
            v01[f"limite_{i}"] = D.var(doc, P.ind("E2", "I-E2-LIMITE"), T.fmt_dia_mes)
            v01[f"r_{i}"] = D.var(doc, P.ind("E2", "I-E2-RISCO-LIMITE"), T.fmt_em10)
            v01.update(D.faixa(doc, P.ind("E2", "I-E2-RISCO-LIMITE", "ic95"), f"lo_{i}", f"hi_{i}"))
            sacos.append(D.saco(f"2º milho até {D.dia_curto(lim['central'])}", risco_lim["valor"], "N2"))
        elif e["e_atual"]:
            v01[f"falado_{i}"] = D.var(doc, P.est(eid, "nome_falado"), str)
    cart.append(("T01_COMPARA_ESTRATEGIAS", v01, [e["id"] for e in ordem_est], [aid] if alerta["estado"] == "ativo" else None,
                 dict(tipo="10_sacos", linhas=sacos, legenda=f"Saco rasgado = ano com geada antes do corte da silagem ({curva[dec_lim]['n']} anos)")))
    for e in sorted(estrategias, key=lambda e: e["ordem"]):
        if e["id"] == "E2":
            cart.append(("T04_GEADA_LIMITE_2A_SAFRA", dict(
                limite=D.var(doc, P.ind("E2", "I-E2-LIMITE"), T.fmt_dia_mes),
                r_lim=D.var(doc, P.ind("E2", "I-E2-RISCO-LIMITE"), T.fmt_em10),
                **D.faixa(doc, P.ind("E2", "I-E2-RISCO-LIMITE", "ic95"), "lo", "hi"),
                data_tarde=D.var(doc, P.linha("E2", dec_tarde, "decendio"), T.fmt_dia_mes),
                r_tarde=D.var(doc, P.linha("E2", dec_tarde, "em10"), T.fmt_em10),
                **D.faixa(doc, P.linha("E2", dec_tarde, "ic95"), "lo_t", "hi_t"),
                km=KM), ["E2"], None,
                dict(tipo="10_sacos", linhas=[D.saco(f"Plantio até {D.dia_curto(lim['central'])}", risco_lim["valor"], "N2"),
                                              D.saco(f"Plantio em {D.dia_curto(dec_tarde)}", curva[dec_tarde]["em10"], "N2")],
                     legenda=f"Saco rasgado = ano com geada antes do corte da silagem ({curva[dec_lim]['n']} anos)")))
        elif e["id"] == "E3" and mist:
            cart.append(("T07_MISTURA_TALHAO_RASO", dict(
                talhao=D.var(doc, "/talhao/nome", str),
                s=D.var(doc, P.ind("E3", "I-E3-SOBREVIVE"), lambda x: T.fmt_em10(x / 10))), ["E3", "E1"], None, None))
    if solo_declarado == "nao_sei" or (srtm and srtm["marca_confirme"] and solo_declarado != "raso_ou_pedregoso"):
        cart.append(("T15_PEDE_SOLO", dict(talhao=D.var(doc, "/talhao/nome", str)), None, None, None))
    for f in (fotos or []):
        cart.append(("T13_FOTO_REGISTRO", dict(talhao=D.var(doc, "/talhao/nome", str)), None, None, None))
    if prioridade == "nao_informado":
        cart.append(("T12_PRIORIDADE", {}, None, None, None))
    for i, (tid, vs, eids, aids, img) in enumerate(cart, 1):
        doc["cartoes"].append(D.cartao(doc, f"C-{i:02d}", tid, "whatsapp", i, vs, eids, aids, img))

    # ------------------------------------------------------------------ limites
    cids = [c["id"] for c in doc["cartoes"]]
    eids = [e["id"] for e in estrategias]
    sat = T.DADOS_SATELITE.format(km=50)
    lims = [
        dict(id="X-REPLAY", texto="Modo replay: as tabelas de geada e a mistura usam anos até 2024 ou 2025, depois da data de referência. Só o percentil do alerta usa apenas anos passados.",
             gravidade="media", afeta=[x for x in ("E1", "E2", "E3") if x in eids] + [aid], mostrar_ao_agricultor=False) if modo == "replay" else None,
        dict(id="X-GRADE", texto=f"Chuva e temperatura vêm de uma grade de ~50 km.{' ' + ', '.join(mesma) + ' cai na mesma célula.' if mesma else ''}",
             gravidade="alta", afeta=[x for x in ("E1", "E2", "E3") if x in eids] + [aid], mostrar_ao_agricultor=True, trecho=sat),
        dict(id="X-AGUA-2M", texto="A falta de água do 2º milho não foi calculada.", gravidade="alta", afeta=["E2"], mostrar_ao_agricultor=True,
             trecho="Não calculamos a falta de água"),
        dict(id="X-GEADA-PERDA", texto="O risco de geada é a chance de o evento ocorrer, não de perder a silagem.", gravidade="media", afeta=["E1", "E2"], mostrar_ao_agricultor=False),
        dict(id="X-GEADA-ESPACO", texto="A data-limite do 2º milho muda 29 dias entre SMO e Concórdia (grade a 884 m) e 22 dias com o ciclo (V2). Vale só para esta célula.",
             gravidade="alta", afeta=["E2"], mostrar_ao_agricultor=False),
        dict(id="X-GEADA-MAGNITUDE", texto=f"A geada do POWER (< 2 °C) dá {jan['01/08']['em10']} em 10 em 1/ago; o risco total do ZARC é 4 em 10. A forma bate, a magnitude não: o POWER parece exagerar (V6). Não foi calibrado.",
             gravidade="media", afeta=["E1"], mostrar_ao_agricultor=False),
        dict(id="X-RECALL", texto=f"O alerta perde cerca de {100 - val['recall_pct']}% dos anos ruins (percentil só do passado, V1 passo 6). Silêncio não quer dizer ano seguro.",
             gravidade="alta", afeta=[aid], mostrar_ao_agricultor=alerta["estado"] in ("ativo", "inativo"),
             trecho="o aviso não pega todos os anos ruins" if alerta["estado"] in ("ativo", "inativo") else None),
        dict(id="X-ALERTA-VALIDACAO", texto=(f"A regra do alerta falha C1 ({val['eventos_acerto']} de {val['eventos']} eventos, abaixo de 50%) e C3 (rendimento relativo médio {val['rel_medio_alerta']}, "
                                             f"acima de 0,85) da V1. Eventos novos: {val['eventos_novos']}. A frase de probabilidade usa o IBGE PAM e fica só na auditoria."),
             gravidade="alta", afeta=[aid], mostrar_ao_agricultor=False),
        dict(id="X-PARAM-EXTERNO", texto="Três valores do cálculo vêm de literatura fora da aba Resources: R = 0,88 (Embrapa; Demarchi), raiz de 0,6 m do solo raso e limiar de geada de 2 °C (os dois do ZARC). Exceção à regra de dados: o time decide se aceita.",
             gravidade="alta", afeta=[x for x in ("E1", "E3") if x in eids], mostrar_ao_agricultor=False),
        dict(id="X-USUARIO", texto="Mensagens e cartões não foram testados com produtores nem técnicos.", gravidade="media", afeta=cids, mostrar_ao_agricultor=False),
    ]
    if mist:
        lims += [
            dict(id="X-KY-SORGO", texto="Ky do sorgo não calibrado. Na V3 (CAD 42 mm) o ganho some se o Ky real for 1,64 vez o da FAO ou se milho e sorgo responderem igual à seca.",
                 gravidade="alta", afeta=["E3"], mostrar_ao_agricultor=False),
            dict(id="X-NIVEL", texto="O nível absoluto de silagem simulado não foi confirmado: no CAD de 42 mm, o milho simulado tem Spearman 0,10 com a PAM de SMO (V3).",
                 gravidade="media", afeta=["E1", "E3"], mostrar_ao_agricultor=False),
            dict(id="X-CAD", texto=(f"CAD de {cad} mm. A V3 validou com 42 mm. Com {cad} mm o motor dá central de {round(mist['central']['ganho_p10'], 1)}% (IC {round(mist['central']['ic95_ganho_p10'][0], 1)} a "
                                    f"{round(mist['central']['ic95_ganho_p10'][1], 1)}), contra 39,6% da V3: sobe cerca de 7 pontos. Ganho em {mist['safras_ganho']} de {mist['central']['n_safras']} safras; perda em {mist['safras_perda']}."),
                 gravidade="media", afeta=["E1", "E3"], mostrar_ao_agricultor=False),
            dict(id="X-GAEZ-RASO", texto="O 65 mm/m é a classe areia do GAEZ aplicada ao talhão raso. O GAEZ não mede profundidade e isso não foi testado (V3).",
                 gravidade="media", afeta=["E3"], mostrar_ao_agricultor=False),
            dict(id="X-GRADE-CORTE", texto=f"A mistura sobrevive em {round(mist['grade']['sobrevive_pct'], 1)}% da grade de parâmetros, abaixo do corte de 70% pré-registrado na V3. Por isso fica N2 e com faixa.",
                 gravidade="media", afeta=["E3"], mostrar_ao_agricultor=False),
            dict(id="X-SRTM", texto="O SRTM só pede para confirmar o solo raso. Ele não mede profundidade.", gravidade="media", afeta=["E3"], mostrar_ao_agricultor=False),
            dict(id="X-BOOT", texto="O IC95 do bootstrap usa o gerador da biblioteca padrão (semente 20261114); a V3 usou numpy, então o IC difere um pouco. O valor central é igual.",
                 gravidade="baixa", afeta=["E3"], mostrar_ao_agricultor=False),
        ]
    doc["limites"] = [{**l, "trecho": l.get("trecho")} for l in lims if l]
    D.virgula_decimal(doc)
    return doc, calculos


def gerar():
    doc, calc = avaliar()
    D.gravar(doc, calc, SLUG)
    return doc
