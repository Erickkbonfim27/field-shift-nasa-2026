"""Contrato v2.0.0: validador de JSON Schema, regras R1-R12 e testes de aceitação A1, A5, A6."""
import copy
import re
import unittest
from pathlib import Path

import _base  # noqa: F401
from motor import config as C
from motor import validador as V
from motor import textos as T
from motor.locais import sao_miguel_do_oeste as SMO, ituporanga as ITU, quixada as QXD, fora_da_area as FORA

SCHEMA = V.carregar_schema()


def erros(doc, **kw):
    return V.validar(doc, schema=SCHEMA, **kw)


def refazer_cartao(doc, c):
    """Remonta o texto de um cartão a partir das variáveis (como o motor faz) e atualiza a contagem de palavras."""
    c["texto"] = T.render(c["template_id"], {k: v["texto"] for k, v in c["variaveis"].items()},
                          {k: V.ponteiro(doc, v["ponteiro"]) for k, v in c["variaveis"].items()})
    c["palavras"] = T.palavras(c["texto"])


class TestValidadorSchema(unittest.TestCase):
    def s(self, schema, x):
        return V.Schema(dict(schema, **{"$defs": {"n": {"type": "integer", "minimum": 1}}})).erros(x)

    def test_tipos_e_bool(self):
        self.assertTrue(self.s({"type": "integer"}, True))  # bool não é inteiro
        self.assertFalse(self.s({"type": "number"}, 3))
        self.assertFalse(self.s({"type": ["string", "null"]}, None))
        self.assertTrue(self.s({"type": "string"}, 3))

    def test_enum_const_pattern_tamanho(self):
        self.assertTrue(self.s({"enum": [20, 30, None]}, 25))
        self.assertFalse(self.s({"enum": [20, 30, None]}, None))
        self.assertTrue(self.s({"const": True}, 1))
        self.assertTrue(self.s({"type": "string", "pattern": "^(01|11|21)/(0[1-9]|1[0-2])$"}, "05/02"))
        self.assertTrue(self.s({"type": "string", "maxLength": 3}, "abcd"))
        self.assertTrue(self.s({"type": "array", "minItems": 2, "items": {"type": "number"}}, [1]))

    def test_objeto_ref_oneof_if_then(self):
        sch = {"type": "object", "additionalProperties": False, "required": ["a"],
               "properties": {"a": {"$ref": "#/$defs/n"}, "b": {"oneOf": [{"type": "null"}, {"type": "string"}]}},
               "allOf": [{"if": {"properties": {"a": {"const": 1}}}, "then": {"required": ["b"]}}]}
        self.assertFalse(self.s(sch, {"a": 2}))
        self.assertTrue(self.s(sch, {"a": 1}))           # if/then exige b
        self.assertTrue(self.s(sch, {"a": 0}))           # $ref -> minimum 1
        self.assertTrue(self.s(sch, {"a": 2, "c": 1}))   # additionalProperties false
        self.assertTrue(self.s(sch, {"a": 2, "b": 5}))   # oneOf não casa

    def test_exemplo_da_spec_passa(self):
        ex = C.ler_json(C.EXEMPLO)
        self.assertEqual(erros(ex, r8_estrito=False), [])
        self.assertEqual(ex["versao_contrato"], C.VERSAO_CONTRATO)


