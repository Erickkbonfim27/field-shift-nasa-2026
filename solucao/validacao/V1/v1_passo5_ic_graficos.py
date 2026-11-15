#!/usr/bin/env python3
"""Passo 5: intervalo de confiança por evento climático (bootstrap por ANO de safra: sorteia anos com
reposição e leva todas as regiões daquele ano juntas) e gráficos SVG."""
import json
from v1_comum import *
from v1_passo4_extensao import FIXA, neutra, LIM_N as LIM_EXT  # noqa  (o import reexecuta o passo 4; resultados iguais, sementes fixas)

orig = json.load(open(V1 / "tabela_original.json"))
ext = json.load(open(V1 / "tabela_extensao.json"))
ata = json.load(open(V1 / "resultado_ataques.json"))
LIM_O = {}
for t in orig: LIM_O.setdefault((t["cultura"], t["ponto"]), []).append(t["ind"])
LIM_O = {k: (q10 if k[0] == "milho" else q90)(v) for k, v in LIM_O.items()}


def neutra_o(cult):
    return (lambda r: r["ind"] <= LIM_O[(cult, r["ponto"])]) if cult == "milho" else (lambda r: r["ind"] >= LIM_O[(cult, r["ponto"])])


def boot_ano(rows, fn, n=5000, seed=11, corte=0.85):
    rnd = random.Random(seed)
    por_ano = {}
    for r in rows: por_ano.setdefault(r["ano"], []).append((fn(r), r["rel"] <= corte))
    anos = sorted(por_ano)
    precs, lifts, vazio = [], [], 0
    def est(sample):
        al = [b for a in sample for (x, b) in por_ano[a] if x]
        tot = [b for a in sample for (x, b) in por_ano[a]]
        if not al: return None
        p = sum(al) / len(al); base = sum(tot) / len(tot)
        return p, p - base
    obs = est(anos)
    for _ in range(n):
        s = [rnd.choice(anos) for _ in anos]
        e = est(s)
        if e is None: vazio += 1; continue
        precs.append(e[0]); lifts.append(e[1])
    precs.sort(); lifts.sort()
    q = lambda v, f: v[int(f * (len(v) - 1))]
    return dict(precisao=round(obs[0], 3), ic95_precisao=[round(q(precs, .025), 2), round(q(precs, .975), 2)],
                lift=round(obs[1], 3), ic95_lift=[round(q(lifts, .025), 2), round(q(lifts, .975), 2)],
                p_lift_menor_ou_igual_0=round(sum(1 for x in lifts if x <= 0) / len(lifts), 3),
                reamostras_sem_alerta=vazio)


casos = []
for cult in ("milho", "cebola"):
    fora = [t for t in orig if t["cultura"] == cult and t["papel"] == "fora B3-3"]
    g_ext = [t for t in ext if t["cultura"] == cult]
    g_ext100 = [t for t in g_ext if t["area"] >= 100]
    casos += [
        (cult, "B3-3 como publicado (regra fixa, regiões vizinhas)", fora, FIXA[cult]),
        (cult, "Extensão, células novas, regra fixa", g_ext, FIXA[cult]),
        (cult, "Extensão, células novas, 10% extremos da célula", g_ext, neutra(cult)),
    ]
    if cult == "cebola":
        casos += [(cult, "Extensão cebola ≥ 100 ha, regra fixa", g_ext100, FIXA[cult]),
                  (cult, "Extensão cebola ≥ 100 ha, 10% extremos", g_ext100, neutra(cult))]
    todos = [t for t in orig if t["cultura"] == cult] + g_ext
    LIM_ALL = dict(LIM_O); LIM_ALL.update({k: v["ind"] for k, v in LIM_EXT.items()})
    fn_all = (lambda r, L=LIM_ALL: r["ind"] <= L[("milho", r["ponto"])]) if cult == "milho" else (lambda r, L=LIM_ALL: r["ind"] >= L[("cebola", r["ponto"])])
    casos += [(cult, "SC inteira (amostra + B3-3 + novas), regra fixa", todos, FIXA[cult]),
              (cult, "SC inteira, 10% extremos da célula", todos, fn_all)]

