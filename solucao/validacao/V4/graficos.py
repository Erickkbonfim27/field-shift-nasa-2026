#!/usr/bin/env python3
"""Gráficos SVG da V4 a partir de v4_resultado.json (rodar depois de v4_motor.py)."""
import json
from pathlib import Path

AQUI = Path(__file__).resolve().parent
R = json.load(open(AQUI / "v4_resultado.json"))

ESTILO = """<style>
svg{--bg:#fcfcfb;--t1:#0b0b0b;--t2:#52514e;--grid:#e4e3df;--s1:#2a78d6;--s2:#eb6834;--s3:#1baf7a;--s4:#eda100;--band:#eef3fb}
@media (prefers-color-scheme: dark){svg{--bg:#1a1a19;--t1:#f0efec;--t2:#c3c2b7;--grid:#3a3a37;--s1:#3987e5;--s2:#d95926;--s3:#199e70;--s4:#c98500;--band:#22303f}}
text{font-family:system-ui,-apple-system,Segoe UI,sans-serif;fill:var(--t1)}
.t2{fill:var(--t2)} .tit{font-size:15px;font-weight:600} .sm{font-size:11px}
.grid{stroke:var(--grid);stroke-width:1} .axis{stroke:var(--t2);stroke-width:1}
rect.mk:hover,circle.mk:hover{opacity:.75}
</style>"""
COR = ["var(--s1)", "var(--s2)", "var(--s3)", "var(--s4)"]


def barras(caminho, titulo, sub, grupos, series, valores, ymin, ymax, passo, ylab, linha=None):
    W, H, ml, mr, mt, mb = 900, 470, 60, 20, 78, 92
    pw, ph = W - ml - mr, H - mt - mb
    Y = lambda v: mt + (ymax - v) / (ymax - ymin) * ph
    gw = pw / len(grupos)
    bw = min(22, (gw - 16) / len(series) - 2)
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" role="img" aria-label="{titulo}">', ESTILO,
         f'<rect width="{W}" height="{H}" fill="var(--bg)"/>',
         f'<text x="{ml}" y="26" class="tit">{titulo}</text>', f'<text x="{ml}" y="46" class="t2 sm">{sub}</text>']
    # legenda
    x = ml
    for i, nome in enumerate(series):
        s.append(f'<rect x="{x}" y="56" width="10" height="10" rx="2" fill="{COR[i]}"/><text x="{x+14}" y="65" class="sm">{nome}</text>')
        x += 14 + 7.2 * len(nome) + 18
    v = ymin
    while v <= ymax + 1e-9:
        s.append(f'<line x1="{ml}" x2="{W-mr}" y1="{Y(v):.1f}" y2="{Y(v):.1f}" class="grid"/>')
        s.append(f'<text x="{ml-6}" y="{Y(v)+4:.1f}" text-anchor="end" class="t2 sm">{v:+.1f}</text>'.replace("+0.0", "0"))
        v += passo
    s.append(f'<line x1="{ml}" x2="{W-mr}" y1="{Y(0):.1f}" y2="{Y(0):.1f}" class="axis"/>')
    if linha is not None:
        s.append(f'<line x1="{ml}" x2="{W-mr}" y1="{Y(linha[0]):.1f}" y2="{Y(linha[0]):.1f}" stroke="var(--t2)" stroke-dasharray="4,4"/>')
        s.append(f'<text x="{W-mr}" y="{Y(linha[0])-5:.1f}" text-anchor="end" class="t2 sm">{linha[1]}</text>')
    s.append(f'<text x="16" y="{mt+ph/2}" transform="rotate(-90 16 {mt+ph/2})" text-anchor="middle" class="t2 sm">{ylab}</text>')
    for g, nome in enumerate(grupos):
        x0 = ml + g * gw + (gw - len(series) * (bw + 2)) / 2
        for i in range(len(series)):
            val = valores[g][i]
            if val is None: continue
            y0, y1 = sorted((Y(0), Y(val)))
            s.append(f'<rect class="mk" x="{x0+i*(bw+2):.1f}" y="{y0:.1f}" width="{bw:.1f}" height="{max(1,y1-y0):.1f}" rx="2" fill="{COR[i]}">'
                     f'<title>{nome} · {series[i]}: {val:+.2f}</title></rect>')
        linhas = nome.split("|")
        for k, t in enumerate(linhas):
            s.append(f'<text x="{ml+g*gw+gw/2:.1f}" y="{H-mb+18+14*k}" text-anchor="middle" class="sm {"t2" if k else ""}">{t}</text>')
    s.append("</svg>")
    Path(caminho).write_text("\n".join(s))


