import { NextResponse } from "next/server";
import { analisar, validarPerfil, validarPoligono } from "@/lib/server/analise";

export const runtime = "nodejs";

/** POST { poligono, perfil } -> análise da fazenda (riscos, números dos cenários, mensagem). */
export async function POST(req: Request) {
  const corpo = await req.json().catch(() => null);
  const poligono = validarPoligono(corpo?.poligono);
  if (!poligono) return NextResponse.json({ erro: "Polígono inválido: mande de 3 a 200 pontos [lon, lat] no Sul do Brasil." }, { status: 400 });
  return NextResponse.json(analisar(poligono, validarPerfil(corpo?.perfil)));
}
