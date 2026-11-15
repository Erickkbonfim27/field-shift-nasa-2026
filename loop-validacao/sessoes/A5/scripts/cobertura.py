#!/usr/bin/env python3
"""A5-1: janela de semeadura da planta de cobertura (NASA POWER, 1984-2025).

Modelo simples, de hackathon (todos os parâmetros de planta são [ESTIMATIVA], ver ficha):
  1. Solo superficial (0-10 cm, 15 mm) para a germinação; zona das raízes (150 mm/m) para o crescimento.
  2. Emergência: soma de graus-dia só em dias com solo superficial úmido (>= metade cheio).
     Sem emergência em 30 dias = falha.
  3. Morte da plântula: >= 6 dias seguidos com solo superficial seco (>= 80% esgotado)
     nos 15 dias após a emergência = falha ("falso começo").
  4. Crescimento: graus-dia x Ks (estresse hídrico FAO-56). "Boa cobertura" = soma alvo de graus-dia.
     Geada (Tmin POWER <= 1 °C) mata as coberturas de verão.
  5. Sucesso = emergiu, não morreu e chegou na boa cobertura antes do prazo.
Uso: python cobertura.py <pasta loop-validacao/dados> <pasta saída>
"""
import json, math, sys, datetime as dt
from pathlib import Path
import numpy as np

DADOS, OUT = Path(sys.argv[1]), Path(sys.argv[2])
OUT.mkdir(parents=True, exist_ok=True)

ESPECIES = {
    # tb: temp. base; tcap: acima disso não acelera; g_germ: graus-dia úmidos até emergir;
    # g_cob: graus-dia (x Ks) até "boa cobertura" (~80% do solo / ~3 t/ha MS); kc: Kc cheio; zmax: raiz (m)
    "milheto":  dict(tb=10, tcap=34, g_germ=40, g_cob=550, kc=1.0, zmax=0.8, p=0.55, geada=True, calor=None),
    "mucuna":   dict(tb=10, tcap=33, g_germ=60, g_cob=900, kc=1.0, zmax=0.8, p=0.50, geada=True, calor=None),
    "aveia":    dict(tb=0,  tcap=25, g_germ=70, g_cob=900, kc=1.0, zmax=0.6, p=0.55, geada=False, calor=30),
}
# (caso, arquivo, especie, ini (mês,dia), fim (mês,dia), prazo (mês,dia, +anos), habitual (mês,dia), lat, ano de semeadura = ano-safra + desloc)
CASOS = [
    ("I-MIL", "power_ituporanga.json", "milheto", (11, 20), (1, 31), (4, 30), (12, 15), -27.414),
    ("I-MUC", "power_ituporanga.json", "mucuna",  (11, 20), (1, 31), (4, 30), (12, 15), -27.414),
    ("I-AVE", "power_ituporanga.json", "aveia",   (3, 1),   (5, 31), (7, 10), (4, 15), -27.414),
    ("S-AVE", "power_sao_miguel_do_oeste.json", "aveia", (2, 14), (5, 31), (8, 15), (4, 15), -26.725),
]
TAW_M, TAW_SUP = 150.0, 15.0

def carrega(arq, lat):
    d = json.load(open(DADOS / arq))
    alt = d["geometry"]["coordinates"][2]
    P = d["properties"]["parameter"]
    dias = sorted(P["T2M"].keys())
    datas = [dt.date(int(s[:4]), int(s[4:6]), int(s[6:])) for s in dias]
    arr = {k: np.array([P[k][s] for s in dias], float) for k in ("PRECTOTCORR", "T2M", "T2M_MAX", "T2M_MIN", "RH2M", "WS2M", "ALLSKY_SFC_SW_DWN")}
    doy = np.array([x.timetuple().tm_yday for x in datas])
    for k, a in arr.items():  # faltante -999: preenche com a média do dia do ano
        bad = a < -900
        if k == "ALLSKY_SFC_SW_DWN":
            bad |= np.array([x.year < 1984 for x in datas])
        if bad.any():
            clim = {j: np.nanmean(np.where(bad | (doy != j), np.nan, a)) for j in set(doy[bad])}
            a[bad] = [clim[j] for j in doy[bad]]
    arr["PRECTOTCORR"] = np.maximum(arr["PRECTOTCORR"], 0)
    arr["ET0"] = et0(arr, doy, lat, alt)
    return datas, arr

