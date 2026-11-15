#!/usr/bin/env python3
"""Gera galeria.html com as fichas e os gráficos de cada sessão do loop.
Rode de novo sempre que as sessões atualizarem: python3 loop-validacao/gerar_galeria.py"""
import re, html, datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
TITULOS = {
    "A1": "Época de plantio", "A2": "Previsibilidade", "A3": "Solo e satélite", "A4": "Rotação e água",
    "A5": "Cobertura e oferta", "B1": "Clima e época (+ controle)", "B2": "Solo e conservação",
    "B3": "Água: seca e excesso", "B4": "Mercado e oferta", "B5": "Persona e canal",
}
CRIT = ["Problema real", "Tamanho do impacto", "Resolve de fato", "Validade", "Muda a decisão",
        "Simples e factível", "Alinhamento com o desafio", "Diferencial", "Cabe no hackathon"]


def nota(txt, k):
    m = re.search(r"\|\s*\**" + re.escape(k) + r"\**\s*\|\s*\**(\d)", txt, re.I)
    return int(m.group(1)) if m else None


def ficha_info(p):
    t = p.read_text(encoding="utf-8")
    titulo = t.splitlines()[0].lstrip("# ").strip()
    m = re.search(r"##\s*5\.\s*Veredito\s*\n+(.+?)(?:\n##|\Z)", t, re.S)
    veredito = re.sub(r"\s+", " ", m.group(1)).strip() if m else "(sem veredito ainda)"
    h = re.search(r"\*\*Hipótese:\*\*\s*(.+)", t)
    notas = {k: nota(t, k) for k in CRIT}
    vals = [v for v in notas.values() if v is not None]
    trava = all((notas[k] or 0) >= 3 for k in ["Problema real", "Resolve de fato", "Validade"])
    return dict(arq=p.name, titulo=titulo, veredito=veredito, hip=h.group(1).strip() if h else "",
                notas=notas, total=sum(vals) if len(vals) == 9 else None, trava=trava)


def esc(s):
    return html.escape(s)


def md_inline(s):
    s = esc(s)
    return re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)


partes = []
resumo = []
for sid, nome in TITULOS.items():
    fichas = sorted((RAIZ / "fichas").glob(f"{sid}-*.md"))
    imgs = sorted([p for p in (RAIZ / "sessoes" / sid).glob("*") if p.suffix.lower() in (".svg", ".png", ".jpg")])
    infos = [ficha_info(f) for f in fichas]
    resumo += [(sid, i) for i in infos]
    cards = ""
    for i in infos:
        cor = "ok" if i["trava"] else "nao"
        chips = "".join(f'<span class="chip {"b" if (v or 0) >= 3 else "r"}" title="{k}">{k.split()[0][:8]} {v if v is not None else "?"}</span>' for k, v in i["notas"].items())
        cards += f"""<article class="ficha {cor}">
          <header><a href="fichas/{esc(i['arq'])}" target="_blank">{esc(i['titulo'])}</a>
          <span class="tot">{i['total'] if i['total'] is not None else '–'}<small>/45</small></span></header>
          <p class="hip">{md_inline(i['hip'][:260])}</p>
          <div class="chips">{chips}</div>
          <p class="ver"><b>{'Passa na trava' if i['trava'] else 'Não passa na trava'}</b> · {md_inline(i['veredito'][:320])}</p>
        </article>"""
    figs = "".join(f'<figure><a href="sessoes/{sid}/{esc(p.name)}" target="_blank"><img loading="lazy" src="sessoes/{sid}/{esc(p.name)}" alt="{esc(p.name)}"></a><figcaption>{esc(p.name)}</figcaption></figure>' for p in imgs)
    partes.append(f"""<section id="{sid}"><h2>{sid} · {esc(nome)} <small>{len(infos)} fichas · {len(imgs)} gráficos</small></h2>
      <div class="fichas">{cards or '<p class="vazio">Nenhuma ficha ainda.</p>'}</div>
      <div class="figs">{figs or '<p class="vazio">Nenhum gráfico ainda.</p>'}</div></section>""")

rank = sorted([r for r in resumo if r[1]["total"] is not None], key=lambda r: (-int(r[1]["trava"]), -r[1]["total"]))
linhas = "".join(f'<tr class="{"ok" if i["trava"] else "nao"}"><td><a href="#{sid}">{sid}</a></td><td><a href="fichas/{esc(i["arq"])}" target="_blank">{esc(i["titulo"])}</a></td><td>{i["notas"]["Problema real"]}</td><td>{i["notas"]["Resolve de fato"]}</td><td>{i["notas"]["Validade"]}</td><td><b>{i["total"]}</b></td><td>{"sim" if i["trava"] else "não"}</td></tr>' for sid, i in rank)