res = []
for cult, nome, rows, fn in casos:
    al = [r for r in rows if fn(r)]
    base = sum(r["rel"] <= 0.85 for r in rows) / len(rows)
    b = boot_ano(rows, fn)
    R = resumo(aplica(rows, fn))
    res.append(dict(cultura=cult, caso=nome, anos_regiao=len(rows), regioes=len({r["regiao"] for r in rows}),
                    alertas=len(al), acertos=sum(r["rel"] <= 0.85 for r in al), taxa_base=round(base, 3),
                    eventos=R["eventos"], eventos_acerto=R["eventos_acerto"], ic95_evento_wilson=R["ic95_evento"], **b))
    print(cult, "|", nome, "|", res[-1])
json.dump(res, open(V1 / "resultado_ic_por_evento.json", "w"), ensure_ascii=False, indent=1)

# ---------------- gráficos ----------------
ESTILO = """<style>
svg{--sf:#fcfcfb;--t1:#0b0b0b;--t2:#52514e;--grid:#e4e3df;--s1:#2a78d6;--s2:#eb6834;--neu:#8a8984}
@media (prefers-color-scheme: dark){svg{--sf:#1a1a19;--t1:#f0efec;--t2:#c3c2b7;--grid:#3a3a37;--s1:#3987e5;--s2:#d95926;--neu:#9a9990}}
text{fill:var(--t1);font-family:system-ui,sans-serif;font-size:12px}.t2{fill:var(--t2)}.tt{font-size:15px;font-weight:600}
</style>"""


def svg_sens(caminho):
    W, H, m = 860, 400, 56
    pw = (W - 3 * m) / 2
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}">', ESTILO,
         f'<rect width="{W}" height="{H}" fill="var(--sf)"/>',
         f'<text x="{m}" y="24" class="tt">B3-3: fração dos alertas em ano ruim conforme o limiar (regiões vizinhas de B3-3)</text>',
         f'<text x="{m}" y="42" class="t2">Linha azul = acerto dos alertas; tracejado cinza = taxa-base; laranja = limiar da ficha. Número = alertas.</text>']
    for i, (cult, lab, lim0) in enumerate((("milho", "Limiar do ISNA (alerta se ISNA &lt; limiar)", 0.75),
                                           ("cebola", "Limiar do excedente set–nov, mm (alerta se ≥)", 360))):
        sens = ata[cult]["A2_sensibilidade"]
        x0 = m + i * (pw + m); y0, y1 = 84, H - m
        xs = [d["limiar"] for d in sens]
        X = lambda v: x0 + (v - min(xs)) / (max(xs) - min(xs)) * pw
        Y = lambda v: y1 - v * (y1 - y0)
        s.append(f'<text x="{x0 + pw}" y="{y0 - 14}" text-anchor="end" class="tt">{cult.capitalize()}</text>')
        for v in (0, .25, .5, .75, 1):
            s.append(f'<line x1="{x0}" x2="{x0 + pw}" y1="{Y(v)}" y2="{Y(v)}" stroke="var(--grid)"/>')
            s.append(f'<text x="{x0 - 6}" y="{Y(v) + 4}" text-anchor="end" class="t2">{v:.0%}</text>')
        for d in sens[::2] if cult == "milho" else sens[::2]:
            s.append(f'<text x="{X(d["limiar"])}" y="{y1 + 16}" text-anchor="middle" class="t2">{d["limiar"]}</text>')
        s.append(f'<text x="{x0 + pw / 2}" y="{y1 + 34}" text-anchor="middle" class="t2">{lab}</text>')
        b = sens[0]["taxa_base"]
        s.append(f'<line x1="{x0}" x2="{x0 + pw}" y1="{Y(b)}" y2="{Y(b)}" stroke="var(--neu)" stroke-dasharray="5,4" stroke-width="2"/>')
        s.append(f'<text x="{x0 + pw}" y="{Y(b) - 5}" text-anchor="end" class="t2">taxa-base {b:.0%}</text>')
        s.append(f'<line x1="{X(lim0)}" x2="{X(lim0)}" y1="{y0}" y2="{y1}" stroke="var(--s2)" stroke-width="2"/>')
        pts = " ".join(f'{X(d["limiar"]):.1f},{Y(d["precisao"]):.1f}' for d in sens)
        s.append(f'<polyline points="{pts}" fill="none" stroke="var(--s1)" stroke-width="2"/>')
        for d in sens:
            s.append(f'<circle cx="{X(d["limiar"]):.1f}" cy="{Y(d["precisao"]):.1f}" r="4.5" fill="var(--s1)" stroke="var(--sf)" stroke-width="2"><title>limiar {d["limiar"]}: {d["acertos"]}/{d["alertas"]} alertas em ano ruim; {d["eventos"]} eventos; passa critério B3-3: {d["passa"]}</title></circle>')
            s.append(f'<text x="{X(d["limiar"]):.1f}" y="{Y(d["precisao"]) - 9:.1f}" text-anchor="middle" class="t2" font-size="10">{d["alertas"]}</text>')
    s.append("</svg>")
    Path(caminho).write_text("\n".join(s))


