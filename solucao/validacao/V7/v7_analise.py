"""V7 · Aderência ao desafio e concorrentes.

Roda com: python3 -I v7_analise.py
Lê:
  - externo/desafio_texto.txt (página do desafio baixada com curl em 14/11/2026)
  - ../../../loop-validacao/sessoes/A1/ext/zarc_2627_smo_itu.csv e zarc_perene_smo_itu.csv (ZARC 2026/27, baixado pela A1)
Escreve:
  - resultado_v7.json
  - fig_v7_concorrentes.svg, fig_v7_criterios.svg, fig_v7_zarc_cobertura.svg

As matrizes de aderência e de concorrentes são codificadas à mão, cada célula com a fonte.
O script só conta, aplica os critérios de 00_criterios_antes.md e desenha.
"""
import csv
import collections
import json
import os
from xml.sax.saxutils import escape

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.abspath(os.path.join(AQUI, "..", "..", ".."))
ZARC_DIR = os.path.join(RAIZ, "loop-validacao", "sessoes", "A1", "ext")

# ---------------------------------------------------------------------------
# 0. Conferir que os trechos-chave estão mesmo na página baixada do desafio
# ---------------------------------------------------------------------------
TRECHOS = [
    "You may compare at least three rotation strategies, including the existing rotation",
    "why it was suggested, what evidence supports it, what benefits it may offer, where information gaps exist",
    "does not replace farmer judgment or local agricultural expertise",
    "frost risk",
    "times when fields are typically bare",
    "input their own priorities or constraints",
    "Explain how the model interprets uncertainty",
]
texto = open(os.path.join(AQUI, "externo", "desafio_texto.txt"), encoding="utf-8", errors="ignore").read()
texto_norm = texto.replace("‑", "-").replace("â\x80\x91", "-")
trechos_ok = {t: (t in texto_norm or t.replace("-", "") in texto_norm) for t in TRECHOS}

# ---------------------------------------------------------------------------
# 1. C1 · Aderência aos 7 itens centrais de "Objectives"
#    estado: "atende", "parcial", "nao"
# ---------------------------------------------------------------------------
ADERENCIA = [
    ("R1", "Combina observação da Terra da NASA com solo, cultura e prioridades do agricultor",
     "parcial",
     "POWER 40 anos + solo raso/fundo + Kc/Ky FAO entram (B3-3, A4-3). Não há pergunta de prioridade "
     "(silagem garantida, renda, solo) no fluxo do WhatsApp nem na spec."),
    ("R2", "Compara 3 ou mais estratégias de rotação, incluindo a atual",
     "parcial",
     "SMO tem 3 com número: atual (milho silagem → aveia), 2º milho após silagem até a data-limite de geada "
     "(B1-1) e mistura milho+sorgo no talhão raso (A4-3). Ituporanga não tem 3 estratégias de rotação "
     "testadas: B4 é regra de venda, A3-1 é erosão."),
    ("R3", "Diz por que cada estratégia foi sugerida",
     "atende",
     "Cada módulo gera o motivo (ex.: 'solo raso e pior ano em 10', 'geada depois de 1/fev'). Spec seção 3."),
    ("R4", "Mostra a evidência que apoia",
     "atende",
     "Frase com o histórico do ponto ('em 36 anos, 4 anos com ISNA < 0,75', B3-3) e o frontend de auditoria "
     "com anos, parâmetros e fontes (spec Q9)."),
    ("R5", "Mostra os benefícios",
     "parcial",
     "Benefício de produção existe (pior ano em 10 +0 a +14% com sorgo, A4-3). Benefício de solo (N, matéria "
     "orgânica, ciclo de praga) não é calculado; a spec marca como 'a validar'."),
    ("R6", "Mostra as lacunas de informação",
     "atende",
     "Seção 'quando o sistema diz não sei' (spec 7) e limites por ficha (grade de 50 km, solo informado)."),
    ("R7", "Mostra os riscos que pedem revisão local",
     "atende",
     "O frontend do técnico é a revisão local. Aviso quando a data sai da janela do ZARC (README do protótipo)."),
]

