"use client";
import { useEffect, useRef, useState } from "react";
import * as d3 from "d3";
import { ddmm, ddmmDoy, fmt, MESES } from "@/lib/formato";
import type { Analise, DadosAno } from "@/lib/tipos";

const ANOS = Array.from({ length: 2025 - 1982 + 1 }, (_, i) => 2025 - i);
const W = 420, H = 220;

function base(label: string) {
  return d3.create("svg").attr("viewBox", `0 0 ${W} ${H}`).attr("class", "chart").attr("role", "img").attr("aria-label", label);
}
// eslint-disable-next-line @typescript-eslint/no-explicit-any
function eixo(g: d3.Selection<SVGGElement, any, null, undefined>) {
  g.selectAll("text").attr("fill", "var(--ink-2)").attr("font-family", "var(--mono)").attr("font-size", 10);
  g.selectAll("line,path").attr("stroke", "var(--line)");
}

function grafTmin(el: HTMLDivElement, D: DadosAno) {
  const m = { l: 34, r: 8, t: 10, b: 24 };
  const pts = D.tmin.map((v, i) => ({ i, v }));
  const x = d3.scaleLinear([0, pts.length - 1], [m.l, W - m.r]);
  const y = d3.scaleLinear([d3.min(D.tmin)! - 1, d3.max(D.tmin)! + 1], [H - m.b, m.t]);
  const s = base("Temperatura mínima diária de " + D.ano);
  if (D.janela2) {
    const a = D.janela2.inicio;
    s.append("rect").attr("x", x(a)).attr("y", m.t).attr("width", Math.max(0, x(Math.min(a + D.janela2.dias, pts.length - 1)) - x(a))).attr("height", H - m.b - m.t).attr("fill", "var(--milho-soft)");
    s.append("text").attr("x", x(a) + 4).attr("y", m.t + 12).attr("font-size", 10).attr("fill", "var(--ink-2)").text("2º milho até a silagem");
  }
  s.append("g").attr("transform", `translate(0,${H - m.b})`).call(d3.axisBottom(x).tickValues([0, 31, 59, 90, 120, 151, 181, 212, 243]).tickFormat((_, k) => MESES[k])).call(eixo);
  s.append("g").attr("transform", `translate(${m.l},0)`).call(d3.axisLeft(y).ticks(5).tickFormat((d) => d + "°")).call(eixo);
  s.append("line").attr("x1", m.l).attr("x2", W - m.r).attr("y1", y(3)).attr("y2", y(3)).attr("stroke", "var(--geada)").attr("stroke-dasharray", "4 3");
  s.append("path").datum(pts).attr("fill", "none").attr("stroke", "var(--ink-2)").attr("stroke-width", 1.2).attr("d", d3.line<{ i: number; v: number }>().x((p) => x(p.i)).y((p) => y(p.v)));
  const g = pts.filter((p) => p.v <= 3);
  s.selectAll("circle.g").data(g).join("circle").attr("cx", (p) => x(p.i)).attr("cy", (p) => y(p.v)).attr("r", 3).attr("fill", "var(--geada)");
  el.replaceChildren(s.node()!);
  return `${D.ano}: ${g.length} dias com mínima ≤ 3 °C (linha azul tracejada). Série T2M_MIN do NASA POWER.`;
}

function grafCurva(el: HTMLDivElement, A: Analise) {
  const c = A.curva2, m = { l: 30, r: 10, t: 12, b: 24 };
  const raw = c.k.map((k, i) => (c.n[i] ? (10 * k) / c.n[i] : 0));
  const x = d3.scaleLinear([1, 90], [m.l, W - m.r]), y = d3.scaleLinear([0, 10], [H - m.b, m.t]);
  const s = base("Chance de geada por data de plantio do 2º milho");
  const lp = A.limitePorLimiar;
  if (lp["4"] && lp["2"]) s.append("rect").attr("x", x(ddmmDoy(lp["4"]))).attr("y", m.t).attr("width", Math.max(1, x(ddmmDoy(lp["2"])) - x(ddmmDoy(lp["4"])))).attr("height", H - m.b - m.t).attr("fill", "var(--alto-soft)");
  s.append("g").attr("transform", `translate(0,${H - m.b})`).call(d3.axisBottom(x).tickValues([1, 11, 21, 32, 42, 52, 60, 70, 80]).tickFormat((d) => ddmm(Number(d)))).call(eixo);
  s.append("g").attr("transform", `translate(${m.l},0)`).call(d3.axisLeft(y).ticks(5)).call(eixo);
  const linha = d3.line<number>().x((_, i) => x(i + 1)).y((v) => y(v));
  s.append("path").datum(raw).attr("fill", "none").attr("stroke", "var(--geada-soft)").attr("stroke-width", 1).attr("d", linha);
  s.append("path").datum(c.sm).attr("fill", "none").attr("stroke", "var(--geada)").attr("stroke-width", 2.5).attr("d", linha);
  s.append("line").attr("x1", m.l).attr("x2", W - m.r).attr("y1", y(2)).attr("y2", y(2)).attr("stroke", "var(--alto)").attr("stroke-dasharray", "4 3");
  const lim = A.limite ? ddmmDoy(A.limite) : c.limiteDoy;
  if (lim) {
    s.append("line").attr("x1", x(lim)).attr("x2", x(lim)).attr("y1", m.t).attr("y2", H - m.b).attr("stroke", "var(--alto)");
    s.append("text").attr("x", x(lim) - 4).attr("y", m.t + 10).attr("text-anchor", "end").attr("font-size", 10.5).attr("fill", "var(--alto)").text("limite " + ddmm(lim));
  }
  const d2 = A.perfil.data2;
  if (d2 && d2 <= 90) s.append("circle").attr("cx", x(d2)).attr("cy", y(c.sm[d2 - 1])).attr("r", 5).attr("fill", "var(--milho)").attr("stroke", "var(--surface)");
  el.replaceChildren(s.node()!);
  return `Anos em 10 com geada antes do corte da silagem (${A.perfil.gdd} °C·dia), ${A.periodo.ini}–${A.periodo.fim}. Faixa vermelha: data-limite com limiar de 4 a 2 °C. Ponto amarelo: a sua data.`;
}

