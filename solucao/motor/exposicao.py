"""Módulo exposicao_solo (Ituporanga): solo descoberto em mês de chuva erosiva.

Reaproveita a A3-1 (loop-validacao/sessoes/A3/a3_1_alerta.py):
- R = índice de Fournier mensal do NASA POWER (p_mês² / P_ano), recalculado aqui só com a
  biblioteca padrão (o teste confere com o R salvo pela A3-1);
- descoberto = fração de dias do mês com NDVI < 0,30 (Sentinel-2 L2A, 2019-2024), por bloco de
  50 m, salvo pela A3-1 em a3_1_blocos.npz. Ler o .npz exige numpy (conferido: instalado).
Só descreve o que foi medido. Não calcula perda de solo evitada (N1).
"""
import statistics as st

MESES = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto",
         "setembro", "outubro", "novembro", "dezembro"]
ANO0_S2 = 2019
INVERNO = (6, 7, 8)


def chuva_mensal(pw):
    m = {}
    for k, v in pw.chuva.items():
        m[(int(k[:4]), int(k[4:6]))] = m.get((int(k[:4]), int(k[4:6])), 0.0) + v
    return m


def fournier(pw):
    """{(ano, mes): p_mes^2 / P_ano} para todos os anos completos da série."""
    m = chuva_mensal(pw)
    anual = {}
    for (a, _), v in m.items():
        anual[a] = anual.get(a, 0.0) + v
    return {(a, mm): v * v / anual[a] for (a, mm), v in m.items()}


def carregar_blocos(caminho):
    import numpy as np  # só aqui: o .npz da A3-1 é formato numpy
    g = np.load(caminho)
    return {k: g[k] for k in ("bare_b", "crop_b", "Eann", "R", "slope_b")}


def bloco_mediano(B):
    """Bloco de lavoura com a exposição anual mediana (Eann da A3-1). Regra fixa do motor."""
    import numpy as np
    idx = np.argwhere(B["crop_b"])
    vals = B["Eann"][B["crop_b"]]
    o = np.argsort(vals, kind="stable")
    i, j = idx[o[len(o) // 2]]
    return int(i), int(j)


def avaliar(pw, caminho_blocos, ano_ref):
    """Último inverno com dado de satélite <= ano_ref. Escolhe o mês do inverno com maior
    exposição (R x descoberto) no bloco mediano e diz se a chuva desse mês foi forte
    (R acima da mediana de todos os meses dos anos anteriores na série do POWER)."""
    B = carregar_blocos(caminho_blocos)
    nmes = B["bare_b"].shape[0]
    anos_s2 = list(range(ANO0_S2, ANO0_S2 + nmes // 12))
    ano = max(a for a in anos_s2 if a <= ano_ref)
    R = fournier(pw)
    i, j = bloco_mediano(B)
    base = (ano - ANO0_S2) * 12
    exp = {m: R[(ano, m)] * float(B["bare_b"][base + m - 1, i, j]) for m in INVERNO}
    mes = max(INVERNO, key=lambda m: exp[m])
    descoberto = float(B["bare_b"][base + mes - 1, i, j])
    recorte = float(B["bare_b"][base + mes - 1][B["crop_b"]].mean())
    passados = [v for (a, _), v in R.items() if a < ano]
    r_mediana = st.median(passados)
    # conferência interna: o R recalculado bate com o R salvo pela A3-1?
    dif_r = max(abs(R[(ANO0_S2 + t // 12, t % 12 + 1)] - float(B["R"][t])) for t in range(nmes))
    return dict(
        ano=ano, mes=mes, mes_nome=MESES[mes - 1], bloco=[i, j], declive_pct=float(B["slope_b"][i, j]),
        fracao_descoberto=round(descoberto, 2), fracao_descoberto_recorte=round(recorte, 2),
        n_blocos_lavoura=int(B["crop_b"].sum()), R_mes=round(R[(ano, mes)], 2),
        R_mediana_meses_passados=round(r_mediana, 2), chuva_forte=R[(ano, mes)] > r_mediana,
        exposicao_inverno={MESES[m - 1]: round(exp[m], 2) for m in INVERNO},
        dif_max_R_vs_A3=dif_r, periodo_satelite=f"{anos_s2[0]}-{anos_s2[-1]}")
