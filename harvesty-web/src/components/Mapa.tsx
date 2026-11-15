"use client";
import { useEffect, useRef, useState } from "react";
import { MapaD3, type Camada, type RelevoMeta } from "@/lib/mapa-d3";
import type { CamadaCelula, Poligono } from "@/lib/tipos";

const ROTULOS: [Camada, string][] = [["relevo", "Relevo (SRTM)"], ["declive", "Declive (SRTM)"], ["geada", "Geada no 2º milho (POWER)"], ["chuva", "Chuva dez–fev (POWER)"]];

interface Props {
  relevo: RelevoMeta;
  poligono: Poligono;
  camadas: Set<Camada>;
  ano: number;
  celulas: CamadaCelula[] | null;
  onDesenhar: (p: Poligono) => void;
  onCamadas: (c: Set<Camada>) => void;
}

export default function Mapa({ relevo, poligono, camadas, ano, celulas, onDesenhar, onCamadas }: Props) {
  const svgRef = useRef<SVGSVGElement>(null), tipRef = useRef<HTMLDivElement>(null);
  const mapa = useRef<MapaD3 | null>(null);
  const [desenhando, setDesenhando] = useState(false);
  const [aviso, setAviso] = useState("Clique para marcar os cantos da fazenda. Dois cliques ou “Concluir área” fecham o desenho.");
  const [legenda, setLegenda] = useState("");
  const aoDesenhar = useRef(onDesenhar);
  aoDesenhar.current = onDesenhar;

  useEffect(() => {
    if (!svgRef.current || !tipRef.current) return;
    const m = new MapaD3(svgRef.current, relevo, tipRef.current, (p) => { setDesenhando(false); aoDesenhar.current(p); }, setLegenda);
    mapa.current = m;
    m.carregar().then(() => { m.setPoly(poligono); setTimeout(() => m.vaiPara(poligono, 14), 50); });
    const r = () => m.redimensionar();
    window.addEventListener("resize", r);
    return () => window.removeEventListener("resize", r);
    // o mapa é criado uma vez; poligono e camadas chegam pelos efeitos abaixo
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [relevo]);

  useEffect(() => { mapa.current?.setPoly(poligono); }, [poligono]);
  useEffect(() => { mapa.current?.setCamadas({ ativas: camadas, ano, celulas }); }, [camadas, ano, celulas]);

  function alterna(k: Camada) {
    const novo = new Set(camadas), liga = !novo.has(k);
    if (liga) novo.add(k); else novo.delete(k);
    onCamadas(novo);
    const m = mapa.current;
    if (!m) return;
    if (liga && (k === "geada" || k === "chuva") && m.zoomAtual > 3) m.verRegiao();
    if (liga && (k === "relevo" || k === "declive") && m.zoomAtual < 6) m.vaiPara(poligono, 14);
  }

  return (
    <section className="mapcard" id="s1" aria-label="Mapa">
      <div className="maptools">
        {!desenhando && <button className="btn pri" onClick={() => { setDesenhando(true); mapa.current?.modoDesenho(true); }}>Desenhar minha fazenda</button>}
        {desenhando && <>
          <button className="btn" onClick={() => { if (!mapa.current?.concluir()) setAviso("Marque pelo menos 3 cantos."); }}>Concluir área</button>
          <button className="btn" onClick={() => mapa.current?.desfazer()}>Desfazer ponto</button>
          <button className="btn" onClick={() => { setDesenhando(false); mapa.current?.modoDesenho(false); }}>Cancelar</button>
        </>}
        <span className="sep" />
        <button className="btn" onClick={() => mapa.current?.vaiPara(poligono)}>Ir para a fazenda</button>
        <button className="btn" onClick={() => mapa.current?.verRegiao()}>Ver o Oeste</button>
      </div>
      <div className="layers" role="group" aria-label="Camadas do mapa: ligue quantas quiser">
        {ROTULOS.map(([k, t]) => <button key={k} aria-pressed={camadas.has(k)} onClick={() => alterna(k)}>{t}</button>)}
        <span className="small" style={{ alignSelf: "center", marginLeft: 4 }}>ligue quantas quiser</span>
      </div>
      <div className="mapwrap">
        <svg id="mapa" ref={svgRef} role="img" aria-label="Mapa do Oeste de Santa Catarina com a fazenda e as camadas de dados NASA" />
        <div className="hint" hidden={!desenhando}>{aviso}</div>
        <div className="tip" ref={tipRef} hidden />
      </div>
      <div className="legend" dangerouslySetInnerHTML={{ __html: legenda }} />
    </section>
  );
}
