import json, numpy as np
from comum import *
p=power('sao_miguel_do_oeste')
mic=load('milho_micro_smo'); mun=load('milho_smo'); msc=load('milho_sc')
anos=list(range(1985,2026))
gw={y:soma(p,'GWETROOT',y,12,1,fn=np.mean) for y in anos}
ch={y:soma(p,'PRECTOTCORR',y,12,1) for y in anos}
out={}
for nome,t in [('micro SMO',mic),('município SMO',mun),('SC',msc)]:
    rend={y:t[y]['rend'] for y in anos}
    for rot,grau,aa in [('quad85',2,anos),('lin95',1,list(range(1995,2026)))]:
        an=anom_trend(rend,aa,grau)
        for iname,ind in [('GWETROOT',gw),('chuva',ch)]:
            rho,pv=spearman([ind[a] for a in aa],[an[a] for a in aa])
            corte=np.percentile([ind[a] for a in aa],100/3)
            alarme=[a for a in aa if ind[a]<=corte]
            quebra=[a for a in aa if an[a]<=-0.20]
            hit=[a for a in quebra if a in alarme]; fa=[a for a in alarme if a not in quebra]
            print(f"{nome:14s} {rot} {iname:8s} rho={rho:+.2f} p={pv:.4f} n={len(aa)} acertos={len(hit)}/{len(quebra)} falsos={len(fa)}/{len(alarme)} quebras={quebra} alarmes={alarme}")
            out[(nome,rot,iname)]=an
# preço SC milho
pr=preco_real('milho_sc'); aa=sorted(pr)
corte=np.percentile([gw[a] for a in aa],100/3); al=[a for a in aa if gw[a]<=corte]
m1=np.mean([pr[a] for a in al]); m0=np.mean([pr[a] for a in aa if a not in al])
print(f"preço real milho SC (R$2025/kg): alarme {m1:.3f} vs outros {m0:.3f} => {100*(m1/m0-1):+.0f}%  alarmes={al}")
pa=anom_trend(pr,aa,1)
m1=np.mean([pa[a] for a in al]); m0=np.mean([pa[a] for a in aa if a not in al]); print(f"preço sem tendência: alarme {m1:+.0%} vs outros {m0:+.0%}")
rho,pv=spearman([gw[a] for a in aa],[pa[a] for a in aa]); print(f"rho GWETROOT x preço sem tendência {rho:+.2f} p={pv:.3f}")
an=out[('micro SMO','lin95','GWETROOT')]
for a in range(1995,2026): print(a, f"gw={gw[a]:.3f} chuva={ch[a]:.0f} rend_micro={mic[a]['rend']:.0f} anom={an[a]:+.0%} preço={pr[a]:.3f}")
json.dump({'gw':gw,'chuva':ch,'rend_micro':{y:mic[y]['rend'] for y in anos},'preco':pr},open('teste2_saida.json','w'),indent=1)
