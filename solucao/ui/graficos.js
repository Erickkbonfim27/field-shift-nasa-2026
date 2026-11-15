"use strict";
/* Gráficos em SVG feitos à mão. Cada função recebe pedaços do JSON e devolve uma string de SVG.
   As escalas (0 a 10 anos, 0 a 100 de percentil) vêm do contrato. O resto vem dos dados. */

function svgSaco(cheio) {
  const corpo = "M7 3h10l-1.500 4c3 1.500 5 5 5 9.500 0 5-3.600 8.500-8.500 8.500S3.500 21.500 3.500 16.500c0-4.500 2-8 5-9.500z";
  return `<svg viewBox="0 0 24 28" aria-hidden="true"><path class="${cheio ? "saco-cheio" : "saco-rasgado"}" d="${corpo}"/>${cheio ? "" : '<path class="saco-risco" d="M8.500 13.500l7 7M15.500 13.500l-7 7"/>'}</svg>`;
}

/* 10 sacos: cheios + rasgados = 10 (regra R7). */
function htmlSacos(cheios, rasgados) {
  let s = `<div class="sacos" role="img" aria-label="${cheios} sacos cheios e ${rasgados} rasgados">`;
  for (let i = 0; i < cheios + rasgados; i++) s += svgSaco(i < cheios);
  return s + "</div>";
}

function htmlCartaoSacos(im) {
  const linhas = (im.linhas || []).map((l) => {
    const selo = `<span class="selo ${esc(l.selo)}">${esc(SELO[l.selo] || l.selo)}</span>`;
    if (l.cheios === null || l.rasgados === null) {
      return `<div class="linha-saco"><div class="topo-l"><span class="rot">${esc(l.rotulo)}</span>${selo}</div><span class="em-teste-txt">ainda em teste, sem número</span></div>`;
    }
    return `<div class="linha-saco"><div class="topo-l"><span class="rot">${esc(l.rotulo)}</span><span class="num">${n(l.rasgados)}<small> em ${n(l.cheios + l.rasgados)}</small></span></div>
      ${htmlSacos(l.cheios, l.rasgados)}<div style="margin-top:6px">${selo}</div></div>`;
  }).join("");
  return `<div class="cartao-img">${linhas}${im.legenda ? `<div class="legenda">${esc(im.legenda)}</div>` : ""}</div>`;
}

/* barras_relativas: valor com faixa (ex.: só milho = 100). */
function htmlCartaoBarras(im) {
  const bs = im.barras || [];
  const max = Math.max(...bs.map((b) => Math.max(b.valor, b.faixa ? b.faixa[1] : 0)), 1);
  const W = 340, x0 = 8, xw = 250, h = 72, alt = bs.length * h + 8;
  let s = `<svg class="graf" viewBox="0 0 ${W} ${alt}" role="img" aria-label="${esc(im.legenda || "Barras relativas")}">`;
  bs.forEach((b, i) => {
    const y = 4 + i * h;
    const w = (b.valor / max) * xw;
    s += `<text x="${x0}" y="${y + 13}" font-size="13">${esc(b.rotulo)}</text>`;
    s += `<rect class="${i === 0 ? "barra2" : "barra"}" x="${x0}" y="${y + 19}" width="${w}" height="16" rx="3"/>`;
    s += `<text x="${x0 + w + 6}" y="${y + 32}" font-size="15" font-weight="700">${n(b.valor)}</text>`;
    if (b.faixa) {
      const a = x0 + (b.faixa[0] / max) * xw, c = x0 + (b.faixa[1] / max) * xw, yy = y + 48;
      s += `<path class="ic" d="M${a} ${yy - 6}v12M${c} ${yy - 6}v12M${a} ${yy}H${c}"/>`;
      s += `<text class="suave" x="${a}" y="${yy + 16}" font-size="11.5">faixa dos parâmetros: ${n(b.faixa[0])} a ${n(b.faixa[1])}</text>`;
    }
  });
  s += "</svg>";
  return `<div class="cartao-img">${s}${im.legenda ? `<div class="legenda">${esc(im.legenda)}</div>` : ""}</div>`;
}

