"""Balanço hídrico (balde FAO-56/FAO-33): unidades sintéticas e reprodução dos scripts validados."""
import datetime as dt
import unittest

import _base  # noqa: F401
from motor import config as C
from motor import balanco as B
from motor import power
from motor import semiarido as SA
from motor import mistura as M


class PowerFalso:
    """Série sintética: ET0 e chuva constantes."""

    def __init__(self, et0=5.0, chuva=0.0, ini=dt.date(2000, 1, 1), dias=400):
        self.chuva, self._e = {}, {}
        for i in range(dias):
            k = power.chave(ini + dt.timedelta(i))
            self.chuva[k] = chuva
            self._e[k] = et0

    def et0(self, k):
        return self._e.get(k)


class TestBalde(unittest.TestCase):
    def test_kc_curva(self):
        f, kc = (25, 40, 45, 30), (0.30, 1.20, 0.60)
        self.assertEqual(B.kc_curva(f, kc, 0), 0.30)
        self.assertAlmostEqual(B.kc_curva(f, kc, 45), 0.75)  # metade da fase de desenvolvimento
        self.assertEqual(B.kc_curva(f, kc, 80), 1.20)
        self.assertAlmostEqual(B.kc_curva(f, kc, 139), 1.20 + (0.60 - 1.20) * 29 / 30)
        self.assertEqual(B.kc_curva(f, kc, 500), 0.60)  # depois do ciclo não passa do Kc final

    def test_chuva_farta_isna_1_e_excedente(self):
        pw = PowerFalso(et0=4.0, chuva=20.0)
        b = B.balde(pw, dt.date(2000, 4, 1), dt.date(2000, 8, 1), (25, 40, 45, 30), (0.3, 1.2, 0.6), 100.0)
        self.assertAlmostEqual(B.isna(b), 1.0)
        self.assertTrue(all(0 <= x["s"] <= 100.0 for x in b))
        self.assertTrue(all(x["exced"] > 0 for x in b))  # balde cheio: chuva que sobra vira excedente

    def test_sem_chuva_estresse_e_limites(self):
        pw = PowerFalso(et0=5.0, chuva=0.0)
        b = B.balde(pw, dt.date(2000, 4, 1), dt.date(2000, 8, 1), (25, 40, 45, 30), (0.3, 1.2, 0.6), 100.0)
        self.assertLess(B.isna(b), 0.5)
        self.assertTrue(all(x["eta"] <= x["etc"] + 1e-12 for x in b))
        self.assertTrue(all(x["s"] >= 0 for x in b))
        s = [x["s"] for x in b]
        self.assertTrue(all(a >= b_ - 1e-12 for a, b_ in zip(s, s[1:])))  # sem chuva o balde só desce

    def test_ks_reduz_abaixo_de_p(self):
        # com p = 0,5 e CAD 100, a ETa só cai quando o balde passa de 50 mm
        pw = PowerFalso(et0=2.0, chuva=0.0)
        b = B.balde(pw, dt.date(2000, 4, 1), dt.date(2000, 4, 30), (25, 40, 45, 30), (1.0, 1.0, 1.0), 1000.0,
                    kc_antes=1.0, dias_antes=0)
        self.assertTrue(all(abs(x["eta"] - x["etc"]) < 1e-12 for x in b))

    def test_falta_dado(self):
        pw = PowerFalso(dias=30)
        self.assertIsNone(B.balde(pw, dt.date(2000, 3, 1), dt.date(2000, 6, 1), (25, 40, 45, 30), (0.3, 1.2, 0.6), 100.0))


