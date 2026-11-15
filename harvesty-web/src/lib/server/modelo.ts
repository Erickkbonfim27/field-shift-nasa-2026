// Modelo de geada e clima, portado do motor (solucao/motor/geada.py e V2) e do app estático.
// As saídas fixas do motor (janela do milho de verão, data-limite, ano seco) vêm prontas em celulas.json;
// aqui ficam só as contas que dependem do perfil (data e ciclo escolhidos) e da série diária.
import { dados, idx, series, type Celula } from "./dados";
import { wilson10 } from "@/lib/formato";

export const ANO_FIM = 2025;

/** Geada (mínima <= L) entre o plantio e o corte da silagem (graus-dia base 10, teto 30); corte em 30/set. */
export function safra(c: Celula, y: number, m: number, d: number, L: number, gdd: number): { g: boolean; dias: number } | null {
  const S = series(c);
  const i0 = idx(y, m, d), fim = idx(y, 9, 30), nd = dados().ndias;
  let i = i0, soma = 0, g = false;
  while (soma < gdd) {
    if (i > fim || i >= nd || i < 0) return null;
    const tn = S.tn[i] / 10, tx = S.tx[i] / 10;
    if (tn <= L) g = true;
    soma += Math.max(0, (Math.min(tx, 30) + Math.max(tn, 10)) / 2 - 10);
    i++;
  }
  return { g, dias: i - i0 };
}

export function chanceIC(c: Celula, m: number, d: number, L: number, gdd: number) {
  let k = 0, n = 0;
  for (let y = dados().anoIni; y <= ANO_FIM; y++) {
    const r = safra(c, y, m, d, L, gdd);
    if (r) { n++; if (r.g) k++; }
  }
  return n ? { v: (10 * k) / n, ic: wilson10(k, n), k, n } : null;
}

const cacheCurva = new Map<string, { k: number[]; n: number[]; sm: number[]; limiteDoy: number | null }>();

/** Chance diária de 1/jan a 31/mar (k e n por dia), média móvel de 5 dias e data-limite (até 2 em 10). */
export function curvaDiaria(c: Celula, L: number, gdd: number) {
  const chave = `${c.id}|${L}|${gdd}`;
  const ja = cacheCurva.get(chave);
  if (ja) return ja;
  const k: number[] = [], n: number[] = [];
  for (let doy = 1; doy <= 90; doy++) {
    const dt = new Date(Date.UTC(2001, 0, doy));
    const r = chanceIC(c, dt.getUTCMonth() + 1, dt.getUTCDate(), L, gdd);
    k.push(r ? r.k : 0); n.push(r ? r.n : 0);
  }
  const raw = k.map((x, i) => (n[i] ? (10 * x) / n[i] : 10));
  const sm = raw.map((_, i) => { const a = raw.slice(Math.max(0, i - 2), i + 3); return a.reduce((s, v) => s + v, 0) / a.length; });
  let limiteDoy: number | null = null;
  for (let i = 0; i < sm.length; i++) if (sm[i] > 2) { limiteDoy = Math.max(1, i); break; }
  const out = { k, n, sm, limiteDoy };
  cacheCurva.set(chave, out);
  return out;
}

// ---------- chuva ----------
export function chuvaPeriodo(c: Celula, y0: number, m0: number, d0: number, y1: number, m1: number, d1: number) {
  const S = series(c);
  let s = 0;
  for (let i = idx(y0, m0, d0); i <= idx(y1, m1, d1); i++) if (i >= 0 && i < S.pr.length) s += S.pr[i] / 10;
  return s;
}
const ultimoDia = (y: number, m: number) => new Date(Date.UTC(y, m, 0)).getUTCDate();
export const chuvaDezFev = (c: Celula, y: number) => chuvaPeriodo(c, y - 1, 12, 1, y, 2, ultimoDia(y, 2));
export const chuvaMensal = (c: Celula, y: number) => Array.from({ length: 12 }, (_, m) => chuvaPeriodo(c, y, m + 1, 1, y, m + 1, ultimoDia(y, m + 1)));

function mediana(a: number[]) {
  const s = [...a].sort((x, y) => x - y), n = s.length;
  return n % 2 ? s[(n - 1) / 2] : (s[n / 2 - 1] + s[n / 2]) / 2;
}

const cacheClima = new Map<string, { med: number; medMes: number[]; fournier: number[] }>();
/** Mediana da chuva de dez–fev, mediana mensal e índice de Fournier médio (chuva do mês² ÷ chuva do ano). */
export function clima(c: Celula) {
  const ja = cacheClima.get(c.id);
  if (ja) return ja;
  const ini = dados().anoIni;
  const df: number[] = [];
  for (let y = ini + 1; y <= ANO_FIM; y++) df.push(chuvaDezFev(c, y));
  const meses: number[][] = [], anos: number[] = [];
  for (let y = ini; y <= ANO_FIM; y++) { const cm = chuvaMensal(c, y); meses.push(cm); anos.push(cm.reduce((s, v) => s + v, 0)); }
  const medMes = Array.from({ length: 12 }, (_, m) => mediana(meses.map((a) => a[m])));
  const fournier = Array.from({ length: 12 }, (_, m) => meses.reduce((s, a, i) => s + a[m] ** 2 / anos[i], 0) / meses.length);
  const out = { med: mediana(df), medMes, fournier };
  cacheClima.set(c.id, out);
  return out;
}
