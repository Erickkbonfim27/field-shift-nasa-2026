#!/usr/bin/env python3
"""Gera os SVGs da sessão A2 a partir de resultados/*.json (sem matplotlib)."""
import json
from pathlib import Path
from html import escape

AQUI = Path(__file__).resolve().parent
R = lambda n: json.load(open(AQUI / "resultados" / n))
S1, S2, S3 = "#2a78d6", "#eb6834", "#1baf7a"
TXT, TXT2, GRADE, FUNDO = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb"
FONTE = "font-family='system-ui,-apple-system,Segoe UI,Roboto,sans-serif'"


def svg(w, h, corpo, titulo):
    return (f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 {w} {h}' width='{w}' height='{h}' {FONTE}>"
            f"<title>{escape(titulo)}</title><rect width='{w}' height='{h}' fill='{FUNDO}'/>{corpo}</svg>")


def texto(x, y, t, tam=12, cor=TXT2, anc="start", peso=400):
    return f"<text x='{x}' y='{y}' font-size='{tam}' fill='{cor}' text-anchor='{anc}' font-weight='{peso}'>{escape(t)}</text>"


def barra(x, y0, w, h, cor, dica):
    # topo arredondado de 4px, base reta na linha zero
    if h <= 0: return ""
    r = min(4, h, w / 2)
    d = f"M{x},{y0} V{y0 - h + r} Q{x},{y0 - h} {x + r},{y0 - h} H{x + w - r} Q{x + w},{y0 - h} {x + w},{y0 - h + r} V{y0} Z"
    return f"<path d='{d}' fill='{cor}'><title>{escape(dica)}</title></path>"


def eixo_y(x0, x1, y0, alt, maxv, passos, fmt):
    out = ""
    for v in passos:
        y = y0 - alt * v / maxv
        out += f"<line x1='{x0}' x2='{x1}' y1='{y}' y2='{y}' stroke='{GRADE}' stroke-width='1'/>"
        out += texto(x0 - 6, y + 4, fmt(v), 11, TXT2, "end")
    return out


def legenda(x, y, itens):
    out = ""
    for cor, nome, tipo in itens:
        if tipo == "barra": out += f"<rect x='{x}' y='{y - 9}' width='12' height='12' rx='2' fill='{cor}'/>"
        elif tipo == "ponto": out += f"<circle cx='{x + 6}' cy='{y - 3}' r='5' fill='{cor}'/>"
        else: out += f"<line x1='{x}' x2='{x + 16}' y1='{y - 3}' y2='{y - 3}' stroke='{cor}' stroke-width='2' stroke-dasharray='4 3'/>"
        out += texto(x + 20, y + 1, nome, 12, TXT)
        x += 28 + 7 * len(nome)
    return out


# ---------- A2-1 ----------
def g_a2_1():
    d = R("a2_1_smo.json")
    res = {(r["alvo"], r["fase"]): r for r in d["resultados"]}
    W, H, x0, y0, alt = 640, 360, 60, 290, 210
    c = texto(20, 28, "São Miguel do Oeste · chance de dez–jan seco (P−ET0 no tercil inferior), 1984–2024", 14, TXT, peso=600)
    c += texto(20, 48, "Fase do ENSO pelo ONI da NOAA (fonte externa, só para separar os anos). Linha tracejada: média de todos os anos.", 11)
    c += eixo_y(x0, W - 20, y0, alt, 0.8, [0, 0.2, 0.4, 0.6, 0.8], lambda v: f"{v:.0%}".replace("%", " %"))
    grupos = [("nina", "La Niña"), ("neutro", "Neutro"), ("nino", "El Niño")]
    gw = (W - 20 - x0) / 3
    for i, (f, nome) in enumerate(grupos):
        cx = x0 + gw * i + gw / 2
        for j, (fase, cor, rot) in enumerate([("fase_ndj", S1, "ONI de NDJ (na própria safra)"), ("fase_jas", S2, "ONI de JAS (sabido antes do plantio)")]):
            pf = res[("bh_dj", fase)]["por_fase"][f]
            h = alt * pf["p"] / 0.8
            bx = cx - 44 + j * 46
            c += barra(bx, y0, 42, h, cor, f"{nome}, {rot}: {pf['ruins']} de {pf['n']} anos secos ({pf['p']:.0%})")
            c += texto(bx + 21, y0 - h - 6, f"{pf['ruins']}/{pf['n']}", 11, TXT, "middle")
        c += texto(cx, y0 + 20, nome, 12, TXT, "middle")
    base = res[("bh_dj", "fase_ndj")]["base"]
    yb = y0 - alt * base / 0.8
    c += f"<line x1='{x0}' x2='{W - 20}' y1='{yb}' y2='{yb}' stroke='{TXT2}' stroke-width='2' stroke-dasharray='5 4'/>"
    c += texto(W - 22, yb - 6, f"todos os anos: {base:.0%}", 11, TXT2, "end")
    c += legenda(x0, H - 22, [(S1, "ONI de NDJ (na própria safra)", "barra"), (S2, "ONI de JAS (antes do plantio)", "barra")])
    (AQUI / "a2_1_fases_enso.svg").write_text(svg(W, H, c, "A2-1 chance de dez-jan seco por fase do ENSO"))


