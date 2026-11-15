"""Templates do WhatsApp (spec-v2 seção 6), arredondamento (R7) e roteiro de áudio.

O texto é sempre montado por código a partir das variáveis do cartão. O validador (R8)
remonta o texto com as mesmas funções e compara.
"""
import datetime as dt
import math
import re
from .estat import arred

MESES = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto",
         "setembro", "outubro", "novembro", "dezembro"]
POR_EXTENSO_QTD = {2: "Dois", 3: "Três", 4: "Quatro", 5: "Cinco"}


# ------------------------------------------------------------------ R7: formatos
def fmt_em10(v):
    """'x em 10': inteiro meio para cima; entre 0 e 0,5 'menos de 1'; zero 'quase nunca'."""
    if v == 0:
        return "quase nunca"
    if v < 0.5:
        return "menos de 1"
    return str(arred(v))


def fmt_pct(v):
    """Porcentagem inteira, sem sinal (o sinal vai na frase: 'X% a menos')."""
    return str(arred(abs(v)))


def fmt_frac_pct(v):
    return str(arred(abs(v) * 100))


def fmt_int(v):
    return str(int(v))


def fmt_dia_mes(s):
    """'05/02' -> '5 de fevereiro'; dia 1 -> '1º de ...'."""
    d, m = int(s[:2]), int(s[3:5])
    return f"{'1º' if d == 1 else d} de {MESES[m - 1]}"


def fmt_data_iso(s):
    d = dt.date.fromisoformat(s)
    return f"{'1º' if d.day == 1 else d.day} de {MESES[d.month - 1]}"


def fmt_data_limite(s):
    """'05/02' -> 'começo de fevereiro' (1-10), 'meados' (11-20), 'fim' (21-31)."""
    d, m = int(s[:2]), int(s[3:5])
    parte = "começo" if d <= 10 else ("meados" if d <= 20 else "fim")
    return f"{parte} de {MESES[m - 1]}"


def fmt_anos(lista):
    lista = [str(a) for a in lista]
    return lista[0] if len(lista) == 1 else ", ".join(lista[:-1]) + " e " + lista[-1]


def formatos(valor):
    """Todos os textos aceitos para um valor do documento (usado pelo verificador R8)."""
    out = set()
    if isinstance(valor, bool):
        return out
    if isinstance(valor, (int, float)):
        v = float(valor)
        if 0 <= v <= 10:
            out.add(fmt_em10(v))
        if 0 <= v <= 100:
            out.add(fmt_em10(v / 10))  # porcentagem lida como 'x em 10' (ex.: 67,4% de cenários = 7 em 10)
        out.add(fmt_pct(v))
        if abs(v) <= 1.5:
            out.add(fmt_frac_pct(v))
        if float(v).is_integer():
            out.add(fmt_int(v))
    elif isinstance(valor, str):
        out.add(valor)
        out.add(valor[:1].lower() + valor[1:])
        if re.fullmatch(r"\d{2}/\d{2}", valor):
            out.update({fmt_dia_mes(valor), fmt_data_limite(valor)})
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}", valor):
            out.add(fmt_data_iso(valor))
    elif isinstance(valor, list) and valor and all(isinstance(x, int) for x in valor):
        out.add(fmt_anos(valor))
    return out


# ------------------------------------------------------------------ frases auxiliares
LIMITE_PALAVRAS = 70
TECNICO = "Fale com o técnico da assistência técnica do seu município antes de decidir."
DADOS_SATELITE = "Dados de satélite, área de {km} km."


def _em_x_de_10(r, sufixo="de cada 10 anos"):
    """'em 4 de cada 10 anos' | 'em menos de 1 de cada 10 anos' | None (quase nunca)."""
    return None if r == "quase nunca" else f"em {r} {sufixo}"


def _faixa(t, lo="lo", hi="hi"):
    """' (entre 1 e 3)' a partir de duas variáveis 'x em 10'. Vazio se não houver faixa nas variáveis."""
    if lo not in t or hi not in t:
        return ""
    a, b = t[lo], t[hi]
    if a in ("quase nunca", "menos de 1"):
        return f" (no máximo {b})" if b not in ("quase nunca", "menos de 1") else ""
    if a == b:
        return f" (faixa estreita, perto de {a})"
    return f" (entre {a} e {b})"


