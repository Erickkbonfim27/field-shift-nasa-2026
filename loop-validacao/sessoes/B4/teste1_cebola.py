import json, numpy as np
from comum import *
p=power('ituporanga')
sc=load('cebola_sc'); itu=load('cebola_ituporanga')
anos=list(range(1985,2026))
ind={y:soma(p,'PRECTOTCORR',y,9,11) for y in anos}
res={}
for nome,t in [('SC',sc),('Ituporanga',itu)]:
    rend={y:t[y]['rend'] for y in anos}
    for rot,grau,aa in [('quad85',2,anos),('lin95',1,list(range(1995,2026)))]:
        an=anom_trend(rend,aa,grau)
        rho,pv=spearman([ind[a] for a in aa],[an[a] for a in aa])
        corte=np.percentile([ind[a] for a in aa],100*2/3)
        alarme=[a for a in aa if ind[a]>=corte]
        quebra=[a for a in aa if an[a]<=-0.15]
        hit=[a for a in quebra if a in alarme]
        fa=[a for a in alarme if a not in quebra]
        res[(nome,rot)]=dict(rho=rho,p=pv,n=len(aa),quebras=quebra,alarmes=alarme,hit=len(hit),fa=len(fa))
        print(nome,rot,f"rho={rho:.2f} p={pv:.3f} n={len(aa)} quebras={quebra} alarmes={alarme} acertos={len(hit)}/{len(quebra)} falsos={len(fa)}/{len(alarme)}")
# preço
pr=preco_real('cebola_sc')
aa=sorted(pr)
corte=np.percentile([ind[a] for a in anos if a>=1995],100*2/3)  # mesmo terço do período do preço
al=[a for a in aa if ind[a]>=corte]; nal=[a for a in aa if a not in al]
m1=np.mean([pr[a] for a in al]); m0=np.mean([pr[a] for a in nal])
print(f"preço real SC (R$2025/kg): alarme {m1:.2f} (n={len(al)}) vs outros {m0:.2f} (n={len(nal)}) => {100*(m1/m0-1):+.0f}%")
rho,pv=spearman([ind[a] for a in aa],[pr[a] for a in aa]); print(f"rho(indice,preço)={rho:.2f} p={pv:.3f}")
# preço vs quantidade SC
rho,pv=spearman([sc[a]['qtd'] for a in aa],[pr[a] for a in aa]); print(f"rho(qtd SC,preço)={rho:.2f} p={pv:.3f}")
an=anom_trend({y:sc[y]['rend'] for y in anos},list(range(1995,2026)),1)
rho,pv=spearman([an[a] for a in aa],[pr[a] for a in aa]); print(f"rho(anom rend SC,preço)={rho:.2f} p={pv:.3f}")
# ano seguinte
quedas=[a for a in aa if a+1 in pr and pr[a+1]<pr[a]]
base=len(quedas)/len([a for a in aa if a+1 in pr])
alq=[a for a in al if a+1 in pr]
print(f"queda no ano seguinte após alarme: {sum(pr[a+1]<pr[a] for a in alq)}/{len(alq)} ; base todos os anos {base:.0%}")
# área ano seguinte
print("var área plantada SC t+1 após alarme:", {a: round(100*(sc[a+1]['area_plant']/sc[a]['area_plant']-1),1) for a in alq})
print("var área t+1 média geral:", np.mean([100*(sc[a+1]['area_plant']/sc[a]['area_plant']-1) for a in aa if a+1 in pr]))
json.dump({'indice':ind,'preco':pr,'rend_sc':{y:sc[y]['rend'] for y in anos}},open('teste1_saida.json','w'),indent=1)
print({a:round(ind[a]) for a in anos})
print({a:round(pr[a],2) for a in aa})
