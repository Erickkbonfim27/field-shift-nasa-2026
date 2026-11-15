"use strict";
/* Utilitários e configuração compartilhados pelas duas telas.
   Regra: nenhum número de resultado nasce aqui. Tudo vem do JSON do contrato v2. */

/* Locais da spec (seção 1.2) e perguntas. As perguntas só dizem qual cartão abre primeiro.
   "templates" é a lista de preferência (ids da seção 6 da spec). */
const LOCAIS = [
  {
    slug: "sao-miguel-do-oeste", nome: "São Miguel do Oeste (SC)", regiao: "sc_extremo_oeste",
    papel: "Principal", resumo: "Leite e milho. Região que abre a demo.",
    perguntas: [
      { id: "segundo-milho", texto: "Planto o 2º milho ou aveia?", templates: ["T04_GEADA_LIMITE_2A_SAFRA", "T01_COMPARA_ESTRATEGIAS"] },
      { id: "ano-seco", texto: "Este ano está seco?", templates: ["T05_ANO_SECO_ATIVO", "T06_ANO_SECO_SILENCIO"] },
      { id: "sorgo", texto: "Quanto da silagem eu ponho em sorgo?", templates: ["T07_MISTURA_TALHAO_RASO", "T01_COMPARA_ESTRATEGIAS"] },
      { id: "caminhos", texto: "Que caminhos eu tenho para a silagem?", templates: ["T01_COMPARA_ESTRATEGIAS"] },
      { id: "data-milho", texto: "Quando planto o milho de verão?", templates: ["T02_GEADA_JANELA_SAFRA", "T03_TANTO_FAZ_DATA"] }
    ]
  },
  {
    slug: "ituporanga", nome: "Ituporanga (SC)", regiao: "sc_alto_vale",
    papel: "Principal (2º cartão)", resumo: "Cebola. Solo exposto medido; sem 3 rotações com número.",
    perguntas: [
      { id: "solo-cebola", texto: "O solo da cebola ficou descoberto?", templates: ["T10_SOLO_EXPOSTO"] },
      { id: "caminhos", texto: "Que caminhos eu tenho para a cebola?", templates: ["T01_COMPARA_ESTRATEGIAS"] }
    ]
  },
  {
    slug: "quixada", nome: "Quixadá (CE)", regiao: "semiarido_ce_pe_pb",
    papel: "Segunda região, só milho", resumo: "Semiárido. Milho na primeira chuva firme ou em data fixa.",
    perguntas: [
      { id: "milho-agora", texto: "Planto o milho agora ou espero?", templates: ["T11_SEMIARIDO_JANELA_MILHO", "T01_COMPARA_ESTRATEGIAS"] },
      { id: "caminhos", texto: "Que culturas eu comparo?", templates: ["T01_COMPARA_ESTRATEGIAS"] }
    ]
  }
];

