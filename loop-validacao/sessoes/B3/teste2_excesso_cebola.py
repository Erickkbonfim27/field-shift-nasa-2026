#!/usr/bin/env python3
"""B3-2: excesso de chuva na cebola (Ituporanga).
Indicador principal: excedente hídrico 1/set–30/nov (balanço FAO-56, cebola, raiz 0,3 m, solo médio).
Secundário: dias de molhamento (chuva >= 1 mm e RH2M >= 90%) 1/set–30/nov.
Conferência: rendimento da cebola, IBGE PAM, microrregião 42014 (e município 4208500)."""
import datetime as dt, json, statistics as st
from comum import *

pw = Power("ituporanga")
FASES, KC = (15, 25, 70, 40), (0.70, 1.05, 0.75)  # FAO-56, cebola seca, 150 dias
CAD = 125 * 0.3
TRANSPLANTE = (8, 1)
JAN = ((9, 1), (11, 30))


def safra(ano, jan=JAN):
    pl = dt.date(ano, *TRANSPLANTE)
    b = balanco(pw, pl, dt.date(ano, 12, 31), FASES, KC, CAD, p_depl=0.3)
    if b is None: return None
    a, z = dt.date(ano, *jan[0]), dt.date(ano, *jan[1])
    g = [x for x in b if a <= x["d"] <= z]
    exced = sum(x["exced"] for x in g)
    isna = sum(x["eta"] for x in g) / sum(x["etc"] for x in g)
    mol = sum(1 for _, k in dias(a, z) if pw.chuva[k] >= 1 and pw.P["RH2M"][k] >= 90)
    chuva = sum(pw.chuva[k] for _, k in dias(a, z))
    # semanas de alerta: semanas (7 dias) com >= 4 dias de molhamento
    sem = 0
    d = a
    while d + dt.timedelta(6) <= z:
        n = sum(1 for _, k in dias(d, d + dt.timedelta(6)) if pw.chuva[k] >= 1 and pw.P["RH2M"][k] >= 90)
        sem += n >= 4
        d += dt.timedelta(7)
    return dict(ano=ano, exced=exced, molhamento=mol, chuva=chuva, isna=isna, semanas_alerta=sem)


def avaliar(arq, nome, jan=JAN):
    rel = rend_relativo(ibge_serie(arq, "Rendimento"))
    linhas = [s for a in range(1984, 2026) if a in rel and (s := safra(a, jan))]
    for s in linhas: s["rel"] = rel[s["ano"]]
    ruins = [s["rel"] <= 0.85 for s in linhas]
    nb, n = sum(ruins), len(linhas)
    res = dict(base=nome, n=n, ruins=nb, anos_ruins=[s["ano"] for s, r in zip(linhas, ruins) if r])
    for ind, sentido in (("exced", +1), ("molhamento", +1), ("chuva", +1), ("semanas_alerta", +1), ("isna", -1)):
        xs = [s[ind] for s in linhas]
        L = loo(xs, ruins, sentido)
        res[ind] = dict(spearman=round(spearman(xs, [s["rel"] for s in linhas]), 2),
                        p=round(p_perm(xs, [s["rel"] for s in linhas]), 4),
                        limiar_todos=round(melhor_limiar(xs, ruins, sentido), 2),
                        acertos=f'{L["acertos"]}/{L["ruins"]}', falsos=L["falsos"],
                        frac_falsos=round(L["frac_falsos"], 2) if L["frac_falsos"] is not None else None,
                        anos_alerta=[s["ano"] for s, a in zip(linhas, L["alertas"]) if a])
    res["linha_base_acaso"] = dict(acertos_esperados=round(nb * nb / n, 1), frac_falsos=round(1 - nb / n, 2))
    return res, linhas


if __name__ == "__main__":
    out = {}
    for arq, nome in (("cebola_micro_ituporanga.json", "microrregião 42014"), ("cebola_ituporanga.json", "município 4208500")):
        r, linhas = avaliar(arq, nome)
        out[nome] = r
        print(json.dumps(r, ensure_ascii=False, indent=1))
        if nome.startswith("micro"): tab = linhas
    sens = {}
    for jan in (((9, 1), (11, 30)), ((10, 1), (11, 30)), ((9, 1), (10, 31)), ((10, 15), (12, 15))):
        r, _ = avaliar("cebola_micro_ituporanga.json", "micro", jan)
        sens[f"{jan[0][1]:02d}/{jan[0][0]:02d}–{jan[1][1]:02d}/{jan[1][0]:02d}"] = {k: dict(spearman=r[k]["spearman"], acertos=r[k]["acertos"], falsos=r[k]["falsos"]) for k in ("exced", "molhamento", "chuva")}
    out["sensibilidade_janela_micro"] = sens
    print(json.dumps(sens, ensure_ascii=False, indent=1))
    json.dump(dict(resultado=out, tabela=[{k: (round(v, 3) if isinstance(v, float) else v) for k, v in s.items()} for s in tab]),
              open(B3 / "teste2_resultado.json", "w"), ensure_ascii=False, indent=1)
    lim = out["microrregião 42014"]["exced"]["limiar_todos"]
    svg_dispersao(B3 / "teste2_excedente_x_rendimento.svg",
                  [(s["exced"], s["rel"], str(s["ano"]), s["rel"] <= 0.85) for s in tab],
                  "Excedente hídrico de 1/set a 30/nov, mm (NASA POWER, balanço FAO-56)",
                  "Rendimento / mediana dos vizinhos (IBGE PAM)",
                  "Alto Vale do Itajaí: excesso de chuva x quebra da cebola (1984–2025)", limiar_x=lim)