/* janela_decendios: uma célula por decêndio, com o em10 da estratégia ligada ao cartão. */
function htmlCartaoJanela(im, est) {
  const ls = est && est.risco_por_decendio ? est.risco_por_decendio.linhas.filter((l) => l.em10 !== null) : [];
  if (!ls.length) return `<div class="cartao-img"><div class="legenda">Sem decêndios para mostrar.</div></div>`;
  const cols = Math.min(ls.length, 5);
  return `<div class="cartao-img"><div class="tira" style="grid-template-columns:repeat(${cols},minmax(0,1fr))">${ls.map((l) =>
    `<div class="tira-celula"><b>${n(l.em10)}</b>${esc(l.decendio)}<span class="tira-bar"><i style="width:${Math.min(l.em10, 10) * 10}%"></i></span></div>`).join("")}</div>
    <div class="legenda">${esc(im.legenda || "Anos com o evento em 10, por decêndio de plantio. Barra cheia = 10 em 10.")}</div></div>`;
}

function htmlImagem(card, doc) {
  const im = card.imagem;
  if (!im || im.tipo === "nenhuma") return "";
  if (im.tipo === "10_sacos") return htmlCartaoSacos(im);
  if (im.tipo === "barras_relativas") return htmlCartaoBarras(im);
  if (im.tipo === "janela_decendios") {
    const est = (card.estrategia_ids || []).map((id) => doc.estrategias.find((e) => e.id === id)).find((e) => e && e.risco_por_decendio);
    return htmlCartaoJanela(im, est);
  }
  return "";
}

/* Risco por decêndio: barra = em10 (0 a 10), traço = IC95, losango = ZARC (só conferência). */
function svgRisco(est) {
  const rp = est.risco_por_decendio;
  const ls = rp.linhas;
  const W = 360, esq = 46, dir = 56, topo = 26, h = 26;
  const xw = W - esq - dir;
  const alt = topo + ls.length * h + 6;
  const X = (v) => esq + (v / 10) * xw;
  let s = `<svg class="graf" viewBox="0 0 ${W} ${alt}" role="img" aria-label="Anos com o evento em 10, por decêndio de plantio">`;
  for (let v = 0; v <= 10; v += 2) {
    s += `<line class="grade-l" x1="${X(v)}" x2="${X(v)}" y1="${topo - 4}" y2="${alt - 4}"/><text class="suave" x="${X(v)}" y="${topo - 10}" font-size="11" text-anchor="middle">${v}</text>`;
  }
  ls.forEach((l, i) => {
    const y = topo + i * h;
    s += `<text x="${esq - 6}" y="${y + 16}" font-size="12" text-anchor="end">${esc(l.decendio)}</text>`;
    if (l.em10 !== null) {
      const tit = `${l.decendio}: ${n(l.em10)} em 10${l.ic95 ? `, IC95 ${n(l.ic95[0])} a ${n(l.ic95[1])}` : ""}${l.k !== null ? `, ${l.k} de ${l.n} anos` : ""}`;
      s += `<rect class="barra" x="${esq}" y="${y + 4}" width="${Math.max(X(l.em10) - esq, 1)}" height="14" rx="2"><title>${esc(tit)}</title></rect>`;
      if (l.ic95) {
        const a = X(l.ic95[0]), c = X(l.ic95[1]), yy = y + 11;
        s += `<path class="ic" d="M${a} ${yy - 5}v10M${c} ${yy - 5}v10M${a} ${yy}H${c}"/>`;
      }
      s += `<text x="${W - dir + 8}" y="${y + 16}" font-size="12.5" font-weight="700">${n(l.em10)}</text>`;
    }
    if (l.zarc && l.zarc.risco_pct !== null && l.zarc.risco_pct !== undefined) {
      const zx = X(l.zarc.risco_pct / 10), zy = y + 11;
      s += `<path class="zarc" d="M${zx} ${zy - 7}l6 7l-6 7l-6 -7z"><title>ZARC (conferência): ${l.zarc.risco_pct}% = ${l.zarc.risco_pct / 10} em 10</title></path>`;
    }
  });
  return s + "</svg>";
}
function legRisco(est) {
  const tem = est.risco_por_decendio.linhas.some((l) => l.zarc && l.zarc.risco_pct);
  const ic = est.risco_por_decendio.linhas.some((l) => l.ic95);
  return `<div class="leg"><span><i class="b1"></i>anos com o evento, em 10</span>${ic ? '<span><i class="ic"></i>IC95 (amostragem)</span>' : ""}${tem ? '<span><i class="zc"></i>ZARC, só conferência (20/30/40% = 2/3/4 em 10)</span>' : ""}</div>`;
}

