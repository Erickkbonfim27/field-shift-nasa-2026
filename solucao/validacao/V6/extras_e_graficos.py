"""V6: estatisticas extras (cebola sequeiro x irrigado) e 3 graficos SVG. Le zarc_gabarito_sc.json."""
import json, os
AQUI = os.path.dirname(os.path.abspath(__file__))
G = json.load(open(os.path.join(AQUI,"zarc_gabarito_sc.json")))["dados"]
ORDEM = list(range(10,37))+list(range(1,10))
def rot(i):
    m,d = divmod(i-1,3); return "%02d/%02d"%(1+10*d,m+1)
LAB = [rot(i) for i in ORDEM]
COR = {0:"#e6e6e6",20:"#2e8b57",30:"#e0b020",40:"#d9534f"}
# ---- cebola: sequeiro x irrigado
ex = {}
for m in G:
    s = G[m]["cebola"].get("Sequeiro",{}).get("ciclos",{}); i = G[m]["cebola"].get("Irrigado",{}).get("ciclos",{})
    iguais=tot=0; difs=[]
    for cn in i:
        for sn in i[cn]:
            if cn in s and sn in s[cn]:
                a=s[cn][sn]["risco_por_decendio"]; b=i[cn][sn]["risco_por_decendio"]; tot+=1
                if a==b: iguais+=1
    ex[m]={"pares_comparaveis":tot,"identicos":iguais}
# ---- quantas combinacoes de AD tem janela de milho no tronco ago-set..jan (SMO), por AD
json.dump(ex,open(os.path.join(AQUI,"extras_cebola_seq_irr.json"),"w"),indent=1)
print(ex)

def melhor(cult, mun, manejo="Sequeiro", filtro=None):
    """menor risco indicado por decendio, entre ciclos e solos filtrados"""
    out = {}
    for cn,s in G[mun][cult][manejo]["ciclos"].items():
        for sn,v in s.items():
            if filtro and not filtro(cn,sn): continue
            for k,r in v["risco_por_decendio"].items(): out[k] = min(out.get(k,99), r)
    return out
def linhas(mun):
    return [("Milho 1ª safra (grupo I, AD5)", melhor("milho_1safra",mun,filtro=lambda c,s:c=="grupo_I" and s=="AD5")),
            ("Sorgo forrageiro 1ª safra", melhor("sorgo_forrageiro_1safra",mun,filtro=lambda c,s:c=="grupo_I" and s=="solo_tipo_2")),
            ("Sorgo forrageiro 2ª safra", melhor("sorgo_forrageiro_2safra",mun,filtro=lambda c,s:c=="grupo_I" and s=="solo_tipo_2")),
            ("Aveia (grupo I, AD5)", melhor("aveia",mun,filtro=lambda c,s:c=="grupo_I" and s=="AD5")),
            ("Cebola (melhor ciclo, AD5)", melhor("cebola",mun,filtro=lambda c,s:s=="AD5"))]
def svg_janelas():
    W,H = 980, 80+2*(5*26+70); x0=230; cw=19
    s=['<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" font-family="Helvetica,Arial,sans-serif" font-size="12">'%(W,H),
       '<rect width="100%%" height="100%%" fill="white"/>',
       '<text x="10" y="22" font-size="16" font-weight="bold">Janelas de plantio do ZARC 2026/27 (risco por decêndio)</text>',
       '<text x="10" y="40" fill="#444">Verde 20%, amarelo 30%, vermelho 40%, cinza = não indicado. Eixo começa em 1/abr. Fonte: SISZARC.</text>']
    y=70
    for mun,nome in (("Sao Miguel do Oeste","São Miguel do Oeste"),("Ituporanga","Ituporanga")):
        s.append('<text x="10" y="%d" font-weight="bold" font-size="14">%s</text>'%(y,nome)); y+=14
        for k,(tit,d) in enumerate(linhas(mun)):
            s.append('<text x="10" y="%d">%s</text>'%(y+17,tit))
            for j,l in enumerate(LAB):
                r=d.get(l,0)
                s.append('<rect x="%d" y="%d" width="%d" height="20" fill="%s" stroke="white"><title>%s: %s</title></rect>'%(x0+j*cw,y,cw,COR[r],l,("%d%%"%r) if r else "não indicado"))
            y+=26
        for j,l in enumerate(LAB):
            if l[:2]=="01": s.append('<text x="%d" y="%d" font-size="10" fill="#333">%s</text>'%(x0+j*cw,y+10,l))
        y+=40
    s.append('</svg>'); open(os.path.join(AQUI,"v6_janelas_zarc.svg"),"w").write("\n".join(s))
