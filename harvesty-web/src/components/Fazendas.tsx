"use client";
import { useEffect, useState } from "react";
import type { Fazenda, Perfil, Poligono } from "@/lib/tipos";

interface Props {
  atual: number | null;
  poligono: Poligono;
  perfil: Perfil;
  exemplo: boolean;
  onAbrir: (f: Fazenda) => void;
  onSalva: (f: Fazenda) => void;
  onApagada: (id: number) => void;
}

/** Fazendas guardadas no servidor (SQLite). Uma área delimitada uma vez fica salva para as próximas visitas. */
export default function Fazendas({ atual, poligono, perfil, exemplo, onAbrir, onSalva, onApagada }: Props) {
  const [lista, setLista] = useState<Fazenda[]>([]);
  const [nome, setNome] = useState("");
  const [nota, setNota] = useState("");
  const [apagar, setApagar] = useState<number | null>(null);

  const recarrega = () => fetch("/api/fazendas").then((r) => r.json()).then(setLista).catch(() => setNota("Não deu para ler as fazendas salvas."));
  useEffect(() => { recarrega(); }, []);

  const daVez = lista.find((f) => f.id === atual) ?? null;
  useEffect(() => { setNome(daVez?.nome ?? ""); }, [daVez?.id, daVez?.nome]);

  async function salvar(novo: boolean) {
    const n = nome.trim();
    if (!n) { setNota("Dê um nome para a fazenda."); return; }
    const url = !novo && atual ? `/api/fazendas/${atual}` : "/api/fazendas";
    const r = await fetch(url, { method: !novo && atual ? "PUT" : "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ nome: n, poligono, perfil }) });
    const f = await r.json().catch(() => null);
    if (!r.ok) { setNota(f?.erro ?? "Não deu para salvar."); return; }
    setNota(novo || !atual ? "Fazenda salva." : "Alterações salvas.");
    onSalva(f);
    recarrega();
  }

  async function confirmaApagar(id: number) {
    const r = await fetch(`/api/fazendas/${id}`, { method: "DELETE" });
    setApagar(null);
    if (!r.ok) { setNota("Não deu para apagar."); return; }
    setNota("Fazenda apagada.");
    onApagada(id);
    recarrega();
  }

  return (
    <div className="fazendas">
      <div className="salvar">
        <label className="small" htmlFor="nomeFaz">Nome da fazenda</label>
        <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
          <input id="nomeFaz" value={nome} maxLength={80} placeholder={exemplo ? "Desenhe a sua e dê um nome" : "Ex.: Sítio da linha São Pedro"} onChange={(e) => setNome(e.target.value)} />
          <button className="btn pri" onClick={() => salvar(false)}>{atual ? "Salvar alterações" : "Salvar fazenda"}</button>
          {atual && <button className="btn" onClick={() => salvar(true)}>Salvar como nova</button>}
        </div>
        <span className="small" role="status">{nota}</span>
      </div>
      {lista.length > 0 && (
        <ul>
          {lista.map((f) => (
            <li key={f.id} className={f.id === atual ? "on" : ""}>
              <button className="link" onClick={() => onAbrir(f)}>{f.nome}</button>
              <span className="small mono">{new Date(f.atualizadaEm).toLocaleDateString("pt-BR")}</span>
              {apagar === f.id ? (
                <span className="confirma">Apagar de vez?
                  <button className="btn perigo" onClick={() => confirmaApagar(f.id)}>Sim, apagar</button>
                  <button className="btn" onClick={() => setApagar(null)}>Não</button>
                </span>
              ) : <button className="btn mini" aria-label={`Apagar ${f.nome}`} onClick={() => setApagar(f.id)}>Apagar</button>}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
