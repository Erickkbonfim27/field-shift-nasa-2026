"use client";
import { useEffect, useState } from "react";
import { MIS } from "@/lib/constantes";
import { dataExt, ddmm, em10curto, faixaTxt, fmt, MESES, MESES_EXT, wilson10 } from "@/lib/formato";
import type { Analise } from "@/lib/tipos";
import { Selo } from "./Riscos";

export type Cenario = "milho2" | "sorgo" | "dataV" | "cobertura";
const BOTOES: [Cenario, string][] = [["milho2", "Plantar o 2º milho"], ["sorgo", "Pôr sorgo na silagem"], ["dataV", "Mudar a data do milho de verão"], ["cobertura", "Cobrir o solo no inverno"]];
const DATAS_V = ["21/09", "01/10", "11/10", "21/10", "01/11", "11/11", "21/11", "01/12", "11/12", "21/12"];
const cor = (v: number | null) => (v === null ? "var(--ink-2)" : v >= 3 ? "var(--alto)" : v >= 1 ? "var(--medio)" : "var(--baixo)");

const NaoCompara = () => <p className="small" style={{ margin: 0 }}>Os números das opções medem coisas diferentes (chance de geada, cenários que ajudam) e não formam um ranking.</p>;

export default function Cenarios({ A }: { A: Analise }) {
  const [cen, setCen] = useState<Cenario>("milho2");
  return (
    <section className="sec" id="s4">
      <div className="sechead"><h2>E se…?</h2><span className="small">Escolha uma possibilidade</span></div>
      <div className="scen" role="group" aria-label="Possibilidades">
        {BOTOES.map(([k, t]) => <button key={k} className={`btn${cen === k ? " on" : ""}`} aria-pressed={cen === k} onClick={() => setCen(k)}>{t}</button>)}
      </div>
      <div style={{ display: "grid", gap: 12 }}>
        {cen === "milho2" && <Milho2 A={A} />}
        {cen === "sorgo" && <Sorgo A={A} />}
        {cen === "dataV" && <DataVerao A={A} />}
        {cen === "cobertura" && <Cobertura A={A} />}
      </div>
    </section>
  );
}

function Milho2({ A }: { A: Analise }) {
  const [doy, setDoy] = useState(A.perfil.data2 || 31);
  useEffect(() => { if (A.perfil.data2) setDoy(A.perfil.data2); }, [A.perfil.data2]);
  const k = A.curva2.k[doy - 1], n = A.curva2.n[doy - 1];
  const r = n ? { v: (10 * k) / n, ic: wilson10(k, n) } : null;
  const rl = A.riscoLim, lim = A.limite ? dataExt(A.limite) : "sem data segura";
  return <>
    <div className="ctrl">
      <label htmlFor="r2">Plantar o 2º milho em <b className="mono">{ddmm(doy)}</b></label>
      <input type="range" id="r2" min={1} max={85} step={1} value={doy} onChange={(e) => setDoy(Number(e.target.value))} />
    </div>
    <div className="bigline"><Selo ev="N2" /><b className="mono" style={{ color: cor(r?.v ?? null) }}>{r ? em10curto(r.v) : "–"}</b>
      <span>com geada antes do corte da silagem{r ? faixaTxt(r.ic) : ""}. Data-limite aqui: <b>{lim}</b>.</span></div>
    <div className="tradewrap"><table className="trade"><thead><tr><th>Caminho</th><th>Ganha</th><th>Arrisca</th><th>Número</th></tr></thead><tbody>
      <tr><td><b>O de sempre</b><br /><span className="small">milho de verão e pasto de inverno</span></td><td>Rotina conhecida.</td><td>—</td><td className="small">sem número (ponto de partida)</td></tr>
      <tr><td><b>2º milho em {ddmm(doy)}</b></td><td>Mais silagem no inverno.</td><td>Geada antes do corte; semente e adubo.</td><td className="mono">{r ? em10curto(r.v) + faixaTxt(r.ic) : "–"}</td></tr>
      <tr><td><b>2º milho até {A.limite ? dataExt(A.limite) : "–"}</b></td><td>Silagem com geada rara.</td><td>Depende de colher o verão a tempo.</td><td className="mono">{rl ? em10curto(rl.em10) + faixaTxt(rl.ic95) : "–"}</td></tr>
      <tr><td><b>Aveia ou azevém</b> <Selo ev="N1" /></td><td>Pasto no inverno, solo coberto.</td><td>Menos volume que o milho.</td><td className="small">não calculada</td></tr>
      <tr><td><b>Sorgo depois do milho</b> <Selo ev="N1" /></td><td>—</td><td>—</td><td className="small">em teste{A.mun === "São Miguel do Oeste" ? "; o ZARC indica até 1º de março aqui" : ""}</td></tr>
    </tbody></table></div>
    <p className="small" style={{ margin: 0 }}>Chance de geada antes do corte (mínima ≤ 3 °C no NASA POWER, {A.perfil.gdd} °C·dia, {A.periodo.ini}–{A.periodo.fim}), não de perder a silagem. A falta de água do 2º milho não foi calculada.</p>
    <NaoCompara />
  </>;
}

