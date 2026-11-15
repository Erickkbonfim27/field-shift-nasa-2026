# Conferência extra da ideia 1 com preço mensal Epagri: estabilidade em duas metades
import json, numpy as np
from comum import *
d=json.load(open('ext/epagri_precos_cebola_milho_leite.json'))
ceb={**d['Cebola pera SC classe 3 a 5 (pagto 35 dias) | saco 20 kg'], **d['Cebola pera - SC classe 3 a 5 (pgto 35 dias) | sc 20 kg']}
ip={}
for r in json.load(open('ext/ipca.json'))[1:]:
    mes,ano=r['D3N'].split(); M=['janeiro','fevereiro','março','abril','maio','junho','julho','agosto','setembro','outubro','novembro','dezembro'].index(mes)+1
    ip[f'{ano}-{M:02d}']=float(r['V'])
cr={k:v/20*ip['2025-12']/ip[k] for k,v in ceb.items()}
pi=power('ituporanga'); ind={y:soma(pi,'PRECTOTCORR',y,9,11) for y in range(1997,2026)}
ps={}
for y in range(1997,2026):
    v=[cr[f'{y}-{m}'] for m in ('11','12') if f'{y}-{m}' in cr]
    if v: ps[y]=np.mean(v)
ys=sorted(ps); an=anom_trend(ps,ys,1)
for nome,sub in [('todos',ys),('1997-2010',[y for y in ys if y<=2010]),('2011-2025',[y for y in ys if y>2010])]:
    r=spearman([ind[y] for y in sub],[an[y] for y in sub]); print(nome,len(sub),f"ρ={r[0]:+.2f} p={r[1]:.3f}")
sem=[y for y in ys if y!=2023]; r=spearman([ind[y] for y in sem],[an[y] for y in sem]); print("sem 2023",f"ρ={r[0]:+.2f} p={r[1]:.3f}")
json.dump({'preco_nov_dez':ps,'anom':an,'ind':ind},open('teste1_epagri_saida.json','w'),indent=1)
