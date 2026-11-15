"""Quixadá (CE): milho no Semiárido, segunda região (spec-v2 seção 4.3).

Módulo ativo: agua_isna (N2, núcleo, só milho). Caupi e sorgo entram como "em teste" (N1):
feijão fraco na V5 (rho 0,30 em Quixadá) e Ky genérico do sorgo.
"""
import datetime as dt
from .. import config as C
from .. import documento as D
from .. import textos as T
from .. import semiarido as SA
from .. import conferencia as K
from ..estat import spearman

SLUG = "quixada"
LOCAL = dict(id="L-quixada", municipio="Quixadá", uf="CE", codigo_ibge="2311306", lat=-4.97, lon=-39.02)
DATA_FIXA = (2, 11)  # 2º decêndio de fevereiro (spec-v2 4.3, Q2)

_cache = {}


def _calc(solo):
    if solo not in _cache:
        L = SA.Local(C.POWER["quixada"])
        _cache[solo] = dict(
            L=L,
            q1=L.estrategia("milho", solo, "chuva"),
            q2=L.estrategia("milho", solo, ("data",) + DATA_FIXA),
            q3=L.estrategia("caupi", solo, "chuva"),
            q4=L.estrategia("sorgo", solo, "chuva"),
            jan_milho=L.janelas("milho", solo),
            jan_caupi=L.janelas("caupi", solo))
    return _cache[solo]