# ---------- A2-2 ----------
def g_a2_2():
    anos = R("a2_1_smo.json")["anos"]
    ib = R("a2_2_smo.json")["ibge"]["gwr_nov"]["anos_quebra"]  # anos de colheita
    W, H = 760, 400
    c = texto(20, 28, "São Miguel do Oeste · umidade do solo de novembro (GWETROOT, POWER/MERRA-2) contra dez–jan", 14, TXT, peso=600)
    c += texto(20, 46, "Cada ponto é uma safra. Laranja: quebra de milho no IBGE (rendimento < 80% do normal) na colheita seguinte.", 11)

    def painel(px, ytit, chave, ymin, ymax, rho, fmt):
        out = ""; x0, x1, y0, y1 = px + 50, px + 350, 340, 100
        xmin, xmax = 0.60, 0.92
        X = lambda v: x0 + (x1 - x0) * (v - xmin) / (xmax - xmin)
        Y = lambda v: y0 - (y0 - y1) * (v - ymin) / (ymax - ymin)
        for k in range(5):
            v = ymin + (ymax - ymin) * k / 4
            out += f"<line x1='{x0}' x2='{x1}' y1='{Y(v)}' y2='{Y(v)}' stroke='{GRADE}'/>" + texto(x0 - 6, Y(v) + 4, fmt(v), 10, TXT2, "end")
        for v in (0.65, 0.75, 0.85):
            out += texto(X(v), y0 + 16, f"{v:.2f}", 10, TXT2, "middle")
        out += texto((x0 + x1) / 2, y0 + 34, "GWETROOT médio de novembro", 11, TXT2, "middle")
        out += texto(x0, y1 - 26, ytit, 12, TXT, peso=600)
        out += texto(x0, y1 - 10, f"correlação de Spearman ρ = {rho:+.2f}".replace(".", ","), 11, TXT2)
        for a in anos:
            if a[chave] is None: continue
            q = (a["Y"] + 1) in ib
            out += (f"<circle cx='{X(a['gwr_nov']):.1f}' cy='{Y(a[chave]):.1f}' r='{6 if q else 4.5}' fill='{S2 if q else S1}' stroke='{FUNDO}' stroke-width='2'>"
                    f"<title>Safra {a['Y']}/{str(a['Y'] + 1)[2:]}: GWETROOT nov {a['gwr_nov']:.2f}; {ytit} {a[chave]:.2f}</title></circle>")
        return out
    r2 = R("a2_2_smo.json")["resultados"]
    rho = {x["alvo"]: x["spearman"][0] for x in r2 if x["pred"] == "gwr_nov"}
    c += painel(0, "GWETROOT de dez–jan (solo do modelo)", "gwr_dj", 0.60, 0.90, rho["gwr_dj"], lambda v: f"{v:.2f}")
    c += painel(380, "Balanço P−ET0 de dez–jan (mm)", "bh_dj", -250, 350, rho["bh_dj"], lambda v: f"{v:.0f}")
    c += legenda(60, H - 4, [(S1, "safra sem quebra no IBGE", "ponto"), (S2, "safra com quebra no IBGE", "ponto")])
    (AQUI / "a2_2_umidade_novembro.svg").write_text(svg(W, H + 4, c, "A2-2 umidade de novembro contra dez-jan"))


