"""Peças comuns para montar o JSON do contrato v2.1.0."""
import datetime as dt
import json
from . import config as C
from . import textos as T


def agora():
    return dt.datetime.now(dt.timezone(dt.timedelta(hours=-3))).replace(microsecond=0).isoformat()


# ------------------------------------------------------------------ rastro
def dado_power(id_, pw, descricao, variaveis):
    return dict(id=id_, tipo="dado", descricao=descricao, fonte=dict(
        nome="NASA_POWER", categoria="resources", variavel=variaveis,
        url=f"https://power.larc.nasa.gov/api/temporal/daily/point?community=AG&longitude={pw.lon}&latitude={pw.lat_grade}",
        periodo=pw.periodo, resolucao="~50 km", arquivo=C.rel(pw.caminho)))


def item(id_, tipo, descricao, nome, categoria, variavel=None, url=None, periodo=None, resolucao=None, arquivo=None):
    return dict(id=id_, tipo=tipo, descricao=descricao, fonte=dict(
        nome=nome, categoria=categoria, variavel=variavel, url=url, periodo=periodo, resolucao=resolucao,
        arquivo=None if arquivo is None else (arquivo if isinstance(arquivo, str) else C.rel(arquivo))))


def calculo(id_, descricao, script, funcao, parametros, entradas, arquivo_resultado, chave, periodo=None, variavel=None):
    it = item(id_, "calculo", descricao, "motor", "motor", variavel=variavel, periodo=periodo)
    it.update(script=dict(caminho=C.rel(script), funcao=funcao), parametros=parametros, entradas=entradas,
              resultado=dict(arquivo=C.rel(arquivo_resultado), chave=chave))
    return it


FAO56 = lambda: item("R-FAO56", "parametro", "Kc por fase, fator p e ET0 Penman-Monteith (FAO-56), coeficientes fixos.",
                     "FAO-56", "metodo_publicado", variavel="Kc, p, ET0")
FAO33 = lambda: item("R-FAO33", "parametro", "Ky por fase ou estágio (FAO-33), coeficientes fixos.",
                     "FAO-33", "metodo_publicado", variavel="Ky")
GAEZ = lambda arq: item("R-GAEZ-CAD", "parametro",
                        "Água disponível por textura do GAEZ v5: areia 65, médio 125, argila 175 mm/m.",
                        "GAEZ", "resources", variavel="água disponível por textura", arquivo=arq)


# Parâmetros de literatura externa: valores que entram no cálculo e NÃO vêm da aba Resources nem de FAO-56/33.
# São uma exceção à regra de dados. O time precisa aceitar ou trocar (README, "O que não foi validado").
def param_externo(id_, descricao, nome, variavel, url=None):
    return item(id_, "parametro", descricao, nome, "literatura_externa", variavel=variavel, url=url)


R_SORGO = lambda: param_externo(
    "R-PARAM-R-SORGO", "R = 0,88: a silagem do sorgo vale 88% da de milho. Vem da Embrapa Gado de Leite e de Demarchi (V3, seção 2.1). "
    "Não é da aba Resources. Se R cair abaixo de 0,77, a média da mistura cai.", "Embrapa", "R (silagem do sorgo / silagem do milho)")
RAIZ_RASO = lambda: param_externo(
    "R-PARAM-RAIZ-RASO", "Raiz de 0,6 m para o talhão raso. Valor do ZARC (Portaria 236 do MAPA), tirado nas frentes V3 e V6. "
    "Não é da aba Resources.", "ZARC", "profundidade de raiz do solo raso (m)")
LIMIAR_GEADA = lambda: param_externo(
    "R-PARAM-LIMIAR-GEADA", "Geada = temperatura mínima abaixo de 2 °C nas fases I a III do milho: critério do ZARC SC (Portaria 236 do MAPA). "
    "O ZARC também usa o POWER na ET0, então a concordância com ele não é independente (V6). Na mistura, o fator 0,3 de perda por geada vem da A4, sem fonte própria.",
    "ZARC", "limiar de T2M_MIN (°C)")