# itens secundários (Potential Considerations), sem nota no critério; só para o relatório
SECUNDARIOS = [
    ("Ferramenta apoia, não substitui", "atende", "Intermediário no circuito (spec Q2)."),
    ("Épocas de solo descoberto", "parcial", "A3-1 (erosão) passou com ajuste; B2-1 a B2-4 descartadas."),
    ("Risco de geada", "atende", "B1-1 aprovada; V2 replica em mais pontos."),
    ("Explicar a incerteza", "atende", "'x em 10 anos', faixa 0 a 14% (A4-3), n = 9 El Niños (A2-4)."),
    ("Prioridades e restrições como entrada", "nao", "Não desenhado."),
    ("Ciclo de nutrientes, praga, matéria orgânica", "nao", "Não calculado; só texto."),
    ("Mercado", "parcial", "B4-1/B4-3 (cebola), ajustar; preço é fonte externa."),
]

# ---------------------------------------------------------------------------
# 2. C2 · Conjuntos da aba Resources usados com dado real em módulos que passaram
# ---------------------------------------------------------------------------
MODULOS_PASSARAM = {
    "B3-3": ["NASA POWER"],
    "B1-1": ["NASA POWER"],
    "A4-3": ["NASA POWER"],
    "A3-1": ["NASA POWER", "Sentinel-2", "SRTM"],
    "B4-1": ["NASA POWER"],
    "B4-3": ["NASA POWER"],
    "A2-4": ["NASA POWER"],
}
NAO_USADOS = {
    "GPM IMERG": "pede login Earthdata; IMERG_PRECTOT do POWER veio vazio (PROTOCOLO.md)",
    "SMAP": "pede login Earthdata (PROTOCOLO.md)",
    "GLDAS": "pede login Earthdata",
    "ECOSTRESS": "não testado",
    "ERA5": "não usado; A2-4 pede ERA5 para trocar o ONI da NOAA",
    "Landsat": "não usado nos módulos que passaram",
    "MODIS": "usado em A5-3 e B5-1, ambos descartados",
    "FAO GAEZ": "só valores de tabela (água por textura), sem baixar camada",
}
usados = sorted({d for v in MODULOS_PASSARAM.values() for d in v})
usados_nasa = [d for d in usados if d in ("NASA POWER", "SRTM")]