def linhas_decisao(caminho, titulo, sub, datas, series, valores, faixa, faixa_rot, ymax):
    W, H, ml, mr, mt, mb = 900, 420, 60, 30, 78, 60
    pw, ph = W - ml - mr, H - mt - mb
    X = lambda i: ml + i / (len(datas) - 1) * pw
    Y = lambda v: mt + (ymax - v) / ymax * ph
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" role="img" aria-label="{titulo}">', ESTILO,
         f'<rect width="{W}" height="{H}" fill="var(--bg)"/>',
         f'<text x="{ml}" y="26" class="tit">{titulo}</text>', f'<text x="{ml}" y="46" class="t2 sm">{sub}</text>']
    if faixa:
        a, b = faixa
        h = pw / (len(datas) - 1) / 2
        x0, x1 = max(ml, X(a) - h), min(W - mr, X(b) + h)
        s.append(f'<rect x="{x0:.1f}" y="{mt}" width="{x1-x0:.1f}" height="{ph}" fill="var(--band)"/>')
        s.append(f'<text x="{x0+4:.1f}" y="{mt+14}" class="t2 sm">{faixa_rot}</text>')
    x = ml
    for i, nome in enumerate(series):
        s.append(f'<rect x="{x}" y="56" width="14" height="3" rx="1" fill="{COR[i]}"/><text x="{x+18}" y="62" class="sm">{nome}</text>')
        x += 18 + 7.2 * len(nome) + 18
    for v in range(0, int(ymax) + 1):
        s.append(f'<line x1="{ml}" x2="{W-mr}" y1="{Y(v):.1f}" y2="{Y(v):.1f}" class="grid"/><text x="{ml-6}" y="{Y(v)+4:.1f}" text-anchor="end" class="t2 sm">{v}</text>')
    s.append(f'<text x="16" y="{mt+ph/2}" transform="rotate(-90 16 {mt+ph/2})" text-anchor="middle" class="t2 sm">anos de falha em cada 10</text>')
    for i, d in enumerate(datas):
        s.append(f'<text x="{X(i):.1f}" y="{H-mb+18}" text-anchor="middle" class="t2 sm">{d}</text>')
    for k, nome in enumerate(series):
        pts = " ".join(f"{X(i):.1f},{Y(v):.1f}" for i, v in enumerate(valores[k]))
        s.append(f'<polyline points="{pts}" fill="none" stroke="{COR[k]}" stroke-width="2"/>')
        for i, v in enumerate(valores[k]):
            s.append(f'<circle class="mk" cx="{X(i):.1f}" cy="{Y(v):.1f}" r="4" fill="{COR[k]}" stroke="var(--bg)" stroke-width="2"><title>{datas[i]} · {nome}: {v} em 10</title></circle>')
    s.append(f'<text x="{ml}" y="{H-14}" class="t2 sm">Data de plantio (decêndio). Falha = rendimento do motor &lt; 0,6, flag de ano extremo ou geada no ciclo.</text>')
    s.append("</svg>")
    Path(caminho).write_text("\n".join(s))


# ---------- fig 1: rho por preditor e gabarito ----------
gab = [("G1_milho_mun_SMO", "Milho SMO|município"), ("G2_milho_micro_42001", "Milho SMO|microrregião"),
       ("G3a_milho_micro_42002_Chapeco", "Milho Chapecó|fora*"), ("G3b_milho_micro_42005_Concordia", "Milho Concórdia|fora*"),
       ("G4_cebola_mun_Itu", "Cebola Itu|município"), ("G5_cebola_micro_42014", "Cebola Itu|microrregião"),
       ("G6_cebola_micro_42011_RioDoSul", "Cebola Rio do Sul|fora*"), ("G6b_cebola_micro_42017_Tabuleiro_mesma_celula", "Cebola Tabuleiro|fora*")]
