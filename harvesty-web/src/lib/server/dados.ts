// Carrega os dados do NASA POWER (por ponto da grade) e a malha dos municípios. Só no servidor.
import fs from "node:fs";
import path from "node:path";
import * as d3 from "d3";
import type { LinhaJanela } from "@/lib/tipos";

const DIR = path.join(process.cwd(), "data");
const PUBLICO = path.join(process.cwd(), "public");

export interface Motor {
  janela_safra: { limiar_c: number; dias: number; periodo: string; linhas: LinhaJanela[]; seguro: string | null };
  limite_2m: {
    central: string | null;
    por_limiar: Record<string, string | null>;
    por_ciclo: Record<string, string | null>;
    risco_no_limite: { em10: number; ic95: [number, number]; n: number } | null;
  };
  curva_2m: { d: string; em10: number; ic95: [number, number] }[];
  seco: { regra: string; serie: Record<string, number>; alertas: { ano: number; percentil: number; n_passados: number }[] };
}

interface CelulaBruta { id: string; lat: number; lon: number; elev: number; api: string; tmin: string; tmax: string; chuva: string; motor: Motor }
export interface Celula extends Omit<CelulaBruta, "tmin" | "tmax" | "chuva"> { _b: CelulaBruta; _s?: Series }
export interface Series { tn: Int16Array; tx: Int16Array; pr: Int16Array }

interface Pacote { ini: string; ndias: number; celulas: Celula[]; t0: number; anoIni: number }

let pacote: Pacote | null = null;

function int16(b64: string): Int16Array {
  const buf = Buffer.from(b64, "base64");
  const ab = new ArrayBuffer(buf.length);
  new Uint8Array(ab).set(buf); // cópia alinhada (o Buffer pode vir com deslocamento ímpar)
  return new Int16Array(ab);
}

export function dados(): Pacote {
  if (pacote) return pacote;
  const bruto = JSON.parse(fs.readFileSync(path.join(DIR, "celulas.json"), "utf-8")) as { ini: string; ndias: number; celulas: CelulaBruta[] };
  const [y, m, d] = bruto.ini.split("-").map(Number);
  pacote = {
    ini: bruto.ini, ndias: bruto.ndias, t0: Date.UTC(y, m - 1, d), anoIni: y,
    celulas: bruto.celulas.map((c) => ({ id: c.id, lat: c.lat, lon: c.lon, elev: c.elev, api: c.api, motor: c.motor, _b: c })),
  };
  return pacote;
}

export function series(c: Celula): Series {
  if (!c._s) c._s = { tn: int16(c._b.tmin), tx: int16(c._b.tmax), pr: int16(c._b.chuva) };
  return c._s;
}

/** Índice do dia na série (dias desde o início do pacote). */
export function idx(y: number, m: number, d: number): number {
  return Math.round((Date.UTC(y, m - 1, d) - dados().t0) / 864e5);
}

export function celulaPorId(id: string): Celula | undefined {
  return dados().celulas.find((c) => c.id === id);
}

export function celulaMaisProxima(lon: number, lat: number): Celula {
  let melhor = dados().celulas[0], dist = Infinity;
  for (const c of dados().celulas) {
    const dd = (c.lat - lat) ** 2 + ((c.lon - lon) * 0.8) ** 2;
    if (dd < dist) { dist = dd; melhor = c; }
  }
  return melhor;
}

// ---------- malha dos municípios (IBGE; só para desenho e para dizer o município) ----------
type Feature = GeoJSON.Feature<GeoJSON.Polygon | GeoJSON.MultiPolygon, { cod: string; nome: string }>;
let malha: Feature[] | null = null;

function carregarMalha(): Feature[] {
  if (malha) return malha;
  const fc = JSON.parse(fs.readFileSync(path.join(PUBLICO, "dados", "malha.json"), "utf-8")) as GeoJSON.FeatureCollection;
  malha = (fc.features as Feature[]).map((f) => {
    // os anéis do IBGE vêm no sentido anti-horário; o d3 (esférico) espera horário
    if (d3.geoArea(f) > 2 * Math.PI) {
      const inv = (g: GeoJSON.Position[][]) => g.map((anel) => anel.slice().reverse());
      const geo = f.geometry;
      const coords = geo.type === "Polygon" ? inv(geo.coordinates) : geo.coordinates.map(inv);
      return { ...f, geometry: { ...geo, coordinates: coords } } as Feature;
    }
    return f;
  });
  return malha;
}

export function municipioEm(lon: number, lat: number): string | null {
  const f = carregarMalha().find((x) => d3.geoContains(x, [lon, lat]));
  return f ? f.properties.nome : null;
}