# ---------------------------------------------------------------------------
# 3. C3 · Matriz de funções contra concorrentes que atendem SC
#    2 = faz; 1 = parcial; 0 = não faz (procurei e não achei); -1 = não verificado
# ---------------------------------------------------------------------------
CONCORRENTES = [
    "ZARC / Plantio Certo",
    "Epagri/Ciram (Agroconnect)",
    "INMET SISDAGRO",
    "Embrapa RAImundo",
    "CNA/Senar JoIA",
    "Plataformas privadas",
    "Apps de cooperativa",
    "Nossa solução",
]
# (funcao, [valores na ordem de CONCORRENTES], nota com a fonte)
FUNCOES = [
    ("Risco por cultura e data (probabilidade histórica)",
     [2, 1, 1, 0, 0, 0, -1, 2],
     "ZARC: risco 20/30/40% por decêndio (CSV A1). Ciram e SISDAGRO: balanço hídrico atual por estação. "
     "RAImundo/JoIA: não citado (Agrolink; CNA). Nossa: B3-3, A1-1."),
    ("3+ estratégias lado a lado, com a atual",
     [1, 0, 0, 0, 0, 0, -1, 2],
     "ZARC: uma cultura por vez; dá para consultar várias, sem comparar. Privadas: Agworld/EOSDA só registram "
     "(pesquisa-solucoes-atuais.md, 1.3). Nossa: desenho da spec."),
    ("Mistura de culturas por talhão (pior ano em 10)",
     [0, 0, 0, 0, 0, 0, -1, 1],
     "Não achei em nenhum. Nossa: A4-3 (ajustar)."),
    ("Data-limite do 2º milho por geada (sequência)",
     [1, 1, 0, 0, 0, 0, -1, 2],
     "ZARC SC não tem 'Milho 2ª Safra' (CSV A1) e corta o milho 1ª safra no fim de jan. Ciram: previsão de "
     "geada de curto prazo e 'possíveis geadas' no Agroconnect. Nossa: B1-1 (aprovada)."),
    ("Alerta de ano extremo com histórico do ponto",
     [0, 1, 1, 0, 0, 0, -1, 2],
     "Agroconnect: ISNA, déficit, % da chuva normal por estação. SISDAGRO: perda estimada. Nenhum diz "
     "'nesses anos quebrou x%'. Nossa: B3-3 (aprovada, fora da amostra)."),
    ("Filtro 'anos parecidos' (El Niño)",
     [0, 1, 0, 0, 0, 0, -1, 1],
     "Ciram publica nota de previsão climática trimestral (site, 28/10/2026). Nossa: A2-4 (ajustar)."),
    ("Alerta de doença (míldio da cebola)",
     [0, 2, 0, 1, 1, 1, -1, 0],
     "Agroconnect emite alerta de míldio (página baixada; B5-3). RAImundo/JoIA: dúvidas de praga e foto. "
     "Nossa: descartada (B5-3)."),
    ("Monitoramento por estação em tempo real",
     [0, 2, 2, 0, 1, 1, -1, 0],
     "Agroconnect (rede de estações) e SISDAGRO. JoIA: previsão de dias. Nossa: descartada (B5-2)."),
    ("Erosão / solo descoberto no talhão",
     [0, 0, 0, 0, 0, 1, -1, 1],
     "Privadas: NDVI Sentinel-2 (Aegro), sem índice de erosão. Nossa: A3-1 (ajustar)."),
    ("Preço da cebola ligado ao clima",
     [0, 1, 0, 0, 1, 0, -1, 1],
     "Cebola Net: preço diário. JoIA: cotações. Nenhum liga à chuva. Nossa: B4-1/B4-3 (ajustar)."),
    ("WhatsApp com áudio e foto",
     [0, 1, 0, 2, 2, 0, -1, 2],
     "RAImundo (Embrapa/MAPA/MDA, beta 2025) e JoIA (CNA, 25/08/2026, texto/áudio/foto, piloto com 10 mil). "
     "Ciram: grupo de WhatsApp no site."),
    ("Cada número ligado à fonte e aos anos (auditoria)",
     [1, 0, 0, 0, 0, 0, -1, 2],
     "ZARC: método e portarias públicos, CSV aberto, mas não por resposta. Bots de IA: não mostram a conta. "
     "Nossa: spec Q9 + frontend."),
    ("Ligado a crédito e seguro",
     [2, 0, 0, 0, 0, 0, -1, 0],
     "ZARC é exigido no crédito rural e no seguro (contexto.md, 7.2)."),
]
NOSSA = CONCORRENTES.index("Nossa solução")
diferenciais = []
for nome, vals, nota in FUNCOES:
    outros = [v for i, v in enumerate(vals) if i != NOSSA]
    if vals[NOSSA] >= 1 and max(outros) < 2:
        diferenciais.append({"funcao": nome, "nossa": vals[NOSSA], "melhor_concorrente": max(outros)})
dif_fortes = [d for d in diferenciais if d["nossa"] == 2]
canal_e_diferencial = not any(
    vals[i] == 2 for nome, vals, _ in FUNCOES if nome.startswith("WhatsApp") for i in range(len(vals)) if i != NOSSA
)