def svg_forest(caminho):
    W = 980; linha = 30; m_esq = 400; topo = 70
    H = topo + linha * len(res) + 70
    X = lambda v: m_esq + v * (W - m_esq - 130)
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}">', ESTILO,
         f'<rect width="{W}" height="{H}" fill="var(--sf)"/>',
         f'<text x="16" y="24" class="tt">Acerto dos alertas de ano extremo, com IC 95% por evento (bootstrap por ano de safra)</text>',
         f'<text x="16" y="42" class="t2">Ponto azul = fração dos alertas em ano ruim; barra = IC 95%; traço laranja = taxa-base (alertar ao acaso).</text>']
    for v in (0, .25, .5, .75, 1):
        s.append(f'<line x1="{X(v)}" x2="{X(v)}" y1="{topo - 8}" y2="{topo + linha * len(res)}" stroke="var(--grid)"/>')
        s.append(f'<text x="{X(v)}" y="{topo + linha * len(res) + 16}" text-anchor="middle" class="t2">{v:.0%}</text>')
    for i, r in enumerate(res):
        y = topo + i * linha + linha / 2
        s.append(f'<text x="16" y="{y + 4}">{r["cultura"]}: {r["caso"]}</text>')
        lo, hi = r["ic95_precisao"]
        s.append(f'<line x1="{X(lo)}" x2="{X(hi)}" y1="{y}" y2="{y}" stroke="var(--s1)" stroke-width="2"/>')
        s.append(f'<line x1="{X(r["taxa_base"])}" x2="{X(r["taxa_base"])}" y1="{y - 9}" y2="{y + 9}" stroke="var(--s2)" stroke-width="3"/>')
        s.append(f'<circle cx="{X(r["precisao"])}" cy="{y}" r="5" fill="var(--s1)" stroke="var(--sf)" stroke-width="2"><title>{r["acertos"]}/{r["alertas"]} alertas em ano ruim; base {r["taxa_base"]:.0%}; IC {lo:.0%}–{hi:.0%}; {r["eventos"]} eventos</title></circle>')
        s.append(f'<text x="{W - 8}" y="{y + 4}" text-anchor="end" class="t2" font-size="11">{r["acertos"]}/{r["alertas"]} · {r["eventos"]} ev.</text>')
    s.append(f'<text x="{X(0.5)}" y="{H - 18}" text-anchor="middle" class="t2">fração dos alertas que caíram em ano ruim (rendimento ≤ 85% da mediana, IBGE PAM)</text>')
    s.append("</svg>")
    Path(caminho).write_text("\n".join(s))


