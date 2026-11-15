"use client";
import { useEffect, useRef, useState } from "react";
import type { Perfil, Poligono } from "@/lib/tipos";

const SUGESTOES: [string, string][] = [
  ["2º milho ou aveia?", "Vale a pena plantar o 2º milho este ano ou é melhor ir de aveia?"],
  ["Onde ponho sorgo?", "Em que parte da fazenda faz sentido pôr sorgo, e o que eu perco com isso?"],
  ["Como cuidar do solo?", "O que eu faço no inverno para não perder solo nos morros?"],
];

// Reconhecimento de voz do navegador (Chrome e Edge). Os tipos não vêm no lib.dom do TypeScript.
interface Reconhecedor { lang: string; interimResults: boolean; continuous: boolean; start(): void; stop(): void;
  onresult: ((e: { resultIndex: number; results: ArrayLike<{ isFinal: boolean; 0: { transcript: string } }> }) => void) | null;
  onend: (() => void) | null; onerror: ((e: { error: string }) => void) | null }
type CtorReconhecedor = new () => Reconhecedor;

function falar(texto: string) {
  if (!("speechSynthesis" in window)) return;
  speechSynthesis.cancel();
  const u = new SpeechSynthesisUtterance(texto);
  u.lang = "pt-BR";
  const voz = speechSynthesis.getVoices().find((v) => v.lang.toLowerCase().startsWith("pt-br"));
  if (voz) u.voice = voz;
  speechSynthesis.speak(u);
}

export default function Pergunte({ poligono, perfil, mensagem }: { poligono: Poligono; perfil: Perfil; mensagem: string }) {
  const [q, setQ] = useState(SUGESTOES[0][1]);
  const [resp, setResp] = useState("");
  const [nota, setNota] = useState("");
  const [rodando, setRodando] = useState(false);
  const [ouvindo, setOuvindo] = useState(false);
  const [temVoz, setTemVoz] = useState(false), [temFala, setTemFala] = useState(false);
  const ctl = useRef<AbortController | null>(null), rec = useRef<Reconhecedor | null>(null);

  useEffect(() => {
    const w = window as unknown as { SpeechRecognition?: CtorReconhecedor; webkitSpeechRecognition?: CtorReconhecedor };
    setTemVoz(!!(w.SpeechRecognition || w.webkitSpeechRecognition));
    setTemFala("speechSynthesis" in window);
  }, []);

  async function perguntar() {
    const pergunta = q.trim();
    if (!pergunta) { setNota("Escreva ou fale uma pergunta primeiro."); return; }
    ctl.current = new AbortController();
    setRodando(true); setResp("Pensando…"); setNota("");
    try {
      const r = await fetch("/api/perguntar", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ pergunta, poligono, perfil }), signal: ctl.current.signal });
      if (!r.ok || !r.body) {
        const e = await r.json().catch(() => ({}));
        setResp(""); setNota(e.erro || "Não deu para responder agora.");
        return;
      }
      const leitor = r.body.getReader(), dec = new TextDecoder();
      let txt = "";
      for (;;) {
        const { done, value } = await leitor.read();
        if (done) break;
        txt += dec.decode(value, { stream: true });
        setResp(txt);
      }
      if (!txt.trim()) setNota("O Claude não devolveu resposta. Tente de novo.");
    } catch (e) {
      if ((e as Error).name === "AbortError") setNota("Pergunta interrompida.");
      else { setResp(""); setNota("Sem conexão com o servidor."); }
    } finally {
      setRodando(false);
    }
  }

  function microfone() {
    if (ouvindo) { rec.current?.stop(); return; }
    const w = window as unknown as { SpeechRecognition?: CtorReconhecedor; webkitSpeechRecognition?: CtorReconhecedor };
    const C = w.SpeechRecognition || w.webkitSpeechRecognition;
    if (!C) return;
    const r = new C();
    r.lang = "pt-BR"; r.interimResults = true; r.continuous = false;
    let fixo = "";
    r.onresult = (e) => {
      let parcial = "";
      for (let i = e.resultIndex; i < e.results.length; i++) {
        const t = e.results[i][0].transcript;
        if (e.results[i].isFinal) fixo = (fixo + " " + t).trim(); else parcial += t;
      }
      setQ((fixo + " " + parcial).trim());
    };
    r.onerror = (e) => setNota(e.error === "not-allowed" ? "Microfone não liberado. Escreva a pergunta." : "Não deu para ouvir agora.");
    r.onend = () => setOuvindo(false);
    rec.current = r;
    setQ(""); setOuvindo(true);
    r.start();
  }

  return (
    <section className="sec" id="s5">
      <div className="sechead"><h2>Pergunte</h2><span className="small">Por texto ou por voz. A resposta usa só os números calculados acima.</span></div>
      <div className="ask">
        <div style={{ display: "grid", gap: 8 }}>
          <div className="scen">{SUGESTOES.map(([t, p]) => <button key={t} className="btn" onClick={() => setQ(p)}>{t}</button>)}</div>
          <label htmlFor="qText" className="small">Sua pergunta</label>
          <textarea id="qText" value={q} maxLength={600} onChange={(e) => setQ(e.target.value)} />
          <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
            <button className="btn pri" onClick={perguntar} disabled={rodando}>Perguntar</button>
            {temVoz && <button className="btn" onClick={microfone} disabled={rodando}>{ouvindo ? "Parar de ouvir" : "Falar a pergunta"}</button>}
            {rodando && <button className="btn" onClick={() => ctl.current?.abort()}>Parar</button>}
          </div>
          <span className="small" role="status">{nota}</span>
        </div>
        <div style={{ display: "grid", gap: 8, alignContent: "start" }}>
          <span className="eyebrow">Resposta</span>
          <div className="answer" aria-live="polite">{resp || "A resposta aparece aqui. Ela compara as opções, diz os riscos e o que fazer, usando só os números da sua fazenda."}</div>
          {temFala && resp && !rodando && <div><button className="btn" onClick={() => falar(resp)}>Ouvir a resposta</button></div>}
        </div>
      </div>
      <div style={{ display: "grid", gap: 8, borderTop: "1px solid var(--line)", paddingTop: 12 }}>
        <span className="eyebrow">Resumo que o agricultor recebe por mensagem</span>
        <div className="msg">{mensagem}</div>
        {temFala && <div><button className="btn" onClick={() => falar(mensagem)}>Ouvir em áudio</button></div>}
      </div>
    </section>
  );
}
