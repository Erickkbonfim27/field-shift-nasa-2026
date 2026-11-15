"""Geada: regra de contagem, reprodução da V4 (D1) e da V2, e o gabarito ZARC (aceitação A3)."""
import datetime as dt
import unittest

import _base  # noqa: F401
from motor import config as C
from motor import geada as G
from motor import power
from motor import conferencia as K


class TminFalso:
    def __init__(self, tmin, tmax=28.0, ini=dt.date(2000, 1, 1), dias=400, frio=None):
        self.tmin, self.tmax = {}, {}
        for i in range(dias):
            d = ini + dt.timedelta(i)
            k = power.chave(d)
            self.tmin[k] = (frio or {}).get(d, tmin)
            self.tmax[k] = tmax


class TestRegras(unittest.TestCase):
    def test_safra_conta_so_fases_I_a_III_e_menor_estrito(self):
        pl = dt.date(2000, 3, 1)
        dentro = pl + dt.timedelta(99)
        fora = pl + dt.timedelta(100)
        self.assertEqual(G.geada_safra(TminFalso(10, frio={dentro: 1.9}), pl), 1)
        self.assertEqual(G.geada_safra(TminFalso(10, frio={fora: -5.0}), pl), 0)
        self.assertEqual(G.geada_safra(TminFalso(10, frio={dentro: 2.0}), pl), 0)  # < 2 °C, estrito (V4)

    def test_2a_safra_menor_ou_igual_e_gdd(self):
        pl = dt.date(2000, 2, 1)
        # Tmed = (28 + 12)/2 = 20 -> 10 °C·dia por dia -> silagem em 125 dias
        r = G.safra_2m(TminFalso(12.0), 2000, 2, 1)
        self.assertEqual(r["dias"], 125)
        self.assertIsNone(r["prim"][3.0])
        r = G.safra_2m(TminFalso(12.0, frio={pl + dt.timedelta(50): 3.0}), 2000, 2, 1)
        self.assertEqual(r["prim"][3.0], pl + dt.timedelta(50))  # <= 3 °C conta (V2)
        self.assertIsNone(r["prim"][2.0])

    def test_decendios(self):
        self.assertEqual(G.decendio_de(dt.date(2001, 2, 5)), "01/02")
        self.assertEqual(G.decendio_de(dt.date(2001, 2, 20)), "11/02")
        self.assertEqual(G.decendio_seguinte("21/12"), "01/01")
        self.assertEqual(G.indice_decendio("21/08") + 1, G.indice_decendio("01/09"))


class TestReproducao(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pw = power.Power(C.POWER["sao_miguel_do_oeste"])
        cls.janela = G.tabela_janela_safra(cls.pw)
        cls.curva = G.curva_2m(cls.pw)
        cls.lim = G.limites_2m(cls.pw)

    def test_janela_safra_igual_v4_d1(self):
        ref = C.ler_json(C.VAL / "V4" / "v4_resultado.json")["decisao_D1_data_milho_SMO"]
        self.assertEqual([l["decendio"] for l in self.janela["linhas"]], [r["data"] for r in ref])
        for l, r in zip(self.janela["linhas"], ref):
            self.assertEqual(l["n"], r["n"])
            self.assertEqual(l["em10"], r["geada_em10"], l["decendio"])
        self.assertEqual(self.janela["linhas"][0]["em10"], 6.3)  # 1/ago (spec: N3)

    def test_2a_safra_igual_v2(self):
        ref = C.ler_json(C.VAL / "V2" / "v2_resultado.json")
        tab = ref["tabela_decendio"]["SMO (São Miguel do Oeste)"]
        for l in self.curva["linhas"]:
            r = tab[l["decendio"]]
            self.assertEqual((l["k"], l["n"], l["em10"]), (r["L3"]["k"], r["n"], r["L3"]["em10"]))
            self.assertEqual(l["ic95"], [r["L3"]["ic_lo"], r["L3"]["ic_hi"]])
            self.assertEqual(l["dias_ate_silagem_mediana"], r["dias_med"])
        self.assertEqual(self.lim["central"], ref["limite"]["SMO (São Miguel do Oeste)"]["L3"]["limite"])
        self.assertEqual(self.lim["central"], "05/02")
        for L in ("2", "3", "4"):
            self.assertEqual(self.lim["por_limiar_c"][L], ref["limite"]["SMO (São Miguel do Oeste)"][f"L{L}"]["limite"])
        self.assertEqual(self.lim["por_ciclo_gdd"], ref["limite_gdd_smo_L3"])

    def test_aceitacao_a3_zarc(self):
        # A3: 1º decêndio com risco <= 2 em 10 até 1 decêndio do 1º com 20% no ZARC;
        #     último plantio do 2º milho até 20 dias do último do ZARC. ZARC só confere.
        zm = K.zarc_milho("sao_miguel_do_oeste", "AD3")
        z20 = next(d for d, r in zm.items() if r == 20)
        nosso = G.primeiro_seguro(self.janela)
        self.assertEqual((nosso, z20), ("01/09", "21/08"))
        self.assertLessEqual(abs(G.indice_decendio(nosso) - G.indice_decendio(z20)), 1)
        ult = max((d for d in zm if d[3:] == "01"), key=lambda d: int(d[:2]))
        dias = (G.ddmm_para_data(self.lim["central"]) - G.ddmm_para_data(ult)).days
        self.assertLessEqual(abs(dias), 20)

    def test_celula_dionisio_igual(self):
        a = power.Power(C.POWER["sao_miguel_do_oeste"])
        self.assertEqual(power.mesma_celula(a, power.Power(C.POWER["dionisio_cerqueira"]))["dias_diferentes"], 0)
        self.assertGreater(power.mesma_celula(a, power.Power(C.POWER["chapeco"]))["dias_diferentes"], 10000)


class TestCacheSafras(unittest.TestCase):
    """Regressão: o cache de _safras_dia era global e indexado por id(pw); um id reaproveitado
    depois de liberar o objeto devolvia as safras de outra célula."""

    @staticmethod
    def _direto(pw, mes, dia, anos):
        return [r for a in anos if (r := G.safra_2m(pw, a, mes, dia, G.GDD_PADRAO))]

    def test_cache_nao_vaza_entre_celulas(self):
        import gc
        anos = list(range(2000, 2004))
        quente = TminFalso(15, ini=dt.date(1999, 12, 1), dias=1800)
        frio = TminFalso(15, ini=dt.date(1999, 12, 1), dias=1800,
                         frio={dt.date(a, 4, 10): 0.0 for a in anos})
        esperado_quente = self._direto(quente, 2, 1, anos)
        self.assertTrue(all(not r["prim"][3.0] for r in esperado_quente))
        G._safras_dia(frio, 2, 1, G.GDD_PADRAO, anos)
        del frio
        gc.collect()
        for _ in range(50):  # objetos novos tendem a reusar o id do liberado
            novo = TminFalso(15, ini=dt.date(1999, 12, 1), dias=1800)
            self.assertEqual(G._safras_dia(novo, 2, 1, G.GDD_PADRAO, anos), esperado_quente)
        self.assertEqual(G._safras_dia(quente, 2, 1, G.GDD_PADRAO, anos), esperado_quente)


if __name__ == "__main__":
    unittest.main()