def svg_disp(caminho, cult, rows, lim, xlabel):
    """Dispersão: indicador x rendimento relativo nas células novas. Laranja = ano ruim."""
    W, H, m = 820, 460, 60
    xs = [r["ind"] for r in rows]; ys = [r["rel"] for r in rows]
    x0, x1 = min(xs), max(xs); y0, y1 = 0.3, max(1.8, max(ys))
    X = lambda v: m + (v - x0) / (x1 - x0) * (W - 2 * m)
    Y = lambda v: H - m - (v - y0) / (y1 - y0) * (H - 2 * m - 30)
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}">', ESTILO,
         f'<rect width="{W}" height="{H}" fill="var(--sf)"/>',
         f'<text x="{m}" y="24" class="tt">Células novas do POWER ({cult}): indicador x rendimento relativo, {len({r["regiao"] for r in rows})} microrregiões</text>',
         f'<text x="{m}" y="42" class="t2">Laranja = ano ruim (≤ 0,85). Linha vertical = limiar fixo de B3-3. Passe o mouse para ver região e ano.</text>']
    for v in (0.5, 0.85, 1.0, 1.5):
        s.append(f'<line x1="{m}" x2="{W - m}" y1="{Y(v)}" y2="{Y(v)}" stroke="var(--grid)" {"stroke-dasharray=\"5,4\"" if v == 0.85 else ""}/>')
        s.append(f'<text x="{m - 6}" y="{Y(v) + 4}" text-anchor="end" class="t2">{v:.2f}</text>')
    for t in range(6):
        v = x0 + t * (x1 - x0) / 5
        s.append(f'<text x="{X(v)}" y="{H - m + 16}" text-anchor="middle" class="t2">{v:.2f}</text>' if cult == "milho" else f'<text x="{X(v)}" y="{H - m + 16}" text-anchor="middle" class="t2">{v:.0f}</text>')
    s.append(f'<text x="{W / 2}" y="{H - 18}" text-anchor="middle" class="t2">{xlabel}</text>')
    s.append(f'<text x="16" y="{H / 2}" text-anchor="middle" class="t2" transform="rotate(-90 16 {H / 2})">rendimento / mediana t±3 (IBGE PAM)</text>')
    s.append(f'<line x1="{X(lim)}" x2="{X(lim)}" y1="60" y2="{H - m}" stroke="var(--t2)" stroke-width="2"/>')
    for r in rows:
        ruim = r["rel"] <= 0.85
        s.append(f'<circle cx="{X(r["ind"]):.1f}" cy="{Y(r["rel"]):.1f}" r="{4.5 if ruim else 3.5}" fill="{"var(--s2)" if ruim else "var(--neu)"}" fill-opacity="{1 if ruim else .55}" stroke="var(--sf)" stroke-width="1.5"><title>{r["regiao"]} {r["ano"]}: indicador {r["ind"]}, rendimento relativo {r["rel"]:.2f}</title></circle>')
    s.append("</svg>")
    Path(caminho).write_text("\n".join(s))


svg_sens(V1 / "v1_sensibilidade_limiar_b33.svg")
svg_forest(V1 / "v1_acerto_ic_por_evento.svg")
svg_disp(V1 / "v1_extensao_milho.svg", "milho", [t for t in ext if t["cultura"] == "milho"], 0.75,
         "ISNA do milho de 20/set a 10/jan (NASA POWER, balanço FAO-56)")
svg_disp(V1 / "v1_extensao_cebola.svg", "cebola", [t for t in ext if t["cultura"] == "cebola"], 360,
         "Excedente hídrico de 1/set a 30/nov, mm (NASA POWER, balanço FAO-56)")
print("svg ok")
