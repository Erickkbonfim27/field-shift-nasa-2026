"""V6: monta o gabarito ZARC (SMO e Ituporanga) a partir da tabua de risco 2026/27.
Uso: python3 -I gerar_gabarito.py   (le ext/*.csv, grava zarc_gabarito_sc.json e resultados_comparacao.json)
"""
import csv, json, os, collections, statistics
AQUI = os.path.dirname(os.path.abspath(__file__))
MUN = {"4217204": "Sao Miguel do Oeste", "4208500": "Ituporanga"}
MES = [("jan",3),("fev",3),("mar",3),("abr",3),("mai",3),("jun",3),("jul",3),("ago",3),("set",3),("out",3),("nov",3),("dez",3)]
def rot(i):  # i = 1..36
    m, d = divmod(i-1, 3)
    return "%02d/%02d" % (1+10*d, m+1)   # dd/mm
ORDEM = list(range(10, 37)) + list(range(1, 10))  # circular, comeca 1/abr
CULT = {  # nome no CSV -> chave
 "Milho 1ª Safra":"milho_1safra", "Sorgo Forrageiro":"sorgo_forrageiro_1safra",
 "Sorgo Forrageiro 2ª Safra":"sorgo_forrageiro_2safra", "Sorgo Granífero":"sorgo_granifero_1safra",
 "Sorgo Granífero 2ª Safra":"sorgo_granifero_2safra", "Aveia":"aveia", "Triticale":"triticale",
 "Centeio":"centeio", "Cebola":"cebola", "Cebola Plantio com Bulbinho":"cebola_bulbinho"}
GRUPO = {"20":"I","21":"II","22":"III"}
def ler():
    linhas = []
    for f in ("zarc_2627_smo_itu.csv", "zarc_perene_smo_itu.csv"):
        linhas += list(csv.DictReader(open(os.path.join(AQUI,"ext",f), encoding="utf-8-sig"), delimiter=";"))
    return linhas
def runs(vals):
    """vals: dict dec->risco(>0). devolve blocos contiguos na ordem circular."""
    seq = [d for d in ORDEM if vals.get(d,0) > 0]
    blocos, atual = [], []
    for d in ORDEM:
        if vals.get(d,0) > 0: atual.append(d)
        elif atual: blocos.append(atual); atual = []
    if atual: blocos.append(atual)
    return [{"de": rot(b[0]), "ate": rot(b[-1]), "n_decendios": len(b),
             "risco_min": min(vals[d] for d in b), "risco_max": max(vals[d] for d in b)} for b in blocos]
