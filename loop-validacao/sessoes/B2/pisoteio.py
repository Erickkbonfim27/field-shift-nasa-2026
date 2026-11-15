"""B2-2: calendário de pisoteio em São Miguel do Oeste (NASA POWER GWETTOP).

Conta dias de risco de compactação (GWETTOP >= limiar) no inverno (mai-set),
compara com a regra só de chuva e testa o efeito no rendimento do milho (IBGE PAM)
da safra seguinte. Gera pisoteio_resultado.json e pisoteio.svg.
  python3 pisoteio.py
"""
import json, os
import numpy as np
from scipy import stats

AQUI = os.path.dirname(os.path.abspath(__file__))
P = json.load(open(os.path.join(AQUI, "..", "..", "dados", "power_sao_miguel_do_oeste.json")))["properties"]["parameter"]
datas = sorted(P["GWETTOP"])
gw = np.array([P["GWETTOP"][d] for d in datas], float)
ch = np.array([P["PRECTOTCORR"][d] for d in datas], float)
gw[gw < 0] = np.nan
ch[ch < 0] = np.nan
ano = np.array([int(d[:4]) for d in datas])
mes = np.array([int(d[4:6]) for d in datas])
inv = (mes >= 5) & (mes <= 9)

# regra só de chuva: soma de 3 dias (hoje e 2 anteriores) >= 30 mm
ch3 = np.convolve(np.nan_to_num(ch), np.ones(3), mode="full")[: len(ch)]
risco_chuva = ch3 >= 30

ANOS = list(range(1985, 2025))
res = {"limiares": {}}
for lim in (0.75, 0.80, 0.85):
    risco = gw >= lim
    dias = np.array([risco[inv & (ano == a)].sum() for a in ANOS])
    dias_ch = np.array([risco_chuva[inv & (ano == a)].sum() for a in ANOS])
    m = inv & (ano >= 1985) & (ano <= 2024)
    a_e_b = (risco & risco_chuva)[m].sum()
    so_power = (risco & ~risco_chuva)[m].sum()
    so_chuva = (~risco & risco_chuva)[m].sum()
    discord = so_power / max(risco[m].sum(), 1)
    res["limiares"][lim] = dict(
        media=float(dias.mean()), dp=float(dias.std(ddof=1)), cv=float(dias.std(ddof=1) / dias.mean()) if dias.mean() > 0 else None,
        p30=float(np.percentile(dias, 70)), min=int(dias.min()), max=int(dias.max()),
        dias_por_ano=dict(zip(ANOS, dias.tolist())), dias_chuva_por_ano=dict(zip(ANOS, dias_ch.tolist())),
        concordam=int(a_e_b), so_power=int(so_power), so_chuva=int(so_chuva),
        frac_power_sem_chuva=float(discord), frac_dias_inverno_risco=float(risco[m].mean()),
        corr_power_chuva_anual=float(stats.spearmanr(dias, dias_ch)[0]),
    )

# rendimento do milho (PAM, kg/ha), safra colhida no ano t+1
pam = json.load(open(os.path.join(AQUI, "dados", "pam1612_milho_smo.json")))[1:]
rend = {int(r["D3N"]): float(r["V"]) for r in pam if r["D2C"] == "112" and r["V"] not in ("...", "-", "X", "..")}
# chuva nov(t)-fev(t+1)
def chuva_verao(t):
    sel = ((ano == t) & (mes >= 11)) | ((ano == t + 1) & (mes <= 2))
    return np.nansum(ch[sel])

def parcial_spearman(x, y, z):
    rx, ry, rz = [stats.rankdata(v) for v in (x, y, z)]
    ex = rx - np.polyval(np.polyfit(rz, rx, 1), rz)
    ey = ry - np.polyval(np.polyfit(rz, ry, 1), rz)
    r, p = stats.pearsonr(ex, ey)
    return float(r), float(p)

res["milho"] = {}
for lim in (0.75, 0.80, 0.85):
    dpa = res["limiares"][lim]["dias_por_ano"]
    ts = [t for t in ANOS if (t + 1) in rend and t + 1 <= 2025]
    y = np.array([rend[t + 1] for t in ts])
    tt = np.array(ts, float)
    y_res = y - np.polyval(np.polyfit(tt, y, 1), tt)  # sem tendência
    x = np.array([dpa[t] for t in ts], float)
    xc = np.array([res["limiares"][lim]["dias_chuva_por_ano"][t] for t in ts], float)
    z = np.array([chuva_verao(t) for t in ts])
    rp, pp = parcial_spearman(x, y_res, z)
    rc, pc = parcial_spearman(xc, y_res, z)
    rz = stats.spearmanr(z, y_res)
    res["milho"][lim] = dict(n=len(ts), parcial_power=rp, p_power=pp, parcial_chuva=rc, p_chuva=pc,
                             spearman_chuva_verao_rend=float(rz[0]), p_chuva_verao=float(rz[1]))
res["milho_anos"] = {t: rend.get(t + 1) for t in ANOS}
json.dump(res, open(os.path.join(AQUI, "pisoteio_resultado.json"), "w"), indent=1, ensure_ascii=False)

# gráfico SVG: dias de risco por inverno (0,80) e regra de chuva
L = res["limiares"][0.80]
W, H, m0 = 760, 320, 50
mx = max(max(L["dias_por_ano"].values()), max(L["dias_chuva_por_ano"].values())) + 5
bw = (W - 2 * m0) / len(ANOS)
s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" font-family="sans-serif" font-size="11">',
     f'<rect width="{W}" height="{H}" fill="white"/>',
     f'<text x="{m0}" y="20" font-size="13">São Miguel do Oeste: dias de risco de pisoteio por inverno (mai–set), NASA POWER</text>']
for i, a in enumerate(ANOS):
    v = L["dias_por_ano"][a]; vc = L["dias_chuva_por_ano"][a]
    x = m0 + i * bw
    h = (H - 2 * m0) * v / mx
    s.append(f'<rect x="{x+1:.1f}" y="{H-m0-h:.1f}" width="{bw-2:.1f}" height="{h:.1f}" fill="#3b6ea5"/>')
    hc = (H - 2 * m0) * vc / mx
    s.append(f'<circle cx="{x+bw/2:.1f}" cy="{H-m0-hc:.1f}" r="2.5" fill="#d9822b"/>')
    if a % 5 == 0:
        s.append(f'<text x="{x:.1f}" y="{H-m0+14}">{a}</text>')
ym = H - m0 - (H - 2 * m0) * L["media"] / mx
s.append(f'<line x1="{m0}" x2="{W-m0}" y1="{ym:.1f}" y2="{ym:.1f}" stroke="#555" stroke-dasharray="4 3"/>')
s.append(f'<text x="{W-m0-150}" y="{ym-4:.1f}">média {L["media"]:.0f} dias (calendário fixo)</text>')
s.append(f'<rect x="{m0}" y="{H-18}" width="10" height="10" fill="#3b6ea5"/><text x="{m0+14}" y="{H-9}">GWETTOP ≥ 0,80</text>')
s.append(f'<circle cx="{m0+150}" cy="{H-13}" r="3" fill="#d9822b"/><text x="{m0+158}" y="{H-9}">regra só de chuva (≥ 30 mm em 3 dias)</text>')
s.append("</svg>")
open(os.path.join(AQUI, "pisoteio.svg"), "w").write("\n".join(s))
print(json.dumps({k: {kk: vv for kk, vv in v.items() if "por_ano" not in kk} for k, v in res["limiares"].items()}, indent=1))
print(json.dumps(res["milho"], indent=1))
