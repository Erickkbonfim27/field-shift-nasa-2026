"use strict";
/* Tela principal: WhatsApp simulado (esquerda) e auditoria do técnico (direita).
   A UI só lê o JSON do contrato v2. Não calcula resultado nenhum. */

const ST = {
  local: null, perg: null, dados: null, info: null, rastro: {},
  vista: "zap", aba: "mensagem", cartaoId: null, estId: null, numero: null, mais: false, tts: null
};
const ABAS = [
  ["mensagem", "Mensagem"], ["estrategias", "Estratégias"], ["graficos", "Gráficos"],
  ["validacao", "Validação"], ["limites", "Limites"], ["rastro", "Rastro"], ["glossario", "Glossário"]
];
const $ = (id) => document.getElementById(id);
const ICON_PLAY = '<svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M8 5v14l11-7z"/></svg>';
const ICON_PAUSE = '<svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M7 5h4v14H7zM13 5h4v14h-4z"/></svg>';
const ICON_MIC = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><rect x="9" y="3" width="6" height="12" rx="3"/><path d="M5 11a7 7 0 0 0 14 0M12 18v3"/></svg>';
const ICON_PIN = '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 21s7-6.200 7-11.500A7 7 0 0 0 5 9.500C5 14.800 12 21 12 21z"/><circle cx="12" cy="9.500" r="2.500"/></svg>';

/* ---------- carga ---------- */
async function iniciar() {
  const p = lerParams();
  ST.local = acharLocal(p.local);
  ST.perg = acharPergunta(ST.local, p.pergunta);
  montarSeletores();
  await carregar();
}

async function carregar() {
  $("chat").innerHTML = '<p class="peq">Carregando…</p>';
  try {
    ST.info = await carregarSaida(ST.local.slug);
  } catch (e) {
    $("aviso").innerHTML = `<div class="faixa-erro"><b>Não consegui abrir os dados.</b> ${esc(e.message)}.<br>Abra esta página por um servidor local, na pasta <code>solucao</code>:<br><code>python3 -m http.server 8765</code>, depois <code>http://localhost:8765/ui/index.html</code>.</div>`;
    $("chat").innerHTML = ""; $("audCorpo").innerHTML = "";
    return;
  }
  ST.dados = ST.info.dados;
  ST.rastro = {};
  (ST.dados.rastro || []).forEach((r) => { ST.rastro[r.id] = r; });
  ST.numero = null; ST.mais = false; ST.aba = "mensagem";
  ST.estId = null;
  ST.cartaoId = (cartoesOrdenados().resposta || cartoesWA()[0] || {}).id || null;
  const pr = ST.dados.estrategias.find((e) => e.risco_por_decendio) || ST.dados.estrategias[0];
  ST.estId = pr ? pr.id : null;
  renderTudo();
}

function montarSeletores() {
  $("selLocal").innerHTML = LOCAIS.map((l) => `<option value="${esc(l.slug)}"${l.slug === ST.local.slug ? " selected" : ""}>${esc(l.nome)}</option>`).join("");
  montarPerguntas();
  atualizarUrl();
}
function montarPerguntas() {
  $("selPerg").innerHTML = ST.local.perguntas.map((q) => `<option value="${esc(q.id)}"${q.id === ST.perg.id ? " selected" : ""}>${esc(q.texto)}</option>`).join("");
}
function atualizarUrl() {
  try { history.replaceState(null, "", `?local=${encodeURIComponent(ST.local.slug)}&pergunta=${encodeURIComponent(ST.perg.id)}`); } catch (e) { /* file:// ou sem histórico */ }
}

/* ---------- dados auxiliares ---------- */
function cartoesWA() { return (ST.dados.cartoes || []).filter((c) => c.destino === "whatsapp").sort((a, b) => a.ordem - b.ordem); }
function cartoesOrdenados() {
  const todos = cartoesWA();
  let resposta = null;
  for (const t of ST.perg.templates) { resposta = todos.find((c) => c.template_id === t); if (resposta) break; }
  return { todos, resposta, outros: todos.filter((c) => c !== resposta) };
}
function moduloPorId(id) { return (ST.dados.modulos || []).find((m) => m.id === id); }
function nomeModulo(id) { const m = moduloPorId(id); return m ? m.nome : id; }
function badgeNivel(nv) { return `<span class="nivel ${esc(nv)}">${esc(nv)} · ${esc(NIVEL[nv] || nv)}</span>`; }
function contarPalavras(t) { return String(t).split(/\s+/).filter(Boolean).length; }

/* ---------- render geral ---------- */
function renderTudo() { renderAviso(); renderZap(); renderAud(); }

function renderAviso() {
  const d = ST.dados, i = ST.info;
  let h = "";
  if (i.exemplo) {
    const outro = !ST.local.nome.startsWith(d.local.municipio);
    h += `<div class="faixa-aviso"><b>Dados de exemplo.</b> Não achei <code>${esc(i.tentou)}</code> (${esc(i.motivo)}). Mostrando <code>${esc(i.usou)}</code>: ${esc(d.local.municipio)}, talhão “${esc(d.talhao.nome)}”, ${d.modo === "replay" ? "replay" : "referência"} de ${esc(dataBR(d.data_referencia))}.${outro ? ` Você escolheu ${esc(ST.local.nome)}, mas estes números não são desse lugar.` : ""}</div>`;
  }
  $("aviso").innerHTML = h;
}

