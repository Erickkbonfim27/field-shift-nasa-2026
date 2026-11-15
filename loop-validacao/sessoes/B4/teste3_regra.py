import json, numpy as np
from comum import spearman, anom_trend
d=json.load(open('teste3_saida.json')); prem={int(k):v for k,v in d['premio'].items()}; ind={int(k):v for k,v in d['ind'].items()}
ys=sorted(prem)
from scipy.stats import spearmanr
r=spearmanr([ind[y] for y in ys],[prem[y] for y in ys]); print("ρ exato",r.statistic,r.pvalue)
corte=np.percentile([ind[y] for y in ys],200/3); al=[y for y in ys if ind[y]>=corte]
print("corte mm",round(corte),"alarmes",al,"prêmio mediano alarme",np.median([prem[y] for y in al]),"outros",np.median([prem[y] for y in ys if y not in al]))
print("prêmio>=15% alarme",sum(prem[y]>=.15 for y in al),"/",len(al)," outros",sum(prem[y]>=.15 for y in ys if y not in al),"/",len(ys)-len(al))
# regra: guardar 50% exceto ano de alarme (vende tudo). perda no galpão 15% [ESTIMATIVA]
P=0.15
def receita(frac,y): return (1-frac)+frac*(1+prem[y])*(1-P)   # em múltiplos do preço da colheita
for nome,f in [('vende tudo',lambda y:0),('guarda 50% sempre',lambda y:.5),('regra NASA (50% se não-alarme)',lambda y:0 if y in al else .5),('guarda 100% sempre',lambda y:1)]:
    rr=[receita(f(y),y) for y in ys]
    print(f"{nome:32s} receita média {np.mean(rr):.3f}  pior ano {min(rr):.3f}  anos abaixo de vender tudo {sum(x<1 for x in rr)}")
# só nos anos de alarme: guardar ajuda?
print("anos alarme, guardar 50%:",[round(receita(.5,y),2) for y in al])
