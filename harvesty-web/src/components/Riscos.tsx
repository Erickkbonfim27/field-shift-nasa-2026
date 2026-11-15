"use client";
import type { NivelEvidencia, Risco } from "@/lib/tipos";

const EV: Record<NivelEvidencia, [string, string]> = { N2: ["n2", "N2 · com ressalva"], N1: ["n1", "N1 · em teste"], MED: ["med", "medido"], CONF: ["n1", "confirme"] };
export const Selo = ({ ev }: { ev: NivelEvidencia }) => <span className={`ev ${EV[ev][0]}`}>{EV[ev][1]}</span>;

export default function Riscos({ riscos }: { riscos: Risco[] }) {
  if (!riscos.length) return <p className="small">Marque o que você planta para ver os riscos.</p>;
  return (
    <div style={{ display: "grid", gap: 10 }}>
      {riscos.map((r, i) => (
        <details className="risk" key={r.id} open={i < 2}>
          <summary><Selo ev={r.ev} /><h3>{r.t}</h3><span className="num mono">{r.num}</span></summary>
          <div className="rbody">
            {/* o texto vem do servidor (motor), sem nada digitado pelo usuário */}
            <p><b>O dado da NASA diz:</b> <span dangerouslySetInnerHTML={{ __html: r.dado }} /></p>
            <div><b>O que fazer</b><ul>{r.fazer.map((f) => <li key={f}>{f}</li>)}</ul></div>
            <div className="conf"><b>O que não sabemos</b><span>{r.limite}</span></div>
            <p className="rastro">{r.rastro}</p>
          </div>
        </details>
      ))}
    </div>
  );
}