/* ---------- WhatsApp ---------- */
function renderZap() {
  const d = ST.dados;
  const { resposta, outros } = cartoesOrdenados();
  let h = `<div class="dia">${d.modo === "replay" ? "Replay" : "Referência"} · ${esc(dataBR(d.data_referencia))}</div>`;
  h += `<div class="bolha eu"><div class="audio"><span class="play" style="background:var(--destaque);cursor:default" aria-hidden="true">${ICON_MIC}</span><span class="onda"></span></div>
      <div class="transcricao"><small>Áudio do agricultor · transcrição automática</small>“${esc(ST.perg.texto)}”</div></div>`;
  h += `<div class="bolha eu"><div class="pin"><span style="color:var(--alerta)">${ICON_PIN}</span><div><b>${esc(d.local.municipio)}, ${esc(d.local.uf)}</b><br><span class="peq">localização enviada · ${n(d.local.lat)}; ${n(d.local.lon)}</span></div></div></div>`;
  if (d.nao_sei && d.nao_sei.ativo) {
    h += `<div class="aviso-sistema">O motor respondeu “não sei”${d.nao_sei.motivos.length ? ` (${esc(d.nao_sei.motivos.map((m) => MOTIVO_NAO_SEI[m] || m).join("; "))})` : ""}. Avisa ${esc(ENCAMINHAR[d.nao_sei.encaminhar_para] || d.nao_sei.encaminhar_para)}.</div>`;
  }
  if (resposta) {
    h += blocoCartao(resposta);
  } else if (!cartoesWA().length) {
    h += `<div class="aviso-sistema">Esta saída não tem cartões para o WhatsApp.</div>`;
  } else {
    h += `<div class="aviso-sistema">Esta saída não tem cartão para a pergunta “${esc(ST.perg.texto)}”. Os cartões que existem estão logo abaixo.</div>`;
  }
  if (outros.length) {
    const ativo = outros.some((c) => (c.alerta_ids || []).some((id) => (d.alertas || []).some((a) => a.id === id && a.estado === "ativo")));
    h += `<button type="button" class="btn-mais" data-act="mais" aria-expanded="${ST.mais}">${ST.mais ? "Esconder" : "Ver mais"} ${outros.length} ${outros.length === 1 ? "mensagem" : "mensagens"} do assistente${ativo ? " (tem aviso ativo)" : ""}</button>`;
    if (ST.mais) h += outros.map((c) => `<div class="dia">${esc(NOME_TEMPLATE[c.template_id] || c.template_id)}</div>${blocoCartao(c)}`).join("");
  }
  $("chat").innerHTML = h;
}

function blocoCartao(c) {
  const img = htmlImagem(c, ST.dados);
  let h = "";
  if (img) h += `<div class="bolha larga">${img}</div>`;
  h += `<div class="bolha"><div class="audio">
      <button type="button" class="play" data-act="falar" data-card="${esc(c.id)}" aria-pressed="false" aria-label="Ouvir o áudio: ${esc(NOME_TEMPLATE[c.template_id] || c.template_id)}">${ICON_PLAY}</button>
      <span class="onda" aria-hidden="true"></span><span class="dur">até ${n(c.audio.duracao_max_s)} s</span></div>
      <details><summary>Ver o que o áudio diz</summary><p>${esc(c.audio.roteiro)}</p></details></div>`;
  h += `<div class="bolha">${esc(c.texto)}</div>`;
  return h;
}

function falar(cardId, btn) {
  const c = ST.dados.cartoes.find((x) => x.id === cardId);
  if (!c) return;
  const parar = () => { document.querySelectorAll('button.play[data-act="falar"]').forEach((b) => { b.setAttribute("aria-pressed", "false"); b.innerHTML = ICON_PLAY; }); };
  if (!("speechSynthesis" in window)) {
    const det = btn.closest(".bolha").querySelector("details"); if (det) det.open = true;
    return;
  }
  if (btn.getAttribute("aria-pressed") === "true") { ST.tts = null; speechSynthesis.cancel(); parar(); return; }
  speechSynthesis.cancel(); parar();
  const u = new SpeechSynthesisUtterance(c.audio.roteiro);
  u.lang = "pt-BR";
  ST.tts = u;
  u.onend = u.onerror = () => { if (ST.tts === u) { ST.tts = null; parar(); } };
  btn.setAttribute("aria-pressed", "true"); btn.innerHTML = ICON_PAUSE;
  speechSynthesis.speak(u);
}

/* ---------- auditoria ---------- */
function renderAud() {
  const d = ST.dados;
  const cel = (r, v, s) => `<div><span>${esc(r)}</span>${esc(v)}${s ? `<br><span style="text-transform:none;letter-spacing:0;font-size:12.5px">${esc(s)}</span>` : ""}</div>`;
  const mesma = (d.local.ponto_power.mesma_celula_que || []).join(", ");
  $("audCtx").innerHTML = `<div class="contexto">
    ${cel("Local", `${d.local.municipio}/${d.local.uf}`, `IBGE ${d.local.codigo_ibge}`)}
    ${cel("Grade do POWER", `~${n(d.local.ponto_power.resolucao_km)} km`, mesma ? `mesma célula: ${mesma}` : "")}
    ${cel("Talhão", d.talhao.nome, `solo ${SOLO[d.talhao.solo_declarado] || d.talhao.solo_declarado}, CAD ${n(d.talhao.cad_mm.valor)} mm`)}
    ${cel("Produtor", d.produtor.id_pseudonimo, `prioridade: ${PRIORIDADE[d.produtor.prioridade] || d.produtor.prioridade}`)}
    ${cel("Região", d.regiao.nome, `papel: ${d.regiao.papel}`)}
    ${cel("Referência", `${dataBR(d.data_referencia)} · ${d.modo === "operacao" ? "operação" : d.modo}`, `safra ${d.safra} · motor ${d.motor.versao}`)}
  </div>`;
  $("abas").innerHTML = ABAS.map(([k, t]) => `<button type="button" data-act="aba" data-k="${k}" aria-pressed="${k === ST.aba}">${t}</button>`).join("");
  const f = { mensagem: tabMensagem, estrategias: tabEstrategias, graficos: tabGraficos, validacao: tabValidacao, limites: tabLimites, rastro: tabRastro, glossario: tabGlossario }[ST.aba];
  $("audCorpo").innerHTML = f();
}