const NOME_TEMPLATE = {
  T01_COMPARA_ESTRATEGIAS: "Comparar caminhos", T02_GEADA_JANELA_SAFRA: "Geada na data do milho",
  T03_TANTO_FAZ_DATA: "Data quase tanto faz", T04_GEADA_LIMITE_2A_SAFRA: "Limite do 2º milho",
  T05_ANO_SECO_ATIVO: "Aviso de ano seco", T06_ANO_SECO_SILENCIO: "Sem aviso de seca",
  T07_MISTURA_TALHAO_RASO: "Metade em sorgo", T08_EM_TESTE: "Em teste",
  T09_CEBOLA_HISTORICO: "Cebola: histórico", T10_SOLO_EXPOSTO: "Solo exposto",
  T11_SEMIARIDO_JANELA_MILHO: "Milho no Semiárido", T12_PRIORIDADE: "Pergunta de prioridade",
  T13_FOTO_REGISTRO: "Foto guardada", T14_NAO_SEI: "Não sei", T15_PEDE_SOLO: "Pergunta do solo"
};
const NIVEL = { N3: "Validado", N2: "Com ressalva", N1: "Em teste", N0: "Fora" };
const COMO_MOSTRAR = { com_numero: "número inteiro", com_faixa: "número com faixa", so_nome_em_teste: "só o nome, em teste", oculto: "oculto" };
const CULTURA = {
  milho_silagem: "Milho para silagem", milho_grao: "Milho grão", sorgo_silagem: "Sorgo para silagem",
  sorgo_forrageiro: "Sorgo forrageiro", pastagem_inverno: "Pasto de inverno", cebola: "Cebola",
  milho_palha: "Milho para palha", cobertura_verao: "Cobertura de verão", feijao_caupi: "Feijão-caupi",
  sorgo_grao: "Sorgo grão", pousio: "Pousio"
};
const ESTACAO = { verao: "verão", segunda_safra: "2ª safra", inverno: "inverno", chuvas: "época das chuvas" };
const PRIORIDADE = { silagem_garantida: "silagem garantida", renda: "renda", solo: "cuidar do solo", nao_informado: "não informada" };
const ATIVIDADE = { leite_milho: "leite e milho", cebola: "cebola", milho_feijao_sequeiro: "milho e feijão de sequeiro" };
const SOLO = { arenoso: "arenoso", medio: "médio", argiloso: "argiloso", raso_ou_pedregoso: "raso ou com pedra", nao_sei: "não sei" };
const PAPEL_MOD = { guarda: "guarda", principal: "principal", alerta: "alerta", insumo: "insumo", descritivo: "descritivo", em_teste: "em teste" };
const FONTE_CAT = {
  resources: "Resources do desafio", metodo_publicado: "método publicado", externo_conferencia: "conferência, não entrada",
  literatura_externa: "literatura externa (exceção à regra de dados)", produtor: "resposta do produtor", motor: "motor"
};
const TIPO_RASTRO = { dado: "dado", parametro: "parâmetro", calculo: "cálculo", conferencia: "conferência", pergunta: "pergunta" };
const SELO = { validado: "validado", com_ressalva: "com ressalva", em_teste: "em teste", atual: "atual" };
const RESULT_CONF = { bate: "bate", bate_em_parte: "bate em parte", nao_bate: "não bate", sem_dado: "sem dado" };
const ENCAMINHAR = { tecnico_ater: "o técnico (ATER)", cooperativa: "a cooperativa", nenhum: "ninguém" };
const MOTIVO_NAO_SEI = {
  fora_da_area: "lugar fora da área testada", cultura_fora: "cultura fora do que testamos",
  pergunta_praga_doenca_adubo_preco: "pergunta sobre praga, doença, adubo ou preço", sem_dado_recente: "sem dado recente",
  modulo_em_teste: "módulo ainda em teste", solo_desconhecido: "solo desconhecido"
};
/* Glossário do painel do técnico. Cada sigla que aparece nos textos de módulos, limites e conferências tem
   uma explicação curta aqui. As siglas V1 a V7 apontam para o relatório da frente de validação. */
