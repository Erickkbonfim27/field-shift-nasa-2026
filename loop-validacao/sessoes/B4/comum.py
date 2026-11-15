import json
import numpy as np
from pam import load
DADOS='../../dados/'
def power(nome):
    d=json.load(open(DADOS+f'power_{nome}.json'))['properties']['parameter']
    return d
def soma(p, var, y, m1, m2, fn=np.sum, cond=None):
    """agrega var de (y,m1) a (y,m2) ; m1>m2 => cruza ano (m1 no ano y-1)"""
    vals=[]
    for k,v in p[var].items():
        yy,mm=int(k[:4]),int(k[4:6])
        if m1<=m2: ok = yy==y and m1<=mm<=m2
        else: ok = (yy==y-1 and mm>=m1) or (yy==y and mm<=m2)
        if ok and v!=-999: vals.append(v)
    vals=np.array(vals)
    if cond is not None: return int(np.sum(cond(vals)))
    return float(fn(vals))
def ipca_anual():
    d=json.load(open('ext/ipca.json'))[1:]
    acc={}
    for r in d:
        y=int(r['D3N'].split()[-1]); acc.setdefault(y,[]).append(float(r['V']))
    return {y:np.mean(v) for y,v in acc.items() if len(v)==12}
def preco_real(nome, base=2025):
    t=load(nome); ip=ipca_anual()
    out={}
    for y in range(1995,2026):
        r=t.get(y,{})
        if r.get('valor') and r.get('qtd'): out[y]=r['valor']/r['qtd']*ip[base]/ip[y]
    return out
def anom_trend(series, anos, grau):
    x=np.array(anos,float); yv=np.array([series[a] for a in anos],float)
    c=np.polyfit(x,yv,grau); tr=np.polyval(c,x)
    return {a: yv[i]/tr[i]-1 for i,a in enumerate(anos)}
def spearman(a,b):
    from scipy.stats import spearmanr
    r=spearmanr(a,b); return r.statistic, r.pvalue