/* Métricas extras (ex.: mistura com sorgo): pior ano em 10 da base e da mistura, por decêndio. */
function svgMetricas(est) {
  const ls = est.risco_por_decendio.linhas.filter((l) => l.metricas_extra && "p10_base" in l.metricas_extra && "p10_mistura" in l.metricas_extra);
  if (!ls.length) return "";
  const max = Math.max(...ls.map((l) => Math.max(l.metricas_extra.p10_base, l.metricas_extra.p10_mistura)));
  const W = 360, esq = 46, dir = 70, topo = 8, h = 40;
  const xw = W - esq - dir;
  const alt = topo + ls.length * h + 6;
  let s = `<svg class="graf" viewBox="0 0 ${W} ${alt}" role="img" aria-label="Pior ano em 10, só milho e com sorgo, por decêndio">`;
  ls.forEach((l, i) => {
    const y = topo + i * h, m = l.metricas_extra;
    s += `<text x="${esq - 6}" y="${y + 20}" font-size="12" text-anchor="end">${esc(l.decendio)}</text>`;
    s += `<rect class="barra2" x="${esq}" y="${y + 3}" width="${(m.p10_base / max) * xw}" height="13" rx="2"/><text class="suave" x="${esq + (m.p10_base / max) * xw + 5}" y="${y + 14}" font-size="11">${n(m.p10_base)}</text>`;
    s += `<rect class="barra" x="${esq}" y="${y + 19}" width="${(m.p10_mistura / max) * xw}" height="13" rx="2"/><text x="${esq + (m.p10_mistura / max) * xw + 5}" y="${y + 30}" font-size="11.5" font-weight="700">${n(m.p10_mistura)}</text>`;
    if ("ganho_p10_pct" in m) s += `<text x="${W - 4}" y="${y + 22}" font-size="12.5" font-weight="700" text-anchor="end">${m.ganho_p10_pct > 0 ? "+" : ""}${n(m.ganho_p10_pct)}%</text>`;
  });
  return s + "</svg>";
}
const LEG_METRICAS = `<div class="leg"><span><i class="b2"></i>só milho (pior ano em 10, fração do potencial)</span><span><i class="b1"></i>com sorgo</span><span>número à direita = ganho no pior ano</span></div>`;

/* Posição do índice entre os anos passados (alerta). */
function svgAlerta(a) {
  const p = a.percentil_local;
  if (!p || p.valor === null) return "";
  const excesso = /excesso/.test(a.modulo_id);
  const W = 360, x0 = 14, xw = W - 28, y = 30;
  const X = (v) => x0 + (v / 100) * xw;
  const zona = excesso ? [100 - p.limiar, 100] : [0, p.limiar];
  let s = `<svg class="graf" viewBox="0 0 ${W} 84" role="img" aria-label="Posição do índice entre os anos passados: ${n(p.valor)} de 100">`;
  s += `<rect class="trilho" x="${x0}" y="${y}" width="${xw}" height="16" rx="8"/>`;
  s += `<rect class="zona" x="${X(zona[0])}" y="${y}" width="${X(zona[1]) - X(zona[0])}" height="16" rx="8"/>`;
  s += `<text class="suave" x="${x0}" y="${y + 34}" font-size="11">0</text><text class="suave" x="${x0 + xw}" y="${y + 34}" font-size="11" text-anchor="end">100</text>`;
  const rotz = `zona de alerta: ${excesso ? "acima de " + n(100 - p.limiar) : "até " + n(p.limiar)}`;
  s += excesso
    ? `<text class="suave" x="${X(zona[0]) - 6}" y="${y + 34}" font-size="11" text-anchor="end">${rotz}</text>`
    : `<text class="suave" x="${X(zona[1]) + 6}" y="${y + 34}" font-size="11">${rotz}</text>`;
  const mx = X(p.valor);
  s += `<path class="marca-v" d="M${mx} ${y + 20}l-7 -9h14z"/><circle class="marca-v" cx="${mx}" cy="${y + 8}" r="9"/>`;
  s += `<text x="${Math.min(Math.max(mx, 40), W - 40)}" y="${y - 8}" font-size="12.5" font-weight="700" text-anchor="middle">posição ${n(p.valor)}</text>`;
  return s + "</svg>";
}

