#!/usr/bin/env python3
"""V3-03: pontos de equilíbrio (Ky do sorgo, R), Ky do milho, raiz, ciclo, geada e datas. Não faz parte da grade pré-definida."""
import sys, json
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
import modelo_v3 as V
AQUI = Path(__file__).resolve().parent


def arr(cs):
    return np.array([c[2] for c in cs]).reshape(-1, 5), np.array([c[3] for c in cs]).reshape(-1, 5)


def met(ym, ys, f=0.5, R=0.88):
    tot = ((1 - f) * ym + f * R * ys).ravel(); b = ym.ravel()
    return 100 * (np.percentile(tot, 10) / np.percentile(b, 10) - 1), 100 * (tot.mean() / b.mean() - 1), int((tot < 0.6).sum()), int((b < 0.6).sum())


out = {}
CADS = {"raso_A4_87.5": 87.5, "raso_ZARC_42": 42.0}

# (a) Ky do sorgo de equilíbrio (ganho P10 = 0) e R de equilíbrio (média = 0 e média = -3%)
print("== (a) pontos de equilíbrio")
out["equilibrio"] = {}
for scen in ("A4", "FAO33", "MISTO", "BIOMASSA"):
    for nome, cad in CADS.items():
        ym = arr(V.casos(cad, scen=scen))[0]
        # Ky sorgo multiplicador: varre 0,25 a 4
        ms = np.round(np.arange(0.25, 4.01, 0.25), 2); gs = []
        for m in ms:
            _, ys = arr(V.casos(cad, scen=scen, kym_sorgo=float(m)))
            gs.append(met(ym, ys)[0])
        gs = np.array(gs)
        cruz = None
        for i in range(len(ms) - 1):
            if gs[i] > 0 >= gs[i + 1]:
                cruz = float(ms[i] + (ms[i + 1] - ms[i]) * gs[i] / (gs[i] - gs[i + 1])); break
        if cruz is None and gs[0] <= 0: cruz = 0.0
        if cruz is None: cruz = float("inf")
        # R de equilíbrio (Ky central)
        _, ys = arr(V.casos(cad, scen=scen))
        Rs = np.arange(0.5, 1.2001, 0.005)
        mm = np.array([met(ym, ys, R=float(r))[1] for r in Rs])
        r0 = float(Rs[np.argmax(mm >= 0)]) if (mm >= 0).any() else None
        r3 = float(Rs[np.argmax(mm >= -3)]) if (mm >= -3).any() else None
        out["equilibrio"][f"{scen}|{nome}"] = dict(ky_mult_equilibrio_p10=cruz, R_media_igual=r0, R_media_menos3=r3, curva_ky=dict(zip(map(str, ms.tolist()), gs.tolist())))
        print(f"{scen:9s} {nome:13s}: Ky sorgo x{cruz:.2f} zera o ganho de P10 | R mínimo p/ média>=0: {r0} ; p/ média>=-3%: {r3}")

# (b) Ky do milho
print("== (b) Ky do milho x (cenário FAO33, Ky sorgo x1, R 0,88)")
out["ky_milho"] = {}
for nome, cad in CADS.items():
    for km in (0.6, 0.8, 1.0, 1.2):
        ym, ys = arr(V.casos(cad, scen="FAO33", kym_milho=km))
        g, mdi, pf, pb = met(ym, ys)
        out["ky_milho"][f"{nome}|{km}"] = dict(ganho_p10=g, var_media=mdi, perda_mistura=pf, perda_base=pb)
        print(f"  {nome} Ky milho x{km}: P10 {g:+.1f}% média {mdi:+.1f}% perdas {pb}->{pf}")

