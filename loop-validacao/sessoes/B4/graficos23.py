import json, numpy as np
from comum import anom_trend
from svg import *
# Gráfico 2: milho
d=json.load(open('teste2_saida.json')); gw={int(k):v for k,v in d['gw'].items()}; rend={int(k):v for k,v in d['rend_micro'].items()}
aa=list(range(1995,2026)); an=anom_trend(rend,aa,1)
corte=np.percentile([gw[a] for a in aa],100/3)
rot=[a for a in aa if an[a]<=-0.2 or gw[a]<=corte]
p=scatter_panel([(100*gw[a],100*an[a],a) for a in aa],70,40,520,300,(60,88),(-50,40),'Milho, microrregião de São Miguel do Oeste (ρ = +0,26; critério ≥ 0,50)','Umidade da zona das raízes dez–jan, NASA POWER GWETROOT (%)','Rendimento vs tendência (%)','#2f855a',rot,100*corte)
open('grafico2_milho.svg','w').write(svg(p,640,420,'Fontes: NASA POWER GWETROOT (MERRA-2); IBGE PAM t.5457, microrregião 42001. 1995–2025. Tracejado: terço mais seco (alarme). 2021: cigarrinha.'))
# Gráfico 3: preço colheita Epagri e prêmio de guardar
e=json.load(open('teste1_epagri_saida.json')); ind={int(k):v for k,v in e['ind'].items()}; anp={int(k):v for k,v in e['anom'].items()}
t=json.load(open('teste3_saida.json')); prem={int(k):v for k,v in t['premio'].items()}
y1=sorted(anp); y2=sorted(prem)
c1=np.percentile([ind[y] for y in y1],200/3); c2=np.percentile([ind[y] for y in y2],200/3)
p1=scatter_panel([(ind[y],100*anp[y],y) for y in y1],70,40,380,280,(200,900),(-80,120),'Preço da colheita (nov–dez) sobe com a chuva (ρ = +0,60)','Chuva set–nov em Ituporanga, NASA POWER (mm)','Preço real ao produtor vs tendência (%)','#c05621',[y for y in y1 if ind[y]>=c1 or abs(anp[y])>.5],c1)
p2=scatter_panel([(ind[y],100*prem[y],y) for y in y2],560,40,380,280,(200,900),(-60,160),'Prêmio de guardar cai após primavera chuvosa (ρ = −0,40)','Chuva set–nov em Ituporanga, NASA POWER (mm)','Prêmio de mar–abr sobre nov–dez (%)','#6b46c1',[y for y in y2 if ind[y]>=c2],c2,hline=15)
open('grafico3_cebola_preco_mensal.svg','w').write(svg(p1+p2,980,400,'Fontes: NASA POWER PRECTOTCORR; Epagri/Cepa, preço recebido pelo produtor, cebola pera SC classe 3 a 5, corrigido pelo IPCA (dez/2025). Linha horizontal à direita: 15% (perda estimada no galpão).'))
