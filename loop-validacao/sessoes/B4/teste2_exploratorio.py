# EXPLORATÓRIO (depois do teste pré-registrado; não conta para o critério).
# Varre janelas de 2 meses; escolhe a melhor em 1995–2010 (treino) e confere em 2011–2025 (teste).
import numpy as np
from comum import *
p=power('sao_miguel_do_oeste'); mic=load('milho_micro_smo')
aa=list(range(1995,2026)); an=anom_trend({y:mic[y]['rend'] for y in aa},aa,1)
jan={'out-nov':(10,11),'nov-dez':(11,12),'dez-jan':(12,1),'jan-fev':(1,2),'out-dez':(10,12)}
def agg(var,y,m1,m2,fn):
    if m1<=m2 and m2>=10: return soma(p,var,y-1,m1,m2,fn=fn)  # meses do ano anterior (plantio em ago-set)
    return soma(p,var,y,m1,m2,fn=fn)
tr=[a for a in aa if a<=2010]; te=[a for a in aa if a>2010]
for var,fn in [('GWETROOT',np.mean),('PRECTOTCORR',np.sum)]:
    for nome,(m1,m2) in jan.items():
        ind={y:agg(var,y,m1,m2,fn) for y in aa}
        r_all=spearman([ind[a] for a in aa],[an[a] for a in aa])
        r_tr=spearman([ind[a] for a in tr],[an[a] for a in tr]); r_te=spearman([ind[a] for a in te],[an[a] for a in te])
        print(f"{var:11s} {nome:8s} todos ρ={r_all[0]:+.2f} (p={r_all[1]:.3f})  treino95-10 ρ={r_tr[0]:+.2f}  teste11-25 ρ={r_te[0]:+.2f}")
# sem 2021 (cigarrinha/enfezamento, não clima)
for var,fn,(m1,m2) in [('GWETROOT',np.mean,(11,12)),('PRECTOTCORR',np.sum,(11,12)),('GWETROOT',np.mean,(12,1))]:
    ind={y:agg(var,y,m1,m2,fn) for y in aa}; s=[a for a in aa if a!=2021]
    r=spearman([ind[a] for a in s],[an[a] for a in s]); 
    corte=np.percentile([ind[a] for a in s],100/3); al=[a for a in s if ind[a]<=corte]; q=[a for a in s if an[a]<=-0.2]
    print(f"sem 2021 {var} {m1}-{m2}: ρ={r[0]:+.2f} p={r[1]:.3f} acertos {len([a for a in q if a in al])}/{len(q)} falsos {len([a for a in al if a not in q])}/{len(al)} alarmes={al}")
