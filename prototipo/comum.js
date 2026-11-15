// Funções compartilhadas pelas duas abordagens. Sem bibliotecas.
const NOMES_FASE = ["emergência", "crescimento", "floração/enchimento", "maturação"];
const CLASSE_TXT = { boa: "Boa colheita", parcial: "Perde um pouco", perda: "Perde muito", total: "Perde quase tudo", sem_plantio: "Chuva não firmou" };
const CLASSE_COR = { boa: "var(--ok)", parcial: "var(--medio)", perda: "var(--ruim)", total: "var(--pessimo)", sem_plantio: "var(--cinza)" };

async function carregar() {
  const r = await fetch("dados/resultado.json");
  if (!r.ok) throw new Error("não achei dados/resultado.json");
  return r.json();
}

// 10 sacos: n cheios. Arredonda para inteiro, porque é o que a pessoa entende.
function sacos(n, tam = 26) {
  const cheios = Math.round(n);
  let s = `<span class="sacos" role="img" aria-label="${cheios} de 10 anos com boa colheita">`;
  for (let i = 0; i < 10; i++) {
    const f = i < cheios;
    s += `<svg width="${tam}" height="${tam * 1.15}" viewBox="0 0 24 28"><path d="M7 3h10l-1.5 4c3 1.5 5 5 5 9.5 0 5-3.6 8.5-8.5 8.5S3.500 21.500 3.500 16.500c0-4.500 2-8 5-9.500z" fill="${f ? "var(--saco)" : "none"}" stroke="${f ? "var(--saco-borda)" : "var(--cinza)"}" stroke-width="1.6" stroke-linejoin="round"/>${f ? "" : '<path d="M8 15l8 4M16 15l-8 4" stroke="var(--cinza)" stroke-width="1.2" opacity=".5"/>'}</svg>`;
  }
  return s + "</span>";
}

// Mensagem que o WhatsApp falaria. Só templates; todo número vem do modelo.
function mensagem(dados, ctx = {}) {
  const e = [...dados.estrategias].sort((a, b) => b.colhe_em_10 - a.colhe_em_10);
  const melhor = e[0];
  const atual = dados.estrategias.find((x) => x.id === "A");
  const r = (x) => Math.round(x.colhe_em_10);
  const nomeCult = (x) => ({ milho: "o milho", caupi: "o caupi", sorgo: "o sorgo" }[x.cultura]);
  const quando = (x) => (x.id === "B" || x.id === "E" ? " plantado só em 11 de março" : " plantado na primeira chuva");
  const txt = [
    `Pelos últimos 25 anos de chuva, em cada 10 anos ${nomeCult(atual)}${quando(atual)} dá boa colheita em ${r(atual)}.`,
    `${nomeCult(melhor)[0].toUpperCase() + nomeCult(melhor).slice(1)}${quando(melhor)} dá em ${r(melhor)}.`,
    melhor.pior_fase ? `Para ${nomeCult(melhor)}, o que mais derruba é a falta d'água na ${melhor.pior_fase}.` : "",
    melhor.cultura === "sorgo" ? "Confira se tem comprador para o sorgo." : "",
    "É uma chance, não uma garantia.",
  ].filter(Boolean).join(" ");
  return { melhor, atual, ordenadas: e, texto: txt, palavras: txt.split(/\s+/).length };
}

// Comparação com o ZARC. No ZARC, nível X% = risco de perda de até X%; ausente = acima de 40%.
function compararZarc(dados) {
  return dados.janelas_caupi.map((j) => {
    const falha = Math.round(100 - j.colhe_em_10 * 10);
    const z = dados.zarc_caupi_medio[j.dec] ?? null;
    const consistente = z === null ? falha > 40 : falha <= z;
    return { ...j, falha, zarc: z, consistente };
  });
}

function mesNome(m) { return ["jan", "fev", "mar", "abr", "mai", "jun"][m - 1]; }

// Gráfico de barras por ano (rendimento relativo), SVG simples.
function graficoAnos(est) {
  const w = 640, h = 150, m = 24, bw = (w - m) / est.anos.length;
  let s = `<svg viewBox="0 0 ${w} ${h + 22}" class="graf" role="img" aria-label="Rendimento por ano">`;
  s += `<line x1="${m}" x2="${w}" y1="${h - 0.6 * h * 0 - h * 0.6}" y2="${h - h * 0.6}" stroke="var(--linha)" stroke-dasharray="4 3"/>`;
  s += `<text x="0" y="${h - h * 0.6 + 4}" font-size="10" fill="var(--texto2)">60%</text>`;
  est.anos.forEach((a, i) => {
    const alt = Math.max(2, a.y * h);
    s += `<rect x="${m + i * bw + 1}" y="${h - alt}" width="${bw - 3}" height="${alt}" rx="2" fill="${CLASSE_COR[a.classe]}"><title>${a.ano}: ${Math.round(a.y * 100)}% (${CLASSE_TXT[a.classe]})</title></rect>`;
    if (i % 2 === 0) s += `<text x="${m + i * bw + bw / 2}" y="${h + 14}" font-size="9" text-anchor="middle" fill="var(--texto2)">${String(a.ano).slice(2)}</text>`;
  });
  return s + "</svg>";
}

