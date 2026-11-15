# EXPLORATÓRIO (depois do teste; não conta para o critério)
import json, numpy as np
from comum import *
d=json.load(open('teste1_saida.json')); ind={int(k):v for k,v in d['indice'].items()}; pr={int(k):v for k,v in d['preco'].items()}
rend={int(k):v for k,v in d['rend_sc'].items()}
aa=list(range(1995,2026))
an=anom_trend(rend,aa,1); pa=anom_trend(pr,aa,1)
for a in aa: print(a, round(ind[a]), f"rend {an[a]:+.0%}", f"preço {pr[a]:.2f} anom {pa[a]:+.0%}", "<-- >=600mm" if ind[a]>=600 else "")
ext=[a for a in aa if ind[a]>=600]
print("anos >=600mm:",ext,"anom rend média",np.mean([an[a] for a in ext]),"resto",np.mean([an[a] for a in aa if a not in ext]))
print("anom preço (sem tendência) nos >=600:",np.mean([pa[a] for a in ext]),"resto",np.mean([pa[a] for a in aa if a not in ext]))
rho,pv=spearman([ind[a] for a in aa],[pa[a] for a in aa]);print("rho indice x preço sem tendência",rho,pv)
rho,pv=spearman([an[a] for a in aa],[pa[a] for a in aa]);print("rho anom rend SC x anom preço",rho,pv)
