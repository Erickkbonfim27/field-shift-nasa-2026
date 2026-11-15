import { NextResponse } from "next/server";
import { criarFazenda, listarFazendas } from "@/lib/server/db";
import { validarPerfil, validarPoligono } from "@/lib/server/analise";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET() {
  return NextResponse.json(listarFazendas());
}

/** POST { nome, poligono, perfil } -> fazenda criada */
export async function POST(req: Request) {
  const corpo = await req.json().catch(() => null);
  const nome = String(corpo?.nome ?? "").trim().slice(0, 80);
  const poligono = validarPoligono(corpo?.poligono);
  if (!nome) return NextResponse.json({ erro: "Dê um nome para a fazenda." }, { status: 400 });
  if (!poligono) return NextResponse.json({ erro: "Desenhe a fazenda no mapa antes de salvar." }, { status: 400 });
  return NextResponse.json(criarFazenda(nome, poligono, validarPerfil(corpo?.perfil)), { status: 201 });
}
