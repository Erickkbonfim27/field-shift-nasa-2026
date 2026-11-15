"use client";
import { ddmm } from "@/lib/formato";
import type { Cultura, Perfil as TPerfil, Prioridade } from "@/lib/tipos";

const CULTURAS: [Cultura, string][] = [["milhoV", "Milho silagem (verão)"], ["milho2", "2º milho (safrinha)"], ["soja", "Soja"], ["aveia", "Aveia ou azevém (inverno)"], ["sorgo", "Sorgo"], ["perene", "Pastagem perene"]];
const PRIORIDADES: [Prioridade, string][] = [["comida", "Não faltar comida para as vacas"], ["custo", "Gastar menos"], ["solo", "Cuidar do solo"], ["renda", "Ganhar mais"]];
const DATAS2 = Array.from({ length: 17 }, (_, i) => 1 + i * 5); // 1/jan a 22/mar, de 5 em 5 dias

export default function Perfil({ perfil, onChange }: { perfil: TPerfil; onChange: (p: TPerfil) => void }) {
  const muda = <K extends keyof TPerfil>(k: K, v: TPerfil[K]) => onChange({ ...perfil, [k]: v });
  const alterna = <T,>(lista: T[], v: T, max = 99) => (lista.includes(v) ? lista.filter((x) => x !== v) : [...lista, v].slice(-max));
  return (
    <form className="form" onSubmit={(e) => e.preventDefault()}>
      <label>Atividade principal
        <select value={perfil.ativ} onChange={(e) => muda("ativ", e.target.value as TPerfil["ativ"])}>
          <option value="leite">Leite</option><option value="graos">Grãos</option><option value="ambos">Leite e grãos</option>
        </select>
      </label>
      <label>Vacas em lactação
        <input type="number" min={0} max={5000} step={1} value={perfil.vacas} onChange={(e) => muda("vacas", Math.max(0, Number(e.target.value) || 0))} />
      </label>
      <div className="full"><span style={{ fontSize: 12.5, fontWeight: 600 }}>O que planta hoje</span>
        <div className="checks">
          {CULTURAS.map(([k, t]) => (
            <label key={k}><input type="checkbox" checked={perfil.cult.includes(k)} onChange={() => muda("cult", alterna(perfil.cult, k))} />{t}</label>
          ))}
        </div>
      </div>
      <label>Planta o milho de verão em
        <select value={perfil.mesV} onChange={(e) => muda("mesV", Number(e.target.value))}>
          {[[8, "agosto"], [9, "setembro"], [10, "outubro"], [11, "novembro"], [12, "dezembro"]].map(([v, t]) => <option key={v} value={v}>{t}</option>)}
        </select>
      </label>
      <label>Planta o 2º milho em
        <select value={perfil.data2} onChange={(e) => muda("data2", Number(e.target.value))}>
          <option value={0}>não planto</option>
          {DATAS2.map((d) => <option key={d} value={d}>{ddmm(d)}</option>)}
        </select>
      </label>
      <label>Ciclo do híbrido de milho
        <select value={perfil.gdd} onChange={(e) => muda("gdd", Number(e.target.value) as TPerfil["gdd"])}>
          <option value={1100}>precoce</option><option value={1250}>normal</option><option value={1400}>tardio</option>
        </select>
      </label>
      <label>Solo que você vê
        <select value={perfil.solo} onChange={(e) => muda("solo", e.target.value as TPerfil["solo"])}>
          <option value="auto">não sei</option><option value="raso">raso ou com pedra</option><option value="medio">médio</option><option value="fundo">fundo, terra boa</option>
        </select>
      </label>
      <div className="full"><span style={{ fontSize: 12.5, fontWeight: 600 }}>O que é mais importante para você (até 2)</span>
        <div className="checks">
          {PRIORIDADES.map(([k, t]) => (
            <label key={k}><input type="checkbox" checked={perfil.pri.includes(k)} onChange={() => muda("pri", alterna(perfil.pri, k, 2))} />{t}</label>
          ))}
        </div>
      </div>
    </form>
  );
}
