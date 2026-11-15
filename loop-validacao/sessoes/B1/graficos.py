#!/usr/bin/env python3
"""Gera os gráficos SVG das fichas B1 (sem matplotlib, que não está instalado)."""
import json
from pathlib import Path

AQUI = Path(__file__).resolve().parent
W, H, M = 640, 400, dict(l=64, r=20, t=48, b=56)
CORES = ["#2a6fdb", "#d1495b", "#3c9d5d", "#8a5cc2"]


def esc(t):
    return str(t).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _eixos(titulo, xl, yl, xr, yr, xticks, yticks):
    titulo, xl, yl = esc(titulo), esc(xl), esc(yl)
    pw, ph = W - M["l"] - M["r"], H - M["t"] - M["b"]
    sx = lambda x: M["l"] + (x - xr[0]) / (xr[1] - xr[0]) * pw
    sy = lambda y: M["t"] + ph - (y - yr[0]) / (yr[1] - yr[0]) * ph
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="Helvetica,Arial,sans-serif" font-size="12">',
         f'<rect width="{W}" height="{H}" fill="#ffffff"/>',
         f'<text x="{W/2}" y="24" text-anchor="middle" font-size="15" font-weight="bold" fill="#222">{titulo}</text>']
    for t, lab in yticks:
        s.append(f'<line x1="{M["l"]}" x2="{W-M["r"]}" y1="{sy(t):.1f}" y2="{sy(t):.1f}" stroke="#e5e5e5"/>')
        s.append(f'<text x="{M["l"]-6}" y="{sy(t)+4:.1f}" text-anchor="end" fill="#555">{lab}</text>')
    for t, lab in xticks:
        s.append(f'<text x="{sx(t):.1f}" y="{H-M["b"]+18}" text-anchor="middle" fill="#555">{lab}</text>')
    s.append(f'<line x1="{M["l"]}" x2="{W-M["r"]}" y1="{H-M["b"]}" y2="{H-M["b"]}" stroke="#888"/>')
    s.append(f'<text x="{W/2}" y="{H-12}" text-anchor="middle" fill="#333">{xl}</text>')
    s.append(f'<text transform="translate(16,{H/2}) rotate(-90)" text-anchor="middle" fill="#333">{yl}</text>')
    return s, sx, sy


def dispersao(arq, titulo, xl, yl, pts, xr, yr, xticks, yticks, nota=""):
    """pts: lista de (x, y, rotulo, destaque)."""
    s, sx, sy = _eixos(titulo, xl, yl, xr, yr, xticks, yticks)
    for x, y, lab, dest in pts:
        cor = CORES[1] if dest else CORES[0]
        s.append(f'<circle cx="{sx(x):.1f}" cy="{sy(y):.1f}" r="{5 if dest else 4}" fill="{cor}" fill-opacity="0.75"/>')
        if dest: s.append(f'<text x="{sx(x)+6:.1f}" y="{sy(y)-5:.1f}" fill="{cor}" font-size="10">{lab}</text>')
    if nota: s.append(f'<text x="{W-M["r"]}" y="{M["t"]-8}" text-anchor="end" fill="#555" font-size="11">{esc(nota)}</text>')
    s.append("</svg>")
    (AQUI / arq).write_text("\n".join(s), encoding="utf-8")


def linhas(arq, titulo, xl, yl, cats, series, yr, yticks, nota=""):
    """series: lista de (nome, valores por categoria)."""
    xr = (-0.5, len(cats) - 0.5)
    s, sx, sy = _eixos(titulo, xl, yl, xr, yr, [(i, c) for i, c in enumerate(cats)], yticks)
    for j, (nome, vals) in enumerate(series):
        cor = CORES[j % 4]
        pts = " ".join(f"{sx(i):.1f},{sy(v):.1f}" for i, v in enumerate(vals))
        s.append(f'<polyline points="{pts}" fill="none" stroke="{cor}" stroke-width="2.5"/>')
        for i, v in enumerate(vals):
            s.append(f'<circle cx="{sx(i):.1f}" cy="{sy(v):.1f}" r="3.5" fill="{cor}"/>')
        s.append(f'<rect x="{M["l"]+10}" y="{M["t"]+8+18*j}" width="12" height="4" fill="{cor}"/>')
        s.append(f'<text x="{M["l"]+28}" y="{M["t"]+13+18*j}" fill="#333">{esc(nome)}</text>')
    if nota: s.append(f'<text x="{W-M["r"]}" y="{M["t"]-8}" text-anchor="end" fill="#555" font-size="11">{esc(nota)}</text>')
    s.append("</svg>")
    (AQUI / arq).write_text("\n".join(s), encoding="utf-8")


yt_rel = [(v / 10, f"{v/10:.1f}") for v in range(2, 19, 2)]
em10 = [(v, str(v)) for v in range(0, 11, 2)]