/* --- aba Mensagem: texto com cada número ligado ao rastro --- */
function segmentar(c) {
  const texto = c.texto;
  const vars = Object.entries(c.variaveis || {}).map(([k, v]) => ({ k, txt: String(v.texto), ptr: v.ponteiro })).filter((v) => v.txt).sort((a, b) => b.txt.length - a.txt.length);
  const usados = [], semTrecho = [];
  const eLetra = (ch) => /[\p{L}\p{N}]/u.test(ch || "");
  for (const v of vars) {
    /* o texto da variável pode aparecer com a 1ª letra minúscula no meio da frase (ex.: lista "Em teste: ...") */
    const cands = [...new Set([v.txt, v.txt[0].toLowerCase() + v.txt.slice(1)])];
    let ok = false;
    for (const cand of cands) {
      let de = 0;
      while (!ok) {
        const i = texto.indexOf(cand, de);
        if (i < 0) break;
        const e = i + cand.length;
        let bom = !usados.some((u) => i < u.e && e > u.s);
        if (bom && eLetra(texto[i - 1]) && eLetra(cand[0])) bom = false;
        if (bom && eLetra(texto[e]) && eLetra(cand[cand.length - 1])) bom = false;
        if (bom) { usados.push({ s: i, e, v: Object.assign({}, v, { txt: cand }) }); ok = true; break; }
        de = i + 1;
      }
      if (ok) break;
    }
    if (!ok) semTrecho.push(v);
  }
  usados.sort((a, b) => a.s - b.s);
  let h = "", pos = 0;
  for (const u of usados) {
    h += esc(texto.slice(pos, u.s));
    const marcado = ST.numero && ST.numero.ptr === u.v.ptr && ST.numero.cardId === c.id && ST.numero.chave === u.v.k;
    h += `<button type="button" class="numero" data-act="numero" data-ptr="${esc(u.v.ptr)}" data-texto="${esc(u.v.txt)}" data-chave="${esc(u.v.k)}" data-card="${esc(c.id)}" aria-pressed="${!!marcado}" title="Ver de onde vem">${esc(texto.slice(u.s, u.e))}</button>`;
    pos = u.e;
  }
  h += esc(texto.slice(pos));
  return { html: h, ligadas: usados.length, total: vars.length, semTrecho };
}

function tabMensagem() {
  const wa = cartoesWA();
  if (!wa.length) return '<p>Esta saída não tem cartões para o WhatsApp.</p>';
  const c = wa.find((x) => x.id === ST.cartaoId) || wa[0];
  const seg = segmentar(c);
  const contadas = contarPalavras(c.texto);
  const chips = wa.map((x) => `<button type="button" data-act="cartao" data-id="${esc(x.id)}" aria-pressed="${x.id === c.id}">${esc(NOME_TEMPLATE[x.template_id] || x.template_id)}</button>`).join("");
  return `
    <p class="peq">É a mensagem que o produtor recebeu. Toque num trecho sublinhado para ver de onde vem o número.</p>
    <div class="chips" role="group" aria-label="Escolha a mensagem">${chips}</div>
    <div class="espelho">${seg.html}</div>
    <div class="leg" style="margin-top:8px"><span>Sublinhado = tem variável e ponteiro no JSON</span><span>Sem sublinhado = constante do template (regra R8)</span></div>
    ${ST.numero && ST.numero.cardId === c.id ? htmlPainel() : ""}
    <h3>Conferências desta mensagem</h3>
    <dl class="par">
      <dt>Template</dt><dd><code>${esc(c.template_id)}</code> · cartão <code>${esc(c.id)}</code></dd>
      <dt>Palavras</dt><dd>${n(c.palavras)} declaradas, ${contadas} contadas ${c.palavras === contadas ? '<span class="tag ok">bate</span>' : '<span class="tag alta">diverge</span>'}</dd>
      <dt>Variáveis no texto</dt><dd>${seg.ligadas} de ${seg.total} ${seg.ligadas === seg.total ? '<span class="tag ok">todas achadas</span>' : `<span class="tag alta">faltam: ${esc(seg.semTrecho.map((v) => v.k).join(", "))}</span>`}</dd>
      <dt>Estratégias</dt><dd>${(c.estrategia_ids || []).map((id) => `<code>${esc(id)}</code>`).join(" ") || "—"}</dd>
      <dt>Alertas</dt><dd>${(c.alerta_ids || []).map((id) => `<code>${esc(id)}</code>`).join(" ") || "—"}</dd>
      <dt>Áudio</dt><dd>até ${n(c.audio.duracao_max_s)} s · lido pelo TTS a partir do roteiro</dd>
    </dl>
    <details><summary>Roteiro do áudio</summary><p>${esc(c.audio.roteiro)}</p></details>
    <p class="peq">O modelo de linguagem só transcreve o áudio do produtor e lê este texto pronto. Nenhum número sai dele.</p>`;
}

