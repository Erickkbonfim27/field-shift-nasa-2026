#!/usr/bin/env python3
"""Patch único (já aplicado) que alinhou src/app.html à spec v2 de solucao/.
Mantido só como registro do que mudou; rodar de novo falha de propósito nas marcas já trocadas."""
import sys
from pathlib import Path

P = Path(__file__).resolve().parent.parent / "src" / "app.html"
s = P.read_text(encoding="utf-8")


def troca(antigo, novo):
    global s
    if antigo not in s:
        sys.exit("marca não encontrada: " + antigo[:80])
    s = s.replace(antigo, novo, 1)


def troca_bloco(inicio, fim, novo):
    """Troca do início de `inicio` até antes de `fim`."""
    global s
    i = s.index(inicio)
    j = s.index(fim, i)
    s = s[:i] + novo + s[j:]


# ---------- período vem do pacote (1981–2025) ----------
troca('const T0 = Date.UTC(1984, 0, 1), ND = PK.ndias, ANO0 = 1984, ANO1 = 2025;',
      'const [Y0, M0, D0] = PK.ini.split("-").map(Number);\n'
      'const T0 = Date.UTC(Y0, M0 - 1, D0), ND = PK.ndias, ANO0 = Y0, ANO1 = 2025;')
troca('const D = dados(c); let i = idx(y, m, d); const fim = i + 240; let s = 0, g = false;',
      'const D = dados(c); let i = idx(y, m, d); const fim = idx(y, 9, 30); let s = 0, g = false;  // corte em 30/set, como no motor')
troca('for (let y = 1985; y <= ANO1; y++) df.push',
      'for (let y = ANO0 + 1; y <= ANO1; y++) df.push')

# ---------- utilitários: IC de Wilson e arredondamento R7 ----------
troca('const cacheCurva = new Map();',
      '''function wilson10(k, n) { if (!n) return [null, null]; const z = 1.96, p = k / n, den = 1 + z * z / n, c = (p + z * z / (2 * n)) / den, h = z * Math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den; return [Math.round(100 * Math.max(0, c - h)) / 10, Math.round(100 * Math.min(1, c + h)) / 10]; }
function chanceIC(c, m, d, L, gdd) { let k = 0, n = 0; for (let y = ANO0; y <= ANO1; y++) { const r = safra(c, y, m, d, L, gdd); if (r) { n++; if (r.g) k++; } } return n ? { v: 10 * k / n, ic: wilson10(k, n), k, n } : null; }
// regra R7 da spec: inteiro com meio para cima; entre 0 e 0,5 "menos de 1"; zero "quase nunca"
const r7 = (x) => Math.floor(x + 0.5);
function em10txt(v) { if (v === null || v === undefined) return "sem dado"; if (v === 0) return "quase nunca"; if (v < 0.5) return "menos de 1 de cada 10 anos"; return "cerca de " + r7(v) + " de cada 10 anos"; }
function em10curto(v) { if (v === null || v === undefined) return "–"; if (v === 0) return "quase nunca"; if (v < 0.5) return "menos de 1 em 10"; return r7(v) + " em 10"; }
function faixaTxt(ic) { return ic && ic[0] !== null && ic[0] !== undefined ? " (entre " + r7(ic[0]) + " e " + r7(ic[1]) + ")" : ""; }
const MESES_EXT = ["janeiro","fevereiro","março","abril","maio","junho","julho","agosto","setembro","outubro","novembro","dezembro"];
const dataExt = (s) => { if (!s) return "sem data"; const [d, m] = s.split("/").map(Number); return (d === 1 ? "1º" : d) + " de " + MESES_EXT[m - 1]; };
const ddmmDoy = (s) => { const [d, m] = s.split("/").map(Number); return Math.round((Date.UTC(2001, m - 1, d) - Date.UTC(2001, 0, 1)) / 864e5) + 1; };
const cacheCurva = new Map();''')