/* Faixa de um indicador: parâmetros (claro), IC95 (traço) e valor (ponto). */
function svgFaixaInd(i) {
  if (typeof i.valor !== "number" || (!i.ic95 && !i.faixa_parametros)) return "";
  const pts = [i.valor, ...(i.ic95 || []), ...(i.faixa_parametros || [])];
  let lo = Math.min(...pts), hi = Math.max(...pts);
  if (lo === hi) { lo -= 1; hi += 1; }
  const W = 340, x0 = 12, xw = W - 24;
  const X = (v) => x0 + ((v - lo) / (hi - lo)) * xw;
  let s = `<svg class="graf" viewBox="0 0 ${W} 58" role="img" aria-label="Valor ${n(i.valor)} com faixas de incerteza">`;
  if (i.faixa_parametros) s += `<rect class="faixa-p" x="${X(i.faixa_parametros[0])}" y="8" width="${X(i.faixa_parametros[1]) - X(i.faixa_parametros[0])}" height="14" rx="3"/>`;
  if (i.ic95) { const a = X(i.ic95[0]), c = X(i.ic95[1]); s += `<path class="ic" d="M${a} 11v8M${c} 11v8M${a} 15H${c}"/>`; }
  s += `<circle class="marca-v" cx="${X(i.valor)}" cy="15" r="6"/>`;
  s += `<text class="suave" x="${x0}" y="46" font-size="11">${n(lo)}</text><text class="suave" x="${x0 + xw}" y="46" font-size="11" text-anchor="end">${n(hi)}</text>`;
  return s + "</svg>";
}
function legFaixaInd(i) {
  return `<div class="leg">${i.faixa_parametros ? '<span><i class="fp"></i>faixa dos parâmetros</span>' : ""}${i.ic95 ? '<span><i class="ic"></i>IC95 (amostragem)</span>' : ""}<span>ponto = valor</span></div>`;
}

/* Calendário de plantio: uma barra por etapa com datas, eixo em meses. */
const DIAS_MES = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];
const INI_MES = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334];
function doy(dm) { const [d, m] = dm.split("/").map(Number); return INI_MES[m - 1] + d - 1; }
function mesDe(p) { let m = 11; while (INI_MES[m] > p) m--; return m; }
function svgCalendario(estrategias) {
  const itens = [];
  estrategias.forEach((e) => (e.sequencia || []).forEach((et) => {
    if (et.plantio && et.plantio.de && et.plantio.ate) itens.push({ e, et, a: doy(et.plantio.de), b: doy(et.plantio.ate) });
  }));
  if (!itens.length) return "";
  const pts = [...new Set(itens.flatMap((x) => [x.a, x.b]))].sort((a, b) => a - b);
  let gap = -1, ini = pts[0];
  pts.forEach((p, i) => { const prox = pts[(i + 1) % pts.length]; const g = (prox - p + 365) % 365 || 365; if (g > gap) { gap = g; ini = prox; } });
  const s0 = INI_MES[mesDe(ini)];
  const off = (p) => (p - s0 + 365) % 365;
  const fimAbs = Math.max(...itens.map((x) => off(x.b)));
  const mFim = mesDe((s0 + fimAbs) % 365);
  const total = Math.max(((INI_MES[mFim] + DIAS_MES[mFim]) - s0 + 365) % 365, fimAbs + 1);
  const W = 360, x0 = 8, xw = W - 16, topo = 22, h = 40;
  const X = (o) => x0 + (o / total) * xw;
  const alt = topo + itens.length * h + 6;
  let s = `<svg class="graf" viewBox="0 0 ${W} ${alt}" role="img" aria-label="Janelas de plantio por estratégia">`;
  for (let k = 0, m = mesDe(s0), o = 0; o < total; k++) {
    s += `<line class="grade-l" x1="${X(o)}" x2="${X(o)}" y1="${topo - 4}" y2="${alt - 4}"/><text class="suave" x="${X(o) + 3}" y="${topo - 8}" font-size="11">${MESES[m]}</text>`;
    o += DIAS_MES[m]; m = (m + 1) % 12;
    if (k > 14) break;
  }
  itens.forEach((it, i) => {
    const y = topo + i * h;
    const a = X(off(it.a)), b = X(off(it.b) + 1);
    s += `<text x="${x0}" y="${y + 12}" font-size="12">${esc(it.e.id)} · ${esc(CULTURA[it.et.cultura] || it.et.cultura)} (${esc(ESTACAO[it.et.estacao] || it.et.estacao)})${it.et.fracao_area < 1 ? ` · ${n(Math.round(it.et.fracao_area * 100))}% da área` : ""}</text>`;
    s += `<rect class="${it.e.e_atual ? "barra2" : "barra"}" x="${a}" y="${y + 17}" width="${Math.max(b - a, 4)}" height="12" rx="3"><title>${esc(it.et.plantio.de)} a ${esc(it.et.plantio.ate)}</title></rect>`;
    const rot = `${esc(it.et.plantio.de)} a ${esc(it.et.plantio.ate)}`;
    if (b + 5 + 80 <= W) s += `<text class="suave" x="${b + 5}" y="${y + 27}" font-size="11">${rot}</text>`;
    else s += `<text class="suave" x="${Math.max(a - 5, 80)}" y="${y + 27}" font-size="11" text-anchor="end">${rot}</text>`;
  });
  return s + "</svg>";
}
