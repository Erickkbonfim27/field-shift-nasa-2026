#!/usr/bin/env python3
"""Gera a1_1_mapa.svg e a1_23_risco_retorno.svg (SVG puro, sem matplotlib)."""
import json
from validar_a1_1 import pares
M = json.load(open("mapa_smo.json"))
MES = "jan fev mar abr mai jun jul ago set out nov dez".split()
NOMES = {"milho_safra": "Milho safra", "milho_safrinha": "Milho safrinha", "feijao": "Feijão", "sorgo": "Sorgo", "pastagem_inv": "Pastagem inverno"}
Z = pares("argiloso"); Z["pastagem_inv"] = Z["pastagem_inv"]  # aveia grão, só referência
# ordem da safra: ago -> jul
ORDEM = list(range(22, 37)) + list(range(1, 22))
cw, ch, x0, y0 = 22, 26, 130, 60
W = x0 + cw * 36 + 20; H = y0 + len(NOMES) * (ch + 14) + 70
def cor(v):  # 0..10 -> branco -> verde escuro
    t = v / 10; r = int(245 - t * (245 - 22)); g = int(245 - t * (245 - 120)); b = int(240 - t * (240 - 60)); return f"rgb({r},{g},{b})"
s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" font-family="Helvetica,Arial,sans-serif" font-size="11">',
     f'<rect width="{W}" height="{H}" fill="white"/>',
     f'<text x="{x0}" y="22" font-size="14" font-weight="bold">São Miguel do Oeste: anos em 10 que a cultura colhe bem, por decêndio de plantio</text>',
     f'<text x="{x0}" y="40" fill="#555">NASA POWER 1984–2024, solo argiloso. Número = colhe bem (água ≥ 0,6 e sem geada). Barra abaixo = indicado pelo ZARC 2026/27 (aveia é grão, só referência).</text>']
for i, d in enumerate(ORDEM):
    if (d - 1) % 3 == 0: s.append(f'<text x="{x0 + i*cw + 2}" y="{y0 - 4}" fill="#333">{MES[(d-1)//3]}</text>')
for j, (c, nome) in enumerate(NOMES.items()):
    y = y0 + j * (ch + 14)
    s.append(f'<text x="{x0 - 6}" y="{y + 17}" text-anchor="end">{nome}</text>')
    m = M[f"{c}|argiloso"]
    for i, d in enumerate(ORDEM):
        v = m[str(d)]["bem"]
        s.append(f'<rect x="{x0 + i*cw}" y="{y}" width="{cw-1}" height="{ch}" fill="{cor(v)}"/>')
        s.append(f'<text x="{x0 + i*cw + cw/2 - 0.5}" y="{y + 17}" text-anchor="middle" fill="{"white" if v >= 6 else "#333"}">{v:.0f}</text>')
        if c in Z and Z[c][d-1] > 0:
            s.append(f'<rect x="{x0 + i*cw}" y="{y + ch + 2}" width="{cw-1}" height="5" fill="#d07a1a"/>')
yl = y0 + len(NOMES) * (ch + 14) + 14
s.append(f'<rect x="{x0}" y="{yl}" width="22" height="5" fill="#d07a1a"/><text x="{x0+28}" y="{yl+6}">indicado pelo ZARC (risco ≤ 40%)</text>')
s.append(f'<text x="{x0}" y="{yl+26}" fill="#555">Lendo: o mapa repete o calendário da geada (mar–ago) e diz que, em solo argiloso, a água quase nunca derruba a chance abaixo de 8 em 10 entre set e jan.</text>')
s.append("</svg>")
open("a1_1_mapa.svg", "w").write("\n".join(s))

# ---------- risco x retorno ----------
from escalonamento import stats
import statistics as st
A = json.load(open("series_milho_argiloso.json")); P = json.load(open("series_milho_pot_argiloso.json"))
def pts(S, combos):
    sing = [(d, stats(list(S[d].values()))) for d in S]
    com = [(n, stats([st.mean(S[str(x)][a] for x in c) for a in S["26"]])) for n, c in combos]
    return sing, com
W, H, L0, T0, PW, PH = 760, 430, 70, 50, 300, 300
def panel(ox, titulo, S, combos):
    sing, com = pts(S, combos)
    X = lambda m: ox + (m - 0.5) / 0.5 * PW
    Y = lambda p: T0 + PH - (p - 0.0) / 0.7 * PH
    o = [f'<text x="{ox}" y="{T0-12}" font-weight="bold">{titulo}</text>',
         f'<rect x="{ox}" y="{T0}" width="{PW}" height="{PH}" fill="none" stroke="#bbb"/>']
    for v in (0.6, 0.7, 0.8, 0.9, 1.0):
        o.append(f'<text x="{X(v)}" y="{T0+PH+14}" text-anchor="middle" fill="#555">{v:.1f}</text>')
    for v in (0.0, 0.2, 0.4, 0.6):
        o.append(f'<text x="{ox-6}" y="{Y(v)+4}" text-anchor="end" fill="#555">{v:.1f}</text>')
    for d, s_ in sing:
        o.append(f'<circle cx="{X(s_["media"])}" cy="{Y(s_["pior"])}" r="4" fill="#8aa" />')
        if d in ("26", "35", "1", "2", "25", "27"):
            o.append(f'<text x="{X(s_["media"])+5}" y="{Y(s_["pior"])-4}" fill="#477" font-size="10">{ {"26":"15/set","35":"15/dez","1":"5/jan","2":"15/jan","25":"5/set","27":"25/set"}[d] }</text>')
    for n, s_ in com:
        o.append(f'<rect x="{X(s_["media"])-5}" y="{Y(s_["pior"])-5}" width="10" height="10" fill="#d07a1a"/>')
        o.append(f'<text x="{X(s_["media"])-8}" y="{Y(s_["pior"])+16}" fill="#a55a0a" font-size="10" text-anchor="end">{n}</text>')
    return o
s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" font-family="Helvetica,Arial,sans-serif" font-size="11">',
     f'<rect width="{W}" height="{H}" fill="white"/>',
     f'<text x="{L0}" y="20" font-size="14" font-weight="bold">Milho em São Miguel do Oeste: plantar numa data só (círculos) ou dividir (quadrados)</text>']
s += panel(L0, "A1-2: só água (sem penalidade de potencial)", A, [("set+out", (26, 29)), ("set+nov", (26, 31)), ("set+out+nov", (26, 29, 32))])
s += panel(L0 + PW + 80, "A1-3: com penalidade de radiação", P, [("set+dez", (26, 35)), ("set+jan", (26, 1))])
s.append(f'<text x="{L0}" y="{T0+PH+34}" fill="#333">Eixo x: rendimento relativo médio (41 safras). Eixo y: rendimento no pior ano. Melhor = para cima e para a direita.</text>')
s.append(f'<text x="{L0}" y="{T0+PH+52}" fill="#555">Dividir só ganha no pior ano quando mistura cedo e tarde, e aí perde ~10 pontos na média. Nenhum quadrado domina a melhor data única.</text>')
s.append("</svg>")
open("a1_23_risco_retorno.svg", "w").write("\n".join(s))
print("ok")
