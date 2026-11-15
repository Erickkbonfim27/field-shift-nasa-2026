"""B2-1: extrai NDVI e NDTI do Sentinel-2 L2A (coleção C1, Earth Search) para os
municípios do teste, numa grade de 40 m recortada pelo polígono do IBGE.

Saída: dados/s2/<cod_ibge>.npz com ndvi[n_cenas, n_pix], ndti[n_cenas, n_pix],
datas[n_cenas] (NaN onde há nuvem, sombra, água ou falta de dado).

Rodar com o venv que tem rasterio, pyproj e shapely:
  python s2_extrair.py
"""
import json, os, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor, as_completed

import numpy as np
import rasterio
from rasterio.features import rasterize
from rasterio.windows import from_bounds
from rasterio.enums import Resampling
from pyproj import Transformer
from shapely.geometry import shape, box
from shapely.ops import transform as shp_transform

AQUI = os.path.dirname(os.path.abspath(__file__))
DADOS = os.path.join(AQUI, "dados")
SAIDA = os.path.join(DADOS, "s2")
os.makedirs(SAIDA, exist_ok=True)

os.environ.setdefault("GDAL_DISABLE_READDIR_ON_OPEN", "EMPTY_DIR")
os.environ.setdefault("GDAL_HTTP_MULTIRANGE", "YES")
os.environ.setdefault("GDAL_HTTP_MERGE_CONSECUTIVE_RANGES", "YES")
os.environ.setdefault("CPL_VSIL_CURL_ALLOWED_EXTENSIONS", ".tif")
os.environ.setdefault("GDAL_CACHEMAX", "1024")

MUNIS = {
    "AV": "4208500 4201901 4200705 4212700 4207403 4204194 4209805 4219200 4201802 4200200",
    "EO": "4217204 4206405 4204905 4202081 4212239 4202099 4215208 4200804",
}
BBOX = {"AV": [-49.95, -27.9, -49.1, -27.2], "EO": [-53.8, -26.98, -53.18, -26.42]}
PERIODO = "2019-10-01T00:00:00Z/2021-09-30T23:59:59Z"
NUVEM_MAX = 60
RES = 40.0
STAC = "https://earth-search.aws.element84.com/v1/search"


def stac_busca(bbox):
    feats, body = [], {
        "collections": ["sentinel-2-c1-l2a"], "bbox": bbox, "datetime": PERIODO,
        "limit": 200, "query": {"eo:cloud_cover": {"lt": NUVEM_MAX}},
    }
    url = STAC
    while True:
        out = subprocess.run(["curl", "-s", "-m", "120", url, "-H", "Content-Type: application/json",
                              "-d", json.dumps(body)], capture_output=True, text=True).stdout
        d = json.loads(out)
        feats += d["features"]
        nxt = [l for l in d.get("links", []) if l.get("rel") == "next"]
        if not nxt:
            return feats
        body = nxt[0].get("body", body)
        url = nxt[0]["href"]


def poligono(cod):
    g = json.load(open(os.path.join(DADOS, "malhas", f"{cod}.geojson")))
    return shape(g["features"][0]["geometry"])