# ---------- A2-3 ----------
def g_a2_3():
    d = R("a2_3_smo.json")
    t = {x["alvo"]: x for x in d["testes"]}["bh_on"]
    W, H, x0, y0, alt = 640, 340, 60, 270, 190
    c = texto(20, 28, "São Miguel do Oeste · primavera seca (P−ET0 out–nov no tercil inferior), 1984–2024", 14, TXT, peso=600)
    c += texto(20, 48, "Fase pelo ONI de JAS (NOAA, sabido no fim de agosto). Linha tracejada: média de todos os anos.", 11)
    c += eixo_y(x0, W - 20, y0, alt, 0.6, [0, 0.2, 0.4, 0.6], lambda v: f"{v:.0%}".replace("%", " %"))
    gw = (W - 20 - x0) / 3
    for i, (f, nome) in enumerate([("nina", "La Niña"), ("neutro", "Neutro"), ("nino", "El Niño")]):
        pf = t["por_fase"][f]; cx = x0 + gw * i + gw / 2; h = alt * pf["p"] / 0.6
        c += barra(cx - 24, y0, 48, h, S1, f"{nome}: {pf['secos']} de {pf['n']} primaveras secas ({pf['p']:.0%})")
        c += texto(cx, y0 - h - 6, f"{pf['secos']}/{pf['n']}", 11, TXT, "middle") + texto(cx, y0 + 20, nome, 12, TXT, "middle")
    yb = y0 - alt * t["base"] / 0.6
    c += f"<line x1='{x0}' x2='{W - 20}' y1='{yb}' y2='{yb}' stroke='{TXT2}' stroke-width='2' stroke-dasharray='5 4'/>"
    c += texto(W - 22, yb - 6, f"todos os anos: {t['base']:.0%}", 11, TXT2, "end")
    (AQUI / "a2_3_primavera_enso.svg").write_text(svg(W, H, c, "A2-3 primavera seca por fase do ENSO"))


# ---------- A2-4 ----------
def g_a2_4():
    d = R("a2_4.json")
    cel = [("chapeco_xanxere", "Chapecó/Xanxerê"), ("concordia", "Concórdia"), ("itapiranga", "Itapiranga"), ("palmitos", "Palmitos")]
    W, H = 760, 380
    c = texto(20, 28, "Oeste de SC, 4 células novas do POWER · chuva de out–jan, safras 1981/82–2024/25", 14, TXT, peso=600)
    c += texto(20, 48, "El Niño = ONI de JAS ≥ +0,5 (NOAA, só para separar os anos; 9 safras). Tracejado: 1 em 3 (tercil).", 11)

    def painel(px, tit, k_n, k_o):
        out = ""; x0, x1, y0, alt = px + 50, px + 360, 300, 200
        out += texto(x0, 84, tit, 12, TXT, peso=600)
        out += eixo_y(x0, x1, y0, alt, 1.0, [0, 0.25, 0.5, 0.75, 1.0], lambda v: f"{v:.0%}".replace("%", " %"))
        gw = (x1 - x0) / 4
        for i, (k, nome) in enumerate(cel):
            r = d["celulas"][k]; cx = x0 + gw * i + gw / 2
            for j, (chave, cor, rot) in enumerate([(k_n, S2, "El Niño"), (k_o, S1, "outros anos")]):
                h = alt * r[chave]; bx = cx - 30 + j * 32
                out += barra(bx, y0, 28, h, cor, f"{nome}, {rot}: {r[chave]:.0%}")
                out += texto(bx + 14, y0 - h - 5, f"{r[chave]:.0%}".replace("%", ""), 10, TXT, "middle")
            out += texto(cx, y0 + 16, nome, 10, TXT2, "middle")
        yb = y0 - alt / 3
        out += f"<line x1='{x0}' x2='{x1}' y1='{yb}' y2='{yb}' stroke='{TXT2}' stroke-width='2' stroke-dasharray='5 4'/>"
        return out
    c += painel(0, "Chance de out–jan SECO (tercil inferior), %", "p_seco_nino", "p_seco_outros")
    c += painel(380, "Chance de out–jan CHUVOSO (tercil superior), %", "p_chuv_nino", "p_chuv_outros")
    c += legenda(60, H - 20, [(S2, "safras de El Niño", "barra"), (S1, "outras safras", "barra"), (TXT2, "1 em 3", "linha")])
    (AQUI / "a2_4_el_nino_tipo_de_risco.svg").write_text(svg(W, H, c, "A2-4 El Niño muda o tipo de risco"))


for g in (g_a2_1, g_a2_2, g_a2_3, g_a2_4): g()
print("ok")
