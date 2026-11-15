#!/usr/bin/env python3
"""V2 · Camada de geada (B1-1) refeita: 4 pontos do Oeste de SC, limiares 2/3/4 C, conferencia externa.

Entrada: NASA POWER diario 1981-2025 (T2M_MIN, T2M_MAX). Saida: v2_resultado.json + SVGs.
Rodar: python3 -I v2_geada.py
"""
import json, math, datetime as dt, statistics as st
from pathlib import Path

AQUI = Path(__file__).resolve().parent
LOOP = AQUI.parents[2] / "loop-validacao"
ARQ = {
    "SMO (São Miguel do Oeste)": LOOP / "dados" / "power_sao_miguel_do_oeste.json",
    "Chapecó": AQUI / "dados" / "power_chapeco.json",
    "Concórdia": AQUI / "dados" / "power_concordia.json",
}
CHECK_DIONISIO = AQUI / "dados" / "power_dionisio_cerqueira.json"
ANOS = list(range(1981, 2026))
LIMIARES = [2.0, 3.0, 4.0]
GDD_PADRAO = 1250
DECENDIOS = [(1, 1), (1, 11), (1, 21), (2, 1), (2, 11), (2, 21), (3, 1), (3, 11), (3, 21)]


def carregar(p):
    d = json.load(open(p))
    P = d["properties"]["parameter"]
    coords = d["geometry"]["coordinates"]
    tmin = {k: v for k, v in P["T2M_MIN"].items() if v != -999}
    tmax = {k: v for k, v in P["T2M_MAX"].items() if v != -999}
    return dict(tmin=tmin, tmax=tmax, lon=coords[0], lat=coords[1], alt=coords[2] if len(coords) > 2 else None)


def key(d):
    return d.strftime("%Y%m%d")


def gdd_dia(pt, k):
    tx = min(pt["tmax"][k], 30.0)
    tn = max(pt["tmin"][k], 10.0)
    return max(0.0, (tx + tn) / 2 - 10.0)


def safra(pt, ano, mes, dia, gdd_alvo=GDD_PADRAO):
    """Devolve (data_silagem, {limiar: primeira data com geada entre plantio e silagem})."""
    d0 = dt.date(ano, mes, dia)
    d = d0
    soma = 0.0
    prim = {L: None for L in LIMIARES}
    while soma < gdd_alvo:
        k = key(d)
        if k not in pt["tmin"] or d > dt.date(ano, 9, 30):
            return None
        for L in LIMIARES:
            if prim[L] is None and pt["tmin"][k] <= L:
                prim[L] = d
        soma += gdd_dia(pt, k)
        d += dt.timedelta(1)
    return dict(silagem=d, dias=(d - d0).days, prim=prim)


def wilson(k, n, z=1.96):
    p = k / n
    den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return max(0, c - h), min(1, c + h)


def curva(pt, datas, gdd=GDD_PADRAO, anos=ANOS):
    out = {}
    for (m, dia) in datas:
        rs = [safra(pt, a, m, dia, gdd) for a in anos]
        rs = [r for r in rs if r]
        n = len(rs)
        row = dict(n=n, dias_med=round(st.median([r["dias"] for r in rs])))
        for L in LIMIARES:
            k = sum(1 for r in rs if r["prim"][L])
            lo, hi = wilson(k, n)
            row[f"L{L:g}"] = dict(k=k, em10=round(10 * k / n, 1), ic_lo=round(10 * lo, 1), ic_hi=round(10 * hi, 1))
        out[f"{dia:02d}/{m:02d}"] = row
    return out


def limite_diario(pt, L, gdd=GDD_PADRAO, anos=ANOS, corte=0.2):
    """Plantio diario de 1/jan a 31/mar. Data-limite = dia anterior ao primeiro dia em que o risco passa de `corte`
    (media movel de 5 dias do risco para tirar o ruido de n=45)."""
    dias = []
    d = dt.date(2001, 1, 1)  # ano sem importancia, so para o calendario (2001 nao e bissexto)
    while d <= dt.date(2001, 3, 31):
        dias.append(d)
        d += dt.timedelta(1)
    risco = []
    for dd in dias:
        rs = [safra(pt, a, dd.month, dd.day, gdd) for a in anos]
        rs = [r for r in rs if r]
        risco.append(sum(1 for r in rs if r["prim"][L]) / len(rs))
    sm = []
    for i in range(len(risco)):
        j0, j1 = max(0, i - 2), min(len(risco), i + 3)
        sm.append(sum(risco[j0:j1]) / (j1 - j0))
    lim = None
    for dd, r in zip(dias, sm):
        if r > corte:
            lim = dd - dt.timedelta(1)
            break
    return dict(limite=lim.strftime("%d/%m") if lim else ">31/03", doy=(lim - dt.date(2001, 1, 1)).days + 1 if lim else None,
                risco_diario=[round(x, 3) for x in sm], dias=[x.strftime("%d/%m") for x in dias])


