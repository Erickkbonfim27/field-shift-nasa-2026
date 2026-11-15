"""Validador do contrato v2.1.0: JSON Schema (subconjunto de 2020-12) + regras R1 a R15.

O pacote `jsonschema` não está instalado nesta máquina; este validador cobre só as palavras do
schema que o contrato usa: $ref local, type, enum, const, pattern, required, properties,
additionalProperties, propertyNames, items, minItems, maxItems, minimum, maximum,
exclusiveMinimum, minLength, maxLength, oneOf, anyOf, allOf, if/then/else. `format` é ignorado.
Uso: python3 solucao/motor/validador.py <arquivo.json> [...]
"""
import re
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from motor import textos as T
    from motor import config as C
    from motor import documento as D
else:
    from . import textos as T
    from . import config as C
    from . import documento as D

TIPOS = {
    "object": lambda x: isinstance(x, dict),
    "array": lambda x: isinstance(x, list),
    "string": lambda x: isinstance(x, str),
    "integer": lambda x: isinstance(x, int) and not isinstance(x, bool),
    "number": lambda x: isinstance(x, (int, float)) and not isinstance(x, bool),
    "boolean": lambda x: isinstance(x, bool),
    "null": lambda x: x is None,
}
CONHECIDAS = {"$schema", "$id", "title", "description", "type", "enum", "const", "pattern", "required",
              "properties", "additionalProperties", "propertyNames", "items", "minItems", "maxItems",
              "minimum", "maximum", "exclusiveMinimum", "minLength", "maxLength", "oneOf", "anyOf", "allOf",
              "if", "then", "else", "$ref", "$defs", "format"}


class Schema:
    def __init__(self, schema):
        self.raiz = schema

    def resolver(self, ref):
        if not ref.startswith("#/"):
            raise ValueError(f"$ref não suportado: {ref}")
        no = self.raiz
        for p in ref[2:].split("/"):
            no = no[p.replace("~1", "/").replace("~0", "~")]
        return no

    def erros(self, x, s=None, caminho=""):
        s = self.raiz if s is None else s
        out = []
        desconhecidas = set(s) - CONHECIDAS
        if desconhecidas:
            raise ValueError(f"palavra do schema não suportada em {caminho}: {desconhecidas}")
        if "$ref" in s:
            out += self.erros(x, self.resolver(s["$ref"]), caminho)
        if "type" in s:
            ts = s["type"] if isinstance(s["type"], list) else [s["type"]]
            if not any(TIPOS[t](x) for t in ts):
                return out + [f"{caminho or '/'}: tipo {type(x).__name__}, esperado {ts}"]
        if "enum" in s and not any(_igual(x, e) for e in s["enum"]):
            out.append(f"{caminho}: {x!r} fora do enum")
        if "const" in s and not _igual(x, s["const"]):
            out.append(f"{caminho}: {x!r} != const {s['const']!r}")
        if isinstance(x, str):
            if "pattern" in s and not re.search(s["pattern"], x):
                out.append(f"{caminho}: {x!r} não casa com {s['pattern']}")
            if "maxLength" in s and len(x) > s["maxLength"]:
                out.append(f"{caminho}: texto com {len(x)} > {s['maxLength']} caracteres")
            if "minLength" in s and len(x) < s["minLength"]:
                out.append(f"{caminho}: texto curto")
        if TIPOS["number"](x):
            if "minimum" in s and x < s["minimum"]:
                out.append(f"{caminho}: {x} < mínimo {s['minimum']}")
            if "maximum" in s and x > s["maximum"]:
                out.append(f"{caminho}: {x} > máximo {s['maximum']}")
            if "exclusiveMinimum" in s and x <= s["exclusiveMinimum"]:
                out.append(f"{caminho}: {x} <= {s['exclusiveMinimum']}")
        if isinstance(x, list):
            if "minItems" in s and len(x) < s["minItems"]:
                out.append(f"{caminho}: {len(x)} itens < {s['minItems']}")
            if "maxItems" in s and len(x) > s["maxItems"]:
                out.append(f"{caminho}: {len(x)} itens > {s['maxItems']}")
            if "items" in s:
                for i, it in enumerate(x):
                    out += self.erros(it, s["items"], f"{caminho}/{i}")
        if isinstance(x, dict):
            for r in s.get("required", []):
                if r not in x:
                    out.append(f"{caminho}: falta '{r}'")
            props = s.get("properties", {})
            for k, v in x.items():
                if "propertyNames" in s:
                    out += self.erros(k, s["propertyNames"], f"{caminho}/<nome {k}>")
                if k in props:
                    out += self.erros(v, props[k], f"{caminho}/{k}")
                elif "additionalProperties" in s:
                    ap = s["additionalProperties"]
                    if ap is False:
                        out.append(f"{caminho}: propriedade não permitida '{k}'")
                    elif isinstance(ap, dict):
                        out += self.erros(v, ap, f"{caminho}/{k}")
        if "allOf" in s:
            for sub in s["allOf"]:
                out += self.erros(x, sub, caminho)
        if "anyOf" in s and not any(not self.erros(x, sub, caminho) for sub in s["anyOf"]):
            out.append(f"{caminho}: nenhum anyOf casa")
        if "oneOf" in s:
            n = sum(1 for sub in s["oneOf"] if not self.erros(x, sub, caminho))
            if n != 1:
                out.append(f"{caminho}: oneOf casou {n} vezes")
        if "if" in s:
            if not self.erros(x, s["if"], caminho):
                if "then" in s:
                    out += self.erros(x, s["then"], caminho)
            elif "else" in s:
                out += self.erros(x, s["else"], caminho)
        return out


