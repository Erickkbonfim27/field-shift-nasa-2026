#!/usr/bin/env python3
"""A1-2: plantar milho em 1, 2 ou 3 datas em São Miguel do Oeste. Reduz a perda no pior ano?"""
import itertools, json, statistics as st
from modelo_sc import *
from mapa import L

JANELA = list(range(24, 37)) + [1, 2, 3]
ANOS = list(range(1984, 2025))
ORD = {d: i for i, d in enumerate(JANELA)}  # posição na safra (ago -> jan)

def serie(solo, dec, cultura="milho_safra"):
    out = {}
    for a in ANOS:
        r = simular(L, cultura, solo, data_plantio(a, dec))
        out[a] = r["y"] * (0.3 if r["geada"] else 1.0)
    return out

def stats(ys):
    ys = sorted(ys); n = len(ys)
    return dict(media=st.mean(ys), pior=ys[0], p10=ys[int(0.1 * n)], dp=st.pstdev(ys),
                anos_perda40=sum(y < 0.6 for y in ys))

def combo(S, decs, anos):
    return [st.mean(S[d][a] for d in decs) for a in anos]

def fmt(nome, s):
    return (f"{nome:34} média {s['media']:.3f}  pior {s['pior']:.2f} (perda {1-s['pior']:.0%})  "
            f"P10 {s['p10']:.2f}  dp {s['dp']:.3f}  anos perda>40%: {s['anos_perda40']}")

def rodar(solo, imprime=True):
    S = {d: serie(solo, d) for d in JANELA}
    single = {d: stats(list(S[d].values())) for d in JANELA}
    melhor = max(JANELA, key=lambda d: single[d]["media"])
    melhor_pior = max(JANELA, key=lambda d: (single[d]["pior"], single[d]["media"]))
    res = dict(solo=solo, single={d: single[d] for d in JANELA}, melhor=melhor, melhor_pior=melhor_pior)
    fixos = {"2 datas: 15/set+15/out": (26, 29), "2 datas: 15/set+5/nov": (26, 31), "3 datas: 15/set+15/out+15/nov": (26, 29, 32)}
    res["fixos"] = {k: stats(combo(S, v, ANOS)) for k, v in fixos.items()}
    if imprime:
        print(f"===== solo {solo}")
        print(fmt(f"única melhor média (dec {melhor})", single[melhor]))
        print(fmt(f"única melhor pior-ano (dec {melhor_pior})", single[melhor_pior]))
        print(fmt("única habitual (dec 27)", single[27]))
        for k, s in res["fixos"].items(): print(fmt(k, s))
    # correlação entre datas nos anos ruins
    ruins = sorted(ANOS, key=lambda a: S[melhor][a])[:6]
    if imprime:
        print("  6 piores anos da melhor data e o rendimento nas outras datas:")
        for a in ruins:
            print(f"   {a}/{a+1}: " + " ".join(f"{d}:{S[d][a]:.2f}" for d in JANELA))
    # fora da amostra: escolhe a melhor combinação em 1984-2003 pelo pior ano, testa em 2004-2024
    tr, te = [a for a in ANOS if a <= 2003], [a for a in ANOS if a >= 2004]
    cands = [c for k in (2, 3) for c in itertools.combinations(JANELA, k) if all(ORD[c[i+1]] - ORD[c[i]] >= 2 for i in range(k - 1))]
    def score(c, anos): s = stats(combo(S, c, anos)); return (s["pior"], s["media"])
    best_c = max(cands, key=lambda c: score(c, tr))
    best_1 = max(JANELA, key=lambda d: (stats([S[d][a] for a in tr])["media"]))
    oos = dict(combo=best_c, combo_teste=stats(combo(S, best_c, te)), single=best_1, single_teste=stats([S[best_1][a] for a in te]))
    # limite superior (escolhida olhando tudo)
    best_all = max(cands, key=lambda c: score(c, ANOS))
    res.update(oos=oos, melhor_combo_tudo=(best_all, stats(combo(S, best_all, ANOS))))
    if imprime:
        print(f"  fora da amostra: combo escolhido em 1984-2003 = {best_c}; data única escolhida = {best_1}")
        print("   " + fmt("teste 2004-24 combo", oos["combo_teste"]))
        print("   " + fmt("teste 2004-24 única", oos["single_teste"]))
        print("   " + fmt(f"limite sup. (tudo) {best_all}", res["melhor_combo_tudo"][1]))
    return res, S

if __name__ == "__main__":
    out = {}
    for solo in ("argiloso", "medio"):
        r, S = rodar(solo); out[solo] = r
        json.dump({str(d): S[d] for d in S}, open(f"series_milho_{solo}.json", "w"))
    json.dump(out, open("escalonamento_smo.json", "w"), indent=1, default=str)
