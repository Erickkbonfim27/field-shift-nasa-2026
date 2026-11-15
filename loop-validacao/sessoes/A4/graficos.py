#!/usr/bin/env python3
"""Gera os gráficos SVG da sessão A4 (sem matplotlib nesta máquina)."""
import json, statistics as st

C = ["#2a78d6", "#eb6834", "#1baf7a"]  # paleta de referência (slots 1-3)
TXT, TXT2, GRID, BG = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb"
F = 'font-family="Helvetica, Arial, sans-serif"'


def svg(w, h, body):
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}"><rect width="{w}" height="{h}" fill="{BG}"/>{body}</svg>'


def t(x, y, s, size=12, color=TXT2, anchor="start", weight="normal"):
    return f'<text x="{x}" y="{y}" {F} font-size="{size}" fill="{color}" text-anchor="{anchor}" font-weight="{weight}">{s}</text>'


# ---------- Figura 1: ano a ano, plantio 1/out, solo médio ----------
def fig1():
    c = json.load(open("casos_a4_1_R0.85_medio_ky1.0_kc1.0_raizNone.json"))
    c = [x for x in c if x["rot"] == "01/10"]
    W, H, L, R, T, B = 900, 400, 60, 140, 60, 64
    pw, ph = W - L - R, H - T - B
    xs = lambda i: L + pw * i / (len(c) - 1)
    ys = lambda v: T + ph * (1 - v)
    b = t(L, 24, "Milho ou sorgo? Rendimento relativo da silagem, plantio em 1/out, solo médio (SMO, 1984–2024)", 15, TXT, weight="bold")
    b += t(L, 44, "Sorgo já descontado (× 0,85). A troca compensa quando a linha laranja fica acima da azul.", 12)
    for v in (0, 0.2, 0.4, 0.6, 0.8, 1.0):
        b += f'<line x1="{L}" x2="{L+pw}" y1="{ys(v)}" y2="{ys(v)}" stroke="{GRID}" stroke-width="1"/>' + t(L - 8, ys(v) + 4, f"{v:.1f}".replace(".", ","), 11, anchor="end")
    b += f'<line x1="{L}" x2="{L+pw}" y1="{ys(0.6)}" y2="{ys(0.6)}" stroke="{TXT2}" stroke-width="1" stroke-dasharray="4 4"/>' + t(L + pw + 6, ys(0.6) + 4, "perda (&lt; 0,6)", 11)
    for i, x in enumerate(c):
        if x["safra"] % 5 == 0: b += t(xs(i), H - B + 18, f'{x["safra"]}/{str(x["safra"]+1)[2:]}', 11, anchor="middle")
        if x["ys"] * 0.85 > x["ym"]:
            b += f'<rect x="{xs(i)-6}" y="{T}" width="12" height="{ph}" fill="{C[1]}" opacity="0.08"/>'
    for k, (campo, mult, cor, nome) in enumerate([("ym", 1, C[0], "Milho"), ("ys", 0.85, C[1], "Sorgo × 0,85")]):
        pts = " ".join(f"{xs(i):.1f},{ys(x[campo]*mult):.1f}" for i, x in enumerate(c))
        b += f'<polyline points="{pts}" fill="none" stroke="{cor}" stroke-width="2"/>'
        for i, x in enumerate(c):
            b += f'<circle cx="{xs(i):.1f}" cy="{ys(x[campo]*mult):.1f}" r="4" fill="{cor}" stroke="{BG}" stroke-width="2"><title>{x["safra"]}/{x["safra"]+1}: {nome} {x[campo]*mult:.2f}</title></circle>'
        last = c[-1]
        b += t(L + pw + 10, ys(last[campo] * mult) + (4 if k == 0 else 16), nome, 12, TXT)
    n = sum(x["ys"] * 0.85 > x["ym"] for x in c)
    b += t(L, H - 22, f"Faixa laranja clara = safras em que a troca teria compensado: {n} de {len(c)}.", 11)
    b += t(L, H - 6, "Fonte: NASA POWER diário; balanço hídrico FAO-56/FAO-33 (cálculo da sessão A4).", 11)
    open("fig_a4_1_ano_a_ano.svg", "w").write(svg(W, H, b))


