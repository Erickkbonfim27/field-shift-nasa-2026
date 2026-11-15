#!/usr/bin/env python3
"""A4-2: qual rotação anual usa menos água em São Miguel do Oeste (balanço contínuo, 1984-2025)."""
import json, sys, datetime as dt, statistics as st
from modelo_smo import CULT, ET0, CHUVA, TMIN, SOLOS, GEADA, INVERNO, kc_dia, fase_dia, key

ROT = {
    "R1 milho grão / aveia":            [("milho_gr", 9, 21), ("aveia", 4, 1)],
    "R2 soja / trigo":                  [("soja", 11, 11), ("trigo", 6, 11)],
    "R3 milho silagem / azevém (ref.)": [("milho_sil", 9, 1), ("azevem", 3, 1)],
    "R4 sorgo silagem / aveia":         [("sorgo_sil", 10, 21), ("aveia", 4, 1)],
    "R5 milho sil. + sorgo safrinha / aveia": [("milho_sil", 9, 1), ("sorgo_sil", 1, 5), ("aveia", 5, 1)],
}
ANOS = range(1984, 2024)  # ano agrícola a = 1/jul/a a 30/jun/a+1 (trigo de jun termina em out do ano seguinte)
PERDA = 0.6


def rodar(rot, solo):
    mm_m, lim = SOLOS[solo]
    prof = 1.0 if lim is None else lim
    cap = mm_m * prof
    inst = []
    for a in ANOS:
        for (c, m, d) in ROT[rot]:
            pl = dt.date(a + (1 if m < 7 else 0), m, d)
            n = sum(CULT[c]["fases"])
            inst.append(dict(ano=a, c=c, pl=pl, fim=pl + dt.timedelta(n), eta=[0.0] * 4, etc=[0.0] * 4, geada=False))
    por_dia = {}
    for i, x in enumerate(inst):
        d = x["pl"]
        while d < x["fim"]:
            por_dia[d] = i; d += dt.timedelta(1)
    ano_ag = lambda d: d.year if d.month >= 7 else d.year - 1
    anual = {a: dict(eta=0.0, etc=0.0, evap_pousio=0.0, drena=0.0, chuva=0.0) for a in ANOS}
    s = cap
    d = dt.date(1984, 7, 1); fim = dt.date(2025, 6, 30)
    while d <= fim:
        k = key(d)
        if k not in ET0: d += dt.timedelta(1); continue
        aa = ano_ag(d)
        s += CHUVA[k]
        dren = max(0.0, s - cap); s = min(s, cap)
        i = por_dia.get(d)
        if i is not None:
            x = inst[i]; c = CULT[x["c"]]; j = (d - x["pl"]).days
            f = fase_dia(c, j)
            e_c = kc_dia(c, j) * ET0[k]
            # raiz explora a fração raiz/prof do perfil; água distribuída por igual
            z = min(c["raiz"], prof)
            frac = s / cap
            ks = min(1.0, frac / (1 - c["p"]))
            e_a = min(e_c * ks, s * z / prof)
            s -= e_a
            x["eta"][f] += e_a; x["etc"][f] += e_c
            if f in (1, 2) and x["c"] not in INVERNO and TMIN[k] <= GEADA: x["geada"] = True
            if aa in anual: anual[aa]["eta"] += e_a; anual[aa]["etc"] += e_c
        else:
            e = 0.3 * ET0[k] * min(1.0, s / (0.5 * cap))
            s -= e
            if aa in anual: anual[aa]["evap_pousio"] += e
        if aa in anual: anual[aa]["drena"] += dren; anual[aa]["chuva"] += CHUVA[k]
        d += dt.timedelta(1)
    for x in inst:
        c = CULT[x["c"]]
        isna = [a / b if b else 1 for a, b in zip(x["eta"], x["etc"])]
        y = 1.0
        for i in range(4): y *= max(0.0, 1 - c["ky"][i] * (1 - isna[i]))
        if x["geada"]: y *= 0.3
        x["y"] = y; x["etc_t"] = sum(x["etc"]); x["eta_t"] = sum(x["eta"])
    anos = []
    for a in ANOS:
        cs = [x for x in inst if x["ano"] == a]
        if any(x["fim"] > dt.date(2025, 12, 31) for x in cs): continue
        etc_c = sum(x["etc_t"] for x in cs); eta_c = sum(x["eta_t"] for x in cs)
        anos.append(dict(ano=a, etc=etc_c, eta=eta_c, deficit=etc_c - eta_c, evap_pousio=anual[a]["evap_pousio"],
                         et_total=anual[a]["eta"] + anual[a]["evap_pousio"], drena=anual[a]["drena"], chuva=anual[a]["chuva"],
                         perda=any(x["y"] < PERDA for x in cs), perda_verao=cs[0]["y"] < PERDA,
                         ys={x["c"] + ("_2" if i else ""): round(x["y"], 3) for i, x in enumerate(cs)},
                         deficit_por_cult={x["c"] + ("_2" if i else ""): round(x["etc_t"] - x["eta_t"], 1) for i, x in enumerate(cs)}))
    return anos


def resumo(anos):
    m = lambda f: st.mean(x[f] for x in anos)
    culturas = anos[0]["ys"].keys()
    return dict(n=len(anos), etc=m("etc"), eta=m("eta"), deficit=m("deficit"), et_total=m("et_total"), drena=m("drena"), chuva=m("chuva"),
                deficit_p90=sorted(x["deficit"] for x in anos)[int(0.9 * (len(anos) - 1))],
                risco_perda=sum(x["perda"] for x in anos) / len(anos), risco_verao=sum(x["perda_verao"] for x in anos) / len(anos),
                perda_por_cult={c: sum(x["ys"][c] < PERDA for x in anos) for c in culturas},
                y_medio={c: round(st.mean(x["ys"][c] for x in anos), 3) for c in culturas},
                deficit_cult={c: round(st.mean(x["deficit_por_cult"][c] for x in anos), 1) for c in culturas})


if __name__ == "__main__":
    tudo = {}
    for solo in SOLOS:
        tudo[solo] = {}
        print(f"\n===== solo {solo} =====")
        print(f"{'rotação':40s} {'ETc':>5} {'ETa':>5} {'déf':>5} {'défP90':>6} {'ETtot':>5} {'dren':>5} {'perda':>6} {'verão':>6}  perdas por cultura / déficit por cultura")
        for r in ROT:
            anos = rodar(r, solo)
            z = resumo(anos)
            tudo[solo][r] = dict(resumo=z, anos=anos)
            print(f"{r:40s} {z['etc']:5.0f} {z['eta']:5.0f} {z['deficit']:5.0f} {z['deficit_p90']:6.0f} {z['et_total']:5.0f} {z['drena']:5.0f} {z['risco_perda']:6.2f} {z['risco_verao']:6.2f}  {z['perda_por_cult']} {z['deficit_cult']}")
    json.dump(tudo, open("res_a4_2.json", "w"), ensure_ascii=False, indent=1, default=str)
