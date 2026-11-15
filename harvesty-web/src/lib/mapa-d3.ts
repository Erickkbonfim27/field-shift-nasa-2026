// Mapa do Oeste de SC em D3 (só no navegador): municípios, relevo do SRTM, camadas de clima do NASA POWER,
// desenho da fazenda. Portado de harvesty/src/app.html.
import * as d3 from "d3";
import type { CamadaCelula, Poligono } from "@/lib/tipos";
import { dataExt, ddmm, ddmmDoy } from "@/lib/formato";

export type Camada = "relevo" | "declive" | "geada" | "chuva";
export interface RelevoMeta { bbox: [number, number, number, number]; classes: string[]; folhas?: string[] }

const CORES_CL = ["#cfe3c4", "#a8cf8d", "#e6cf6a", "#e0913f", "#c4553a", "#7a2a22"];
type Feature = GeoJSON.Feature<GeoJSON.Polygon | GeoJSON.MultiPolygon, { cod: string; nome: string }>;

export interface EstadoCamadas { ativas: Set<Camada>; ano: number; celulas: CamadaCelula[] | null }

// eslint-disable-next-line @typescript-eslint/no-explicit-any
type G = d3.Selection<SVGGElement, any, null, undefined>;

export class MapaD3 {
  private svg: d3.Selection<SVGSVGElement, unknown, null, undefined>;
  private gZoom: G; private gBase: G; private gImg: G; private gCel: G; private gMun: G; private gLab: G; private gFarm: G; private gDraw: G;
  private proj = d3.geoMercator();
  private path = d3.geoPath(this.proj);
  private zoom: d3.ZoomBehavior<SVGSVGElement, unknown>;
  private W = 800; private H = 600; private K = 1;
  private malha: GeoJSON.FeatureCollection | null = null;
  private imgSombra: string | null = null; private imgDeclive: string | null = null;
  private poly: Poligono = [];
  private estado: EstadoCamadas = { ativas: new Set(["relevo"]), ano: 2022, celulas: null };
  private desenhando = false; private pontos: Poligono = [];

  constructor(el: SVGSVGElement, private relevo: RelevoMeta, private tip: HTMLDivElement, private aoDesenhar: (p: Poligono) => void, private legenda: (html: string) => void) {
    this.svg = d3.select(el);
    this.gZoom = this.svg.append("g");
    [this.gBase, this.gImg, this.gCel, this.gMun, this.gLab, this.gFarm, this.gDraw] = Array.from({ length: 7 }, () => this.gZoom.append("g"));
    this.zoom = d3.zoom<SVGSVGElement, unknown>().scaleExtent([1, 400]).clickDistance(5).on("zoom", (e) => {
      this.gZoom.attr("transform", e.transform.toString()); this.K = e.transform.k; this.ajustaEscala();
    });
    this.svg.call(this.zoom).on("dblclick.zoom", null);
    this.svg.on("click", (e: MouseEvent) => {
      if (!this.desenhando) return;
      const t = d3.zoomTransform(el);
      const p = this.proj.invert!(t.invert(d3.pointer(e, el)))!;
      this.pontos.push([+p[0].toFixed(5), +p[1].toFixed(5)]); this.desenhaRascunho();
    });
    this.svg.on("dblclick", (e: MouseEvent) => { if (this.desenhando) { e.preventDefault(); this.pontos.pop(); this.concluir(); } });
  }

  async carregar() {
    const fc = (await (await fetch("/dados/malha.json")).json()) as GeoJSON.FeatureCollection;
    fc.features.forEach((f) => {
      if (d3.geoArea(f) > 2 * Math.PI) {
        const inv = (g: GeoJSON.Position[][]) => g.map((anel) => anel.slice().reverse());
        const geo = f.geometry as GeoJSON.Polygon | GeoJSON.MultiPolygon;
        geo.coordinates = (geo.type === "Polygon" ? inv(geo.coordinates) : geo.coordinates.map(inv)) as never;
      }
    });
    this.malha = fc;
    this.tamanho(); this.desenhaBase();
    const [classes, sombra] = await Promise.all([carregaImg("/relevo/classes.png"), carregaImg("/relevo/sombra.png")]);
    this.imgSombra = sombra.src;
    const cv = document.createElement("canvas"); cv.width = classes.width; cv.height = classes.height;
    const cx = cv.getContext("2d")!; cx.drawImage(classes, 0, 0);
    const id = cx.getImageData(0, 0, cv.width, cv.height);
    const cor = CORES_CL.map((h) => [parseInt(h.slice(1, 3), 16), parseInt(h.slice(3, 5), 16), parseInt(h.slice(5, 7), 16)]);
    for (let i = 0; i < cv.width * cv.height; i++) {
      const v = id.data[i * 4];
      if (v > 5) { id.data[i * 4 + 3] = 0; continue; }
      const c = cor[v]; id.data[i * 4] = c[0]; id.data[i * 4 + 1] = c[1]; id.data[i * 4 + 2] = c[2]; id.data[i * 4 + 3] = 255;
    }
    cx.putImageData(id, 0, 0); this.imgDeclive = cv.toDataURL("image/png");
    this.desenhaCamada();
  }

