#!/usr/bin/env python3
"""Balanço hídrico simples (FAO-56 + FAO-33) para estimar a chance de colher.

Entrada : dados/power_quixada.json (NASA POWER, diário, 2001-2025, Quixadá-CE)
Saída   : dados/resultado.json (usado pelo protótipo)

Tudo aqui é aproximação de hackathon. Parâmetros de cultura (Kc, fases, Ky) vêm da
FAO-56/FAO-33 e devem ser trocados pelos das portarias do ZARC. Ver spec-solucao.md.
"""
import json, math, datetime as dt, statistics as st
from pathlib import Path

AQUI = Path(__file__).resolve().parent.parent
LAT, ALT = -4.97, 190.0

# ---------- dados ----------
P = json.load(open(AQUI / "dados/power_quixada.json"))["properties"]["parameter"]
DIAS = sorted(P["PRECTOTCORR"].keys())
def d2date(s): return dt.date(int(s[:4]), int(s[4:6]), int(s[6:]))

# ---------- ET0 Penman-Monteith FAO-56 ----------
def e_sat(t): return 0.6108 * math.exp(17.27 * t / (t + 237.3))

def et0(day):
    d = d2date(day)
    tmax, tmin, tm = P["T2M_MAX"][day], P["T2M_MIN"][day], P["T2M"][day]
    rh, u2, rs = P["RH2M"][day], P["WS2M"][day], P["ALLSKY_SFC_SW_DWN"][day]
    es = (e_sat(tmax) + e_sat(tmin)) / 2
    ea = rh / 100 * e_sat(tm)
    delta = 4098 * e_sat(tm) / (tm + 237.3) ** 2
    pr = 101.3 * ((293 - 0.0065 * ALT) / 293) ** 5.26
    gam = 0.000665 * pr
    j = d.timetuple().tm_yday
    phi = math.radians(LAT)
    dr = 1 + 0.033 * math.cos(2 * math.pi * j / 365)
    dec = 0.409 * math.sin(2 * math.pi * j / 365 - 1.39)
    ws = math.acos(max(-1, min(1, -math.tan(phi) * math.tan(dec))))
    ra = 24 * 60 / math.pi * 0.082 * dr * (ws * math.sin(phi) * math.sin(dec) + math.cos(phi) * math.cos(dec) * math.sin(ws))
    rso = (0.75 + 2e-5 * ALT) * ra
    rnl = 4.903e-9 * (((tmax + 273.16) ** 4 + (tmin + 273.16) ** 4) / 2) * (0.34 - 0.14 * math.sqrt(max(ea, 0.01))) * (1.35 * min(rs / rso, 1) - 0.35)
    rn = 0.77 * rs - rnl
    num = 0.408 * delta * rn + gam * 900 / (tm + 273) * u2 * (es - ea)
    return max(0.5, num / (delta + gam * (1 + 0.34 * u2)))

ET0 = {d: et0(d) for d in DIAS}
CHUVA = {d: max(0.0, P["PRECTOTCORR"][d]) for d in DIAS}

# ---------- parâmetros por cultura (FAO-56 / FAO-33) ----------
# fases em dias: ini, dev, mid, late ; Kc: ini, mid, end ; Ky por fase (ini, dev, mid, late)
CULTURAS = {
    "caupi": dict(nome="Feijão-caupi", fases=(10, 20, 25, 15), kc=(0.40, 1.05, 0.35), ky=(0.2, 0.2, 1.1, 0.75), raiz=0.6),
    "milho": dict(nome="Milho", fases=(20, 30, 30, 20), kc=(0.30, 1.20, 0.60), ky=(0.4, 0.4, 1.5, 0.5), raiz=1.0),
    "sorgo": dict(nome="Sorgo", fases=(20, 30, 30, 20), kc=(0.30, 1.05, 0.55), ky=(0.2, 0.2, 0.55, 0.45), raiz=1.0),
}
# água disponível por textura (mm por metro), GAEZ v5
SOLOS = {"arenoso": 65, "medio": 125, "argiloso": 175}
P_DEPL = 0.5  # fração de água do CAD que a planta usa sem sofrer estresse


def kc_do_dia(cult, k):
    ini, dev, mid, late = cult["fases"]
    k_ini, k_mid, k_end = cult["kc"]
    if k < ini: return k_ini
    if k < ini + dev: return k_ini + (k_mid - k_ini) * (k - ini) / dev
    if k < ini + dev + mid: return k_mid
    return k_mid + (k_end - k_mid) * (k - ini - dev - mid) / late