const GLOSSARIO = [
  ["IC95", "Intervalo de confiança de 95%. Mostra o quanto o número muda só por termos poucos anos de dados."],
  ["Faixa dos parâmetros", "Quanto o número muda se trocarmos os valores que assumimos (por exemplo, o Ky do sorgo)."],
  ["ZARC", "Zoneamento Agrícola de Risco Climático do MAPA. Só conferência: nunca entra no cálculo."],
  ["Decêndio", "Período de 10 dias (dias 1 a 10, 11 a 20, 21 ao fim do mês)."],
  ["CAD", "Capacidade de água disponível do solo, em mm. Quanto de água o solo guarda para a planta."],
  ["ISNA", "Índice de satisfação da necessidade de água: água que a planta usou dividida pela que precisava (1 = não faltou)."],
  ["ET0", "Evapotranspiração de referência: quanto de água a atmosfera pede por dia (FAO-56)."],
  ["Ky", "Quanto a falta de água derruba o rendimento em cada fase da planta (FAO-33). Ky maior = mais sensível."],
  ["P10 e P90", "O pior ano em 10 (P10) e o melhor ano em 10 (P90): o valor que só 1 ano em 10 fica abaixo (ou acima)."],
  ["Percentil", "Posição do ano entre os anos passados do mesmo lugar. Percentil 0 = o mais seco de todos."],
  ["Spearman (rho)", "Correlação entre duas listas pela ordem. 1 = mesma ordem, 0 = nenhuma relação, -1 = ordem inversa."],
  ["Bootstrap", "Refazer a conta sorteando os anos com reposição, para medir a incerteza do número."],
  ["N1, N2, N3", "Nível de evidência. N3 validado, N2 com ressalva (sai com faixa), N1 em teste (só o nome), N0 fora."],
  ["Recall", "De todos os anos ruins, quantos o aviso pegou."],
  ["Ponto de silagem", "Quando o milho já somou 1.250 °C·dia desde o plantio e pode ser cortado para silagem. Na mensagem aparece como “corte da silagem”."],
  ["Quebra (Semiárido)", "Ano em que o rendimento simulado fica abaixo de 60% do potencial. Na mensagem: colher menos de 6 sacos em cada 10 possíveis."],
  ["Cenário (mistura com sorgo)", "Uma combinação de valores assumidos (Ky, Kc, razão sorgo/milho, data). A grade tem 270. “Ajudou em 7 de cada 10 cenários” = 7 em 10 mantiveram o ganho no ano ruim sem perder mais de 3% na média."],
  ["PAM", "Pesquisa Agrícola Municipal do IBGE. Só conferência."],
  ["POWER", "NASA POWER: chuva, temperatura e radiação por dia, numa grade de cerca de 50 km."],
  ["GAEZ", "Mapa mundial de aptidão agrícola da FAO. Aqui só dá a água que o solo guarda, por textura."],
  ["SRTM", "Relevo medido por radar da NASA, 30 m. Aqui só pede para confirmar o solo raso."],
  ["ATER", "Assistência técnica e extensão rural: o técnico que acompanha o produtor."],
  ["Parâmetro de literatura externa", "Valor que vem de norma ou publicação fora da aba Resources do desafio. É uma exceção declarada à regra de dados."],
  ["V1 a V7", "Frentes de validação feitas depois do loop. Cada uma tem relatório em validacao/Vn/relatorio.md."]
];
const SIGLAS = {
  "IC95": "Intervalo de confiança de 95%", ZARC: "Zoneamento Agrícola de Risco Climático (MAPA). Só conferência",
  CAD: "Capacidade de água disponível do solo, em mm", ISNA: "Índice de satisfação da necessidade de água",
  Ky: "Sensibilidade do rendimento à falta de água (FAO-33)", ET0: "Evapotranspiração de referência",
  PAM: "Pesquisa Agrícola Municipal (IBGE). Só conferência", POWER: "NASA POWER, grade de cerca de 50 km",
  SRTM: "Relevo medido por radar da NASA, 30 m", GAEZ: "Mapa de aptidão agrícola da FAO", ATER: "Assistência técnica e extensão rural",
  P10: "O pior ano em 10", P90: "O melhor ano em 10", Spearman: "Correlação pela ordem (1 igual, 0 nenhuma, -1 inversa)",
  decêndio: "Período de 10 dias", decêndios: "Períodos de 10 dias", "ponto de silagem": "Milho com 1.250 °C·dia, pronto para cortar", bootstrap: "Refazer a conta sorteando os anos", recall: "Quantos anos ruins o aviso pegou"
};
/* Texto seguro com siglas explicadas (abbr) e V1 a V7 ligadas ao relatório. */
function rico(txt) {
  let h = esc(txt);
  h = h.replace(/\bV([1-7])\b/g, (m, d) => `<a href="../validacao/V${d}/relatorio.md" target="_blank" rel="noopener" title="Relatório da frente V${d}">${m}</a>`);
  const chaves = Object.keys(SIGLAS).sort((a, b) => b.length - a.length).map((k) => k.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"));
  const re = new RegExp(`(?<![\\p{L}\\p{N}-])(${chaves.join("|")})(?![\\p{L}\\p{N}])`, "gu");
  return h.replace(re, (m) => `<abbr title="${esc(SIGLAS[m] || "")}">${m}</abbr>`);
}
const MESES = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"];

function esc(s) {
  return String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}
/* Número como veio do JSON, só com vírgula decimal. Sem arredondar. */
function n(v) {
  if (v === null || v === undefined) return "—";
  if (typeof v === "number") return String(v).replace(".", ",");
  return String(v);
}
function faixa(a) { return Array.isArray(a) ? `${n(a[0])} a ${n(a[1])}` : "—"; }
function dataBR(iso) {
  const m = /^(\d{4})-(\d{2})-(\d{2})/.exec(iso || "");
  return m ? `${m[3]}/${m[2]}/${m[1]}` : (iso || "—");
}
function valorInd(i) {
  switch (i.unidade) {
    case "pct": return `${n(i.valor)}%`;
    case "anos_em_10": return `${n(i.valor)} em 10 anos`;
    default: return n(i.valor);
  }
}

function lerParams() {
  const p = new URLSearchParams(location.search);
  return { local: p.get("local"), pergunta: p.get("pergunta") };
}
function acharLocal(slug) { return LOCAIS.find((l) => l.slug === slug) || LOCAIS[0]; }
function acharPergunta(loc, id) { return loc.perguntas.find((q) => q.id === id) || loc.perguntas[0]; }

/* Lê ../saida/<local>.json. Se não existir ou não for um contrato v2, cai para ../exemplo_saida.json. */
async function carregarSaida(slug) {
  const tentou = `../saida/${slug}.json`;
  let motivo = "arquivo não encontrado";
  try {
    const r = await fetch(tentou, { cache: "no-store" });
    if (r.ok) {
      const d = await r.json();
      if (d && d.versao_contrato && Array.isArray(d.cartoes) && Array.isArray(d.estrategias)) return { dados: d, exemplo: false, tentou, usou: tentou };
      motivo = "arquivo fora do contrato v2";
    }
  } catch (e) { motivo = "arquivo ilegível"; }
  const r2 = await fetch("../exemplo_saida.json", { cache: "no-store" });
  if (!r2.ok) throw new Error("Não achei ../exemplo_saida.json");
  return { dados: await r2.json(), exemplo: true, tentou, motivo, usou: "../exemplo_saida.json" };
}

/* JSON Pointer: devolve o valor e a cadeia de ancestrais. */
function resolver(doc, ptr) {
  const partes = String(ptr || "").split("/").slice(1).map((p) => p.replace(/~1/g, "/").replace(/~0/g, "~"));
  let cur = doc; const cadeia = [{ caminho: [], obj: doc }];
  for (let i = 0; i < partes.length; i++) {
    if (cur === null || cur === undefined) break;
    cur = cur[partes[i]];
    cadeia.push({ caminho: partes.slice(0, i + 1), obj: cur });
  }
  return { partes, valor: cur, cadeia };
}

/* Tema claro/escuro. O padrão segue o sistema; o botão força um dos dois. */
function temaAtual() {
  const f = document.documentElement.getAttribute("data-theme");
  if (f) return f;
  return window.matchMedia && matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
}
function iniciarTema() {
  try { const t = localStorage.getItem("fs-tema"); if (t === "dark" || t === "light") document.documentElement.setAttribute("data-theme", t); } catch (e) { /* sem armazenamento: segue o sistema */ }
}
function alternarTema() {
  const novo = temaAtual() === "dark" ? "light" : "dark";
  document.documentElement.setAttribute("data-theme", novo);
  try { localStorage.setItem("fs-tema", novo); } catch (e) { /* ok */ }
}
iniciarTema();
