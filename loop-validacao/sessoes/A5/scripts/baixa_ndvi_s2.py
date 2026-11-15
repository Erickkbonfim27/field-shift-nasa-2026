"""A5-2: baixa NDVI do Sentinel-2 L2A (Earth Search/AWS) recortado no município de Ituporanga.

Lê só a janela do município nos COGs (B04, B08 a 10 m; SCL a 20 m) e guarda NDVI em uint8
(0..200 = NDVI 0..1; 255 = nuvem/sem dado) em <saida>/ndvi_<data>.npz.
Uso: python baixa_ndvi_s2.py <pasta_dados_A5> <saida> [nuvem_max]
"""
import json, sys, os, time
import numpy as np, rasterio
from rasterio.windows import from_bounds
from rasterio.features import rasterize
from pyproj import Transformer
from shapely.geometry import shape
from shapely.ops import transform as shp_transform

DADOS, SAIDA = sys.argv[1], sys.argv[2]
NUV = float(sys.argv[3]) if len(sys.argv) > 3 else 60
os.makedirs(SAIDA, exist_ok=True)
os.environ.update(GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR", CPL_VSIL_CURL_ALLOWED_EXTENSIONS=".tif",
                  GDAL_HTTP_MULTIRANGE="YES", GDAL_HTTP_MERGE_CONSECUTIVE_RANGES="YES", AWS_NO_SIGN_REQUEST="YES")

geo = json.load(open(f"{DADOS}/limite_ituporanga.geojson"))["features"][0]["geometry"]
tr = Transformer.from_crs(4326, 32722, always_xy=True)
mun = shp_transform(lambda x, y, z=None: tr.transform(x, y), shape(geo))
xmin, ymin, xmax, ymax = [round(v / 20) * 20 for v in mun.bounds]
xmin -= 20; ymin -= 20; xmax += 20; ymax += 20
W, H = int((xmax - xmin) / 10), int((ymax - ymin) / 10)
aff = rasterio.transform.from_origin(xmin, ymax, 10, 10)
mask_mun = rasterize([(mun, 1)], out_shape=(H, W), transform=aff, fill=0, dtype="uint8").astype(bool)
np.savez_compressed(f"{SAIDA}/mascara_municipio.npz", m=mask_mun, bounds=np.array([xmin, ymin, xmax, ymax]))
print("grade", W, H, "pixels no município", mask_mun.sum(), "=", mask_mun.sum() / 100, "ha", flush=True)

itens = []
ANOS = [int(a) for a in sys.argv[4].split(",")] if len(sys.argv) > 4 else (2022, 2023, 2024, 2025)
for y in ANOS:
    fontes = [f"{DADOS}/stac_{y}.json"] + ([f"{DADOS}/stac_prim_{y}.json"] if os.path.exists(f"{DADOS}/stac_prim_{y}.json") else [])
    for arq in fontes:  # stac_prim_: cenas de jul-nov com 60-97% de nuvem (sobram pedaços limpos)
        for f in json.load(open(arq))["features"]:
            if f["properties"]["eo:cloud_cover"] < NUV and f["id"] not in {i["id"] for i in itens}:
                itens.append(f)
itens.sort(key=lambda f: f["properties"]["datetime"])
for f in itens:
    data = f["properties"]["datetime"][:10]
    out = f"{SAIDA}/ndvi_{data}.npz"
    if os.path.exists(out):
        continue
    t0 = time.time()
    try:
        bands = {}
        for k in ("red", "nir", "scl"):
            with rasterio.open(f["assets"][k]["href"]) as src:
                win = from_bounds(xmin, ymin, xmax, ymax, src.transform)
                bands[k] = src.read(1, window=win, boundless=True, fill_value=0)
        scl = np.repeat(np.repeat(bands["scl"], 2, 0), 2, 1)[:H, :W]
        # Earth Search já aplica o BOA_ADD_OFFSET (earthsearch:boa_offset_applied = True): não subtrair 1000
        assert f["properties"].get("earthsearch:boa_offset_applied", False)
        r = bands["red"][:H, :W].astype("float32")
        n = bands["nir"][:H, :W].astype("float32")
        ndvi = (n - r) / np.maximum(n + r, 1)
        ok = np.isin(scl, [4, 5, 6]) & (bands["red"][:H, :W] > 0)  # vegetação, solo, água
        q = np.where(ok, np.clip(np.round(ndvi * 200), 0, 200), 255).astype("uint8")
        np.savez_compressed(out, ndvi=q)
        fr = ok[mask_mun].mean()
        print(data, f["id"], f"livre={fr:.2f}", f"{time.time()-t0:.0f}s", flush=True)
    except Exception as e:
        print("ERRO", data, e, flush=True)
