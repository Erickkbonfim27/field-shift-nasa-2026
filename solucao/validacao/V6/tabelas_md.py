"""Gera tabelas.md (janelas do gabarito) a partir de zarc_gabarito_sc.json."""
import json, os
AQUI=os.path.dirname(os.path.abspath(__file__))
G=json.load(open(os.path.join(AQUI,"zarc_gabarito_sc.json")))["dados"]
def fm(v):
    if not v["janelas"]: return "—"
    return "; ".join("%s a %s (%d–%d%%)"%(w["de"],w["ate"],w["risco_min"],w["risco_max"]) if w["risco_min"]!=w["risco_max"] else "%s a %s (%d%%)"%(w["de"],w["ate"],w["risco_min"]) for w in v["janelas"])
out=[]
for m in G:
    out.append("\n### %s — milho 1ª safra (sequeiro, %s)\n"%(m,G[m]["milho_1safra"]["Sequeiro"]["portaria"]))
    out.append("| Grupo | "+" | ".join("AD%d"%i for i in range(1,7))+" |\n|---|"+"---|"*6)
    for g in ("grupo_I","grupo_II","grupo_III"):
        c=G[m]["milho_1safra"]["Sequeiro"]["ciclos"][g]
        out.append("| %s | "%g.replace("grupo_","")+" | ".join(fm(c["AD%d"%i]) if "AD%d"%i in c else "—" for i in range(1,7))+" |")
    for cult,nome in (("sorgo_forrageiro_1safra","Sorgo forrageiro 1ª safra"),("sorgo_forrageiro_2safra","Sorgo forrageiro 2ª safra"),("aveia","Aveia"),("triticale","Triticale"),("centeio","Centeio")):
        c=G[m][cult]["Sequeiro"]
        out.append("\n**%s (%s)**\n"%(nome,c["portaria"]))
        sn=sorted({s for cn in c["ciclos"].values() for s in cn})
        out.append("| Grupo | "+" | ".join(sn)+" |\n|---|"+"---|"*len(sn))
        for g in ("grupo_I","grupo_II","grupo_III"):
            cc=c["ciclos"][g]; out.append("| %s | "%g.replace("grupo_","")+" | ".join(fm(cc[s]) if s in cc else "—" for s in sn)+" |")
    for manejo in ("Sequeiro",):
        c=G[m]["cebola"][manejo]
        out.append("\n**Cebola %s (%s)**, solo AD5 (AD1–AD6 variam; ver JSON)\n"%(manejo.lower(),c["portaria"]))
        out.append("| Ciclo | Janelas (plantio) |\n|---|---|")
        for cn in sorted(c["ciclos"]):
            v=c["ciclos"][cn].get("AD5"); out.append("| %s | %s |"%(cn,fm(v) if v else "—"))
open(os.path.join(AQUI,"tabelas.md"),"w").write("\n".join(out)+"\n")
print("\n".join(out)[:200])
