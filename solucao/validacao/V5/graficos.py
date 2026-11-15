"""V5 · gráficos SVG (sem bibliotecas)."""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import motor as M
AQUI = Path(__file__).resolve().parent
R = json.load(open(AQUI / "resultado.json")); X = json.load(open(AQUI / "resultado_extra.json"))
LOCS = [l for l in R if l != "sintese"]
FONT = "font-family='Helvetica,Arial,sans-serif'"

# ---- 1. barras: rho por município x cultura, modelo e chuva bruta ----
W, H, ml, mt = 900, 520, 170, 50
parts = [f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 {W} {H}' {FONT} font-size='12'><rect width='{W}' height='{H}' fill='#fff'/>",
         "<text x='20' y='24' font-size='15' font-weight='bold'>Spearman do balanço hídrico contra a PAM (1985-2025), Semiárido</text>",
         "<text x='20' y='42' fill='#555'>Azul: balanço hídrico (risco.py). Cinza: chuva bruta da estação. Linhas: SC (0,28) e meta (0,40).</text>"]
x0, x1 = ml, W - 30
sx = lambda v: x0 + (v + 0.2) / 1.0 * (x1 - x0)
for v in (0, 0.2, 0.4, 0.6, 0.8):
    parts.append(f"<line x1='{sx(v)}' y1='{mt+10}' x2='{sx(v)}' y2='{H-30}' stroke='#ddd'/><text x='{sx(v)}' y='{H-14}' text-anchor='middle' fill='#555'>{v:.1f}</text>")
parts.append(f"<line x1='{sx(0.28)}' y1='{mt+10}' x2='{sx(0.28)}' y2='{H-30}' stroke='#c0392b' stroke-dasharray='4 3'/><text x='{sx(0.28)+3}' y='{mt+22}' fill='#c0392b'>SC 0,28</text>")
parts.append(f"<line x1='{sx(0.40)}' y1='{mt+10}' x2='{sx(0.40)}' y2='{H-30}' stroke='#2e7d32' stroke-dasharray='4 3'/><text x='{sx(0.40)+3}' y='{mt+22}' fill='#2e7d32'>meta 0,40</text>")
y = mt + 40; rowh = (H - 30 - y) / (len(LOCS) * 2)
for l in LOCS:
    for c in ("milho", "feijao"):
        p = R[l][c]["chuva"]["principal"]
        parts.append(f"<text x='{ml-8}' y='{y+rowh*0.55:.0f}' text-anchor='end'>{M.LOCAIS[l]['nome']} · {c}</text>")
        parts.append(f"<rect x='{sx(0)}' y='{y+1:.0f}' width='{max(0.5, sx(p['rho'])-sx(0)):.0f}' height='{rowh*0.45:.0f}' fill='#1f6fb2'/>")
        parts.append(f"<rect x='{sx(0)}' y='{y+rowh*0.47:.0f}' width='{max(0.5, sx(p['rho_chuva'])-sx(0)):.0f}' height='{rowh*0.35:.0f}' fill='#aaa'/>")
        parts.append(f"<text x='{sx(max(p['rho'], p['rho_chuva']))+4:.0f}' y='{y+rowh*0.45:.0f}' fill='#222'>{p['rho']:+.2f}</text>")
        y += rowh
parts.append("</svg>")
(AQUI / "v5_rho_por_municipio.svg").write_text("".join(parts))

# ---- 2. Garantia-Safra x modelo (média CE/PE/PB) ----
t = X["garantia_safra_vs_regiao"]["tabela"]
W, H, ml, mt = 900, 420, 60, 60
parts = [f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 {W} {H}' {FONT} font-size='12'><rect width='{W}' height='{H}' fill='#fff'/>",
         "<text x='20' y='24' font-size='15' font-weight='bold'>Garantia-Safra x balanço hídrico, por ano de colheita</text>",
         "<text x='20' y='42' fill='#555'>Barras: parte dos municípios aderidos com perda comprovada (MDA/SPA). Linha azul: rendimento simulado médio de 6 municípios CE/PE/PB.</text>"]
