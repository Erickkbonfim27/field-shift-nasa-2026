#!/usr/bin/env python3
"""A1-1, análises pós-teste (não fazem parte do critério): linha de base ingênua, geada, IBGE 2000+."""
from validar_a1_1 import *
# linha de base ingênua: "plante de setembro a janeiro" (dec 25-36 e 1-3) para todas
ing = [int(d >= 25 or d <= 3) for d in range(1, 37)]
for solo in ("argiloso", "medio"):
    tot = ac = 0
    for c, zr in pares(solo).items():
        if c == "pastagem_inv": continue
        ze = [int(v > 0) for v in zr]; a = sum(x == y for x, y in zip(ing, ze)); tot += 36; ac += a
        print(f"ingênua {solo} {c}: {a}/36 kappa {kappa(ing, ze):+.2f}")
    print(f"== ingênua {solo}: {ac}/{tot} = {ac/tot:.0%}")
print()
for tg in (0.0, 3.0):
    a, _ = comparar("argiloso", t_geada=tg, imprime=False); print(f"geada {tg} °C: acerto {a:.0%}")
a, _ = comparar("argiloso", corte=6, imprime=False); print(f"corte 6: acerto {a:.0%}")
# dias de geada por ano no POWER
import collections
cnt = collections.Counter(); cnt3 = collections.Counter(); cnt0 = collections.Counter()
for d, t in L.tmin.items():
    if 1984 <= d.year <= 2025:
        cnt[d.year] += t <= 2; cnt3[d.year] += t <= 3; cnt0[d.year] += t <= 0
print("dias/ano T2M_MIN<=0/2/3 °C:", round(st.mean(cnt0.values()), 1), round(st.mean(cnt.values()), 1), round(st.mean(cnt3.values()), 1))
# última geada (<=2) do inverno e primeira do outono, mediana
ult, pri = [], []
for a in range(1984, 2026):
    ds = [d for d, t in L.tmin.items() if d.year == a and t <= 2]
    if ds:
        ult.append(max(d for d in ds if d.month <= 10).timetuple().tm_yday if any(d.month <= 10 for d in ds) else None)
        pri.append(min(ds).timetuple().tm_yday)
ult = [u for u in ult if u]
print("1ª geada (mediana dia do ano):", st.median(pri), " última:", st.median(ult), " P90 última:", sorted(ult)[int(0.9*len(ult))])
print()
rho, hits, sim, an = validar_ibge(imprime=False)
anos = [a for a in sorted(sim) if a in an and a >= 2000]
print("IBGE 2000-2025: Spearman", round(spearman([sim[a] for a in anos], [an[a] for a in anos]), 2), "n", len(anos))
for dec in (25, 26, 28, 29, 30):
    r, h, *_ = validar_ibge(dec=dec, imprime=False); print(f"dec {dec}: Spearman {r:.2f} acertos {h}")
print("série:", " ".join(f"{a}:{sim[a]:.2f}/{an[a]:.2f}" for a in sorted(sim) if a in an))