# ---------- análise da fazenda ----------
troca_bloco('function analise() {', 'const SORGO = ', '''function analise() {
  const P = lerPerfil(), poly = S.poly;
  const centro = d3.polygonCentroid(poly), c = celulaMaisProxima(centro[0], centro[1]), M = c.motor;
  let area = d3.geoArea({ type: "Polygon", coordinates: [[...poly, poly[0]].reverse()] }) * 6371008.8 ** 2 / 1e4;
  if (area > 5e6) area = d3.geoArea({ type: "Polygon", coordinates: [[...poly, poly[0]]] }) * 6371008.8 ** 2 / 1e4;
  const mun = PK.malha.features.find((f) => d3.geoContains(f, centro));
  const rel = relevoNaArea(poly);
  const L = 3, gdd = P.gdd;
  const curva = curvaDiaria(c, L, gdd);
  const limite = M.limite_2m.por_ciclo[String(gdd)] || null;
  let riscoLim = null;
  if (limite && gdd === 1250) riscoLim = M.limite_2m.risco_no_limite;
  else if (limite) { const [d, m] = limite.split("/").map(Number); const r = chanceIC(c, m, d, L, gdd); riscoLim = r && { em10: r.v, ic95: r.ic }; }
  const dt2 = P.data2 ? new Date(Date.UTC(2001, 0, P.data2)) : null;
  const ch2 = dt2 ? chanceIC(c, dt2.getUTCMonth() + 1, dt2.getUTCDate(), L, gdd) : null;
  const tarde = chanceIC(c, 2, 11, L, gdd);
  const jan = M.janela_safra;
  const linhaV = jan.linhas.find((l) => l.d === "01/" + String(P.mesV).padStart(2, "0"));
  const ago = jan.linhas.find((l) => l.d === "01/08");
  const seguro = jan.seguro ? jan.linhas.find((l) => l.d === jan.seguro) : null;
  const cl = clima(c);
  const topEros = cl.fournier.map((v, m) => ({ m, v })).sort((a, b) => b.v - a.v).slice(0, 3).map((x) => x.m);
  return { P, c, M, area, mun: mun ? mun.properties.nome : "fora do Oeste", rel, curva, limite, riscoLim, ch2, tarde, jan, linhaV, ago, seguro,
    cl, topEros, L, gdd, dt2, seco: M.seco, solo: P.solo };
}

''')

