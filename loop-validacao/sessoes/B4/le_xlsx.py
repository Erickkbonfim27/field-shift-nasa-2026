import zipfile, re, sys, xml.etree.ElementTree as ET
NS={'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
def ler(path):
    z=zipfile.ZipFile(path)
    ss=[]
    if 'xl/sharedStrings.xml' in z.namelist():
        for si in ET.fromstring(z.read('xl/sharedStrings.xml')).findall('m:si',NS):
            ss.append(''.join(t.text or '' for t in si.iter('{%s}t'%NS['m'])))
    wb=ET.fromstring(z.read('xl/workbook.xml'))
    nomes=[s.get('name') for s in wb.find('m:sheets',NS)]
    rels=ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))
    alvo={r.get('Id'):r.get('Target') for r in rels}
    folhas={}
    for s,nome in zip(wb.find('m:sheets',NS),nomes):
        rid=s.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')
        t=alvo[rid]; t=t.lstrip('/'); t=t if t.startswith('xl/') else 'xl/'+t
        rows=[]
        for row in ET.fromstring(z.read(t)).iter('{%s}row'%NS['m']):
            r={}
            for c in row.findall('m:c',NS):
                ref=re.match(r'([A-Z]+)',c.get('r')).group(1)
                v=c.find('m:v',NS)
                if v is None:
                    is_=c.find('m:is',NS); val=''.join(x.text or '' for x in is_.iter('{%s}t'%NS['m'])) if is_ is not None else None
                else:
                    val=v.text
                    if c.get('t')=='s': val=ss[int(val)]
                r[ref]=val
            rows.append(r)
        folhas[nome]=rows
    return folhas
if __name__=='__main__':
    f=ler(sys.argv[1])
    for n,rows in f.items():
        print('FOLHA',n,len(rows))
        for r in rows[:6]: print('  ',list(r.items())[:14])