# ---------------------------------------------------------------------------
# 4. C4 · Perguntas prováveis do jurado
#    tem_numero: a resposta tem número de ficha/script (True) ou não (False)
# ---------------------------------------------------------------------------
PERGUNTAS = [
    ("O ZARC já faz isso. Por que vocês?", True, "A1-1: motor reproduz o ZARC em 94%; ZARC SC não tem milho 2ª safra; nada de mistura (V7)."),
    ("O modelo funciona em SC?", True, "B1-0: ρ = 0,28, igual à chuva bruta. Por isso só usamos extremos (B3-3)."),
    ("O alerta de ano extremo funciona fora da amostra?", True, "B3-3: milho 4 anos em 36, 2 com quebra > 15%; cebola 3 de 4."),
    ("Grade de 50 km para talhão pequeno?", True, "B5-2: alerta na safra a 50 km falhou; A2-4: células vizinhas com r de 0,76 a 0,97."),
    ("Isso é rotação ou só previsão de seca?", True, "SMO: 3 estratégias com número (B1-1, A4-3). Ituporanga ainda não."),
    ("Qual o tamanho do problema?", True, "Estiagem 2021/22: -43% do milho de SC (A1-1); cebola -55% em 2015 e -27,5% em 2023 (B3-2)."),
    ("Qual a incerteza?", True, "Faixa 0 a 14% (A4-3); n = 9 El Niños (A2-4); ±2-3 semanas (A5-1)."),
    ("Por que não alerta de míldio?", True, "B5-3: Agroconnect já faz; nosso índice ρ = 0,45 serve de contexto."),
    ("RAImundo e JoIA já estão no WhatsApp. E aí?", True, "JoIA: piloto com 10 mil produtores (CNA). Canal não é diferencial; o motor é."),
    ("Usaram dado de fora da NASA?", True, "IBGE, ZARC, Epagri só para conferir. Exceção a corrigir: ONI da NOAA em A2-4."),
    ("Funciona em outra região?", True, "Quixadá: 16 de 18 decêndios iguais ao ZARC (spec 6)."),
    ("O que muda no El Niño forte de 2026/27?", True, "A2-4: 9 El Niños, 1 out-jan seco e 6 chuvosos."),
    ("Cadê IMERG e SMAP? Só usaram POWER?", False, "Não usados (login Earthdata). Sem número que mostre ganho."),
    ("Testaram com agricultor ou técnico?", False, "Não. Só alcance: 50,5% dos estabelecimentos de SC com internet em 2017 (B5-2)."),
    ("O LLM pode inventar número?", False, "Por desenho, não: só transcreve e lê template (spec Q9). Sem teste medido."),
    ("Quanto o agricultor ganha em dinheiro?", False, "Só na cebola (B4-3: prejuízo de 6 para 2 anos). No leite não medido."),
    ("Usaram SI (IA) para ter a ideia?", False, "Regra do Space Apps proíbe. Precisa declarar onde a IA entrou e marcar áudio e imagem."),
]

# ---------------------------------------------------------------------------
# 5. Conferência externa: o que o ZARC já cobre (sequeiro) em SMO e Ituporanga
# ---------------------------------------------------------------------------
ALVO = ["Milho 1ª Safra", "Milho 2ª Safra", "Sorgo Forrageiro", "Sorgo Forrageiro 2ª Safra",
        "Aveia", "Milheto", "Trigo", "Cebola", "Feijão", "Soja"]
linhas = []
for fn in ("zarc_2627_smo_itu.csv", "zarc_perene_smo_itu.csv"):
    with open(os.path.join(ZARC_DIR, fn), encoding="utf-8-sig") as f:
        linhas += list(csv.DictReader(f, delimiter=";"))
culturas_por_mun = collections.defaultdict(set)
cont = collections.defaultdict(collections.Counter)
for x in linhas:
    culturas_por_mun[x["municipio"]].add(x["Nome_cultura"])
    if x["Nome_Outros_Manejos"] != "Sequeiro" or x["Nome_cultura"] not in ALVO:
        continue
    for i in range(1, 37):
        cont[(x["municipio"], x["Nome_cultura"])][x["dec%d" % i]] += 1
zarc = {}
for mun in ("São Miguel do Oeste", "Ituporanga"):
    zarc[mun] = {"n_culturas_total": len(culturas_por_mun[mun]), "culturas": {}}
    for c in ALVO:
        k = cont.get((mun, c))
        if not k:
            zarc[mun]["culturas"][c] = None
            continue
        ind = sum(v for r, v in k.items() if r != "0")
        zarc[mun]["culturas"][c] = {
            "celulas_indicadas": ind,
            "pct_risco_20": round(100 * k.get("20", 0) / ind, 1) if ind else None,
            "pct_risco_30": round(100 * k.get("30", 0) / ind, 1) if ind else None,
            "pct_risco_40": round(100 * k.get("40", 0) / ind, 1) if ind else None,
        }

