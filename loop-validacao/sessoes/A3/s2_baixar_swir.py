"""Baixa recortes de Sentinel-2 L2A (B11, B12) para NDTI (indice de palhada) sobre Ituporanga, 2019-2024.
Recorte: 5 x 5 km centrado em -27.414, -49.601 (EPSG:32722, 10 m). Saida: raw/s2/cubo_swir.npz"""
import json, glob, os, sys, numpy as np, rasterio
from rasterio.windows import from_bounds
from rasterio.warp import transform
from concurrent.futures import ThreadPoolExecutor
os.environ.update(GDAL_DISABLE_READDIR_ON_OPEN='EMPTY_DIR', CPL_VSIL_CURL_ALLOWED_EXTENSIONS='.tif', GDAL_HTTP_MAX_RETRY='4', GDAL_HTTP_RETRY_DELAY='2', AWS_NO_SIGN_REQUEST='YES')
LON, LAT, HALF = -49.601, -27.414, 2500
xs, ys = transform('EPSG:4326', 'EPSG:32722', [LON], [LAT])
cx, cy = round(xs[0] / 10) * 10, round(ys[0] / 10) * 10
B = (cx - HALF, cy - HALF, cx + HALF, cy + HALF)
items = {}
for f in sorted(glob.glob('raw/s2/stac_*.json')):
    for x in json.load(open(f))['features']:
        d = x['properties']['datetime'][:10]
        # fica com a versao de processamento mais nova por data
        if d not in items or x['id'] > items[d]['id']:
            items[d] = x
dates = sorted(items)
print(len(dates), 'datas', file=sys.stderr)
def read(href, res):
    with rasterio.open(href) as src:
        w = from_bounds(*B, transform=src.transform)
        a = src.read(1, window=w, boundless=True, fill_value=0)
        return a
def job(d):
    it = items[d]['assets']
    try:
        red = read(it['swir16']['href'], 20)   # B11 (20 m)
        nir = read(it['swir22']['href'], 20)   # B12 (20 m)
        scl = np.zeros((1, 1), np.uint8)
        p = items[d]['properties']
        off = 1000.0 if (p.get('s2:processing_baseline', '00') >= '04.00' and not p.get('earthsearch:boa_offset_applied', False)) else 0.0
        return d, red, nir, scl, off
    except Exception as e:
        print('falha', d, e, file=sys.stderr); return None
out = []
with ThreadPoolExecutor(12) as ex:
    for i, r in enumerate(ex.map(job, dates)):
        if r: out.append(r)
        if i % 20 == 0: print(i, file=sys.stderr)
out.sort(key=lambda r: r[0])
np.savez_compressed('raw/s2/cubo_swir.npz', dates=np.array([r[0] for r in out]),
    b11=np.stack([r[1] for r in out]).astype(np.uint16), b12=np.stack([r[2] for r in out]).astype(np.uint16),
    off=np.array([r[4] for r in out]), bounds=np.array(B))
print('ok', len(out), out[0][1].shape)