# ---------- Figura 2: por decêndio, safras em que a troca compensa, 3 solos ----------
def fig2():
    W, H, L, R, T, B = 960, 360, 60, 190, 60, 60
    pw, ph = W - L - R, H - T - B
    dados = {s: json.load(open(f"res_a4_1_R0.85_{s}_ky1.0_kc1.0_raizNone.json"))["por_decendio"] for s in ("argiloso", "medio", "raso")}
    n = len(dados["argiloso"])
    xs = lambda i: L + pw * i / (n - 1)
    mx = 25
    ys = lambda v: T + ph * (1 - v / mx)
    b = t(L, 24, "Em quantas das 41 safras plantar sorgo teria compensado, por data de plantio", 15, TXT, weight="bold")
    b += t(L, 44, "Sorgo × 0,85 &gt; milho. Só no solo raso, plantando em out, chega a cerca de metade das safras (linha tracejada).", 12)
    for v in range(0, mx + 1, 5):
        b += f'<line x1="{L}" x2="{L+pw}" y1="{ys(v)}" y2="{ys(v)}" stroke="{GRID}"/>' + t(L - 8, ys(v) + 4, str(v), 11, anchor="end")
    for i, x in enumerate(dados["argiloso"]):
        if i % 2 == 0: b += t(xs(i), H - B + 18, x["rot"], 11, anchor="middle")
    nomes = {"argiloso": "Solo argiloso profundo", "medio": "Solo médio", "raso": "Solo raso (0,5 m)"}
    for k, s in enumerate(dados):
        pts = " ".join(f"{xs(i):.1f},{ys(x['compensa']):.1f}" for i, x in enumerate(dados[s]))
        b += f'<polyline points="{pts}" fill="none" stroke="{C[k]}" stroke-width="2"/>'
        for i, x in enumerate(dados[s]):
            b += f'<circle cx="{xs(i):.1f}" cy="{ys(x["compensa"]):.1f}" r="4" fill="{C[k]}" stroke="{BG}" stroke-width="2"><title>{nomes[s]}, {x["rot"]}: {x["compensa"]} de {x["n"]}</title></circle>'
        b += t(L + pw + 10, ys(dados[s][-1]["compensa"]) + 4 - 14 * k, nomes[s], 12, TXT)
    b += f'<line x1="{L}" x2="{L+pw}" y1="{ys(20.5)}" y2="{ys(20.5)}" stroke="{TXT2}" stroke-dasharray="4 4"/>'
    b += t(L, H - 14, "Data de plantio (decêndio). Fonte: NASA POWER diário 1984–2025; cálculo da sessão A4.", 11)
    open("fig_a4_1_por_decendio.svg", "w").write(svg(W, H, b))


# ---------- Figura 3: rotações, déficit e risco ----------
def fig3():
    d = json.load(open("res_a4_2.json"))
    rots = list(d["argiloso"].keys())
    solos = [("argiloso", "Argiloso profundo"), ("medio", "Médio"), ("raso", "Raso (0,5 m)")]
    W, H = 980, 440
    L, T = 270, 80
    bh, gap = 9, 2
    grp = 3 * (bh + gap) + 14
    b = t(20, 24, "Rotações anuais em São Miguel do Oeste: água que falta e anos de perda (1984–2023)", 15, TXT, weight="bold")
    b += t(20, 44, "Déficit = água que a cultura pediu e o solo não deu (ETc − ETa), por ano. Chove ~1.860 mm/ano; a diferença entre rotações é pequena.", 12)
    for p, (campo, mx, titulo, fmt, x0) in enumerate([("deficit", 80, "Déficit médio (mm/ano)", lambda v: f"{v:.0f}", L),
                                                      ("risco_perda", 0.45, "Anos com perda em alguma cultura", lambda v: f"{100*v:.0f}%", L + 360)]):
        pw = 260
        b += t(x0, T - 12, titulo, 12, TXT, weight="bold")
        for gi, r in enumerate(rots):
            y0 = T + gi * grp
            if p == 0: b += t(L - 10, y0 + 18, r.replace("(ref.)", "(referência)"), 12, TXT, anchor="end")
            for k, (s, _) in enumerate(solos):
                v = d[s][r]["resumo"][campo]
                w = max(1, pw * v / mx)
                y = y0 + k * (bh + gap)
                b += f'<rect x="{x0}" y="{y}" width="{w:.1f}" height="{bh}" rx="2" fill="{C[k]}"><title>{r} · {s}: {fmt(v)}</title></rect>'
                b += t(x0 + w + 4, y + bh - 1, fmt(v), 10)
        b += f'<line x1="{x0}" x2="{x0}" y1="{T-4}" y2="{T + len(rots)*grp - 10}" stroke="{TXT2}"/>'
    ly = T + len(rots) * grp + 10
    for k, (_, nome) in enumerate(solos):
        b += f'<rect x="{L + k*170}" y="{ly}" width="12" height="12" rx="2" fill="{C[k]}"/>' + t(L + k * 170 + 18, ly + 11, nome, 12, TXT)
    b += t(20, H - 14, "Fonte: NASA POWER diário; balanço hídrico contínuo FAO-56/FAO-33, parâmetros FAO genéricos (sorgo não calibrado). Cálculo da sessão A4.", 11)
    open("fig_a4_2_rotacoes.svg", "w").write(svg(W, H, b))


fig1(); fig2(); fig3()
print("ok")
