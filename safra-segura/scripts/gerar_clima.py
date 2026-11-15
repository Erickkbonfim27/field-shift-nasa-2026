#!/usr/bin/env python3
"""Gera o pacote de clima do app (Oeste de SC) a partir do NASA POWER.

Entradas (dados/bruto/):
  power/p_<lat>_<lon>.json  NASA POWER diário 1981–2025 (T2M_MIN, T2M_MAX, PRECTOTCORR), grade de 20 pontos
  malha_oeste.json          malha municipal do IBGE (só para desenhar contornos; não entra no cálculo)
  municipios_oeste.json     nomes dos municípios (IBGE)
Saída:
  dados/gerado/pacote.json  lido por montar.py, que injeta no HTML

Também imprime a curva de geada de SMO calculada aqui, para conferir contra a V2 e contra o JS do navegador.
"""
import base64, json, sys, datetime as dt
from pathlib import Path
import numpy as np

RAIZ = Path(__file__).resolve().parent.parent
BRUTO = RAIZ / "dados" / "bruto"
GERADO = RAIZ / "dados" / "gerado"
INI = dt.date(1981, 1, 1)
FIM = dt.date(2025, 12, 31)
NDIAS = (FIM - INI).days + 1


def b64_i16(arr):
    a = np.asarray(arr, dtype="<i2")
    return base64.b64encode(a.tobytes()).decode()


# ---------- células do POWER ----------
celulas = []
for f in sorted((BRUTO / "power").glob("p_*.json")):
    j = json.load(open(f))
    P = j["properties"]["parameter"]
    lon, lat, elev = j["geometry"]["coordinates"]
    dias = sorted(P["T2M_MIN"].keys())
    assert len(dias) == NDIAS, (f, len(dias))
    tmin = [round(P["T2M_MIN"][k] * 10) for k in dias]
    tmax = [round(P["T2M_MAX"][k] * 10) for k in dias]
    chuva = [round(max(0, P["PRECTOTCORR"][k]) * 10) for k in dias]
    lat_req, lon_req = f.stem.split("_")[1:]
    celulas.append(dict(id=f"{lat_req}_{lon_req}", lat=float(lat_req), lon=float(lon_req), elev=round(elev),
                        tmin=b64_i16(tmin), tmax=b64_i16(tmax), chuva=b64_i16(chuva),
                        _tmin=tmin, _tmax=tmax,
                        api=f"https://power.larc.nasa.gov/api/temporal/daily/point?parameters=T2M_MIN,T2M_MAX,PRECTOTCORR&community=AG&longitude={lon_req}&latitude={lat_req}&start=19840101&end=20251231&format=JSON"))

# ---------- municípios: contorno + célula mais próxima do centróide ----------
malha = json.load(open(BRUTO / "malha_oeste.json"))
nomes = {str(m["id"]): m["nome"] for m in json.load(open(BRUTO / "municipios_oeste.json"))}


def centroide(geom):
    pts = []
    polys = geom["coordinates"] if geom["type"] == "MultiPolygon" else [geom["coordinates"]]
    for poly in polys:
        pts += poly[0]
    return sum(p[0] for p in pts) / len(pts), sum(p[1] for p in pts) / len(pts)


for ft in malha["features"]:
    cod = ft["properties"]["codarea"]
    lon, lat = centroide(ft["geometry"])
    c = min(celulas, key=lambda c: (c["lat"] - lat) ** 2 + ((c["lon"] - lon) * 0.8) ** 2)
    ft["properties"] = dict(cod=cod, nome=nomes.get(cod, cod), cel=c["id"], cx=round(lon, 4), cy=round(lat, 4))
    # arredonda coordenadas para diminuir o arquivo
    def rnd(x):
        return [rnd(y) for y in x] if isinstance(x[0], list) else [round(x[0], 4), round(x[1], 4)]
    ft["geometry"]["coordinates"] = rnd(ft["geometry"]["coordinates"])

# ---------- conferência do modelo de geada em Python (mesma regra da V2) ----------
def safra(c, ano, mes, dia, L=3.0, gdd_alvo=1250):
    i = (dt.date(ano, mes, dia) - INI).days
    fim = (dt.date(ano, 9, 30) - INI).days
    soma, geada = 0.0, False
    while soma < gdd_alvo:
        if i > fim or i >= NDIAS:
            return None
        tn, tx = c["_tmin"][i] / 10, c["_tmax"][i] / 10
        if tn <= L:
            geada = True
        soma += max(0.0, (min(tx, 30.0) + max(tn, 10.0)) / 2 - 10.0)
        i += 1
    return geada


smo = next(c for c in celulas if c["id"] == "-26.75_-53.75")
print("Conferência SMO (célula -26,75; -53,75), limiar 3 °C, 1.250 °C·dia, 1981–2025:")
for (m, d) in [(1, 1), (1, 11), (1, 21), (2, 1), (2, 11), (2, 21), (3, 1), (3, 11), (3, 21)]:
    rs = [safra(smo, a, m, d) for a in range(1981, 2026)]
    rs = [r for r in rs if r is not None]
    print(f"  {d:02d}/{m:02d}: {10 * sum(rs) / len(rs):.1f} em 10 (n={len(rs)})")
