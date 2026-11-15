#!/usr/bin/env python3
"""A4-3: parte da área com sorgo como seguro de silagem (SMO)."""
import json, statistics as st, sys
R = 0.85
def q(v, p):
    v = sorted(v); i = p * (len(v) - 1); lo = int(i); hi = min(lo + 1, len(v) - 1)
    return v[lo] + (v[hi] - v[lo]) * (i - lo)
out = {}
ky = sys.argv[1] if len(sys.argv) > 1 else "1.0"
for solo in ["argiloso", "medio", "raso"]:
    c = json.load(open(f"casos_a4_1_R0.85_{solo}_ky{ky}_kc1.0_raizNone.json"))
    c = [x for x in c if x["dec"] in (2, 3, 4, 5, 6)]
    out[solo] = {}
    for f in (0, 0.25, 0.5, 1.0):
        tot = [(1 - f) * x["ym"] + f * R * x["ys"] for x in c]
        out[solo][f] = dict(media=st.mean(tot), p10=q(tot, 0.10), p05=q(tot, 0.05), abaixo06=sum(t < 0.6 for t in tot), n=len(tot), minimo=min(tot))
    b = out[solo][0]
    print(f"== solo {solo} (Ky sorgo x{ky}), n={b['n']} casos (41 safras x 5 decêndios)")
    for f, r in out[solo].items():
        print(f"  sorgo {int(f*100):>3}% | média {r['media']:.3f} ({100*(r['media']/b['media']-1):+.1f}%) | P10 {r['p10']:.3f} ({100*(r['p10']/b['p10']-1):+.1f}%) | P05 {r['p05']:.3f} | casos <0,6: {r['abaixo06']} | mínimo {r['minimo']:.2f}")
json.dump(out, open(f"res_a4_3_ky{ky}.json", "w"), indent=1)
