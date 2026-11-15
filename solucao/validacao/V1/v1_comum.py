"""V1: funções comuns. Reusa o balanço da sessão B3 (somente leitura, nada é escrito lá).
Rodar com: python3 v1_xxx.py (de dentro de solucao/validacao/V1)."""
import sys, json, datetime as dt, statistics as st, math, random
from pathlib import Path

V1 = Path(__file__).resolve().parent
RAIZ = V1.parent.parent.parent
B3 = RAIZ / "loop-validacao" / "sessoes" / "B3"
sys.path.insert(0, str(B3))
import comum  # noqa: E402  (B3/comum.py: Power, balanco, rend_relativo, spearman)
import teste1_estiagem_milho as t1  # noqa: E402  (só define funções; o __main__ não roda)
import teste2_excesso_cebola as t2  # noqa: E402
from comum import Power, rend_relativo, spearman, dias  # noqa: E402

EXTERNO_V1 = V1 / "externo"
POWER_V1 = V1 / "power"


def ibge(arquivo, pasta=None, var="Rendimento"):
    pasta = pasta or (B3 / "externo")
    rows = json.load(open(pasta / arquivo))[1:]
    out = {}
    for r in rows:
        if r["D2N"].startswith(var) and r["V"] not in ("...", "-", "X", "..", "0"):
            out[int(r["D3N"])] = float(r["V"])
    return out


def ind_milho(pw, ano, plantio=(9, 20), decisao=(1, 10)):
    t1.pw = pw
    s = t1.safra(ano, plantio, decisao)
    return s


def ind_cebola(pw, ano):
    t2.pw = pw
    return t2.safra(ano)


def wilson(k, n, z=1.96):
    if n == 0: return (None, None)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0, c - h), min(1, c + h))


def hipergeom_p(N, K, n, k):
    """P(X >= k), X ~ Hipergeométrica(N população, K sucessos, n sorteios)."""
    from math import comb
    return sum(comb(K, i) * comb(N - K, n - i) for i in range(k, min(K, n) + 1)) / comb(N, n)


# ---------- avaliação da regra ----------
def q10(xs):
    return st.quantiles(xs, n=10, method="inclusive")[0]


def q90(xs):
    return st.quantiles(xs, n=10, method="inclusive")[-1]


def aplica(rows, regra):
    """regra(row) -> bool. Devolve cópia com campo alerta."""
    return [dict(r, alerta=bool(regra(r))) for r in rows]


def resumo(rows, corte=0.85, campo_rel="rel"):
    n = len(rows)
    ruim = [r[campo_rel] <= corte for r in rows]
    al = [r for r in rows if r["alerta"]]
    hits = sum(1 for r in al if r[campo_rel] <= corte)
    base = sum(ruim) / n if n else None
    prec = hits / len(al) if al else None
    # por evento: um ano de safra = um evento, juntando as regiões
    anos = sorted({r["ano"] for r in al})
    ev = []
    for a in anos:
        g = [r for r in al if r["ano"] == a]
        fr = sum(r[campo_rel] <= corte for r in g) / len(g)
        ev.append(dict(ano=a, regioes=[r["regiao"] for r in g], frac_ruim=round(fr, 2),
                       rel=[round(r[campo_rel], 2) for r in g], acerto=fr >= 0.5))
    ke = sum(e["acerto"] for e in ev)
    lo, hi = wilson(ke, len(ev))
    return dict(anos_regiao=n, ruins=sum(ruim), taxa_base=round(base, 3) if base is not None else None,
                alertas=len(al), acertos=hits, precisao=round(prec, 3) if prec is not None else None,
                recall=round(hits / sum(ruim), 3) if sum(ruim) else None,
                rel_medio_alerta=round(st.mean(r[campo_rel] for r in al), 3) if al else None,
                eventos=len(ev), eventos_acerto=ke,
                acerto_evento=round(ke / len(ev), 3) if ev else None,
                ic95_evento=[round(lo, 2), round(hi, 2)] if ev else None,
                lista_eventos=ev)


def permutacao_conjunta(rows, regra_fn, corte=0.85, n=10000, seed=7, anos=range(1990, 2026)):
    """Sorteia uma permutação dos anos e aplica a MESMA a todas as regiões: o indicador do ano pi(a)
    é pareado com o rendimento do ano a. Preserva a dependência espacial (anos ruins no estado todo).
    regra_fn(regiao, valor_indicador_row) -> bool, recebe a linha com o indicador trocado.
    Estatística: acertos por evento (anos com alerta em que >= metade das regiões alertadas teve ano ruim)
    menos taxa-base x eventos; e precisão por ano-região. Devolve p unilaterais."""
    rnd = random.Random(seed)
    anos = list(anos)
    por_reg = {}
    for r in rows: por_reg.setdefault(r["regiao"], {})[r["ano"]] = r

    def estat(mapa):
        al = []
        for reg, d in por_reg.items():
            for a, r in d.items():
                b = mapa.get(a)
                if b is None or b not in d: continue
                rr = dict(d[b]); rr["rel"] = r["rel"]; rr["ano"] = a
                if regra_fn(rr): al.append(rr)
        if not al: return 0.0, 0.0
        prec = sum(x["rel"] <= corte for x in al) / len(al)
        evs = {}
        for x in al: evs.setdefault(x["ano"], []).append(x["rel"] <= corte)
        fe = sum(1 for v in evs.values() if sum(v) / len(v) >= 0.5) / len(evs)
        return prec, fe

    obs = estat({a: a for a in anos})
    c1 = c2 = 0
    for _ in range(n):
        p = anos[:]; rnd.shuffle(p)
        s = estat(dict(zip(anos, p)))
        c1 += s[0] >= obs[0] - 1e-12
        c2 += s[1] >= obs[1] - 1e-12
    return dict(precisao_obs=round(obs[0], 3), acerto_evento_obs=round(obs[1], 3),
                p_precisao=round((c1 + 1) / (n + 1), 4), p_evento=round((c2 + 1) / (n + 1), 4), n=n)
