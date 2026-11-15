"""Módulo agua_isna no Semiárido (CE/PE/PB, milho).

Cópia fiel de prototipo/modelo/risco.py (ET0, balde com Ks, Ky por fase FAO-33, regra de início
de chuva de Sivakumar adaptada). A V5 (solucao/validacao/V5/motor.py, checa_fidelidade.py)
conferiu a mesma cópia: 48 de 48 pares iguais. Parâmetros fixos, sem ajuste.
"""
import datetime as dt
import statistics as st
from .power import Power, chave
from .estat import wilson

CULTURAS = {
    "caupi": dict(nome="Feijão-caupi", fases=(10, 20, 25, 15), kc=(0.40, 1.05, 0.35), ky=(0.2, 0.2, 1.1, 0.75), raiz=0.6),
    "milho": dict(nome="Milho", fases=(20, 30, 30, 20), kc=(0.30, 1.20, 0.60), ky=(0.4, 0.4, 1.5, 0.5), raiz=1.0),
    "sorgo": dict(nome="Sorgo", fases=(20, 30, 30, 20), kc=(0.30, 1.05, 0.55), ky=(0.2, 0.2, 0.55, 0.45), raiz=1.0),
}
SOLOS = {"arenoso": 65, "medio": 125, "argiloso": 175}  # mm/m, GAEZ v5 (tabela do protótipo)
P_DEPL = 0.5
LIMIAR_COLHE = 0.6
ALT_QUIXADA, LAT_QUIXADA = 190.0, -4.97  # como em risco.py (altitude da sede)


class Local:
    def __init__(self, caminho, alt=ALT_QUIXADA, lat=LAT_QUIXADA):
        self.pw = Power(caminho, alt=alt, lat=lat, piso=0.5)
        P = self.pw.P
        self.dias = sorted(P["PRECTOTCORR"])
        self.anos = sorted({int(k[:4]) for k in self.dias})
        self.CHUVA = {d: max(0.0, P["PRECTOTCORR"][d]) for d in self.dias}
        self.ET0 = {d: self.pw.et0(d) for d in self.dias}

    # --- risco.py: kc_do_dia, fase_do_dia (sem o min(1, .) na fase final, como no original)
    @staticmethod
    def kc_do_dia(c, k):
        ini, dev, mid, late = c["fases"]
        k_ini, k_mid, k_end = c["kc"]
        if k < ini:
            return k_ini
        if k < ini + dev:
            return k_ini + (k_mid - k_ini) * (k - ini) / dev
        if k < ini + dev + mid:
            return k_mid
        return k_mid + (k_end - k_mid) * (k - ini - dev - mid) / late

    @staticmethod
    def fase_do_dia(c, k):
        acum = 0
        for i, n in enumerate(c["fases"]):
            acum += n
            if k < acum:
                return i
        return 3

    def agua_no_solo_em(self, data, cad):
        s = 0.0
        d = dt.date(data.year - 1, 12, 1)
        while d < data:
            k = chave(d)
            if k not in self.CHUVA:
                d += dt.timedelta(1)
                continue
            s = min(cad, s + self.CHUVA[k])
            s = max(0.0, s - 0.35 * self.ET0[k] * min(1.0, s / (0.5 * cad)) * 0.5)
            d += dt.timedelta(1)
        return s

    def inicio_chuva(self, ano):
        d = dt.date(ano, 1, 1)
        fim = dt.date(ano, 4, 30)
        C = self.CHUVA
        while d <= fim:
            ks = [chave(d + dt.timedelta(i)) for i in range(3)]
            if all(k in C for k in ks) and sum(C[k] for k in ks) >= 20:
                ok, seco = True, 0
                for i in range(3, 33):
                    k = chave(d + dt.timedelta(i))
                    if k not in C:
                        ok = False
                        break
                    seco = seco + 1 if C[k] <= 2 else 0
                    if seco > 7:
                        ok = False
                        break
                if ok:
                    return d + dt.timedelta(2)
            d += dt.timedelta(1)
        return None

    def simular(self, cultura, solo, plantio):
        c = CULTURAS[cultura]
        cad = SOLOS[solo] * c["raiz"]
        s = self.agua_no_solo_em(plantio, cad)
        s0 = s
        n = sum(c["fases"])
        et_a, et_c = [0.0] * 4, [0.0] * 4
        for k in range(n):
            key = chave(plantio + dt.timedelta(k))
            if key not in self.CHUVA:
                return None
            etc = self.kc_do_dia(c, k) * self.ET0[key]
            s = min(cad, s + self.CHUVA[key])
            ks = min(1.0, s / ((1 - P_DEPL) * cad)) if cad > 0 else 0
            eta = etc * ks
            s = max(0.0, s - eta)
            f = self.fase_do_dia(c, k)
            et_a[f] += eta
            et_c[f] += etc
        isna = [a / b if b else 1 for a, b in zip(et_a, et_c)]
        y = 1.0
        for i in range(4):
            y *= max(0.0, 1 - c["ky"][i] * (1 - isna[i]))
        return dict(y=round(y, 3), isna=[round(x, 2) for x in isna], agua_plantio=round(s0, 1), cad=round(cad, 1))

    def estrategia(self, cultura, solo, regra):
        """regra = 'chuva' ou ('data', mes, dia). Ano sem plantio vale y = 0 (como risco.py)."""
        anos = []
        for a in self.anos:
            pl = self.inicio_chuva(a) if regra == "chuva" else dt.date(a, regra[1], regra[2])
            if pl is None:
                anos.append(dict(ano=a, plantio=None, y=0.0))
                continue
            r = self.simular(cultura, solo, pl)
            if r is None:
                continue
            anos.append(dict(ano=a, plantio=pl.isoformat(), y=r["y"], isna=r["isna"]))
        n = len(anos)
        k = sum(1 for x in anos if x["y"] >= LIMIAR_COLHE)
        lo, hi = wilson(k, n)
        return dict(cultura=cultura, solo=solo, regra=regra if regra == "chuva" else f"data {regra[2]:02d}/{regra[1]:02d}",
                    n=n, k_colhe=k, colhe_em_10=round(10 * k / n, 1), ic95_colhe=[round(10 * lo, 1), round(10 * hi, 1)],
                    falha_em_10=round(10 * (n - k) / n, 1), ic95_falha=[round(10 * (1 - hi), 1), round(10 * (1 - lo), 1)],
                    y_mediano=round(st.median(x["y"] for x in anos), 2),
                    sem_plantio=sum(1 for x in anos if x["plantio"] is None),
                    periodo=f"{anos[0]['ano']}-{anos[-1]['ano']}", anos=anos)

    def janelas(self, cultura, solo, meses=range(1, 7)):
        out = []
        for m in meses:
            for dia in (1, 11, 21):
                ys = []
                for a in self.anos:
                    r = self.simular(cultura, solo, dt.date(a, m, dia))
                    if r:
                        ys.append(r["y"])
                if ys:
                    n = len(ys)
                    k = sum(1 for y in ys if y >= LIMIAR_COLHE)
                    lo, hi = wilson(n - k, n)
                    out.append(dict(decendio=f"{dia:02d}/{m:02d}", dec=(m - 1) * 3 + (dia - 1) // 10 + 1, n=n,
                                    k_falha=n - k, colhe_em_10=round(10 * k / n, 1), falha_em10=round(10 * (n - k) / n, 1),
                                    ic95_falha=[round(10 * lo, 1), round(10 * hi, 1)]))
        return out

    def et0_media(self):
        return round(st.mean(v for v in self.ET0.values() if v is not None), 2)