def fase_do_dia(cult, k):
    acum = 0
    for i, n in enumerate(cult["fases"]):
        acum += n
        if k < acum: return i
    return 3


def agua_no_solo_em(data, cad):
    """Simula solo em pousio desde 1/dez do ano anterior até `data` (balde)."""
    s = 0.0
    d = dt.date(data.year - 1, 12, 1)
    while d < data:
        k = d.strftime("%Y%m%d")
        if k not in CHUVA: d += dt.timedelta(1); continue
        s = min(cad, s + CHUVA[k])
        s = max(0.0, s - 0.35 * ET0[k] * min(1.0, s / (0.5 * cad)) * 0.5)  # evaporação do solo nu, reduzida
        d += dt.timedelta(1)
    return s


def inicio_chuva(ano):
    """Regra de Sivakumar adaptada: 20 mm em 3 dias e sem sequência seca >7 dias (<=2 mm) nos 30 seguintes."""
    d = dt.date(ano, 1, 1)
    fim = dt.date(ano, 4, 30)
    while d <= fim:
        ks = [(d + dt.timedelta(i)).strftime("%Y%m%d") for i in range(3)]
        if all(k in CHUVA for k in ks) and sum(CHUVA[k] for k in ks) >= 20:
            ok, seco = True, 0
            for i in range(3, 33):
                k = (d + dt.timedelta(i)).strftime("%Y%m%d")
                if k not in CHUVA: ok = False; break
                seco = seco + 1 if CHUVA[k] <= 2 else 0
                if seco > 7: ok = False; break
            if ok: return d + dt.timedelta(2)
        d += dt.timedelta(1)
    return None


def simular(cultura, solo, plantio):
    """Retorna rendimento relativo (0-1), ISNA por fase e água no solo no plantio."""
    c = CULTURAS[cultura]
    cad = SOLOS[solo] * c["raiz"]
    s = agua_no_solo_em(plantio, cad)
    s0 = s
    n = sum(c["fases"])
    et_a = [0.0] * 4
    et_c = [0.0] * 4
    for k in range(n):
        d = plantio + dt.timedelta(k)
        key = d.strftime("%Y%m%d")
        if key not in CHUVA: return None
        kc = kc_do_dia(c, k)
        etc = kc * ET0[key]
        s = min(cad, s + CHUVA[key])
        ks = min(1.0, s / ((1 - P_DEPL) * cad)) if cad > 0 else 0
        eta = etc * ks
        s = max(0.0, s - eta)
        f = fase_do_dia(c, k)
        et_a[f] += eta
        et_c[f] += etc
    isna = [a / b if b else 1 for a, b in zip(et_a, et_c)]
    y = 1.0
    for i in range(4):
        y *= max(0.0, 1 - c["ky"][i] * (1 - isna[i]))
    return dict(y=round(y, 3), isna=[round(x, 2) for x in isna], agua_plantio=round(s0, 1), cad=round(cad, 1))


ANOS = list(range(2001, 2026))
FASES_NOME = ["emergência", "crescimento", "floração/enchimento", "maturação"]
LIMIAR_COLHE = 0.6  # perda < 40% (mesmo corte do Garantia-Safra, mas aqui por talhão)


def classe(y):
    return "boa" if y >= 0.7 else ("parcial" if y >= LIMIAR_COLHE else ("perda" if y >= 0.3 else "total"))


