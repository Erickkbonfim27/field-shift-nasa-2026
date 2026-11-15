#!/usr/bin/env python3
"""B5-4: boletim mensal de estiagem (GWETROOT, NASA POWER) contra os decretos de emergência.

Mês em alerta: GWETROOT médio do mês < média - 1 DP daquele mês (1991-2020).
Boletim: 2 meses seguidos em alerta (sai no fim do 2º mês).
Base: chuva de 3 meses (SPI-3 simplificado) < média - 1 DP, 2 meses seguidos.
Uso: python3 boletim_estiagem.py  (lê decretos_smo.csv: ano,data_decreto)
"""
import json, csv, statistics as st, datetime as dt, calendar
from pathlib import Path

AQUI = Path(__file__).resolve().parent
P = json.load(open(AQUI.parent.parent / "dados/power_sao_miguel_do_oeste.json"))["properties"]["parameter"]

mes = {}   # (ano, m) -> (gw médio, chuva do mês)
for k, v in P["GWETROOT"].items():
    a, m = int(k[:4]), int(k[4:6])
    g = mes.setdefault((a, m), [[], 0.0]); g[0].append(v); g[1] += max(0, P["PRECTOTCORR"][k])
gw = {km: st.mean(v[0]) for km, v in mes.items()}
ch = {km: v[1] for km, v in mes.items()}
ch3 = {}
for (a, m) in ch:
    ks = [((a * 12 + m - 1 - i) // 12, (a * 12 + m - 1 - i) % 12 + 1) for i in range(3)]
    if all(x in ch for x in ks): ch3[(a, m)] = sum(ch[x] for x in ks)


def alertas(serie):
    ref = {m: [serie[(a, m)] for a in range(1991, 2021) if (a, m) in serie] for m in range(1, 13)}
    lim = {m: st.mean(v) - st.pstdev(v) for m, v in ref.items()}
    al = {km: serie[km] < lim[km[1]] for km in serie}
    bol = []
    for (a, m) in sorted(serie):
        prev = ((a * 12 + m - 2) // 12, (a * 12 + m - 2) % 12 + 1)
        if al[(a, m)] and al.get(prev):
            bol.append(dt.date(a, m, calendar.monthrange(a, m)[1]))
    return bol


bol_gw, bol_ch = alertas(gw), alertas(ch3)
anos = range(2005, 2026)   # o Atlas Digital de Desastres cobre 2005-2025
dec = {}
arq = AQUI / "decretos_smo.csv"
if arq.exists():
    for r in csv.DictReader(open(arq)):
        dec.setdefault(int(r["ano"]), []).append(dt.date.fromisoformat(r["data_decreto"]))
print("Boletins GWETROOT (fim do mês):", [d.isoformat()[:7] for d in bol_gw if d.year >= 2003])
print("Boletins chuva 3 meses:", [d.isoformat()[:7] for d in bol_ch if d.year >= 2003])
if dec:
    alvo = set(dec)
    for nome, bol in [("GWETROOT (NASA)", bol_gw), ("chuva 3 meses (base)", bol_ch)]:
        marc = {d.year for d in bol if d.year in anos}
        tp, fp = len(marc & alvo), len(marc - alvo)
        antes = []
        for a in sorted(marc & alvo):
            pri = min(d for d in bol if d.year == a); dd = min(dec[a])
            antes.append((a, (dd - pri).days))
        print(f"{nome:22s} marca {len(marc):2d} acertos {tp}/{len(alvo)} falsos {fp} precisão {tp/max(1,len(marc)):.0%} "
              f"| dias do 1º boletim até o decreto: {antes} | marcados {sorted(marc)}")
    # Sensibilidade (depois do critério): casar por evento, boletim de 4 meses antes até 2 meses depois do decreto
    for nome, bol in [("GWETROOT (NASA)", bol_gw), ("chuva 3 meses (base)", bol_ch)]:
        ev = []
        for a, ds in sorted(dec.items()):
            d = min(ds); perto = [b for b in bol if -122 <= (b - d).days <= 61]
            ev.append((d.isoformat(), (d - min(perto)).days if perto else None))
        acert = sum(1 for _, x in ev if x is not None)
        print(f"  por evento, {nome:22s}: {acert}/{len(ev)} decretos com boletim por perto | dias de antecedência: {ev}")
    print("Anos com decreto:", {a: [d.isoformat() for d in v] for a, v in sorted(dec.items())})


# ---- gráfico SVG: linha do tempo 2005-2025 ----
if dec:
    W, H, ml = 900, 200, 150
    x = lambda d: ml + (d.year - 2005 + (d.month - 0.5) / 12) / 21 * (W - ml - 20)
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" font-family="sans-serif" font-size="11">',
         f'<rect width="{W}" height="{H}" fill="#fff"/>',
         '<text x="10" y="20" font-size="14" font-weight="bold">B5-4 · São Miguel do Oeste: boletins de estiagem e decretos (2005-2025)</text>']
    for y in range(2005, 2026, 5):
        xx = x(dt.date(y, 1, 1)); o.append(f'<line x1="{xx}" x2="{xx}" y1="35" y2="160" stroke="#eee"/><text x="{xx}" y="175" text-anchor="middle">{y}</text>')
    for lin, (nome, bol, cor) in enumerate([("GWETROOT (NASA)", bol_gw, "#2471a3"), ("Chuva 3 meses (base)", bol_ch, "#7f8c8d")]):
        yy = 50 + 40 * lin
        o.append(f'<text x="10" y="{yy+10}">{nome}</text>')
        for b in bol:
            if b.year >= 2005: o.append(f'<rect x="{x(b)-3}" y="{yy}" width="6" height="14" fill="{cor}"/>')
    o.append('<text x="10" y="140">Decreto (Atlas S2iD)</text>')
    for a, ds in dec.items():
        for d in ds: o.append(f'<path d="M{x(d)} 128 l6 12 l-12 0 z" fill="#c0392b"/>')
    o.append('<text x="10" y="194" fill="#555">Barras = mês com boletim (2 meses seguidos abaixo de média - 1 DP). Triângulos = registro de estiagem no S2iD.</text></svg>')
    (AQUI / "grafico_b5_4_boletim.svg").write_text("\n".join(o))
