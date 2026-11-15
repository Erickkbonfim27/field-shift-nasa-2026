import { NextResponse } from "next/server";
import { dados } from "@/lib/server/dados";
import { chuvaDezFev, clima, ANO_FIM } from "@/lib/server/modelo";
import type { CamadaCelula } from "@/lib/tipos";

export const runtime = "nodejs";

/** GET ?ano=2022&gdd=1250 -> por ponto do POWER: data-limite do 2º milho (ciclo) e chuva dez–fev do ano em % do normal. */
export async function GET(req: Request) {
  const u = new URL(req.url);
  const ini = dados().anoIni + 1;
  const ano = Math.max(ini, Math.min(ANO_FIM, Number(u.searchParams.get("ano")) || 2022));
  const gdd = ["1100", "1250", "1400"].includes(u.searchParams.get("gdd") ?? "") ? u.searchParams.get("gdd")! : "1250";
  const out: CamadaCelula[] = dados().celulas.map((c) => ({
    id: c.id, lat: c.lat, lon: c.lon,
    limite: c.motor.limite_2m.por_ciclo[gdd] ?? null,
    chuvaPct: Math.round((100 * chuvaDezFev(c, ano)) / clima(c).med),
  }));
  return NextResponse.json({ ano, gdd: Number(gdd), celulas: out }, { headers: { "Cache-Control": "public, max-age=3600" } });
}
