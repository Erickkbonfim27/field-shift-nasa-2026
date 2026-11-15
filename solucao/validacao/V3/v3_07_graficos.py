#!/usr/bin/env python3
"""V3-07: gráficos SVG (sem matplotlib nesta máquina). Lê os res_*.json."""
import sys, json
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
import modelo_v3 as V
AQUI = Path(__file__).resolve().parent
J = lambda n: json.load(open(AQUI / n))
C = {"A4": "#eb6834", "FAO33": "#2a78d6", "MISTO": "#1baf7a", "BIOMASSA": "#8a6fd1"}
NOME = {"A4": "Ky da A4 (por fase)", "FAO33": "Ky FAO-33 por estágio (central)", "MISTO": "Ky misto grão + biomassa (pós-teste)", "BIOMASSA": "Ky = 1 nos dois (biomassa)"}
TXT, TXT2, GRID, BG = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb"
F = 'font-family="Helvetica, Arial, sans-serif"'


def svg(w, h, body):
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}"><rect width="{w}" height="{h}" fill="{BG}"/>{body}</svg>'


def t(x, y, s, size=12, color=TXT2, anchor="start", weight="normal"):
    if anchor == "start" and len(s) > 125 and size <= 12:
        palavras, linhas, atual = s.split(" "), [], ""
        for pw in palavras:
            if len(atual) + len(pw) + 1 > 125: linhas.append(atual); atual = pw
            else: atual = (atual + " " + pw).strip()
        linhas.append(atual)
        return "".join(t(x, y + 14 * i, l, size, color, anchor, weight) for i, l in enumerate(linhas))
    return f'<text x="{x}" y="{y}" {F} font-size="{size}" fill="{color}" text-anchor="{anchor}" font-weight="{weight}">{s}</text>'


def fmt(v, d=0): return f"{v:.{d}f}".replace(".", ",")


class Eixo:
    def __init__(s, x0, y0, w, h, xmin, xmax, ymin, ymax):
        s.x0, s.y0, s.w, s.h, s.xmin, s.xmax, s.ymin, s.ymax = x0, y0, w, h, xmin, xmax, ymin, ymax
    def X(s, v): return s.x0 + s.w * (v - s.xmin) / (s.xmax - s.xmin)
    def Y(s, v): return s.y0 + s.h * (1 - (v - s.ymin) / (s.ymax - s.ymin))
    def grade(s, yt, xt, ylab=lambda v: fmt(v), xlab=lambda v: fmt(v)):
        b = ""
        for v in yt:
            b += f'<line x1="{s.x0}" x2="{s.x0+s.w}" y1="{s.Y(v)}" y2="{s.Y(v)}" stroke="{GRID}"/>' + t(s.x0 - 8, s.Y(v) + 4, ylab(v), 11, anchor="end")
        for v in xt:
            b += t(s.X(v), s.y0 + s.h + 18, xlab(v), 11, anchor="middle")
        return b


