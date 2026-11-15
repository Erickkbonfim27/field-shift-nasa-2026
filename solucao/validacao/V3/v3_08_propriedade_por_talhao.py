#!/usr/bin/env python3
"""V3-08 (pós-teste, exploratório): decisão por talhão numa propriedade com 38% de solo raso (UDESC, SMO) e 62% de solo fundo.
Compara: (a) tudo milho; (b) 50% sorgo em todos os talhões; (c) 50% sorgo só nos talhões rasos; (d) 100% sorgo só nos rasos.
Mesma chuva nos dois tipos de talhão (mesma safra). R = 0,88. Cenários FAO-33 e misto.
"""
import sys, json
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
import modelo_v3 as V
AQUI = Path(__file__).resolve().parent
A_RASO = 0.382
out = {}


def arr(cs):
    return np.array([c[2] for c in cs]).reshape(-1, 5), np.array([c[3] for c in cs]).reshape(-1, 5)


for scen in ("FAO33", "MISTO", "BIOMASSA"):
    for cad_r in (42.0, 87.5):
        ymr, ysr = arr(V.casos(cad_r, scen=scen)); ymf, ysf = arr(V.casos(175.0, scen=scen))
        R = 0.88
        def farm(fr, ff):  # fração de sorgo no raso e no fundo
            return (A_RASO * ((1 - fr) * ymr + fr * R * ysr) + (1 - A_RASO) * ((1 - ff) * ymf + ff * R * ysf)).ravel()
        base = farm(0, 0)
        row = {}
        for nome, (fr, ff) in {"a_tudo_milho": (0, 0), "b_50pct_em_todos": (0.5, 0.5), "c_50pct_so_no_raso": (0.5, 0), "d_100pct_so_no_raso": (1.0, 0)}.items():
            t = farm(fr, ff)
            row[nome] = dict(media=float(t.mean()), p10=float(np.percentile(t, 10)), ganho_p10=float(100 * (np.percentile(t, 10) / np.percentile(base, 10) - 1)), var_media=float(100 * (t.mean() / base.mean() - 1)),
                             area_sorgo=float(A_RASO * fr + (1 - A_RASO) * ff))
        out[f"{scen}|raso{cad_r}"] = row
        print(f"== {scen}, raso {cad_r} mm (38,2% da área) + fundo 175 mm")
        for k, v in row.items(): print(f"   {k:22s} área em sorgo {100*v['area_sorgo']:4.1f}% | P10 {v['p10']:.3f} ({v['ganho_p10']:+.1f}%) | média {v['media']:.3f} ({v['var_media']:+.1f}%)")
json.dump(out, open(AQUI / "res_08_propriedade.json", "w"), indent=1)
