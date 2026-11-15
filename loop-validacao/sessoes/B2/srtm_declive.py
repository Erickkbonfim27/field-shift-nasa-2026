"""Declive (SRTM 1", tile S28W050) na mesma grade de 40 m (UTM 22S) usada em s2_extrair.py,
para os municípios do Alto Vale. Saída: dados/declive_<cod>.npy (declive em %, só pixels do polígono,
na mesma ordem do npz do Sentinel-2).
Rodar com o venv (rasterio, pyproj, shapely).
"""
import json, os
import numpy as np
import rasterio
from rasterio.features import rasterize
from rasterio.warp import reproject, Resampling
from pyproj import Transformer
from shapely.geometry import shape
from shapely.ops import transform as shp_transform

AQUI = os.path.dirname(os.path.abspath(__file__))
D = os.path.join(AQUI, "dados")
RES = 40.0
CRS = "EPSG:32722"

hgt = os.path.join(D, "srtm", "S28W050.hgt")
n = 3601
z = np.fromfile(hgt, ">i2").reshape(n, n).astype("float32")
z[z < -1000] = np.nan
src_tf = rasterio.transform.from_origin(-50 - 0.5 / 3600, -27 + 0.5 / 3600, 1 / 3600, 1 / 3600)

for cod in "4208500 4201901 4200705 4212700 4207403 4204194 4209805 4219200 4201802 4200200".split():
    g = json.load(open(os.path.join(D, "malhas", f"{cod}.geojson")))
    pol = shape(g["features"][0]["geometry"])
    b = pol.bounds
    if not (-50 <= b[0] and b[2] <= -49 and -28 <= b[1] and b[3] <= -27):
        print(cod, "fora do tile SRTM, pulado"); continue
    p = shp_transform(Transformer.from_crs("EPSG:4326", CRS, always_xy=True).transform, pol)
    x0, y0, x1, y1 = p.bounds
    x0, y0 = np.floor(x0 / RES) * RES, np.floor(y0 / RES) * RES
    x1, y1 = np.ceil(x1 / RES) * RES, np.ceil(y1 / RES) * RES
    w, h = int((x1 - x0) / RES), int((y1 - y0) / RES)
    tf = rasterio.transform.from_origin(x0, y1, RES, RES)
    mask = rasterize([(p, 1)], out_shape=(h, w), transform=tf, fill=0, dtype="uint8").astype(bool)
    # reprojeta a 20 m (bilinear) e calcula o declive, depois agrega para 40 m
    dz = np.full((h * 2, w * 2), np.nan, "float32")
    reproject(z, dz, src_transform=src_tf, src_crs="EPSG:4326", dst_transform=rasterio.transform.from_origin(x0, y1, 20, 20),
              dst_crs=CRS, resampling=Resampling.bilinear)
    gy, gx = np.gradient(dz, 20.0)
    dec = np.hypot(gx, gy) * 100
    dec40 = dec.reshape(h, 2, w, 2).mean(axis=(1, 3))
    np.save(os.path.join(D, f"declive_{cod}.npy"), dec40[mask].astype("float32"))
    print(cod, "pixels", mask.sum(), "declive mediano %.1f%%" % np.nanmedian(dec40[mask]))