def primeira_geada(pt, L):
    out = []
    for a in ANOS:
        d = dt.date(a, 3, 1)
        achou = None
        while d <= dt.date(a, 9, 30):
            if pt["tmin"].get(key(d), 99) <= L:
                achou = d
                break
            d += dt.timedelta(1)
        out.append(achou.timetuple().tm_yday if achou else None)
    v = sorted(x for x in out if x)

    def f(s):
        return (dt.date(2001, 1, 1) + dt.timedelta(s - 1)).strftime("%d/%m")

    return dict(p10=f(v[len(v) // 10]), mediana=f(v[len(v) // 2]), p90=f(v[9 * len(v) // 10]), anos_sem=len(ANOS) - len(v))


# ---------------- carregar ----------------
PT = {n: carregar(p) for n, p in ARQ.items()}
res = dict(pontos={n: dict(lat=p["lat"], lon=p["lon"], alt_grade=p["alt"]) for n, p in PT.items()})

# celulas iguais? (SMO x Dionisio)
PT_CHECK = dict(PT); PT_CHECK["Dionísio Cerqueira"] = carregar(CHECK_DIONISIO)
cel = {}
nomes = list(PT_CHECK)
for i in range(len(nomes)):
    for j in range(i + 1, len(nomes)):
        a, b = PT_CHECK[nomes[i]], PT_CHECK[nomes[j]]
        ks = sorted(set(a["tmin"]) & set(b["tmin"]))
        difs = sum(1 for k in ks if abs(a["tmin"][k] - b["tmin"][k]) > 0.005)
        cel[f"{nomes[i]} x {nomes[j]}"] = dict(dias_diferentes=difs, de=len(ks))
res["celulas_iguais"] = cel

# ---------------- 1. tabelas por decendio ----------------
res["tabela_decendio"] = {n: curva(p, DECENDIOS) for n, p in PT.items()}

# sensibilidade ao ciclo (gdd) em SMO
smo = PT["SMO (São Miguel do Oeste)"]
res["sens_gdd_smo"] = {str(g): curva(smo, DECENDIOS, g) for g in (1100, 1250, 1400)}

# metade do periodo (tendencia) em SMO e Chapecó
res["tendencia"] = {}
for n in ("SMO (São Miguel do Oeste)", "Chapecó"):
    res["tendencia"][n] = dict(a1981_2002=curva(PT[n], DECENDIOS, anos=list(range(1981, 2003))),
                               a2003_2025=curva(PT[n], DECENDIOS, anos=list(range(2003, 2026))))

# ---------------- 2. data-limite diaria ----------------
res["limite"] = {}
serie = {}
for n, p in PT.items():
    res["limite"][n] = {}
    for L in LIMIARES:
        r = limite_diario(p, L)
        res["limite"][n][f"L{L:g}"] = dict(limite=r["limite"], doy=r["doy"])
        serie[(n, L)] = r
# sensibilidade do limite ao GDD em SMO (3 C)
res["limite_gdd_smo_L3"] = {str(g): limite_diario(smo, 3.0, gdd=g)["limite"] for g in (1100, 1250, 1400)}

res["risco_28fev"] = {n: curva(p, [(2, 28)])["28/02"] for n, p in PT.items()}

# ---------------- 3. 1a geada do outono ----------------
res["primeira_geada"] = {n: {f"L{L:g}": primeira_geada(p, L) for L in LIMIARES} for n, p in PT.items()}

# dias por ano com T2M_MIN <= L (mai-ago)
res["dias_ano"] = {}
for n, p in PT.items():
    res["dias_ano"][n] = {f"L{L:g}": round(sum(1 for k, v in p["tmin"].items() if v <= L) / len(ANOS), 1) for L in LIMIARES}

# ---------------- 4. eventos ----------------
# status: E = estacao (INMET/Epagri) com data e local; R = regional confirmado (Serra/estado), Oeste nao; N = nao confirmado / data diferente
EVENTOS = [
    # (data, ponto principal, descricao, status, fonte)
    ("1981-06-19", "Chapecó", "mínima absoluta de junho 1961-90 na estação INMET de Chapecó: -2,8 °C (19/06/1981)", "E", "Embrapa Clima Temperado, tabela INMET 1961-90 (temp_min_absoluta_1_6_SC.pdf)"),
    ("1988-05-31", "Chapecó", "mínima absoluta de maio 1961-90 na estação INMET de Chapecó: -0,6 °C (31/05/1988)", "E", "mesma tabela"),
    ("2000-07-14", "Chapecó", "Chapecó -4,5 °C em 14/07/2000 (recorde, Epagri/Ciram)", "E*", "trecho de busca atribuído ao NSC Total/Epagri; página devolveu 403, não aberta"),
    ("2000-07-14", "SMO (São Miguel do Oeste)", "São Miguel do Oeste -3 °C em 14/07/2000 (Epagri/Ciram)", "E*", "mesmo trecho de busca, não aberto"),
    ("2009-08-15", "SMO (São Miguel do Oeste)", "São Miguel do Oeste -3 °C em 15/08/2009 (Epagri/Ciram)", "E*", "mesmo trecho de busca, não aberto"),
    # lista da memoria do B1-1
    ("1994-06-26", "SMO (São Miguel do Oeste)", "jun/1994 (lista do B1-1)", "N", "só achei geada de jun/1994 no Sudeste (café); Sul não confirmado"),
    ("2000-07-17", "SMO (São Miguel do Oeste)", "jul/2000 (data 17/07 do B1-1)", "N", "o dado datado é 14/07; frio de jul/2000 confirmado (Embrapa: mês mais frio da série), mas a data 17/07 não"),
    ("2013-07-24", "SMO (São Miguel do Oeste)", "jul/2013 (neve em SC)", "R", "Epagri/Ciram: neve 22 a 25/07/2013; INMET Major Vieira -4,1 °C em 24/07; Oeste não citado"),
    ("2021-06-30", "SMO (São Miguel do Oeste)", "jun/2021", "R", "Epagri/Ciram: 3 dias seguidos de neve até 30/06/2021; Oeste não citado"),
    ("2021-07-29", "SMO (São Miguel do Oeste)", "jul/2021", "R", "Climatempo/INMET: -8,6 °C em Bom Jardim da Serra em 29/07/2021; Oeste não citado"),
    ("2022-05-19", "SMO (São Miguel do Oeste)", "mai/2022", "R", "Epagri/Ciram: neve 17/05 e -5,1 °C em Urupema em 20/05/2022; Oeste não citado"),
    ("2025-06-25", "SMO (São Miguel do Oeste)", "jun/2025 (evento novo)", "R", "Epagri/Ciram: 49 municípios negativos em 25/06/2025; frio mais forte na Serra e Meio-Oeste"),
]


def janela_min(pt, data, meia=2):
    d0 = dt.date.fromisoformat(data)
    v = [pt["tmin"].get(key(d0 + dt.timedelta(i))) for i in range(-meia, meia + 1)]
    v = [x for x in v if x is not None]
    return min(v) if v else None


ev_out = []
for data, ponto, desc, status, fonte in EVENTOS:
    row = dict(data=data, ponto=ponto, desc=desc, status=status, fonte=fonte, tmin_pontos={})
    for n, p in PT.items():
        row["tmin_pontos"][n] = round(janela_min(p, data), 1)
    ev_out.append(row)
res["eventos"] = ev_out

# eventos E/E*: marcacao no ponto proprio, janelas +-2 d
tab = {}
for L in LIMIARES:
    ok = tot = 0
    for e in ev_out:
        if e["status"] in ("E", "E*"):
            tot += 1
            ok += e["tmin_pontos"][e["ponto"]] <= L
    tab[f"L{L:g}"] = dict(ok=ok, de=tot)
res["marcacao_eventos_estacao"] = tab
# so os "E" (tabela aberta)
tabE = {}
for L in LIMIARES:
    ev = [e for e in ev_out if e["status"] == "E"]
    tabE[f"L{L:g}"] = dict(ok=sum(1 for e in ev if e["tmin_pontos"][e["ponto"]] <= L), de=len(ev))
res["marcacao_eventos_E"] = tabE
# regionais e nao confirmados: em quantos dos 4 pontos marca (qualquer ponto)
reg = {}
for L in LIMIARES:
    reg[f"L{L:g}"] = {e["data"] + " " + e["status"]: sum(1 for n in PT if e["tmin_pontos"][n] <= L) for e in ev_out if e["status"] in ("R", "N")}
res["marcacao_eventos_regionais_pontos_de_4"] = reg

# taxa de acerto ao acaso: P(min de 5 dias <= L) nos meses do evento, SMO e Chapecó
def acaso(pt, mes, L):
    ks = sorted(k for k in pt["tmin"] if int(k[4:6]) == mes)
    v = [pt["tmin"][k] for k in ks]
    hits = sum(1 for i in range(len(v) - 4) if min(v[i:i + 5]) <= L)
    return round(hits / (len(v) - 4), 3)


res["acaso_5dias"] = {n: {str(m): {f"L{L:g}": acaso(PT[n], m, L) for L in LIMIARES} for m in (5, 6, 7, 8)} for n in ("SMO (São Miguel do Oeste)", "Chapecó")}

# ---------------- 5. vies do POWER vs normal INMET Chapecó 1961-90 ----------------
NORMAL_CHAPECO = {3: 17.4, 4: 14.6, 5: 11.8, 6: 9.9, 7: 10.3, 8: 11.5, 9: 12.1, 10: 14.3}  # Embrapa/INMET temp_minima_SC.pdf
vies = {}
ch = PT["Chapecó"]
for m, norm in NORMAL_CHAPECO.items():
    v = [x for k, x in ch["tmin"].items() if int(k[4:6]) == m]
    v1 = [x for k, x in ch["tmin"].items() if int(k[4:6]) == m and 1981 <= int(k[:4]) <= 1990]
    vies[str(m)] = dict(power_1981_2025=round(st.mean(v), 1), power_1981_1990=round(st.mean(v1), 1), normal_inmet_1961_90=norm,
                        vies_81_25=round(st.mean(v) - norm, 1), vies_81_90=round(st.mean(v1) - norm, 1))
res["vies_chapeco"] = vies
# minimas absolutas mensais 1981-1990 POWER vs estacao
minabs = {}
for m, (est, dtx) in {5: (-0.6, "31/05/1988"), 6: (-2.8, "19/06/1981")}.items():
    v = [x for k, x in ch["tmin"].items() if int(k[4:6]) == m and 1981 <= int(k[:4]) <= 1990]
    minabs[str(m)] = dict(power_min_1981_90=round(min(v), 1), estacao=est, data_estacao=dtx)
res["minima_absoluta_1981_90_chapeco"] = minabs

res["janela_2009_smo"] = {k: smo["tmin"][k] for k in sorted(smo["tmin"]) if "20090805" <= k <= "20090825"}
json.dump(res, open(AQUI / "v2_resultado.json", "w"), ensure_ascii=False, indent=1)

# ---------------- ZARC (A1/ext) ----------------
import csv
zarc = {}
rows = list(csv.DictReader(open(LOOP / "sessoes" / "A1" / "ext" / "zarc_2627_smo_itu.csv", encoding="utf-8-sig"), delimiter=";"))
DECNOME = []
for m in range(1, 13):
    for dd in ("01", "11", "21"):
        DECNOME.append(f"{dd}/{m:02d}")
for cultura in ("Sorgo Forrageiro 2ª Safra", "Sorgo Granífero 2ª Safra", "Feijão 2ª Safra", "Milho 1ª Safra"):
    for r in rows:
        if r["municipio"] == "São Miguel do Oeste" and r["Nome_cultura"] == cultura and r["Cod_Outros_Manejos"] == "1":
            ok = [i for i in range(1, 37) if int(r[f"dec{i}"]) in (20,)]  # risco 20%
            pos = [i for i in range(1, 37) if int(r[f"dec{i}"]) > 0]
            chave = f"{cultura} | ciclo {r['Cod_Ciclo']} | solo {r['Cod_Solo']}"
            zarc[chave] = dict(risco20=[DECNOME[i - 1] for i in ok], qualquer_risco=[DECNOME[i - 1] for i in pos], portaria=r["Portaria"])
res["zarc_smo"] = zarc
json.dump(res, open(AQUI / "v2_resultado.json", "w"), ensure_ascii=False, indent=1)

# ---------------- SVGs ----------------
CORES = {2.0: "#2a7de1", 3.0: "#111111", 4.0: "#d9480f"}
CORES_PT = ["#111111", "#2a7de1", "#d9480f"]
W, H, ML, MR, MT, MB = 760, 420, 56, 20, 40, 56


def svg_linhas(titulo, series, xdias, arquivo, faixas=None, sub=""):
    """series: lista (rotulo, cor, lista de y 0..1, tracejado)."""
    n = len(xdias)
    def X(i): return ML + (W - ML - MR) * i / (n - 1)
    def Y(v): return MT + (H - MT - MB) * (1 - v)
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" font-family="Helvetica,Arial,sans-serif" font-size="12">',
         f'<rect width="{W}" height="{H}" fill="#ffffff"/>',
         f'<text x="{ML}" y="22" font-size="15" font-weight="bold">{titulo}</text>',
         f'<text x="{ML}" y="36" fill="#555">{sub}</text>']
    for v in (0, .2, .4, .6, .8, 1):
        s.append(f'<line x1="{ML}" x2="{W-MR}" y1="{Y(v):.1f}" y2="{Y(v):.1f}" stroke="{"#c92a2a" if v==.2 else "#ddd"}" stroke-dasharray="{"4 3" if v==.2 else "0"}"/>')
        s.append(f'<text x="{ML-6}" y="{Y(v)+4:.1f}" text-anchor="end">{int(v*10)}</text>')
    s.append(f'<text x="14" y="{MT+(H-MT-MB)/2:.0f}" transform="rotate(-90 14 {MT+(H-MT-MB)/2:.0f})" text-anchor="middle">anos em 10 com geada antes da silagem</text>')
    for i, dstr in enumerate(xdias):
        if dstr in ("01/01", "15/01", "01/02", "15/02", "01/03", "15/03", "31/03"):
            s.append(f'<line x1="{X(i):.1f}" x2="{X(i):.1f}" y1="{H-MB}" y2="{H-MB+4}" stroke="#555"/>')
            s.append(f'<text x="{X(i):.1f}" y="{H-MB+17}" text-anchor="middle">{dstr}</text>')
    if faixas:
        for (a, b, cor, rot, lin) in faixas:
            ia, ib = xdias.index(a), xdias.index(b)
            y0 = H - MB - 8 - 10 * lin
            s.append(f'<rect x="{X(ia):.1f}" y="{y0}" width="{X(ib)-X(ia):.1f}" height="7" fill="{cor}" opacity="0.8"/>')
            s.append(f'<text x="{X(ib)+4:.1f}" y="{y0+7}" font-size="10" fill="#333">{rot}</text>')
    for rot, cor, ys, trac in series:
        pts = " ".join(f"{X(i):.1f},{Y(v):.1f}" for i, v in enumerate(ys))
        s.append(f'<polyline fill="none" stroke="{cor}" stroke-width="2.2" stroke-dasharray="{trac}" points="{pts}"/>')
    lx = ML + 10
    for j, (rot, cor, ys, trac) in enumerate(series):
        s.append(f'<line x1="{lx}" x2="{lx+22}" y1="{MT+12+16*j}" y2="{MT+12+16*j}" stroke="{cor}" stroke-width="2.2" stroke-dasharray="{trac}"/>')
        s.append(f'<text x="{lx+28}" y="{MT+16+16*j}">{rot}</text>')
    s.append(f'<text x="{ML}" y="{H-8}" fill="#555" font-size="11">Data de plantio. Linha vermelha tracejada = 2 em 10 (risco de 20%). Fonte: NASA POWER T2M_MIN, 1981-2025.</text>')
    s.append("</svg>")
    open(AQUI / arquivo, "w").write("\n".join(s))


smo_n = "SMO (São Miguel do Oeste)"
xd = serie[(smo_n, 3.0)]["dias"]
svg_linhas("SMO: risco de geada por limiar", [(f"T2M_MIN ≤ {L:g} °C", CORES[L], serie[(smo_n, L)]["risco_diario"], "0") for L in LIMIARES], xd,
           "v2_1_smo_limiares.svg", sub="Média móvel de 5 dias do plantio diário; silagem = 1.250 °C·dia",
           faixas=[("01/01", "20/02", "#2f9e44", "ZARC sorgo forrageiro 2ª safra, ciclo médio (até 20/02)", 0),
                   ("01/01", "10/03", "#94d82d", "ciclo curto (até 10/03)", 1), ("01/01", "31/01", "#0b7285", "ciclo longo (até 31/01)", 2)])
svg_linhas("Quatro pontos do Oeste de SC (limiar 3 °C)", [(n, CORES_PT[i], serie[(n, 3.0)]["risco_diario"], "0") for i, n in enumerate(PT)], xd,
           "v2_2_pontos.svg", sub="Média móvel de 5 dias do plantio diário; silagem = 1.250 °C·dia")

# SVG 3: barras de eventos
ev_plot = [e for e in ev_out]
Hh = 60 + 22 * len(ev_plot)
s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 760 {Hh}" font-family="Helvetica,Arial,sans-serif" font-size="12"><rect width="760" height="{Hh}" fill="#fff"/>',
     '<text x="20" y="22" font-size="15" font-weight="bold">Menor T2M_MIN do POWER em ±2 dias de cada evento</text>',
     '<text x="20" y="38" fill="#555">Barra = ponto citado. Linhas: 2, 3 e 4 °C. E = estação com data; R = só regional; N = não confirmado.</text>']
x0, esc = 330, 24  # px por grau
def XX(t): return x0 + (t + 6) * esc
for L in LIMIARES:
    s.append(f'<line x1="{XX(L):.0f}" x2="{XX(L):.0f}" y1="46" y2="{Hh-8}" stroke="{CORES[L]}" stroke-dasharray="4 3"/>')
    s.append(f'<text x="{XX(L):.0f}" y="{Hh-0}" font-size="10" fill="{CORES[L]}" text-anchor="middle">{L:g}</text>')
for i, e in enumerate(ev_plot):
    y = 56 + 22 * i
    t = e["tmin_pontos"][e["ponto"]]
    cor = "#2f9e44" if t <= 3 else "#c92a2a"
    s.append(f'<text x="20" y="{y+11}" font-size="11">{e["data"]} {e["status"]} · {e["ponto"].split(" (")[0]}</text>')
    s.append(f'<rect x="{XX(min(t,0)):.0f}" y="{y}" width="{abs(XX(t)-XX(0)):.0f}" height="14" fill="{cor}"/>')
    s.append(f'<text x="{XX(max(t,0))+5:.0f}" y="{y+11}" font-size="11">{t:.1f} °C</text>')
s.append("</svg>")
open(AQUI / "v2_3_eventos.svg", "w").write("\n".join(s))

# ---------------- impressao ----------------
print("celulas:", json.dumps(cel, ensure_ascii=False))
for n in PT:
    print("\n==", n, res["pontos"][n])
    for k, r in res["tabela_decendio"][n].items():
        print(k, r["dias_med"], "d |", " | ".join(f"{L}: {r[L]['em10']} [{r[L]['ic_lo']}-{r[L]['ic_hi']}]" for L in ("L2", "L3", "L4")))
    print("limite:", res["limite"][n])
    print("1a geada:", res["primeira_geada"][n]["L3"], "dias/ano:", res["dias_ano"][n])
print("\nlimite GDD SMO L3:", res["limite_gdd_smo_L3"])
print("\nEventos:")
for e in ev_out:
    print(e["data"], e["status"], e["ponto"][:10], e["tmin_pontos"])
print(res["marcacao_eventos_estacao"], res["marcacao_eventos_E"])
print(res["marcacao_eventos_regionais_pontos_de_4"])
print("acaso:", json.dumps(res["acaso_5dias"], ensure_ascii=False))
print("vies:", vies, minabs)
print("28/02:", json.dumps(res["risco_28fev"], ensure_ascii=False)); print("2009:", res["janela_2009_smo"]); print("tend:", json.dumps({n:{h:{d:v["L3"]["em10"] for d,v in t.items() if d in("01/02","11/02","21/02")} for h,t in x.items()} for n,x in res["tendencia"].items()}, ensure_ascii=False)); print("gdd:", json.dumps({g:{d:v["L3"]["em10"] for d,v in t.items()} for g,t in res["sens_gdd_smo"].items()}))
print("ZARC:")
for k, v in zarc.items():
    print(k, v["risco20"][:3], "...", v["risco20"][-3:] if v["risco20"] else "", v["portaria"])