class TestSaidas(unittest.TestCase):
    """A1: toda saída real passa no schema e em R1-R12."""

    @classmethod
    def setUpClass(cls):
        cls.docs = {m.SLUG: m.avaliar()[0] for m in (SMO, ITU, QXD)}

    def test_saidas_validas(self):
        for slug, doc in self.docs.items():
            self.assertEqual(erros(doc), [], slug)

    def test_arquivos_gerados_validos(self):
        # os arquivos de solucao/saida/ (se já gerados) passam também na checagem de arquivos do rastro
        for slug in self.docs:
            p = C.SAIDA / f"{slug}.json"
            if p.exists():
                self.assertEqual(erros(C.ler_json(p), checar_arquivos=True), [], slug)

    def test_chaves_do_rastro_existem_nos_calculos(self):
        for m in (SMO, ITU, QXD):
            doc, calc = m.avaliar()
            for it in doc["rastro"]:
                if it["tipo"] == "calculo" and it["resultado"]["arquivo"].startswith("solucao/saida/calculos"):
                    chave = re.split(r"[ .\[]", it["resultado"]["chave"])[0]
                    self.assertIn(chave, calc, (m.SLUG, it["id"]))

    def test_a2_numeros_da_spec(self):
        d = self.docs["sao-miguel-do-oeste"]
        e = {x["id"]: x for x in d["estrategias"]}
        ind = {i["id"]: i for x in d["estrategias"] for i in x["indicadores"]}
        self.assertEqual(ind["I-E2-LIMITE"]["valor"], "05/02")
        self.assertEqual((ind["I-E2-GEADA-0102"]["valor"], ind["I-E2-GEADA-1102"]["valor"]), (1.1, 4.4))
        self.assertEqual(ind["I-E2-GEADA-0102"]["ic95"], [0.5, 2.3])
        self.assertEqual(ind["I-E1-GEADA-AGO"]["valor"], 6.3)
        self.assertEqual(d["alertas"][0]["indice"]["valor"], 0.618)
        self.assertEqual(sum(x["e_atual"] for x in e.values()), 1)
        q = {i["id"]: i["valor"] for x in self.docs["quixada"]["estrategias"] for i in x["indicadores"]}
        self.assertEqual((q["I-E1-COLHE"], q["I-E2-COLHE"], q["I-E3-COLHE"], q["I-E4-COLHE"]), (6.4, 8.0, 7.6, 8.8))
        k = [c for c in self.docs["quixada"]["conferencias"] if c["id"] == "K-ZARC-CAUPI"][0]
        self.assertTrue(k["detalhe"].startswith("16 de 18"))  # A4: 16 de 18 decêndios do ZARC do caupi

    def test_r9_prioridade_so_muda_ordem(self):
        a = SMO.avaliar(prioridade="silagem_garantida")[0]
        b = SMO.avaliar(prioridade="renda")[0]
        self.assertNotEqual([e["ordem"] for e in a["estrategias"]], [e["ordem"] for e in b["estrategias"]])

        def numeros(doc):
            d = copy.deepcopy(doc)
            for k in ("cartoes", "gerado_em", "produtor", "rastro"):
                d.pop(k)
            for e in d["estrategias"]:
                e.pop("ordem")
            return d
        self.assertEqual(numeros(a), numeros(b))
        self.assertEqual(erros(b), [])

    def test_variantes_validas(self):
        # julho: planejamento do verão (T02/T03), alerta fora da janela; solo médio: mistura desligada
        jul = SMO.avaliar(data_referencia="2021-07-20", colheita_verao=None)[0]
        self.assertEqual(erros(jul), [])
        self.assertIn("T02_GEADA_JANELA_SAFRA", [c["template_id"] for c in jul["cartoes"]])
        self.assertEqual(jul["alertas"][0]["estado"], "fora_da_janela")
        dez = SMO.avaliar(data_referencia="2021-12-01")[0]
        self.assertEqual(erros(dez), [])
        self.assertIn("T06_ANO_SECO_SILENCIO", [c["template_id"] for c in dez["cartoes"]])
        medio = SMO.avaliar(solo_declarado="medio", prioridade="nao_informado")[0]
        self.assertEqual(erros(medio), [])
        self.assertNotIn("E4", [e["id"] for e in medio["estrategias"] if e["nome_curto"] == "Metade em sorgo"])
        self.assertIn("T15_PEDE_SOLO", [c["template_id"] for c in SMO.avaliar(solo_declarado="nao_sei")[0]["cartoes"]])
        self.assertIn("T12_PRIORIDADE", [c["template_id"] for c in medio["cartoes"]])
        self.assertEqual(len(medio["estrategias"]), 3)