/* --- painel do número: valor, incerteza, premissas e cadeia de rastro --- */
function valorTxt(v) {
  if (v === null || v === undefined) return "—";
  if (typeof v === "object") return `<code>${esc(JSON.stringify(v))}</code>`;
  return esc(n(v));
}
function htmlPainel() {
  const nu = ST.numero;
  if (!nu) return "";
  const d = ST.dados, r = resolver(d, nu.ptr), p = r.partes;
  const ids = [];
  if (p[0] === "rastro" && r.cadeia[2] && r.cadeia[2].obj && r.cadeia[2].obj.id) ids.push(r.cadeia[2].obj.id);
  [...r.cadeia].reverse().forEach((c) => {
    const o = c.obj;
    if (o && typeof o === "object" && Array.isArray(o.rastro) && o.rastro.every((x) => typeof x === "string")) o.rastro.forEach((x) => { if (!ids.includes(x)) ids.push(x); });
  });
  const est = p[0] === "estrategias" ? d.estrategias[p[1]] : null;
  const ind = est && p[2] === "indicadores" ? est.indicadores[p[3]] : null;
  const lin = est && p[2] === "risco_por_decendio" && p[3] === "linhas" ? est.risco_por_decendio.linhas[p[4]] : null;
  const al = p[0] === "alertas" ? d.alertas[p[1]] : null;
  let corpo = `<dl class="par"><dt>Trecho</dt><dd>${nu.texto ? `“${esc(nu.texto)}”` : "—"}</dd><dt>Onde está no JSON</dt><dd><code>${esc(nu.ptr)}</code></dd><dt>Valor guardado</dt><dd><b>${valorTxt(r.valor)}</b></dd></dl>`;
  if (ind) {
    corpo += `<h4>Indicador</h4><p>${esc(ind.rotulo)}</p><dl class="par">
      <dt>Valor</dt><dd><b>${esc(valorInd(ind))}</b></dd>
      <dt>IC95 (amostragem)</dt><dd>${ind.ic95 ? esc(faixa(ind.ic95)) : "não tem"}</dd>
      <dt>Faixa dos parâmetros</dt><dd>${ind.faixa_parametros ? esc(faixa(ind.faixa_parametros)) : "não tem"}</dd>
      <dt>Anos e período</dt><dd>${n(ind.n_anos)} anos · ${esc(ind.periodo)}</dd>
      <dt>Nível</dt><dd>${badgeNivel(ind.nivel_evidencia)}</dd>
      <dt>Módulo</dt><dd>${esc(nomeModulo(ind.modulo_id))}</dd></dl>${svgFaixaInd(ind)}${svgFaixaInd(ind) ? legFaixaInd(ind) : ""}`;
  }
  if (lin) {
    corpo += `<h4>Linha do decêndio ${esc(lin.decendio)}</h4><dl class="par">
      <dt>Em 10 anos</dt><dd><b>${n(lin.em10)}</b>${lin.ic95 ? ` · IC95 ${esc(faixa(lin.ic95))}` : ""}</dd>
      <dt>Anos com o evento</dt><dd>${lin.k !== null ? `${n(lin.k)} de ${n(lin.n)}` : `${n(lin.n)} anos simulados`}</dd>
      <dt>Componentes</dt><dd>água ${n(lin.componentes.agua)} · geada ${n(lin.componentes.geada)} · ano extremo ${n(lin.componentes.ano_extremo)}</dd>
      ${lin.zarc ? `<dt>ZARC</dt><dd><span class="tag conf">conferência, não entrada</span> ${lin.zarc.risco_pct !== null ? esc(lin.zarc.risco_pct) + "%" : "sem indicação"}</dd>` : ""}</dl>`;
  }
  if (al) {
    corpo += `<h4>Alerta ${esc(al.id)}</h4><dl class="par">
      <dt>Estado</dt><dd>${esc(al.estado)} · ${badgeNivel(al.nivel_evidencia)}</dd>
      <dt>Janela</dt><dd>${esc(dataBR(al.janela.de))} a ${esc(dataBR(al.janela.ate))}</dd>
      <dt>Índice</dt><dd>${esc(al.indice.nome)}: <b>${n(al.indice.valor)}</b></dd>
      <dt>Posição entre anos passados</dt><dd>${n(al.percentil_local.valor)} de 100 · ${n(al.percentil_local.n_anos_passados)} anos (${esc(al.percentil_local.periodo_passado)})</dd>
      ${al.frase_probabilidade ? `<dt>Frase de probabilidade (só auditoria, não vai ao WhatsApp)</dt><dd>${n(al.frase_probabilidade.anos_assim_ruins_em_10)} em 10 em anos assim, ${n(al.frase_probabilidade.ano_qualquer_ruim_em_10)} em 10 num ano qualquer. Ano ruim = ${esc(al.frase_probabilidade.definicao_ruim)}. ${n(al.frase_probabilidade.eventos_testados)} eventos testados.</dd>` : ""}
      <dt>Recall</dt><dd>${n(al.recall_pct)}%</dd></dl>
      ${al.silencio_nao_e_seguranca ? '<p class="aviso-inline"><b>Sem aviso não quer dizer ano seguro.</b></p>' : ""}`;
  }
  if (est) {
    const bloco = (t, arr) => (arr && arr.length ? `<h4>${t}</h4><ul class="lista">${arr.map((x) => `<li>${rico(x)}</li>`).join("")}</ul>` : "");
    corpo += `<h4>Estratégia ${esc(est.id)} · ${esc(est.nome_curto)}</h4>${bloco("Premissas", est.premissas)}${bloco("Quebra se", est.quebra_se)}${bloco("Não foi calculado", est.nao_calculado)}`;
  }
  corpo += `<h4>Cadeia do rastro</h4>`;
  corpo += ids.length ? `<ul class="cadeia">${ids.map((id) => htmlItemRastro(id, new Set())).join("")}</ul>`
    : '<p class="peq">Sem item de rastro: o valor vem direto do JSON (nome ou resposta do produtor).</p>';
  return `<section class="painel-numero" id="painelNumero" aria-label="Painel do número">
    <div class="cab-bloco"><h3 style="margin:0">De onde vem este número</h3><button type="button" data-act="fechar-num">Fechar</button></div>${corpo}</section>`;
}

