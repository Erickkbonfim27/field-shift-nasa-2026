"use client";
import { useCallback, useEffect, useRef, useState } from "react";
import type { Camada, RelevoMeta } from "@/lib/mapa-d3";
import { EXEMPLO } from "@/lib/constantes";
import { fmt } from "@/lib/formato";
import { PERFIL_PADRAO, type Analise, type CamadaCelula, type Fazenda, type Perfil as TPerfil, type Poligono } from "@/lib/tipos";
import Cenarios from "./Cenarios";
import DadosNasa from "./DadosNasa";
import Fazendas from "./Fazendas";
import Logo from "./Logo";
import Mapa from "./Mapa";
import Perfil from "./Perfil";
import Pergunte from "./Pergunte";
import Riscos from "./Riscos";

// Preferências deste navegador (não são dados da fazenda; esses ficam no servidor).
const K_CAMADAS = "harvesty-camadas", K_ATUAL = "harvesty-fazenda-atual", K_RASCUNHO = "harvesty-rascunho";
const ler = <T,>(k: string): T | null => { try { const v = localStorage.getItem(k); return v ? (JSON.parse(v) as T) : null; } catch { return null; } };
const grava = (k: string, v: unknown) => { try { if (v === null) localStorage.removeItem(k); else localStorage.setItem(k, JSON.stringify(v)); } catch { /* navegador sem armazenamento */ } };

