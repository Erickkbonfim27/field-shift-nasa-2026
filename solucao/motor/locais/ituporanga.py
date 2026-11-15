"""Ituporanga (SC): cebola (spec-v2 seção 4.2).

Módulos ativos: exposicao_solo (N2 descritivo: fato medido), ano_extremo_excesso (N1: só
histórico, na auditoria), agua_isna (N1, insumo do excedente). preco_cebola e
data_transplante_cebola ficam desligados (pré-registro falhou; V4 D2 contradiz o ZARC).
Ituporanga NÃO fecha 3 rotações com número: duas das três estratégias são "em teste".
"""
import datetime as dt
from .. import config as C
from .. import documento as D
from .. import textos as T
from .. import ano_extremo as A
from .. import exposicao as X
from .. import conferencia as K
from ..power import Power, mesma_celula

SLUG = "ituporanga"
LOCAL = dict(id="L-ituporanga", municipio="Ituporanga", uf="SC", codigo_ibge="4208500", lat=-27.414, lon=-49.601)
VIZINHOS = ("rio_do_sul", "alfredo_wagner")
SOLO_MM_M = {"arenoso": 65, "medio": 125, "argiloso": 175, "raso_ou_pedregoso": 65, "nao_sei": 125}
RAIZ_CEBOLA_M = 0.3