class TestNegativos(unittest.TestCase):
    """A5: o validador pega fonte externa como dado, N1 com número no WhatsApp, número solto etc."""

    @classmethod
    def setUpClass(cls):
        cls.base = SMO.avaliar()[0]

    def doc(self):
        return copy.deepcopy(self.base)

    def tem(self, doc, prefixo):
        es = erros(doc)
        self.assertTrue(any(e.startswith(prefixo) for e in es), (prefixo, es[:5]))

    def test_zarc_como_dado(self):
        d = self.doc()
        next(r for r in d["rastro"] if r["id"] == "R-ZARC")["tipo"] = "dado"
        self.tem(d, "schema:")
        self.tem(d, "R2:")

    def test_pam_como_entrada_de_calculo(self):
        d = self.doc()
        next(r for r in d["rastro"] if r["id"] == "R-CALC-ISNA-SECO")["entradas"].append("R-PAM-SC")
        self.tem(d, "R2:")

    def test_duas_atuais(self):
        d = self.doc()
        d["estrategias"][1]["e_atual"] = True
        self.tem(d, "R3:")

    def test_n1_com_numero_no_whatsapp(self):
        d = self.doc()
        c = next(c for c in d["cartoes"] if c["template_id"] == "T01_COMPARA_ESTRATEGIAS")
        i = next(i for i in range(1, 5) if d["estrategias"][int(c["variaveis"][f"nome_{i}"]["ponteiro"].split("/")[2])]["nivel_evidencia"] == "N1")
        e = d["estrategias"][int(c["variaveis"][f"nome_{i}"]["ponteiro"].split("/")[2])]
        e["nome_curto"] = "Sorgo em 3 de 10"
        c["variaveis"][f"nome_{i}"]["texto"] = "Sorgo em 3 de 10"
        refazer_cartao(d, c)
        self.tem(d, "R4:")

    def test_n1_como_com_faixa(self):
        d = self.doc()
        next(e for e in d["estrategias"] if e["nivel_evidencia"] == "N1")["como_mostrar"] = "com_faixa"
        self.tem(d, "R4:")

    def test_numero_solto_no_texto(self):
        d = self.doc()
        c = d["cartoes"][0]
        c["texto"] = c["texto"].replace("Sim, este ano está seco.", "Em 7 anos foi pior.")
        c["palavras"] = T.palavras(c["texto"])
        self.tem(d, "R8:")

    def test_variavel_que_nao_bate_com_o_valor(self):
        d = self.doc()
        c = d["cartoes"][0]
        c["variaveis"]["n_anos"]["texto"] = "6"
        c["texto"] = T.render(c["template_id"], {k: v["texto"] for k, v in c["variaveis"].items()}, {})
        c["palavras"] = T.palavras(c["texto"])
        self.tem(d, "R8:")

    def test_ponteiro_quebrado(self):
        d = self.doc()
        d["cartoes"][0]["variaveis"]["n_anos"]["ponteiro"] = "/alertas/9/x"
        self.tem(d, "R1:")

    def test_rastro_inexistente(self):
        d = self.doc()
        d["estrategias"][0]["indicadores"][0]["rastro"] = ["R-NAO-EXISTE"]
        self.tem(d, "R1:")

    def test_intervalo_invertido(self):
        d = self.doc()
        i = next(i for e in d["estrategias"] for i in e["indicadores"] if i["ic95"])
        i["ic95"] = [i["ic95"][1] + 1, i["ic95"][0]]
        self.tem(d, "R5:")

    def test_percentil_com_ano_futuro(self):
        d = self.doc()
        d["alertas"][0]["percentil_local"]["periodo_passado"] = "1990-2025"
        self.tem(d, "R6:")

    def test_sacos_que_nao_somam_10(self):
        d = self.doc()
        l = next(l for c in d["cartoes"] for l in c["imagem"].get("linhas", []) if l["cheios"] is not None)
        l["cheios"] += 1
        self.tem(d, "R7:")

    def test_modulos_ativos_errados(self):
        d = self.doc()
        d["regiao"]["modulos_ativos"].append("enso_tipo_risco")
        self.tem(d, "R10:")

    def test_contagem_de_palavras(self):
        d = self.doc()
        d["cartoes"][0]["palavras"] += 1
        self.tem(d, "R11:")


