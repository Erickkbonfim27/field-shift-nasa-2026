// Análise de uma fazenda: riscos com nível de evidência, números para os cenários e a mensagem do agricultor.
// Regras e textos seguem a spec v2 (solucao/spec-v2.md) e o app estático harvesty/src/app.html.
import * as d3 from "d3";
import { celulaMaisProxima, municipioEm, dados } from "./dados";
import { chanceIC, curvaDiaria, clima, ANO_FIM } from "./modelo";
import { relevoNaArea } from "./relevo";
import { em10txt, em10curto, faixaTxt, dataExt, ddmm, fmt, MESES, MESES_EXT } from "@/lib/formato";
import { PERFIL_PADRAO, type Analise, type Perfil, type Poligono, type Risco, type Cultura, type Prioridade } from "@/lib/tipos";

import { MIS } from "@/lib/constantes";

const CULTURAS: Cultura[] = ["milhoV", "milho2", "soja", "aveia", "sorgo", "perene"];
const PRIORIDADES: Prioridade[] = ["comida", "custo", "solo", "renda"];

/** Valida o polígono vindo do navegador: 3 a 200 pontos dentro de uma caixa larga em volta de SC. */
export function validarPoligono(x: unknown): Poligono | null {
  if (!Array.isArray(x) || x.length < 3 || x.length > 200) return null;
  const pts: Poligono = [];
  for (const p of x) {
    if (!Array.isArray(p) || p.length !== 2) return null;
    const [lon, lat] = p.map(Number);
    if (!Number.isFinite(lon) || !Number.isFinite(lat) || lon < -58 || lon > -47 || lat < -30 || lat > -24) return null;
    pts.push([lon, lat]);
  }
  return pts;
}

/** Normaliza o perfil: qualquer campo inválido volta ao padrão. */
export function validarPerfil(x: unknown): Perfil {
  const p = (x && typeof x === "object" ? x : {}) as Record<string, unknown>;
  const num = (v: unknown, d: number) => (Number.isFinite(Number(v)) ? Number(v) : d);
  const gdd = num(p.gdd, 1250);
  return {
    ativ: (["leite", "graos", "ambos"] as const).includes(p.ativ as never) ? (p.ativ as Perfil["ativ"]) : PERFIL_PADRAO.ativ,
    vacas: Math.max(0, Math.min(5000, Math.round(num(p.vacas, PERFIL_PADRAO.vacas)))),
    cult: Array.isArray(p.cult) ? (p.cult.filter((c) => CULTURAS.includes(c as Cultura)) as Cultura[]) : PERFIL_PADRAO.cult,
    mesV: Math.max(8, Math.min(12, Math.round(num(p.mesV, 9)))),
    data2: Math.max(0, Math.min(85, Math.round(num(p.data2, 31)))),
    gdd: (gdd === 1100 || gdd === 1400 ? gdd : 1250) as Perfil["gdd"],
    solo: (["auto", "raso", "medio", "fundo"] as const).includes(p.solo as never) ? (p.solo as Perfil["solo"]) : "auto",
    pri: Array.isArray(p.pri) ? (p.pri.filter((c) => PRIORIDADES.includes(c as Prioridade)).slice(0, 2) as Prioridade[]) : PERFIL_PADRAO.pri,
  };
}

function areaHa(poly: Poligono): number {
  const R2 = 6371008.8 ** 2 / 1e4;
  let a = d3.geoArea({ type: "Polygon", coordinates: [[...poly, poly[0]].reverse()] }) * R2;
  if (a > 5e6) a = d3.geoArea({ type: "Polygon", coordinates: [[...poly, poly[0]]] }) * R2;
  return a;
}