def main():
    L = ler(); gab = {}; viol = 0; n = 0
    for x in L:
        if x["geocodigo"] not in MUN or x["Nome_cultura"] not in CULT: continue
        c = CULT[x["Nome_cultura"]]; m = MUN[x["geocodigo"]]
        vals = {i:int(x["dec%d"%i]) for i in range(1,37)}
        for v in vals.values():
            n += 1
            if v not in (0,20,30,40): viol += 1
        ciclo = x["Cod_Ciclo"]; solo = x["Cod_Solo"]
        manejo = x["Nome_Outros_Manejos"]
        no = gab.setdefault(m,{}).setdefault(c,{}).setdefault(manejo,{"portaria":x["Portaria"],"ciclos":{}})
        cn = ("grupo_"+GRUPO[ciclo]) if c.startswith(("milho","sorgo","aveia","triticale","centeio")) else "ciclo_"+ciclo
        no["ciclos"].setdefault(cn,{})[("AD%d"%(int(solo)-10)) if int(solo)>=11 else ("solo_tipo_%s"%solo)] = {
            "risco_por_decendio": {rot(i):vals[i] for i in ORDEM if vals[i]>0},
            "janelas": runs(vals),
            "melhor_risco": min([v for v in vals.values() if v>0], default=None)}
    out = {"fonte":"ZARC/MAPA, tabua de risco 2026/27 (SISZARC, dados.agricultura.gov.br)",
     "uso":"GABARITO para conferir a solucao. Nao e entrada do modelo.",
     "convencoes":{"decendio":"chave dd/mm = primeiro dia do decendio de PLANTIO (01, 11, 21)",
       "risco":"20, 30 ou 40 (% de risco climatico); decendio ausente = nao indicado (>40% ou fora de zona)",
       "AD1..AD6":"agua disponivel 24; 31,8; 41,4; 54,6; 72,6; 95,4 mm (raiz 60 cm), Portaria 236/2026 item 1.12",
       "grupo_I_II_III":"ciclos 20, 21, 22 do CSV (milho: 130; 130-150; >150 dias). Mapeamento 20/21/22=I/II/III e dec1=jan: inferido (dicionario de dados nao baixou)",
       "solo_tipo_1_2_3":"sorgo e culturas de inverno nao usam AD; classes 1-3 do CSV (textura)",
       "cebola_ciclo_20_26":"codigos de ciclo do CSV, significado nao confirmado"},
     "milho_2safra":{"existe_no_zarc_sc":False,"nota":"Nao ha portaria ZARC de milho 2a safra para SC em 2026/27 (so milho 1a safra). Analogos: milho_1safra no tronco de jan e sorgo_forrageiro_2safra."},
     "dados":gab}
    json.dump(out, open(os.path.join(AQUI,"zarc_gabarito_sc.json"),"w"), ensure_ascii=False, indent=1)
    # ---------- comparacoes ----------
    R = collections.OrderedDict()
    R["G2"] = {"valores":n, "fora_de_0_20_30_40":viol}
    cob = {m:sorted(gab[m].keys()) for m in gab}
    R["G1_culturas_por_municipio"] = cob
    smo = gab["Sao Miguel do Oeste"]; itu = gab["Ituporanga"]
    # B1-0: milho 1a safra SMO, grupo I, AD4..AD6, ago-set
    B1_geada = {"01/08":6.3,"11/08":4.6,"21/08":3.2,"01/09":1.7,"11/09":0.5,"21/09":0.0,"01/10":0.0,"11/10":0.0}
    tab = {}
    for ad in ["AD2","AD3","AD4","AD5","AD6"]:
        for g in ["grupo_I","grupo_II","grupo_III"]:
            d = smo["milho_1safra"]["Sequeiro"]["ciclos"][g][ad]["risco_por_decendio"]
            tab["%s_%s"%(g,ad)] = {k:d.get(k,0) for k in B1_geada}
    R["B1_0_milho_SMO_ago_out"] = {"geada_B1_em_10_anos":B1_geada,"zarc_risco":tab}
    def primeiro_le(d, lim, ordem):
        for k in ordem:
            if 0 < d.get(k,0) <= lim: return k
    ordem_as = list(B1_geada)
    R["B1_0_primeiro_dec_risco_le20"] = {k:primeiro_le(v,20,ordem_as) for k,v in tab.items()}
    # B1-1: fim da janela no tronco de jan
    fim = {}
    for g in ["grupo_I","grupo_II","grupo_III"]:
        for ad in ["AD4","AD5","AD6"]:
            d = smo["milho_1safra"]["Sequeiro"]["ciclos"][g][ad]["risco_por_decendio"]
            fim["milho_%s_%s"%(g,ad)] = [k for k in ("01/01","11/01","21/01") if k in d]
    for g in ["grupo_I","grupo_II","grupo_III"]:
        d = smo["sorgo_forrageiro_2safra"]["Sequeiro"]["ciclos"][g]["solo_tipo_2"]["risco_por_decendio"]
        fim["sorgo2_%s"%g] = [k for k in ORDEM_K(d)]
    R["B1_1_ultimo_plantio_zarc"] = fim
    # A4-3: media 11/09..21/10 milho x sorgo, SMO
    jan = ["11/09","21/09","01/10","11/10","21/10"]
    comp = {}
    for ad in ["AD1","AD2","AD3","AD4","AD5","AD6"]:
        for g in ["grupo_I","grupo_II","grupo_III"]:
            d = smo["milho_1safra"]["Sequeiro"]["ciclos"][g][ad]["risco_por_decendio"]
            vals = [d.get(k) for k in jan]
            comp.setdefault(ad,{})[g] = {"decendios_indicados":sum(v is not None for v in vals),
                "risco_medio_se_indicado":(round(statistics.mean(v for v in vals if v),1) if any(vals) else None),
                "valores":vals}
    sg = {}
    for g in ["grupo_I","grupo_II","grupo_III"]:
        d = smo["sorgo_forrageiro_1safra"]["Sequeiro"]["ciclos"][g]["solo_tipo_1"]["risco_por_decendio"]
        sg[g] = [d.get(k) for k in jan]
    R["A4_3_milho_x_sorgo_SMO_11set_21out"] = {"milho_por_AD":comp,"sorgo_forrageiro_solo1":sg,
       "sorgo_igual_em_todos_os_solos": all(smo["sorgo_forrageiro_1safra"]["Sequeiro"]["ciclos"][g]["solo_tipo_%d"%s]["risco_por_decendio"]==smo["sorgo_forrageiro_1safra"]["Sequeiro"]["ciclos"][g]["solo_tipo_1"]["risco_por_decendio"] for g in sg for s in (1,2,3))}
    # cebola
    ceb = {}
    for m,dd in (("Sao Miguel do Oeste",smo),("Ituporanga",itu)):
        for manejo in ("Sequeiro","Irrigado"):
            if "cebola" not in dd or manejo not in dd["cebola"]: continue
            j = []; menor = []
            for cn,s in dd["cebola"][manejo]["ciclos"].items():
                for sn,v in s.items():
                    j.append(v["risco_por_decendio"]); menor.append(v["melhor_risco"])
            todos = sorted({k for r in j for k in r}, key=lambda k:ORDEM.index(int(k[3:])*3-3+{"01":1,"11":2,"21":3}[k[:2]]) if False else 0)
            ceb[m+"|"+manejo] = {"combinacoes":len(j),"com_alguma_janela":sum(1 for r in j if r),
                "melhor_risco_mediano":statistics.median(menor), "pct_decendios_20":round(100*sum(1 for r in j for v in r.values() if v==20)/max(1,sum(len(r) for r in j)),1),
                "pct_decendios_40":round(100*sum(1 for r in j for v in r.values() if v==40)/max(1,sum(len(r) for r in j)),1)}
    R["cebola_resumo"] = ceb
    json.dump(R, open(os.path.join(AQUI,"resultados_comparacao.json"),"w"), ensure_ascii=False, indent=1)
    print(json.dumps(R, ensure_ascii=False, indent=1)[:6000])
def ORDEM_K(d):
    # ordem cronologica circular (comeca 1/abr) das chaves
    idx = lambda k: (int(k[3:])-1)*3 + {"01":0,"11":1,"21":2}[k[:2]] + 1
    return sorted(d, key=lambda k: ORDEM.index(idx(k)))
if __name__ == "__main__": main()