def svg_b1():
    ks=["01/08","11/08","21/08","01/09","11/09","21/09","01/10","11/10"]
    geada=[6.3,4.6,3.2,1.7,0.5,0,0,0]
    sm=G["Sao Miguel do Oeste"]["milho_1safra"]["Sequeiro"]["ciclos"]["grupo_I"]
    ad4=[sm["AD4"]["risco_por_decendio"].get(k,0) for k in ks]; ad6=[sm["AD6"]["risco_por_decendio"].get(k,0) for k in ks]
    W,H=760,420; x0=70; y0=350; bw=34
    s=['<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" font-family="Helvetica,Arial,sans-serif" font-size="12">'%(W,H),'<rect width="100%" height="100%" fill="white"/>',
       '<text x="10" y="22" font-size="16" font-weight="bold">Geada medida (B1-0) x risco ZARC, milho 1ª safra, SMO</text>',
       '<text x="10" y="40" fill="#444">Barras cinza: anos com geada em cada 100 (T2M_MIN &lt; 2 °C, NASA POWER). Pontos: risco ZARC, grupo I.</text>']
    for v in (0,20,40,60):
        y=y0-v*4.5; s.append('<line x1="%d" x2="%d" y1="%d" y2="%d" stroke="#ddd"/><text x="%d" y="%d" text-anchor="end">%d%%</text>'%(x0,W-20,y,y,x0-6,y+4,v))
    for i,k in enumerate(ks):
        x=x0+20+i*80
        s.append('<rect x="%d" y="%.1f" width="%d" height="%.1f" fill="#9aa5b1"><title>geada %.1f em 10 anos</title></rect>'%(x,y0-geada[i]*10*4.5,bw,geada[i]*10*4.5,geada[i]))
        for val,c,dx,nm in ((ad4[i],"#1f4e9c",8,"AD4"),(ad6[i],"#c2185b",26,"AD6")):
            if val: s.append('<circle cx="%d" cy="%.1f" r="6" fill="%s"><title>ZARC %s: %d%%</title></circle>'%(x+dx,y0-val*4.5,c,nm,val))
        s.append('<text x="%d" y="%d" text-anchor="middle">%s</text>'%(x+bw/2,y0+16,k))
    s.append('<circle cx="80" cy="390" r="6" fill="#1f4e9c"/><text x="92" y="394">ZARC AD4 (54,6 mm)</text><circle cx="250" cy="390" r="6" fill="#c2185b"/><text x="262" y="394">ZARC AD6 (95,4 mm)</text><rect x="430" y="383" width="14" height="14" fill="#9aa5b1"/><text x="450" y="394">geada em % dos anos (B1-0)</text></svg>')
    open(os.path.join(AQUI,"v6_b1_geada_x_zarc.svg"),"w").write("\n".join(s))
def svg_a4():
    jan=["11/09","21/09","01/10","11/10","21/10"]; sm=G["Sao Miguel do Oeste"]
    rows=[]
    for ad in ["AD1","AD2","AD3","AD4","AD5","AD6"]:
        d=sm["milho_1safra"]["Sequeiro"]["ciclos"]["grupo_I"][ad]["risco_por_decendio"]
        rows.append(("Milho "+ad,[d.get(k,0) for k in jan]))
    d=sm["sorgo_forrageiro_1safra"]["Sequeiro"]["ciclos"]["grupo_I"]["solo_tipo_1"]["risco_por_decendio"]
    rows.append(("Sorgo forrageiro (qualquer solo)",[d.get(k,0) for k in jan]))
    W,H=640,330; x0=230; cw=70
    s=['<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" font-family="Helvetica,Arial,sans-serif" font-size="12">'%(W,H),'<rect width="100%" height="100%" fill="white"/>',
       '<text x="10" y="22" font-size="16" font-weight="bold">ZARC SMO: milho x sorgo, plantio 11/set a 21/out</text>',
       '<text x="10" y="40" fill="#444">Grupo I. AD1 a AD6 = 24 a 95 mm de água disponível (raiz 60 cm).</text>']
    for j,k in enumerate(jan): s.append('<text x="%d" y="64" text-anchor="middle">%s</text>'%(x0+j*cw+cw/2,k))
    for i,(t,v) in enumerate(rows):
        y=74+i*34; s.append('<text x="10" y="%d">%s</text>'%(y+19,t))
        for j,r in enumerate(v):
            s.append('<rect x="%d" y="%d" width="%d" height="28" fill="%s" stroke="white"/><text x="%d" y="%d" text-anchor="middle" fill="%s">%s</text>'%(x0+j*cw,y,cw,COR[r],x0+j*cw+cw/2,y+19,"#fff" if r in(20,40) else "#222",("%d%%"%r) if r else "n/i"))
    s.append('<text x="10" y="%d" fill="#444">n/i = não indicado. A4 chamou de "raso" 87,5 mm, o que cai em AD5/AD6.</text></svg>'%(H-12))
    open(os.path.join(AQUI,"v6_a4_milho_x_sorgo.svg"),"w").write("\n".join(s))
svg_janelas(); svg_b1(); svg_a4()
