"""Alerta de ano extremo: percentil só com anos passados (R6), estados e histórico de excesso."""
import datetime as dt
import unittest

import _base  # noqa: F401
from motor import config as C
from motor import ano_extremo as A
from motor import power
from motor import exposicao as X


class TestPercentil(unittest.TestCase):
    def test_percentil_passado(self):
        passados = [0.7, 0.8, 0.9, 1.0]
        self.assertEqual(A.percentil_passado(0.6, passados), 0.0)
        self.assertEqual(A.percentil_passado(0.7, passados), 25.0)
        self.assertEqual(A.percentil_passado(1.1, passados), 100.0)
        self.assertIsNone(A.percentil_passado(None, passados))


class TestAlertaSMO(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pw = power.Power(C.POWER["sao_miguel_do_oeste"])

    def test_safra_2021_22_ativo(self):
        a = A.alerta_seco(self.pw, dt.date(2022, 1, 25))
        self.assertEqual(a["estado"], "ativo")
        self.assertAlmostEqual(a["indice"], 0.618, places=3)
        self.assertEqual(a["percentil"], 0.0)
        self.assertEqual((a["n_anos_passados"], a["periodo_passado"]), (32, "1990-2021"))
        self.assertEqual(a["minimo_passado"], dict(ano=2009, valor=0.6771))  # spec 7.6

    def test_so_anos_passados_r6(self):
        a = A.alerta_seco(self.pw, dt.date(2022, 1, 25))
        self.assertTrue(all(int(k) < 2022 for k in a["serie_passada"]))
        # a série passada é a mesma da V1 (campo ind), ano a ano
        v1 = {x["ano"]: x["ind"] for x in C.ler_json(C.PAM_V1) if x["regiao"] == "SMO 42001"}
        for k, v in a["serie_passada"].items():
            self.assertAlmostEqual(v, v1[int(k)], places=4)

    def test_janela_parcial_inativo(self):
        # em 1/dez de 2021 a seca ainda não tinha chegado: índice até 1/dez, comparado com 1/dez dos outros anos
        a = A.alerta_seco(self.pw, dt.date(2021, 12, 1))
        self.assertEqual(a["estado"], "inativo")
        self.assertGreater(a["percentil"], 10)

    def test_janela_vai_ate_o_corte_efetivo(self):
        a = A.alerta_seco(self.pw, dt.date(2021, 12, 15))
        self.assertEqual(a["ate"], "2021-12-15")
        self.assertEqual(A.alerta_seco(self.pw, dt.date(2022, 1, 25))["ate"], "2022-01-10")

    def test_fora_da_janela(self):
        a = A.alerta_seco(self.pw, dt.date(2021, 7, 20))
        self.assertEqual(a["estado"], "fora_da_janela")
        self.assertIsNone(a["indice"])

    def test_numeros_da_validacao_v1(self):
        # regra que o motor roda: percentil só do passado (V1, passo 6)
        v = A.validacao_v1(C.V1_SO_PASSADO, C.V1_EXTENSAO)
        self.assertEqual((v["acertos"], v["alertas"], v["eventos_acerto"], v["eventos"]), (13, 29, 4, 9))
        self.assertEqual(v["eventos_novos"], "2/6")
        self.assertEqual((v["anos_assim_ruins_em_10"], v["ano_qualquer_ruim_em_10"], v["recall_pct"]), (4.5, 1.6, 48))
        self.assertFalse(v["criterios"]["C1"] or v["criterios"]["C3"])
        # a regra do passo 4 usava 1990-2025 inteiro, com anos futuros
        f = v["com_futuro"]
        self.assertEqual((f["acertos"], f["alertas"], f["eventos_acerto"], f["eventos"], f["eventos_novos"]), (14, 32, 4, 11, "2/8"))


class TestHistoricoCebola(unittest.TestCase):
    def test_primaveras_extremas(self):
        itu = power.Power(C.POWER["ituporanga"])
        h = A.historico_excesso(itu, 2024)
        self.assertEqual(h["periodo"], "1984-2023")
        self.assertEqual(h["anos_extremos"], [1997, 2008, 2015, 2023])
        self.assertTrue(all(int(k) < 2024 for k in h["serie"]))

    def test_fournier_igual_a3_1(self):
        itu = power.Power(C.POWER["ituporanga"])
        ex = X.avaliar(itu, C.S2_BLOCOS, 2024)
        self.assertLess(ex["dif_max_R_vs_A3"], 1e-9)
        self.assertEqual((ex["ano"], ex["mes_nome"], ex["n_blocos_lavoura"]), (2024, "julho", 2302))
        self.assertTrue(ex["chuva_forte"])


if __name__ == "__main__":
    unittest.main()