  tamanho() {
    const r = (this.svg.node() as SVGSVGElement).getBoundingClientRect();
    this.W = Math.max(300, r.width); this.H = Math.max(300, r.height);
    this.svg.attr("viewBox", `0 0 ${this.W} ${this.H}`);
    if (this.malha) this.proj.fitExtent([[10, 10], [this.W - 10, this.H - 10]], this.malha);
  }

  redimensionar() { const t = d3.zoomTransform(this.svg.node()!); this.tamanho(); this.desenhaBase(); this.svg.call(this.zoom.transform, t); }

  setPoly(p: Poligono) { this.poly = p; this.desenhaFazenda(); }
  setCamadas(e: EstadoCamadas) { this.estado = e; this.desenhaCamada(); }

  vaiPara(poly: Poligono, k?: number) {
    if (!poly.length || !this.malha) return;
    const pts = poly.map((p) => this.proj(p)!);
    const x0 = d3.min(pts, (p) => p[0])!, x1 = d3.max(pts, (p) => p[0])!, y0 = d3.min(pts, (p) => p[1])!, y1 = d3.max(pts, (p) => p[1])!;
    const kk = k ?? Math.min(300, 0.35 * Math.min(this.W / Math.max(1, x1 - x0), this.H / Math.max(1, y1 - y0)));
    this.svg.transition().duration(650).call(this.zoom.transform, d3.zoomIdentity.translate(this.W / 2, this.H / 2).scale(kk).translate(-(x0 + x1) / 2, -(y0 + y1) / 2));
  }
  verRegiao() { this.svg.transition().duration(650).call(this.zoom.transform, d3.zoomIdentity); }
  get zoomAtual() { return this.K; }

  modoDesenho(on: boolean) {
    this.desenhando = on; this.pontos = [];
    (this.svg.node() as SVGSVGElement).classList.toggle("drawing", on);
    this.desenhaRascunho();
    if (on && this.K < 20) this.vaiPara(this.poly, 60);
  }
  desfazer() { this.pontos.pop(); this.desenhaRascunho(); }
  concluir(): boolean {
    if (this.pontos.length < 3) return false;
    const p = this.pontos.slice(); this.desenhando = false; this.pontos = [];
    (this.svg.node() as SVGSVGElement).classList.remove("drawing"); this.desenhaRascunho();
    this.aoDesenhar(p);
    return true;
  }

  // ---------- desenho ----------
  private desenhaBase() {
    if (!this.malha) return;
    const feats = this.malha.features as Feature[];
    this.gBase.selectAll("*").remove(); this.gMun.selectAll("*").remove(); this.gLab.selectAll("*").remove();
    this.gBase.append("path").datum(this.malha).attr("d", this.path).attr("fill", "var(--surface)").attr("stroke", "none");
    this.gMun.selectAll("path").data(feats).join("path").attr("d", this.path).attr("fill", "transparent").attr("stroke", "var(--ink)").attr("stroke-opacity", 0.35)
      .on("mousemove", (e: MouseEvent, d) => this.mostraTip(e, d)).on("mouseleave", () => { this.tip.hidden = true; });
    this.gLab.selectAll("text").data(feats).join("text").attr("x", (d) => this.path.centroid(d)[0]).attr("y", (d) => this.path.centroid(d)[1]).attr("text-anchor", "middle")
      .attr("fill", "var(--ink)").attr("pointer-events", "none").attr("font-family", "var(--body)").attr("paint-order", "stroke").attr("stroke", "var(--surface)").attr("stroke-width", 0.3).text((d) => d.properties.nome);
    this.desenhaCamada(); this.desenhaFazenda(); this.ajustaEscala();
  }