# ---------- riscos, cenários e mensagem (spec v2) ----------
troca_bloco('const SORGO = ', '// ---------- gráficos dos dados NASA ----------', r'''// Mistura no talhão raso: números do motor (mistura_talhao, CAD 39 mm) e da validação V3 (spec v2, E3)
const MIS = { s: 7, sobrevive: 67.4, p10: 46.9, ic: [31.1, 60.8], gradeMed: 15.4, gradeFaixa: [-7.4, 76.3], media: 8.0, mediaIc: [5.4, 11.3] };
// Níveis de evidência da spec v2 (nenhum módulo é N3 hoje)
const EV = { N2: ["n2", "N2 · com ressalva"], N1: ["n1", "N1 · em teste"], MED: ["med", "medido"], CONF: ["n1", "confirme"] };
const evChip = (k) => `<span class="ev ${EV[k][0]}">${EV[k][1]}</span>`;
const celTxt = (A) => `célula ${fmt(A.c.lat, 2)}; ${fmt(A.c.lon, 3)}`;

function riscos(A) {
  const R = [], P = A.P, M = A.M, lp = M.limite_2m.por_limiar, lc = M.limite_2m.por_ciclo;
  if (P.cult.includes("milho2")) {
    const rl = A.riscoLim, sua = A.ch2;
    R.push({ id: "geada2", t: "Geada no 2º milho", ev: "N2", num: A.limite ? "até " + dataExt(A.limite) : "sem data segura",
      dado: A.limite
        ? `Plante até <b>${dataExt(A.limite)}</b>. Nesse dia, a geada chegou antes do corte da silagem em ${em10txt(rl && rl.em10)}${faixaTxt(rl && rl.ic95)}.` +
          (sua ? ` Na sua data (${ddmm(P.data2)}): ${em10txt(sua.v)}${faixaTxt(sua.ic)}.` : "") +
          ` Em 11 de fevereiro: ${em10txt(A.tarde && A.tarde.v)}${faixaTxt(A.tarde && A.tarde.ic)}.`
        : "Aqui, com este ciclo, o 2º milho quase nunca chega ao corte da silagem antes da geada.",
      fazer: [A.limite ? `Plantar até ${dataExt(A.limite)}.` : "Ir de aveia ou azevém no inverno.", "Se a colheita do verão atrasar, trocar por aveia ou azevém.", "Semente de ciclo longo (que demora mais): plantar antes."],
      limite: `A data-limite muda com o limiar de geada (${lp["4"] || "–"} a ${lp["2"] || "–"}) e com o ciclo da semente (${lc["1400"] || "–"} a ${lc["1100"] || "–"}), e muda de um município para outro. É a chance de geada, não de perder a silagem. A falta de água do 2º milho não foi calculada.`,
      rastro: `NASA POWER T2M_MIN e T2M_MAX, ${ANO0}–${ANO1}, ${celTxt(A)}. Geada = mínima ≤ 3 °C entre o plantio e ${A.gdd} °C·dia (validação V2; motor geada_limite_2a_safra).` });
  }
  if (P.cult.includes("milhoV") && A.linhaV && A.ago) {
    const sg = A.seguro;
    R.push({ id: "geadaV", t: "Geada no milho de verão", ev: "N2", num: em10curto(A.linhaV.em10),
      dado: `Aqui, não plante em agosto. Plantando em 1º de agosto, a geada pegou a lavoura nova em ${em10txt(A.ago.em10)}${faixaTxt(A.ago.ic95)}.` +
        (sg ? ` A partir de ${dataExt(sg.d)}, ${em10txt(sg.em10)}.` : "") +
        ` Na sua data (1º de ${MESES_EXT[P.mesV - 1]}): ${em10txt(A.linhaV.em10)}${faixaTxt(A.linhaV.ic95)}. Do fim de setembro a dezembro, para o clima, a data quase não muda o risco.`,
      fazer: P.mesV === 8 ? ["Esperar setembro para plantar.", "Do fim de setembro a dezembro, escolher a data pela mão de obra e pelo pasto."] : ["Manter a data: fora de agosto, a geada quase não muda com a data."],
      limite: "A forma bate com o ZARC (40% de risco em agosto); a força não: o dado da NASA mostra mais geada que o ZARC. O limiar de 2 °C vem do ZARC e não foi calibrado.",
      rastro: `NASA POWER T2M_MIN, plantios de ${A.jan.periodo}, ${celTxt(A)}. Geada = algum dia com mínima < 2 °C nos primeiros ${A.jan.dias} dias da lavoura (validação V4; motor geada_janela_safra).` });
  }
  if (P.cult.includes("milhoV") || P.ativ !== "graos") {
    const al = A.seco.alertas.map((a) => a.ano), n = Object.keys(A.seco.serie).length;
    R.push({ id: "seco", t: "Aviso de ano seco no milho", ev: "N2", num: al.length + " em " + n + " safras",
      dado: `O aviso dispara quando a água para o milho, de 20 de setembro a 10 de janeiro, fica entre os 10% piores dos anos anteriores aqui. Ele teria disparado nas safras de <b>${al.join(", ") || "nenhum ano"}</b>. Não é certeza, e o aviso não pega todos os anos ruins.`,
      fazer: ["Quando o aviso disparar: conferir o estoque de silagem e falar com o técnico.", P.solo === "raso" ? "No talhão raso, metade da silagem em sorgo (veja “E se…?”)." : "Confirmar o solo dos talhões de morro: se for raso, o sorgo pode ajudar.", "Manter pastagem perene para os meses críticos."],
      limite: "Silêncio não quer dizer ano seguro: nos testes, o aviso deixou passar cerca de metade dos anos ruins. Só na auditoria (usa o IBGE PAM, não vai ao agricultor): 13 de 29 avisos caíram em ano de quebra (45%), contra 16% num ano qualquer.",
      rastro: `NASA POWER (chuva, temperatura, umidade, vento, radiação) → evapotranspiração FAO-56 → balanço de água do milho, ${celTxt(A)}. Percentil só com os anos anteriores, desde 1990 (validação V1; motor ano_extremo_seco).` });
  }
  if (P.solo === "raso") R.push({ id: "mistura", t: "Talhão raso: sorgo na silagem", ev: "N2", num: MIS.s + " em 10 cenários",
    dado: `Você disse que o talhão é raso. Plantar metade da silagem com sorgo ajudou o ano ruim (o pior de cada 10) em ${MIS.s} de cada 10 cenários testados. A conta não é firme. Em ano bom, a mistura pode render um pouco menos.`,
    fazer: ["Testar numa faixa do talhão antes de mudar tudo.", "Fale com o técnico antes de decidir."],
    limite: `Só na auditoria: pior ano em 10 com ${fmt(MIS.p10)}% a mais (entre ${fmt(MIS.ic[0])}% e ${fmt(MIS.ic[1])}%), ano normal com ${fmt(MIS.media)}% a mais (entre ${fmt(MIS.mediaIc[0])}% e ${fmt(MIS.mediaIc[1])}%). O ganho some se o sorgo sofrer com a falta de água 1,5 vez mais do que a FAO supõe. Não há dado de produtividade de sorgo na região.`,
    rastro: "Balanço de água com o NASA POWER, solo raso de ~39 mm (água por textura do GAEZ), parâmetros FAO e Embrapa (R = 0,88). Validação V3; motor mistura_talhao." });
  else if (P.solo === "medio") R.push({ id: "mistura", t: "Sorgo na silagem", ev: "N1", num: "sem número",
    dado: "Neste solo médio, a conta do sorgo ainda está em teste. Por enquanto não temos um número confiável para o seu lugar.",
    fazer: ["Fale com o técnico antes de decidir."], limite: "Solo de 55 a 90 mm de água: a mistura é N1 na spec v2.", rastro: "Validação V3; motor mistura_talhao (desligado fora do raso)." });
  else if (P.solo === "auto" && A.rel && A.rel.morro >= 15) R.push({ id: "solo", t: "Confirme o solo dos morros", ev: "CONF", num: fmt(A.rel.morro, 0) + "% de morro",
    dado: `Pelo relevo do satélite, ${fmt(A.rel.morro, 0)}% da área tem declive acima de 20%, onde o solo costuma ser raso. O satélite não mede a profundidade do solo. Como é a terra lá? Marque em “Solo que você vê”.`,
    fazer: ["Andar no talhão e ver se há pedra ou rocha perto da superfície.", "Se for raso, marcar “raso ou com pedra” para ver a conta do sorgo."],
    limite: "O SRTM só pede para confirmar: ele erra o solo raso de topo de morro.", rastro: "SRTM 1″ (NASA/USGS) reamostrado a ~90 m; classes de relevo da Embrapa." });
  const semCobertura = !P.cult.includes("aveia");
  R.push({ id: "erosao", t: "Chuva que arrasta solo", ev: "MED", num: A.topEros.map((m) => MESES[m]).join(", "),
    dado: `Os meses de chuva mais erosiva aqui são ${A.topEros.map((m) => MESES_EXT[m]).join(", ")}. ${semCobertura ? "Sem planta no inverno, o solo chega descoberto a esses meses." : "A aveia ou o azevém no inverno cobrem o solo."}${A.rel ? " " + fmt(A.rel.morro, 0) + "% da área é morro." : ""}`,
    fazer: ["Semear aveia ou azevém logo depois da colheita.", "Plantar direto sobre a palha.", "Terraço ou cordão em nível nos talhões com mais de 20% de declive."],
    limite: "Quanto solo a cobertura salva, não medimos. A erosividade mensal do POWER bateu com o pluviômetro da ANA (correlação 0,85), mas o teste foi feito em Ituporanga.",
    rastro: "NASA POWER PRECTOTCORR; índice de Fournier = chuva do mês² ÷ chuva do ano, média dos anos (validação A3-1)." });
  return R;
}

function desenhaRiscos(A) {
  const R = riscos(A); A.R = R;
  $("celTag").textContent = "POWER " + fmt(A.c.lat, 2) + "; " + fmt(A.c.lon, 3);
  $("risks").innerHTML = R.map((r, i) => `<details class="risk" ${i < 2 ? "open" : ""}><summary>${evChip(r.ev)}<h3>${r.t}</h3><span class="num mono">${r.num}</span></summary>
    <div class="rbody"><p><b>O dado da NASA diz:</b> ${r.dado}</p><div><b>O que fazer</b><ul>${r.fazer.map((f) => "<li>" + f + "</li>").join("")}</ul></div>
    <div class="conf"><b>O que não sabemos</b><span>${r.limite}</span></div><p class="rastro">${r.rastro}</p></div></details>`).join("") || '<p class="small">Marque o que você planta para ver os riscos.</p>';
}

const NAO_COMPARA = '<p class="small" style="margin:0">Os números das opções medem coisas diferentes (chance de geada, cenários que ajudam) e não formam um ranking.</p>';
function desenhaCenario(A) {
  const P = A.P, el = $("scen");
  document.querySelectorAll("#scenBtns button").forEach((b) => b.classList.toggle("on", b.dataset.s === S.scen));
  if (S.scen === "milho2") {
    const doy = S.data2, dt = new Date(Date.UTC(2001, 0, doy)), r = chanceIC(A.c, dt.getUTCMonth() + 1, dt.getUTCDate(), A.L, A.gdd), rl = A.riscoLim;
    const smo = A.mun === "São Miguel do Oeste";
    el.innerHTML = `<div class="ctrl"><label for="r2">Plantar o 2º milho em <b class="mono" id="r2o">${ddmm(doy)}</b></label><input type="range" id="r2" min="1" max="85" step="1" value="${doy}"></div>
      <div class="bigline">${evChip("N2")}<b class="mono" style="color:${r && r.v >= 3 ? "var(--alto)" : r && r.v >= 1 ? "var(--medio)" : "var(--baixo)"}">${r ? em10curto(r.v) : "–"}</b><span>com geada antes do corte da silagem${r ? faixaTxt(r.ic) : ""}. Data-limite aqui: <b>${A.limite ? dataExt(A.limite) : "sem data segura"}</b>.</span></div>
      <div class="tradewrap"><table class="trade"><thead><tr><th>Caminho</th><th>Ganha</th><th>Arrisca</th><th>Número</th></tr></thead><tbody>
      <tr><td><b>O de sempre</b><br><span class="small">milho de verão e pasto de inverno</span></td><td>Rotina conhecida.</td><td>—</td><td class="small">sem número (ponto de partida)</td></tr>
      <tr><td><b>2º milho em ${ddmm(doy)}</b></td><td>Mais silagem no inverno.</td><td>Geada antes do corte; semente e adubo.</td><td class="mono">${r ? em10curto(r.v) + faixaTxt(r.ic) : "–"}</td></tr>
      <tr><td><b>2º milho até ${A.limite ? dataExt(A.limite) : "–"}</b></td><td>Silagem com geada rara.</td><td>Depende de colher o verão a tempo.</td><td class="mono">${rl ? em10curto(rl.em10) + faixaTxt(rl.ic95) : "–"}</td></tr>
      <tr><td><b>Aveia ou azevém</b> ${evChip("N1")}</td><td>Pasto no inverno, solo coberto.</td><td>Menos volume que o milho.</td><td class="small">não calculada</td></tr>
      <tr><td><b>Sorgo depois do milho</b> ${evChip("N1")}</td><td>—</td><td>—</td><td class="small">em teste${smo ? "; o ZARC indica até 1º de março aqui" : ""}</td></tr></tbody></table></div>
      <p class="small" style="margin:0">Chance de geada antes do corte (mínima ≤ 3 °C no NASA POWER, ${A.gdd} °C·dia, ${ANO0}–${ANO1}), não de perder a silagem. A falta de água do 2º milho não foi calculada.</p>${NAO_COMPARA}`;
    $("r2").addEventListener("input", (e) => { S.data2 = +e.target.value; desenhaCenario(A); $("r2").focus(); });
  } else if (S.scen === "sorgo") {
    if (P.solo === "raso") el.innerHTML = `<div class="bigline">${evChip("N2")}<b class="mono" style="color:var(--baixo)">${MIS.s} em 10</b><span>cenários testados em que metade da silagem em sorgo ajudou o ano ruim, no talhão que você disse ser raso.</span></div>
      <div class="tradewrap"><table class="trade"><thead><tr><th>Caminho</th><th>Ganha</th><th>Arrisca</th></tr></thead><tbody>
      <tr><td><b>Só milho</b></td><td>Mais energia por tonelada.</td><td>No ano seco, quebra maior no solo raso.</td></tr>
      <tr><td><b>Metade sorgo</b></td><td>Segura a comida no ano ruim.</td><td>Silagem de sorgo vale cerca de 85% a 90% da de milho (Embrapa). Em ano bom, pode render um pouco menos.</td></tr></tbody></table></div>
      <div class="conf"><b>O que não sabemos</b><span>A conta não é firme: o ganho some se o sorgo sofrer mais com a falta de água do que a FAO supõe, e não há dado de produtividade de sorgo na região. Auditoria: pior ano em 10 com ${fmt(MIS.p10)}% a mais (entre ${fmt(MIS.ic[0])}% e ${fmt(MIS.ic[1])}%).</span></div>`;
    else if (P.solo === "medio") el.innerHTML = `<p style="margin:0">${evChip("N1")} No solo médio, a conta do sorgo ainda está em teste. Por enquanto não temos um número confiável para o seu lugar.</p>`;
    else if (P.solo === "fundo") el.innerHTML = `<p style="margin:0">No solo fundo, o milho rende mais e o sorgo não ajuda o ano ruim. O módulo fica desligado.</p>`;
    else el.innerHTML = `<p style="margin:0">${evChip("CONF")} Para calcular, preciso saber como é a terra do talhão. Marque em “Solo que você vê”: raso ou com pedra, médio ou fundo.${A.rel ? " Pelo relevo, " + fmt(A.rel.morro, 0) + "% da área parece morro." : ""}</p>`;
  } else if (S.scen === "dataV") {
    const ls = A.jan.linhas, set = ls.filter((l) => ["21/09", "01/10", "11/10", "21/10", "01/11", "11/11", "21/11", "01/12", "11/12", "21/12"].includes(l.d));
    const dif = set.length ? Math.max(...set.map((l) => l.em10)) - Math.min(...set.map((l) => l.em10)) : null;
    el.innerHTML = `<div class="tradewrap"><table class="trade"><thead><tr><th>Plantar em</th><th>Geada na lavoura nova ${evChip("N2")}</th></tr></thead><tbody>${ls.map((l) => `<tr><td><b>${dataExt(l.d)}</b>${l.d === "01/" + String(P.mesV).padStart(2, "0") ? " (hoje)" : ""}</td><td class="mono">${em10curto(l.em10)}${faixaTxt(l.ic95)}</td></tr>`).join("")}</tbody></table></div>
      <p style="margin:0">${dif !== null && dif < 1 ? "Entre o fim de setembro e dezembro, para o clima, a data de plantio quase não muda o risco: a diferença é menor que 1 ano em 10. Escolha pela mão de obra e pela máquina." : "Fora de agosto, a geada cai rápido."}</p>
      <p class="small" style="margin:0">Geada = algum dia com mínima < 2 °C nos primeiros ${A.jan.dias} dias da lavoura (NASA POWER, plantios de ${A.jan.periodo}). A forma bate com o ZARC; a força é maior que a do ZARC.</p>`;
  } else {
    const f = A.cl.fournier, mx = Math.max(...f);
    el.innerHTML = `<p style="margin:0">${evChip("MED")} Quanto a chuva de cada mês pode arrastar solo aqui (índice de Fournier com a chuva do NASA POWER, média ${ANO0}–${ANO1}):</p>
      <div>${f.map((v, m) => `<div style="display:grid;grid-template-columns:36px minmax(0,1fr) 40px;gap:8px;align-items:center;font-size:12.5px"><span class="mono">${MESES[m]}</span><span style="height:10px;border-radius:4px;background:${A.topEros.includes(m) ? "var(--alto)" : "var(--line)"};width:${100 * v / mx}%"></span><span class="mono">${Math.round(v)}</span></div>`).join("")}</div>
      <div class="tradewrap"><table class="trade"><thead><tr><th>Caminho</th><th>Ganha</th><th>Arrisca</th></tr></thead><tbody>
      <tr><td><b>Solo nu no inverno</b></td><td>Não gasta com semente.</td><td>Chega descoberto a ${A.topEros.map((m) => MESES_EXT[m]).join(", ")}${A.rel ? ", com " + fmt(A.rel.morro, 0) + "% da área em morro" : ""}.</td></tr>
      <tr><td><b>Aveia ou azevém</b> ${evChip("N1")}</td><td>Solo coberto, pasto no inverno, palha para o plantio direto.</td><td>Custo de semente.</td></tr></tbody></table></div>
      <div class="conf"><b>O que não sabemos</b><span>Quanto solo a cobertura salva, não medimos. A erosividade do POWER bateu com o pluviômetro da ANA (testado em Ituporanga).</span></div>`;
  }
}

// Mensagem do agricultor no formato do template T01 da spec v2 (até 70 palavras, sempre anos ruins)
function mensagem(A) {
  const P = A.P, caminhos = [];
  caminhos.push("O de sempre, milho de verão e pasto de inverno: sem número");
  if (A.limite) { const rl = A.riscoLim; caminhos.push(`Segundo milho: plantando até ${dataExt(A.limite)}, a geada chega antes do corte em ${em10txt(rl && rl.em10)}${faixaTxt(rl && rl.ic95)}; não calculamos a falta de água`); }
  if (P.solo === "raso") caminhos.push(`Metade da silagem em sorgo no talhão raso: ajudou em ${MIS.s} de cada 10 cenários testados`);
  const qt = ["", "Um", "Dois", "Três", "Quatro"][caminhos.length + 1] || String(caminhos.length + 1);
  let txt = `${qt} caminhos para a sua fazenda em ${A.mun}. ${caminhos.join(". ")}. Em teste: sorgo depois do milho.`;
  const extra = [" Dados de satélite, área de 55 km.", " Fale com o técnico antes de decidir."];
  for (const e of extra) if ((txt + e).split(/\s+/).length <= 70) txt += e;
  if (P.solo === "auto" && A.rel && A.rel.morro >= 15) { const p = " Como é a terra dos morros: rasa, média ou funda?"; if ((txt + p).split(/\s+/).length <= 70) txt += p; }
  return txt;
}

''')

