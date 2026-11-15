"""Estatística simples, só biblioteca padrão."""
import math
import random


def wilson(k, n, z=1.96):
    """Intervalo de Wilson (fração). Igual a V1/v1_comum.py e V2/v2_geada.py."""
    if n == 0:
        return (None, None)
    p = k / n
    den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return max(0.0, c - h), min(1.0, c + h)


def em10(k, n):
    return round(10 * k / n, 1)


def ic10(k, n):
    lo, hi = wilson(k, n)
    return [round(10 * lo, 1), round(10 * hi, 1)]


def quantil(v, p):
    """Interpolação linear (igual a numpy.percentile padrão e a modelo_v3.q)."""
    v = sorted(v)
    i = p * (len(v) - 1)
    lo = int(i)
    hi = min(lo + 1, len(v) - 1)
    return v[lo] + (v[hi] - v[lo]) * (i - lo)


def mediana(v):
    return quantil(v, 0.5)


def arred(x):
    """Arredondamento 'meio para cima' (regra R7), para x >= 0."""
    return int(math.floor(x + 0.5))


def bootstrap_por_safra(linhas, estat, nb=2000, semente=20261114):
    """linhas: lista por safra (cada item é o que `estat` recebe em lista).
    Sorteia safras com reposição. Devolve a lista de nb valores."""
    rnd = random.Random(semente)
    n = len(linhas)
    out = []
    for _ in range(nb):
        amostra = [linhas[rnd.randrange(n)] for _ in range(n)]
        out.append(estat(amostra))
    return out


def _ranks(x):
    ordem = sorted(range(len(x)), key=lambda i: x[i])
    r = [0.0] * len(x)
    i = 0
    while i < len(x):
        j = i
        while j + 1 < len(x) and x[ordem[j + 1]] == x[ordem[i]]:
            j += 1
        for q in range(i, j + 1):
            r[ordem[q]] = (i + j) / 2 + 1
        i = j + 1
    return r


def spearman(a, b):
    """Correlação de Spearman (postos com empate pela média). None se uma série for constante."""
    ra, rb = _ranks(a), _ranks(b)
    ma, mb = sum(ra) / len(ra), sum(rb) / len(rb)
    num = sum((x - ma) * (y - mb) for x, y in zip(ra, rb))
    den = (sum((x - ma) ** 2 for x in ra) * sum((y - mb) ** 2 for y in rb)) ** 0.5
    return None if den == 0 else num / den
