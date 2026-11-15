#!/usr/bin/env python3
"""V5 · baixa NASA POWER (1984-2025) e IBGE PAM (milho 40122, feijão 40112) por curl."""
import subprocess
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

D = Path(__file__).resolve().parent / "dados"
D.mkdir(exist_ok=True)
LOCAIS = {  # chave: (lat, lon, código IBGE)
    "quixada": (-4.97, -39.02, "2311306"),
    "quixeramobim": (-5.20, -39.29, "2311405"),
    "crateus": (-5.18, -40.65, "2304103"),
    "taua": (-6.00, -40.30, "2313302"),
    "irece": (-11.30, -41.85, "2914604"),
    "serratalhada": (-7.99, -38.30, "2613909"),
    "patos": (-7.02, -37.28, "2510808"),
    "bonfim": (-10.46, -40.19, "2930105"),
}
PAR = "PRECTOTCORR,T2M,T2M_MAX,T2M_MIN,RH2M,WS2M,ALLSKY_SFC_SW_DWN"


def baixa(k):
    lat, lon, ibge = LOCAIS[k]
    u1 = (f"https://power.larc.nasa.gov/api/temporal/daily/point?parameters={PAR}&community=AG"
          f"&longitude={lon}&latitude={lat}&start=19840101&end=20251231&format=JSON")
    u2 = f"https://apisidra.ibge.gov.br/values/t/5457/n6/{ibge}/v/112,216/p/all/c782/40122,40112"
    for u, f in ((u1, D / f"power_{k}.json"), (u2, D / f"pam_{k}.json")):
        if f.exists() and f.stat().st_size > 1000:
            continue
        subprocess.run(["curl", "-s", "--max-time", "240", u, "-o", str(f)], check=False)
    return k


with ThreadPoolExecutor(4) as ex:
    for k in ex.map(baixa, LOCAIS):
        print("ok", k)