# ---------- camada de geada no mapa e dica: data-limite do motor ----------
troca('const vals = CEL.map((c) => { if (S.layer === "geada") { const cv = curvaDiaria(c, 3, A ? A.gdd : 1250); return { c, v: cv.limite || 90, t: cv.limite ? ddmm(cv.limite) : ">31 mar" }; }',
      'const vals = CEL.map((c) => { if (S.layer === "geada") { const l = c.motor.limite_2m.por_ciclo[String(A ? A.gdd : 1250)]; return { c, v: l ? ddmmDoy(l) : 90, t: l ? ddmm(ddmmDoy(l)) : "sem data" }; }')
troca('if (S.layer === "geada") { const cv = curvaDiaria(c, 3, S.A ? S.A.gdd : 1250); extra = "2º milho até " + (cv.limite ? ddmm(cv.limite) : "31 mar"); }',
      'if (S.layer === "geada") { const l = c.motor.limite_2m.por_ciclo[String(S.A ? S.A.gdd : 1250)]; extra = "2º milho até " + (l ? dataExt(l) : "sem data segura"); }')
troca('Número: última data para plantar o 2º milho com até 2 anos em 10 de geada antes da silagem. Mais escuro: data mais cedo.',
      'Número: data-limite do 2º milho (até 2 anos em 10 com geada antes do corte, média de 5 dias; motor da spec v2). Mais escuro: data mais cedo. Evidência N2.')