# ---------------------------------------------------------------------------
# 6. Aplicar os critérios (00_criterios_antes.md)
# ---------------------------------------------------------------------------
n_atende = sum(1 for r in ADERENCIA if r[2] == "atende")
n_nao = sum(1 for r in ADERENCIA if r[2] == "nao")
n_resp = sum(1 for p in PERGUNTAS if p[1])
crit = {
    "C1": {"valor": n_atende, "meta": 5, "passa": n_nao == 0 and n_atende >= 5,
           "texto": f"{n_atende} de 7 'atende', {n_nao} 'não' (meta: 5 e nenhum 'não')"},
    "C2": {"valor": len(usados), "meta": 3, "passa": len(usados) >= 3,
           "texto": f"{len(usados)} conjuntos ({', '.join(usados)}); só da NASA: {len(usados_nasa)}"},
    "C3": {"valor": len(dif_fortes), "meta": 2, "passa": len(dif_fortes) >= 2,
           "texto": f"{len(dif_fortes)} funções que nenhum concorrente faz e nós fazemos; canal é diferencial: {canal_e_diferencial}"},
    "C4": {"valor": round(100 * n_resp / len(PERGUNTAS), 1), "meta": 80.0,
           "passa": n_resp / len(PERGUNTAS) >= 0.8,
           "texto": f"{n_resp} de {len(PERGUNTAS)} perguntas com número ({100 * n_resp / len(PERGUNTAS):.0f}%)"},
}
n_pass = sum(c["passa"] for c in crit.values())
veredito = "sustenta" if n_pass == 4 else ("parcial" if n_pass >= 2 else "nao_sustenta")

saida = {
    "trechos_do_desafio_conferidos": trechos_ok,
    "aderencia": [dict(zip(("id", "item", "estado", "prova"), r)) for r in ADERENCIA],
    "secundarios": [dict(zip(("item", "estado", "prova"), r)) for r in SECUNDARIOS],
    "dados_usados_em_modulos_aprovados": usados,
    "dados_nao_usados": NAO_USADOS,
    "funcoes": [{"funcao": n, "valores": dict(zip(CONCORRENTES, v)), "fonte": s} for n, v, s in FUNCOES],
    "diferenciais": diferenciais,
    "perguntas": [dict(zip(("pergunta", "tem_numero", "resposta"), p)) for p in PERGUNTAS],
    "zarc_cobertura": zarc,
    "criterios": crit,
    "criterios_passaram": n_pass,
    "veredito": veredito,
}
with open(os.path.join(AQUI, "resultado_v7.json"), "w", encoding="utf-8") as f:
    json.dump(saida, f, ensure_ascii=False, indent=2)

# ---------------------------------------------------------------------------
# 7. Gráficos (SVG). Paleta: rampa azul sequencial + texto em tinta neutra.
# ---------------------------------------------------------------------------
ESTILO = """
<style>
  .bg{fill:#fcfcfb}.t1{fill:#0b0b0b}.t2{fill:#52514e}.grid{stroke:#e4e3df}
  .v2{fill:#1c5cab}.v1{fill:#86b6ef}.v0{fill:#efeeea}.vq{fill:#ffffff;stroke:#c3c2b7;stroke-dasharray:3 2}
  .lv2{fill:#ffffff}.lv1{fill:#0b0b0b}.lv0{fill:#8a8984}.lvq{fill:#8a8984}
  .bar{fill:#2a78d6}.bar-off{fill:#86b6ef}.ref{stroke:#0b0b0b;stroke-width:1.5;stroke-dasharray:4 3}
  .nossa{fill:none;stroke:#0b0b0b;stroke-width:1.5}
  text{font-family:-apple-system,'Segoe UI',Roboto,Helvetica,Arial,sans-serif}
  @media (prefers-color-scheme: dark){
    .bg{fill:#1a1a19}.t1{fill:#f0efec}.t2{fill:#c3c2b7}.grid{stroke:#33332f}
    .v2{fill:#3987e5}.v1{fill:#1c5cab}.v0{fill:#2a2a28}.vq{fill:#1a1a19;stroke:#55554f}
    .lv2{fill:#0b0b0b}.lv1{fill:#f0efec}.lv0{fill:#8a8984}
    .bar{fill:#3987e5}.bar-off{fill:#1c5cab}.ref{stroke:#f0efec}.nossa{stroke:#f0efec}
  }
</style>"""
ROT = {2: "faz", 1: "parcial", 0: "—", -1: "?"}
CL = {2: "v2", 1: "v1", 0: "v0", -1: "vq"}
LC = {2: "lv2", 1: "lv1", 0: "lv0", -1: "lvq"}