doc = f"""<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Galeria do loop</title><style>
:root{{--f:#f6f4ee;--c:#fff;--t:#1d2a1f;--t2:#5a665c;--l:#d9d6ca;--ok:#3f8f4f;--r:#c0533a;--d:#1f6b4a}}
@media (prefers-color-scheme:dark){{:root:not([data-theme=light]){{--f:#141a15;--c:#1e2620;--t:#eef1ea;--t2:#a5b0a6;--l:#36423a;--ok:#62b873;--r:#e58a52;--d:#62b873}}}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--f);color:var(--t);font:15px/1.5 system-ui,sans-serif}}
main{{max-width:1200px;margin:0 auto;padding:16px}}h1{{font-size:20px;margin:4px 0}}h2{{font-size:17px;border-bottom:2px solid var(--l);padding-bottom:6px;margin-top:34px}}h2 small{{font-weight:400;color:var(--t2);font-size:13px}}
nav{{display:flex;flex-wrap:wrap;gap:6px;margin:10px 0}}nav a{{padding:4px 10px;border:1px solid var(--l);border-radius:99px;text-decoration:none;color:var(--d);background:var(--c)}}
a{{color:var(--d)}}.peq{{color:var(--t2);font-size:13px}}
table{{width:100%;border-collapse:collapse;background:var(--c);font-size:13px}}td,th{{padding:5px 8px;border-bottom:1px solid var(--l);text-align:left}}tr.ok td:first-child{{border-left:4px solid var(--ok)}}tr.nao td:first-child{{border-left:4px solid var(--l)}}
.fichas{{display:grid;grid-template-columns:repeat(auto-fill,minmax(330px,1fr));gap:12px}}
.ficha{{background:var(--c);border:1px solid var(--l);border-left:5px solid var(--l);border-radius:10px;padding:12px}}.ficha.ok{{border-left-color:var(--ok)}}
.ficha header{{display:flex;justify-content:space-between;gap:8px;font-weight:600}}.tot{{font-size:20px;font-weight:800}}.tot small{{font-size:11px;color:var(--t2)}}
.hip{{font-size:13px;color:var(--t2);margin:6px 0}}.ver{{font-size:13px;margin:8px 0 0}}
.chips{{display:flex;flex-wrap:wrap;gap:4px}}.chip{{font-size:11px;padding:1px 6px;border-radius:6px;border:1px solid var(--l)}}.chip.b{{border-color:var(--ok)}}.chip.r{{border-color:var(--r);color:var(--r)}}
.figs{{display:grid;grid-template-columns:repeat(auto-fill,minmax(360px,1fr));gap:12px;margin-top:12px}}
figure{{margin:0;background:#fff;border:1px solid var(--l);border-radius:10px;padding:8px}}figure img{{width:100%;height:auto;display:block}}figcaption{{font-size:11px;color:#555;margin-top:4px}}
.vazio{{color:var(--t2);font-style:italic}}
@media(max-width:600px){{.fichas,.figs{{grid-template-columns:1fr}}}}
</style></head><body><main>
<h1>Galeria do loop de validação</h1>
<p class="peq">Gerado em {datetime.datetime.now():%d/%m/%Y %H:%M}. Rode <code>python3 loop-validacao/gerar_galeria.py</code> para atualizar. "Trava" = nota 3 ou mais em problema real, resolve de fato e validade. Verde = passa na trava. Clique no título para abrir a ficha completa e no gráfico para ampliar.</p>
<nav>{''.join(f'<a href="#{s}">{s} · {n}</a>' for s, n in TITULOS.items())}</nav>
<h2>Placar provisório <small>ordenado por trava e depois por nota total</small></h2>
<table><thead><tr><th>Sessão</th><th>Ficha</th><th>Problema real</th><th>Resolve</th><th>Validade</th><th>Total</th><th>Trava</th></tr></thead><tbody>{linhas}</tbody></table>
{''.join(partes)}
</main></body></html>"""
(RAIZ / "galeria.html").write_text(doc, encoding="utf-8")
print("galeria.html gerada:", len(resumo), "fichas")