export function analisar(poly: Poligono, P: Perfil): Analise {
  const centro = d3.polygonCentroid(poly) as [number, number];
  const c = celulaMaisProxima(centro[0], centro[1]), M = c.motor;
  const L = 3, gdd = P.gdd;
  const curva = curvaDiaria(c, L, gdd);
  const limite = M.limite_2m.por_ciclo[String(gdd)] ?? null;
  let riscoLim: Analise["riscoLim"] = null;
  if (limite && gdd === 1250 && M.limite_2m.risco_no_limite) riscoLim = { em10: M.limite_2m.risco_no_limite.em10, ic95: M.limite_2m.risco_no_limite.ic95 };
  else if (limite) { const [d, m] = limite.split("/").map(Number); const r = chanceIC(c, m, d, L, gdd); riscoLim = r && { em10: r.v, ic95: r.ic }; }
  const dt2 = P.data2 ? new Date(Date.UTC(2001, 0, P.data2)) : null;
  const r2 = dt2 ? chanceIC(c, dt2.getUTCMonth() + 1, dt2.getUTCDate(), L, gdd) : null;
  const rt = chanceIC(c, 2, 11, L, gdd);
  const cl = clima(c);
  const topEros = cl.fournier.map((v, m) => ({ m, v })).sort((a, b) => b.v - a.v).slice(0, 3).map((x) => x.m);
  const rel = relevoNaArea(poly);
  const A: Analise = {
    area: areaHa(poly),
    mun: municipioEm(centro[0], centro[1]) ?? "fora do Oeste",
    celula: { id: c.id, lat: c.lat, lon: c.lon, elev: c.elev, api: c.api },
    relevo: rel,
    perfil: P,
    limite,
    limitePorLimiar: M.limite_2m.por_limiar,
    limitePorCiclo: M.limite_2m.por_ciclo,
    riscoLim,
    ch2: r2 && { v: r2.v, ic: r2.ic },
    tarde: rt && { v: rt.v, ic: rt.ic },
    janela: { linhas: M.janela_safra.linhas, dias: M.janela_safra.dias, periodo: M.janela_safra.periodo, seguro: M.janela_safra.seguro },
    seco: { alertas: M.seco.alertas.map((a) => a.ano), nSafras: Object.keys(M.seco.serie).length },
    fournier: cl.fournier,
    topEros,
    curva2: curva,
    riscos: [],
    mensagem: "",
    periodo: { ini: dados().anoIni, fim: ANO_FIM },
  };
  A.riscos = riscos(A);
  A.mensagem = mensagem(A);
  return A;
}

const celTxt = (A: Analise) => `célula ${fmt(A.celula.lat, 2)}; ${fmt(A.celula.lon, 3)}`;