function htmlItemRastro(id, vis) {
  const it = ST.rastro[id];
  if (!it) return `<li class="item-rastro faltando"><b>${esc(id)}</b>: não existe em rastro[] (regra R1).</li>`;
  const conf = it.tipo === "conferencia" || (it.fonte && it.fonte.categoria === "externo_conferencia");
  const f = it.fonte || {};
  const lit = f.categoria === "literatura_externa";
  const valid = it.tipo === "calculo" && it.parametros && it.parametros.so_auditoria === true;
  let h = `<li class="item-rastro ${esc(it.tipo)}"><div class="cab"><span class="ts">${esc(TIPO_RASTRO[it.tipo] || it.tipo)}</span><b>${esc(it.id)}</b>
    ${conf ? '<span class="tag conf">conferência, não entrada</span>' : ""}${lit ? '<span class="tag alta">exceção à regra de dados</span>' : ""}${valid ? '<span class="tag conf">validação, só auditoria</span>' : ""}<span class="tag">${esc(f.nome)} · ${esc(FONTE_CAT[f.categoria] || f.categoria)}</span></div>
    <div class="descr">${rico(it.descricao)}</div>`;
  const meta = [];
  if (f.variavel) meta.push(`variável: ${esc(f.variavel)}`);
  if (f.periodo) meta.push(`período: ${esc(f.periodo)}`);
  if (f.resolucao) meta.push(`resolução: ${esc(f.resolucao)}`);
  if (meta.length) h += `<div class="meta">${meta.join(" · ")}</div>`;
  if (f.arquivo) h += `<div class="meta">arquivo: <code>${esc(f.arquivo)}</code></div>`;
  if (f.url) h += `<div class="meta">fonte: <code>${esc(f.url)}</code></div>`;
  if (it.tipo === "calculo") {
    if (it.script) h += `<div class="meta">script: <code>${esc(it.script.caminho)}</code>${it.script.funcao ? ` · função <code>${esc(it.script.funcao)}</code>` : ""}</div>`;
    if (it.parametros && Object.keys(it.parametros).length) h += `<div class="meta">parâmetros: ${Object.entries(it.parametros).map(([k, v]) => `<code>${esc(k)} = ${esc(typeof v === "object" ? JSON.stringify(v) : v)}</code>`).join(" ")}</div>`;
    if (it.resultado) h += `<div class="meta">resultado: <code>${esc(it.resultado.arquivo)}</code>${it.resultado.chave ? ` · chave <code>${esc(it.resultado.chave)}</code>` : ""}</div>`;
    if ((it.entradas || []).length && !vis.has(id)) {
      const v2 = new Set(vis); v2.add(id);
      h += `<div class="meta">entradas:</div><ul class="cadeia">${it.entradas.map((e) => htmlItemRastro(e, v2)).join("")}</ul>`;
    }
  }
  return h + "</li>";
}

/* --- aba Estratégias --- */
function tabEstrategias() {
  const d = ST.dados;
  const idx = d.estrategias.map((e, i) => ({ e, i })).sort((a, b) => a.e.ordem - b.e.ordem);
  const cal = svgCalendario(idx.map((x) => x.e));
  let h = `<p class="peq">Ordem pela prioridade do produtor (“${esc(PRIORIDADE[d.produtor.prioridade] || d.produtor.prioridade)}”). A prioridade muda só a ordem, nunca os números (regra R9). Toda comparação inclui a estratégia atual.</p>`;
  if (cal) h += `<div class="bloco"><h3>Janelas de plantio</h3>${cal}<div class="leg"><span><i class="b1"></i>estratégia nova</span><span><i class="b2"></i>o de sempre (atual)</span></div></div>`;
  h += idx.map(({ e, i }) => blocoEstrategia(e, i)).join("");
  return h;
}
function blocoEstrategia(e, i) {
  const seq = (e.sequencia || []).map((s) => {
    const pl = s.plantio && s.plantio.de ? `, plantio de ${esc(s.plantio.de)} a ${esc(s.plantio.ate)}` : "";
    return `<li>${esc(CULTURA[s.cultura] || s.cultura)} (${esc(ESTACAO[s.estacao] || s.estacao)})${s.fracao_area < 1 ? `, ${n(Math.round(s.fracao_area * 100))}% da área` : ""}${pl}${s.manejo ? `. ${esc(s.manejo)}` : ""}</li>`;
  }).join("");
  const inds = (e.indicadores || []).map((x, j) => `<div class="bloco" style="background:var(--cartao2)">
      <div class="cab-bloco"><b>${esc(valorInd(x))}</b>${badgeNivel(x.nivel_evidencia)}</div>
      <div>${rico(x.rotulo)}</div>
      <div class="peq">${n(x.n_anos)} anos · ${esc(x.periodo)} · ${esc(nomeModulo(x.modulo_id))}${x.ic95 ? ` · IC95 ${esc(faixa(x.ic95))}` : ""}${x.faixa_parametros ? ` · parâmetros ${esc(faixa(x.faixa_parametros))}` : ""}</div>
      ${svgFaixaInd(x)}${svgFaixaInd(x) ? legFaixaInd(x) : ""}
      <button type="button" data-act="numero" data-ptr="/estrategias/${i}/indicadores/${j}/valor" data-texto="${esc(valorInd(x))}" data-card="" style="margin-top:8px">Ver rastro</button></div>`).join("");
  const lista = (t, a) => (a && a.length ? `<h4>${t}</h4><ul class="lista">${a.map((x) => `<li>${rico(x)}</li>`).join("")}</ul>` : "");
  const aqui = ST.numero && ST.numero.cardId === "" && ST.numero.ptr.startsWith(`/estrategias/${i}/`);
  return `<article class="bloco${e.nivel_evidencia === "N1" ? " inativo" : ""}">
    <div class="cab-bloco"><b>${n(e.ordem)}. ${esc(e.nome_curto)}</b>${e.e_atual ? '<span class="tag ok">atual</span>' : ""}${badgeNivel(e.nivel_evidencia)}<span class="tag">${esc(COMO_MOSTRAR[e.como_mostrar] || e.como_mostrar)}</span></div>
    <p>${esc(e.nome_falado)}</p>
    <h4>Sequência</h4><ul class="lista">${seq}</ul>
    ${inds ? `<h4>Números</h4>${inds}` : '<p class="peq">Sem número calculado. Aparece só pelo nome, como “em teste”.</p>'}
    ${lista("Premissas", e.premissas)}${lista("Quebra se", e.quebra_se)}${lista("Não foi calculado", e.nao_calculado)}
    ${e.solo_texto ? `<h4>Solo <span class="tag">a validar</span></h4><p>${esc(typeof e.solo_texto === "object" ? JSON.stringify(e.solo_texto) : e.solo_texto)}</p>` : ""}
    ${aqui ? htmlPainel() : ""}</article>`;
}

