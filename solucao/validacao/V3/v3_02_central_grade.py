#!/usr/bin/env python3
"""V3-02: cenário central, bootstrap por safra, grade de sensibilidade pré-definida, curva por CAD."""
import sys, json, itertools
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
import modelo_v3 as V
AQUI = Path(__file__).resolve().parent
rng = np.random.default_rng(20261114)
NB = 2000


def arr(cs):
    """cs ordenado por safra e data -> arrays (41,5)."""
    ym = np.array([c[2] for c in cs]).reshape(-1, 5)
    ys = np.array([c[3] for c in cs]).reshape(-1, 5)
    return ym, ys


def stats(ym, ys, f, R):
    tot = ((1 - f) * ym + f * R * ys).ravel(); base = ym.ravel()
    return dict(media=tot.mean(), p10=np.percentile(tot, 10), perda=int((tot < 0.6).sum()), base_media=base.mean(), base_p10=np.percentile(base, 10), base_perda=int((base < 0.6).sum()))


def ganho(ym, ys, f, R):
    s = stats(ym, ys, f, R)
    return 100 * (s["p10"] / s["base_p10"] - 1), 100 * (s["media"] / s["base_media"] - 1), s


def boot(ym, ys, f, R):
    ns = ym.shape[0]; g = np.empty(NB); m = np.empty(NB); pr = np.empty(NB)
    for b in range(NB):
        idx = rng.integers(0, ns, ns)
        a, bb = ym[idx], ys[idx]
        tot = ((1 - f) * a + f * R * bb).ravel(); base = a.ravel()
        g[b] = 100 * (np.percentile(tot, 10) / np.percentile(base, 10) - 1)
        m[b] = 100 * (tot.mean() / base.mean() - 1)
        pr[b] = (tot < 0.6).sum() / max(1, (base < 0.6).sum()) - 1
    return g, m, pr


out = {"central": {}, "curva_cad": {}, "grade": {}}
CENTRAL = dict(scen="FAO33", kym=1.0, kcm=1.0, desl=0, R=0.88)

# ---------- 1. central + bootstrap ----------
for rotulo, cad in (("V3a_raso_A4_87.5", 87.5), ("V3b_raso_ZARC_42", 42.0), ("controle_fundo_175", 175.0), ("medio_125", 125.0)):
    cs = V.casos(cad, scen="FAO33"); ym, ys = arr(cs)
    r = {}
    for f in (0.25, 0.5, 1.0):
        gp, gm, s = ganho(ym, ys, f, 0.88)
        g, m, pr = boot(ym, ys, f, 0.88)
        r[f] = dict(ganho_p10=gp, var_media=gm, p10=s["p10"], base_p10=s["base_p10"], media=s["media"], base_media=s["base_media"], perda=s["perda"], base_perda=s["base_perda"],
                    boot_p10_ic80=[float(np.percentile(g, 10)), float(np.percentile(g, 90))], boot_p10_ic95=[float(np.percentile(g, 2.5)), float(np.percentile(g, 97.5))],
                    boot_prob_ganho_pos=float((g > 0).mean()), boot_media_ic95=[float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))],
                    boot_prob_media_ok=float((m >= -3).mean()), boot_perda_var_ic80=[float(np.percentile(pr, 10)), float(np.percentile(pr, 90))])
    out["central"][rotulo] = r
    x = r[0.5]
    print(f"[central] {rotulo} f=50%: P10 {x['base_p10']:.3f}->{x['p10']:.3f} ({x['ganho_p10']:+.1f}%, IC95 {x['boot_p10_ic95'][0]:+.1f} a {x['boot_p10_ic95'][1]:+.1f}; P(ganho>0)={x['boot_prob_ganho_pos']:.2f}) | média {x['var_media']:+.1f}% (IC95 {x['boot_media_ic95'][0]:+.1f} a {x['boot_media_ic95'][1]:+.1f}; P(>=-3%)={x['boot_prob_media_ok']:.2f}) | perda {x['base_perda']}->{x['perda']}")