function grafChuva(el: HTMLDivElement, D: DadosAno, A: Analise) {
  const cm = D.chuvaMensal, med = D.medMes, m = { l: 36, r: 8, t: 10, b: 24 };
  const x = d3.scaleBand<number>(d3.range(12), [m.l, W - m.r]).padding(0.25);
  const y = d3.scaleLinear([0, Math.max(d3.max(cm)!, d3.max(med)!) * 1.1], [H - m.b, m.t]);
  const s = base("Chuva mensal do ano contra a mediana");
  s.append("g").attr("transform", `translate(0,${H - m.b})`).call(d3.axisBottom(x).tickFormat((d) => MESES[d])).call(eixo);
  s.append("g").attr("transform", `translate(${m.l},0)`).call(d3.axisLeft(y).ticks(5)).call(eixo);
  s.selectAll("rect").data(cm).join("rect").attr("x", (_, i) => x(i)!).attr("y", (d) => y(d)).attr("width", x.bandwidth()).attr("height", (d) => y(0) - y(d)).attr("rx", 3)
    .attr("fill", (d, i) => (d < 0.6 * med[i] ? "var(--alto)" : "var(--pasto)"));
  s.append("path").datum(med).attr("fill", "none").attr("stroke", "var(--ink)").attr("stroke-width", 1.5).attr("stroke-dasharray", "3 3")
    .attr("d", d3.line<number>().x((_, i) => x(i)! + x.bandwidth() / 2).y((d) => y(d)));
  el.replaceChildren(s.node()!);
  return `${D.ano}: dez–fev somou ${Math.round(D.dezfev)} mm, ${Math.round((100 * D.dezfev) / D.med)}% do normal. Barras vermelhas: mês abaixo de 60% do normal. Tracejado: mediana ${A.periodo.ini}–${A.periodo.fim}.`;
}

export default function DadosNasa({ A, ano, onAno }: { A: Analise; ano: number; onAno: (a: number) => void }) {
  const refA = useRef<HTMLDivElement>(null), refB = useRef<HTMLDivElement>(null), refC = useRef<HTMLDivElement>(null);
  const [D, setD] = useState<DadosAno | null>(null);
  const [cap, setCap] = useState<[string, string, string]>(["", "", ""]);
  const [erro, setErro] = useState("");

  useEffect(() => {
    const ctl = new AbortController();
    const q = new URLSearchParams({ data2: String(A.perfil.data2), gdd: String(A.perfil.gdd) });
    fetch(`/api/celulas/${encodeURIComponent(A.celula.id)}/ano/${ano}?${q}`, { signal: ctl.signal })
      .then((r) => (r.ok ? r.json() : Promise.reject(new Error(String(r.status)))))
      .then((d: DadosAno) => { setD(d); setErro(""); })
      .catch((e) => { if (e.name !== "AbortError") setErro("Não deu para carregar a série deste ano."); });
    return () => ctl.abort();
  }, [A.celula.id, A.perfil.data2, A.perfil.gdd, ano]);

  useEffect(() => {
    if (!refB.current) return;
    const b = grafCurva(refB.current, A);
    if (D && refA.current && refC.current) setCap([grafTmin(refA.current, D), b, grafChuva(refC.current, D, A)]);
    else setCap((c) => [c[0], b, c[2]]);
  }, [A, D]);

  return (
    <section style={{ display: "grid", gap: 12 }}>
      <div className="sechead">
        <div><span className="eyebrow">Dados da NASA neste ponto</span><h2 style={{ fontSize: 21, marginTop: 4 }}>O que o satélite e a reanálise mostram aqui</h2></div>
        <label className="small" style={{ display: "flex", gap: 8, alignItems: "center" }}>Ano
          <select value={ano} onChange={(e) => onAno(Number(e.target.value))} style={{ border: "1px solid var(--line)", borderRadius: 8, padding: "5px 8px", background: "var(--surface)" }}>
            {ANOS.map((a) => <option key={a} value={a}>{a}</option>)}
          </select>
        </label>
      </div>
      {erro && <p className="erro">{erro}</p>}
      <div className="nasa">
        <div className="chartcard"><h3>Temperatura mínima diária</h3><span className="small">{cap[0]}</span><div ref={refA} /></div>
        <div className="chartcard"><h3>Chance de geada pela data de plantio do 2º milho</h3><span className="small">{cap[1]}</span><div ref={refB} /></div>
        <div className="chartcard"><h3>Chuva por mês: o ano contra o normal</h3><span className="small">{cap[2]}</span><div ref={refC} /></div>
      </div>
      <p className="small" style={{ margin: 0 }}>Ponto da grade do NASA POWER usado: <span className="mono">lat {fmt(A.celula.lat, 2)}, lon {fmt(A.celula.lon, 3)}, altitude da grade {A.celula.elev} m</span>. <a href={A.celula.api} target="_blank" rel="noopener noreferrer" style={{ color: "var(--pasto)" }}>Abrir esta série na API da NASA</a></p>
    </section>
  );
}