def _igual(a, b):
    if isinstance(a, bool) or isinstance(b, bool):
        return a is b
    return a == b


def carregar_schema():
    return Schema(C.ler_json(C.SCHEMA))


# ====================================================================== regras R1-R15
def ponteiro(doc, p):
    """Resolve JSON Pointer (RFC 6901). Levanta KeyError/IndexError se não existir."""
    no = doc
    for parte in p.lstrip("/").split("/") if p != "/" else []:
        parte = parte.replace("~1", "/").replace("~0", "~")
        no = no[int(parte)] if isinstance(no, list) else no[parte]
    return no


def _ancestrais(doc, p):
    no = doc
    out = [no]
    for parte in p.lstrip("/").split("/"):
        no = no[int(parte)] if isinstance(no, list) else no[parte]
        out.append(no)
    return out


def _rastro_do_ponteiro(doc, p):
    """Ids de rastro que sustentam o valor apontado: o item de rastro, se o ponteiro cai dentro dele, e
    os campos 'rastro' (lista de ids) de todos os nós do caminho."""
    partes = p.lstrip("/").split("/")
    ids = []
    if partes[0] == "rastro":
        ids.append(doc["rastro"][int(partes[1])]["id"])
    for no in _ancestrais(doc, p):
        if isinstance(no, dict) and isinstance(no.get("rastro"), list) and all(isinstance(x, str) for x in no["rastro"]):
            ids += no["rastro"]
    return ids


def _refs_rastro(doc):
    """Todos os ids de rastro citados no documento (fora de /rastro/*/id)."""
    achados = []

    def andar(x, cam):
        if isinstance(x, dict):
            for k, v in x.items():
                if k in ("rastro", "entradas") and isinstance(v, list):
                    if all(isinstance(i, str) for i in v):
                        achados.extend((cam + "/" + k, i) for i in v)
                        continue
                andar(v, cam + "/" + k)
        elif isinstance(x, list):
            for i, v in enumerate(x):
                andar(v, f"{cam}/{i}")

    for k, v in doc.items():
        if k == "rastro":
            for i, it in enumerate(v):
                for e in it.get("entradas", []):
                    achados.append((f"/rastro/{i}/entradas", e))
        else:
            andar(v, "/" + k)
    return achados


def _intervalos(doc):
    out = []

    def andar(x, cam):
        if isinstance(x, dict):
            for k, v in x.items():
                if k in ("ic95", "faixa_parametros", "faixa") and isinstance(v, list) and len(v) == 2:
                    out.append((cam + "/" + k, v))
                else:
                    andar(v, cam + "/" + k)
        elif isinstance(x, list):
            for i, v in enumerate(x):
                andar(v, f"{cam}/{i}")
    andar(doc, "")
    return out


NIVEL_MOSTRAR = {"N3": {"com_numero", "com_faixa"}, "N2": {"com_faixa"}, "N1": {"so_nome_em_teste"}, "N0": {"oculto"}}