/* --- aba Gráficos --- */
function tabGraficos() {
  const d = ST.dados;
  const e = d.estrategias.find((x) => x.id === ST.estId) || d.estrategias[0];
  const ei = d.estrategias.indexOf(e);
  const chips = d.estrategias.map((x) => `<button type="button" data-act="est" data-id="${esc(x.id)}" aria-pressed="${x.id === e.id}">${esc(x.id)} · ${esc(x.nome_curto)}</button>`).join("");
  let h = `<h3 style="margin-top:0">Risco por decêndio de plantio</h3><div class="chips" role="group" aria-label="Escolha a estratégia">${chips}</div>`;
  const rp = e.risco_por_decendio;
  if (!rp) {
    h += `<p>A estratégia <b>${esc(e.nome_curto)}</b> não tem cálculo por decêndio.</p>`;
  } else {
    const temEm10 = rp.linhas.some((l) => l.em10 !== null);
    h += `<div class="bloco"><div class="cab-bloco"><b>${esc(e.nome_curto)}</b>${badgeNivel(e.nivel_evidencia)}<span class="tag">${esc(nomeModulo(rp.modulo_id))}</span></div>
      <p class="peq">${esc(Object.keys(CULTURA).reduce((t, k) => t.replace(k, CULTURA[k]), rp.cultura_alvo))}. Evento: ${esc(rp.evento)}.</p>`;
    h += temEm10 ? svgRisco(e) + legRisco(e) : (svgMetricas(e) + LEG_METRICAS);
    h += `<button type="button" data-act="numero" data-ptr="/estrategias/${ei}/risco_por_decendio" data-texto="tabela por decêndio" data-card="" style="margin-top:10px">Ver rastro da tabela</button>`;
    h += `</div>`;
    h += `<details class="bloco"><summary><b>Tabela por decêndio (${rp.linhas.length} linhas)</b></summary>${tabelaDecendios(e)}</details>`;
    h += ST.numero && ST.numero.cardId === "" && ST.numero.ptr.startsWith("/estrategias/") ? htmlPainel() : "";
  }
  const als = d.alertas || [];
  h += `<h3>Alertas de ano extremo</h3>`;
  h += als.length ? als.map((a, i) => blocoAlerta(a, i)).join("") : '<p class="peq">Esta saída não tem alertas.</p>';
  return h;
}
function tabelaDecendios(e) {
  const ls = e.risco_por_decendio.linhas;
  const algum = (f) => ls.some((l) => f(l) !== null && f(l) !== undefined);
  const metKeys = [...new Set(ls.flatMap((l) => Object.keys(l.metricas_extra || {})))];
  /* Só entram colunas que têm algum valor. Evita linhas de traços. */
  const cols = [
    ["Decêndio", (l) => `<b>${esc(l.decendio)}</b>`, true],
    ["Em 10 anos", (l) => n(l.em10), algum((l) => l.em10)],
    ["IC95", (l) => (l.ic95 ? esc(faixa(l.ic95)) : "—"), algum((l) => l.ic95)],
    ["Anos", (l) => (l.k !== null ? `${n(l.k)}/${n(l.n)}` : `n=${n(l.n)}`), true],
    ["Água", (l) => n(l.componentes.agua), algum((l) => l.componentes.agua)],
    ["Geada", (l) => n(l.componentes.geada), algum((l) => l.componentes.geada)],
    ["Ano extremo", (l) => n(l.componentes.ano_extremo), algum((l) => l.componentes.ano_extremo)],
    ...metKeys.map((k) => [k, (l) => (l.metricas_extra && k in l.metricas_extra ? n(l.metricas_extra[k]) : "—"), true]),
    ["ZARC (conferência)", (l) => (l.zarc ? (l.zarc.risco_pct !== null ? `${l.zarc.risco_pct}% (${l.zarc.risco_pct / 10} em 10)` : "sem indicação") : "—"), algum((l) => l.zarc), "conf-c"]
  ].filter((c) => c[2]);
  return `<table class="tab"><thead><tr>${cols.map((c) => `<th>${esc(c[0])}</th>`).join("")}</tr></thead><tbody>${ls.map((l) =>
    `<tr>${cols.map((c) => `<td data-r="${esc(c[0])}"${c[3] ? ` class="${c[3]}"` : ""}>${c[1](l)}</td>`).join("")}</tr>`).join("")}</tbody></table>
    <p class="peq">Colunas sem valor em nenhum decêndio não aparecem. Água, geada e ano extremo são componentes em anos de 10. ZARC é só conferência.</p>`;
}
function blocoAlerta(a, i) {
  const f = a.frase_probabilidade;
  return `<div class="bloco${a.estado === "ativo" ? " alta" : ""}">
    <div class="cab-bloco"><b>${esc(nomeModulo(a.modulo_id))}</b><span class="tag ${a.estado === "ativo" ? "alta" : ""}">${esc(a.estado)}</span>${badgeNivel(a.nivel_evidencia)}</div>
    <p>${esc(a.indice.nome)}: <b>${n(a.indice.valor)}</b> · janela ${esc(dataBR(a.janela.de))} a ${esc(dataBR(a.janela.ate))}</p>
    ${svgAlerta(a)}
    <p class="peq">Posição entre ${n(a.percentil_local.n_anos_passados)} anos passados (${esc(a.percentil_local.periodo_passado)}). Só anos anteriores à safra entram (regra R6).</p>
    ${f ? `<p class="peq"><b>Só auditoria.</b> Esta frase usa o IBGE PAM para definir "ano ruim" e não vai ao WhatsApp (regra R2).</p><dl class="par"><dt>Em anos assim</dt><dd>${n(f.anos_assim_ruins_em_10)} em 10</dd><dt>Num ano qualquer</dt><dd>${n(f.ano_qualquer_ruim_em_10)} em 10</dd><dt>Ano ruim é</dt><dd>${esc(f.definicao_ruim)}</dd><dt>Eventos testados</dt><dd>${n(f.eventos_testados)}</dd></dl>` : ""}
    <p>O alerta pega ${n(a.recall_pct)}% dos anos ruins nos testes. ${a.silencio_nao_e_seguranca ? "<b>Sem aviso não quer dizer ano seguro.</b>" : ""}</p>
    <button type="button" data-act="numero" data-ptr="/alertas/${i}" data-texto="alerta" data-card="">Ver rastro do alerta</button>
    ${ST.numero && ST.numero.cardId === "" && ST.numero.ptr === `/alertas/${i}` ? htmlPainel() : ""}</div>`;
}

