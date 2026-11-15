"""Ponto fora da área testada (regra R12, teste de aceitação A6): devolve só 'não sei' (T14).

O schema pede 3 estratégias, módulos e rastro mesmo assim. Aqui todas ficam N0 / ocultas,
nenhum módulo liga e nenhum cartão tem número.
"""
import datetime as dt
from .. import config as C
from .. import documento as D


def avaliar(lat, lon, municipio, uf, codigo_ibge, data_referencia="2026-01-05", modo="operacao"):
    dref = dt.date.fromisoformat(data_referencia)
    rid = C.regiao_do_ponto(lat, lon)
    dentro = rid is not None
    if dentro:
        raise ValueError("ponto dentro da área testada: use o construtor do local")
    perto = C.regiao_mais_proxima(lat, lon)
    safra = f"{dref.year - 1}/{str(dref.year)[2:]}" if dref.month < 7 else f"{dref.year}/{str(dref.year + 1)[2:]}"
    slug = D.slug_talhao(municipio)[2:]
    mods = {"sc_extremo_oeste": ["geada_janela_safra", "geada_limite_2a_safra", "ano_extremo_seco", "mistura_talhao", "agua_isna"],
            "sc_alto_vale": ["exposicao_solo", "ano_extremo_excesso", "agua_isna"],
            "semiarido_ce_pe_pb": ["agua_isna"]}[perto]
    modulos = [dict(id=m, nome=m, ativo=False, nivel_evidencia="N0", papel="em_teste",
                    motivo="Desligado: o ponto fica fora da área em que o módulo foi testado.",
                    validacao=[dict(ref="spec-v2", caminho="solucao/spec-v2.md", resultado="módulo só vale na área testada da região")],
                    nao_ve=["tudo neste ponto"]) for m in mods]
    est = [dict(id=f"E{i}", nome_curto=n, nome_falado=n.lower(), e_atual=i == 1, nivel_evidencia="N0", como_mostrar="oculto", ordem=i,
                sequencia=[dict(cultura="pousio", estacao="verao", fracao_area=1.0, plantio=dict(de=None, ate=None), manejo="sem cálculo")],
                modulos=[], indicadores=[], risco_por_decendio=None, premissas=[], quebra_se=[], nao_calculado=["tudo: fora da área testada"],
                solo_texto=None)
           for i, n in enumerate(("O de sempre", "Outra rotação", "Outra cultura"), 1)]
    doc = dict(versao_contrato=C.VERSAO_CONTRATO, gerado_em=D.agora(), modo=modo, data_referencia=data_referencia, safra=safra,
               motor=dict(versao=C.VERSAO_MOTOR, commit=None),
               local=dict(id=f"L-{slug}", municipio=municipio, uf=uf, codigo_ibge=codigo_ibge, lat=lat, lon=lon,
                          ponto_power=dict(lat=lat, lon=lon, alt_grade_m=None, resolucao_km=50, mesma_celula_que=[]),
                          dentro_da_area_testada=False),
               talhao=dict(id="T-sem-nome", nome="Talhão", area_ha=None, solo_declarado="nao_sei",
                           cad_mm=dict(valor=125, fonte="padrao_regiao", nota="Não usado: fora da área testada.", rastro=["R-GAEZ-CAD"]),
                           srtm=None, ciclo_gdd=dict(valor=1250, fonte="padrao"), colheita_verao=None, fotos_registro=[]),
               produtor=dict(id_pseudonimo="P-00000000", prioridade="nao_informado", atividade="milho_feijao_sequeiro" if perto == "semiarido_ce_pe_pb" else "leite_milho"),
               regiao=dict(id=perto, nome=C.REGIOES[perto]["nome"] + " (mais próxima; o ponto está fora)", papel=C.REGIOES[perto]["papel"], modulos_ativos=[]),
               modulos=modulos, estrategias=est, alertas=[], cartoes=[],
               rastro=[D.item("R-PROD-LOCAL", "pergunta", f"Localização enviada pelo produtor: {lat}, {lon} ({municipio}-{uf}).", "produtor", "produtor", variavel="pin"),
                       D.GAEZ(C.RAIZ / "prototipo" / "modelo" / "risco.py")],
               conferencias=[],
               limites=[dict(id="X-FORA", texto=f"O seu lugar fica fora da área que testamos. A região mais perto é {C.REGIOES[perto]['nome']}, mas os números de lá não valem aqui.",
                             gravidade="alta", afeta=["E1", "E2", "E3"], mostrar_ao_agricultor=True, trecho="fica fora da área que testamos")],
               nao_sei=dict(ativo=True, motivos=["fora_da_area"], encaminhar_para="tecnico_ater"))
    D.virgula_decimal(doc)
    doc["cartoes"].append(D.cartao(doc, "C-01", "T14_NAO_SEI", "whatsapp", 1,
                                   dict(motivo=("o seu lugar fica fora da área que testamos", "/limites/0/texto"))))
    return doc, dict(local=doc["local"], regiao_mais_proxima=perto)
