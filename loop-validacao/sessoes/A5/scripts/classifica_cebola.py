"""A5-2: estima a área de cebola em Ituporanga com regras de fenologia do NDVI (Sentinel-2), só com imagens até 31/out.

Regra (pixel = cebola):
  - AGO (16/jul-31/ago) < LIM_AGO     -> solo exposto, palha ou muda recém-transplantada (tira mata, pasto, trigo)
  - min(JUN, AGO) < LIM_BAIXO         -> teve fase baixa no inverno
  - OUT (1-31/out) >= T                -> verde em outubro (cebola perto do pico)
  - OUT - AGO >= SUBIDA                -> subiu de agosto para outubro
  T é o único parâmetro calibrado: escolhido na safra de calibração para bater a área plantada do IBGE PAM.
Área = fração de pixels "cebola" entre os pixels com dado em AGO e OUT x área do município (assume nuvem ao acaso).
Uso: python classifica_cebola.py <pasta_npz> <pam_json> <ano_calibracao> <anos> <saida_json>
"""
import sys, json
import numpy as np
from scipy import ndimage

PASTA, PAM, ANO_CAL, ANOS, SAIDA = sys.argv[1], sys.argv[2], int(sys.argv[3]), [int(a) for a in sys.argv[4].split(",")], sys.argv[5]
LIM_AGO, LIM_BAIXO, SUBIDA = 0.45, 0.40, 0.20
m = np.load(f"{PASTA}/mascara_municipio.npz")["m"]
AREA_MUN = m.sum() / 100.0  # ha (pixel de 10 m = 0,01 ha)
pam = {int(r["D3N"]): float(r["V"]) for r in json.load(open(PAM))[1:] if r["D2N"].startswith("Área plantada")}

def classifica(c, T, fim="OUT"):
    jun, ago, out = c["JUN"], c["AGO"], c[fim]
    base = np.where(np.isfinite(ago), ago, jun)
    valido = m & np.isfinite(base) & np.isfinite(out)
    with np.errstate(invalid="ignore"):
        ceb = valido & (base < LIM_AGO) & (np.fmin(jun, ago) < LIM_BAIXO) & (out >= T) & (out - base >= SUBIDA)
    ceb = ndimage.binary_opening(ceb, structure=np.ones((2, 2)))  # tira pixel solto (< 4 px = 0,04 ha)
    return ceb, valido

def area(c, T, fim="OUT"):
    ceb, valido = classifica(c, T, fim)
    fv = valido.sum() / m.sum()
    return (ceb.sum() / max(valido.sum(), 1)) * AREA_MUN, fv

comp = {a: dict(np.load(f"{PASTA}/comp_{a}.npz")) for a in ANOS}
Ts = np.round(np.arange(0.40, 0.86, 0.01), 2)
curva = {a: [area(comp[a], t)[0] for t in Ts] for a in ANOS}
alvo = pam[ANO_CAL]
i_cal = int(np.argmin([abs(v - alvo) for v in curva[ANO_CAL]]))
T = float(Ts[i_cal])
res = {"T_calibrado": T, "ano_calibracao": ANO_CAL, "area_municipio_ha": AREA_MUN, "safras": {}}
for a in ANOS:
    A, fv = area(comp[a], T)
    np.savez_compressed(f"{PASTA}/cebola_{a}.npz", c=classifica(comp[a], T)[0])  # usada na A5-3
    prev = pam.get(a - 1)
    res["safras"][a] = dict(
        area_sat_ha=round(A), pam_plantada_ha=pam.get(a), erro_pct=round(100 * (A - pam[a]) / pam[a], 1) if a in pam else None,
        persistencia_ha=prev, erro_persist_pct=round(100 * (prev - pam[a]) / pam[a], 1) if prev and a in pam else None,
        fracao_sem_nuvem=round(fv, 2),
        area_T_menos005=round(curva[a][max(i_cal - 5, 0)]), area_T_mais005=round(curva[a][min(i_cal + 5, len(Ts) - 1)]),
        area_com_novembro=round(area(comp[a], T, "NOV")[0]) if np.isfinite(comp[a]["NOV"][m]).any() else None,
    )
    print(a, res["safras"][a])
res["curva_T"] = {str(a): dict(zip([str(t) for t in Ts], [round(v) for v in curva[a]])) for a in ANOS}
json.dump(res, open(SAIDA, "w"), ensure_ascii=False, indent=1)
print("T calibrado em", ANO_CAL, "=", T)