export default function HarvestyApp({ relevo }: { relevo: RelevoMeta }) {
  const [poly, setPoly] = useState<Poligono>(EXEMPLO);
  const [perfil, setPerfil] = useState<TPerfil>(PERFIL_PADRAO);
  const [exemplo, setExemplo] = useState(true);
  const [fazendaId, setFazendaId] = useState<number | null>(null);
  const [A, setA] = useState<Analise | null>(null);
  const [erro, setErro] = useState("");
  const [carregando, setCarregando] = useState(false);
  const [camadas, setCamadas] = useState<Set<Camada>>(new Set(["relevo"]));
  const [ano, setAno] = useState(2022);
  const [celulas, setCelulas] = useState<CamadaCelula[] | null>(null);
  const pronto = useRef(false);

  // Volta para a última fazenda aberta (ou o rascunho), uma vez.
  useEffect(() => {
    const c = ler<Camada[]>(K_CAMADAS);
    if (c) setCamadas(new Set(c));
    const id = ler<number>(K_ATUAL), rasc = ler<{ poly: Poligono; perfil: TPerfil }>(K_RASCUNHO);
    const fim = () => { pronto.current = true; };
    if (id) {
      fetch(`/api/fazendas/${id}`).then((r) => (r.ok ? r.json() : null)).then((f: Fazenda | null) => {
        if (f) abrir(f); else grava(K_ATUAL, null);
      }).finally(fim);
    } else if (rasc) { setPoly(rasc.poly); setPerfil({ ...PERFIL_PADRAO, ...rasc.perfil }); setExemplo(false); fim(); }
    else fim();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Análise no servidor, com um pequeno atraso para não recalcular a cada tecla.
  useEffect(() => {
    const ctl = new AbortController();
    const t = setTimeout(() => {
      setCarregando(true);
      fetch("/api/analise", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ poligono: poly, perfil }), signal: ctl.signal })
        .then(async (r) => { const j = await r.json(); if (!r.ok) throw new Error(j.erro || "erro"); return j as Analise; })
        .then((a) => { setA(a); setErro(""); })
        .catch((e) => { if (e.name !== "AbortError") setErro(e.message === "erro" ? "Não deu para calcular agora." : e.message); })
        .finally(() => setCarregando(false));
    }, 200);
    return () => { clearTimeout(t); ctl.abort(); };
  }, [poly, perfil]);

  // Rascunho local da área ainda não salva.
  useEffect(() => { if (pronto.current && !exemplo && !fazendaId) grava(K_RASCUNHO, { poly, perfil }); }, [poly, perfil, exemplo, fazendaId]);

  // Camadas da grade NASA POWER (só quando ligadas).
  const precisaGrade = camadas.has("geada") || camadas.has("chuva");
  useEffect(() => {
    if (!precisaGrade) return;
    const ctl = new AbortController();
    fetch(`/api/camadas?ano=${ano}&gdd=${perfil.gdd}`, { signal: ctl.signal }).then((r) => r.json()).then((j) => setCelulas(j.celulas)).catch(() => {});
    return () => ctl.abort();
  }, [precisaGrade, ano, perfil.gdd]);

  const mudaCamadas = (c: Set<Camada>) => { setCamadas(c); grava(K_CAMADAS, [...c]); };
  const abrir = useCallback((f: Fazenda) => {
    setPoly(f.poligono); setPerfil({ ...PERFIL_PADRAO, ...f.perfil }); setFazendaId(f.id); setExemplo(false); grava(K_ATUAL, f.id);
  }, []);
  const desenhou = (p: Poligono) => { setPoly(p); setExemplo(false); setFazendaId(null); grava(K_ATUAL, null); };
  const salva = (f: Fazenda) => { setFazendaId(f.id); setExemplo(false); grava(K_ATUAL, f.id); grava(K_RASCUNHO, null); };
  const apagada = (id: number) => { if (id === fazendaId) { setFazendaId(null); grava(K_ATUAL, null); } };

  const tag = exemplo ? "Exemplo fictício em São Miguel do Oeste. Desenhe a sua no mapa." : fazendaId ? "Fazenda salva no servidor." : "Área nova, ainda não salva.";

  return (
    <div className="page">
      <header className="top">
        <div className="brand"><Logo /><p>Oeste de Santa Catarina · dados NASA POWER (1981–2025) e SRTM</p></div>
        <nav className="steps" aria-label="Etapas">
          {["Delimitar a fazenda", "O que tenho", "Riscos", "E se…?", "Pergunte"].map((t, i) => (
            <a key={t} className={`step${A && i < 4 ? " done" : ""}`} href={`#s${i + 1}`}><b>{i + 1}</b>{t}</a>
          ))}
        </nav>
      </header>

      <div className="main">
        <Mapa relevo={relevo} poligono={poly} camadas={camadas} ano={ano} celulas={celulas} onDesenhar={desenhou} onCamadas={mudaCamadas} />
        <div className={`col${carregando ? " carregando" : ""}`}>
          <section className="sec" id="s2">
            <div className="sechead"><h2>Minha fazenda</h2><span className="small">{tag}</span></div>
            <div className="farmsum">
              <div className="kpi"><span className="eyebrow">Área</span><b className="mono">{A ? fmt(A.area, A.area < 100 ? 1 : 0) + " ha" : "–"}</b></div>
              <div className="kpi"><span className="eyebrow">Município</span><b style={{ fontSize: 16 }}>{A?.mun ?? "–"}</b></div>
              <div className="kpi"><span className="eyebrow">Morro (declive &gt;20%)</span><b className="mono">{A ? (A.relevo ? fmt(A.relevo.morro, 0) + "%" : "sem relevo") : "–"}</b></div>
            </div>
            <Perfil perfil={perfil} onChange={setPerfil} />
            <Fazendas atual={fazendaId} poligono={poly} perfil={perfil} exemplo={exemplo} onAbrir={abrir} onSalva={salva} onApagada={apagada} />
          </section>
          <section className="sec" id="s3">
            <div className="sechead"><h2>Riscos deste lugar</h2>{A && <span className="small mono">célula {fmt(A.celula.lat, 2)}; {fmt(A.celula.lon, 3)}</span>}</div>
            {erro && <p className="erro">{erro}</p>}
            {A ? <Riscos riscos={A.riscos} /> : <p className="small">Calculando com os dados da NASA…</p>}
          </section>
          {A && <Cenarios A={A} />}
        </div>
      </div>

      {A && <DadosNasa A={A} ano={ano} onAno={setAno} />}
      {A && <Pergunte poligono={poly} perfil={perfil} mensagem={A.mensagem} />}

      <footer className="foot">
        <span><b>Dados da solução:</b> NASA POWER diário (temperatura, chuva, umidade, vento e radiação), comunidade AG, grade de ~0,5° × 0,625° (cerca de 55 × 60 km), 1981–2025; SRTM 1″ (NASA/USGS) reamostrado a ~90 m. Contorno dos municípios: IBGE, só para desenho. Três parâmetros vêm de literatura externa (R = 0,88; raiz de 0,6 m; limiar de 2 °C do ZARC).</span>
        <span><b>Níveis de evidência (spec v2):</b> N2 · com ressalva = passou em parte e a direção bate com fonte externa; sai com faixa. N1 · em teste = sem número para o agricultor. Medido = fato do dado, sem previsão. Nenhum módulo é N3 (validado) hoje.</span>
        <span><b>Como foi validado:</b> data-limite do 2º milho (V2: geadas de estação aparecem no dado; muda até 29 dias entre municípios); geada tirando agosto do milho de verão (V4: a forma bate com o ZARC, a força não); aviso de ano seco (V1: 13 de 29 avisos em ano de quebra, mas deixa passar cerca de metade); sorgo no raso (V3: ajuda em 7 de 10 cenários, abaixo do corte de 7 em 10 que pedimos); erosividade (A3-1, em Ituporanga). Nada foi testado com agricultor.</span>
        <span><b>Limites:</b> a grade do clima é grossa e não vê o talhão; o solo vem do relevo e da sua resposta, não de análise; o relevo cobre todo o Oeste catarinense (SRTM a ~90 m). É chance, não garantia. A pergunta livre usa o Claude só para explicar os números do motor.</span>
      </footer>
    </div>
  );
}
