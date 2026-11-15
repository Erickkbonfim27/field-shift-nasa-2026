#!/usr/bin/env python3
"""A1-3: milho cedo + tarde com penalidade de potencial por radiação (POWER ALLSKY_SFC_SW_DWN)."""
import itertools, json, statistics as st
from modelo_sc import *
from mapa import L
from escalonamento import JANELA, ANOS, ORD, stats, fmt

C = CULTURAS["milho_safra"]; ini, dev, mid, late = C["fases"]
RS = {}
for k, v in L.P["ALLSKY_SFC_SW_DWN"].items():
    if v != -999: RS[dt.date(int(k[:4]), int(k[4:6]), int(k[6:]))] = v
def rad(pl): return sum(RS[pl + dt.timedelta(i)] for i in range(ini + dev, ini + dev + mid + late))
rad_dec = {d: st.mean(rad(data_plantio(a, d)) for a in ANOS) for d in JANELA}
POT = {d: rad_dec[d] / max(rad_dec.values()) for d in JANELA}

def serie(solo, d):
    out = {}
    for a in ANOS:
        r = simular(L, "milho_safra", solo, data_plantio(a, d))
        out[a] = POT[d] * r["y"] * (0.3 if r["geada"] else 1.0)
    return out

def combo(S, c, anos): return [st.mean(S[d][a] for d in c) for a in anos]

if __name__ == "__main__":
    print("potencial relativo:", " ".join(f"{d}:{POT[d]:.2f}" for d in JANELA))
    out = {"pot": POT}
    for solo in ("argiloso", "medio"):
        S = {d: serie(solo, d) for d in JANELA}
        single = {d: stats(list(S[d].values())) for d in JANELA}
        best = max(JANELA, key=lambda d: single[d]["media"])
        print(f"===== solo {solo}")
        print("   média por data:", " ".join(f"{d}:{single[d]['media']:.2f}/{single[d]['pior']:.2f}" for d in JANELA))
        print(fmt(f"única melhor média (dec {best})", single[best]))
        print(fmt("única habitual (dec 27)", single[27]))
        res = {}
        for nome, c in (("15/set + 15/dez", (26, 35)), ("15/set + 5/jan", (26, 1)), ("[extra] melhor + 5/jan", (best, 1)) if best != 1 else ("[extra] melhor + 15/dez", (best, 35))):
            s = stats(combo(S, c, ANOS)); res[nome] = s; print(fmt(f"{nome} {c}", s))
        tr, te = [a for a in ANOS if a <= 2003], [a for a in ANOS if a >= 2004]
        cands = [c for k in (2, 3) for c in itertools.combinations(JANELA, k) if all(ORD[c[i+1]] - ORD[c[i]] >= 2 for i in range(k - 1))]
        bc = max(cands, key=lambda c: (stats(combo(S, c, tr))["pior"], stats(combo(S, c, tr))["media"]))
        b1 = max(JANELA, key=lambda d: stats([S[d][a] for a in tr])["media"])
        print(f"  fora da amostra: combo {bc}, única {b1}")
        print("   " + fmt("teste 2004-24 combo", stats(combo(S, bc, te))))
        print("   " + fmt("teste 2004-24 única", stats([S[b1][a] for a in te])))
        for a in (2004, 2008, 2011, 2020, 2021, 2024):
            print(f"   {a}/{a+1}: set(26) {S[26][a]:.2f}  dez(35) {S[35][a]:.2f}  jan(1) {S[1][a]:.2f}  melhor({best}) {S[best][a]:.2f}  set+jan {(S[26][a]+S[1][a])/2:.2f}")
        out[solo] = dict(best=best, single={d: single[d] for d in JANELA}, combos=res)
        json.dump({str(d): S[d] for d in S}, open(f"series_milho_pot_{solo}.json", "w"))
    json.dump(out, open("cedo_tarde_smo.json", "w"), indent=1)
