"use strict";
/* Tela 2: escolher o local e a pergunta. Leva para index.html?local=...&pergunta=... */
const SEL = { local: null, perg: null, tem: {} };
const $e = (id) => document.getElementById(id);

async function existe(slug) {
  try { const r = await fetch(`../saida/${slug}.json`, { method: "HEAD", cache: "no-store" }); return r.ok; } catch (e) { return false; }
}

function desenhar() {
  $e("locais").innerHTML = LOCAIS.map((l) => {
    const t = SEL.tem[l.slug];
    const tag = t === undefined ? "" : (t ? '<span class="tag ok">saída do motor encontrada</span>' : '<span class="tag">usa dados de exemplo</span>');
    return `<button type="button" class="opcao" data-l="${esc(l.slug)}" aria-pressed="${l.slug === SEL.local.slug}"><b>${esc(l.nome)}</b><span>${esc(l.papel)}. ${esc(l.resumo)}</span><br>${tag}</button>`;
  }).join("");
  $e("perguntas").innerHTML = SEL.local.perguntas.map((q) =>
    `<button type="button" class="opcao" data-q="${esc(q.id)}" aria-pressed="${q.id === SEL.perg.id}"><b>“${esc(q.texto)}”</b></button>`).join("");
  $e("abrir").href = `index.html?local=${encodeURIComponent(SEL.local.slug)}&pergunta=${encodeURIComponent(SEL.perg.id)}`;
}

document.addEventListener("click", (ev) => {
  const el = ev.target.closest("button");
  if (!el) return;
  if (el.dataset.act === "tema") { alternarTema(); return; }
  if (el.dataset.l) { SEL.local = acharLocal(el.dataset.l); SEL.perg = SEL.local.perguntas[0]; desenhar(); }
  if (el.dataset.q) { SEL.perg = acharPergunta(SEL.local, el.dataset.q); desenhar(); }
});

const p0 = lerParams();
SEL.local = acharLocal(p0.local);
SEL.perg = acharPergunta(SEL.local, p0.pergunta);
desenhar();
LOCAIS.forEach(async (l) => { SEL.tem[l.slug] = await existe(l.slug); desenhar(); });
