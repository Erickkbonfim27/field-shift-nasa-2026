#!/usr/bin/env python3
"""B5: balanço hídrico do milho de verão (FAO-56 + FAO-33) com NASA POWER.

Reaproveita a lógica de ../../../prototipo/modelo/risco.py (Quixadá), adaptada para SC.
Gera indicadores por safra para:
  - B5-1 (laudo de perda): rendimento relativo simulado, chuva out-fev, GWETROOT dez-jan.
  - B5-2 (alerta WhatsApp): alerta até o dia 80 após o plantio e a regra "olho do agricultor".
Saída: indicadores_<local>.csv
"""
import json, math, datetime as dt, csv, sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DADOS = AQUI.parent.parent / "dados"

LOCAIS = {
    "smo": dict(arq="power_sao_miguel_do_oeste.json", lat=-26.725, alt=533.0),
    "itu": dict(arq="power_ituporanga.json", lat=-27.414, alt=677.0),
}

# Milho de verão, ciclo ~130 dias (FAO-56 tab. 11, ajustado para ciclo médio do Sul)
FASES = (25, 35, 40, 30)          # inicial, desenvolvimento, floração/enchimento, maturação
KC = (0.30, 1.20, 0.50)
KY = (0.4, 0.4, 1.5, 0.5)          # FAO-33
P_DEPL = 0.55                      # FAO-56, milho
CAD_PADRAO = 125.0                 # mm (GAEZ "médio" 125 mm/m x 1,0 m de raiz)
PLANTIOS = [(9, 1), (9, 15), (10, 1), (10, 15)]   # espalhamento do plantio no município
PLANTIO_REF = (10, 1)              # agricultor de referência do alerta
DIA_DECISAO = 80                   # até aqui ainda dá para ensilar a planta inteira


def carregar(local):
    cfg = LOCAIS[local]
    P = json.load(open(DADOS / cfg["arq"]))["properties"]["parameter"]
    return cfg, P


def e_sat(t): return 0.6108 * math.exp(17.27 * t / (t + 237.3))


def et0_dia(P, k, lat, alt):
    d = dt.date(int(k[:4]), int(k[4:6]), int(k[6:]))
    tmax, tmin, tm = P["T2M_MAX"][k], P["T2M_MIN"][k], P["T2M"][k]
    rh, u2, rs = P["RH2M"][k], P["WS2M"][k], P["ALLSKY_SFC_SW_DWN"][k]
    if rs is None or rs < 0:
        return None
    es = (e_sat(tmax) + e_sat(tmin)) / 2
    ea = rh / 100 * e_sat(tm)
    delta = 4098 * e_sat(tm) / (tm + 237.3) ** 2
    pr = 101.3 * ((293 - 0.0065 * alt) / 293) ** 5.26
    gam = 0.000665 * pr
    j = d.timetuple().tm_yday
    phi = math.radians(lat)
    dr = 1 + 0.033 * math.cos(2 * math.pi * j / 365)
    dec = 0.409 * math.sin(2 * math.pi * j / 365 - 1.39)
    ws = math.acos(max(-1, min(1, -math.tan(phi) * math.tan(dec))))
    ra = 24 * 60 / math.pi * 0.082 * dr * (ws * math.sin(phi) * math.sin(dec) + math.cos(phi) * math.cos(dec) * math.sin(ws))
    rso = (0.75 + 2e-5 * alt) * ra
    rnl = 4.903e-9 * (((tmax + 273.16) ** 4 + (tmin + 273.16) ** 4) / 2) * (0.34 - 0.14 * math.sqrt(max(ea, 0.01))) * (1.35 * min(rs / rso, 1) - 0.35)
    rn = 0.77 * rs - rnl
    num = 0.408 * delta * rn + gam * 900 / (tm + 273) * u2 * (es - ea)
    return max(0.3, num / (delta + gam * (1 + 0.34 * u2)))


def kc_do_dia(k):
    ini, dev, mid, late = FASES
    if k < ini: return KC[0]
    if k < ini + dev: return KC[0] + (KC[1] - KC[0]) * (k - ini) / dev
    if k < ini + dev + mid: return KC[1]
    return KC[1] + (KC[2] - KC[1]) * (k - ini - dev - mid) / late


def fase_do_dia(k):
    acc = 0
    for i, n in enumerate(FASES):
        acc += n
        if k < acc: return i
    return 3


def key(d): return d.strftime("%Y%m%d")