class TestReproducao(unittest.TestCase):
    """Teste de aceitação A2/A4 da spec: o motor reproduz os scripts validados."""

    @classmethod
    def setUpClass(cls):
        cls.smo = power.Power(C.POWER["sao_miguel_do_oeste"])
        cls.itu = power.Power(C.POWER["ituporanga"])
        cls.tab = C.ler_json(C.PAM_V1)

    def test_isna_milho_igual_v1(self):
        # V1/tabela_original.json, campo ind (ISNA B3-1) da microrregião 42001, 1990-2025
        linhas = [x for x in self.tab if x["regiao"] == "SMO 42001"]
        self.assertEqual(len(linhas), 36)
        for x in linhas:
            self.assertAlmostEqual(B.isna_milho_b31(self.smo, x["ano"]), x["ind"], places=4, msg=x["ano"])
        self.assertAlmostEqual(B.isna_milho_b31(self.smo, 2022), 0.618, places=3)

    def test_excedente_cebola_igual_v1(self):
        for x in (x for x in self.tab if x["regiao"] == "Ituporanga 42014"):
            self.assertAlmostEqual(B.excedente_cebola_b32(self.itu, x["ano"]), x["ind"], delta=0.051, msg=x["ano"])

    def test_isna_parcial_causal(self):
        # parar o balde antes não muda os dias anteriores
        a = B.isna_milho_b31(self.smo, 2022, ate=dt.date(2021, 12, 1))
        pl = dt.date(2021, 9, 20)
        b = B.balde(self.smo, pl, dt.date(2022, 1, 10), B.MILHO_B31["fases"], B.MILHO_B31["kc"], 125.0, 0.5)
        self.assertAlmostEqual(a, B.isna(b, dt.date(2021, 12, 1)), places=12)

    def test_semiarido_igual_risco_py(self):
        # A4 da spec: reproduz prototipo/modelo/risco.py (resultado.json) em Quixadá
        ref = C.ler_json(C.RAIZ / "prototipo" / "dados" / "resultado.json")
        L = SA.Local(C.POWER["quixada"])
        regras = {"A": ("milho", "chuva"), "B": ("milho", ("data", 3, 11)), "C": ("caupi", "chuva"),
                  "D": ("sorgo", "chuva"), "E": ("caupi", ("data", 3, 11))}
        for e in ref["estrategias"]:
            r = L.estrategia(*regras[e["id"]][:1], "medio", regras[e["id"]][1])
            self.assertEqual(r["colhe_em_10"], e["colhe_em_10"], e["id"])
            self.assertEqual(r["y_mediano"], e["y_mediano"], e["id"])
            for a, b in zip([x for x in r["anos"]], e["anos"]):
                self.assertEqual(a["y"], b["y"], (e["id"], a["ano"]))
        for nome in ("milho", "caupi"):
            jm = L.janelas(nome, "medio")
            self.assertEqual([j["colhe_em_10"] for j in jm], [j["colhe_em_10"] for j in ref[f"janelas_{nome}"]])

    def test_mistura_igual_v3_cad42(self):
        # V3/res_02_central_grade.json: central.V3b_raso_ZARC_42['0.5'] e a grade de 270
        ref = C.ler_json(C.VAL / "V3" / "res_02_central_grade.json")
        S = M.Serie(C.POWER["sao_miguel_do_oeste"])
        r = M.avaliar(S, 42.0)
        c = ref["central"]["V3b_raso_ZARC_42"]["0.5"]
        self.assertAlmostEqual(r["central"]["ganho_p10"], c["ganho_p10"], places=6)
        self.assertAlmostEqual(r["central"]["var_media"], c["var_media"], places=6)
        self.assertEqual(r["central"]["base_perda"], c["base_perda"])
        self.assertEqual(r["central"]["perda"], c["perda"])
        # bootstrap com outro gerador: o IC95 fica perto, não igual
        for a, b in zip(r["central"]["ic95_ganho_p10"], c["boot_p10_ic95"]):
            self.assertAlmostEqual(a, b, delta=3.0)
        g = [l for l in ref["grade"]["V3b_raso_ZARC_42"] if l["scen"] in ("A4", "FAO33", "BIOMASSA")]
        self.assertEqual(r["grade"]["n"], len(g))
        self.assertAlmostEqual(r["grade"]["sobrevive_pct"], 100 * sum(l["ok"] for l in g) / len(g), places=6)
        self.assertAlmostEqual(r["grade"]["ganho_p10_mediana"], 13.885596449555472, places=6)
        x = C.ler_json(C.VAL / "V3" / "res_03_extras.json")["por_data"]
        for l in r["por_data"]:
            self.assertAlmostEqual(l["ganho_p10_pct"], x[f"raso_ZARC_42|{l['decendio']}"]["ganho_p10"], places=6)


if __name__ == "__main__":
    unittest.main()
