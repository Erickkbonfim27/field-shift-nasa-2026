"""A5-1: sensibilidade (graus-dia alvo, prazo, critério de morte) e checagem sem modelo (veranicos após a semeadura)."""
import sys, os, datetime as dt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
sys.argv = [sys.argv[0], sys.argv[1], sys.argv[2]]
import cobertura as C

def p_ok(caso, prazo=None, escala=1.0, sp_extra=None):
    nome, arq, esp, ini, fim, prz, hab, lat = [c for c in C.CASOS if c[0] == caso][0]
    prz = prazo or prz
    datas, a = C.carrega(arq, lat)
    sp = dict(C.ESPECIES[esp]); sp.update(sp_extra or {})
    anos = [y for y in range(1984, 2026) if C.prazo_de(y, ini, prz) <= datas[-1]]
    lab = [d.strftime("%d/%m") for d in C.datas_janela(2001, ini, fim)]
    out = []
    for di in range(len(lab)):
        v = []
        for y in anos:
            d = C.datas_janela(y, ini, fim)[di]
            v.append(C.simula(a, C.idx(datas, d), C.idx(datas, C.prazo_de(y, ini, prz)), sp, escala)[0] == "ok")
        out.append(np.mean(v))
    return lab, np.round(out, 2)

def ultima_data(lab, p, lim=0.8):
    ok = [l for l, x in zip(lab, p) if x >= lim]
    return ok[-1] if ok else "nenhuma"

print("== Última data com chance >= 80% de boa cobertura ==")
for caso in ("I-MIL", "I-MUC", "I-AVE", "S-AVE"):
    linha = []
    for esc in (0.8, 1.0, 1.25):
        lab, p = p_ok(caso, escala=esc)
        linha.append(f"g_cob x{esc}: {ultima_data(lab, p)}")
    print(caso, " | ".join(linha))
for prz in ((7, 10), (7, 31), (6, 20)):
    lab, p = p_ok("I-AVE", prazo=prz)
    print("I-AVE prazo", prz, "última data >=80%:", ultima_data(lab, p), "| P(15/04)=", p[lab.index("15/04")])

# veranico: >= 10 dias seguidos com chuva < 1 mm nos 20 dias após a semeadura (sem modelo)
print("\n== Checagem sem modelo: % de anos com veranico >= 10 dias nos 20 dias após semear ==")
for arq, lat, nome in (("power_ituporanga.json", -27.414, "Ituporanga"), ("power_sao_miguel_do_oeste.json", -26.725, "S.M.Oeste")):
    datas, a = C.carrega(arq, lat)
    for (m, d) in ((12, 15), (1, 15), (3, 15), (4, 15), (5, 15)):
        n = 0; tot = 0
        for y in range(1984, 2025):
            i = C.idx(datas, dt.date(y, m, d)); seco = a["PRECTOTCORR"][i:i + 20] < 1
            run = best = 0
            for s in seco:
                run = run + 1 if s else 0; best = max(best, run)
            n += best >= 10; tot += 1
        print(f"  {nome} semeadura {d:02d}/{m:02d}: {100*n/tot:.0f}% dos anos")

print("\n== Critério de morte mais duro (só solo superficial seco por 4 dias) ==")
import types
orig = C.simula
def simula_dura(a, i0, ip, sp, escala=1.0):
    return orig(a, i0, ip, sp, escala)
for caso in ("I-MIL", "I-AVE", "S-AVE"):
    # aproximação: dobra a exigência de emergência úmida e encurta zona de raiz
    lab, p = p_ok(caso, sp_extra={"g_germ": C.ESPECIES[[c for c in C.CASOS if c[0]==caso][0][2]]["g_germ"] * 2, "p": 0.3})
    print(caso, "P mínimo na janela:", p.min(), "| P habitual:", p[lab.index([c for c in C.CASOS if c[0]==caso][0][6][1].__format__('02d') + '/' + [c for c in C.CASOS if c[0]==caso][0][6][0].__format__('02d'))])
