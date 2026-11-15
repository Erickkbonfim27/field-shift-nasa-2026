import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import json, re, sys
from le_xlsx import ler
f=ler('ext/epagri/Precos_recebidos_1998_2026.xlsx')
MES={'jan':1,'fev':2,'mar':3,'abr':4,'mai':5,'jun':6,'jul':7,'ago':8,'set':9,'out':10,'nov':11,'dez':12}
out={}
for folha in ['PRECOS_RECEBIDOS_2026_2014','PRECOS_RECEBIDOS_2013_2007','PRECOS_RECEBIDOS_2006_1998']:
    rows=f[folha]
    hdr=next(r for r in rows if any((v or '') in ('Produto',) for v in r.values()))
    pcol=[k for k,v in hdr.items() if v=='Produto'][0]
    cols={}
    for k,v in hdr.items():
        m=re.match(r'([A-Za-z]{3})[/_](\d{2})',v or '')
        if m: cols[k]=(2000+int(m.group(2)) if int(m.group(2))<50 else 1900+int(m.group(2)), MES[m.group(1).lower()])
    for r in rows:
        nome=(r.get(pcol) or '').strip()
        if re.search(r'cebola|milho|leite',nome,re.I):
            ucol=chr(ord(pcol)+1)
            for k,(y,m) in cols.items():
                v=r.get(k)
                try: v=float(v)
                except: continue
                out.setdefault(nome+' | '+str(r.get(ucol)),{})[f'{y}-{m:02d}']=v
for k,v in out.items(): print(k, len(v), min(v), max(v))
json.dump(out,open('ext/epagri_precos_cebola_milho_leite.json','w'),indent=0,ensure_ascii=False)