def main():
    trabalhos = []  # (cod, tile, crs, window bounds, mask, transform)
    cenas_por_tile = {}
    for grp, ids in MUNIS.items():
        feats = stac_busca(BBOX[grp])
        print(grp, "cenas", len(feats), flush=True)
        por_tile = {}
        for f in feats:
            por_tile.setdefault(f["properties"]["grid:code"], []).append(f)
        # geometria e CRS de cada quadrícula
        info = {}
        for t, fs in por_tile.items():
            epsg = fs[0]["properties"]["proj:code"] if "proj:code" in fs[0]["properties"] else f"EPSG:{fs[0]['properties']['proj:epsg']}"
            with rasterio.open(fs[0]["assets"]["red"]["href"]) as s:
                info[t] = (s.crs, s.bounds)
            cenas_por_tile[t] = fs
        for cod in ids.split():
            pol = poligono(cod)
            melhor = None
            for t, (crs, b) in info.items():
                tr = Transformer.from_crs("EPSG:4326", crs, always_xy=True)
                p = shp_transform(tr.transform, pol)
                frac = p.intersection(box(*b).buffer(-200)).area / p.area
                if melhor is None or frac > melhor[0]:
                    melhor = (frac, t, crs, p)
            frac, t, crs, p = melhor
            x0, y0, x1, y1 = p.bounds
            x0, y0 = np.floor(x0 / RES) * RES, np.floor(y0 / RES) * RES
            x1, y1 = np.ceil(x1 / RES) * RES, np.ceil(y1 / RES) * RES
            w, h = int((x1 - x0) / RES), int((y1 - y0) / RES)
            tf = rasterio.transform.from_origin(x0, y1, RES, RES)
            mask = rasterize([(p, 1)], out_shape=(h, w), transform=tf, fill=0, dtype="uint8").astype(bool)
            print(f"  {cod} -> {t} (fração dentro {frac:.2f}), {mask.sum()} pixels", flush=True)
            trabalhos.append((cod, t, (x0, y0, x1, y1), (h, w), mask))

    def ler(href, bounds, shape_):
        for tent in range(4):
            try:
                with rasterio.open(href) as s:
                    win = from_bounds(*bounds, transform=s.transform)
                    return s.read(1, window=win, out_shape=shape_, boundless=True, fill_value=0,
                                  resampling=Resampling.nearest)
            except Exception as e:
                err = e
                time.sleep(2 + 3 * tent)
        print("    falhou", href, err, flush=True)
        return None

    def processa_cena(f, alvos):
        a = f["assets"]
        res = {}
        for cod, t, bounds, shape_, mask in alvos:
            bandas = {k: ler(a[k]["href"], bounds, shape_) for k in ["red", "nir", "swir16", "swir22", "scl"]}
            if any(v is None for v in bandas.values()):
                continue
            scl = bandas["scl"][mask]
            ok = np.isin(scl, [4, 5])
            r, n, s1, s2 = [(bandas[k][mask].astype("float32") - 1000.0) / 10000.0 for k in ["red", "nir", "swir16", "swir22"]]
            for arr in (r, n, s1, s2):
                ok &= arr > 0
            with np.errstate(divide="ignore", invalid="ignore"):
                ndvi = np.where(ok, (n - r) / (n + r), np.nan).astype("float32")
                ndti = np.where(ok, (s1 - s2) / (s1 + s2), np.nan).astype("float32")
            res[cod] = (ndvi, ndti)
        return f["properties"]["datetime"][:10], f["id"], res

    resultados = {cod: [] for cod, *_ in trabalhos}
    for t, fs in cenas_por_tile.items():
        alvos = [x for x in trabalhos if x[1] == t]
        if not alvos:
            continue
        print(f"quadrícula {t}: {len(fs)} cenas, {len(alvos)} municípios", flush=True)
        t0 = time.time()
        with ThreadPoolExecutor(max_workers=12) as ex:
            futs = [ex.submit(processa_cena, f, alvos) for f in fs]
            for i, fu in enumerate(as_completed(futs)):
                data, fid, res = fu.result()
                for cod, v in res.items():
                    resultados[cod].append((data, fid, v[0], v[1]))
                if i % 10 == 0:
                    print(f"  {i+1}/{len(fs)} cenas, {time.time()-t0:.0f}s", flush=True)
    for cod, lst in resultados.items():
        lst.sort()
        np.savez_compressed(os.path.join(SAIDA, f"{cod}.npz"),
                            datas=np.array([x[0] for x in lst]), ids=np.array([x[1] for x in lst]),
                            ndvi=np.stack([x[2] for x in lst]), ndti=np.stack([x[3] for x in lst]))
        print("salvo", cod, len(lst), flush=True)


if __name__ == "__main__":
    main()
