#!/usr/bin/env python3
"""A1-1: (a) concordância com ZARC 2026/27 e (b) correlação com IBGE PAM (milho, São Miguel do Oeste)."""
import csv, json, statistics as st, datetime as dt
from modelo_sc import *
from mapa import mapa, L

# ---------- ZARC ----------
Z = list(csv.DictReader(open("ext/zarc_2627_smo_itu.csv", encoding="utf-8-sig"), delimiter=";"))
def zarc(nome, ciclo, solo):
    for x in Z:
        if x["municipio"] == "São Miguel do Oeste" and x["Nome_cultura"] == nome and x["Cod_Ciclo"] == ciclo \
           and x["Cod_Solo"] == solo and x["Nome_Outros_Manejos"] == "Sequeiro":
            return [int(x[f"dec{i}"]) for i in range(1, 37)]
    return [0] * 36

def uniao(*vs): return [max(c) if any(c) else 0 for c in zip(*vs)]
SOLO_AD = {"argiloso": "15", "medio": "13"}       # AD5 / AD3
SOLO_T = {"argiloso": "3", "medio": "2"}          # tipo 3 / tipo 2 (sorgo)
def pares(solo):
    ad, t = SOLO_AD[solo], SOLO_T[solo]
    return {
        "milho_safra": zarc("Milho 1ª Safra", "21", ad),
        "feijao": uniao(zarc("Feijão", "20", ad), zarc("Feijão 2ª Safra", "20", ad)),
        "sorgo": uniao(zarc("Sorgo Granífero", "21", t), zarc("Sorgo Granífero 2ª Safra", "21", t)),
        "pastagem_inv": zarc("Aveia", "21", ad),  # aveia grão: só referência, não é a mesma cultura
    }

def kappa(a, b):
    n = len(a); po = sum(x == y for x, y in zip(a, b)) / n
    pa, pb = sum(a) / n, sum(b) / n
    pe = pa * pb + (1 - pa) * (1 - pb)
    return (po - pe) / (1 - pe) if pe < 1 else 1.0

def comparar(solo, corte=7, t_geada=T_GEADA, imprime=True):
    tot = ac = 0; linhas = {}
    for c, zr in pares(solo).items():
        m = mapa(c, solo, t_geada)
        nos = [int(m[d]["agua"] >= corte and m[d]["geada"] <= 2) for d in range(1, 37)]
        ze = [int(v > 0) for v in zr]
        acc = sum(x == y for x, y in zip(nos, ze))
        linhas[c] = dict(acc=acc, kappa=round(kappa(nos, ze), 2), nos=nos, zarc=zr,
                         so_nos=[d for d in range(1, 37) if nos[d-1] and not ze[d-1]],
                         so_zarc=[d for d in range(1, 37) if ze[d-1] and not nos[d-1]])
        if c != "pastagem_inv": tot += 36; ac += acc
        if imprime:
            print(f"{c:13} acerto {acc}/36  kappa {linhas[c]['kappa']:+.2f}  só nós: {linhas[c]['so_nos']}  só ZARC: {linhas[c]['so_zarc']}")
            print("   nós :", "".join("X" if v else "." for v in nos))
            print("   ZARC:", "".join(str(v // 10) if v else "." for v in zr))
    if imprime: print(f"== solo {solo}, corte {corte}, geada {t_geada}: acerto (sem aveia) {ac}/{tot} = {ac/tot:.0%}")
    return ac / tot, linhas

# ---------- IBGE ----------
def ibge():
    d = json.load(open("ext/pam_smo.json"))
    y = {int(r["D3N"]): float(r["V"]) for r in d[1:] if r["D2C"] == "112" and r["D4C"] == "2711" and r["V"] not in ("-", "...", "X")}
    anos = sorted(y); an = {}
    for a in anos:
        jan = [y[b] for b in range(a - 3, a + 4) if b in y]
        an[a] = y[a] / st.median(jan)
    return y, an

def spearman(a, b):
    def rank(v):
        o = sorted(range(len(v)), key=lambda i: v[i]); r = [0] * len(v)
        i = 0
        while i < len(o):
            j = i
            while j + 1 < len(o) and v[o[j + 1]] == v[o[i]]: j += 1
            for k in range(i, j + 1): r[o[k]] = (i + j) / 2
            i = j + 1
        return r
    ra, rb = rank(a), rank(b)
    ma, mb = st.mean(ra), st.mean(rb)
    num = sum((x - ma) * (y - mb) for x, y in zip(ra, rb))
    return num / (sum((x - ma) ** 2 for x in ra) * sum((y - mb) ** 2 for y in rb)) ** 0.5

def validar_ibge(solo="argiloso", dec=27, imprime=True):
    y, an = ibge()
    sim = {}
    for a in range(1984, 2025):
        r = simular(L, "milho_safra", solo, data_plantio(a, dec))
        sim[a + 1] = r["y"] * (0.3 if r["geada"] else 1)  # colheita no ano seguinte
    anos = [a for a in sorted(sim) if a in an]
    rho = spearman([sim[a] for a in anos], [an[a] for a in anos])
    piores_ibge = sorted(anos, key=lambda a: an[a])[:5]
    piores_sim = set(sorted(anos, key=lambda a: sim[a])[:8])
    hits = [a for a in piores_ibge if a in piores_sim]
    if imprime:
        print(f"IBGE x simulado ({solo}, dec {dec}): n={len(anos)} Spearman={rho:.2f}")
        print("  5 piores IBGE:", [(a, round(an[a], 2), round(sim[a], 2)) for a in piores_ibge], "acertos:", hits)
        print("  8 piores simulados:", sorted((a, round(sim[a], 2), round(an[a], 2)) for a in piores_sim))
    return rho, hits, sim, an

if __name__ == "__main__":
    for solo in ("argiloso", "medio"):
        comparar(solo)
    print()
    for solo in ("argiloso", "medio"):
        validar_ibge(solo)
