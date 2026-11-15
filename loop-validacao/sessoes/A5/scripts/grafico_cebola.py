"""A5-2: mapa da cebola classificada (por safra) e curva área x limiar, mais a comparação com o IBGE PAM."""
import sys, json
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
# Uso: python grafico_cebola.py <pasta_npz> <resultado_json> <saida_png>
PASTA, RES, SAIDA = sys.argv[1], sys.argv[2], sys.argv[3]
R = json.load(open(RES))
anos = sorted(int(a) for a in R["safras"])
m = np.load(f"{PASTA}/mascara_municipio.npz")["m"]
fig = plt.figure(figsize=(13, 8))
for i, a in enumerate(anos):
    c = dict(np.load(f"{PASTA}/comp_{a}.npz"))
    jun, ago, out = c["JUN"], c["AGO"], c["OUT"]
    base = np.where(np.isfinite(ago), ago, jun)
    with np.errstate(invalid="ignore"):
        ceb = m & (base < 0.45) & (np.fmin(jun, ago) < 0.40) & (out >= R["T_calibrado"]) & (out - base >= 0.20)
    img = np.full(m.shape + (3,), 1.0)
    img[m] = [0.85, 0.85, 0.85]
    img[m & ~np.isfinite(out)] = [0.6, 0.75, 0.95]
    img[ceb] = [0.85, 0.2, 0.1]
    ax = fig.add_subplot(2, len(anos), i + 1); ax.imshow(img[::2, ::2]); ax.set_axis_off()
    s = R["safras"][str(a)]
    ax.set_title(f"safra {a}\nsatélite {s['area_sat_ha']} ha · IBGE {s['pam_plantada_ha']:.0f} ha", fontsize=9)
ax = fig.add_subplot(2, 2, 3)
for a in anos:
    cv = R["curva_T"][str(a)]
    ax.plot([float(t) for t in cv], list(cv.values()), label=str(a))
ax.axvline(R["T_calibrado"], color="k", ls="--", lw=.8)
ax.set_xlabel("limiar de NDVI em outubro (T)"); ax.set_ylabel("área estimada (ha)"); ax.legend(fontsize=8)
ax.set_title(f"Área x limiar (T calibrado em {R['ano_calibracao']} = {R['T_calibrado']})", fontsize=9)
ax = fig.add_subplot(2, 2, 4)
x = np.arange(len(anos))
ax.bar(x - .27, [R["safras"][str(a)]["pam_plantada_ha"] for a in anos], .27, label="IBGE PAM (plantada)", color="#636363")
ax.bar(x, [R["safras"][str(a)]["area_sat_ha"] for a in anos], .27, label="Sentinel-2 até 31/out", color="#d7301f")
ax.bar(x + .27, [R["safras"][str(a)]["persistencia_ha"] or np.nan for a in anos], .27, label="persistência (ano anterior)", color="#9ecae1")
ax.set_xticks(x); ax.set_xticklabels(anos); ax.set_ylabel("ha"); ax.legend(fontsize=8)
ax.set_title("Área de cebola em Ituporanga", fontsize=9)
fig.suptitle("A5-2 · Cebola por fenologia do NDVI (Sentinel-2). Vermelho = classificado como cebola; azul = sem dado em outubro (nuvem)", fontsize=10)
fig.tight_layout(); fig.savefig(SAIDA, dpi=100)