# ---------- gráfico B: data-limite e faixa do motor ----------
troca('''  if (c.limite) { s.append("line").attr("x1", x(c.limite)).attr("x2", x(c.limite))''',
      '''  const lp = A.M.limite_2m.por_limiar; if (lp["4"] && lp["2"]) s.insert("rect", ":first-child").attr("x", x(ddmmDoy(lp["4"]))).attr("y", m.t).attr("width", Math.max(1, x(ddmmDoy(lp["2"])) - x(ddmmDoy(lp["4"])))).attr("height", H - m.b - m.t).attr("fill", "var(--alto-soft)");
  if (A.limite) c.limite = ddmmDoy(A.limite);
  if (c.limite) { s.append("line").attr("x1", x(c.limite)).attr("x2", x(c.limite))''')
troca('$("capB").textContent = `Anos em 10 com geada antes do ponto de silagem (${A.gdd} °C·dia), 1984–2025. Ponto amarelo: a sua data.`;',
      '$("capB").textContent = `Anos em 10 com geada antes do corte da silagem (${A.gdd} °C·dia), ${ANO0}–${ANO1}. Faixa vermelha: data-limite com limiar de 4 a 2 °C. Ponto amarelo: a sua data.`;')
troca('Tracejado: mediana 1984–2025.`;', 'Tracejado: mediana ${ANO0}–${ANO1}.`;')

