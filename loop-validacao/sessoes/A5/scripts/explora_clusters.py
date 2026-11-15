"""A5-2 (exploração): k-means nas curvas de NDVI por período, para ver as fenologias que existem no município.
Uso: python explora_clusters.py <pasta_npz> <ano>"""
import sys
import numpy as np
P, ANO = sys.argv[1], int(sys.argv[2])
m = np.load(f"{P}/mascara_municipio.npz")["m"]; c = np.load(f"{P}/comp_{ANO}.npz")
ks = sys.argv[3].split(",") if len(sys.argv) > 3 else ["JUN", "AGO", "OUT", "NOV", "DEZ"]
X = np.stack([c[k][m] for k in ks], 1); ok = np.isfinite(X).all(1)
Xo = X[ok]; rng = np.random.default_rng(0); S = Xo[rng.choice(len(Xo), min(200000, len(Xo)), replace=False)]
K = 12; C = S[rng.choice(len(S), K, replace=False)]
for _ in range(50):
    l = ((S[:, None] - C[None]) ** 2).sum(2).argmin(1)
    C = np.array([S[l == k].mean(0) if (l == k).any() else C[k] for k in range(K)])
L = np.concatenate([((Xo[i:i + 200000, None] - C[None]) ** 2).sum(2).argmin(1) for i in range(0, len(Xo), 200000)])
print(ANO, "pixels com todos os períodos:", round(ok.mean(), 2))
for k in np.argsort(C[:, 2] - C[:, 1])[::-1]:
    print(" ", " ".join(f"{ks[j]}={C[k, j]:.2f}" for j in range(len(ks))), f"área~{(L == k).sum() / 100 / ok.mean():.0f} ha")