transf = {"G3a_milho_micro_42002_Chapeco": "milho_G2->Chapeco", "G3b_milho_micro_42005_Concordia": "milho_G2->Concordia",
          "G6_cebola_micro_42011_RioDoSul": "cebola_G5->RioDoSul", "G6b_cebola_micro_42017_Tabuleiro_mesma_celula": "cebola_G5->Tabuleiro(mesma celula)"}
vals = []
for k, _ in gab:
    m = R[k]
    d2 = R["fora_regiao"][transf[k]]["rho_d2"] if k in transf else m["d2"]["rho"]
    vals.append([m["b_cru"]["rho"], m["c1_cru"]["rho"], m["d1_cru"]["rho"], d2])
barras(AQUI / "fig1_rho_por_preditor.svg", "Quem explica o rendimento do IBGE PAM? (Spearman ρ)",
       "Chuva, água e motor d1 sem nenhum ajuste; d2 = ridge em leave-one-out (*fora da região: treinado na microrregião de origem, sem reajuste)",
       [g[1] for g in gab], ["(b) chuva bruta", "(c) só água", "(d1) motor fixo", "(d2) motor ajustado"], vals, -0.4, 0.6, 0.2, "ρ com o rendimento sem tendência",
       linha=(0.4, "meta do milho (0,40)"))

# ---------- fig 2: ganho sobre a climatologia (SS) na ablação ----------
abl = [("G1_milho_mun_SMO", "Milho SMO|município"), ("G2_milho_micro_42001", "Milho SMO|microrregião"),
       ("G4_cebola_mun_Itu", "Cebola Itu|município"), ("G5_cebola_micro_42014", "Cebola Itu|microrregião")]
vals = [[R["ablacao"][k][c]["SS"] for c in ("agua(0,1,2)", "so_flag", "agua+flag", "motor_completo")] for k, _ in abl]
barras(AQUI / "fig2_ganho_sobre_climatologia.svg", "Ganho sobre a média dos anos (SS, leave-one-out)",
       "SS > 0: erra menos que a climatologia. O flag de ano extremo sozinho ganha; somar módulos num ajuste estatístico perde.",
       [g[1] for g in abl], ["só água por fase", "só flag de extremo", "água + flag", "motor completo (6 variáveis)"], vals, -0.3, 0.3, 0.1,
       "SS = 1 − EQM / EQM da climatologia")

# ---------- fig 3: decisão da data do milho ----------
D1 = R["decisao_D1_data_milho_SMO"]
linhas_decisao(AQUI / "fig3_decisao_data_milho.svg", "Milho em São Miguel do Oeste: só água manda plantar em agosto; o motor não",
               "NASA POWER 1985–2025, solo argiloso. Faixa azul: ZARC 2026/27 risco 20–30% (solos AD4–AD6). ZARC dá 40% em 1/ago e 11/ago.",
               [j["data"] for j in D1], ["só água (controle)", "motor composto (d1)"],
               [[j["falha_agua"] for j in D1], [j["falha_motor"] for j in D1]], (2, 14), "ZARC 20–30%", 7)

# ---------- fig 4: decisão do transplante da cebola ----------
D2 = R["decisao_D2_transplante_cebola_Itu"]
i20 = [i for i, j in enumerate(D2) if j["zarc_n_linhas_20pct"] > 0]
linhas_decisao(AQUI / "fig4_decisao_transplante_cebola.svg", "Cebola em Ituporanga: o motor prefere setembro; o ZARC, não",
               "NASA POWER 1984–2025. Faixa azul: decêndios com risco 20% em ao menos uma linha do ZARC cebola sequeiro de Ituporanga.",
               [j["data"] for j in D2], ["só água (controle)", "motor composto (d1)"],
               [[j["falha_agua"] for j in D2], [j["falha_motor"] for j in D2]], (min(i20), max(i20)), "ZARC 20% em alguma linha", 3)
print("ok")