def _frase_em10(r, t, lo="lo", hi="hi", verbo_zero="quase nunca"):
    """'em cerca de 2 de cada 10 anos (entre 1 e 3)' ou 'quase nunca'."""
    if r == "quase nunca":
        return verbo_zero
    pre = "em cerca de" if r != "menos de 1" else "em"
    return f"{pre} {r} de cada 10 anos{_faixa(t, lo, hi)}"


# ------------------------------------------------------------------ templates
# Cada renderizador recebe (t, v): t = textos das variáveis; v = valores apontados (para sinal).
def _lista_nomes(nomes):
    return nomes[0] if len(nomes) == 1 else ", ".join(nomes[:-1]) + " e " + nomes[-1]


def _t01(t, v):
    """Comparação de caminhos. Uma frase por caminho, na ordem da prioridade do produtor.
    Chaves por posição i: nome_i, e UMA destas: limite_i (+ r_i, lo_i, hi_i) | q_i (+ lo_i, hi_i, falado_i) |
    s_i | pct_i (+ meses_i) | falado_i. Sem nenhuma delas = caminho em teste, sem número."""
    itens, teste = [], []
    i = 1
    while f"nome_{i}" in t:
        nome = t[f"nome_{i}"]
        if f"limite_{i}" in t:
            g = _frase_em10(t[f"r_{i}"], t, f"lo_{i}", f"hi_{i}", "quase nunca")
            if t[f"r_{i}"] == "quase nunca":
                frase = f"plantando até {t[f'limite_{i}']}, a geada quase nunca chega antes do corte"
            else:
                frase = f"plantando até {t[f'limite_{i}']}, a geada chega antes do corte {g}"
            itens.append(f"{nome}: {frase}; não calculamos a falta de água.")
        elif f"q_{i}" in t:
            g = _frase_em10(t[f"q_{i}"], t, f"lo_{i}", f"hi_{i}", "quase nunca")
            rot = f"{nome} ({t[f'falado_{i}']})" if f"falado_{i}" in t else nome
            itens.append(f"{rot}: " + ("quebra quase nunca." if t[f"q_{i}"] == "quase nunca" else f"quebra {g}."))
        elif f"s_{i}" in t:
            itens.append(f"{nome}: ajudou em {t[f's_{i}']} de cada 10 cenários testados.")
        elif f"pct_{i}" in t:
            itens.append(f"{nome}: no último inverno, o solo ficou descoberto em {t[f'pct_{i}']}% dos dias de {t[f'meses_{i}']}.")
        elif f"falado_{i}" in t:
            itens.append(f"{nome}: {t[f'falado_{i}']}, sem número.")
        else:
            teste.append(nome)
        i += 1
    n = len(itens) + len(teste)
    txt = f"{POR_EXTENSO_QTD[n]} caminhos para a {t['talhao']}. " + " ".join(itens)
    if teste:
        txt += f" Em teste: {_lista_nomes([x[:1].lower() + x[1:] for x in teste])}."
    # frases opcionais, só se couberem em 70 palavras (a variável 'km' sai do cartão se a frase não entrou)
    if "km" in t and palavras(txt) + palavras(DADOS_SATELITE.format(km=t["km"])) <= LIMITE_PALAVRAS:
        txt += " " + DADOS_SATELITE.format(km=t["km"])
    if teste and palavras(txt) + palavras(TECNICO) <= LIMITE_PALAVRAS:
        txt += " " + TECNICO
    return txt


def _t02(t, v):
    seg = "quase nunca" if t["r_seguro"] == "quase nunca" else f"em {t['r_seguro']} de cada 10 anos"
    return (f"Milho de verão: aqui, não plante em agosto. Plantando em 1º de agosto, a geada pegou a lavoura nova "
            f"{_frase_em10(t['r_ago'], t, 'lo', 'hi', 'quase nunca')}. A partir de {t['data_segura']}, {seg}. "
            f"Do fim de setembro a dezembro, para o clima, a data quase não muda o risco.")


def _t03(t, v):
    return (f"Entre {t['de']} e {t['ate']}, para o clima, a data de plantio quase não muda o risco: a diferença é "
            f"menor que 1 ano em 10. Escolha pela mão de obra e pela máquina.")


def _t04(t, v):
    if t["r_lim"] == "quase nunca":
        ate = "a geada quase nunca chega antes do corte da silagem"
    else:
        ate = f"a geada chega antes do corte da silagem {_frase_em10(t['r_lim'], t, 'lo', 'hi')}"
    tarde = _frase_em10(t["r_tarde"], t, "lo_t", "hi_t", "quase nunca")
    return (f"Segundo milho (aveia não calculada): plante até {t['limite']}. Nesse dia, {ate}. "
            f"Em {t['data_tarde']}, {tarde}. Semente de ciclo longo (que demora mais): plante antes. "
            f"Não calculamos a falta de água. " + DADOS_SATELITE.format(km=t["km"]))