class TestRevisao(unittest.TestCase):
    """Achados da revisão de 14/11/2026: cada regra nova pega o erro que antes passava."""

    @classmethod
    def setUpClass(cls):
        cls.docs = {m.SLUG: m.avaliar()[0] for m in (SMO, ITU, QXD)}

    def tem(self, doc, prefixo):
        es = erros(doc)
        self.assertTrue(any(e.startswith(prefixo) for e in es), (prefixo, es[:5]))

    def wa(self, doc, tid):
        return next(c for c in doc["cartoes"] if c["template_id"] == tid)

    def test_r2_segue_o_ponteiro_do_cartao_ate_a_pam(self):
        # antes: o T05 levava 'em anos assim, 4 em 10 regiões' (IBGE PAM) ao WhatsApp e o validador deixava passar
        d = copy.deepcopy(self.docs["sao-miguel-do-oeste"])
        c = self.wa(d, "T05_ANO_SECO_ATIVO")
        c["variaveis"]["n_anos"]["ponteiro"] = "/alertas/0/frase_probabilidade/anos_assim_ruins_em_10"
        self.tem(d, "R2:")

    def test_nenhum_cartao_do_whatsapp_chega_a_fonte_externa(self):
        for slug, d in self.docs.items():
            for c in d["cartoes"]:
                if c["destino"] != "whatsapp":
                    continue
                for nome, v in c["variaveis"].items():
                    for i in V._rastro_do_ponteiro(d, v["ponteiro"]):
                        it = next(r for r in d["rastro"] if r["id"] == i)
                        self.assertNotEqual(it["fonte"]["categoria"], "externo_conferencia", (slug, c["id"], nome, i))

    def test_r2_calculo_de_validacao_sem_marca_falha(self):
        d = copy.deepcopy(self.docs["sao-miguel-do-oeste"])
        next(r for r in d["rastro"] if r["id"] == "R-CALC-ALERTA-VALID")["parametros"]["so_auditoria"] = False
        self.tem(d, "R2:")

    def test_texto_do_t05_nao_traz_numero_da_pam(self):
        c = self.wa(self.docs["sao-miguel-do-oeste"], "T05_ANO_SECO_ATIVO")
        self.assertNotIn("regiões", c["texto"])
        self.assertNotIn("Num ano qualquer", c["texto"])
        self.assertEqual(sorted(c["variaveis"]), ["fim", "inicio", "km", "n_anos"])

    def test_r4_numero_n2_sem_faixa(self):
        d = copy.deepcopy(self.docs["sao-miguel-do-oeste"])
        c = self.wa(d, "T04_GEADA_LIMITE_2A_SAFRA")
        for k in ("lo", "hi"):
            del c["variaveis"][k]
        refazer_cartao(d, c)
        self.tem(d, "R4:")

    def test_todo_numero_n2_com_intervalo_traz_faixa(self):
        for slug, d in self.docs.items():
            self.assertFalse([e for e in erros(d) if "não traz a faixa" in e], slug)

    def test_r7_polaridade_dos_sacos(self):
        # antes: o texto de Quixadá dizia 'boa colheita em 6 de 10' e o cartão mostrava 4 sacos rasgados
        d = copy.deepcopy(self.docs["quixada"])
        c = self.wa(d, "T11_SEMIARIDO_JANELA_MILHO")
        self.assertNotIn("boa colheita", c["texto"])
        l = c["imagem"]["linhas"][0]
        self.assertEqual(l["rasgados"], 4)  # o texto diz 'quebra em cerca de 4 de cada 10 anos'
        l["cheios"], l["rasgados"] = 3, 7   # polaridade trocada ou número que o texto não diz
        self.tem(d, "R7:")

    def test_r13_ponto_decimal_em_limite(self):
        for slug, d in self.docs.items():
            self.assertFalse([e for e in erros(d) if e.startswith("R13")], slug)
            for l in d["limites"]:
                self.assertNotRegex(l["texto"], r"\d\.\d", (slug, l["id"]))
        d = copy.deepcopy(self.docs["quixada"])
        d["limites"][0]["texto"] += " Diferença de 1.6 em 10."
        self.tem(d, "R13:")

    def test_r14_limite_que_vai_ao_produtor_tem_trecho(self):
        for slug, d in self.docs.items():
            for l in d["limites"]:
                if l["mostrar_ao_agricultor"]:
                    self.assertTrue(any(l["trecho"] in c["texto"] for c in d["cartoes"] if c["destino"] == "whatsapp"), (slug, l["id"]))
        d = copy.deepcopy(self.docs["sao-miguel-do-oeste"])
        next(l for l in d["limites"] if l["id"] == "X-GRADE")["trecho"] = "frase que não está em cartão nenhum"
        self.tem(d, "R14:")
        d = copy.deepcopy(self.docs["sao-miguel-do-oeste"])
        next(l for l in d["limites"] if l["id"] == "X-GRADE")["trecho"] = None
        self.tem(d, "R14:")

    def test_r15_fim_da_janela_do_alerta(self):
        d = copy.deepcopy(self.docs["sao-miguel-do-oeste"])
        d["alertas"][0]["janela"]["ate"] = "2022-01-05"
        self.tem(d, "R15:")

    def test_t05_antes_de_10_jan_diz_o_fim_certo(self):
        # antes: o alerta de 15/12/2021 dizia 'de 20 de setembro a 10 de janeiro' (26 dias que não aconteceram)
        d = SMO.avaliar(data_referencia="2021-12-15")[0]
        self.assertEqual(erros(d), [])
        a = d["alertas"][0]
        self.assertEqual(a["janela"]["ate"], "2021-12-15")
        self.assertIn("15/12", a["indice"]["nome"])
        for c in d["cartoes"]:
            if c["template_id"] == "T05_ANO_SECO_ATIVO":
                self.assertIn("a 15 de dezembro", c["texto"])
                self.assertNotIn("10 de janeiro", c["texto"])

    def test_geada_janela_safra_e_n2(self):
        d = self.docs["sao-miguel-do-oeste"]
        m = next(m for m in d["modulos"] if m["id"] == "geada_janela_safra")
        self.assertEqual(m["nivel_evidencia"], "N2")
        self.assertFalse([i for e in d["estrategias"] for i in e["indicadores"] if i["nivel_evidencia"] == "N3"])

    def test_limite_do_2o_milho_tem_data_e_nao_terco_do_mes(self):
        d = self.docs["sao-miguel-do-oeste"]
        for tid in ("T01_COMPARA_ESTRATEGIAS", "T04_GEADA_LIMITE_2A_SAFRA"):
            t = self.wa(d, tid)["texto"]
            self.assertIn("5 de fevereiro", t)
            self.assertNotIn("começo de fevereiro", t)
            self.assertIn("Não calculamos a falta de água" if tid.startswith("T04") else "não calculamos a falta de água", t)

    def test_parametros_de_literatura_externa_no_rastro(self):
        d = self.docs["sao-miguel-do-oeste"]
        ext = {r["id"]: r for r in d["rastro"] if r["fonte"]["categoria"] == "literatura_externa"}
        self.assertEqual(sorted(ext), ["R-PARAM-LIMIAR-GEADA", "R-PARAM-R-SORGO", "R-PARAM-RAIZ-RASO"])
        self.assertTrue(all(r["tipo"] == "parametro" for r in ext.values()))
        calc = {r["id"]: r for r in d["rastro"]}
        self.assertIn("R-PARAM-R-SORGO", calc["R-CALC-MISTURA"]["entradas"])
        self.assertIn("R-PARAM-RAIZ-RASO", calc["R-CALC-CAD"]["entradas"])
        self.assertIn("R-PARAM-LIMIAR-GEADA", calc["R-CALC-GEADA-SAFRA"]["entradas"])
        # literatura externa como 'dado' é recusada
        d2 = copy.deepcopy(d)
        next(r for r in d2["rastro"] if r["id"] == "R-PARAM-R-SORGO")["tipo"] = "dado"
        self.assertTrue([e for e in erros(d2) if e.startswith("R2:") or e.startswith("schema:")])

    def test_t07_sem_porcentagem_para_o_produtor(self):
        t = self.wa(self.docs["sao-miguel-do-oeste"], "T07_MISTURA_TALHAO_RASO")["texto"]
        self.assertNotIn("%", t)
        self.assertNotIn("deve melhorar", t)

    def test_quixada_sem_t12_e_sem_t08_solto(self):
        for slug, d in self.docs.items():
            self.assertNotIn("T08_EM_TESTE", [c["template_id"] for c in d["cartoes"]], slug)
        self.assertNotIn("T12_PRIORIDADE", [c["template_id"] for c in self.docs["quixada"]["cartoes"]])

    def test_validacao_do_alerta_usa_so_o_passado(self):
        d = self.docs["sao-miguel-do-oeste"]
        r = next(r for r in d["rastro"] if r["id"] == "R-CALC-ALERTA-VALID")
        self.assertEqual(r["script"]["caminho"], "solucao/validacao/V1/v1_passo6_so_passado.py")
        self.assertTrue(r["parametros"]["so_auditoria"])
        self.assertTrue(any("C1 e C3 falham" in v["resultado"] for m in d["modulos"] if m["id"] == "ano_extremo_seco" for v in m["validacao"]))

    def test_toda_pergunta_da_ui_tem_cartao(self):
        """Lê as perguntas de ui/comum.js e confere que cada uma acha um cartão do WhatsApp na saída do local."""
        js = (Path(__file__).resolve().parents[2] / "ui" / "comum.js").read_text()
        blocos = re.findall(r'slug: "([^"]+)".*?perguntas: \[(.*?)\n    \]', js, re.S)
        self.assertEqual(sorted(b[0] for b in blocos), sorted(self.docs))
        for slug, perg in blocos:
            tem = {c["template_id"] for c in self.docs[slug]["cartoes"] if c["destino"] == "whatsapp"}
            for pid, templates in re.findall(r'id: "([^"]+)".*?templates: \[(.*?)\]', perg):
                lista = re.findall(r'"([^"]+)"', templates)
                self.assertTrue(set(lista) & tem, (slug, pid, lista, sorted(tem)))


