// Banco das fazendas: SQLite embutido no Node (node:sqlite), arquivo data/harvesty.db.
import fs from "node:fs";
import path from "node:path";
import { DatabaseSync } from "node:sqlite";
import type { Fazenda, Perfil, Poligono } from "@/lib/tipos";

let db: DatabaseSync | null = null;

function conexao(): DatabaseSync {
  if (db) return db;
  const dir = path.join(process.cwd(), "data");
  fs.mkdirSync(dir, { recursive: true });
  db = new DatabaseSync(path.join(dir, "harvesty.db"));
  db.exec(`CREATE TABLE IF NOT EXISTS fazendas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    poligono TEXT NOT NULL,
    perfil TEXT NOT NULL,
    criada_em TEXT NOT NULL DEFAULT (datetime('now')),
    atualizada_em TEXT NOT NULL DEFAULT (datetime('now'))
  )`);
  return db;
}

interface Linha { id: number; nome: string; poligono: string; perfil: string; criada_em: string; atualizada_em: string }
const paraFazenda = (l: Linha): Fazenda => ({
  id: l.id, nome: l.nome, poligono: JSON.parse(l.poligono), perfil: JSON.parse(l.perfil), criadaEm: l.criada_em, atualizadaEm: l.atualizada_em,
});

export function listarFazendas(): Fazenda[] {
  return (conexao().prepare("SELECT * FROM fazendas ORDER BY atualizada_em DESC, id DESC").all() as unknown as Linha[]).map(paraFazenda);
}

export function obterFazenda(id: number): Fazenda | null {
  const l = conexao().prepare("SELECT * FROM fazendas WHERE id = ?").get(id) as unknown as Linha | undefined;
  return l ? paraFazenda(l) : null;
}

export function criarFazenda(nome: string, poligono: Poligono, perfil: Perfil): Fazenda {
  const r = conexao().prepare("INSERT INTO fazendas (nome, poligono, perfil) VALUES (?, ?, ?)").run(nome, JSON.stringify(poligono), JSON.stringify(perfil));
  return obterFazenda(Number(r.lastInsertRowid))!;
}

export function atualizarFazenda(id: number, nome: string, poligono: Poligono, perfil: Perfil): Fazenda | null {
  const r = conexao().prepare("UPDATE fazendas SET nome = ?, poligono = ?, perfil = ?, atualizada_em = datetime('now') WHERE id = ?")
    .run(nome, JSON.stringify(poligono), JSON.stringify(perfil), id);
  return r.changes ? obterFazenda(id) : null;
}

export function apagarFazenda(id: number): boolean {
  return conexao().prepare("DELETE FROM fazendas WHERE id = ?").run(id).changes > 0;
}
