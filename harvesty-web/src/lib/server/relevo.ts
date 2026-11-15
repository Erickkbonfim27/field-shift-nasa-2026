// Classes de declive do SRTM (~90 m) para a área desenhada. Lê o PNG gerado pelo pipeline do Harvesty.
// O PNG é simples (cinza 8 bits, filtro 0 em todas as linhas), então decodifica com zlib, sem biblioteca.
import fs from "node:fs";
import path from "node:path";
import zlib from "node:zlib";
import * as d3 from "d3";
import type { Poligono } from "@/lib/tipos";

interface Meta { bbox: [number, number, number, number]; classes: string[]; classe: { w: number; h: number } }
let raster: { w: number; h: number; px: Uint8Array; meta: Meta } | null = null;

function carregar() {
  if (raster) return raster;
  const meta = JSON.parse(fs.readFileSync(path.join(process.cwd(), "data", "relevo-meta.json"), "utf-8")) as Meta;
  const png = fs.readFileSync(path.join(process.cwd(), "public", "relevo", "classes.png"));
  let pos = 8, w = 0, h = 0;
  const idat: Buffer[] = [];
  while (pos < png.length) {
    const len = png.readUInt32BE(pos), tipo = png.toString("ascii", pos + 4, pos + 8), corpo = png.subarray(pos + 8, pos + 8 + len);
    if (tipo === "IHDR") { w = corpo.readUInt32BE(0); h = corpo.readUInt32BE(4); if (corpo[8] !== 8 || corpo[9] !== 0) throw new Error("PNG de classes fora do formato esperado"); }
    if (tipo === "IDAT") idat.push(corpo);
    pos += 12 + len;
  }
  const bruto = zlib.inflateSync(Buffer.concat(idat));
  const px = new Uint8Array(w * h);
  for (let r = 0; r < h; r++) {
    if (bruto[r * (w + 1)] !== 0) throw new Error("PNG de classes com filtro inesperado");
    px.set(bruto.subarray(r * (w + 1) + 1, (r + 1) * (w + 1)), r * w);
  }
  raster = { w, h, px, meta };
  return raster;
}

export function relevoMeta() { return carregar().meta; }

/** % da área em cada classe (0..5) e % de "morro" (declive > 20%). null se a área estiver fora do mosaico. */
export function relevoNaArea(poly: Poligono): { pct: number[]; px: number; morro: number } | null {
  const R = carregar();
  const [w, s, e, n] = R.meta.bbox, W = R.w, H = R.h;
  const xs = poly.map((p) => p[0]), ys = poly.map((p) => p[1]);
  if (Math.min(...xs) < w || Math.max(...xs) > e || Math.min(...ys) < s || Math.max(...ys) > n) return null;
  const c0 = Math.max(0, Math.floor(((Math.min(...xs) - w) / (e - w)) * W)), c1 = Math.min(W - 1, Math.ceil(((Math.max(...xs) - w) / (e - w)) * W));
  const r0 = Math.max(0, Math.floor(((n - Math.max(...ys)) / (n - s)) * H)), r1 = Math.min(H - 1, Math.ceil(((n - Math.min(...ys)) / (n - s)) * H));
  const cont = [0, 0, 0, 0, 0, 0];
  let tot = 0;
  for (let r = r0; r <= r1; r++) for (let c = c0; c <= c1; c++) {
    const lon = w + ((c + 0.5) / W) * (e - w), lat = n - ((r + 0.5) / H) * (n - s);
    if (d3.polygonContains(poly, [lon, lat])) { const k = R.px[r * W + c]; if (k < 6) { cont[k]++; tot++; } }
  }
  if (!tot) {
    const c = Math.floor(((d3.mean(xs)! - w) / (e - w)) * W), r = Math.floor(((n - d3.mean(ys)!) / (n - s)) * H);
    const k = R.px[r * W + c];
    if (k === undefined || k > 5) return null;
    cont[k]++; tot = 1;
  }
  return { pct: cont.map((v) => (100 * v) / tot), px: tot, morro: (100 * (cont[3] + cont[4] + cont[5])) / tot };
}