# ------------------------------------------------------------------ vírgula decimal (pt-BR)
_CAMPOS_TEXTO = {"descricao", "detalhe", "motivo", "resultado", "rotulo", "nota", "texto", "o_que", "nao_ve",
                 "premissas", "quebra_se", "nao_calculado", "nome"}


def _br(s):
    import re

    def troca(m):
        inteiro, frac = m.group(1), m.group(2)
        if inteiro.lstrip("-") != "0" and len(frac) == 3:  # 1.250 = milhar em pt-BR
            return m.group(0)
        return f"{inteiro},{frac}"
    return re.sub(r"(?<![\w/.])(-?\d+)\.(\d+)(?![\w/]|\.\w)", troca, s)


def virgula_decimal(doc):
    """Troca ponto decimal por vírgula nos campos de texto (não toca em números, ids, caminhos
    nem nos cartões, que são montados depois e não têm decimal)."""
    def andar(x, chave=None):
        if isinstance(x, dict):
            for k, v in x.items():
                if k in ("cartoes", "fonte", "script", "parametros", "resultado") and not isinstance(v, str):
                    if k != "resultado":
                        continue
                x[k] = andar(v, k)
            return x
        if isinstance(x, list):
            return [andar(v, chave) for v in x]
        if isinstance(x, str) and chave in _CAMPOS_TEXTO:
            return _br(x)
        return x
    andar(doc)
    return doc


# ------------------------------------------------------------------ ponteiros
class Ptr:
    def __init__(self, doc):
        self.doc = doc

    def _i(self, lista, id_, campo="id"):
        for i, x in enumerate(self.doc[lista] if isinstance(lista, str) else lista):
            if x[campo] == id_:
                return i
        raise KeyError(id_)

    def est(self, eid, *resto):
        return "/" + "/".join(["estrategias", str(self._i("estrategias", eid))] + [str(r) for r in resto])

    def ind(self, eid, iid, campo="valor", *resto):
        e = self.doc["estrategias"][self._i("estrategias", eid)]
        return self.est(eid, "indicadores", self._i(e["indicadores"], iid), campo, *resto)

    def linha(self, eid, dec, campo):
        e = self.doc["estrategias"][self._i("estrategias", eid)]
        return self.est(eid, "risco_por_decendio", "linhas", self._i(e["risco_por_decendio"]["linhas"], dec, "decendio"), campo)

    def alerta(self, aid, *resto):
        return "/" + "/".join(["alertas", str(self._i("alertas", aid))] + [str(r) for r in resto])

    def rastro(self, rid, *resto):
        return "/" + "/".join(["rastro", str(self._i("rastro", rid))] + [str(r) for r in resto])

    def valor(self, p):
        from .validador import ponteiro
        return ponteiro(self.doc, p)


# ------------------------------------------------------------------ cartões
def cartao(doc, id_, template_id, destino, ordem, variaveis, estrategia_ids=None, alerta_ids=None, imagem=None):
    """variaveis: {nome: (texto, ponteiro)}. O texto do cartão é montado pelo template."""
    ptr = Ptr(doc)
    vals = {k: ptr.valor(p) for k, (_, p) in variaveis.items()}
    textos = {k: t for k, (t, _) in variaveis.items()}
    texto = T.render(template_id, textos, vals)
    if template_id == "T01_COMPARA_ESTRATEGIAS" and "km" in variaveis and T.DADOS_SATELITE.format(km=variaveis["km"][0]) not in texto:
        # a frase dos dados de satélite só entra se couber em 70 palavras; se não coube, a variável sai
        variaveis = {k: v for k, v in variaveis.items() if k != "km"}
        textos.pop("km")
        vals.pop("km")
        texto = T.render(template_id, textos, vals)
    rot = T.roteiro(texto)
    c = dict(id=id_, template_id=template_id, destino=destino, ordem=ordem)
    if estrategia_ids:
        c["estrategia_ids"] = estrategia_ids
    if alerta_ids:
        c["alerta_ids"] = alerta_ids
    c.update(variaveis={k: dict(texto=t, ponteiro=p) for k, (t, p) in variaveis.items()}, texto=texto,
             palavras=T.palavras(texto), imagem=imagem or dict(tipo="nenhuma"),
             audio=dict(roteiro=rot, duracao_max_s=T.duracao_s(rot)))
    return c