function riscos(A: Analise): Risco[] {
  const R: Risco[] = [], P = A.perfil, lp = A.limitePorLimiar, lc = A.limitePorCiclo, { ini, fim } = A.periodo;
  if (P.cult.includes("milho2")) {
    const rl = A.riscoLim, sua = A.ch2;
    R.push({
      id: "geada2", t: "Geada no 2º milho", ev: "N2", num: A.limite ? "até " + dataExt(A.limite) : "sem data segura",
      dado: A.limite
        ? `Plante até <b>${dataExt(A.limite)}</b>. Nesse dia, a geada chegou antes do corte da silagem em ${em10txt(rl?.em10)}${faixaTxt(rl?.ic95)}.` +
          (sua ? ` Na sua data (${ddmm(P.data2)}): ${em10txt(sua.v)}${faixaTxt(sua.ic)}.` : "") +
          ` Em 11 de fevereiro: ${em10txt(A.tarde?.v)}${faixaTxt(A.tarde?.ic)}.`
        : "Aqui, com este ciclo, o 2º milho quase nunca chega ao corte da silagem antes da geada.",
      fazer: [A.limite ? `Plantar até ${dataExt(A.limite)}.` : "Ir de aveia ou azevém no inverno.", "Se a colheita do verão atrasar, trocar por aveia ou azevém.", "Semente de ciclo longo (que demora mais): plantar antes."],
      limite: `A data-limite muda com o limiar de geada (${lp["4"] ?? "–"} a ${lp["2"] ?? "–"}) e com o ciclo da semente (${lc["1400"] ?? "–"} a ${lc["1100"] ?? "–"}), e muda de um município para outro. É a chance de geada, não de perder a silagem. A falta de água do 2º milho não foi calculada.`,
      rastro: `NASA POWER T2M_MIN e T2M_MAX, ${ini}–${fim}, ${celTxt(A)}. Geada = mínima ≤ 3 °C entre o plantio e ${P.gdd} °C·dia (validação V2; motor geada_limite_2a_safra).`,
    });
  }
  const linhaV = A.janela.linhas.find((l) => l.d === "01/" + String(P.mesV).padStart(2, "0"));
  const ago = A.janela.linhas.find((l) => l.d === "01/08");
  if (P.cult.includes("milhoV") && linhaV && ago) {
    const sg = A.janela.seguro ? A.janela.linhas.find((l) => l.d === A.janela.seguro) : null;
    R.push({
      id: "geadaV", t: "Geada no milho de verão", ev: "N2", num: em10curto(linhaV.em10),
      dado: `Aqui, não plante em agosto. Plantando em 1º de agosto, a geada pegou a lavoura nova em ${em10txt(ago.em10)}${faixaTxt(ago.ic95)}.` +
        (sg ? ` A partir de ${dataExt(sg.d)}, ${em10txt(sg.em10)}.` : "") +
        ` Na sua data (1º de ${MESES_EXT[P.mesV - 1]}): ${em10txt(linhaV.em10)}${faixaTxt(linhaV.ic95)}. Do fim de setembro a dezembro, para o clima, a data quase não muda o risco.`,
      fazer: P.mesV === 8 ? ["Esperar setembro para plantar.", "Do fim de setembro a dezembro, escolher a data pela mão de obra e pelo pasto."] : ["Manter a data: fora de agosto, a geada quase não muda com a data."],
      limite: "A forma bate com o ZARC (40% de risco em agosto); a força não: o dado da NASA mostra mais geada que o ZARC. O limiar de 2 °C vem do ZARC e não foi calibrado.",
      rastro: `NASA POWER T2M_MIN, plantios de ${A.janela.periodo}, ${celTxt(A)}. Geada = algum dia com mínima < 2 °C nos primeiros ${A.janela.dias} dias da lavoura (validação V4; motor geada_janela_safra).`,
    });
  }
  if (P.cult.includes("milhoV") || P.ativ !== "graos") {
    const al = A.seco.alertas;
    R.push({
      id: "seco", t: "Aviso de ano seco no milho", ev: "N2", num: `${al.length} em ${A.seco.nSafras} safras`,
      dado: `O aviso dispara quando a água para o milho, de 20 de setembro a 10 de janeiro, fica entre os 10% piores dos anos anteriores aqui. Ele teria disparado nas safras de <b>${al.join(", ") || "nenhum ano"}</b>. Não é certeza, e o aviso não pega todos os anos ruins.`,
      fazer: ["Quando o aviso disparar: conferir o estoque de silagem e falar com o técnico.", P.solo === "raso" ? "No talhão raso, metade da silagem em sorgo (veja “E se…?”)." : "Confirmar o solo dos talhões de morro: se for raso, o sorgo pode ajudar.", "Manter pastagem perene para os meses críticos."],
      limite: "Silêncio não quer dizer ano seguro: nos testes, o aviso deixou passar cerca de metade dos anos ruins. Só na auditoria (usa o IBGE PAM, não vai ao agricultor): 13 de 29 avisos caíram em ano de quebra (45%), contra 16% num ano qualquer.",
      rastro: `NASA POWER (chuva, temperatura, umidade, vento, radiação) → evapotranspiração FAO-56 → balanço de água do milho, ${celTxt(A)}. Percentil só com os anos anteriores, desde 1990 (validação V1; motor ano_extremo_seco).`,
    });
  }
  if (P.solo === "raso") R.push({
    id: "mistura", t: "Talhão raso: sorgo na silagem", ev: "N2", num: `${MIS.s} em 10 cenários`,
    dado: `Você disse que o talhão é raso. Plantar metade da silagem com sorgo ajudou o ano ruim (o pior de cada 10) em ${MIS.s} de cada 10 cenários testados. A conta não é firme. Em ano bom, a mistura pode render um pouco menos.`,
    fazer: ["Testar numa faixa do talhão antes de mudar tudo.", "Fale com o técnico antes de decidir."],
    limite: `Só na auditoria: pior ano em 10 com ${fmt(MIS.p10)}% a mais (entre ${fmt(MIS.ic[0])}% e ${fmt(MIS.ic[1])}%), ano normal com ${fmt(MIS.media)}% a mais (entre ${fmt(MIS.mediaIc[0])}% e ${fmt(MIS.mediaIc[1])}%). O ganho some se o sorgo sofrer com a falta de água 1,5 vez mais do que a FAO supõe. Não há dado de produtividade de sorgo na região.`,
    rastro: "Balanço de água com o NASA POWER, solo raso de ~39 mm (água por textura do GAEZ), parâmetros FAO e Embrapa (R = 0,88). Validação V3; motor mistura_talhao.",
  });
  else if (P.solo === "medio") R.push({
    id: "mistura", t: "Sorgo na silagem", ev: "N1", num: "sem número",
    dado: "Neste solo médio, a conta do sorgo ainda está em teste. Por enquanto não temos um número confiável para o seu lugar.",
    fazer: ["Fale com o técnico antes de decidir."], limite: "Solo de 55 a 90 mm de água: a mistura é N1 na spec v2.", rastro: "Validação V3; motor mistura_talhao (desligado fora do raso).",
  });
  else if (P.solo === "auto" && A.relevo && A.relevo.morro >= 15) R.push({
    id: "solo", t: "Confirme o solo dos morros", ev: "CONF", num: `${fmt(A.relevo.morro, 0)}% de morro`,
    dado: `Pelo relevo do satélite, ${fmt(A.relevo.morro, 0)}% da área tem declive acima de 20%, onde o solo costuma ser raso. O satélite não mede a profundidade do solo. Como é a terra lá? Marque em “Solo que você vê”.`,
    fazer: ["Andar no talhão e ver se há pedra ou rocha perto da superfície.", "Se for raso, marcar “raso ou com pedra” para ver a conta do sorgo."],
    limite: "O SRTM só pede para confirmar: ele erra o solo raso de topo de morro.", rastro: "SRTM 1″ (NASA/USGS) reamostrado a ~90 m; classes de relevo da Embrapa.",
  });
  const semCobertura = !P.cult.includes("aveia");
  R.push({
    id: "erosao", t: "Chuva que arrasta solo", ev: "MED", num: A.topEros.map((m) => MESES[m]).join(", "),
    dado: `Os meses de chuva mais erosiva aqui são ${A.topEros.map((m) => MESES_EXT[m]).join(", ")}. ${semCobertura ? "Sem planta no inverno, o solo chega descoberto a esses meses." : "A aveia ou o azevém no inverno cobrem o solo."}${A.relevo ? ` ${fmt(A.relevo.morro, 0)}% da área é morro.` : ""}`,
    fazer: ["Semear aveia ou azevém logo depois da colheita.", "Plantar direto sobre a palha.", "Terraço ou cordão em nível nos talhões com mais de 20% de declive."],
    limite: "Quanto solo a cobertura salva, não medimos. A erosividade mensal do POWER bateu com o pluviômetro da ANA (correlação 0,85), mas o teste foi feito em Ituporanga.",
    rastro: "NASA POWER PRECTOTCORR; índice de Fournier = chuva do mês² ÷ chuva do ano, média dos anos (validação A3-1).",
  });
  return R;
}