# ---------- textos fixos ----------
troca('<p>Oeste de Santa Catarina · dados NASA POWER (1984–2025) e SRTM</p>', '<p>Oeste de Santa Catarina · dados NASA POWER (1981–2025) e SRTM</p>')
troca('const partes = [`Olá. Olhei 42 anos', 'const partes = [`Olá. Olhei 45 anos') if 'Olhei 42 anos' in s else None
troca('''    <span><b>Dados da solução:</b> NASA POWER diário (temperatura mínima e máxima, chuva), comunidade AG, grade de ~0,5° × 0,625° (cerca de 55 × 60 km), 1984–2025; SRTM 1″ (NASA/USGS) reamostrado a ~90 m. Contorno dos municípios: IBGE, só para desenho.</span>''',
      '''    <span><b>Dados da solução:</b> NASA POWER diário (temperatura, chuva, umidade, vento e radiação), comunidade AG, grade de ~0,5° × 0,625° (cerca de 55 × 60 km), 1981–2025; SRTM 1″ (NASA/USGS) reamostrado a ~90 m. Contorno dos municípios: IBGE, só para desenho. Três parâmetros vêm de literatura externa (R = 0,88; raiz de 0,6 m; limiar de 2 °C do ZARC).</span>
    <span><b>Níveis de evidência (spec v2):</b> N2 · com ressalva = passou em parte e a direção bate com fonte externa; sai com faixa. N1 · em teste = sem número para o agricultor. Medido = fato do dado, sem previsão. Nenhum módulo é N3 (validado) hoje.</span>''')