function Sorgo({ A }: { A: Analise }) {
  const solo = A.perfil.solo;
  if (solo === "raso") return <>
    <div className="bigline"><Selo ev="N2" /><b className="mono" style={{ color: "var(--baixo)" }}>{MIS.s} em 10</b><span>cenários testados em que metade da silagem em sorgo ajudou o ano ruim, no talhão que você disse ser raso.</span></div>
    <div className="tradewrap"><table className="trade"><thead><tr><th>Caminho</th><th>Ganha</th><th>Arrisca</th></tr></thead><tbody>
      <tr><td><b>Só milho</b></td><td>Mais energia por tonelada.</td><td>No ano seco, quebra maior no solo raso.</td></tr>
      <tr><td><b>Metade sorgo</b></td><td>Segura a comida no ano ruim.</td><td>Silagem de sorgo vale cerca de 85% a 90% da de milho (Embrapa). Em ano bom, pode render um pouco menos.</td></tr>
    </tbody></table></div>
    <div className="conf"><b>O que não sabemos</b><span>A conta não é firme: o ganho some se o sorgo sofrer mais com a falta de água do que a FAO supõe, e não há dado de produtividade de sorgo na região. Auditoria: pior ano em 10 com {fmt(MIS.p10)}% a mais (entre {fmt(MIS.ic[0])}% e {fmt(MIS.ic[1])}%).</span></div>
  </>;
  if (solo === "medio") return <p style={{ margin: 0 }}><Selo ev="N1" /> No solo médio, a conta do sorgo ainda está em teste. Por enquanto não temos um número confiável para o seu lugar.</p>;
  if (solo === "fundo") return <p style={{ margin: 0 }}>No solo fundo, o milho rende mais e o sorgo não ajuda o ano ruim. O módulo fica desligado.</p>;
  return <p style={{ margin: 0 }}><Selo ev="CONF" /> Para calcular, preciso saber como é a terra do talhão. Marque em “Solo que você vê”: raso ou com pedra, médio ou fundo.{A.relevo ? ` Pelo relevo, ${fmt(A.relevo.morro, 0)}% da área parece morro.` : ""}</p>;
}

function DataVerao({ A }: { A: Analise }) {
  const ls = A.janela.linhas, hoje = "01/" + String(A.perfil.mesV).padStart(2, "0");
  const sel = ls.filter((l) => DATAS_V.includes(l.d));
  const dif = sel.length ? Math.max(...sel.map((l) => l.em10)) - Math.min(...sel.map((l) => l.em10)) : null;
  return <>
    <div className="tradewrap"><table className="trade"><thead><tr><th>Plantar em</th><th>Geada na lavoura nova <Selo ev="N2" /></th></tr></thead><tbody>
      {ls.map((l) => <tr key={l.d}><td><b>{dataExt(l.d)}</b>{l.d === hoje ? " (hoje)" : ""}</td><td className="mono">{em10curto(l.em10)}{faixaTxt(l.ic95)}</td></tr>)}
    </tbody></table></div>
    <p style={{ margin: 0 }}>{dif !== null && dif < 1 ? "Entre o fim de setembro e dezembro, para o clima, a data de plantio quase não muda o risco: a diferença é menor que 1 ano em 10. Escolha pela mão de obra e pela máquina." : "Fora de agosto, a geada cai rápido."}</p>
    <p className="small" style={{ margin: 0 }}>Geada = algum dia com mínima &lt; 2 °C nos primeiros {A.janela.dias} dias da lavoura (NASA POWER, plantios de {A.janela.periodo}). A forma bate com o ZARC; a força é maior que a do ZARC.</p>
  </>;
}

function Cobertura({ A }: { A: Analise }) {
  const f = A.fournier, mx = Math.max(...f);
  return <>
    <p style={{ margin: 0 }}><Selo ev="MED" /> Quanto a chuva de cada mês pode arrastar solo aqui (índice de Fournier com a chuva do NASA POWER, média {A.periodo.ini}–{A.periodo.fim}):</p>
    <div>{f.map((v, m) => (
      <div key={m} style={{ display: "grid", gridTemplateColumns: "36px minmax(0,1fr) 40px", gap: 8, alignItems: "center", fontSize: 12.5 }}>
        <span className="mono">{MESES[m]}</span>
        <span style={{ height: 10, borderRadius: 4, background: A.topEros.includes(m) ? "var(--alto)" : "var(--line)", width: `${(100 * v) / mx}%` }} />
        <span className="mono">{Math.round(v)}</span>
      </div>))}</div>
    <div className="tradewrap"><table className="trade"><thead><tr><th>Caminho</th><th>Ganha</th><th>Arrisca</th></tr></thead><tbody>
      <tr><td><b>Solo nu no inverno</b></td><td>Não gasta com semente.</td><td>Chega descoberto a {A.topEros.map((m) => MESES_EXT[m]).join(", ")}{A.relevo ? `, com ${fmt(A.relevo.morro, 0)}% da área em morro` : ""}.</td></tr>
      <tr><td><b>Aveia ou azevém</b> <Selo ev="N1" /></td><td>Solo coberto, pasto no inverno, palha para o plantio direto.</td><td>Custo de semente.</td></tr>
    </tbody></table></div>
    <div className="conf"><b>O que não sabemos</b><span>Quanto solo a cobertura salva, não medimos. A erosividade do POWER bateu com o pluviômetro da ANA (testado em Ituporanga).</span></div>
  </>;
}