print("  V2 (1981–2025): 01/01 0,0 · 21/01 0,2 · 01/02 1,1 · 11/02 4,4 · 21/02 6,7 · 01/03 8,9 · 11/03 9,6")

# ---------- módulos do motor validado (solucao/motor), célula a célula ----------
# Usa o código do motor, não uma cópia: as regras ficam iguais às da spec v2.
sys.path.insert(0, str(RAIZ.parent))
from solucao.motor import power as MP, geada as MG, balanco as MB, ano_extremo as MA, estat as ME  # noqa: E402

ANO_INI_SECO = MA.ANO_INICIO_PERCENTIL


def modulos_do_motor(arq):
    pw = MP.Power(str(arq))
    jan = MG.tabela_janela_safra(pw)
    def limite_seguro(L, g):
        # célula fria com ciclo longo: nenhuma safra chega ao ponto até 30/set -> o motor divide por zero
        try:
            return MG.limite_diario(pw, L, g)["limite"]
        except ZeroDivisionError:
            return None
    lim = dict(central=limite_seguro(3.0, MG.GDD_PADRAO),
               por_limiar_c={f"{L:g}": limite_seguro(L, MG.GDD_PADRAO) for L in MG.LIMIARES_2M},
               por_ciclo_gdd={str(g): limite_seguro(3.0, g) for g in MG.GDD_SENS})
    # risco no próprio dia-limite (3 °C, 1.250 °C·dia), com IC de Wilson, como na V2/spec
    # igual ao motor (locais/sao_miguel_do_oeste.py): risco suavizado (média de 5 dias) no dia-limite, Wilson
    risco_lim = None
    if lim["central"]:
        cen = MG.limite_diario(pw, 3.0, MG.GDD_PADRAO)
        d, m = map(int, lim["central"].split("/"))
        i_lim = (dt.date(2001, m, d) - dt.date(2001, 1, 1)).days
        sm = cen["risco_suavizado"][i_lim]
        n = len(MG._safras_dia(pw, m, d, MG.GDD_PADRAO, MG.ANOS_V2))
        lo, hi = ME.wilson(sm * n, n)
        risco_lim = dict(em10=round(10 * sm, 1), ic95=[round(10 * lo, 1), round(10 * hi, 1)], n=n)
    try:
        curva = MG.curva_2m(pw)
    except ZeroDivisionError:
        curva = dict(linhas=[])
    serie = {}
    for a in range(ANO_INI_SECO, 2026):
        v = MB.isna_milho_b31(pw, a)
        if v is not None:
            serie[a] = round(v, 4)
    alertas = []
    for a in sorted(serie):
        passados = [serie[x] for x in serie if ANO_INI_SECO <= x < a]
        if len(passados) >= 10:
            pct = MA.percentil_passado(serie[a], passados)
            if pct is not None and pct <= MA.LIMIAR_PCT:
                alertas.append(dict(ano=a, percentil=pct, n_passados=len(passados)))
    return dict(
        janela_safra=dict(limiar_c=jan["limiar_c"], dias=jan["dias_avaliados"], periodo=jan["anos_plantio"],
                          linhas=[dict(d=l["decendio"], em10=l["em10"], ic95=l["ic95"], n=l["n"]) for l in jan["linhas"]],
                          seguro=MG.primeiro_seguro(jan)),
        limite_2m=dict(central=lim["central"], por_limiar=lim["por_limiar_c"], por_ciclo=lim["por_ciclo_gdd"], risco_no_limite=risco_lim),
        curva_2m=[dict(d=l.get("decendio") or l.get("data"), em10=l["em10"], ic95=l.get("ic95")) for l in curva["linhas"]],
        seco=dict(regra="ISNA do milho de 20/set a 10/jan entre os 10% piores dos anos anteriores da célula (desde 1990)",
                  serie=serie, alertas=alertas),
    )


for c in celulas:
    c["motor"] = modulos_do_motor(BRUTO / "power" / f"p_{c['id']}.json")
smo_m = smo["motor"]
print("Motor, SMO: geada 1/ago", smo_m["janela_safra"]["linhas"][0], "| seguro", smo_m["janela_safra"]["seguro"],
      "| limite 2º milho", smo_m["limite_2m"], "| alertas de ano seco", [a["ano"] for a in smo_m["seco"]["alertas"]])

for c in celulas:
    c.pop("_tmin"); c.pop("_tmax")
pacote = dict(ini=INI.isoformat(), ndias=NDIAS, celulas=celulas, malha=malha,
              meta=dict(power="NASA POWER diário, comunidade AG, T2M_MIN/T2M_MAX/PRECTOTCORR, 1981–2025 (radiação a partir de 1984), grade ~0,5° x 0,625°",
                        gerado="safra-segura/scripts/gerar_clima.py"))
out = GERADO / "pacote.json"
json.dump(pacote, open(out, "w"), separators=(",", ":"), ensure_ascii=False)
print("pacote:", round(out.stat().st_size / 1e6, 2), "MB")
