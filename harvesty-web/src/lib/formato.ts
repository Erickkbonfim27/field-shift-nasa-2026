// Formatação compartilhada (servidor e navegador), com as regras de texto da spec v2.

export const MESES = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"];
export const MESES_EXT = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"];

export const fmt = (x: number, d = 1) => Number(x).toLocaleString("pt-BR", { minimumFractionDigits: d, maximumFractionDigits: d });

// Regra R7: inteiro com meio para cima; entre 0 e 0,5 "menos de 1"; zero "quase nunca".
export const r7 = (x: number) => Math.floor(x + 0.5);

export function em10txt(v: number | null | undefined): string {
  if (v === null || v === undefined) return "sem dado";
  if (v === 0) return "quase nunca";
  if (v < 0.5) return "menos de 1 de cada 10 anos";
  return `cerca de ${r7(v)} de cada 10 anos`;
}

export function em10curto(v: number | null | undefined): string {
  if (v === null || v === undefined) return "–";
  if (v === 0) return "quase nunca";
  if (v < 0.5) return "menos de 1 em 10";
  return `${r7(v)} em 10`;
}

export function faixaTxt(ic: [number, number] | null | undefined): string {
  return ic ? ` (entre ${r7(ic[0])} e ${r7(ic[1])})` : "";
}

/** "05/02" -> "5 de fevereiro"; "01/08" -> "1º de agosto". */
export function dataExt(s: string | null | undefined): string {
  if (!s) return "sem data";
  const [d, m] = s.split("/").map(Number);
  return `${d === 1 ? "1º" : d} de ${MESES_EXT[m - 1]}`;
}

/** dia do ano (ano não bissexto) -> "5 fev" */
export function ddmm(doy: number): string {
  const dt = new Date(Date.UTC(2001, 0, doy));
  return `${dt.getUTCDate()} ${MESES[dt.getUTCMonth()]}`;
}

/** "05/02" -> dia do ano */
export function ddmmDoy(s: string): number {
  const [d, m] = s.split("/").map(Number);
  return Math.round((Date.UTC(2001, m - 1, d) - Date.UTC(2001, 0, 1)) / 864e5) + 1;
}

/** Intervalo de Wilson em "anos de 10", como no motor (estat.py). */
export function wilson10(k: number, n: number): [number, number] {
  if (!n) return [0, 0];
  const z = 1.96, p = k / n, den = 1 + (z * z) / n, c = (p + (z * z) / (2 * n)) / den;
  const h = (z * Math.sqrt((p * (1 - p)) / n + (z * z) / (4 * n * n))) / den;
  return [Math.round(100 * Math.max(0, c - h)) / 10, Math.round(100 * Math.min(1, c + h)) / 10];
}
