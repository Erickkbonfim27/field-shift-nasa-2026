"""A5-2: monta compostos de NDVI por período (mediana das observações sem nuvem) para uma safra.

A máscara SCL deixa passar névoa/nuvem fina em algumas cenas (ex.: 28/07 e 27/08/2022, mata com NDVI ~0,1).
Filtro extra: pixels de referência "sempre verdes" (percentil 80 da safra >= 0,75). Em cada cena, por bloco de
500 m x 500 m, se a mediana do NDVI dos pixels de referência do bloco for < 0,65, o bloco inteiro é descartado
naquela cena. Cena com mediana geral de referência < 0,65 é descartada inteira.
Uso: python compostos_s2.py <pasta_npz> <ano>  -> <pasta_npz>/comp_<ano>.npz
"""
import sys, glob, os, datetime as dt
import numpy as np
PASTA, ANO = sys.argv[1], int(sys.argv[2])
PER = {"JUN": ((5, 15), (7, 15)), "AGO": ((7, 16), (8, 31)), "SET": ((9, 1), (9, 30)),
       "OUT": ((10, 1), (10, 31)), "NOV": ((11, 1), (11, 30)), "DEZ": ((12, 1), (12, 31))}
B = 50  # bloco de 50 px = 500 m
m = np.load(f"{PASTA}/mascara_municipio.npz")["m"]
arqs = sorted(glob.glob(f"{PASTA}/ndvi_{ANO}-*.npz"))
cenas = {}
for f in arqs:
    q = np.load(f)["ndvi"].astype("float32"); q[q == 255] = np.nan
    cenas[dt.date.fromisoformat(os.path.basename(f)[5:15])] = q / 200
with np.errstate(all="ignore"):
    p80 = np.nanpercentile(np.stack(list(cenas.values())), 80, axis=0)
ref = m & (p80 >= 0.75)
H, W = m.shape
hb, wb = H // B, W // B
def limpa(q):
    r = np.where(ref, q, np.nan)
    if np.nanmedian(r[m]) < 0.65 if np.isfinite(r[m]).sum() > 1000 else False:
        return None
    rb = r[:hb * B, :wb * B].reshape(hb, B, wb, B)
    with np.errstate(all="ignore"):
        med = np.nanmedian(rb, axis=(1, 3)); n = np.isfinite(rb).sum(axis=(1, 3))
    ruim = (n >= 20) & (med < 0.65)
    mk = np.zeros_like(m); mk[:hb * B, :wb * B] = np.repeat(np.repeat(ruim, B, 0), B, 1)
    q = q.copy(); q[mk] = np.nan
    return q
log = []
out, info = {}, {}
limpas = {}
for d, q in cenas.items():
    c = limpa(q)
    antes = np.isfinite(q[m]).mean()
    depois = 0.0 if c is None else np.isfinite(c[m]).mean()
    log.append(f"{d} sem_nuvem_SCL={antes:.2f} depois_do_filtro={depois:.2f}")
    if c is not None:
        limpas[d] = c
for p, (a, b) in PER.items():
    d0, d1 = dt.date(ANO, *a), dt.date(ANO, *b)
    pilha = [q for d, q in limpas.items() if d0 <= d <= d1]
    if pilha:
        with np.errstate(all="ignore"):
            out[p] = np.nanmedian(np.stack(pilha), axis=0).astype("float32")
    else:
        out[p] = np.full(m.shape, np.nan, "float32")
    info[p] = (len(pilha), float(np.isfinite(out[p][m]).mean()))
np.savez_compressed(f"{PASTA}/comp_{ANO}.npz", **out)
print("\n".join(log))
for p, (n, c) in info.items():
    print(ANO, p, f"cenas={n}", f"cobertura_sem_nuvem={c:.2f}")