/* --- aba Validação --- */
function tabValidacao() {
  const d = ST.dados;
  const ordemN = { N3: 0, N2: 1, N1: 2, N0: 3 };
  const mods = [...d.modulos].sort((a, b) => (b.ativo - a.ativo) || (ordemN[a.nivel_evidencia] - ordemN[b.nivel_evidencia]));
  const nAt = d.modulos.filter((m) => m.ativo).length;
  let h = `<p class="peq">${nAt} de ${d.modulos.length} módulos ligados nesta saída. Região: ${esc(d.regiao.nome)}. A região decide quais módulos pesam.</p>`;
  h += mods.map((m) => `<article class="bloco${m.ativo ? "" : " inativo"}">
      <div class="cab-bloco"><b>${esc(m.nome)}</b>${badgeNivel(m.nivel_evidencia)}<span class="tag ${m.ativo ? "ok" : ""}">${m.ativo ? "ligado" : "desligado"}</span><span class="tag">${esc(PAPEL_MOD[m.papel] || m.papel)}</span></div>
      <p>${rico(m.motivo)}</p>
      ${(m.validacao || []).length ? `<h4>Validação</h4><ul class="lista">${m.validacao.map((v) => `<li><b>${esc(v.ref)}</b>: ${rico(v.resultado)}<br>${/^solucao\//.test(v.caminho) ? `<a href="../${esc(v.caminho.replace(/^solucao\//, ""))}" target="_blank" rel="noopener"><code>${esc(v.caminho)}</code></a>` : `<code>${esc(v.caminho)}</code>`}</li>`).join("")}</ul>` : ""}
      ${(m.nao_ve || []).length ? `<h4>O que não vê</h4><ul class="lista">${m.nao_ve.map((x) => `<li>${rico(x)}</li>`).join("")}</ul>` : ""}</article>`).join("");
  h += `<h3>Conferências com fontes externas</h3><p class="peq">Servem para conferir o resultado. Nunca entram como dado de cálculo do produto, e nenhuma mensagem do WhatsApp leva número delas (regra R2). O único cálculo que lê a PAM é o de validação do alerta, marcado “só auditoria”.</p>`;
  h += (d.conferencias || []).map((c) => `<article class="bloco conf">
      <div class="cab-bloco"><span class="tag conf">conferência, não entrada</span><b>${esc(c.o_que)}</b></div>
      <p><span class="tag ${c.resultado === "bate" ? "ok" : c.resultado === "nao_bate" ? "alta" : ""}">${esc(RESULT_CONF[c.resultado] || c.resultado)}</span> contra ${esc(c.contra)}</p>
      <p>${rico(c.detalhe)}</p>
      <div>${(c.rastro || []).map((r) => `<code>${esc(r)}</code>`).join(" ")}</div></article>`).join("") || '<p class="peq">Sem conferências nesta saída.</p>';
  h += `<h3>Resposta “não sei”</h3><p>${d.nao_sei.ativo ? `<b>Ativa.</b> Motivos: ${esc(d.nao_sei.motivos.map((m) => MOTIVO_NAO_SEI[m] || m).join("; ") || "não informado")}. Avisa ${esc(ENCAMINHAR[d.nao_sei.encaminhar_para] || d.nao_sei.encaminhar_para)}.` : `Inativa. Se ativar, avisa ${esc(ENCAMINHAR[d.nao_sei.encaminhar_para] || d.nao_sei.encaminhar_para)}.`}</p>`;
  return h;
}

