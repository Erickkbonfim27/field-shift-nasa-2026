"""ET0 Penman-Monteith FAO-56."""
import unittest

import _base  # noqa: F401
from motor import config as C
from motor import power
from motor import semiarido as SA


class TestET0(unittest.TestCase):
    def test_e_sat_fao56(self):
        # FAO-56, tabela 2.3: e°(25 °C) = 3,168 kPa; e°(10 °C) = 1,228 kPa
        self.assertAlmostEqual(power.e_sat(25.0), 3.168, places=3)
        self.assertAlmostEqual(power.e_sat(10.0), 1.228, places=3)

    def test_ra_exemplo_8_fao56(self):
        # FAO-56, exemplo 8: 20° S, 3 de setembro (dia 246) -> Ra = 32,2 MJ m-2 dia-1
        self.assertAlmostEqual(power.radiacao_ra(-20.0, 246), 32.2, delta=0.1)

    def test_et0_exemplo_18_fao56(self):
        # FAO-56, exemplo 18 (Bruxelas, 6/jul, 50°48' N, 100 m): ET0 = 3,9 mm/dia.
        # ea = 1,409 kPa; o motor usa ea = RH/100 * e(Tmed), então passamos o RH que dá esse ea.
        tmed = (21.5 + 12.3) / 2
        rh = 100 * 1.409 / power.e_sat(tmed)
        et0 = power.et0_fao56(21.5, 12.3, tmed, rh, 2.078, 22.07, 50.8, 100.0, 187)
        self.assertAlmostEqual(et0, 3.9, delta=0.1)

    def test_piso(self):
        # dia frio e escuro: a ET0 cai no piso do script validado
        self.assertEqual(power.et0_fao56(5, 0, 2.5, 99, 0.5, 1.0, -27.0, 600, 180, piso=0.5), 0.5)
        bruto = power.et0_fao56(5, 0, 2.5, 99, 0.5, 1.0, -27.0, 600, 180, piso=-99)
        self.assertLess(bruto, 0.5)
        self.assertEqual(power.et0_fao56(5, 0, 2.5, 99, 0.5, 1.0, -27.0, 600, 180, piso=0.3), max(0.3, bruto))

    def test_falta_allsky_1981(self):
        # ALLSKY vazio de 1981 a 1983 no POWER de SMO: sem ET0
        pw = power.Power(C.POWER["sao_miguel_do_oeste"])
        self.assertIsNone(pw.et0("19820615"))
        self.assertIsNotNone(pw.et0("19840615"))
        self.assertEqual(pw.primeiro_dia_com_et0()[:4], "1984")

    def test_reproduz_et0_media_do_prototipo(self):
        # prototipo/dados/resultado.json: et0_media = 6,47 mm/dia em Quixadá (2001-2025)
        ref = C.ler_json(C.RAIZ / "prototipo" / "dados" / "resultado.json")["et0_media"]
        self.assertEqual(SA.Local(C.POWER["quixada"]).et0_media(), ref)


if __name__ == "__main__":
    unittest.main()