class TestForaDaArea(unittest.TestCase):
    """A6: ponto fora de SC e do CE/PE/PB, ou na Bahia, devolve T14 sem número."""

    def test_bahia_e_rs(self):
        for lat, lon, mun, uf, cod in ((-11.30, -41.86, "Irecê", "BA", "2914604"), (-28.26, -52.41, "Passo Fundo", "RS", "4314100")):
            doc, _ = FORA.avaliar(lat, lon, mun, uf, cod)
            self.assertEqual(erros(doc), [], mun)
            self.assertTrue(doc["nao_sei"]["ativo"])
            self.assertEqual([c["template_id"] for c in doc["cartoes"]], ["T14_NAO_SEI"])
            self.assertFalse(any(re.search(r"\d", c["texto"]) for c in doc["cartoes"]))
            self.assertEqual(doc["regiao"]["modulos_ativos"], [])

    def test_r12_pega_numero_fora_da_area(self):
        doc, _ = FORA.avaliar(-11.30, -41.86, "Irecê", "BA", "2914604")
        doc["nao_sei"]["ativo"] = False
        self.assertTrue(any(e.startswith("R12:") for e in erros(doc)))

    def test_ponto_testado_nao_e_fora(self):
        self.assertEqual(C.regiao_do_ponto(-26.725, -53.518), "sc_extremo_oeste")
        self.assertEqual(C.regiao_do_ponto(-27.414, -49.601), "sc_alto_vale")
        self.assertEqual(C.regiao_do_ponto(-4.97, -39.02), "semiarido_ce_pe_pb")
        self.assertIsNone(C.regiao_do_ponto(-11.30, -41.86))


