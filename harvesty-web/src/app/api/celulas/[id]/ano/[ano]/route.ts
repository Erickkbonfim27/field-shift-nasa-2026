import { NextResponse } from "next/server";
import { celulaPorId, dados, idx, series } from "@/lib/server/dados";
import { chuvaDezFev, chuvaMensal, clima, safra, ANO_FIM } from "@/lib/server/modelo";
import type { DadosAno } from "@/lib/tipos";

export const runtime = "nodejs";

/** GET /api/celulas/<id>/ano/<ano>?data2=31&gdd=1250 -> série do ano para os gráficos "Dados da NASA neste ponto". */
export async function GET(req: Request, { params }: { params: Promise<{ id: string; ano: string }> }) {
  const { id, ano: anoTxt } = await params;
  const c = celulaPorId(id);
  if (!c) return NextResponse.json({ erro: "Ponto da grade não encontrado." }, { status: 404 });
  const ano = Number(anoTxt);
  if (!Number.isInteger(ano) || ano < dados().anoIni + 1 || ano > ANO_FIM) return NextResponse.json({ erro: "Ano fora do período dos dados." }, { status: 400 });
  const u = new URL(req.url);
  const data2 = Math.max(0, Math.min(85, Number(u.searchParams.get("data2")) || 0));
  const gdd = [1100, 1250, 1400].includes(Number(u.searchParams.get("gdd"))) ? Number(u.searchParams.get("gdd")) : 1250;
  const S = series(c), i0 = idx(ano, 1, 1), i1 = idx(ano, 9, 30);
  const tmin = Array.from(S.tn.subarray(i0, i1 + 1), (v) => v / 10);
  let janela2: DadosAno["janela2"] = null;
  if (data2) {
    const dt = new Date(Date.UTC(2001, 0, data2));
    const r = safra(c, ano, dt.getUTCMonth() + 1, dt.getUTCDate(), 3, gdd);
    if (r) janela2 = { inicio: data2 - 1, dias: r.dias };
  }
  const cl = clima(c);
  const out: DadosAno = { ano, tmin, chuvaMensal: chuvaMensal(c, ano), medMes: cl.medMes, dezfev: chuvaDezFev(c, ano), med: cl.med, janela2 };
  return NextResponse.json(out, { headers: { "Cache-Control": "public, max-age=3600" } });
}
