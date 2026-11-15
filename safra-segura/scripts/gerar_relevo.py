#!/usr/bin/env python3
"""Gera o relevo do app a partir do SRTM 1" (tiles públicos "skadi", NASA/USGS).

Monta um mosaico com todas as folhas que cobrem a malha da região (dados/bruto/malha_oeste.json)
e grava em dados/gerado/relevo.json dois PNG em base64:
  - classes de declive da Embrapa (0..5) a ~90 m, em tons de cinza (valor do pixel = classe)
  - sombreado do relevo a ~270 m, para o fundo do mapa
Folha que faltar em dados/bruto/srtm/ vira área sem dado (classe 0, sombreado neutro) e é avisada.
Sem dependências além de numpy e zlib.

Baixar uma folha:  https://s3.amazonaws.com/elevation-tiles-prod/skadi/S28/S28W053.hgt.gz
(o nome é o canto sudoeste: S28W053 cobre lat -28 a -27 e lon -53 a -52)
"""
import base64, gzip, json, math, struct, zlib
from pathlib import Path
import numpy as np

RAIZ = Path(__file__).resolve().parent.parent
BRUTO = RAIZ / "dados" / "bruto"
GERADO = RAIZ / "dados" / "gerado"
N = 3601          # pixels por lado de uma folha 1"
K90 = 3           # 1" -> ~90 m
K270 = 3          # ~90 m -> ~270 m (sombreado)
CORTES = [3, 8, 20, 45, 75]  # Embrapa: plano, suave ondulado, ondulado, forte ondulado, montanhoso, escarpado


def limites_da_malha():
    g = json.load(open(BRUTO / "malha_oeste.json"))
    xs, ys = [], []

    def anda(c):
        if isinstance(c[0], (int, float)):
            xs.append(c[0]); ys.append(c[1])
        else:
            for x in c:
                anda(x)
    for f in g["features"]:
        anda(f["geometry"]["coordinates"])
    return math.floor(min(xs)), math.floor(min(ys)), math.ceil(max(xs)), math.ceil(max(ys))


def folha(lat_sul, lon_oeste):
    """Folha cujo canto sudoeste é (lat_sul, lon_oeste), reamostrada para ~90 m (1200 x 1200)."""
    nome = f"{'S' if lat_sul < 0 else 'N'}{abs(lat_sul):02d}{'W' if lon_oeste < 0 else 'E'}{abs(lon_oeste):03d}"
    arq = BRUTO / "srtm" / f"{nome}.hgt.gz"
    lado = (N - 1) // K90
    if not arq.exists():
        print(f"  falta {nome}: área sem relevo")
        return np.full((lado, lado), np.nan), nome, False
    z = np.frombuffer(gzip.open(arq).read(), dtype=">i2").reshape(N, N).astype(np.float32)
    z = z[:-1, :-1]  # a última linha e coluna repetem a borda da folha vizinha
    z[z < -1000] = np.nan
    return np.nanmean(z.reshape(lado, K90, lado, K90), axis=(1, 3)), nome, True


def png_gray(arr, alfa=None):
    a = arr.astype(np.uint8)
    tipo = 0
    if alfa is not None:
        a = np.dstack([a, alfa.astype(np.uint8)]).reshape(a.shape[0], -1)
        tipo = 4  # cinza + alfa
    a = np.ascontiguousarray(a)
    h = a.shape[0]
    w = arr.shape[1]
    raw = b"".join(b"\x00" + a[i].tobytes() for i in range(h))

    def chunk(t, d):
        c = struct.pack(">I", len(d)) + t + d
        return c + struct.pack(">I", zlib.crc32(t + d) & 0xFFFFFFFF)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, tipo, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b""))


oeste, sul, leste, norte = limites_da_malha()
print(f"Região: lon {oeste} a {leste}, lat {sul} a {norte}")
linhas, usadas = [], []
for lat_sul in range(norte - 1, sul - 1, -1):           # de norte para sul
    linha = []
    for lon_oeste in range(oeste, leste):                 # de oeste para leste
        z, nome, ok = folha(lat_sul, lon_oeste)
        linha.append(z)
        if ok:
            usadas.append(nome)
    linhas.append(np.hstack(linha))