def var(doc, ptr_, fmt):
    """(texto formatado, ponteiro) a partir do valor apontado."""
    v = Ptr(doc).valor(ptr_)
    return (fmt(v), ptr_)


def faixa(doc, ptr_ic, lo, hi, fmt=None):
    """Duas variáveis (lo, hi) do cartão a partir de um intervalo do documento (ex.: .../ic95)."""
    fmt = fmt or T.fmt_em10
    return {lo: var(doc, ptr_ic + "/0", fmt), hi: var(doc, ptr_ic + "/1", fmt)}


def dia_curto(dec):
    """'01/02' -> '1º/fev'."""
    d, m = int(dec[:2]), int(dec[3:5])
    return f"{'1º' if d == 1 else d}/{T.MESES[m - 1][:3]}"


def slug_talhao(nome):
    import unicodedata
    s = unicodedata.normalize("NFKD", nome.lower()).encode("ascii", "ignore").decode()
    s = "-".join("".join(ch if ch.isalnum() else " " for ch in s).split())
    return "T-" + s[:30]


SELO = {"N3": "validado", "N2": "com_ressalva", "N1": "em_teste", "N0": "em_teste"}


def saco(rotulo, em10_falha, nivel, atual=False):
    if em10_falha is None or nivel in ("N1", "N0"):
        return dict(rotulo=rotulo[:28], cheios=None, rasgados=None, selo="em_teste")
    r = T.arred(em10_falha)
    return dict(rotulo=rotulo[:28], cheios=10 - r, rasgados=r, selo="atual" if atual else SELO[nivel])


# ------------------------------------------------------------------ ordem pela prioridade (R9)
def ordenar(estrategias, prioridade, papel):
    """papel: {id: 'melhora_pior_ano' | 'mais_silagem' | 'mais_area' | 'solo' | 'atual' | 'outro'}.
    Só muda o campo 'ordem'. Nunca toca em número (R9)."""
    regras = {
        "silagem_garantida": ["melhora_pior_ano", "mais_silagem", "mais_area", "atual", "outro"],
        "renda": ["mais_area", "mais_silagem", "atual", "melhora_pior_ano", "outro"],
        "solo": ["solo", "atual", "melhora_pior_ano", "mais_silagem", "mais_area", "outro"],
    }
    base = sorted(estrategias, key=lambda e: e["id"])
    if prioridade in regras:
        seq = regras[prioridade]

        def chave(e):
            p = "solo" if prioridade == "solo" and e.get("solo_texto") else papel.get(e["id"], "outro")
            if e["nivel_evidencia"] in ("N1", "N0") and not e["e_atual"] and p != "solo":
                return (len(seq) + 1, e["id"])
            return (seq.index(p) if p in seq else len(seq), e["id"])
        base = sorted(base, key=chave)
    else:  # nao_informado: ordem do motor (as com número primeiro, em teste por último)
        base = sorted(base, key=lambda e: (e["nivel_evidencia"] in ("N1", "N0") and not e["e_atual"], e["id"]))
    for i, e in enumerate(base, 1):
        e["ordem"] = i


def gravar(doc, calculos, slug):
    C.SAIDA.mkdir(parents=True, exist_ok=True)
    C.CALCULOS.mkdir(parents=True, exist_ok=True)
    (C.SAIDA / f"{slug}.json").write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n")
    (C.CALCULOS / f"{slug}.json").write_text(json.dumps(calculos, ensure_ascii=False, indent=1, default=str) + "\n")