/* --- aba Limites --- */
function tabLimites() {
  const ordem = { alta: 0, media: 1, baixa: 2 };
  const ls = [...(ST.dados.limites || [])].sort((a, b) => ordem[a.gravidade] - ordem[b.gravidade]);
  const nome = { alta: "alta", media: "média", baixa: "baixa" };
  return `<p class="peq">Os de gravidade alta vêm primeiro. “Vai ao produtor” quer dizer que a frase do limite aparece, igual, numa mensagem do WhatsApp (regra R14). Sigla sublinhada: passe o mouse ou veja o Glossário.</p>` +
    ls.map((l) => `<article class="bloco${l.gravidade === "alta" ? " alta" : ""}">
      <div class="cab-bloco"><span class="tag ${l.gravidade === "alta" ? "alta" : ""}">gravidade ${nome[l.gravidade]}</span><span class="tag ${l.mostrar_ao_agricultor ? "ok" : ""}">${l.mostrar_ao_agricultor ? "vai ao produtor" : "só na auditoria"}</span><code>${esc(l.id)}</code></div>
      <p>${rico(l.texto)}</p>
      ${l.trecho ? `<p class="peq">Frase na mensagem: “${esc(l.trecho)}”</p>` : ""}
      <div class="peq">Afeta: ${(l.afeta || []).map((x) => `<code>${esc(x)}</code>`).join(" ") || "—"}</div></article>`).join("");
}

/* --- aba Glossário --- */
function tabGlossario() {
  return `<p class="peq">Termos que aparecem nas outras abas. As siglas V1 a V7 são as frentes de validação; cada uma tem um relatório.</p>
    <dl class="par">${GLOSSARIO.map(([t, d]) => `<dt>${esc(t)}</dt><dd>${esc(d)}</dd>`).join("")}</dl>
    <h3>Relatórios das frentes</h3><ul class="lista">${[1, 2, 3, 4, 5, 6, 7].map((i) => `<li><a href="../validacao/V${i}/relatorio.md" target="_blank" rel="noopener">V${i}</a></li>`).join("")}</ul>`;
}

/* --- aba Rastro --- */
function tabRastro() {
  const grupos = ["dado", "parametro", "pergunta", "calculo", "conferencia"];
  const todos = ST.dados.rastro || [];
  return `<p class="peq">Todos os ${todos.length} itens. Dado e parâmetro vêm da aba Resources ou de método publicado. Conferência fica em outra cor e nunca entra num cálculo.</p>` +
    grupos.map((g) => {
      const its = todos.filter((r) => r.tipo === g);
      if (!its.length) return "";
      return `<h3>${esc(TIPO_RASTRO[g])}s (${its.length})</h3><ul class="cadeia">${its.map((r) => htmlItemRastro(r.id, new Set())).join("")}</ul>`;
    }).join("");
}

/* ---------- eventos ---------- */
document.addEventListener("click", (ev) => {
  const el = ev.target.closest("[data-act]");
  if (!el) return;
  const a = el.dataset.act;
  if (a === "tema") { alternarTema(); return; }
  if (a === "vista") {
    document.body.dataset.vista = el.dataset.v;
    document.querySelectorAll('[data-act="vista"]').forEach((b) => b.setAttribute("aria-pressed", String(b === el)));
    window.scrollTo({ top: 0 });
    return;
  }
  if (!ST.dados) return;
  if (a === "mais") { ST.mais = !ST.mais; renderZap(); return; }
  if (a === "falar") { falar(el.dataset.card, el); return; }
  if (a === "aba") { ST.aba = el.dataset.k; renderAud(); return; }
  if (a === "cartao") { ST.cartaoId = el.dataset.id; ST.numero = null; renderAud(); return; }
  if (a === "est") { ST.estId = el.dataset.id; renderAud(); return; }
  if (a === "numero") {
    ST.numero = { ptr: el.dataset.ptr, texto: el.dataset.texto || "", chave: el.dataset.chave || "", cardId: el.dataset.card ?? "" };
    renderAud();
    const p = $("painelNumero");
    if (p) p.scrollIntoView({ block: "nearest", behavior: "smooth" });
    return;
  }
  if (a === "fechar-num") { ST.numero = null; renderAud(); return; }
});

$("selLocal").addEventListener("change", (ev) => {
  ST.local = acharLocal(ev.target.value);
  ST.perg = ST.local.perguntas[0];
  montarPerguntas(); atualizarUrl(); carregar();
});
$("selPerg").addEventListener("change", (ev) => {
  ST.perg = acharPergunta(ST.local, ev.target.value);
  atualizarUrl();
  if (!ST.dados) return;
  ST.numero = null; ST.mais = false;
  ST.cartaoId = (cartoesOrdenados().resposta || cartoesWA()[0] || {}).id || null;
  renderZap(); renderAud();
});

iniciar();