def regras(doc, r8_estrito=True, checar_arquivos=False):
    """Devolve lista de erros 'Rn: ...'. r8_estrito=False só confere os números soltos
    (usado no exemplo escrito à mão). checar_arquivos=True confere se scripts e arquivos do
    rastro existem no projeto."""
    E = []
    rastro = {it["id"]: it for it in doc.get("rastro", [])}
    # ---------------- R1: ids e ponteiros existem
    ids = [it["id"] for it in doc.get("rastro", [])]
    if len(ids) != len(set(ids)):
        E.append("R1: ids de rastro repetidos")
    for cam, i in _refs_rastro(doc):
        if i not in rastro:
            E.append(f"R1: {cam} cita {i}, que não existe em /rastro")
    est_ids = {e["id"] for e in doc["estrategias"]}
    al_ids = {a["id"] for a in doc["alertas"]}
    for c in doc["cartoes"]:
        for e in c.get("estrategia_ids", []):
            if e not in est_ids:
                E.append(f"R1: {c['id']} cita estratégia {e} inexistente")
        for a in c.get("alerta_ids", []):
            if a not in al_ids:
                E.append(f"R1: {c['id']} cita alerta {a} inexistente")
        for nome, var in c["variaveis"].items():
            try:
                ponteiro(doc, var["ponteiro"])
            except (KeyError, IndexError, ValueError, TypeError):
                E.append(f"R1: {c['id']}.{nome} aponta para {var['ponteiro']}, que não existe")
    for lim in doc["limites"]:
        for a in lim["afeta"]:
            if a not in est_ids | al_ids | {c["id"] for c in doc["cartoes"]} | {m["id"] for m in doc["modulos"]}:
                E.append(f"R1: limite {lim['id']} afeta {a}, que não existe")
    if checar_arquivos:
        for it in doc["rastro"]:
            for p in [it.get("script", {}).get("caminho"), it.get("resultado", {}).get("arquivo"), it["fonte"].get("arquivo")]:
                if p and not (C.RAIZ / p).exists():
                    E.append(f"R1: {it['id']} cita o arquivo {p}, que não existe no projeto")
    # ---------------- R2: fonte externa nunca entra num cálculo do produto
    # (a) nenhum cálculo do produto tem fonte externa nas entradas, direta ou indireta. Os cálculos de
    #     validação (parametros.so_auditoria = true) são a única exceção declarada.
    # (b) nenhuma variável de cartão do WhatsApp chega, pelos ponteiros, a uma fonte externa nem a um cálculo
    #     de validação. Isso vale também para o que o produtor lê: o número não pode vir do IBGE nem do ZARC.
    def fecho(i, vistos):
        for e in rastro.get(i, {}).get("entradas", []):
            if e not in vistos:
                vistos.add(e)
                fecho(e, vistos)
        return vistos

    def so_auditoria(it):
        return it["tipo"] == "calculo" and (it.get("parametros") or {}).get("so_auditoria") is True

    def externo(e):
        return e in rastro and rastro[e]["fonte"]["categoria"] == "externo_conferencia"
    for i, it in rastro.items():
        if it["tipo"] != "calculo" or so_auditoria(it):
            continue
        for e in fecho(i, set()):
            if externo(e):
                E.append(f"R2: o cálculo {i} usa a fonte externa {e} como entrada")
            elif e in rastro and so_auditoria(rastro[e]):
                E.append(f"R2: o cálculo {i} usa o cálculo de validação {e} como entrada")
    for it in rastro.values():
        if it["fonte"]["categoria"] == "externo_conferencia" and it["tipo"] != "conferencia":
            E.append(f"R2: {it['id']} é externo e não é conferência")
        if it["fonte"]["categoria"] == "literatura_externa" and it["tipo"] != "parametro":
            E.append(f"R2: {it['id']} é de literatura externa e não é parâmetro")
    for c in doc["cartoes"]:
        if c["destino"] != "whatsapp":
            continue
        for nome, var in c["variaveis"].items():
            try:
                ids = _rastro_do_ponteiro(doc, var["ponteiro"])
            except (KeyError, IndexError, ValueError, TypeError):
                continue
            alcance = set()
            for i in ids:
                alcance |= {i} | fecho(i, set())
            for e in sorted(alcance):
                if externo(e) or (e in rastro and so_auditoria(rastro[e])):
                    E.append(f"R2: {c['id']}.{nome} chega à fonte de conferência ou validação {e} pelo rastro de {var['ponteiro']}")
    # ---------------- R3
    n_atual = sum(1 for e in doc["estrategias"] if e["e_atual"])
    if n_atual != 1:
        E.append(f"R3: {n_atual} estratégias com e_atual = true (precisa ser 1)")
    # ---------------- R4
    for e in doc["estrategias"]:
        if e["como_mostrar"] not in NIVEL_MOSTRAR[e["nivel_evidencia"]]:
            E.append(f"R4: {e['id']} é {e['nivel_evidencia']} e está como {e['como_mostrar']}")
    for c in doc["cartoes"]:
        if c["destino"] != "whatsapp":
            continue
        for nome, var in c["variaveis"].items():
            if not re.search(r"\d", var["texto"]):
                continue
            try:
                for no in _ancestrais(doc, var["ponteiro"]):
                    if isinstance(no, dict) and no.get("nivel_evidencia") in ("N1", "N0"):
                        E.append(f"R4: {c['id']}.{nome} leva número de um item {no['nivel_evidencia']} ao WhatsApp")
                        break
            except (KeyError, IndexError, ValueError):
                pass
    # ---------------- R4b: número N2 com intervalo traz a faixa no mesmo cartão
    for c in doc["cartoes"]:
        if c["destino"] != "whatsapp":
            continue
        ptrs = [v["ponteiro"] for v in c["variaveis"].values()]
        for nome, var in c["variaveis"].items():
            partes = var["ponteiro"].lstrip("/").split("/")
            if not re.search(r"\d", var["texto"]) or partes[-1] not in ("valor", "em10"):
                continue
            try:
                anc = _ancestrais(doc, var["ponteiro"])
            except (KeyError, IndexError, ValueError):
                continue
            pai = anc[-2]
            if not (isinstance(pai, dict) and (pai.get("ic95") or pai.get("faixa_parametros"))):
                continue
            nivel = next((n["nivel_evidencia"] for n in reversed(anc) if isinstance(n, dict) and "nivel_evidencia" in n), None)
            base = "/" + "/".join(partes[:-1])
            if nivel == "N2" and not any(q.startswith(base + "/ic95") or q.startswith(base + "/faixa_parametros") for q in ptrs):
                E.append(f"R4: {c['id']}.{nome} é N2 com intervalo ({base}) e o cartão não traz a faixa")
    # ---------------- R5
    for cam, (a, b) in _intervalos(doc):
        if a is not None and b is not None and a > b:
            E.append(f"R5: {cam} tem inferior {a} > superior {b}")
    # ---------------- R6
    safra0 = int(doc["safra"][:4])
    for a in doc["alertas"]:
        pl = a["percentil_local"]
        ini, fim = int(pl["periodo_passado"][:4]), int(pl["periodo_passado"][5:])
        if fim > safra0:
            E.append(f"R6: {a['id']} usa anos até {fim}, depois do início da safra {doc['safra']}")
        if pl["n_anos_passados"] > fim - ini + 1:
            E.append(f"R6: {a['id']} diz {pl['n_anos_passados']} anos num período de {fim - ini + 1}")
    # ---------------- R7 (sacos)
    for c in doc["cartoes"]:
        for l in c["imagem"].get("linhas", []):
            ch, ra = l["cheios"], l["rasgados"]
            if (ch is None) != (ra is None):
                E.append(f"R7: {c['id']} linha '{l['rotulo']}' com só um de cheios/rasgados")
            elif ch is not None and ch + ra != 10:
                E.append(f"R7: {c['id']} linha '{l['rotulo']}' tem {ch} + {ra} != 10 sacos")
            if l["selo"] == "em_teste" and ch is not None:
                E.append(f"R7: {c['id']} linha '{l['rotulo']}' em teste com sacos")
    # ---------------- R7b: o número de cada saco rasgado aparece no texto do cartão (mesma polaridade)
    for c in doc["cartoes"]:
        nums = {int(x) for v in c["variaveis"].values() for x in re.findall(r"\d+", v["texto"])}
        for l in c["imagem"].get("linhas", []):
            if l["rasgados"] and l["rasgados"] not in nums:
                E.append(f"R7: {c['id']} linha '{l['rotulo']}' tem {l['rasgados']} sacos rasgados e o texto não diz esse número")
    # ---------------- R8 (números do texto)
    for c in doc["cartoes"]:
        tid = c["template_id"]
        sobra = T.numeros(c["texto"])
        for var in c["variaveis"].values():
            for n in T.numeros(var["texto"]):
                if n in sobra:
                    sobra.remove(n)
        soltos = [n for n in sobra if n not in T.CONSTANTES.get(tid, set())]
        if soltos:
            E.append(f"R8: {c['id']} tem números sem variável: {soltos}")
        if not r8_estrito:
            continue
        valores = {}
        for nome, var in c["variaveis"].items():
            try:
                v = ponteiro(doc, var["ponteiro"])
            except (KeyError, IndexError, ValueError):
                continue
            valores[nome] = v
            if re.search(r"\d", var["texto"]) or isinstance(v, (int, float)):
                ok = var["texto"] in T.formatos(v) or (isinstance(v, str) and var["texto"] in v)
                if not ok:
                    E.append(f"R8: {c['id']}.{nome} = '{var['texto']}' não é formato de {v!r} ({var['ponteiro']})")
        try:
            esperado = T.render(tid, {k: v["texto"] for k, v in c["variaveis"].items()}, valores)
        except (KeyError, TypeError) as ex:
            E.append(f"R8: {c['id']} não remonta pelo template {tid} ({ex})")
            continue
        if esperado != c["texto"]:
            E.append(f"R8: {c['id']} texto difere do template preenchido")
    # ---------------- R9: só a ordem muda com a prioridade (conferido em teste, gerando duas vezes)
    ordens = [e["ordem"] for e in doc["estrategias"]]
    if sorted(ordens) != list(range(1, len(ordens) + 1)):
        E.append(f"R9: ordens das estratégias não são 1..n: {ordens}")
    # ---------------- R10
    ativos = sorted(m["id"] for m in doc["modulos"] if m["ativo"])
    if sorted(doc["regiao"]["modulos_ativos"]) != ativos:
        E.append(f"R10: modulos_ativos {doc['regiao']['modulos_ativos']} != módulos ativos {ativos}")
    # ---------------- R11
    for c in doc["cartoes"]:
        n = T.palavras(c["texto"])
        if c["palavras"] != n:
            E.append(f"R11: {c['id']} declara {c['palavras']} palavras, tem {n}")
        if n > 70:
            E.append(f"R11: {c['id']} tem {n} palavras (máximo 70)")
    # ---------------- R12
    if not doc["local"]["dentro_da_area_testada"]:
        if not doc["nao_sei"]["ativo"]:
            E.append("R12: fora da área testada sem nao_sei.ativo")
        for c in doc["cartoes"]:
            if re.search(r"\d", c["texto"]) and c["template_id"] not in ("T12_PRIORIDADE", "T15_PEDE_SOLO"):
                E.append(f"R12: fora da área, {c['id']} tem número")
    # ---------------- R13: vírgula decimal nos textos de módulos, estratégias, limites e conferências
    def decimais(x, cam, chave=None):
        if isinstance(x, dict):
            for k, v in x.items():
                if k in ("cartoes", "fonte", "script", "parametros"):
                    continue
                decimais(v, f"{cam}/{k}", k)
        elif isinstance(x, list):
            for i, v in enumerate(x):
                decimais(v, f"{cam}/{i}", chave)
        elif isinstance(x, str) and chave in D._CAMPOS_TEXTO and D._br(x) != x:
            E.append(f"R13: {cam} tem ponto decimal em vez de vírgula: {x[:70]!r}")
    decimais(doc, "")
    # ---------------- R14: limite que vai ao produtor tem o trecho num cartão do WhatsApp
    textos_wa = [c["texto"] for c in doc["cartoes"] if c["destino"] == "whatsapp"]
    for lim in doc["limites"]:
        if lim["mostrar_ao_agricultor"]:
            tr = lim.get("trecho")
            if not tr:
                E.append(f"R14: o limite {lim['id']} vai ao produtor e não tem 'trecho'")
            elif not any(tr in t for t in textos_wa):
                E.append(f"R14: o trecho do limite {lim['id']} não aparece em nenhum cartão do WhatsApp: {tr!r}")
    # ---------------- R15: o fim da janela do alerta é o fim que o índice usou
    for a in doc["alertas"]:
        if a["estado"] in ("ativo", "inativo"):
            ate = a["janela"]["ate"]
            dm = f"{ate[8:10]}/{ate[5:7]}"
            if dm not in a["indice"]["nome"]:
                E.append(f"R15: {a['id']} diz que a janela vai até {ate}, mas o índice é '{a['indice']['nome']}'")
    return E


def validar(doc, r8_estrito=True, checar_arquivos=False, schema=None):
    schema = schema or carregar_schema()
    return [f"schema: {e}" for e in schema.erros(doc)] + regras(doc, r8_estrito, checar_arquivos)


if __name__ == "__main__":
    ok = True
    for arq in sys.argv[1:]:
        erros = validar(C.ler_json(arq), r8_estrito="exemplo" not in arq, checar_arquivos="exemplo" not in arq)
        print(f"{arq}: {'OK' if not erros else str(len(erros)) + ' erro(s)'}")
        for e in erros:
            print("  -", e)
        ok = ok and not erros
    sys.exit(0 if ok else 1)
