import { NextResponse } from "next/server";
import { apagarFazenda, atualizarFazenda, obterFazenda } from "@/lib/server/db";
import { validarPerfil, validarPoligono } from "@/lib/server/analise";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

type Ctx = { params: Promise<{ id: string }> };
const lerId = async (ctx: Ctx) => { const n = Number((await ctx.params).id); return Number.isInteger(n) && n > 0 ? n : null; };
const naoAchou = () => NextResponse.json({ erro: "Fazenda não encontrada." }, { status: 404 });

export async function GET(_req: Request, ctx: Ctx) {
  const id = await lerId(ctx);
  const f = id ? obterFazenda(id) : null;
  return f ? NextResponse.json(f) : naoAchou();
}

export async function PUT(req: Request, ctx: Ctx) {
  const id = await lerId(ctx);
  if (!id) return naoAchou();
  const corpo = await req.json().catch(() => null);
  const nome = String(corpo?.nome ?? "").trim().slice(0, 80);
  const poligono = validarPoligono(corpo?.poligono);
  if (!nome || !poligono) return NextResponse.json({ erro: "Nome e polígono são obrigatórios." }, { status: 400 });
  const f = atualizarFazenda(id, nome, poligono, validarPerfil(corpo?.perfil));
  return f ? NextResponse.json(f) : naoAchou();
}

export async function DELETE(_req: Request, ctx: Ctx) {
  const id = await lerId(ctx);
  return id && apagarFazenda(id) ? new NextResponse(null, { status: 204 }) : naoAchou();
}