def svg_concorrentes(path):
    rot_w, cw, ch, top = 330, 84, 30, 120
    w = rot_w + cw * len(CONCORRENTES) + 20
    h = top + ch * len(FUNCOES) + 70
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" '
         f'aria-label="Matriz de funções contra concorrentes em Santa Catarina">', ESTILO,
         f'<rect class="bg" width="{w}" height="{h}"/>',
         '<text class="t1" x="16" y="26" font-size="16" font-weight="600">Quem já faz o quê em SC</text>',
         '<text class="t2" x="16" y="46" font-size="12">Fonte de cada célula em resultado_v7.json. '
         '"?" = não verificado. Coluna com borda = nossa solução.</text>']
    for j, c in enumerate(CONCORRENTES):
        x = rot_w + j * cw + cw / 2
        partes = c.split(" ", 1) if len(c) > 12 else [c]
        for k, p in enumerate(partes):
            o.append(f'<text class="t1" x="{x}" y="{top - 30 + 14 * k}" font-size="11" text-anchor="middle"'
                     f'{" font-weight=\"600\"" if j == NOSSA else ""}>{escape(p)}</text>')
    for i, (nome, vals, nota) in enumerate(FUNCOES):
        y = top + i * ch
        o.append(f'<text class="t1" x="16" y="{y + ch / 2 + 4}" font-size="12">{escape(nome)}</text>')
        for j, v in enumerate(vals):
            x = rot_w + j * cw
            o.append(f'<g><title>{escape(CONCORRENTES[j])} · {escape(nome)}: {ROT[v]}. {escape(nota)}</title>'
                     f'<rect class="{CL[v]}" x="{x + 2}" y="{y + 2}" width="{cw - 4}" height="{ch - 4}" rx="4"/>'
                     f'<text class="{LC[v]}" x="{x + cw / 2}" y="{y + ch / 2 + 4}" font-size="11" '
                     f'text-anchor="middle">{ROT[v]}</text></g>')
    xn = rot_w + NOSSA * cw
    o.append(f'<rect class="nossa" x="{xn}" y="{top}" width="{cw}" height="{ch * len(FUNCOES)}" rx="5"/>')
    ly = top + ch * len(FUNCOES) + 30
    lx = 16
    for v in (2, 1, 0, -1):
        o.append(f'<rect class="{CL[v]}" x="{lx}" y="{ly - 11}" width="22" height="14" rx="3"/>'
                 f'<text class="t2" x="{lx + 28}" y="{ly}" font-size="11">'
                 f'{ {2: "faz", 1: "faz em parte", 0: "não achei", -1: "não verificado"}[v] }</text>')
        lx += 130
    o.append('<text class="t2" x="16" y="%d" font-size="11">Diferencial = linha onde nenhum concorrente "faz" e nós fazemos.</text>' % (ly + 22))
    o.append("</svg>")
    open(path, "w", encoding="utf-8").write("\n".join(o))


def svg_criterios(path):
    w, h = 760, 300
    x0, x1 = 240, 540  # 0% e 150% da meta
    esc = lambda p: x0 + (x1 - x0) * min(p, 150) / 150
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" '
         f'aria-label="Critérios da V7 em porcentagem da meta">', ESTILO,
         f'<rect class="bg" width="{w}" height="{h}"/>',
         '<text class="t1" x="16" y="26" font-size="16" font-weight="600">V7: cada critério contra a meta definida antes</text>',
         '<text class="t2" x="16" y="46" font-size="12">Barra = valor medido ÷ meta. A linha tracejada é a meta (100%).</text>']
    nomes = {"C1": "C1 Aderência (itens 'atende')", "C2": "C2 Conjuntos da aba usados",
             "C3": "C3 Funções sem concorrente", "C4": "C4 Perguntas com número"}
    for k, xg in ((0, 0), (50, 0), (100, 0), (150, 0)):
        xx = esc(k)
        o.append(f'<line class="grid" x1="{xx}" y1="70" x2="{xx}" y2="250"/>'
                 f'<text class="t2" x="{xx}" y="266" font-size="11" text-anchor="middle">{k}%</text>')
    for i, (cid, c) in enumerate(crit.items()):
        y = 80 + i * 42
        p = 100 * c["valor"] / c["meta"]
        cls = "bar" if c["passa"] else "bar-off"
        rot = {"C1": f'{c["valor"]} de 7 (meta 5)', "C2": f'{c["valor"]} (meta 3)',
               "C3": f'{c["valor"]} (meta 2)', "C4": f'{c["valor"]:.0f}% (meta 80%)'}[cid]
        o.append(f'<g><title>{escape(c["texto"])}</title>'
                 f'<text class="t1" x="16" y="{y + 15}" font-size="12">{escape(nomes[cid])}</text>'
                 f'<rect class="{cls}" x="{x0}" y="{y + 2}" width="{max(esc(p) - x0, 2)}" height="18" rx="4"/>'
                 f'<text class="t1" x="{x1 + 18}" y="{y + 15}" font-size="12">'
                 f'{rot} · {"passa" if c["passa"] else "não passa"}</text></g>')
    o.append(f'<line class="ref" x1="{esc(100)}" y1="70" x2="{esc(100)}" y2="250"/>')
    o.append(f'<text class="t2" x="16" y="288" font-size="11">Barra forte = passa; barra apagada = não passa. '
             f'Resultado: {n_pass} de 4 → {veredito}.</text>')
    o.append("</svg>")
    open(path, "w", encoding="utf-8").write("\n".join(o))


