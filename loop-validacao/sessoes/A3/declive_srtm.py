"""Declive (%) do SRTM 1" (tile skadi S28W050) reamostrado para a grade do recorte Sentinel-2 (EPSG:32722, 10 m)."""
import numpy as np, rasterio
from rasterio.warp import reproject, Resampling
from rasterio.transform import from_origin
from rasterio.warp import transform
LON, LAT, HALF = -49.601, -27.414, 2500
xs, ys = transform('EPSG:4326', 'EPSG:32722', [LON], [LAT]); cx, cy = round(xs[0]/10)*10, round(ys[0]/10)*10
# 1) reprojeta a elevacao para UTM 30 m numa area um pouco maior, 2) declive, 3) reamostra para 10 m
big = 3000; t30 = from_origin(cx-big, cy+big, 30, 30); n30 = 2*big//30
dem = np.zeros((n30, n30), np.float32)
with rasterio.open('raw/srtm/S28W050.hgt') as src:
    reproject(rasterio.band(src, 1), dem, dst_transform=t30, dst_crs='EPSG:32722', resampling=Resampling.bilinear)
gy, gx = np.gradient(dem, 30)
slope = np.hypot(gx, gy) * 100
t10 = from_origin(cx-HALF, cy+HALF, 10, 10); out = np.zeros((500, 500), np.float32); dem10 = np.zeros((500,500), np.float32)
reproject(slope, out, src_transform=t30, src_crs='EPSG:32722', dst_transform=t10, dst_crs='EPSG:32722', resampling=Resampling.bilinear)
reproject(dem, dem10, src_transform=t30, src_crs='EPSG:32722', dst_transform=t10, dst_crs='EPSG:32722', resampling=Resampling.bilinear)
np.savez_compressed('declive.npz', slope=out, dem=dem10)
print('elev min/med/max', dem10.min(), np.median(dem10), dem10.max())
print('declive %: p10 p50 p90', np.percentile(out, [10, 50, 90]).round(1), ' frac>20%:', (out > 20).mean().round(2))