def simular(P, ET0, plantio, cad):
    """Balde começa cheio 60 dias antes do plantio (inverno úmido no Sul) e roda até a colheita."""
    s = cad
    d = plantio - dt.timedelta(60)
    while d < plantio:   # pousio: evaporação do solo nu reduzida
        k = key(d)
        s = min(cad, s + max(0, P["PRECTOTCORR"][k]))
        s = max(0.0, s - 0.3 * ET0[k] * min(1.0, s / (0.5 * cad)))
        d += dt.timedelta(1)
    n = sum(FASES)
    eta_f, etc_f = [0.0] * 4, [0.0] * 4
    diario = []   # fração de água útil e chuva por dia (para o alerta)
    for i in range(n):
        k = key(plantio + dt.timedelta(i))
        etc = kc_do_dia(i) * ET0[k]
        chuva = max(0, P["PRECTOTCORR"][k])
        s = min(cad, s + chuva)
        ks = min(1.0, s / ((1 - P_DEPL) * cad))
        eta = etc * ks
        s = max(0.0, s - eta)
        f = fase_do_dia(i)
        eta_f[f] += eta; etc_f[f] += etc
        diario.append(dict(dia=i, frac=s / cad, ks=ks, chuva=chuva, gw=P["GWETROOT"][k]))
    isna = [a / b if b else 1 for a, b in zip(eta_f, etc_f)]
    y = 1.0
    for i in range(4):
        y *= max(0.0, 1 - KY[i] * (1 - isna[i]))
    return y, isna, diario


def alerta_modelo(diario):
    """Alerta B5-2: fração de água útil < 0,40 por 10 dias seguidos entre os dias 45 e DIA_DECISAO.
    Retorna (dia do 1º alerta ou None, nº de mensagens: 1 por episódio, novo episódio após 10 dias de recuperação)."""
    seq, primeiro, msgs, recup, em_ep = 0, None, 0, 99, False
    for x in diario[:DIA_DECISAO + 1]:
        if x["dia"] < 45:
            continue
        if x["frac"] < 0.40:
            seq += 1; recup = 0
            if seq >= 10 and not em_ep:
                em_ep = True; msgs += 1
                if primeiro is None: primeiro = x["dia"]
        else:
            seq = 0; recup += 1
            if recup >= 10: em_ep = False
    return primeiro, msgs


def alerta_olho(diario, limiar=5.0, dias=15):
    """Linha de base: 15 dias seguidos com chuva < 5 mm/dia entre o plantio e o dia 80."""
    seq = 0
    for x in diario[:DIA_DECISAO + 1]:
        seq = seq + 1 if x["chuva"] < limiar else 0
        if seq >= dias:
            return x["dia"]
    return None


def rodar(local, cad=CAD_PADRAO):
    cfg, P = carregar(local)
    ET0 = {}
    for k in P["PRECTOTCORR"]:
        if int(k[:4]) >= 1984:
            ET0[k] = et0_dia(P, k, cfg["lat"], cfg["alt"])
    linhas = []
    for safra in range(1985, 2026):   # safra = ano da colheita (mesma convenção do IBGE/PAM)
        a0 = safra - 1
        ys = []
        for m, d in PLANTIOS:
            y, isna, _ = simular(P, ET0, dt.date(a0, m, d), cad)
            ys.append(y)
        y_ref, isna_ref, diario = simular(P, ET0, dt.date(a0, *PLANTIO_REF), cad)
        dia_al, msgs = alerta_modelo(diario)
        dia_olho = alerta_olho(diario)
        chuva_of = sum(max(0, P["PRECTOTCORR"][key(dt.date(a0, 10, 1) + dt.timedelta(i))]) for i in range((dt.date(safra, 2, 28) - dt.date(a0, 10, 1)).days + 1))
        gw_dj = [P["GWETROOT"][key(dt.date(a0, 12, 1) + dt.timedelta(i))] for i in range(62)]
        linhas.append(dict(safra=safra, y_mun=round(sum(ys) / len(ys), 3), y_ref=round(y_ref, 3),
                           isna_flor=round(isna_ref[2], 3), chuva_out_fev=round(chuva_of, 1),
                           gwroot_dez_jan=round(sum(gw_dj) / len(gw_dj), 3),
                           alerta_dia=dia_al if dia_al is not None else "", alerta_msgs=msgs,
                           olho_dia=dia_olho if dia_olho is not None else ""))
    return linhas


if __name__ == "__main__":
    local = sys.argv[1] if len(sys.argv) > 1 else "smo"
    cad = float(sys.argv[2]) if len(sys.argv) > 2 else CAD_PADRAO
    L = rodar(local, cad)
    suf = "" if cad == CAD_PADRAO else f"_cad{int(cad)}"
    out = AQUI / f"indicadores_{local}{suf}.csv"
    with open(out, "w") as f:
        w = csv.DictWriter(f, fieldnames=list(L[0].keys())); w.writeheader(); w.writerows(L)
    for x in L: print(x)
    print("->", out)