// Gráfico: nossa chance de falhar por decêndio contra o nível do ZARC.
function graficoZarc(dados) {
  const c = compararZarc(dados).filter((j) => j.dec <= 15);
  const w = 640, h = 150, m = 28, bw = (w - m) / c.length;
  let s = `<svg viewBox="0 0 ${w} ${h + 30}" class="graf" role="img" aria-label="Risco calculado contra ZARC">`;
  [20, 40, 60, 80, 100].forEach((v) => {
    const y = h - (v / 100) * h;
    s += `<line x1="${m}" x2="${w}" y1="${y}" y2="${y}" stroke="var(--linha)" stroke-width=".6"/><text x="0" y="${y + 3}" font-size="9" fill="var(--texto2)">${v}%</text>`;
  });
  c.forEach((j, i) => {
    const x = m + i * bw;
    const alt = (j.falha / 100) * h;
    s += `<rect x="${x + 2}" y="${h - alt}" width="${bw - 6}" height="${Math.max(alt, 1)}" rx="2" fill="${j.consistente ? "var(--ok)" : "var(--ruim)"}" opacity=".85"><title>${j.dia}/${mesNome(j.mes)}: risco calculado ${j.falha}% | ZARC ${j.zarc ? "até " + j.zarc + "%" : "não recomendado"}</title></rect>`;
    const zy = j.zarc ? h - (j.zarc / 100) * h : null;
    if (zy !== null) s += `<line x1="${x + 1}" x2="${x + bw - 3}" y1="${zy}" y2="${zy}" stroke="var(--texto)" stroke-width="2.5"/>`;
    else s += `<text x="${x + bw / 2 - 1}" y="12" font-size="9" text-anchor="middle" fill="var(--texto2)">fora</text>`;
    s += `<text x="${x + bw / 2 - 1}" y="${h + 12}" font-size="9" text-anchor="middle" fill="var(--texto2)">${j.dia}</text>`;
    if (j.dia === 1) s += `<text x="${x + bw / 2 - 1}" y="${h + 25}" font-size="9" font-weight="600" text-anchor="middle" fill="var(--texto2)">${mesNome(j.mes)}</text>`;
  });
  return s + "</svg>";
}

function validacaoSecas(dados) {
  const secos = [2001, 2010, 2012, 2013, 2014, 2015, 2016, 2017, 2019];
  return dados.estrategias.map((e) => {
    const ys = Object.fromEntries(e.anos.map((a) => [a.ano, a.y]));
    const m = (arr) => arr.reduce((s, k) => s + ys[k], 0) / arr.length;
    const outros = e.anos.map((a) => a.ano).filter((a) => !secos.includes(a));
    return { id: e.id, nome: e.nome, seca: m(secos), outros: m(outros) };
  });
}

function tabelaAnos(est) {
  let s = `<table class="tab"><thead><tr><th>Ano</th><th>Plantio</th><th>Resultado</th><th>Rend.</th><th title="Água usada / água pedida em cada fase">Água por fase (ISNA)</th><th>Água no solo no plantio</th></tr></thead><tbody>`;
  est.anos.forEach((a) => {
    const d = a.plantio ? a.plantio.slice(8) + "/" + a.plantio.slice(5, 7) : "—";
    s += `<tr><td>${a.ano}</td><td>${d}</td><td><span class="ponto" style="background:${CLASSE_COR[a.classe]}"></span>${CLASSE_TXT[a.classe]}</td><td>${Math.round(a.y * 100)}%</td><td>${a.isna ? a.isna.map((v) => v.toFixed(2)).join(" · ") : "—"}</td><td>${a.agua_plantio ?? "—"} mm</td></tr>`;
  });
  return s + "</tbody></table>";
}

const PARAMS = {
  milho: { ciclo: "20/30/30/20 dias (100)", kc: "0,30 → 1,20 → 0,60", ky: "0,4 · 0,4 · 1,5 · 0,5", raiz: "1,0 m", fonte: "FAO-56 e FAO-33; fases iguais às do ZARC-CE" },
  caupi: { ciclo: "10/20/25/15 dias (70)", kc: "0,40 → 1,05 → 0,35", ky: "0,2 · 0,2 · 1,1 · 0,75", raiz: "0,6 m", fonte: "FAO-56 e FAO-33 (feijão); a conferir na portaria do ZARC" },
  sorgo: { ciclo: "20/30/30/20 dias (100)", kc: "0,30 → 1,05 → 0,55", ky: "0,2 · 0,2 · 0,55 · 0,45", raiz: "1,0 m", fonte: "FAO-56 e FAO-33; a conferir na portaria do ZARC" },
};

function painelParametros(est, dados) {
  const p = PARAMS[est.cultura];
  return `<dl class="params">
    <dt>Cultura</dt><dd>${est.nome}</dd>
    <dt>Solo</dt><dd>${est.solo === "medio" ? "médio" : est.solo} → água disponível ${({ arenoso: 65, medio: 125, argiloso: 175 })[est.solo]} mm/m × raiz ${p.raiz} = <b>${({ arenoso: 65, medio: 125, argiloso: 175 })[est.solo] * parseFloat(p.raiz)} mm</b> guardados</dd>
    <dt>Fases</dt><dd>${p.ciclo}</dd>
    <dt>Kc (início → meio → fim)</dt><dd>${p.kc}</dd>
    <dt>Ky por fase</dt><dd>${p.ky}</dd>
    <dt>Chuva e clima</dt><dd>${dados.fonte}</dd>
    <dt>Origem dos parâmetros</dt><dd>${p.fonte}</dd>
    <dt>Colher =</dt><dd>rendimento relativo ≥ ${Math.round(dados.limiar_colhe * 100)}% (perda menor que 40%)</dd>
  </dl>`;
}
