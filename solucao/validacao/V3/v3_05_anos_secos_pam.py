#!/usr/bin/env python3
"""V3-05: o ganho da mistura aparece nos anos secos conhecidos? E o milho simulado acompanha a PAM/IBGE de SMO?

PAM (IBGE, tabela 5457, milho em grão, SMO, produto 40122): rendimento relativo à mediana móvel centrada de 9 anos
(mesmo tratamento da B1). O ano da PAM é o da colheita: safra de plantio a = ano de colheita a+1.
Anos secos conhecidos no Extremo Oeste/SC (estiagens): safras 2004/05, 2011/12, 2021/22 (ficha A4-3/B1, Epagri/Cepa); 2019/20 também (La Niña).
"""
import sys, json
from pathlib import Path
import numpy as np
from scipy.stats import spearmanr
sys.path.insert(0, str(Path(__file__).resolve().parent))
import modelo_v3 as V
AQUI = Path(__file__).resolve().parent
PAM = AQUI.parents[2] / "loop-validacao" / "sessoes" / "B1" / "externo" / "pam_5457.json"

d = json.load(open(PAM))[1:]
serie = {int(r["D3N"]): float(r["V"]) for r in d if r["D4C"] == "40122" and r["D1C"] == "4217204" and r["D2N"].startswith("Rendimento") and r["V"] not in ("-", "...", "X")}
anos = sorted(serie)
rel = {}
for a in anos:
    viz = sorted(serie[b] for b in anos if abs(b - a) <= 4)
    m = viz[len(viz) // 2] if len(viz) % 2 else (viz[len(viz) // 2 - 1] + viz[len(viz) // 2]) / 2
    rel[a] = serie[a] / m

out = {}
SECOS = {2004: "2004/05", 2011: "2011/12", 2019: "2019/20", 2021: "2021/22"}
for nome, cad in (("raso_ZARC_42", 42.0), ("raso_A4_87.5", 87.5), ("medio_125", 125.0), ("fundo_175", 175.0)):
    cs = V.casos(cad, scen="FAO33")
    ym = np.array([c[2] for c in cs]).reshape(-1, 5); ys = np.array([c[3] for c in cs]).reshape(-1, 5)
    mix = 0.5 * ym + 0.5 * 0.88 * ys
    ym_ano = ym.mean(axis=1); gain_ano = (mix - ym).mean(axis=1)  # ganho médio da mistura (em unidades de milho) por safra
    safras = V.SAFRAS
    xs = [ym_ano[i] for i, a in enumerate(safras) if (a + 1) in rel]; ys_pam = [rel[a + 1] for a in safras if (a + 1) in rel]
    rho = spearmanr(xs, ys_pam)
    # 8 piores PAM vs 8 piores simulados
    ap = sorted([a + 1 for a in safras if (a + 1) in rel], key=lambda y: rel[y])[:8]
    asim = sorted(safras, key=lambda a: ym_ano[safras.index(a)])[:8]
    acerto = len(set(ap) & set(a + 1 for a in asim))
    # ranking do ganho
    rank_gain = sorted(safras, key=lambda a: -gain_ano[safras.index(a)])
    top10 = rank_gain[:10]
    secos_no_top10 = [SECOS[a] for a in SECOS if a in top10]
    secos_info = {SECOS[a]: dict(milho_sim=float(ym_ano[safras.index(a)]), ganho_mistura=float(gain_ano[safras.index(a)]), pam_rel=rel.get(a + 1), posicao_ganho=rank_gain.index(a) + 1) for a in SECOS}
    out[nome] = dict(rho_milho_sim_x_pam=float(rho.statistic), p=float(rho.pvalue), n=len(xs), piores8_pam=ap, piores8_sim=[a + 1 for a in asim], acerto8=acerto,
                     top10_ganho=[f"{a}/{str(a+1)[2:]}" for a in top10], secos_no_top10=secos_no_top10, secos=secos_info,
                     ganho_medio_top10=float(np.mean([gain_ano[safras.index(a)] for a in top10])), ganho_medio_resto=float(np.mean([gain_ano[safras.index(a)] for a in safras if a not in top10])))
    print(f"== {nome}: Spearman milho sim x PAM = {rho.statistic:+.2f} (p={rho.pvalue:.3f}, n={len(xs)}) | acerto 8 piores {acerto}/8")
    print("   10 safras de maior ganho da mistura:", out[nome]["top10_ganho"], "| secos conhecidos entre elas:", secos_no_top10)
    for k, v in secos_info.items(): print(f"   {k}: milho sim {v['milho_sim']:.2f}, ganho mistura {v['ganho_mistura']:+.3f}, posição {v['posicao_ganho']}/41, PAM rel {v['pam_rel']}")
    # ganho concentrado em poucos anos?
    g = np.sort(gain_ano)[::-1]
    out[nome]["fracao_do_ganho_nos_5_melhores"] = float(g[:5].sum() / g[g > 0].sum()) if (g > 0).any() else None
    print(f"   safras com ganho > 0: {(gain_ano>0).sum()} de 41; soma do ganho positivo nas 5 maiores: {100*out[nome]['fracao_do_ganho_nos_5_melhores']:.0f}%; safras em que a mistura PERDE (ganho < -0,02): {(gain_ano < -0.02).sum()}")
json.dump(out, open(AQUI / "res_05_anos_secos_pam.json", "w"), indent=1, default=float)