def avaliar(data_referencia="2026-01-05", modo="operacao", solo_declarado="medio", prioridade="nao_informado",
            nome_talhao="Roça do baixio", id_produtor="P-b41e9a07"):
    dref = dt.date.fromisoformat(data_referencia)
    solo_sim = solo_declarado if solo_declarado in SA.SOLOS else "medio"
    r = _calc(solo_sim)
    L = r["L"]
    pw = L.pw
    cad = round(SA.SOLOS[solo_sim] * SA.CULTURAS["milho"]["raiz"], 1)
    safra = f"{dref.year - 1}/{str(dref.year)[2:]}" if dref.month < 7 else f"{dref.year}/{str(dref.year + 1)[2:]}"
    arq_calc = C.CALCULOS / f"{SLUG}.json"
    me = C.MOTOR
    zc = K.zarc_caupi_quixada()
    comp = []
    for j in r["jan_caupi"]:
        z = zc.get(j["dec"])
        falha_pct = round(100 - j["colhe_em_10"] * 10)
        comp.append(dict(decendio=j["decendio"], dec=j["dec"], falha_pct=falha_pct, zarc=z, consistente=(falha_pct > 40) if z is None else (falha_pct <= z)))
    n_cons = sum(c["consistente"] for c in comp)
    # ordem dentro da janela do ZARC (decêndios em que o ZARC indica o caupi) e linha de base ingênua:
    # os 8 decêndios mais chuvosos do POWER (média 2001-2025), falha de 30% dentro e alta fora
    dentro = [c for c in comp if c["zarc"] is not None]
    rho_janela = spearman([c["falha_pct"] for c in dentro], [c["zarc"] for c in dentro])
    chuva_dec = {}
    for k, v in L.CHUVA.items():
        dec = (int(k[4:6]) - 1) * 3 + min(int(k[6:]) - 1, 29) // 10 + 1
        chuva_dec[(int(k[:4]), dec)] = chuva_dec.get((int(k[:4]), dec), 0.0) + v
    media_dec = {}
    for (a, dec), v in chuva_dec.items():
        media_dec.setdefault(dec, []).append(v)
    media_dec = {dec: sum(v) / len(v) for dec, v in media_dec.items()}
    top8 = set(sorted(media_dec, key=lambda d: -media_dec[d])[:8])
    cons_ing = 0
    for j in r["jan_caupi"]:
        z, pred = zc.get(j["dec"]), (30 if j["dec"] in top8 else 100)
        cons_ing += (pred <= z) if z is not None else (pred > 40)
    rho_chuva_janela = spearman([-media_dec[c["dec"]] for c in dentro], [c["zarc"] for c in dentro])
    v5 = K.v5_quixada()
    calculos = dict(local=LOCAL, data_referencia=data_referencia, Q1=r["q1"], Q2=r["q2"], Q3=r["q3"], Q4=r["q4"],
                    janelas_milho=r["jan_milho"], janelas_caupi=r["jan_caupi"], et0_media_mm=L.et0_media(),
                    cad=dict(solo=solo_sim, mm_m=SA.SOLOS[solo_sim], raiz_m=1.0, cad_mm=cad))

    modulos = [dict(id="agua_isna", nome="Água por fase (ISNA, FAO-56/FAO-33), milho no Semiárido", ativo=True, nivel_evidencia="N2", papel="principal",
                    motivo="No CE/PE/PB a água é o fator dominante e não há geada. Passou os 4 critérios da V5, por pouco (0,414 contra 0,40). Não supera a soma de chuva (+0,06).",
                    validacao=[dict(ref="V5", caminho="solucao/validacao/V5/relatorio.md",
                                    resultado=(f"Quixadá, milho: rho {v5['rho_milho']} (chuva bruta {v5['rho_chuva']}), {v5['acerto8']} de 8 piores anos. Contra SMO: 0,28 (chuva 0,23). "
                                               "Critério pré-registrado, 16 pares: mediana 0,414. A mediana 0,615 do milho em 6 municípios é um recorte feito depois de ver a Bahia falhar")),
                               dict(ref="prototipo", caminho="prototipo/README.md",
                                    resultado=(f"caupi (N1, em teste) contra o ZARC: {n_cons} de {len(comp)} decêndios consistentes, mas a ordem dentro da janela não bate (Spearman {round(rho_janela, 2)}) "
                                               f"e um calendário ingênuo dá {cons_ing} de {len(comp)}. Não é evidência do milho"))],
                    nao_ve=["feijão com a mesma qualidade (rho 0,31)", "Bahia (rho 0,07)", "praga, manejo, irrigação"])]

    def ind_colhe(eid, q, nivel, rot):
        return dict(id=f"I-{eid}-COLHE", tipo="colhe_em_10", rotulo=rot, valor=q["colhe_em_10"], unidade="anos_em_10",
                    ic95=q["ic95_colhe"], faixa_parametros=None, n_anos=q["n"], periodo=q["periodo"], nivel_evidencia=nivel,
                    modulo_id="agua_isna", rastro=[f"R-CALC-{eid}"])

    def ind_falha(eid, q, nivel):
        return dict(id=f"I-{eid}-FALHA", tipo="falha_em_10", rotulo="Anos com rendimento simulado abaixo de 60% (inclui ano sem plantio = 0)",
                    valor=q["falha_em_10"], unidade="anos_em_10", ic95=q["ic95_falha"], faixa_parametros=None, n_anos=q["n"],
                    periodo=q["periodo"], nivel_evidencia=nivel, modulo_id="agua_isna", rastro=[f"R-CALC-{eid}"])

    df = f"{DATA_FIXA[1]:02d}/{DATA_FIXA[0]:02d}"
    chuva = dict(de=None, ate=None)
    jm = {j["decendio"]: j for j in r["jan_milho"]}
    E1 = dict(id="E1", nome_curto="O de sempre", nome_falado="milho plantado na primeira chuva firme",
              e_atual=True, nivel_evidencia="N2", como_mostrar="com_faixa", ordem=1,
              sequencia=[dict(cultura="milho_grao", estacao="chuvas", fracao_area=1.0, plantio=chuva, manejo="planta na 1ª chuva firme (20 mm em 3 dias, sem 8 dias secos depois)")],
              modulos=["agua_isna"],
              indicadores=[ind_colhe("E1", r["q1"], "N2", "Anos com boa colheita (rendimento simulado >= 60%), plantio na 1ª chuva firme"), ind_falha("E1", r["q1"], "N2")],
              risco_por_decendio=None, premissas=["solo médio, 125 mm/m, raiz 1 m", "milho de 100 dias (20/30/30/20)", "ano sem chuva firme até 30/abr = sem plantio (y = 0)"],
              quebra_se=["a regra de início de chuva não representar o plantio real (na Bahia ela falhou)"], nao_calculado=["praga e manejo"], solo_texto=None)
    E2 = dict(id="E2", nome_curto="Milho em meados de fevereiro", nome_falado=f"milho plantado em data fixa, no decêndio de {T.fmt_dia_mes(df)}",
              e_atual=False, nivel_evidencia="N2", como_mostrar="com_faixa", ordem=2,
              sequencia=[dict(cultura="milho_grao", estacao="chuvas", fracao_area=1.0, plantio=dict(de=df, ate=df), manejo=None)],
              modulos=["agua_isna"],
              indicadores=[ind_colhe("E2", r["q2"], "N2", f"Anos com boa colheita, plantio em {T.fmt_dia_mes(df)}"), ind_falha("E2", r["q2"], "N2")],
              risco_por_decendio=dict(cultura_alvo="milho_grao", evento="rendimento simulado < 60% do potencial (FAO-33), plantio no decêndio",
                                      modulo_id="agua_isna", rastro=["R-CALC-JANELAS-MILHO"],
                                      linhas=[dict(decendio=j["decendio"], em10=j["falha_em10"], ic95=j["ic95_falha"], k=j["k_falha"], n=j["n"],
                                                   componentes=dict(agua=j["falha_em10"], geada=None, ano_extremo=None), zarc=None)
                                              for j in r["jan_milho"]]),
              premissas=["mesmos parâmetros do E1", "plantio no dia, com ou sem chuva"],
              quebra_se=[f"a diferença para o E1 ({round(r['q2']['colhe_em_10'] - r['q1']['colhe_em_10'], 1)} em 10) cabe no IC de {r['q1']['n']} anos"],
              nao_calculado=["germinação em solo seco no dia do plantio"], solo_texto=None)
    E3 = dict(id="E3", nome_curto="Caupi na primeira chuva", nome_falado="feijão-caupi de ciclo curto na primeira chuva firme",
              e_atual=False, nivel_evidencia="N1", como_mostrar="so_nome_em_teste", ordem=3,
              sequencia=[dict(cultura="feijao_caupi", estacao="chuvas", fracao_area=1.0, plantio=chuva, manejo="70 dias")],
              modulos=["agua_isna"], indicadores=[dict(ind_colhe("E3", r["q3"], "N1", "Anos com boa colheita, caupi na 1ª chuva (em teste)"))],
              risco_por_decendio=dict(cultura_alvo="feijao_caupi (data fixa, para conferir com o ZARC)",
                                      evento="rendimento simulado < 60%, plantio no decêndio; o número principal do E3 usa a regra da chuva",
                                      modulo_id="agua_isna", rastro=["R-CALC-JANELAS-CAUPI"],
                                      linhas=[dict(decendio=j["decendio"], em10=j["falha_em10"], ic95=j["ic95_falha"], k=j["k_falha"], n=j["n"],
                                                   componentes=dict(agua=j["falha_em10"], geada=None, ano_extremo=None),
                                                   zarc=dict(risco_pct=zc.get(j["dec"]), indicado=zc.get(j["dec"]) is not None, rastro=["R-ZARC-QXD"]))
                                              for j in r["jan_caupi"]]),
              premissas=["Kc e Ky do feijão (FAO), não calibrados para o caupi"], quebra_se=["V5: feijão com rho 0,30 em Quixadá"],
              nao_calculado=["valor do caupi contra o milho"], solo_texto=None)
    E4 = dict(id="E4", nome_curto="Sorgo na primeira chuva", nome_falado="sorgo na primeira chuva firme",
              e_atual=False, nivel_evidencia="N1", como_mostrar="so_nome_em_teste", ordem=4,
              sequencia=[dict(cultura="sorgo_grao", estacao="chuvas", fracao_area=1.0, plantio=chuva, manejo=None)],
              modulos=["agua_isna"], indicadores=[ind_colhe("E4", r["q4"], "N1", "Anos com boa colheita, sorgo na 1ª chuva (Ky genérico, em teste)")],
              risco_por_decendio=None, premissas=["Ky genérico da FAO (baixo na floração)"],
              quebra_se=["o Ky real do sorgo for maior que o da FAO"], nao_calculado=["rendimento observado de sorgo"], solo_texto=None)
    estrategias = [E1, E2, E3, E4]
    D.ordenar(estrategias, prioridade, {"E1": "atual", "E2": "mais_area"})

    rastro = [D.dado_power("R-POWER-QXD", pw, "Série diária do NASA POWER em Quixadá, comunidade AG.",
                           "PRECTOTCORR, T2M, T2M_MAX, T2M_MIN, RH2M, WS2M, ALLSKY_SFC_SW_DWN"),
              D.item("R-PROD-SOLO", "pergunta", f"Resposta do produtor no WhatsApp (T15): solo '{solo_declarado}'.", "produtor", "produtor", variavel="solo_declarado"),
              D.GAEZ(C.RAIZ / "prototipo" / "modelo" / "risco.py"),
              D.calculo("R-CALC-CAD", f"CAD = {SA.SOLOS[solo_sim]} mm/m (GAEZ) x 1,0 m de raiz do milho = {cad} mm.", me / "semiarido.py", "Local.simular",
                        dict(mm_por_m=SA.SOLOS[solo_sim], raiz_m=1.0), ["R-PROD-SOLO", "R-GAEZ-CAD"], arq_calc, "cad"),
              D.FAO56(), D.FAO33()]
    par = dict(limiar_colhe=SA.LIMIAR_COLHE, p_depl=SA.P_DEPL, et0=dict(alt_m=SA.ALT_QUIXADA, lat=SA.LAT_QUIXADA, piso_mm=0.5),
               regra_chuva="20 mm em 3 dias e sem 8 dias secos (<= 2 mm) nos 30 seguintes, de 1/jan a 30/abr")
    for eid, q, cult, rot in (("E1", r["q1"], "milho", "milho na 1ª chuva"), ("E2", r["q2"], "milho", f"milho em {df}"),
                              ("E3", r["q3"], "caupi", "caupi na 1ª chuva"), ("E4", r["q4"], "sorgo", "sorgo na 1ª chuva")):
        rastro.append(D.calculo(f"R-CALC-{eid}", f"Rendimento relativo por ano ({rot}), {q['n']} anos, {q['sem_plantio']} sem plantio. Cópia de prototipo/modelo/risco.py (estrategia).",
                                me / "semiarido.py", "Local.estrategia", dict(par, cultura=cult, **{k: list(v) if isinstance(v, tuple) else v for k, v in SA.CULTURAS[cult].items()}),
                                ["R-POWER-QXD", "R-FAO56", "R-FAO33", "R-CALC-CAD"], arq_calc, eid.replace("E", "Q"), periodo=q["periodo"]))
    rastro += [
        D.calculo("R-CALC-JANELAS-MILHO", "Falha (y < 0,6) por decêndio de plantio fixo, milho, 2001-2025. Cópia de risco.py (janelas).",
                  me / "semiarido.py", "Local.janelas", dict(par, cultura="milho"), ["R-POWER-QXD", "R-FAO56", "R-FAO33", "R-CALC-CAD"], arq_calc, "janelas_milho", periodo=pw.periodo),
        D.calculo("R-CALC-JANELAS-CAUPI", "Falha (y < 0,6) por decêndio de plantio fixo, caupi, 2001-2025. Cópia de risco.py (janelas).",
                  me / "semiarido.py", "Local.janelas", dict(par, cultura="caupi"), ["R-POWER-QXD", "R-FAO56", "R-FAO33", "R-CALC-CAD"], arq_calc, "janelas_caupi", periodo=pw.periodo),
        D.item("R-ZARC-QXD", "conferencia", "ZARC 2026/27, caupi grupo I, sequeiro, solo tipo 2, Quixadá (lido do CSV do MAPA pela sessão do protótipo).",
               "ZARC", "externo_conferencia", variavel="risco por decêndio", url="https://dados.agricultura.gov.br", periodo="safra 2026/27",
               resolucao="município", arquivo=C.RAIZ / "prototipo" / "dados" / "resultado.json"),
        D.item("R-PAM-QXD", "conferencia", "IBGE PAM (SIDRA 5457), rendimento do milho em Quixadá, contra o modelo (V5).", "IBGE_PAM", "externo_conferencia",
               variavel="rendimento (kg/ha)", periodo="1985-2025", resolucao="município", arquivo=C.V5_RESULTADO),
        D.item("R-GARANTIA-SAFRA", "conferencia", "MDA/SPA, Garantia-Safra: parte dos municípios aderidos com perda comprovada, 2003-2018 (V5).", "Garantia-Safra",
               "externo_conferencia", periodo="2003-2018", resolucao="Semiárido (total)", arquivo=C.V5_EXTRA),
    ]
    gs = v5["garantia_safra"]
    discord = [c["decendio"] for c in comp if not c["consistente"]]
    conferencias = [
        dict(id="K-ZARC-CAUPI", contra="ZARC_2026_27", o_que="Caupi (em teste): falha calculada por decêndio contra o nível do ZARC",
             resultado="bate" if n_cons == len(comp) else ("bate_em_parte" if n_cons >= len(comp) / 2 else "nao_bate"),
             detalhe=(f"{n_cons} de {len(comp)} decêndios consistentes (falha <= nível do ZARC, ou > 40% fora). Linha de base ingênua (8 decêndios mais chuvosos do POWER): {cons_ing} de {len(comp)}. "
                      f"Dentro da janela do ZARC a ordem não bate: Spearman {round(rho_janela, 2)} (a chuva média do decêndio dá {round(rho_chuva_janela, 2)}). Discordam: {', '.join(discord) or 'nenhum'}."),
             rastro=["R-ZARC-QXD", "R-CALC-JANELAS-CAUPI"]),
        dict(id="K-PAM-QXD", contra="IBGE_PAM", o_que="O rendimento simulado do milho acompanha a PAM de Quixadá?", resultado="bate_em_parte",
             detalhe=f"Spearman {v5['rho_milho']} (n = {v5['n']}), {v5['acerto8']} de 8 piores anos. A chuva bruta da estação dá {v5['rho_chuva']}: o balanço não supera a chuva (V5).",
             rastro=["R-PAM-QXD"]),
        dict(id="K-GARANTIA-SAFRA", contra="Garantia-Safra", o_que="Anos de seca no Semiárido (6 municípios CE/PE/PB)", resultado="bate_em_parte",
             detalhe=f"Rendimento simulado contra a parte com perda: Spearman {gs['rho_modelo_vs_gs']} (n = {gs['n']}). A chuva bruta dá {gs['rho_chuva_vs_gs']}. Série nacional, não por município.",
             rastro=["R-GARANTIA-SAFRA"]),
    ]

    doc = dict(versao_contrato=C.VERSAO_CONTRATO, gerado_em=D.agora(), modo=modo, data_referencia=data_referencia, safra=safra,
               motor=dict(versao=C.VERSAO_MOTOR, commit=None),
               local=dict(LOCAL, ponto_power=dict(lat=pw.lat_grade, lon=pw.lon, alt_grade_m=pw.alt_grade, resolucao_km=50, mesma_celula_que=[]),
                          dentro_da_area_testada=C.regiao_do_ponto(LOCAL["lat"], LOCAL["lon"]) == "semiarido_ce_pe_pb"),
               talhao=dict(id=D.slug_talhao(nome_talhao), nome=nome_talhao, area_ha=None, solo_declarado=solo_declarado,
                           cad_mm=dict(valor=cad, fonte="pergunta+gaez" if solo_declarado in SA.SOLOS else "padrao_regiao", nota=None,
                                       rastro=["R-PROD-SOLO", "R-GAEZ-CAD", "R-CALC-CAD"]),
                           srtm=None, ciclo_gdd=dict(valor=1250, fonte="padrao"), colheita_verao=None, fotos_registro=[]),
               produtor=dict(id_pseudonimo=id_produtor, prioridade=prioridade, atividade="milho_feijao_sequeiro"),
               regiao=dict(id="semiarido_ce_pe_pb", nome=C.REGIOES["semiarido_ce_pe_pb"]["nome"], papel="segunda",
                           modulos_ativos=[m["id"] for m in modulos if m["ativo"]]),
               modulos=modulos, estrategias=estrategias, alertas=[], cartoes=[], rastro=rastro, conferencias=conferencias,
               limites=[], nao_sei=dict(ativo=False, motivos=[], encaminhar_para="tecnico_ater"))

    D.virgula_decimal(doc)
    P = D.Ptr(doc)
    KM = D.var(doc, "/local/ponto_power/resolucao_km", T.fmt_int)
    leg = "Saco rasgado = ano de quebra (colheita menor que 6 em cada 10 sacos)"
    cart = [("T11_SEMIARIDO_JANELA_MILHO", dict(
        municipio=D.var(doc, "/local/municipio", str),
        q_atual=D.var(doc, P.ind("E1", "I-E1-FALHA"), T.fmt_em10),
        **D.faixa(doc, P.ind("E1", "I-E1-FALHA", "ic95"), "lo_a", "hi_a"),
        janela=D.var(doc, P.est("E2", "sequencia", 0, "plantio", "de"), T.fmt_data_limite),
        q_janela=D.var(doc, P.ind("E2", "I-E2-FALHA"), T.fmt_em10),
        **D.faixa(doc, P.ind("E2", "I-E2-FALHA", "ic95"), "lo_j", "hi_j"),
        n=D.var(doc, P.ind("E1", "I-E1-FALHA", "n_anos"), T.fmt_int)), ["E1", "E2"],
        dict(tipo="10_sacos", linhas=[D.saco("Milho na 1ª chuva", r["q1"]["falha_em_10"], "N2", atual=True),
                                      D.saco(f"Milho em {D.dia_curto(df)}", r["q2"]["falha_em_10"], "N2")],
             legenda=leg))]
    ordem_est = sorted(estrategias, key=lambda e: e["ordem"])[:4]
    v01 = dict(talhao=D.var(doc, "/talhao/nome", str), km=KM)
    sacos = []
    for i, e in enumerate(ordem_est, 1):
        v01[f"nome_{i}"] = D.var(doc, P.est(e["id"], "nome_curto"), str)
        if e["nivel_evidencia"] in ("N2", "N3"):
            v01[f"q_{i}"] = D.var(doc, P.ind(e["id"], f"I-{e['id']}-FALHA"), T.fmt_em10)
            v01.update(D.faixa(doc, P.ind(e["id"], f"I-{e['id']}-FALHA", "ic95"), f"lo_{i}", f"hi_{i}"))
            if e["e_atual"]:
                v01[f"falado_{i}"] = D.var(doc, P.est(e["id"], "nome_falado"), str)
            q = r["q1"] if e["id"] == "E1" else r["q2"]
            sacos.append(D.saco(e["nome_curto"], q["falha_em_10"], "N2", atual=e["e_atual"]))
        else:
            sacos.append(D.saco(e["nome_curto"], None, "N1"))
    cart.append(("T01_COMPARA_ESTRATEGIAS", v01, [e["id"] for e in ordem_est], dict(tipo="10_sacos", linhas=sacos, legenda=leg)))
    # T12 (prioridade) fala de silagem e de solo: pergunta de SC. Não sai no Semiárido (limite X-T12-SC).
    for i, (tid, vs, eids, img) in enumerate(cart, 1):
        doc["cartoes"].append(D.cartao(doc, f"C-{i:02d}", tid, "whatsapp", i, vs, eids, None, img))

    cids = [c["id"] for c in doc["cartoes"]]
    dif = round(r['q1']['falha_em_10'] - r['q2']['falha_em_10'], 1)
    doc["limites"] = [
        dict(id="X-N-ANOS", texto=f"Só {r['q1']['n']} anos de dados ({r['q1']['periodo']}). A diferença entre E2 e E1 é {dif} em 10 e os IC95 se sobrepõem: dizer 'tende a ser melhor', nunca 'é melhor'.",
             gravidade="alta", afeta=["E1", "E2"], mostrar_ao_agricultor=True, trecho="tende a ser melhor, mas não é certo"),
        dict(id="X-CHUVA-BRUTA", texto="O balanço hídrico não supera a soma de chuva da estação (V5: +0,06; +0,016 com perda total). O ganho é traduzir o risco para o talhão, não prever melhor o ano.",
             gravidade="media", afeta=["E1", "E2"], mostrar_ao_agricultor=False),
        dict(id="X-ZARC-CAUPI", texto=f"O '{n_cons} de {len(comp)} decêndios do ZARC' é do caupi (em teste), não do milho. Dentro da janela a ordem não bate (Spearman {round(rho_janela, 2)}) e o calendário ingênuo dá {cons_ing} de {len(comp)}. Não use como prova do milho.",
             gravidade="alta", afeta=["E3"], mostrar_ao_agricultor=False),
        dict(id="X-RHO-RECORTE", texto="O rho 0,615 do milho é a mediana de 6 municípios do CE, PE e PB, recorte feito depois de ver a Bahia falhar. Comparável com SC: Quixadá 0,50 (chuva 0,46) contra SMO 0,28 (chuva 0,23). Critério pré-registrado: 0,414.",
             gravidade="media", afeta=["E1", "E2"], mostrar_ao_agricultor=False),
        dict(id="X-FEIJAO", texto="Caupi e sorgo ficam em teste: feijão com rho 0,30 em Quixadá (V5) e Ky do sorgo genérico.",
             gravidade="media", afeta=["E3", "E4"], mostrar_ao_agricultor=False),
        dict(id="X-BAHIA", texto="Não vale para a Bahia (Irecê, Senhor do Bonfim): rho 0,07, a regra de início de chuva não planta em 16 e 24 de 41 anos (V5).",
             gravidade="alta", afeta=["E1"], mostrar_ao_agricultor=False),
        dict(id="X-ALTITUDE", texto=f"A ET0 usa a altitude da sede (190 m, como risco.py), não a da grade do POWER ({pw.alt_grade} m).",
             gravidade="baixa", afeta=["E1", "E2", "E3", "E4"], mostrar_ao_agricultor=False),
        dict(id="X-CICLO-GDD", texto="O campo ciclo_gdd não é usado no Semiárido: o ciclo do milho é fixo em 100 dias.",
             gravidade="baixa", afeta=["E1", "E2"], mostrar_ao_agricultor=False),
        dict(id="X-GRADE", texto="Chuva e temperatura vêm de uma grade de ~50 km.", gravidade="alta", afeta=["E1", "E2"], mostrar_ao_agricultor=True,
             trecho=T.DADOS_SATELITE.format(km=50)),
        dict(id="X-T12-SC", texto="O T12 (prioridade) tem opções de SC. Não sai no Semiárido até existirem opções próprias; a prioridade fica 'não informada'.",
             gravidade="baixa", afeta=["E1", "E2"], mostrar_ao_agricultor=False),
        dict(id="X-USUARIO", texto="Mensagens e cartões não foram testados com produtores nem técnicos.", gravidade="media", afeta=cids, mostrar_ao_agricultor=False),
    ]
    doc["limites"] = [{**l, "trecho": l.get("trecho")} for l in doc["limites"]]
    D.virgula_decimal(doc)
    return doc, calculos


def gerar():
    doc, calc = avaliar()
    D.gravar(doc, calc, SLUG)
    return doc