  private imgRelevo(href: string, op: number, pix = false) {
    const [w, s, e, n] = this.relevo.bbox, p0 = this.proj([w, n])!, p1 = this.proj([e, s])!;
    this.gImg.append("image").attr("href", href).attr("x", p0[0]).attr("y", p0[1]).attr("width", p1[0] - p0[0]).attr("height", p1[1] - p0[1])
      .attr("preserveAspectRatio", "none").attr("opacity", op).style("image-rendering", pix ? "pixelated" : "auto");
  }

  private desenhaCamada() {
    if (!this.malha) return;
    this.gImg.selectAll("*").remove(); this.gCel.selectAll("*").remove();
    const { ativas, ano, celulas } = this.estado, lg: string[] = [];
    const relevo = ativas.has("relevo"), declive = ativas.has("declive"), geada = ativas.has("geada"), chuva = ativas.has("chuva");
    if (this.imgSombra && (relevo || declive)) this.imgRelevo(this.imgSombra, relevo ? (declive ? 0.45 : 0.55) : 0.3);
    if (declive && this.imgDeclive) this.imgRelevo(this.imgDeclive, relevo ? 0.55 : 0.65, true);
    const [bw, bs, be, bn] = this.relevo.bbox;
    if (relevo) lg.push(`<span><b>Relevo</b>: sombreado do SRTM (NASA)${this.relevo.folhas ? ", " + this.relevo.folhas.length + " folhas" : ""}, longitude ${bw} a ${be}, latitude ${bs} a ${bn}.</span>`);
    if (declive) lg.push("<span><b>Declive</b> (SRTM, ~90 m):</span>" + this.relevo.classes.slice(0, 5).map((t, i) => `<span><i style="background:${CORES_CL[i]}"></i>${t}</span>`).join(""));
    if ((geada || chuva) && celulas) {
      const vals = celulas.map((c) => {
        const xy = this.proj([c.lon, c.lat])!, hy = Math.abs(this.proj([c.lon, c.lat + 0.25])![1] - this.proj([c.lon, c.lat - 0.25])![1]);
        return { c, x: xy[0], y: xy[1], hy, g: c.limite ? ddmmDoy(c.limite) : 90, gt: c.limite ? ddmm(ddmmDoy(c.limite)) : "sem data", r: (c.chuvaPct ?? 100) / 100, rt: `${c.chuvaPct ?? "–"}%` };
      });
      const colG = d3.scaleSequential([50, 15], d3.interpolatePuBu).clamp(true), colR = d3.scaleDiverging([0.4, 1, 1.6], d3.interpolateBrBG).clamp(true);
      const ambas = geada && chuva;
      const quadrado = (c: CamadaCelula): GeoJSON.Polygon => {
        const a = 0.25, b = 0.3125;
        return { type: "Polygon", coordinates: [[[c.lon - b, c.lat - a], [c.lon - b, c.lat + a], [c.lon + b, c.lat + a], [c.lon + b, c.lat - a], [c.lon - b, c.lat - a]]] };
      };
      this.gCel.selectAll("path.cel").data(vals).join("path").attr("class", "cel").attr("d", (d) => this.path(quadrado(d.c)))
        .attr("fill", (d) => (geada ? colG(d.g) : colR(d.r))).attr("fill-opacity", relevo || declive ? 0.5 : 0.62).attr("stroke", "var(--surface)");
      if (ambas) this.gCel.selectAll("circle.chuva").data(vals).join("circle").attr("class", "chuva").attr("cx", (d) => d.x).attr("cy", (d) => d.y + d.hy * 0.1)
        .attr("r", (d) => d.hy * 0.24).attr("fill", (d) => colR(d.r)).attr("stroke", "#13201a");
      const rot = vals.flatMap((d) => (ambas ? [{ x: d.x, y: d.y - d.hy * 0.3, t: d.gt }, { x: d.x, y: d.y + d.hy * 0.1, t: d.rt }] : [{ x: d.x, y: d.y, t: geada ? d.gt : d.rt }]));
      this.gCel.selectAll("text.lbl").data(rot).join("text").attr("class", "lbl").attr("x", (d) => d.x).attr("y", (d) => d.y).attr("text-anchor", "middle").attr("dominant-baseline", "middle")
        .attr("font-family", "var(--mono)").attr("font-weight", 600).attr("fill", "#ffffff").attr("stroke", "#13201a").attr("paint-order", "stroke").attr("pointer-events", "none").text((d) => d.t);
      if (geada) lg.push(`<span><b>Geada no 2º milho${ambas ? " (quadrado)" : ""}</b>: data-limite por ponto do NASA POWER (até 2 anos em 10 com geada antes do corte). Mais escuro: data mais cedo. N2.</span>`);
      if (chuva) lg.push(`<span><b>Chuva dez–fev ${ano}${ambas ? " (círculo)" : ""}</b>: % do normal por ponto do NASA POWER. Marrom: seco. Verde: chuvoso. Troque o ano em “Dados da NASA neste ponto”.</span>`);
    } else if (geada || chuva) lg.push("<span>Carregando as camadas de clima…</span>");
    this.legenda(lg.length ? lg.join("") : "<span>Nenhuma camada ligada. Ligue uma ou mais acima.</span>");
    this.ajustaEscala();
  }