def estrategia(id_, nome, cultura, solo, regra, desc):
    anos = []
    for a in ANOS:
        if regra == "chuva":
            pl = inicio_chuva(a)
        else:  # ("data", mes, dia)
            pl = dt.date(a, regra[1], regra[2])
        if pl is None:
            anos.append(dict(ano=a, plantio=None, y=0.0, classe="sem_plantio", isna=None, agua_plantio=None)); continue
        r = simular(cultura, solo, pl)
        if r is None: continue
        anos.append(dict(ano=a, plantio=pl.isoformat(), classe=classe(r["y"]), **r))
    ys = [x["y"] for x in anos]
    colhe = sum(1 for x in anos if x["y"] >= LIMIAR_COLHE)
    pior = [0] * 4
    for x in anos:
        if x["isna"]:
            f = min(range(4), key=lambda i: x["isna"][i])
            if x["y"] < LIMIAR_COLHE: pior[f] += 1
    ruins = sum(pior)
    fase_pior = FASES_NOME[max(range(4), key=lambda i: pior[i])] if ruins else None
    # chance condicional pela data de início: plantio até 31/jan (cedo) contra depois
    com = [x for x in anos if x["plantio"]]
    cedo = [x for x in com if x["plantio"][5:] <= "01-31"]
    tarde = [x for x in com if x["plantio"][5:] > "01-31"]
    def pc(g): return (round(10 * sum(1 for x in g if x["y"] >= LIMIAR_COLHE) / len(g), 1), len(g)) if g else None
    seco, umido = cedo, tarde
    return dict(
        id=id_, nome=nome, cultura=cultura, solo=solo, desc=desc,
        colhe_em_10=round(10 * colhe / len(anos), 1), anos_total=len(anos),
        y_mediano=round(st.median(ys), 2), pior_fase=fase_pior,
        cond_cedo=pc(cedo), cond_tarde=pc(tarde),
        anos=anos,
    )


def janelas(cultura, solo):
    """Chance de colher por decêndio de plantio (para comparar com o ZARC)."""
    out = []
    for m in range(1, 7):
        for dia in (1, 11, 21):
            ys = []
            for a in ANOS:
                pl = dt.date(a, m, dia)
                r = simular(cultura, solo, pl)
                if r: ys.append(r["y"])
            if ys:
                out.append(dict(mes=m, dia=dia, colhe_em_10=round(10 * sum(1 for y in ys if y >= LIMIAR_COLHE) / len(ys), 1),
                                dec=(m - 1) * 3 + (dia - 1) // 10 + 1))
    return out


if __name__ == "__main__":
    solo = "medio"
    est = [
        estrategia("A", "Milho na 1ª chuva (o de sempre)", "milho", solo, "chuva", "Planta milho assim que a chuva firma."),
        estrategia("B", "Milho esperando a chuva firmar mais (11/mar)", "milho", solo, ("data", 3, 11), "Mesmo milho, plantio na janela de menor risco do ZARC para caupi."),
        estrategia("C", "Caupi (ciclo curto) na 1ª chuva", "caupi", solo, "chuva", "Troca a cultura por uma de 70 dias."),
        estrategia("D", "Sorgo na 1ª chuva", "sorgo", solo, "chuva", "Cultura mais tolerante à seca."),
        estrategia("E", "Caupi esperando até 11/mar", "caupi", solo, ("data", 3, 11), "Ciclo curto plantado na janela de menor risco do ZARC."),
    ]
    jan_caupi = janelas("caupi", solo)
    jan_milho = janelas("milho", solo)
    # ZARC 2026/27, caupi grupo I, sequeiro, solo tipo 2, Quixadá (conferido pelo agente a partir do CSV do MAPA)
    zarc = {3: 40, 4: 40, 5: 40, 6: 40, 7: 30, 8: 20, 9: 20, 10: 30}
    resultado = dict(
        municipio="Quixadá (CE)", lat=LAT, lon=-39.02, periodo="2001-2025", solo_padrao=solo,
        fonte="NASA POWER diário (PRECTOTCORR, T2M, RH2M, WS2M, ALLSKY_SFC_SW_DWN)",
        limiar_colhe=LIMIAR_COLHE, estrategias=est, janelas_caupi=jan_caupi, janelas_milho=jan_milho, zarc_caupi_medio=zarc,
        et0_media=round(st.mean(ET0.values()), 2),
    )
    json.dump(resultado, open(AQUI / "dados/resultado.json", "w"), ensure_ascii=False, indent=1)
    print("ET0 média", resultado["et0_media"], "mm/dia")
    for e in est:
        print(e["id"], e["nome"], "| colhe em 10:", e["colhe_em_10"], "| y mediano", e["y_mediano"], "| pior fase", e["pior_fase"],
              "| cedo/tarde:", e["cond_cedo"], e["cond_tarde"])
    print("\nJanelas caupi (dec: nossa chance de colher em 10 | ZARC risco):")
    for j in jan_caupi:
        print(f'dec{j["dec"]:>2} {j["dia"]:02d}/{j["mes"]:02d}: {j["colhe_em_10"]:>4} | ZARC {zarc.get(j["dec"], "fora")}')