# (c) raiz mais funda do sorgo (CAD do sorgo maior que o do milho), só onde o solo permite
print("== (c) sorgo explora mais volume de solo (CAD sorgo / CAD milho)")
out["raiz"] = {}
for nome, cad in CADS.items():
    for mult in (1.0, 1.25, 1.5):
        ym, ys = arr(V.casos(cad, scen="FAO33", cad_sorgo=cad * mult))
        g, mdi, pf, pb = met(ym, ys)
        out["raiz"][f"{nome}|{mult}"] = dict(ganho_p10=g, var_media=mdi)
        print(f"  {nome} CAD sorgo x{mult}: P10 {g:+.1f}% média {mdi:+.1f}%")

# (d) ciclo
print("== (d) ciclo (dias) do sorgo, milho fixo em 110")
out["ciclo"] = {}
for nome, cad in CADS.items():
    for ns in (95, 110, 125):
        ym, ys = arr(V.casos(cad, scen="FAO33", n_sorgo=ns))
        g, mdi, pf, pb = met(ym, ys)
        out["ciclo"][f"{nome}|{ns}"] = dict(ganho_p10=g, var_media=mdi)
        print(f"  {nome} sorgo {ns} d: P10 {g:+.1f}% média {mdi:+.1f}%")

# (e) geada: quanto do efeito vem de escapar da geada de setembro?
print("== (e) geada")
out["geada"] = {}
cs = V.casos(125.0, scen="FAO33")
fr = {}
for di, dd in enumerate(V.DATAS):
    fr[f"{dd[1]:02d}/{dd[0]:02d}"] = float(np.mean([c[4] for c in cs if c[1] == di]))
out["geada"]["freq_geada_milho_por_data"] = fr
print("  fração de safras com geada (Tmin<=2 °C entre os dias 20 e 95) no milho:", fr)
orig = V.GEADA
for desl in (0, 30):
    for g_on in (True, False):
        V.GEADA = orig if g_on else -100.0
        for nome, cad in CADS.items():
            ym, ys = arr(V.casos(cad, scen="FAO33", desloca_sorgo=desl))
            g, mdi, pf, pb = met(ym, ys)
            out["geada"][f"desl{desl}|geada{'on' if g_on else 'off'}|{nome}"] = dict(ganho_p10=g, var_media=mdi)
            print(f"  sorgo +{desl} d, geada {'ligada' if g_on else 'DESLIGADA'}, {nome}: P10 {g:+.1f}% média {mdi:+.1f}%")
V.GEADA = orig
# controle negativo sem geada
V.GEADA = -100.0
for scen in ("A4", "FAO33", "MISTO", "BIOMASSA"):
    ym, ys = arr(V.casos(175.0, scen=scen))
    g, mdi, pf, pb = met(ym, ys)
    out["geada"][f"controle175_semgeada|{scen}"] = dict(ganho_p10=g, var_media=mdi)
    print(f"  controle CAD 175 sem geada, {scen}: P10 {g:+.1f}% média {mdi:+.1f}%")
V.GEADA = orig

# (f) por data de plantio (FAO33 central)
print("== (f) por data de plantio (cenário FAO33)")
out["por_data"] = {}
for nome, cad in CADS.items():
    ym, ys = arr(V.casos(cad, scen="FAO33"))
    for di, dd in enumerate(V.DATAS):
        a, b = ym[:, di], ys[:, di]
        tot = 0.5 * a + 0.5 * 0.88 * b
        g = 100 * (np.percentile(tot, 10) / np.percentile(a, 10) - 1); mdi = 100 * (tot.mean() / a.mean() - 1)
        out["por_data"][f"{nome}|{dd[1]:02d}/{dd[0]:02d}"] = dict(p10_base=float(np.percentile(a, 10)), p10_mist=float(np.percentile(tot, 10)), ganho_p10=float(g), var_media=float(mdi))
        print(f"  {nome} {dd[1]:02d}/{dd[0]:02d}: P10 {np.percentile(a,10):.3f}->{np.percentile(tot,10):.3f} ({g:+.1f}%), média {mdi:+.1f}%")
json.dump(out, open(AQUI / "res_03_extras.json", "w"), indent=1, default=float)