class TestTextos(unittest.TestCase):
    def test_r7_arredondamento(self):
        self.assertEqual(T.fmt_em10(4.5), "5")   # meio para cima
        self.assertEqual(T.fmt_em10(4.4), "4")
        self.assertEqual(T.fmt_em10(0.2), "menos de 1")
        self.assertEqual(T.fmt_em10(0.0), "quase nunca")
        self.assertEqual(T.fmt_pct(-9.3), "9")
        self.assertEqual(T.fmt_data_limite("05/02"), "começo de fevereiro")
        self.assertEqual(T.fmt_data_limite("15/02"), "meados de fevereiro")
        self.assertEqual(T.fmt_data_limite("25/01"), "fim de janeiro")

    def test_extenso_e_roteiro(self):
        self.assertEqual(T.extenso(32), "trinta e dois")
        self.assertEqual(T.extenso(2023), "dois mil e vinte e três")
        self.assertEqual(T.extenso(1997), "mil novecentos e noventa e sete")
        self.assertEqual(T.roteiro("cerca de 2 em cada 10 regiões de SC"), "cerca de duas em cada dez regiões de Santa Catarina")
        self.assertNotRegex(T.roteiro("1) Teste: 14% em 1º de fevereiro."), r"\d")
        self.assertEqual(T.roteiro("em cerca de 2 de cada 10 anos (entre 1 e 3). Área de 50 km."),
                         "em cerca de dois de cada dez anos (entre um e três). Área de cinquenta quilômetros.")
        self.assertNotRegex(T.roteiro("(entre 5 e 8)."), r"\d")


if __name__ == "__main__":
    unittest.main()