def et0(a, doy, lat, alt):  # Penman-Monteith FAO-56 (mesma fórmula de prototipo/modelo/risco.py)
    es_ = lambda t: 0.6108 * np.exp(17.27 * t / (t + 237.3))
    tmax, tmin, tm, rh, u2, rs = a["T2M_MAX"], a["T2M_MIN"], a["T2M"], a["RH2M"], a["WS2M"], a["ALLSKY_SFC_SW_DWN"]
    es = (es_(tmax) + es_(tmin)) / 2; ea = rh / 100 * es_(tm)
    delta = 4098 * es_(tm) / (tm + 237.3) ** 2
    gam = 0.000665 * 101.3 * ((293 - 0.0065 * alt) / 293) ** 5.26
    phi = math.radians(lat); dr = 1 + 0.033 * np.cos(2 * np.pi * doy / 365)
    dec = 0.409 * np.sin(2 * np.pi * doy / 365 - 1.39)
    ws = np.arccos(np.clip(-math.tan(phi) * np.tan(dec), -1, 1))
    ra = 24 * 60 / np.pi * 0.082 * dr * (ws * math.sin(phi) * np.sin(dec) + math.cos(phi) * np.cos(dec) * np.sin(ws))
    rso = (0.75 + 2e-5 * alt) * ra
    rnl = 4.903e-9 * (((tmax + 273.16) ** 4 + (tmin + 273.16) ** 4) / 2) * (0.34 - 0.14 * np.sqrt(np.maximum(ea, 0.01))) * (1.35 * np.minimum(rs / rso, 1) - 0.35)
    rn = 0.77 * rs - rnl
    return np.maximum(0.5, (0.408 * delta * rn + gam * 900 / (tm + 273) * u2 * (es - ea)) / (delta + gam * (1 + 0.34 * u2)))

def simula(a, i0, i_prazo, sp, escala=1.0):
    """Retorna (resultado, dias até boa cobertura). resultado: 'ok', 'sem_emergencia', 'morte_plantula', 'nao_cobriu'."""
    # aquecimento: 30 dias de solo nu antes da semeadura
    dsup, dr = TAW_SUP / 2, 0.0
    for i in range(i0 - 30, i0):
        dsup = min(TAW_SUP, max(0, dsup - a["PRECTOTCORR"][i]) + a["ET0"][i] * (TAW_SUP - dsup) / TAW_SUP)
        dr = min(TAW_M * 0.3, max(0, dr - a["PRECTOTCORR"][i]) + 0.3 * a["ET0"][i] * (1 - dr / (TAW_M * 0.3)))
    g_germ, gcov, emerg, seca, cob, tb = 0.0, 0.0, None, 0, 0.0, sp["tb"]
    calor = []
    for i in range(i0, i_prazo + 1):
        chuva, e0 = a["PRECTOTCORR"][i], a["ET0"][i]
        gd = max(0.0, min(a["T2M"][i], sp["tcap"]) - tb)
        frac = min(1.0, gcov / (sp["g_cob"] * escala))
        zr = 0.1 + (sp["zmax"] - 0.1) * frac
        taw = TAW_M * zr
        # solo superficial (evaporação + transpiração inicial)
        dsup = min(TAW_SUP, max(0, dsup - chuva) + e0 * (TAW_SUP - dsup) / TAW_SUP)
        if emerg is None:
            if dsup <= 0.5 * TAW_SUP:
                g_germ += gd
            if g_germ >= sp["g_germ"]:
                emerg = i
            elif i - i0 >= 30:
                return "sem_emergencia", None
            continue
        # zona das raízes
        dr = max(0, dr - chuva)
        ks = 1.0 if dr <= sp["p"] * taw else max(0.0, (taw - dr) / ((1 - sp["p"]) * taw))
        kc = 0.3 + (sp["kc"] - 0.3) * frac
        dr = min(taw, dr + kc * e0 * ks)
        if i - emerg < 15:
            seca = seca + 1 if (dsup >= 0.8 * TAW_SUP and dr >= 0.8 * taw) else 0
            if seca >= 6:
                return "morte_plantula", None
            calor.append(a["T2M_MAX"][i])
        fator = 1.0
        if sp["calor"] and len(calor) == 15 and np.mean(calor) > sp["calor"]:
            fator = 0.6
        if sp["geada"] and a["T2M_MIN"][i] <= 1.0:
            return "nao_cobriu", None
        gcov += gd * ks * fator
        if gcov >= sp["g_cob"] * escala:
            return "ok", i - i0
    return "nao_cobriu", None

def idx(datas, d):
    return (d - datas[0]).days

def datas_janela(ano_safra, ini, fim):
    """ano_safra = ano da colheita anterior. Para janelas que viram o ano (nov->jan), o fim cai em ano+1."""
    d0 = dt.date(ano_safra, *ini)
    d1 = dt.date(ano_safra + (1 if fim[0] < ini[0] else 0), *fim)
    out, d = [], d0
    while d <= d1:
        out.append(d); d += dt.timedelta(days=5)
    return out

def prazo_de(ano_safra, ini, prazo):
    return dt.date(ano_safra + (1 if prazo[0] < ini[0] else 0), *prazo)

def habitual_de(ano_safra, ini, hab):
    return dt.date(ano_safra + (1 if hab[0] < ini[0] else 0), *hab)