troca('''    <span><b>Como foi validado:</b> geada conferida com eventos de estação e com o ZARC (validação parcial); sorgo no solo raso sobrevive em 56% a 68,5% dos cenários de parâmetros; tirar agosto da janela do milho bate com o ZARC; erosividade mensal pelo POWER bate com pluviômetro da ANA (testado em Ituporanga). Prever se o próximo verão será seco não funcionou bem: mostramos os anos secos do passado, não uma previsão.</span>''',
      '''    <span><b>Como foi validado:</b> data-limite do 2º milho (V2: geadas de estação aparecem no dado; muda até 29 dias entre municípios); geada tirando agosto do milho de verão (V4: a forma bate com o ZARC, a força não); aviso de ano seco (V1: 13 de 29 avisos em ano de quebra, mas deixa passar cerca de metade); sorgo no raso (V3: ajuda em 7 de 10 cenários, abaixo do corte de 7 em 10 que pedimos); erosividade (A3-1, em Ituporanga). Nada foi testado com agricultor.</span>''')

# ---------- pergunta ao Claude: fatos com nível de evidência e regras da spec ----------
troca_bloco('function fatos(A) {', '$("bAsk").onclick', r'''function fatos(A) {
  return { local: A.mun + ", SC", area_ha: Math.round(A.area * 10) / 10, perfil: A.P, morro_pct_pelo_relevo: A.rel ? Math.round(A.rel.morro) : null,
    riscos: (A.R || []).map((r) => ({ risco: r.t, nivel_evidencia: r.ev, numero: r.num, dado: r.dado.replace(/<[^>]+>/g, ""), o_que_fazer: r.fazer, o_que_nao_sabemos: r.limite })),
    segundo_milho: { data_limite: A.limite, risco_no_limite_em10: A.riscoLim, na_data_do_produtor: A.ch2 && { em10: A.ch2.v, ic95: A.ch2.ic }, em_11_fev: A.tarde && { em10: A.tarde.v, ic95: A.tarde.ic } },
    milho_verao_geada_por_data: A.jan.linhas, aviso_ano_seco_safras: A.seco.alertas.map((a) => a.ano),
    sorgo_no_raso: A.P.solo === "raso" ? { cenarios_que_ajudam_em10: MIS.s } : "só calculado se o produtor declarar solo raso",
    meses_mais_erosivos: A.topEros.map((m) => MESES_EXT[m]),
    fonte: "NASA POWER diário 1981–2025 (grade ~55 km) e SRTM ~90 m; regras e números do motor da spec v2" };
}
''')
troca_bloco('  const prompt = `', '  try { const r = await sample(', r'''  const prompt = `Você é um extensionista rural do Oeste de Santa Catarina falando com um agricultor familiar com pouca leitura técnica.
Responda em português do Brasil, frases curtas, no máximo 150 palavras.
Regras (spec v2 do projeto):
- Use SOMENTE os números dos FATOS. Não invente número nem faça conta nova.
- Comece pela resposta curta à pergunta. Depois: o que ganha e o que arrisca em cada opção; riscos e o que fazer; o que não sabemos.
- Fale sempre de anos ruins: "em cerca de X de cada 10 anos (entre A e B)". Arredonde para inteiro. Sem porcentagem de modelo.
- Item com nivel_evidencia N1 ou "em teste": diga só que está em teste, sem número.
- Não diga: que é validado ou garantido; que o risco de geada é perder a silagem; que a ferramenta prevê o clima da safra; que se não houver aviso o ano é seguro; que o satélite mede o solo; ganho em dinheiro.
- Praga, doença, adubo ou preço: diga que a ferramenta não calcula isso e indique o técnico.

FATOS (JSON):
${JSON.stringify(fatos(S.A))}

PERGUNTA DO AGRICULTOR: ${q}`;
''')

# ---------- CSS dos selos ----------
troca('.risk h3{font-size:15.5px}', '''.risk h3{font-size:15.5px}
.ev{font:600 10.5px var(--mono);letter-spacing:.03em;padding:4px 8px;border-radius:7px;white-space:nowrap;display:inline-block}
.ev.n2{background:var(--medio-soft);color:var(--medio)}.ev.n1{background:var(--surface-2);color:var(--ink-2);border:1px dashed var(--line)}.ev.med{background:var(--geada-soft);color:var(--geada)}
.rastro{font:400 11.5px/1.45 var(--mono);color:var(--ink-2);border-top:1px dashed var(--line);padding-top:8px}''')
troca('<option value="auto">não sei (estimar pelo relevo)</option>', '<option value="auto">não sei</option>')

P.write_text(s, encoding="utf-8")
print("app.html alinhado à spec v2")
