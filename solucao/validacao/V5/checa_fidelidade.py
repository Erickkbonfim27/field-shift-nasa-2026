"""Confere que motor.py reproduz prototipo/modelo/risco.py em Quixadá 2001-2025 (mesma entrada)."""
import sys, importlib.util, datetime as dt
from pathlib import Path
RAIZ = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(Path(__file__).resolve().parent))
import motor

spec = importlib.util.spec_from_file_location("risco", RAIZ / "prototipo/modelo/risco.py")
risco = importlib.util.module_from_spec(spec); spec.loader.exec_module(risco)

L = motor.Local("quixada")
# risco.py usa a altitude 190 e o POWER 2001-2025; o nosso POWER é 1984-2025 (mesma API). Compara y e plantio.
dif, n = [], 0
for cult in ("caupi", "milho"):
    for a in range(2001, 2026):
        pl_r = risco.inicio_chuva(a); pl_m = L.inicio_chuva(a)
        if pl_r is None or pl_m is None:
            dif.append((cult, a, "plantio", pl_r, pl_m)) if pl_r != pl_m else None
            continue
        yr = risco.simular(cult, "medio", pl_r)["y"]
        ym = L.simular(cult, "medio", pl_m)["y"]
        n += 1
        if abs(yr - ym) > 0.01 or pl_r != pl_m: dif.append((cult, a, pl_r, pl_m, round(yr, 3), round(ym, 3)))
print("pares comparados:", n, "| diferenças (>0,01 ou plantio diferente):", len(dif))
for d in dif[:15]: print(d)