def avaliar(data_referencia="2024-09-02", modo="replay", solo_declarado="medio", prioridade="solo",
            nome_talhao="Encosta da cebola", id_produtor="P-7c1d0e42"):
    dref = dt.date.fromisoformat(data_referencia)
    pw = Power(C.POWER["ituporanga"])
    viz = {n: mesma_celula(pw, Power(C.POWER[n])) for n in VIZINHOS}
    mesma = [C.NOME_PONTO[n] for n, v in viz.items() if v["dias_diferentes"] == 0]
    ano_ref = dref.year if dref.month >= 9 else dref.year - 1  # último inverno completo
    ex = X.avaliar(pw, C.S2_BLOCOS, ano_ref)
    hist = A.historico_excesso(pw, dref.year)
    cad = round(SOLO_MM_M[solo_declarado] * RAIZ_CEBOLA_M, 1)
    safra = f"{dref.year}/{str(dref.year + 1)[2:]}"
    arq_calc = C.CALCULOS / f"{SLUG}.json"
    me = C.MOTOR
    calculos = dict(local=LOCAL, data_referencia=data_referencia, mesma_celula=viz, exposicao_solo=ex,
                    historico_excesso=hist, cad=dict(solo=solo_declarado, mm_m=SOLO_MM_M[solo_declarado], raiz_m=RAIZ_CEBOLA_M, cad_mm=cad))

    modulos = [
        dict(id="exposicao_solo", nome="Solo descoberto em mês de chuva forte", ativo=True, nivel_evidencia="N2", papel="descritivo",
             motivo="Fato medido: solo descoberto pelo Sentinel-2 e chuva erosiva pelo POWER. O benefício (solo salvo) não é calculado (N1).",
             validacao=[dict(ref="A3-1", caminho="loop-validacao/fichas/A3-1-alerta-erosao.md",
                             resultado="erosividade do POWER: Spearman 0,85 com o pluviômetro (Back et al. 2023); 64% dos talhões-ano com pico fora de out-fev; p90/p10 = 9")],
             nao_ve=["perda de solo em t/ha", "terraço, curva de nível e palha que o NDVI não separa", "meses sem cena limpa"]),
        dict(id="ano_extremo_excesso", nome="Primaveras de chuva extrema na cebola (só histórico)", ativo=True, nivel_evidencia="N1", papel="descritivo",
             motivo="O limiar de 360 mm da B3-3 era o P90 da amostra. Fora do Alto Vale: 22% contra 12,7%, p = 0,39 (V1). Fica só como histórico, na auditoria.",
             validacao=[dict(ref="V1", caminho="solucao/validacao/V1/relatorio.md", resultado="cebola: regra fixa caiu nos ataques A1, A2 e A3; fora do Alto Vale 11 de 49 = 22%, p = 0,39")],
             nao_ve=["míldio e doença", "chuva na colheita", "preço"]),
        dict(id="agua_isna", nome="Água por fase (ISNA, FAO-56/FAO-33)", ativo=True, nivel_evidencia="N1", papel="insumo",
             motivo="Só calcula o excedente de chuva da primavera para o histórico. Sem sinal na cebola de Ituporanga (B1-0).",
             validacao=[dict(ref="B1-0", caminho="loop-validacao/fichas/B1-0-controle.md", resultado="sem sinal na cebola de Ituporanga")],
             nao_ve=["irrigação", "manejo"]),
        dict(id="preco_cebola", nome="Regra de venda pela chuva da primavera", ativo=False, nivel_evidencia="N1", papel="em_teste",
             motivo="Pré-registro falhou (B4-1: rho -0,11). O preço é fonte externa. Só auditoria, marcado 'mercado'.",
             validacao=[dict(ref="B4-1", caminho="loop-validacao/fichas/B4-1-quebra-cebola-sinal-preco.md", resultado="pré-registro falhou: rho -0,11; preço IBGE -4%"),
                        dict(ref="B4-3", caminho="loop-validacao/fichas/B4-3-guardar-cebola-fugir-pico.md", resultado="passou em parte: |rho| 0,397; alta >= 15% em 75% das safras, com preço da Epagri")],
             nao_ve=["custo de armazenar", "perda no galpão"]),
        dict(id="data_transplante_cebola", nome="Data de transplante da cebola", ativo=False, nivel_evidencia="N0", papel="em_teste",
             motivo="Fora (N0): o motor prefere setembro e o ZARC não dá 20% em nenhuma linha a partir de 11/set (V4, critério D2 falhou).",
             validacao=[dict(ref="V4", caminho="solucao/validacao/V4/relatorio.md", resultado="D2 falhou: contradiz o ZARC")],
             nao_ve=["tudo: módulo desligado"]),
    ]

    mes = ex["mes_nome"]
    anos_ex = hist["anos_extremos"]
    E1 = dict(id="E1", nome_curto="O de sempre", nome_falado="preparo convencional no inverno, transplante em julho e agosto e venda na colheita",
              e_atual=True, nivel_evidencia="N2", como_mostrar="com_faixa", ordem=1,
              sequencia=[dict(cultura="cebola", estacao="inverno", fracao_area=1.0, plantio=dict(de="01/07", ate="21/08"),
                              manejo="preparo convencional (aração, grade, enxada rotativa)"),
                         dict(cultura="pousio", estacao="verao", fracao_area=1.0, plantio=dict(de=None, ate=None), manejo=None)],
              modulos=["exposicao_solo", "ano_extremo_excesso", "agua_isna"],
              indicadores=[
                  dict(id="I-E1-DESCOBERTO", tipo="fracao_dias_descoberto",
                       rotulo=f"Fração dos dias de {mes} de {ex['ano']} com solo descoberto (NDVI < 0,30) no talhão (bloco de 50 m {ex['bloco'][0]}-{ex['bloco'][1]})",
                       valor=ex["fracao_descoberto"], unidade="fracao", ic95=None, faixa_parametros=None, n_anos=1,
                       periodo=f"{ex['ano']}-{ex['ano']}", nivel_evidencia="N2", modulo_id="exposicao_solo", rastro=["R-CALC-EXPOSICAO"]),
                  dict(id="I-E1-DESCOBERTO-RECORTE", tipo="fracao_dias_descoberto",
                       rotulo=f"Mesma fração, média dos {ex['n_blocos_lavoura']} blocos de lavoura do recorte de 5 x 5 km",
                       valor=ex["fracao_descoberto_recorte"], unidade="fracao", ic95=None, faixa_parametros=None, n_anos=1,
                       periodo=f"{ex['ano']}-{ex['ano']}", nivel_evidencia="N2", modulo_id="exposicao_solo", rastro=["R-CALC-EXPOSICAO"]),
                  dict(id="I-E1-PRIMAVERAS", tipo="anos_ruins_em_10",
                       rotulo=(f"Primaveras com excedente set-nov >= P90 ({hist['p90_mm']} mm) dos anos passados, em 10 anos. "
                               f"Hipótese de ano ruim, não quebra medida: {T.fmt_anos(anos_ex)}"),
                       valor=round(10 * len(anos_ex) / hist["n_anos"], 1), unidade="anos_em_10", ic95=None, faixa_parametros=None,
                       n_anos=hist["n_anos"], periodo=hist["periodo"], nivel_evidencia="N1", modulo_id="ano_extremo_excesso",
                       rastro=["R-CALC-EXCESSO-HIST"])],
              risco_por_decendio=None,
              premissas=["talhão = bloco de 50 x 50 m com >= 60% de pixels de lavoura anual (A3-1)", "descoberto = NDVI < 0,30, interpolado dia a dia"],
              quebra_se=["a palha seca tiver NDVI baixo e for contada como solo descoberto", "o mês tiver poucas cenas sem nuvem"],
              nao_calculado=["perda de solo", "rendimento da cebola"], solo_texto=None)
    E2 = dict(id="E2", nome_curto="Milho e cebola na palha", nome_falado="milho no verão e cebola em plantio direto sobre a palha",
              e_atual=False, nivel_evidencia="N1", como_mostrar="so_nome_em_teste", ordem=2,
              sequencia=[dict(cultura="milho_palha", estacao="verao", fracao_area=1.0, plantio=dict(de=None, ate=None), manejo="palha deixada no talhão"),
                         dict(cultura="cebola", estacao="inverno", fracao_area=1.0, plantio=dict(de="01/07", ate="21/08"), manejo="plantio direto sobre a palha")],
              modulos=["exposicao_solo"], indicadores=[], risco_por_decendio=None,
              premissas=[], quebra_se=[], nao_calculado=["solo salvo pela palha", "rendimento da cebola no plantio direto", "o motor não distingue o risco climático desta estratégia do atual"],
              solo_texto=dict(texto="A palha cobre o solo no inverno, justo quando o talhão hoje fica descoberto. Quanto solo isso salva e o efeito no rendimento não foram medidos.",
                              fonte="A3-1 (loop-validacao/fichas/A3-1-alerta-erosao.md); dissertação UDESC citada na A3-1 (só mecanismo)", a_validar=True))
    E3 = dict(id="E3", nome_curto="Guardar parte para março e abril", nome_falado="o de sempre, guardando parte da cebola para vender em março e abril",
              e_atual=False, nivel_evidencia="N1", como_mostrar="so_nome_em_teste", ordem=3,
              sequencia=[dict(cultura="cebola", estacao="inverno", fracao_area=1.0, plantio=dict(de="01/07", ate="21/08"), manejo="venda escalonada (mercado)")],
              modulos=["preco_cebola"], indicadores=[], risco_por_decendio=None, premissas=[], quebra_se=[],
              nao_calculado=["preço: só existe com fonte externa (Epagri), fora da regra de dados", "custo e perda no armazenamento"], solo_texto=None)
    estrategias = [E1, E2, E3]
    D.ordenar(estrategias, prioridade, {"E1": "atual", "E2": "solo", "E3": "outro"})

    viz_txt = "; ".join(f"{C.NOME_PONTO[n]}: {v['dias_diferentes']} de {v['de']} dias diferentes" for n, v in viz.items())
    rastro = [D.dado_power("R-POWER-ITU", pw, "Série diária do NASA POWER no ponto de Ituporanga, comunidade AG.",
                           "PRECTOTCORR, T2M, T2M_MAX, T2M_MIN, RH2M, WS2M, ALLSKY_SFC_SW_DWN")]
    for n in VIZINHOS:
        rastro.append(D.dado_power(f"R-POWER-{n.upper().replace('_', '-')}", Power(C.POWER[n]),
                                   f"Série diária do NASA POWER em {C.NOME_PONTO[n]}, só para conferir se a célula é a mesma.", "T2M_MIN"))
    rastro += [
        D.calculo("R-CALC-CELULA", f"Dias com T2M_MIN diferente entre Ituporanga e vizinhos. {viz_txt}.", me / "power.py", "mesma_celula",
                  dict(variavel="T2M_MIN", tolerancia_c=0.005), ["R-POWER-ITU"] + [f"R-POWER-{n.upper().replace('_', '-')}" for n in VIZINHOS],
                  arq_calc, "mesma_celula", periodo=pw.periodo),
        D.item("R-S2-BLOCOS", "dado", "Sentinel-2 L2A (B04, B08, SCL), 259 datas de 2019 a 2024, 10 m, recorte de 5 x 5 km; fração de dias com NDVI < 0,30 por bloco de 50 m e mês (A3-1).",
               "Sentinel-2", "resources", variavel="NDVI (B04, B08), máscara SCL", url="https://earth-search.aws.element84.com/v1",
               periodo="2019-2024", resolucao="10 m (bloco de 50 m)", arquivo=C.S2_BLOCOS),
        D.item("R-SRTM-ITU", "dado", "Declive do SRTM 1 arco-segundo (tile S28W050) por bloco de 50 m, usado no fator S da exposição da A3-1 (escolha do bloco mediano).",
               "SRTM", "resources", variavel="elevação 1 arco-segundo", resolucao="30 m", arquivo=C.S2_BLOCOS),
        D.item("R-PROD-SOLO", "pergunta", f"Resposta do produtor no WhatsApp (T15): talhão '{solo_declarado}'.", "produtor", "produtor", variavel="solo_declarado"),
        D.item("R-PROD-PRIORIDADE", "pergunta", f"Resposta do produtor (T12): prioridade '{prioridade}'. Só muda a ordem.", "produtor", "produtor", variavel="prioridade"),
        D.GAEZ(C.RAIZ / "prototipo" / "modelo" / "risco.py"),
        D.calculo("R-CALC-CAD", f"CAD = {SOLO_MM_M[solo_declarado]} mm/m (GAEZ) x {RAIZ_CEBOLA_M} m de raiz da cebola = {cad} mm.",
                  me / "locais" / "ituporanga.py", "avaliar", dict(mm_por_m=SOLO_MM_M[solo_declarado], raiz_m=RAIZ_CEBOLA_M),
                  ["R-PROD-SOLO", "R-GAEZ-CAD"], arq_calc, "cad"),
        D.FAO56(),
        D.calculo("R-CALC-FOURNIER", f"Índice de Fournier mensal do POWER (p_mês² / P_ano). Igual ao R salvo pela A3-1 (diferença máxima {ex['dif_max_R_vs_A3']:.1e}).",
                  me / "exposicao.py", "fournier", dict(formula="p_mes^2 / P_ano"), ["R-POWER-ITU"], arq_calc, "exposicao_solo.R_mes", periodo=pw.periodo),
        D.calculo("R-CALC-EXPOSICAO", (f"Bloco de lavoura com exposição anual mediana ({ex['bloco'][0]}-{ex['bloco'][1]}, declive {round(ex['declive_pct'], 1)}%). "
                                       f"Mês do inverno de {ex['ano']} com maior R x descoberto: {mes} (R {ex['R_mes']} contra mediana {ex['R_mediana_meses_passados']} dos meses passados)."),
                  me / "exposicao.py", "avaliar", dict(limiar_ndvi=0.30, meses_inverno=list(X.INVERNO), regra_bloco="exposição anual mediana",
                                                       regra_chuva_forte="R do mês > mediana de R de todos os meses dos anos anteriores"),
                  ["R-S2-BLOCOS", "R-SRTM-ITU", "R-CALC-FOURNIER"], arq_calc, "exposicao_solo", periodo=ex["periodo_satelite"]),
        D.calculo("R-CALC-EXCESSO-HIST", (f"Excedente hídrico de 1/set a 30/nov, cebola transplantada em 1/ago, raiz 0,3 m, solo médio (B3-2), {hist['periodo']}. "
                                          f"P90 dos anos passados = {hist['p90_mm']} mm."),
                  me / "ano_extremo.py", "historico_excesso", dict(percentil=90, transplante="01/08", janela="01/09-30/11", cad_mm=37.5, p_depl=0.3),
                  ["R-POWER-ITU", "R-FAO56"], arq_calc, "historico_excesso", periodo=hist["periodo"]),
        D.item("R-PAM-ITU", "conferencia", "IBGE PAM, rendimento da cebola na microrregião 42014 (Ituporanga), relativo à mediana móvel (t-3 a t+3).",
               "IBGE_PAM", "externo_conferencia", variavel="rendimento (kg/ha)", periodo="1990-2025", resolucao="microrregião", arquivo=C.PAM_V1),
    ]
    pam = K.pam_serie("Ituporanga 42014")
    com_pam = [a for a in anos_ex if a in pam]
    quebra = [a for a in com_pam if pam[a] <= 0.85]
    conferencias = [dict(id="K-PAM-EXCESSO", contra="IBGE_PAM", o_que="As primaveras de chuva extrema tiveram quebra da cebola?",
                         resultado="bate" if com_pam and len(quebra) == len(com_pam) else ("bate_em_parte" if quebra else "nao_bate"),
                         detalhe=(f"Das {len(com_pam)} primaveras extremas com PAM, {len(quebra)} tiveram rendimento <= 85% da mediana móvel "
                                  f"({T.fmt_anos(quebra) if quebra else 'nenhuma'}). Microrregião 42014."),
                         rastro=["R-PAM-ITU", "R-CALC-EXCESSO-HIST"])]

    doc = dict(versao_contrato=C.VERSAO_CONTRATO, gerado_em=D.agora(), modo=modo, data_referencia=data_referencia, safra=safra,
               motor=dict(versao=C.VERSAO_MOTOR, commit=None),
               local=dict(LOCAL, ponto_power=dict(lat=pw.lat_grade, lon=pw.lon, alt_grade_m=pw.alt_grade, resolucao_km=50, mesma_celula_que=mesma),
                          dentro_da_area_testada=C.regiao_do_ponto(LOCAL["lat"], LOCAL["lon"]) == "sc_alto_vale"),
               talhao=dict(id=D.slug_talhao(nome_talhao), nome=nome_talhao, area_ha=0.25, solo_declarado=solo_declarado,
                           cad_mm=dict(valor=cad, fonte="pergunta+gaez", nota="Raiz da cebola 0,3 m (B3-2). O CAD só entra no histórico de excedente.",
                                       rastro=["R-PROD-SOLO", "R-GAEZ-CAD", "R-CALC-CAD"]),
                           srtm=None, ciclo_gdd=dict(valor=1250, fonte="padrao"), colheita_verao=None, fotos_registro=[]),
               produtor=dict(id_pseudonimo=id_produtor, prioridade=prioridade, atividade="cebola"),
               regiao=dict(id="sc_alto_vale", nome=C.REGIOES["sc_alto_vale"]["nome"], papel="principal",
                           modulos_ativos=[m["id"] for m in modulos if m["ativo"]]),
               modulos=modulos, estrategias=estrategias, alertas=[], cartoes=[], rastro=rastro, conferencias=conferencias,
               limites=[], nao_sei=dict(ativo=False, motivos=[], encaminhar_para="tecnico_ater"))

    D.virgula_decimal(doc)
    P = D.Ptr(doc)
    KM = D.var(doc, "/local/ponto_power/resolucao_km", T.fmt_int)
    cart = []
    destino_t10 = "whatsapp" if ex["chuva_forte"] else "auditoria"
    cart.append(("T10_SOLO_EXPOSTO", destino_t10, dict(
        talhao=D.var(doc, "/talhao/nome", str),
        pct=D.var(doc, P.ind("E1", "I-E1-DESCOBERTO"), T.fmt_frac_pct),
        meses=(mes, P.ind("E1", "I-E1-DESCOBERTO", "rotulo")), km=KM), ["E1"]))
    # T01: os caminhos, na ordem da prioridade. Quem não tem número aparece só pelo nome, em teste.
    ordem_est = sorted(estrategias, key=lambda e: e["ordem"])[:4]
    v01 = dict(talhao=D.var(doc, "/talhao/nome", str))
    for i, e in enumerate(ordem_est, 1):
        v01[f"nome_{i}"] = D.var(doc, P.est(e["id"], "nome_curto"), str)
        if e["e_atual"]:
            v01[f"pct_{i}"] = D.var(doc, P.ind(e["id"], "I-E1-DESCOBERTO"), T.fmt_frac_pct)
            v01[f"meses_{i}"] = (mes, P.ind(e["id"], "I-E1-DESCOBERTO", "rotulo"))
    cart.append(("T01_COMPARA_ESTRATEGIAS", "whatsapp", v01, [e["id"] for e in ordem_est]))
    cart.append(("T09_CEBOLA_HISTORICO", "auditoria", dict(
        municipio=D.var(doc, "/local/municipio", str),
        n=D.var(doc, P.ind("E1", "I-E1-PRIMAVERAS", "n_anos"), T.fmt_int),
        anos=(T.fmt_anos(anos_ex), P.ind("E1", "I-E1-PRIMAVERAS", "rotulo"))), ["E1"]))
    if prioridade == "nao_informado":
        cart.append(("T12_PRIORIDADE", "whatsapp", {}, None))
    # cartões do WhatsApp primeiro, auditoria depois
    cart.sort(key=lambda c: c[1] != "whatsapp")
    for i, (tid, dest, vs, eids) in enumerate(cart, 1):
        doc["cartoes"].append(D.cartao(doc, f"C-{i:02d}", tid, dest, i, vs, eids))

    cids = [c["id"] for c in doc["cartoes"]]
    doc["limites"] = [
        dict(id="X-TRES-ROTACOES", texto="Ituporanga não fecha 3 rotações com número: só o de sempre tem número (o solo descoberto). As outras duas estão em teste.",
             gravidade="alta", afeta=["E1", "E2", "E3"], mostrar_ao_agricultor=False),
        dict(id="X-TALHAO-DEMO", texto=f"Talhão de demonstração: bloco de 50 m ({ex['bloco'][0]}, {ex['bloco'][1]}) do recorte da A3-1, o de exposição anual mediana entre {ex['n_blocos_lavoura']} blocos de lavoura. Não é o talhão de um produtor real.",
             gravidade="alta", afeta=["E1"] + cids, mostrar_ao_agricultor=False),
        dict(id="X-SOLO-PERDA", texto="Quanto solo a palha ou a cobertura salvam não foi calculado.", gravidade="alta", afeta=["E1", "E2"], mostrar_ao_agricultor=True,
             trecho="Quanto solo isso salva, ainda não medimos."),
        dict(id="X-NUVEM", texto="Em 15% dos meses de 2019 a 2024 o recorte não teve cena com 50% limpa (A3-1, critério C2). O NDVI desses meses foi interpolado.",
             gravidade="media", afeta=["E1"], mostrar_ao_agricultor=False),
        dict(id="X-GRADE", texto=f"Chuva vem de uma grade de ~50 km.{' ' + ', '.join(mesma) + ' cai na mesma célula.' if mesma else ''} O satélite tem 10 m.",
             gravidade="alta", afeta=["E1"], mostrar_ao_agricultor=True, trecho="A chuva é medida numa área de 50 km."),
        dict(id="X-EXCESSO-N1", texto="O histórico de primaveras chuvosas é N1: o alerta de excesso não passou fora do Alto Vale (V1). Fica na auditoria.",
             gravidade="media", afeta=["E1"], mostrar_ao_agricultor=False),
        dict(id="X-MERCADO", texto="Guardar para vender em março e abril depende de preço, que só existe em fonte externa (Epagri). Fica fora do WhatsApp.",
             gravidade="media", afeta=["E3"], mostrar_ao_agricultor=False),
        dict(id="X-REPLAY", texto=f"Modo replay da safra {safra}: o histórico usa só anos antes de {dref.year} e o satélite só o inverno de {ex['ano']}.",
             gravidade="baixa", afeta=["E1"], mostrar_ao_agricultor=False),
        dict(id="X-USUARIO", texto="Mensagens e cartões não foram testados com produtores nem técnicos.", gravidade="media", afeta=cids, mostrar_ao_agricultor=False),
    ]
    doc["limites"] = [{**l, "trecho": l.get("trecho")} for l in doc["limites"]]
    D.virgula_decimal(doc)
    return doc, calculos


def gerar():
    doc, calc = avaliar()
    D.gravar(doc, calc, SLUG)
    return doc