z90 = np.vstack(linhas)
print(f"Mosaico ~90 m: {z90.shape[1]} x {z90.shape[0]} px, folhas: {', '.join(usadas)}")

def mascara(h, w):
    """True dentro dos municípios da malha. Rasteriza pela regra par-ímpar, linha a linha."""
    g = json.load(open(BRUTO / "malha_oeste.json"))
    arestas = []
    for f in g["features"]:
        geo = f["geometry"]
        polys = geo["coordinates"] if geo["type"] == "MultiPolygon" else [geo["coordinates"]]
        for poly in polys:
            for anel in poly:
                a = np.array(anel)
                arestas.append(np.hstack([a[:-1], a[1:]]))
    E = np.vstack(arestas)
    x1, y1, x2, y2 = E[:, 0], E[:, 1], E[:, 2], E[:, 3]
    m = np.zeros((h, w), dtype=bool)
    for r in range(h):
        lat = norte - (r + 0.5) / h * (norte - sul)
        cruza = (y1 > lat) != (y2 > lat)
        if not cruza.any():
            continue
        xs = x1[cruza] + (lat - y1[cruza]) * (x2[cruza] - x1[cruza]) / (y2[cruza] - y1[cruza])
        cols = np.sort((xs - oeste) / (leste - oeste) * w)
        for a, b in zip(cols[0::2], cols[1::2]):
            m[r, max(0, int(round(a))):min(w, int(round(b)))] = True
    return m


lat_c = math.radians((sul + norte) / 2)
dy = K90 * 30.87
dx = dy * math.cos(lat_c)
gy, gx = np.gradient(z90, dy, dx)
decl = np.nan_to_num(np.hypot(gx, gy) * 100)
classe = np.digitize(decl, CORTES).astype(np.uint8)
dentro = mascara(*classe.shape)
classe[~dentro] = 6  # 6 = fora da região (transparente no app)
print(f"Dentro da região: {100 * dentro.mean():.0f}% do mosaico")

h, w = (z90.shape[0] // K270) * K270, (z90.shape[1] // K270) * K270
z270 = np.nanmean(z90[:h, :w].reshape(h // K270, K270, w // K270, K270), axis=(1, 3))
media = np.nanmean(z270)
gy2, gx2 = np.gradient(np.nan_to_num(z270, nan=media), dy * K270, dx * K270)
inclin = np.arctan(np.hypot(gx2, gy2) * 2.0)
aspecto = np.arctan2(-gx2, gy2)
az, alt = math.radians(315), math.radians(45)
hs = np.sin(alt) * np.cos(inclin) + np.cos(alt) * np.sin(inclin) * np.cos(az - aspecto)
hs = np.clip((hs - hs.min()) / (hs.max() - hs.min()) * 255, 0, 255)

dentro270 = dentro[:h, :w].reshape(h // K270, K270, w // K270, K270).any(axis=(1, 3))
hs[~dentro270] = 0  # valor constante fora da região comprime melhor
p1, p2 = png_gray(classe), png_gray(hs, np.where(dentro270, 255, 0))
out = dict(bbox=[oeste, sul, leste, norte],
           classe=dict(w=classe.shape[1], h=classe.shape[0], png=base64.b64encode(p1).decode(), res_m=round(dy)),
           sombra=dict(w=hs.shape[1], h=hs.shape[0], png=base64.b64encode(p2).decode()),
           classes=["plano (0–3%)", "suave ondulado (3–8%)", "ondulado (8–20%)", "forte ondulado (20–45%)", "montanhoso (45–75%)", "escarpado (>75%)"],
           folhas=usadas, fonte="SRTM 1\" (NASA/USGS), reamostrado; classes de relevo da Embrapa")
json.dump(out, open(GERADO / "relevo.json", "w"))
print(f"classes {classe.shape[1]}x{classe.shape[0]} ({round(len(p1)/1e3)} KB) | sombreado {hs.shape[1]}x{hs.shape[0]} ({round(len(p2)/1e3)} KB)")
print("distribuição das classes dentro da região (%):", [round(100 * float(np.mean(classe[dentro] == i)), 1) for i in range(6)])
