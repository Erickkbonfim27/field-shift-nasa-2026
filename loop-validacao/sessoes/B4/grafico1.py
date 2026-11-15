import json, numpy as np
from comum import anom_trend
from svg import *
d=json.load(open('teste1_saida.json')); ind={int(k):v for k,v in d['indice'].items()}; pr={int(k):v for k,v in d['preco'].items()}
rend={int(k):v for k,v in d['rend_sc'].items()}; aa=list(range(1995,2026))
an=anom_trend(rend,aa,1); pa=anom_trend(pr,aa,1)
corte=np.percentile([ind[a] for a in aa],100*2/3)
rot1=[a for a in aa if ind[a]>=600 or an[a]<=-0.15]; rot2=[a for a in aa if ind[a]>=600 or abs(pa[a])>0.4]
p1=scatter_panel([(ind[a],100*an[a],a) for a in aa],70,40,380,280,(200,900),(-40,40),'Produtividade: só os extremos respondem (ρ = −0,12)','Chuva set–nov em Ituporanga, NASA POWER (mm)','Rendimento cebola SC vs tendência (%)','#2b6cb0',rot1,corte)
p2=scatter_panel([(ind[a],100*pa[a],a) for a in aa],560,40,380,280,(200,900),(-80,80),'Preço: sem relação (ρ = +0,21; p = 0,25)','Chuva set–nov em Ituporanga, NASA POWER (mm)','Preço real cebola SC vs tendência (%)','#c05621',rot2,corte)
open('grafico1_cebola.svg','w').write(svg(p1+p2,980,400,'Fontes: NASA POWER PRECTOTCORR; IBGE PAM t.5457 (rendimento; valor ÷ quantidade); IPCA t.1737. 1995–2025. Tracejado: corte do terço mais chuvoso (alarme).'))
