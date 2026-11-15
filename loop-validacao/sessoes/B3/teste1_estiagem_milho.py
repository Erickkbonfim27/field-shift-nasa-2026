#!/usr/bin/env python3
"""B3-1: alerta de estiagem na floração do milho (São Miguel do Oeste).
Indicador: ISNA (ETa/ETc) de 20/set a 10/jan, balanço FAO-56 com NASA POWER.
Conferência: rendimento do milho, IBGE PAM, microrregião 42001 (e município 4217204)."""
import datetime as dt, json, statistics as st, sys
from comum import *

pw = Power("sao_miguel_do_oeste")
FASES, KC = (25, 40, 45, 30), (0.30, 1.20, 0.60)  # FAO-56, milho grão, ~140 dias
CAD = 125 * 1.0  # solo médio (GAEZ v5, 125 mm/m) x raiz 1,0 m
PLANTIO = (9, 20)
DECISAO = (1, 10)
KY = (0.4, 0.4, 1.5, 0.5)


def safra(ano_colheita, plantio=PLANTIO, decisao=DECISAO):
    pl = dt.date(ano_colheita - 1, *plantio)
    fim_ciclo = pl + dt.timedelta(sum(FASES))
    b = balanco(pw, pl, fim_ciclo, FASES, KC, CAD)
    if b is None: return None
    dec = dt.date(ano_colheita, *decisao)
    ate = [x for x in b if x["d"] <= dec]
    isna_dec = sum(x["eta"] for x in ate) / sum(x["etc"] for x in ate)
    # rendimento relativo do ciclo todo (Ky por fase), só para checar o modelo
    lim = [0, FASES[0], FASES[0] + FASES[1], FASES[0] + FASES[1] + FASES[2], 10 ** 6]
    y = 1.0
    for f in range(4):
        g = [x for x in b if lim[f] <= x["k"] < lim[f + 1]]
        isna = sum(x["eta"] for x in g) / sum(x["etc"] for x in g)
        y *= max(0, 1 - KY[f] * (1 - isna))
    chuva_nd = sum(pw.chuva[k] for _, k in dias(dt.date(ano_colheita - 1, 11, 1), dt.date(ano_colheita - 1, 12, 31)))
    gw = [pw.v("GWETROOT", k) for _, k in dias(dt.date(ano_colheita - 1, 12, 1), dt.date(ano_colheita, 1, 10))]
    return dict(ano=ano_colheita, isna_dec=isna_dec, y_ciclo=y, chuva_novdez=chuva_nd, gwetroot_dez=st.mean(gw))


def avaliar(arquivo_ibge, nome):
    rend = ibge_serie(arquivo_ibge, "Rendimento")
    rel = rend_relativo(rend)
    linhas = [s for a in range(1985, 2026) if a in rel and (s := safra(a))]
    for s in linhas: s["rel"] = rel[s["ano"]]
    ruins = [s["rel"] <= 0.85 for s in linhas]
    nb, n = sum(ruins), len(linhas)
    res = dict(base=nome, n=n, ruins=nb, anos_ruins=[s["ano"] for s, r in zip(linhas, ruins) if r])
    for ind, sentido in (("isna_dec", -1), ("chuva_novdez", -1), ("gwetroot_dez", -1), ("y_ciclo", -1)):
        xs = [s[ind] for s in linhas]
        L = loo(xs, ruins, sentido)
        res[ind] = dict(spearman=round(spearman(xs, [s["rel"] for s in linhas]), 2),
                        p=round(p_perm(xs, [s["rel"] for s in linhas]), 4),
                        limiar_todos=round(melhor_limiar(xs, ruins, sentido), 3),
                        acertos=f'{L["acertos"]}/{L["ruins"]}', falsos=L["falsos"],
                        frac_falsos=round(L["frac_falsos"], 2) if L["frac_falsos"] is not None else None,
                        anos_alerta=[s["ano"] for s, a in zip(linhas, L["alertas"]) if a])
    p = nb / n
    res["linha_base_acaso"] = dict(acertos_esperados=round(p * nb, 1), frac_falsos=round(1 - p, 2))
    return res, linhas


if __name__ == "__main__":
    out = {}
    for arq, nome in (("milho_micro_smo.json", "microrregião 42001"), ("milho_smo.json", "município 4217204")):
        r, linhas = avaliar(arq, nome)
        out[nome] = r
        print(json.dumps(r, ensure_ascii=False, indent=1))
        if nome.startswith("micro"):
            tab = linhas
    # sensibilidade: data de decisão e plantio
    sens = {}
    for pl, dec in (((9, 20), (12, 31)), ((9, 20), (1, 10)), ((9, 20), (1, 31)), ((10, 10), (1, 10)), ((9, 1), (1, 10))):
        rend = rend_relativo(ibge_serie("milho_micro_smo.json", "Rendimento"))
        ls = [s for a in range(1985, 2026) if a in rend and (s := safra(a, pl, dec))]
        xs = [s["isna_dec"] for s in ls]; rr = [rend[s["ano"]] for s in ls]; ru = [x <= 0.85 for x in rr]
        L = loo(xs, ru, -1)
        sens[f"plantio {pl[1]:02d}/{pl[0]:02d}, decisão {dec[1]:02d}/{dec[0]:02d}"] = dict(
            spearman=round(spearman(xs, rr), 2), acertos=f'{L["acertos"]}/{L["ruins"]}', falsos=L["falsos"])
    out["sensibilidade_isna_micro"] = sens
    print(json.dumps(sens, ensure_ascii=False, indent=1))
    json.dump(dict(resultado=out, tabela=[{k: (round(v, 3) if isinstance(v, float) else v) for k, v in s.items()} for s in tab]),
              open(B3 / "teste1_resultado.json", "w"), ensure_ascii=False, indent=1)
    lim = out["microrregião 42001"]["isna_dec"]["limiar_todos"]
    svg_dispersao(B3 / "teste1_isna_x_rendimento.svg",
                  [(s["isna_dec"], s["rel"], str(s["ano"]), s["rel"] <= 0.85) for s in tab],
                  "ISNA do milho de 20/set a 10/jan (NASA POWER, balanço FAO-56)",
                  "Rendimento / mediana dos vizinhos (IBGE PAM)",
                  "Extremo Oeste SC: falta de água até 10/jan x quebra do milho (1985–2025)", limiar_x=lim)