# ---------- Fig 1: ganho de P10 e variação da média vs CAD ----------
def fig1():
    r = J("res_02_central_grade.json")["curva_cad"]
    W, H = 980, 490
    b = t(40, 26, "Metade da silagem em sorgo: quanto sobe o pior ano em 10, conforme a água que o solo guarda", 15, TXT, weight="bold")
    b += t(40, 46, "Silagem total = 50% milho + 50% × 0,88 × sorgo, plantio de 11/set a 21/out, 41 safras (SMO, NASA POWER). CAD = água disponível na zona de raiz.", 12)
    for k, (campo, tit, lim, ymin, ymax, yt) in enumerate([("ganho_p10", "Mudança do pior ano em 10 (P10), %", 10, -10, 70, range(-10, 71, 10)), ("var_media", "Mudança da média, %", -3, -10, 16, range(-10, 17, 4))]):
        ax = Eixo(70 + k * 480, 90, 380, 270, 20, 180, ymin, ymax)
        b += t(ax.x0, 78, tit, 12, TXT, weight="bold")
        b += ax.grade(yt, (24, 42, 66, 87.5, 125, 175))
        b += f'<line x1="{ax.x0}" x2="{ax.x0+ax.w}" y1="{ax.Y(0)}" y2="{ax.Y(0)}" stroke="{TXT2}" stroke-width="1"/>'
        b += f'<line x1="{ax.x0}" x2="{ax.x0+ax.w}" y1="{ax.Y(lim)}" y2="{ax.Y(lim)}" stroke="{TXT}" stroke-dasharray="5 4"/>' + t(ax.x0 + ax.w - 4, ax.Y(lim) - 5, ("critério: ≥ +10%" if k == 0 else "critério: ≥ −3%"), 11, TXT, anchor="end")
        for cadm, rot in ((42, "raso ZARC"), (87.5, "raso A4")):
            b += f'<line x1="{ax.X(cadm)}" x2="{ax.X(cadm)}" y1="{ax.y0}" y2="{ax.y0+ax.h}" stroke="{TXT2}" stroke-width="0.8" stroke-dasharray="2 3"/>' + t(ax.X(cadm) + 3, ax.y0 + 12, rot, 10)
        for scen in ("A4", "FAO33", "MISTO", "BIOMASSA"):
            pts = [(p["cad"], p[campo]) for p in r[scen]]
            b += f'<polyline points="{" ".join(f"{ax.X(x):.1f},{ax.Y(min(max(y, ymin), ymax)):.1f}" for x, y in pts)}" fill="none" stroke="{C[scen]}" stroke-width="2.2"/>'
            for x, y in pts:
                b += f'<circle cx="{ax.X(x):.1f}" cy="{ax.Y(min(max(y, ymin), ymax)):.1f}" r="3.2" fill="{C[scen]}"><title>{NOME[scen]}, CAD {x} mm: {y:+.1f}%</title></circle>'
        b += t(ax.x0 + ax.w / 2, ax.y0 + ax.h + 38, "CAD (mm)", 11, anchor="middle")
    for i, scen in enumerate(("A4", "FAO33", "MISTO", "BIOMASSA")):
        x = 70 + (i % 2) * 450; y = 410 + (i // 2) * 18
        b += f'<line x1="{x}" x2="{x+22}" y1="{y-4}" y2="{y-4}" stroke="{C[scen]}" stroke-width="2.5"/>' + t(x + 28, y, NOME[scen], 11, TXT)
    b += t(40, 462, "Fonte: cálculo V3 (v3_02_central_grade.py).", 11)
    open(AQUI / "fig_v3_1_ganho_por_cad.svg", "w").write(svg(W, H, b))


# ---------- Fig 2: Ky do sorgo ----------
def fig2():
    r = J("res_03_extras.json")["equilibrio"]
    W, H = 980, 470
    b = t(40, 26, "O ganho no pior ano depende do Ky do sorgo", 15, TXT, weight="bold")
    b += t(40, 46, "Eixo x: multiplicador sobre o Ky do sorgo em cada cenário. A linha cruza o zero no \"Ky de equilíbrio\".", 12)
    for k, (nome, tit) in enumerate([("raso_A4_87.5", "Raso da A4 (CAD 87,5 mm)"), ("raso_ZARC_42", "Raso pelo ZARC (CAD 42 mm)")]):
        ax = Eixo(70 + k * 480, 90, 380, 250, 0.25, 4.0, -40, 100)
        b += t(ax.x0, 78, tit, 12, TXT, weight="bold")
        b += ax.grade(range(-40, 101, 20), (0.5, 1, 1.5, 2, 3, 4), xlab=lambda v: "×" + fmt(v, 1 if v < 1 or v % 1 else 0))
        b += f'<line x1="{ax.x0}" x2="{ax.x0+ax.w}" y1="{ax.Y(0)}" y2="{ax.Y(0)}" stroke="{TXT2}"/>'
        b += f'<line x1="{ax.x0}" x2="{ax.x0+ax.w}" y1="{ax.Y(10)}" y2="{ax.Y(10)}" stroke="{TXT}" stroke-dasharray="5 4"/>' + t(ax.x0 + ax.w - 4, ax.Y(10) - 5, "critério +10%", 11, TXT, anchor="end")
        b += f'<line x1="{ax.X(1)}" x2="{ax.X(1)}" y1="{ax.y0}" y2="{ax.y0+ax.h}" stroke="{TXT2}" stroke-width="0.8" stroke-dasharray="2 3"/>' + t(ax.X(1) + 3, ax.y0 + 12, "Ky da fonte", 10)
        for scen in ("A4", "FAO33", "MISTO", "BIOMASSA"):
            cur = r[f"{scen}|{nome}"]["curva_ky"]
            pts = [(float(x), y) for x, y in cur.items()]
            b += f'<polyline points="{" ".join(f"{ax.X(x):.1f},{ax.Y(min(max(y, -40), 100)):.1f}" for x, y in pts)}" fill="none" stroke="{C[scen]}" stroke-width="2.2"/>'
            eq = r[f"{scen}|{nome}"]["ky_mult_equilibrio_p10"]
            if eq not in (None, float("inf")) and 0.25 <= eq <= 4:
                b += f'<circle cx="{ax.X(eq):.1f}" cy="{ax.Y(0):.1f}" r="5" fill="{BG}" stroke="{C[scen]}" stroke-width="2"><title>{NOME[scen]}: equilíbrio em ×{eq:.2f}</title></circle>'
        b += t(ax.x0 + ax.w / 2, ax.y0 + ax.h + 38, "multiplicador do Ky do sorgo", 11, anchor="middle")
        b += t(ax.x0 - 50, ax.y0 - 14, "ganho do P10, %", 11)
    for i, scen in enumerate(("A4", "FAO33", "MISTO", "BIOMASSA")):
        x = 70 + (i % 2) * 450; y = 392 + (i // 2) * 18
        b += f'<line x1="{x}" x2="{x+22}" y1="{y-4}" y2="{y-4}" stroke="{C[scen]}" stroke-width="2.5"/>' + t(x + 28, y, NOME[scen] + (f" · equilíbrio ×{r[f'{scen}|raso_A4_87.5']['ky_mult_equilibrio_p10']:.2f} / ×{r[f'{scen}|raso_ZARC_42']['ky_mult_equilibrio_p10']:.2f}"), 11, TXT)
    b += t(40, 432, "Círculos = Ky de equilíbrio (ganho de P10 = 0). Fonte: cálculo V3 (v3_03_extras.py). R = 0,88.", 11)
    open(AQUI / "fig_v3_2_ky_sorgo.svg", "w").write(svg(W, H, b))


# ---------- Fig 3: fração da grade que sobrevive, por fator ----------
def fig3():
    g = J("res_02_central_grade.json")["grade"]
    W, H = 980, 540
    b = t(40, 26, "Em quantas combinações de parâmetros a afirmação sobrevive", 15, TXT, weight="bold")
    b += t(40, 46, "Sobrevive = ganho de P10 &gt; 0 e média caindo no máximo 3%. Grade pré-definida: 270 combinações por solo (cenário \"misto\" fica de fora, é pós-teste).", 12)
    fatores = [("R = 0,75", lambda l: l["R"] == 0.75), ("R = 0,88", lambda l: l["R"] == 0.88), ("R = 1,0", lambda l: l["R"] == 1.0),
               ("Ky sorgo ×0,5", lambda l: l["kym"] == 0.5), ("×0,75", lambda l: l["kym"] == 0.75), ("×1", lambda l: l["kym"] == 1.0), ("×1,5", lambda l: l["kym"] == 1.5), ("×2", lambda l: l["kym"] == 2.0),
               ("cenário A4", lambda l: l["scen"] == "A4"), ("FAO-33", lambda l: l["scen"] == "FAO33"), ("biomassa", lambda l: l["scen"] == "BIOMASSA"),
               ("sorgo mesma data", lambda l: l["desl"] == 0), ("sorgo +30 d", lambda l: l["desl"] == 30), ("TODAS", lambda l: True)]
    ax = Eixo(190, 80, 330, 400, 0, 100, 0, 1)
    for k, (rot, nome, cor) in enumerate([("V3a_raso_A4_87.5", "Raso A4 (87,5 mm)", "#2a78d6"), ("V3b_raso_ZARC_42", "Raso ZARC (42 mm)", "#eb6834"), ("controle_fundo_175", "Controle: fundo (175 mm)", "#8a8a85")]):
        x0 = 190 + k * 260 if False else 0
    # três painéis lado a lado
    painel_w = 220
    for k, (rot, nome, cor) in enumerate([("V3a_raso_A4_87.5", "Raso A4 (87,5 mm)", "#2a78d6"), ("V3b_raso_ZARC_42", "Raso ZARC (42 mm)", "#eb6834"), ("controle_fundo_175", "Controle: fundo (175 mm)", "#8a8a85")]):
        ox = 190 + k * 260
        b += t(ox, 78, nome, 12, TXT, weight="bold")
        pre = [l for l in g[rot] if l["scen"] in ("A4", "FAO33", "BIOMASSA")]
        for i, (rotf, fn) in enumerate(fatores):
            ls = [l for l in pre if fn(l)]
            sh = np.mean([l["ok"] for l in ls])
            y = 92 + i * 27
            if k == 0: b += t(ox - 10, y + 15, rotf, 11, TXT if rotf != "TODAS" else TXT, anchor="end", weight="bold" if rotf == "TODAS" else "normal")
            b += f'<rect x="{ox}" y="{y}" width="{painel_w}" height="19" fill="{GRID}"/><rect x="{ox}" y="{y}" width="{painel_w*sh:.1f}" height="19" fill="{cor}"><title>{nome}, {rotf}: {100*sh:.0f}%</title></rect>'
            b += t(ox + painel_w * sh + 5 if sh < 0.8 else ox + painel_w * sh - 5, y + 14, f"{100*sh:.0f}%", 11, TXT if sh < 0.8 else "#ffffff", anchor="start" if sh < 0.8 else "end")
        for lim, cl in ((0.4, "40%"), (0.7, "70%")):
            b += f'<line x1="{ox+painel_w*lim}" x2="{ox+painel_w*lim}" y1="88" y2="{92+len(fatores)*27}" stroke="{TXT}" stroke-dasharray="3 3" stroke-width="0.8"/>' + (t(ox + painel_w * lim, 86, cl, 10, TXT, anchor="middle") if k == 0 else t(ox + painel_w * lim, 86, cl, 10, TXT, anchor="middle"))
    b += t(40, 504, "Linhas tracejadas: 40% e 70% (cortes do critério pré-definido: ≥ 70% sustenta, 40–70% parcial). Fonte: cálculo V3 (v3_02_central_grade.py).", 11)
    open(AQUI / "fig_v3_3_grade.svg", "w").write(svg(W, H, b))


# ---------- Fig 4: ano a ano ----------
def fig4():
    W, H = 980, 490
    b = t(40, 26, "O sorgo como seguro: ganho da mistura 50/50 sobre 100% milho, safra a safra", 15, TXT, weight="bold")
    b += t(40, 46, "Média das 5 datas de plantio, FAO-33 central, R = 0,88. Barra para cima = a mistura rendeu mais silagem que só milho.", 12)
    for k, (cad, tit) in enumerate([(87.5, "Raso da A4 (CAD 87,5 mm)"), (42.0, "Raso pelo ZARC (CAD 42 mm)")]):
        cs = V.casos(cad, scen="FAO33")
        ym = np.array([c[2] for c in cs]).reshape(-1, 5); ys = np.array([c[3] for c in cs]).reshape(-1, 5)
        gain = (0.5 * ym + 0.5 * 0.88 * ys - ym).mean(axis=1)
        ax = Eixo(70, 90 + k * 175, 840, 120, -0.5, 40.5, -0.15, 0.25)
        b += t(ax.x0, 82 + k * 175, tit, 12, TXT, weight="bold")
        for v in (-0.1, 0, 0.1, 0.2):
            b += f'<line x1="{ax.x0}" x2="{ax.x0+ax.w}" y1="{ax.Y(v)}" y2="{ax.Y(v)}" stroke="{GRID if v else TXT2}"/>' + t(ax.x0 - 8, ax.Y(v) + 4, fmt(v, 1), 11, anchor="end")
        for i, a in enumerate(V.SAFRAS):
            g = gain[i]; cor = "#2a78d6" if g >= 0 else "#eb6834"
            b += f'<rect x="{ax.X(i)-6:.1f}" y="{min(ax.Y(g), ax.Y(0)):.1f}" width="12" height="{abs(ax.Y(g)-ax.Y(0)):.1f}" fill="{cor}"><title>{a}/{str(a+1)[2:]}: milho {ym[i].mean():.2f}, ganho {g:+.3f}</title></rect>'
            if (a % 5 == 0 and a not in (2005, 2010, 2020)) or a in (2004, 2011, 2021): b += t(ax.X(i), ax.y0 + ax.h + 15, f"{a}/{str(a+1)[2:]}", 10, anchor="middle", color=TXT if a in (2004, 2011, 2021) else TXT2)
        b += t(ax.x0 + ax.w, ax.y0 - 6, f"safras com ganho: {(gain>0).sum()} de 41 · safras com perda &gt; 0,02: {(gain < -0.02).sum()}", 11, TXT, anchor="end")
    b += t(40, 462, "Rótulos em preto: 2004/05, 2011/12 e 2021/22, estiagens conhecidas. Fonte: cálculo V3 (v3_05_anos_secos_pam.py).", 11)
    open(AQUI / "fig_v3_4_ano_a_ano.svg", "w").write(svg(W, H, b))


# ---------- Fig 5: ZARC ----------
def fig5():
    r = J("res_04_zarc.json")
    W, H = 980, 470
    b = t(40, 26, "Conferência com o ZARC 2026/27 de SMO: chance de o ISNA ficar abaixo do limite da fase", 15, TXT, weight="bold")
    b += t(40, 46, "Nosso balanço (pontos) e a classe de risco publicada pelo ZARC (faixas), por água disponível do solo. Milho: fase I &lt; 0,70 ou fase III &lt; 0,55. Sorgo: 0,70 / 0,60 / 0,40.", 12)
    ax = Eixo(80, 90, 820, 280, 20, 100, 0, 0.5)
    b += ax.grade([0, 0.1, 0.2, 0.3, 0.4, 0.5], (24, 31.8, 41.4, 54.6, 72.6, 95.4), ylab=lambda v: fmt(100 * v) + "%", xlab=lambda v: fmt(v, 0 if v % 1 == 0 else 1))
    for lim, nome in ((0.2, "ZARC 20%"), (0.3, "ZARC 30%"), (0.4, "ZARC 40%")):
        b += f'<line x1="{ax.x0}" x2="{ax.x0+ax.w}" y1="{ax.Y(lim)}" y2="{ax.Y(lim)}" stroke="{TXT}" stroke-dasharray="5 4" stroke-width="0.9"/>' + t(ax.x0 + ax.w + 4, ax.Y(lim) + 4, nome, 11, TXT)
    for crop, cor in (("milho", "#2a78d6"), ("sorgo", "#eb6834")):
        pts = []
        for nome, v in r[crop].items():
            p = float(np.mean(v["p_evento"])); pts.append((v["cad"], p))
            zr = [x for x in v["zarc"] if x]
            lab = f"ZARC {int(np.mean(zr))}%" if zr else "ZARC: não indicado"
            b += f'<circle cx="{ax.X(v["cad"]):.1f}" cy="{ax.Y(p):.1f}" r="5.5" fill="{cor}"><title>{crop} {nome} CAD {v["cad"]} mm: P(evento) {p:.2f}; {lab}</title></circle>'
            b += t(ax.X(v["cad"]), ax.Y(p) - 10 if crop == "milho" else ax.Y(p) + 20, f"{nome}", 10, anchor="middle")
        b += f'<polyline points="{" ".join(f"{ax.X(x):.1f},{ax.Y(y):.1f}" for x, y in sorted(pts))}" fill="none" stroke="{cor}" stroke-width="1.8"/>'
    b += t(ax.x0 + ax.w / 2, ax.y0 + ax.h + 38, "CAD (mm): milho AD1–AD6 (60 cm); sorgo tipos 1–3 (42, 66, 90 mm)", 11, anchor="middle")
    b += f'<circle cx="95" cy="408" r="5.5" fill="#2a78d6"/>' + t(106, 412, "milho", 11, TXT) + f'<circle cx="170" cy="408" r="5.5" fill="#eb6834"/>' + t(181, 412, "sorgo forrageiro", 11, TXT)
    b += t(40, 432, "ZARC SMO: milho AD3 = 30%, AD2 40% ou não indicado, AD4–AD6 20–30%; sorgo = 20% nos três tipos. Fonte: cálculo V3 (v3_04_zarc.py); ZARC em sessoes/A4/zarc_smo_resumo.txt.", 11)
    open(AQUI / "fig_v3_5_zarc.svg", "w").write(svg(W, H, b))


# ---------- Fig 6: solo raso por SRTM ----------
def fig6():
    r = J("res_06_srtm.json")
    W, H = 980, 450
    b = t(40, 26, "Solo raso por talhão com SRTM: o declive sozinho erra o Neossolo Litólico", 15, TXT, weight="bold")
    b += t(40, 46, "Fração da área marcada como \"possível solo raso\" em 210 ha mapeados em SMO (UDESC: 38,2% Neossolo Regolítico + Litólico) e nos 3 perfis descritos. Limiares escolhidos depois de ver os 3 perfis.", 12)
    nomes = list(r["regras"].keys())
    ax = Eixo(250, 80, 380, 240, 0, 0.7, 0, 1)
    for i, n in enumerate(nomes):
        y = 90 + i * 40; reg = r["regras"][n]
        b += t(240, y + 16, n.replace(">=", " ≥ ").replace("declive", "declive").replace("ou", "ou"), 12, TXT, anchor="end")
        b += f'<rect x="250" y="{y}" width="{380*reg["frac_area_udesc"]/0.7:.1f}" height="22" fill="#2a78d6"><title>área UDESC: {100*reg["frac_area_udesc"]:.0f}%</title></rect>' + t(250 + 380 * reg["frac_area_udesc"] / 0.7 + 5, y + 16, f'{100*reg["frac_area_udesc"]:.0f}%', 11, TXT)
        for j, (k, lab) in enumerate([("marca_perfil5_profundo", "P5"), ("marca_perfil6_regolitico", "P6"), ("marca_perfil7_litolico", "P7")]):
            ok = reg[k] if j > 0 else (not reg[k])  # P5 profundo: acerto = não marcar
            cx = 700 + j * 60
            b += f'<circle cx="{cx}" cy="{y+11}" r="9" fill="{"#1baf7a" if ok else "#eb6834"}"><title>{lab}: {"acerta" if ok else "erra"}</title></circle>' + t(cx, y + 15, "✓" if ok else "✗", 12, "#ffffff", anchor="middle", weight="bold")
    x38 = 250 + 380 * 0.382 / 0.7
    b += f'<line x1="{x38}" x2="{x38}" y1="84" y2="{90+len(nomes)*40}" stroke="{TXT}" stroke-dasharray="5 4"/>' + t(x38, 78, "mapa UDESC: 38,2%", 11, TXT, anchor="middle")
    for j, lab in enumerate(["P5 Latossolo (profundo)", "P6 Regolítico", "P7 Litólico"]):
        b += t(700 + j * 60, 80, lab.split(" ")[0], 11, TXT, anchor="middle")
    b += t(700, 66, "perfis: acerta (✓) ou erra (✗)", 11, TXT)
    b += t(40, 400, "SRTM 30 m dá declive de 10,5% / 21,3% / 9,6% nos perfis 5 / 6 / 7; a medida de campo foi 9% / 38% / 19%. O SRTM suaviza o relevo e subestima o declive.", 11)
    b += t(40, 418, "P7 é topo de encosta, pedregoso, solo &lt; 50 cm: declive baixo e posição convexa (TPI 90 m = +4,9 m). Fonte: cálculo V3 (v3_06_srtm_solo_raso.py); UDESC, Müller (2020).", 11)
    open(AQUI / "fig_v3_6_solo_raso_srtm.svg", "w").write(svg(W, H, b))


for f in (fig1, fig2, fig3, fig4, fig5, fig6): f()
print("ok")
