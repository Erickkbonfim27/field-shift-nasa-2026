#!/usr/bin/env python3
"""A4-1: quando trocar milho por sorgo em São Miguel do Oeste."""
import json, sys, datetime as dt, statistics as st
QUIET = "-q" in sys.argv
sys.argv = [a for a in sys.argv if a != "-q"]
from modelo_smo import simular, CHUVA, GWR, key, AQUI

R = float(sys.argv[1]) if len(sys.argv) > 1 else 0.85  # valor relativo do sorgo
SOLO = sys.argv[2] if len(sys.argv) > 2 else "argiloso"
KYS = float(sys.argv[3]) if len(sys.argv) > 3 else 1.0   # multiplica Ky do sorgo (sensibilidade)
KCS = float(sys.argv[4]) if len(sys.argv) > 4 else 1.0   # multiplica Kc do sorgo
RAIZS = float(sys.argv[5]) if len(sys.argv) > 5 else None
PERDA = 0.6
SAFRAS = range(1984, 2025)
DECS = [(8, 21), (9, 1), (9, 11), (9, 21), (10, 1), (10, 11), (10, 21), (11, 1), (11, 11), (11, 21), (12, 1), (12, 11), (12, 21),
        (1, 1), (1, 11), (1, 21), (2, 1), (2, 11), (2, 21)]


def data(safra, m, d): return dt.date(safra + (1 if m < 7 else 0), m, d)


casos = []
for a in SAFRAS:
    for i, (m, d) in enumerate(DECS):
        pl = data(a, m, d)
        rm = simular("milho_sil", SOLO, pl)
        rs = simular("sorgo_sil", SOLO, pl, kc_mult=KCS, ky_mult=KYS, raiz=RAIZS)
        if not rm or not rs: continue
        ch30 = sum(CHUVA[key(pl - dt.timedelta(j))] for j in range(1, 31))
        casos.append(dict(safra=a, dec=i, rot=f"{d:02d}/{m:02d}", ym=rm["y"], ys=rs["y"], gw=GWR[key(pl)], ch30=ch30,
                          geada_m=rm["geada"], geada_s=rs["geada"], isna_m=rm["isna"], s_ini=rm["s_ini"]))


def avalia(cs, escolhe):
    perdas = 0; soma = 0.0; troca = 0; acerta = 0
    for c in cs:
        sorgo = escolhe(c)
        y = c["ys"] if sorgo else c["ym"]
        perdas += y < PERDA
        soma += c["ys"] * R if sorgo else c["ym"]
        if sorgo:
            troca += 1; acerta += c["ys"] * R > c["ym"]
    n = len(cs)
    return dict(n=n, perdas=perdas, media=soma / n, troca=troca, acerta=acerta)


REGRAS = {
    "data": (lambda c, t: c["dec"] >= t, list(range(0, len(DECS) + 1))),
    "gwetroot": (lambda c, t: c["gw"] < t, [x / 100 for x in range(40, 96, 2)]),
    "chuva30": (lambda c, t: c["ch30"] < t, list(range(0, 301, 10))),
}


def loo(nome, cs):
    f, grade = REGRAS[nome]
    escolhas = {}
    for a in SAFRAS:
        treino = [c for c in cs if c["safra"] != a]
        base = avalia(treino, lambda c: False)
        melhor = None
        for t in grade:
            r = avalia(treino, lambda c, t=t: f(c, t))
            if r["media"] + 1e-9 < base["media"]: continue
            sc = (r["perdas"], -r["media"])
            if melhor is None or sc < melhor[0]: melhor = (sc, t)
        escolhas[a] = melhor[1] if melhor else None
    def escolhe(c):
        t = escolhas[c["safra"]]
        return False if t is None else f(c, t)
    return avalia(cs, escolhe), escolhas


def fit_total(nome, cs):
    f, grade = REGRAS[nome]
    base = avalia(cs, lambda c: False)
    res = []
    for t in grade:
        r = avalia(cs, lambda c, t=t: f(c, t))
        res.append((t, r))
    return base, res


if __name__ == "__main__":
    sempre_m = avalia(casos, lambda c: False)
    sempre_s = avalia(casos, lambda c: True)
    taxa_base = sum(c["ys"] * R > c["ym"] for c in casos) / len(casos)
    por_dec = []
    for i, (m, d) in enumerate(DECS):
        g = [c for c in casos if c["dec"] == i]
        por_dec.append(dict(rot=f"{d:02d}/{m:02d}", n=len(g),
                            ym=st.mean(c["ym"] for c in g), ys=st.mean(c["ys"] for c in g),
                            perda_m=sum(c["ym"] < PERDA for c in g), perda_s=sum(c["ys"] < PERDA for c in g),
                            compensa=sum(c["ys"] * R > c["ym"] for c in g),
                            salva=sum(c["ym"] < PERDA <= c["ys"] for c in g),
                            geada_m=sum(c["geada_m"] for c in g)))
    regras = {n: loo(n, casos) for n in REGRAS}
    out = dict(R=R, solo=SOLO, ky_sorgo_mult=KYS, kc_sorgo_mult=KCS, raiz_sorgo=RAIZS, n=len(casos), taxa_base_compensa=taxa_base,
               sempre_milho=sempre_m, sempre_sorgo=sempre_s, por_decendio=por_dec,
               regras={n: dict(res=r, limiares=e) for n, (r, e) in regras.items()})
    tag = f"R{R}_{SOLO}_ky{KYS}_kc{KCS}_raiz{RAIZS}"
    json.dump(out, open(AQUI / f"res_a4_1_{tag}.json", "w"), ensure_ascii=False, indent=1, default=str)
    json.dump(casos, open(AQUI / f"casos_a4_1_{tag}.json", "w"), default=str)
    if QUIET:
        print(tag, "| milho perdas", sempre_m["perdas"], "media %.3f" % sempre_m["media"], "| sorgo perdas", sempre_s["perdas"], "media %.3f" % sempre_s["media"],
              "| compensa %.2f" % taxa_base, "|", " ".join(f"{n}:{r['perdas']}/{r['media']:.3f}/troca{r['troca']}/ac{r['acerta']}" for n, (r, e) in regras.items()))
        sys.exit()
    print(f"Solo {SOLO}, R={R}, n={len(casos)} casos (safra x decêndio)")
    print("Sempre milho:", sempre_m)
    print("Sempre sorgo:", sempre_s)
    print("Taxa-base em que a troca compensa: %.2f" % taxa_base)
    print("\ndec    ym    ys   perdaM perdaS compensa salva geadaM (em", len(SAFRAS), "safras)")
    for x in por_dec:
        print(f'{x["rot"]}  {x["ym"]:.2f}  {x["ys"]:.2f}   {x["perda_m"]:>3}    {x["perda_s"]:>3}    {x["compensa"]:>3}    {x["salva"]:>3}  {x["geada_m"]:>3}')
    for n, (r, e) in regras.items():
        print(f"\nRegra {n} (LOO):", r, "limiares:", sorted(set(map(str, e.values()))))