n = len(t); bw = (W - ml - 30) / n
sy = lambda v: H - 40 - v * (H - 40 - mt - 10)
for v in (0, 0.25, 0.5, 0.75, 1.0):
    parts.append(f"<line x1='{ml}' y1='{sy(v)}' x2='{W-20}' y2='{sy(v)}' stroke='#e5e5e5'/><text x='{ml-6}' y='{sy(v)+4}' text-anchor='end' fill='#555'>{v:.2f}</text>")
pts = []
for i, r in enumerate(t):
    x = ml + i * bw
    parts.append(f"<rect x='{x+4:.0f}' y='{sy(r['gs']):.0f}' width='{bw-8:.0f}' height='{H-40-sy(r['gs']):.0f}' fill='#e0a458'/>")
    parts.append(f"<text x='{x+bw/2:.0f}' y='{H-24}' text-anchor='middle' fill='#555'>{r['ano']}</text>")
    pts.append(f"{x+bw/2:.0f},{sy(min(1.0, r['y_mod'])):.0f}")
parts.append(f"<polyline points='{' '.join(pts)}' fill='none' stroke='#1f6fb2' stroke-width='2.5'/>")
for p in pts: parts.append(f"<circle cx='{p.split(',')[0]}' cy='{p.split(',')[1]}' r='3.5' fill='#1f6fb2'/>")
g = X["garantia_safra_vs_regiao"]
parts.append(f"<text x='{ml}' y='{H-6}' fill='#333'>Spearman modelo x Garantia-Safra = {g['rho_modelo_vs_gs']:+.2f} (n=16); PAM = {g['rho_pam_vs_gs']:+.2f}; chuva bruta = {g['rho_chuva_vs_gs']:+.2f}</text>")
parts.append("</svg>")
(AQUI / "v5_garantia_safra.svg").write_text("".join(parts))

# ---- 3. Quixadá milho: modelo x PAM por ano ----
t = {a["ano"]: a for a in R["quixada"]["milho"]["chuva"]["anos"]}
anos = sorted(a for a in t if t[a]["pam_rel"] is not None)
W, H, ml, mt = 900, 380, 50, 60
parts = [f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 {W} {H}' {FONT} font-size='12'><rect width='{W}' height='{H}' fill='#fff'/>",
         "<text x='20' y='24' font-size='15' font-weight='bold'>Quixadá, milho: rendimento simulado x PAM (relativo à mediana móvel)</text>",
         "<text x='20' y='42' fill='#555'>Azul: simulado (0-1). Laranja: PAM / mediana de 9 anos (cortado em 2). Anos de seca em faixa.</text>"]
bw = (W - ml - 20) / len(anos); sy = lambda v: H - 40 - min(v, 2.0) / 2.0 * (H - 40 - mt)
for i, a in enumerate(anos):
    x = ml + i * bw
    if a in (1993, 1998, 2010, 2012, 2013, 2014, 2015, 2016, 2017, 2023): parts.append(f"<rect x='{x:.0f}' y='{mt}' width='{bw:.0f}' height='{H-40-mt}' fill='#f3e1e1'/>")
    parts.append(f"<rect x='{x+1:.0f}' y='{sy(t[a]['pam_rel']):.0f}' width='{bw/2-1:.0f}' height='{H-40-sy(t[a]['pam_rel']):.0f}' fill='#e0a458'/>")
    parts.append(f"<rect x='{x+bw/2:.0f}' y='{sy(t[a]['y_mod']*2):.0f}' width='{bw/2-1:.0f}' height='{H-40-sy(t[a]['y_mod']*2):.0f}' fill='#1f6fb2'/>")
    if a % 4 == 1: parts.append(f"<text x='{x+bw/2:.0f}' y='{H-24}' text-anchor='middle' fill='#555'>{a}</text>")
parts.append(f"<text x='{ml}' y='{H-6}' fill='#333'>ρ = {R['quixada']['milho']['chuva']['principal']['rho']:+.2f} (azul em escala 0-1 desenhado na altura 0-2). Faixas: 1993, 1998, 2010, 2012-2017, 2023.</text></svg>")
(AQUI / "v5_quixada_milho.svg").write_text("".join(parts))
print("ok")