def regra_dinamica(datas, a, d_hab, limite=20):
    """A partir da data habitual, semeia no 1º dia com chuva dos últimos 3 dias >= 15 mm; senão, na data limite."""
    i = idx(datas, d_hab)
    for k in range(limite + 1):
        if a["PRECTOTCORR"][i + k - 2:i + k + 1].sum() >= 15:
            return datas[i + k]
    return datas[i + limite]

def main():
    resumo = {}
    for caso, arq, esp, ini, fim, prazo, hab, lat in CASOS:
        datas, a = carrega(arq, lat)
        sp = ESPECIES[esp]
        ultimo = datas[-1]
        anos = [y for y in range(1984, 2026) if prazo_de(y, ini, prazo) <= ultimo]
        janela_ref = datas_janela(2001, ini, fim)
        rotulos = [d.strftime("%d/%m") for d in janela_ref]
        res = {}
        for escala in (0.8, 1.0, 1.25):
            M = np.zeros((len(anos), len(janela_ref)), dtype=object)
            for yi, y in enumerate(anos):
                ip = idx(datas, prazo_de(y, ini, prazo))
                for di, d in enumerate(datas_janela(y, ini, fim)[:len(janela_ref)]):
                    M[yi, di] = simula(a, idx(datas, d), ip, sp, escala)[0]
            res[escala] = M
        M = res[1.0]
        ok = (M == "ok").astype(float)
        treino = np.array([y <= 2004 for y in anos]); teste = ~treino
        di_hab = rotulos.index(dt.date(2001 + (1 if hab[0] < ini[0] else 0), *hab).strftime("%d/%m"))
        p_tr, p_te = ok[treino].mean(0), ok[teste].mean(0)
        di_best = int(np.argmax(p_tr))  # empate: a mais cedo
        # regra dinâmica
        din, din_falha, hab_falha = [], [], []
        for y in [y for y, t in zip(anos, teste) if t]:
            ip = idx(datas, prazo_de(y, ini, prazo))
            d_hab = habitual_de(y, ini, hab)
            dd = regra_dinamica(datas, a, d_hab)
            r = simula(a, idx(datas, dd), ip, sp)[0]
            rh = simula(a, idx(datas, d_hab), ip, sp)[0]
            din.append(r == "ok"); din_falha.append(r in ("sem_emergencia", "morte_plantula"))
            hab_falha.append(rh in ("sem_emergencia", "morte_plantula"))
        dias_ok = []
        for di in range(len(janela_ref)):
            v = []
            for yi, y in enumerate(anos):
                ip = idx(datas, prazo_de(y, ini, prazo))
                d = datas_janela(y, ini, fim)[di]
                r, n = simula(a, idx(datas, d), ip, sp)
                if r == "ok": v.append(n)
            dias_ok.append(float(np.median(v)) if v else None)
        causas = {c: [(M[:, di] == c).mean().round(3) for di in range(len(janela_ref))] for c in ("ok", "sem_emergencia", "morte_plantula", "nao_cobriu")}
        sens = {str(e): (res[e] == "ok").mean(0).round(3).tolist() for e in res}
        resumo[caso] = dict(
            especie=esp, anos=[anos[0], anos[-1]], n_anos=len(anos), datas=rotulos,
            p_todos=ok.mean(0).round(3).tolist(), p_treino=p_tr.round(3).tolist(), p_teste=p_te.round(3).tolist(),
            habitual=rotulos[di_hab], p_hab_teste=round(float(p_te[di_hab]), 3),
            melhor_treino=rotulos[di_best], p_melhor_teste=round(float(p_te[di_best]), 3),
            C1_ganho_pp=round(100 * float(p_te[di_best] - p_te[di_hab]), 1),
            dinamica_p_teste=round(float(np.mean(din)), 3), dinamica_falha=round(float(np.mean(din_falha)), 3),
            habitual_falha_teste=round(float(np.mean(hab_falha)), 3),
            C2_ganho_pp=round(100 * (float(np.mean(din)) - float(p_te[di_hab])), 1),
            dias_ate_cobrir_mediana=dias_ok, causas=causas, sensibilidade_gcob=sens,
        )
        print(caso, esp, f"anos {anos[0]}-{anos[-1]}", "habitual", rotulos[di_hab], "p_teste_hab", resumo[caso]["p_hab_teste"],
              "| melhor(treino)", rotulos[di_best], resumo[caso]["p_melhor_teste"], "C1", resumo[caso]["C1_ganho_pp"],
              "| dinâmica", resumo[caso]["dinamica_p_teste"], "C2", resumo[caso]["C2_ganho_pp"],
              "falha hab/din", resumo[caso]["habitual_falha_teste"], resumo[caso]["dinamica_falha"])
        print("   P(todos)", dict(zip(rotulos, resumo[caso]["p_todos"])))
    json.dump(resumo, open(OUT / "resultado_cobertura.json", "w"), ensure_ascii=False, indent=1)

if __name__ == "__main__":
    main()