def _t05(t, v):
    return (f"Sim, este ano está seco. De {t['inicio']} a {t['fim']}, a água para o milho ficou entre os 10% piores "
            f"dos últimos {t['n_anos']} anos aqui. Não é certeza, e o aviso não pega todos os anos ruins. "
            f"Vale conferir o estoque de silagem e falar com o técnico da assistência técnica. "
            + DADOS_SATELITE.format(km=t["km"]))


def _t06(t, v):
    return (f"Ainda não. Até agora, a água para o milho está dentro do normal dos últimos {t['n_anos']} anos aqui. "
            f"Mas o aviso não pega todos os anos ruins: nos testes, ele deixou passar muitas quebras. "
            f"Continue de olho na lavoura. " + DADOS_SATELITE.format(km=t["km"]))


def _t07(t, v):
    ajuda = "pode ajudar" if v["s"] >= 50 else "pode não ajudar"
    return (f"Na {t['talhao']}, que você disse ser rasa: plantar metade da silagem com sorgo {ajuda} no ano ruim, "
            f"desses que vêm 1 vez a cada 10. A conta não é firme: a mistura ajudou em {t['s']} de cada 10 cenários "
            f"que testamos. Em ano bom, ela pode render um pouco menos. Fale com o técnico antes de decidir.")


def _t08(t, v):
    return (f"{t['nome']}: ainda estamos testando. Por enquanto não temos um número confiável para o seu lugar. "
            f"{TECNICO}")


def _t09(t, v):
    return (f"Cebola em {t['municipio']}. Nos últimos {t['n']} anos, as primaveras com mais chuva aqui foram "
            f"{t['anos']}. Chuva demais na formação do bulbo prejudica a cebola. Isso é o histórico do lugar, "
            f"calculado com dados de satélite. Não é previsão para este ano.")


def _t10(t, v):
    return (f"No último inverno, o solo do talhão {t['talhao']} ficou descoberto em {t['pct']}% dos dias de "
            f"{t['meses']}, quando a chuva já é forte. Palha ou cobertura nessa época protege o solo. Quanto solo "
            f"isso salva, ainda não medimos. A chuva é medida numa área de {t['km']} km.")


def _quebra(r, t, lo, hi):
    """'deu quebra em cerca de 4 de cada 10 anos (entre 3 e 6)' | 'quase nunca deu quebra'."""
    return "quase nunca deu quebra" if r == "quase nunca" else f"deu quebra {_frase_em10(r, t, lo, hi)}"


def _t11(t, v):
    return (f"Milho em {t['municipio']}. Na primeira chuva firme, {_quebra(t['q_atual'], t, 'lo_a', 'hi_a')}. "
            f"Plantando em {t['janela']}, {_quebra(t['q_janela'], t, 'lo_j', 'hi_j')}. "
            f"Só {t['n']} anos de dados: tende a ser melhor, mas não é certo. Se a chuva não firmar, espere. "
            f"Quebra é colher menos de 6 sacos em cada 10 possíveis.")


def _t12(t, v):
    return ("Para organizar as opções: o que pesa mais para você agora? Responda 1 para colheita mais segura, "
            "2 para renda, 3 para cuidar do solo.")


def _t13(t, v):
    return (f"Recebi a foto do talhão {t['talhao']}. Ela fica guardada como registro, com data e lugar. Eu não "
            f"analiso doença nem praga pela foto. Para isso, fale com o técnico.")


def _t14(t, v):
    return f"Isso eu não sei responder com segurança: {t['motivo']}. Vou avisar o técnico para falar com você."


def _t15(t, v):
    return (f"Para calcular, preciso saber como é a terra do talhão {t['talhao']}. Responda: 1 arenosa, 2 média, "
            f"3 argilosa, 4 rasa ou com pedra, 5 não sei.")


