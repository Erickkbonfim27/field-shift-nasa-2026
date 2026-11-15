import json, numpy as np
from comum import *
d=json.load(open('ext/epagri_precos_cebola_milho_leite.json'))
ceb={**d['Cebola pera SC classe 3 a 5 (pagto 35 dias) | saco 20 kg'], **d['Cebola pera - SC classe 3 a 5 (pgto 35 dias) | sc 20 kg']}
mil={**d['Milho amarelo | sc 60 kg'], **d['Milho-amarelo | sc 60 kg']}
# IPCA mensal
ip={}
for r in json.load(open('ext/ipca.json'))[1:]:
    mes,ano=r['D3N'].split(); M=['janeiro','fevereiro','março','abril','maio','junho','julho','agosto','setembro','outubro','novembro','dezembro'].index(mes)+1
    ip[f'{ano}-{M:02d}']=float(r['V'])
ref=ip['2025-12']
real=lambda s:{k:v/20*ref/ip[k] for k,v in s.items() if k in ip}  # R$ dez/2025 por kg (cebola sc 20kg)
cr=real(ceb)
def media(s,y,meses):
    v=[s[f'{y}-{m:02d}'] for m in meses if f'{y}-{m:02d}' in s]; return np.mean(v) if v else None
pi=power('ituporanga'); ind={y:soma(pi,'PRECTOTCORR',y,9,11) for y in range(1997,2026)}
print('== TESTE 3: prêmio de guardar (mar–abr t+1 vs nov–dez t) ==')
prem={}
for y in range(1997,2026):
    a=media(cr,y,[11,12]); b=media(cr,y+1,[3,4])
    if a and b: prem[y]=b/a-1; print(y, f"nov-dez {a:.2f}  mar-abr {b:.2f}  prêmio {prem[y]:+.0%}  chuva set-nov {ind[y]:.0f}")
ys=sorted(prem); n15=sum(prem[y]>=0.15 for y in ys)
print(f"safras com prêmio >=15%: {n15}/{len(ys)} ; mediana {np.median([prem[y] for y in ys]):+.0%}; média {np.mean([prem[y] for y in ys]):+.0%}")
r=spearman([ind[y] for y in ys],[prem[y] for y in ys]); print(f"ρ(chuva set-nov, prêmio)={r[0]:+.2f} p={r[1]:.3f}")
print('== CONFERÊNCIA EXTRA ideia 1: preço da safra (nov–dez t) real Epagri vs chuva set–nov ==')
ps={y:media(cr,y,[11,12]) for y in range(1997,2026) if media(cr,y,[11,12])}
ys=sorted(ps); an=anom_trend(ps,ys,1)
r=spearman([ind[y] for y in ys],[an[y] for y in ys]); print(f"ρ(chuva, preço nov-dez sem tendência)={r[0]:+.2f} p={r[1]:.3f} n={len(ys)}")
corte=np.percentile([ind[y] for y in ys],200/3); al=[y for y in ys if ind[y]>=corte]
print("alarmes",al,"anom preço alarme",np.mean([an[y] for y in al]),"outros",np.mean([an[y] for y in ys if y not in al]))
q=[y for y in al if y+1 in ps]; print("preço safra seguinte menor após alarme:",sum(ps[y+1]<ps[y] for y in q),"/",len(q), " base:", np.mean([ps[y+1]<ps[y] for y in ys if y+1 in ps]))
print('== CONFERÊNCIA EXTRA ideia 2: milho SC, alta de jan a mai em ano de alarme ==')
mr={k:v/60*ref/ip[k] for k,v in mil.items() if k in ip}
ps2=power('sao_miguel_do_oeste')
ch={y:soma(ps2,'PRECTOTCORR',y,12,1) for y in range(1999,2027)}
gw={y:soma(ps2,'GWETROOT',y,12,1,fn=np.mean) for y in range(1999,2027)}
alta={}
for y in range(1999,2027):
    a=media(mr,y,[1,2]); b=media(mr,y,[5,6])
    if a and b: alta[y]=b/a-1
ys=sorted(alta)
for nome,ind2 in [('GWETROOT',gw),('chuva',ch)]:
    corte=np.percentile([ind2[y] for y in ys],100/3); al=[y for y in ys if ind2[y]<=corte]
    r=spearman([ind2[y] for y in ys],[alta[y] for y in ys])
    print(f"{nome}: alarmes {al}; alta jan/fev→mai/jun alarme {np.mean([alta[y] for y in al]):+.1%} vs outros {np.mean([alta[y] for y in ys if y not in al]):+.1%}; ρ={r[0]:+.2f} p={r[1]:.3f} n={len(ys)}")
print({y:f"{alta[y]:+.0%}" for y in ys})
json.dump({'premio':prem,'ind':ind,'alta_milho':alta,'chuva_smo':ch},open('teste3_saida.json','w'),indent=1)