# B1-0: dispersão modelo x PAM (milho SMO)
r0 = json.load(open(AQUI / "b1_0_resultado.json"))["milho_smo"]
piores = set(r0["piores_obs"])
dispersao("b1_0_milho_modelo_x_pam.svg", "B1-0 · Milho em São Miguel do Oeste: modelo x IBGE",
          "rendimento relativo simulado (balanço hídrico, plantio 20/set)", "rendimento PAM / mediana móvel 9 anos",
          [(a["y_mod"], a["obs_rel"], str(a["ano"]), a["ano"] in piores) for a in r0["anos"]],
          (0.1, 1.05), (0.3, 1.8), [(v / 10, f"{v/10:.1f}") for v in range(1, 11, 2)], yt_rel,
          nota=f"ρ = {r0['rho_modelo']} · em vermelho os 8 piores anos da PAM")

# B1-0: janelas (perda hídrica x geada)
linhas_ctrl = [l.split(" | ") for l in (AQUI / "b1_0_geada_controle.txt").read_text().splitlines()[1:]]
linhas("b1_0_janelas_agua_x_geada.svg", "B1-0 · Milho safra em SMO: o balanço hídrico sozinho indica agosto",
       "data de plantio", "anos em cada 10", [l[0] for l in linhas_ctrl],
       [("perda por falta de água (y < 0,6)", [float(l[2]) for l in linhas_ctrl]),
        ("geada nas fases I–III (T2M_MIN < 2 °C)", [float(l[1]) for l in linhas_ctrl])],
       (0, 10), em10, nota="NASA POWER 1984–2025, solo argiloso")

# B1-1: curva de geada do milho safrinha
r1 = json.load(open(AQUI / "b1_1_resultado.json"))
linhas("b1_1_geada_safrinha.svg", "B1-1 · Milho safrinha (silagem) em SMO: geada antes do ponto",
       "data de plantio da safrinha", "anos em cada 10 com geada", [c["plantio"] for c in r1["curva"]],
       [("geada provável (T2M_MIN ≤ 3 °C)", [c["geada_leve_em_10"] for c in r1["curva"]]),
        ("geada forte (T2M_MIN ≤ 1 °C)", [c["geada_forte_em_10"] for c in r1["curva"]])],
       (0, 10), em10, nota="NASA POWER 1981–2025 · ponto de silagem = 1.250 °C·dia")

# B1-2: chuva na colheita x PAM cebola
r2 = json.load(open(AQUI / "b1_2_resultado.json"))
p2 = set(r2["resultados"][0]["piores_obs"])
dispersao("b1_2_chuva_colheita_x_pam.svg", "B1-2 · Cebola em Ituporanga: chuva na colheita x IBGE",
          "chuva de 15/out a 31/dez (mm, NASA POWER)", "rendimento PAM / mediana móvel 9 anos",
          [(a["chuva_out_dez"], a["obs_rel"], str(a["ano"]), a["ano"] in p2) for a in r2["anos"]],
          (180, 650), (0.5, 1.5), [(v, str(v)) for v in range(200, 651, 100)], [(v / 10, f"{v/10:.1f}") for v in range(5, 16, 2)],
          nota=f"ρ = {r2['resultados'][0]['rho']} · em vermelho os 8 piores anos da PAM")

# B1-3: calor na floração x PAM milho
r3 = json.load(open(AQUI / "b1_3_resultado.json"))["32.0"]
o0 = {a["ano"]: a["obs_rel"] for a in r0["anos"]}
dispersao("b1_3_calor_x_pam.svg", "B1-3 · Milho em SMO: dias de calor na floração x IBGE",
          "dias com T2M_MAX ≥ 32 °C (dias 55–80 após 20/set)", "rendimento PAM / mediana móvel 9 anos",
          [(v, o0[int(a)], a, int(a) in piores) for a, v in r3["por_ano"].items()],
          (-1, 26), (0.3, 1.8), [(v, str(v)) for v in range(0, 26, 5)], yt_rel,
          nota=f"ρ = {r3['rho']} (sinal ao contrário do esperado)")

# B1-4: dias favoráveis ao míldio x PAM cebola
r4 = json.load(open(AQUI / "b1_4_resultado.json"))["85"]
oc = {a["ano"]: a["obs_rel"] for a in r2["anos"]}
dispersao("b1_4_mildio_x_pam.svg", "B1-4 · Cebola em Ituporanga: clima de míldio x IBGE",
          "dias favoráveis ao míldio, 1/ago–31/out (RH2M ≥ 85%, 10–22 °C, chuva)", "rendimento PAM / mediana móvel 9 anos",
          [(v, oc[int(a)], a, int(a) in set(r4["piores_obs"])) for a, v in r4["por_ano"].items() if int(a) in oc],
          (10, 70), (0.5, 1.5), [(v, str(v)) for v in range(10, 71, 10)], [(v / 10, f"{v/10:.1f}") for v in range(5, 16, 2)],
          nota=f"ρ = {r4['rho']}")
print("ok")