  private desenhaFazenda() {
    this.gFarm.selectAll("*").remove();
    if (!this.malha || this.poly.length < 3) return;
    const anel = [...this.poly, this.poly[0]];
    this.gFarm.append("path").attr("d", d3.line()(anel.map((p) => this.proj(p)!))!).attr("fill", "var(--farm)").attr("fill-opacity", 0.28).attr("stroke", "var(--farm)").attr("stroke-linejoin", "round");
    const cc = this.proj(d3.polygonCentroid(this.poly))!;
    this.gFarm.append("circle").attr("class", "pin").attr("cx", cc[0]).attr("cy", cc[1]).attr("fill", "var(--farm)").attr("stroke", "#13201a");
    this.ajustaEscala();
  }

  private desenhaRascunho() {
    this.gDraw.selectAll("*").remove();
    if (!this.pontos.length) return;
    const pp = this.pontos.map((p) => this.proj(p)!);
    this.gDraw.append("path").attr("d", d3.line()(pp)!).attr("fill", "none").attr("stroke", "var(--farm)").attr("stroke-dasharray", "4 3");
    this.gDraw.selectAll("circle").data(pp).join("circle").attr("cx", (p) => p[0]).attr("cy", (p) => p[1]).attr("fill", "var(--farm)").attr("stroke", "var(--surface)");
    this.ajustaEscala();
  }

  private ajustaEscala() {
    const K = this.K;
    this.gMun.selectAll("path").attr("stroke-width", 0.8 / K); this.gCel.selectAll("path").attr("stroke-width", 1 / K);
    this.gLab.selectAll<SVGTextElement, Feature>("text").attr("font-size", 11 / K).attr("display", (d) => (K > 3.5 || ["São Miguel do Oeste", "Chapecó"].includes(d.properties.nome) ? null : "none"));
    this.gCel.selectAll("text").attr("font-size", 12 / K).attr("stroke-width", 2.6 / K); this.gCel.selectAll("circle.chuva").attr("stroke-width", 1.2 / K);
    this.gFarm.selectAll("path").attr("stroke-width", 2.5 / K);
    this.gFarm.selectAll("circle.pin").attr("r", 6 / K).attr("stroke-width", 1.5 / K).attr("display", K > 25 ? "none" : null);
    this.gDraw.selectAll("circle").attr("r", 4 / K); this.gDraw.selectAll("path").attr("stroke-width", 2 / K);
  }

  private mostraTip(e: MouseEvent, d: Feature) {
    const el = this.svg.node()!, caixa = el.parentElement!;
    const [mx, my] = d3.pointer(e, caixa);
    const ll = this.proj.invert!(d3.zoomTransform(el).invert(d3.pointer(e, el)))!;
    const linhas: string[] = [];
    const cels = this.estado.celulas;
    if (cels && (this.estado.ativas.has("geada") || this.estado.ativas.has("chuva"))) {
      let c = cels[0], best = Infinity;
      for (const x of cels) { const dd = (x.lat - ll[1]) ** 2 + ((x.lon - ll[0]) * 0.8) ** 2; if (dd < best) { best = dd; c = x; } }
      if (this.estado.ativas.has("geada")) linhas.push("2º milho até " + (c.limite ? dataExt(c.limite) : "sem data segura"));
      if (this.estado.ativas.has("chuva")) linhas.push(`dez–fev ${this.estado.ano}: ${c.chuvaPct ?? "–"}% do normal`);
    }
    const t = this.tip;
    t.innerHTML = "";
    const b = document.createElement("b"); b.textContent = d.properties.nome; t.appendChild(b);
    for (const l of linhas) { t.appendChild(document.createElement("br")); t.appendChild(document.createTextNode(l)); }
    t.style.left = Math.min(mx + 12, this.W - 230) + "px"; t.style.top = my + 12 + "px"; t.hidden = false;
  }
}

function carregaImg(src: string): Promise<HTMLImageElement> {
  return new Promise((ok, falha) => { const im = new Image(); im.onload = () => ok(im); im.onerror = falha; im.src = src; });
}
