#!/usr/bin/env python3
"""B5: gráficos SVG simples (sem matplotlib nesta máquina).

Cada gráfico: barras = rendimento do IBGE/PAM em % da tendência (vermelho = ano de perda);
linhas de marcas embaixo = anos que cada regra marcou.
"""
import csv, statistics as st
from html import escape
from pathlib import Path

AQUI = Path(__file__).resolve().parent


def tendencia(serie):
    anos = sorted(serie); mx, my = st.mean(anos), st.mean(serie.values())
    b = sum((a - mx) * (serie[a] - my) for a in anos) / sum((a - mx) ** 2 for a in anos)
    a0 = my - b * mx
    return {a: serie[a] / (a0 + b * a) for a in anos}


def svg(titulo, rel, corte, regras, arq, nota=""):
    anos = sorted(rel); n = len(anos)
    W, H, ml, mt = 900, 420 + 26 * len(regras), 60, 50
    bw = (W - ml - 20) / n
    y0 = mt + 250  # base das barras (0%)
    esc = 250 / 1.6
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" font-family="sans-serif" font-size="11">',
         f'<rect width="{W}" height="{H}" fill="#fff"/>',
         f'<text x="{ml}" y="24" font-size="15" font-weight="bold">{titulo}</text>',
         f'<text x="{ml}" y="40" fill="#555">{nota}</text>']
    for p in (0.5, 1.0, 1.5):
        y = y0 - p * esc
        o.append(f'<line x1="{ml}" x2="{W-20}" y1="{y}" y2="{y}" stroke="#ddd"/><text x="{ml-6}" y="{y+4}" text-anchor="end">{int(p*100)}%</text>')
    yc = y0 - corte * esc
    o.append(f'<line x1="{ml}" x2="{W-20}" y1="{yc}" y2="{yc}" stroke="#c00" stroke-dasharray="4 3"/><text x="{ml+4}" y="{mt+8}" fill="#c00">- - - corte de perda {int(corte*100)}%</text>')
    for i, a in enumerate(anos):
        x = ml + i * bw; h = min(rel[a], 1.6) * esc
        cor = "#c0392b" if rel[a] < corte else "#95a5a6"
        o.append(f'<rect x="{x+1}" y="{y0-h}" width="{bw-2}" height="{h}" fill="{cor}"/>')
        if a % 5 == 0:
            o.append(f'<text x="{x+bw/2}" y="{y0+14}" text-anchor="middle">{a}</text>')
    for j, (nome, marcados) in enumerate(regras.items()):
        y = y0 + 40 + 26 * j
        o.append(f'<text x="{ml}" y="{y-6}" fill="#333">{escape(nome)}</text>')
        for i, a in enumerate(anos):
            if a in marcados:
                acerto = rel[a] < corte
                o.append(f'<rect x="{ml+i*bw+2}" y="{y}" width="{bw-4}" height="8" fill="{"#c0392b" if acerto else "#2c3e50"}"/>')
    o.append(f'<text x="{ml}" y="{H-8}" fill="#555">Marca vermelha = acertou um ano de perda; marca escura = alarme falso. Fonte: IBGE/PAM (conferência) e NASA POWER (indicadores).</text>')
    o.append('</svg>')
    (AQUI / arq).write_text("\n".join(o))
    print("->", arq)


def pam(mun, prod):
    return {int(r["ano"]): float(r["rend_kg_ha"]) for r in csv.DictReader(open(AQUI / "pam_ibge.csv"))
            if r["municipio"] == mun and r["produto"] == prod and 1990 <= int(r["ano"]) <= 2024}


if __name__ == "__main__":
    rel = tendencia(pam("São Miguel do Oeste (SC)", "Milho (em grão)"))
    ind = {int(r["safra"]): r for r in csv.DictReader(open(AQUI / "indicadores_smo.csv"))}
    anos = sorted(rel)
    ch = {a: float(ind[a]["chuva_out_fev"]) for a in anos}; q1 = sorted(ch.values())[len(ch) // 4]
    extra = {}
    ndvi = AQUI / "ndvi_smo.csv"
    if ndvi.exists():
        nd = {int(r["safra"]): r for r in csv.DictReader(open(ndvi))}
        extra["NDVI MODIS jan (anomalia < 1º quartil, 2001+)"] = {a for a in nd if nd[a]["marca"] == "1"}
    svg("B5-1 · Milho em São Miguel do Oeste: anos de perda e o que cada regra marcou",
        rel, 0.70,
        {"Laudo: balanço hídrico NASA POWER (y < 0,70)": {a for a in anos if float(ind[a]["y_mun"]) < 0.70},
         "Base: chuva out-fev no 1º quartil": {a for a in anos if ch[a] < q1}, **extra},
        "grafico_b5_1_laudo.svg", "Barras: rendimento do IBGE/PAM em % da tendência 1990-2024")
    svg("B5-2 · Alerta até o dia 80 (plantio em 1º/out) contra o olho do agricultor",
        rel, 0.70,
        {"Alerta do modelo (água útil < 40% por 10 dias, dias 45-80)": {a for a in anos if ind[a]["alerta_dia"]},
         "Olho do agricultor (15 dias seguidos < 5 mm)": {a for a in anos if ind[a]["olho_dia"]}},
        "grafico_b5_2_alerta.svg", "Barras: rendimento do IBGE/PAM em % da tendência 1990-2024")
    ce = {int(r["ano"]): r for r in csv.DictReader(open(AQUI / "indicadores_cebola_itu.csv"))}
    relc = {a: float(ce[a]["pct_tendencia"]) for a in ce}
    sq = sorted(int(ce[a]["semanas_risco"]) for a in ce)[(3 * len(ce)) // 4]
    cq = sorted(float(ce[a]["chuva_ago_nov"]) for a in ce)[(3 * len(ce)) // 4]
    svg("B5-3 · Cebola em Ituporanga: semanas úmidas (ago-nov) e anos de quebra",
        relc, 0.80,
        {"Painel: semanas de risco no quartil de cima": {a for a in ce if int(ce[a]["semanas_risco"]) >= sq},
         "Base: chuva ago-nov no quartil de cima": {a for a in ce if float(ce[a]["chuva_ago_nov"]) >= cq}},
        "grafico_b5_3_cebola.svg", "Barras: rendimento do IBGE/PAM em % da tendência 1990-2024")