def svg_zarc(path):
    itens = []
    for mun, sig in (("São Miguel do Oeste", "SMO"), ("Ituporanga", "Itu")):
        for c in ("Milho 1ª Safra", "Milho 2ª Safra", "Sorgo Forrageiro", "Aveia", "Cebola"):
            itens.append((f"{sig} · {c}", zarc[mun]["culturas"].get(c)))
    w, ch, top = 720, 28, 80
    h = top + ch * len(itens) + 60
    x0, x1 = 230, 640
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" '
         f'aria-label="Parte das janelas do ZARC com risco de 20%">', ESTILO,
         f'<rect class="bg" width="{w}" height="{h}"/>',
         '<text class="t1" x="16" y="26" font-size="16" font-weight="600">O ZARC já tem janela para quase toda a rotação, menos o 2º milho</text>',
         '<text class="t2" x="16" y="46" font-size="12">% das combinações decêndio × solo × ciclo indicadas (sequeiro, 2026/27) '
         'com risco de 20%, o menor do ZARC.</text>']
    for k in (0, 25, 50, 75, 100):
        xx = x0 + (x1 - x0) * k / 100
        o.append(f'<line class="grid" x1="{xx}" y1="{top - 6}" x2="{xx}" y2="{top + ch * len(itens)}"/>'
                 f'<text class="t2" x="{xx}" y="{top + ch * len(itens) + 16}" font-size="11" text-anchor="middle">{k}%</text>')
    for i, (nome, d) in enumerate(itens):
        y = top + i * ch
        o.append(f'<text class="t1" x="16" y="{y + 17}" font-size="12">{escape(nome)}</text>')
        if d is None:
            o.append(f'<text class="t2" x="{x0 + 4}" y="{y + 17}" font-size="11">sem zoneamento em SC</text>')
            continue
        p = d["pct_risco_20"]
        xx = x0 + (x1 - x0) * p / 100
        o.append(f'<g><title>{escape(nome)}: {d["celulas_indicadas"]} combinações indicadas; '
                 f'20%: {p}%, 30%: {d["pct_risco_30"]}%, 40%: {d["pct_risco_40"]}%</title>'
                 f'<rect class="bar" x="{x0}" y="{y + 5}" width="{max(xx - x0, 2)}" height="16" rx="4"/>'
                 f'<text class="t1" x="{xx + 6}" y="{y + 17}" font-size="11">{p:.0f}%</text></g>')
    o.append(f'<text class="t2" x="16" y="{h - 14}" font-size="11">Fonte: tábua de risco ZARC 2026/27 (MAPA), '
             f'recorte da A1 em loop-validacao/sessoes/A1/ext/. Só para conferir; não entra na solução.</text>')
    o.append("</svg>")
    open(path, "w", encoding="utf-8").write("\n".join(o))


svg_concorrentes(os.path.join(AQUI, "fig_v7_concorrentes.svg"))
svg_criterios(os.path.join(AQUI, "fig_v7_criterios.svg"))
svg_zarc(os.path.join(AQUI, "fig_v7_zarc_cobertura.svg"))

print(json.dumps({"trechos": trechos_ok, "criterios": crit, "veredito": veredito,
                  "diferenciais": diferenciais, "zarc": zarc}, ensure_ascii=False, indent=1))