# ---------- 2. grade pré-definida ----------
KYM = (0.5, 0.75, 1.0, 1.5, 2.0); RS = (0.75, 0.88, 1.0); SCENS = ("A4", "FAO33", "BIOMASSA"); DESL = (0, 30); KCM = (0.85, 1.0, 1.15)
for rotulo, cad in (("V3a_raso_A4_87.5", 87.5), ("V3b_raso_ZARC_42", 42.0), ("medio_125", 125.0), ("controle_fundo_175", 175.0)):
    linhas = []
    for scen in SCENS + ("MISTO",):
        cm = V.casos(cad, scen=scen)  # milho (sorgo recalculado abaixo)
        ym = np.array([c[2] for c in cm]).reshape(-1, 5)
        for kym, desl, kcm in itertools.product(KYM, DESL, KCM):
            cs = V.casos(cad, scen=scen, kym_sorgo=kym, kcm_sorgo=kcm, desloca_sorgo=desl)
            ym2, ys = arr(cs)
            if ym2.shape != ys.shape: continue
            for R in RS:
                gp, gm, s = ganho(ym2, ys, 0.5, R)
                linhas.append(dict(scen=scen, kym=kym, desl=desl, kcm=kcm, R=R, ganho_p10=float(gp), var_media=float(gm), ok=bool(gp > 0 and gm >= -3)))
    out["grade"][rotulo] = linhas
    pre = [l for l in linhas if l["scen"] in SCENS]
    sh = np.mean([l["ok"] for l in pre])
    g = np.array([l["ganho_p10"] for l in pre]); mm = np.array([l["var_media"] for l in pre])
    print(f"[grade pré-def.] {rotulo}: {len(pre)} combinações, sobrevivem {100*sh:.0f}% | ganho P10: mín {g.min():+.1f} mediana {np.median(g):+.1f} máx {g.max():+.1f} | média: mín {mm.min():+.1f} mediana {np.median(mm):+.1f} máx {mm.max():+.1f}")
    for scen in SCENS + ("MISTO",):
        ls = [l for l in linhas if l["scen"] == scen]
        print(f"     {scen:9s}: sobrevivem {100*np.mean([l['ok'] for l in ls]):.0f}% de {len(ls)} | ganho P10 mediana {np.median([l['ganho_p10'] for l in ls]):+.1f}")
    for kym in KYM:
        ls = [l for l in pre if l["kym"] == kym]
        print(f"     Ky sorgo x{kym}: sobrevivem {100*np.mean([l['ok'] for l in ls]):.0f}% | ganho P10 mediana {np.median([l['ganho_p10'] for l in ls]):+.1f}")
    for R in RS:
        ls = [l for l in pre if l["R"] == R]
        print(f"     R={R}: sobrevivem {100*np.mean([l['ok'] for l in ls]):.0f}%")
    for d in DESL:
        ls = [l for l in pre if l["desl"] == d]
        print(f"     sorgo +{d} d: sobrevivem {100*np.mean([l['ok'] for l in ls]):.0f}%")

# ---------- 3. curva por CAD (central e cenários) ----------
CADS = [24, 31.8, 41.4, 54.6, 66, 72.6, 87.5, 95.4, 110, 125, 150, 175]
for scen in ("A4", "FAO33", "MISTO", "BIOMASSA"):
    out["curva_cad"][scen] = []
    for cad in CADS:
        cs = V.casos(cad, scen=scen); ym, ys = arr(cs)
        gp, gm, s = ganho(ym, ys, 0.5, 0.88)
        out["curva_cad"][scen].append(dict(cad=cad, ganho_p10=float(gp), var_media=float(gm), base_p10=float(s["base_p10"]), base_media=float(s["base_media"]), base_perda=s["base_perda"], perda=s["perda"]))
json.dump(out, open(AQUI / "res_02_central_grade.json", "w"), indent=1, default=float)
print("ok")