/** Mensagem do agricultor no formato do template T01 da spec v2 (até 70 palavras, sempre anos ruins). */
function mensagem(A: Analise): string {
  const P = A.perfil, caminhos: string[] = ["O de sempre, milho de verão e pasto de inverno: sem número"];
  if (A.limite) caminhos.push(`Segundo milho: plantando até ${dataExt(A.limite)}, a geada chega antes do corte em ${em10txt(A.riscoLim?.em10)}${faixaTxt(A.riscoLim?.ic95)}; não calculamos a falta de água`);
  if (P.solo === "raso") caminhos.push(`Metade da silagem em sorgo no talhão raso: ajudou em ${MIS.s} de cada 10 cenários testados`);
  const qt = ["", "Um", "Dois", "Três", "Quatro"][caminhos.length + 1] ?? String(caminhos.length + 1);
  const palavras = (t: string) => t.split(/\s+/).length;
  let txt = `${qt} caminhos para a sua fazenda em ${A.mun}. ${caminhos.join(". ")}. Em teste: sorgo depois do milho.`;
  if (palavras(txt) > 70) {
    const curtos = caminhos.map((c) => c.replace("O de sempre, milho de verão e pasto de inverno: sem número", "O de sempre: sem número").replace("Metade da silagem em sorgo no talhão raso", "Metade em sorgo no talhão raso"));
    txt = `${qt} caminhos para a sua fazenda. ${curtos.join(". ")}. Em teste: sorgo depois do milho.`;
  }
  for (const e of [" Dados de satélite, área de 55 km.", " Fale com o técnico antes de decidir."]) if (palavras(txt + e) <= 70) txt += e;
  if (P.solo === "auto" && A.relevo && A.relevo.morro >= 15) { const p = " Como é a terra dos morros: rasa, média ou funda?"; if (palavras(txt + p) <= 70) txt += p; }
  return txt;
}

/** Fatos que vão para o Claude na pergunta livre (recalculados no servidor; nunca vêm do navegador). */
export function fatos(A: Analise) {
  return {
    local: `${A.mun}, SC`, area_ha: Math.round(A.area * 10) / 10, perfil: A.perfil,
    morro_pct_pelo_relevo: A.relevo ? Math.round(A.relevo.morro) : null,
    riscos: A.riscos.map((r) => ({ risco: r.t, nivel_evidencia: r.ev, numero: r.num, dado: r.dado.replace(/<[^>]+>/g, ""), o_que_fazer: r.fazer, o_que_nao_sabemos: r.limite })),
    segundo_milho: { data_limite: A.limite, risco_no_limite_em10: A.riscoLim, na_data_do_produtor: A.ch2, em_11_fev: A.tarde },
    milho_verao_geada_por_data: A.janela.linhas, aviso_ano_seco_safras: A.seco.alertas,
    sorgo_no_raso: A.perfil.solo === "raso" ? { cenarios_que_ajudam_em10: MIS.s } : "só calculado se o produtor declarar solo raso",
    meses_mais_erosivos: A.topEros.map((m) => MESES_EXT[m]),
    fonte: `NASA POWER diário ${A.periodo.ini}–${A.periodo.fim} (grade ~55 km) e SRTM ~90 m; regras e números do motor da spec v2`,
  };
}