RENDER = {
    "T01_COMPARA_ESTRATEGIAS": _t01, "T02_GEADA_JANELA_SAFRA": _t02, "T03_TANTO_FAZ_DATA": _t03,
    "T04_GEADA_LIMITE_2A_SAFRA": _t04, "T05_ANO_SECO_ATIVO": _t05, "T06_ANO_SECO_SILENCIO": _t06,
    "T07_MISTURA_TALHAO_RASO": _t07, "T08_EM_TESTE": _t08, "T09_CEBOLA_HISTORICO": _t09,
    "T10_SOLO_EXPOSTO": _t10, "T11_SEMIARIDO_JANELA_MILHO": _t11, "T12_PRIORIDADE": _t12,
    "T13_FOTO_REGISTRO": _t13, "T14_NAO_SEI": _t14, "T15_PEDE_SOLO": _t15,
}

# Números que são do próprio template (regra R8): o "10" de "em 10", a numeração 1) a 5) e as
# opções de resposta. Qualquer outro número tem de vir de uma variável.
CONSTANTES = {
    "T01_COMPARA_ESTRATEGIAS": {"10"},
    "T02_GEADA_JANELA_SAFRA": {"1", "10"},
    "T03_TANTO_FAZ_DATA": {"1", "10"},
    "T04_GEADA_LIMITE_2A_SAFRA": {"10"},
    "T05_ANO_SECO_ATIVO": {"10"},
    "T06_ANO_SECO_SILENCIO": {"10"},
    "T07_MISTURA_TALHAO_RASO": {"1", "10"},
    "T11_SEMIARIDO_JANELA_MILHO": {"6", "10"},
    "T12_PRIORIDADE": {"1", "2", "3"},
    "T15_PEDE_SOLO": {"1", "2", "3", "4", "5"},
}


def render(template_id, textos, valores):
    return RENDER[template_id](textos, valores)


def numeros(texto):
    return re.findall(r"\d+(?:[.,]\d+)?", texto)


def palavras(texto):
    return len(texto.split())


# ------------------------------------------------------------------ áudio
_UN = ["zero", "um", "dois", "três", "quatro", "cinco", "seis", "sete", "oito", "nove", "dez", "onze", "doze",
       "treze", "catorze", "quinze", "dezesseis", "dezessete", "dezoito", "dezenove"]
_DZ = ["", "", "vinte", "trinta", "quarenta", "cinquenta", "sessenta", "setenta", "oitenta", "noventa"]
_CT = ["", "cento", "duzentos", "trezentos", "quatrocentos", "quinhentos", "seiscentos", "setecentos",
       "oitocentos", "novecentos"]
_FEM = {"um": "uma", "dois": "duas"}
_NOMES_FEM = {"regiões", "safras", "vez", "vezes", "semanas", "quebras"}


def extenso(n, fem=False):
    """Inteiro de 0 a 9999 por extenso (pt-BR)."""
    n = int(n)
    if n < 20:
        s = _UN[n]
        return _FEM.get(s, s) if fem else s
    if n < 100:
        d, u = divmod(n, 10)
        return _DZ[d] + ("" if u == 0 else " e " + extenso(u, fem))
    if n < 1000:
        if n == 100:
            return "cem"
        c, r = divmod(n, 100)
        return _CT[c] + ("" if r == 0 else " e " + extenso(r, fem))
    m, r = divmod(n, 1000)
    pre = "mil" if m == 1 else extenso(m) + " mil"
    if r == 0:
        return pre
    return pre + (" e " if r < 100 or r % 100 == 0 else " ") + extenso(r, fem)


def roteiro(texto):
    """Transforma o texto pronto em roteiro para o TTS: números por extenso, sem símbolos."""
    s = texto.replace("SC", "Santa Catarina").replace(" km", " quilômetros")
    s = re.sub(r"(?:(?<=^)|(?<=\s))(\d)\) ", lambda m: extenso(int(m.group(1))).capitalize() + ". ", s)
    s = re.sub(r"\b1º\b", "primeiro", s)
    s = s.replace("1º", "primeiro")
    s = re.sub(r"(\d+)%", lambda m: m.group(1) + " por cento", s)
    toks = s.split(" ")
    out = []
    for i, tk in enumerate(toks):
        m = re.fullmatch(r"(\(?)(\d+)([.,:;)]*)", tk)
        if m:
            seguinte = [re.sub(r"[^\wà-ú]", "", x) for x in toks[i + 1:i + 5]]
            fem = any(x in _NOMES_FEM for x in seguinte)
            out.append(m.group(1) + extenso(int(m.group(2)), fem) + m.group(3))
        else:
            out.append(tk)
    return " ".join(out)


def duracao_s(rot):
    """~2,4 palavras por segundo, arredondado para cima de 5 em 5 (5 a 40 s)."""
    return int(min(40, max(5, 5 * math.ceil(palavras(rot) / 2.4 / 5))))
