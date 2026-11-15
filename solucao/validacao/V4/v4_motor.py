#!/usr/bin/env python3
"""V4 · Motor composto (o controle reformulado) contra o IBGE PAM.

Critérios escritos antes: 00_criterios_antes.md (não mudar).
Entrada da solução: só NASA POWER (diário, comunidade AG).
Conferência: IBGE PAM (rendimento) e ZARC 2026/27 (janelas), nunca como entrada.
Saída: v4_resultado.json e impressão dos números do relatório.
"""
import json, math, csv, datetime as dt, statistics as st, random
from pathlib import Path
import numpy as np

AQUI = Path(__file__).resolve().parent
PROJ = AQUI.parents[2]
LV = PROJ / "loop-validacao"
DADOS = LV / "dados"
EXTRA = LV / "sessoes" / "B3" / "power_extra"
B1EXT = LV / "sessoes" / "B1" / "externo"
B3EXT = LV / "sessoes" / "B3" / "externo"
ZARC = LV / "sessoes" / "A1" / "ext"

LAMBDA = 3.0          # ridge, fixado antes
LIM_RUIM = 0.85       # ano ruim = rendimento relativo <= 0,85
LIM_COLHE = 0.6       # falha no "x em 10" = y < 0,6 (mesmo corte do protótipo)


# ============================ NASA POWER ============================
def e_sat(t): return 0.6108 * math.exp(17.27 * t / (t + 237.3))


class Power:
    def __init__(self, caminho, alt=None):
        d = json.load(open(caminho))
        lon, lat, alt_json = d["geometry"]["coordinates"]
        self.lat, self.alt = lat, (alt if alt is not None else alt_json)
        self.P = d["properties"]["parameter"]
        self.chuva = {k: max(0.0, v) for k, v in self.P["PRECTOTCORR"].items()}
        self.tmin = self.P["T2M_MIN"]
        self._et0 = {}

    def et0(self, day):
        if day in self._et0: return self._et0[day]
        P = self.P
        vals = [P[x].get(day, -999) for x in ("T2M_MAX", "T2M_MIN", "T2M", "RH2M", "WS2M", "ALLSKY_SFC_SW_DWN")]
        if -999 in vals: self._et0[day] = None; return None
        tmax, tmin, tm, rh, u2, rs = vals
        d = dt.date(int(day[:4]), int(day[4:6]), int(day[6:]))
        es = (e_sat(tmax) + e_sat(tmin)) / 2
        ea = rh / 100 * e_sat(tm)
        delta = 4098 * e_sat(tm) / (tm + 237.3) ** 2
        gam = 0.000665 * 101.3 * ((293 - 0.0065 * self.alt) / 293) ** 5.26
        j = d.timetuple().tm_yday
        phi = math.radians(self.lat)
        dr = 1 + 0.033 * math.cos(2 * math.pi * j / 365)
        dec = 0.409 * math.sin(2 * math.pi * j / 365 - 1.39)
        ws = math.acos(max(-1, min(1, -math.tan(phi) * math.tan(dec))))
        ra = 24 * 60 / math.pi * 0.082 * dr * (ws * math.sin(phi) * math.sin(dec) + math.cos(phi) * math.cos(dec) * math.sin(ws))
        rso = (0.75 + 2e-5 * self.alt) * ra
        rnl = 4.903e-9 * (((tmax + 273.16) ** 4 + (tmin + 273.16) ** 4) / 2) * (0.34 - 0.14 * math.sqrt(max(ea, 0.01))) * (1.35 * min(rs / rso, 1) - 0.35)
        rn = 0.77 * rs - rnl
        num = 0.408 * delta * rn + gam * 900 / (tm + 273) * u2 * (es - ea)
        r = max(0.5, num / (delta + gam * (1 + 0.34 * u2)))
        self._et0[day] = r
        return r


def K(d): return d.strftime("%Y%m%d")


def kc_curva(fases, kc, i):
    ini, dev, mid, late = fases
    a, b, e = kc
    if i < ini: return a
    if i < ini + dev: return a + (b - a) * (i - ini) / dev
    if i < ini + dev + mid: return b
    return b + (e - b) * min(1, (i - ini - dev - mid) / late)


# ---------- balde do controle (B1-0): começa em 70% do CAD no plantio ----------
CULT = {
    "milho": dict(fases=(25, 35, 40, 30), kc=(0.30, 1.20, 0.60), ky=(0.4, 0.4, 1.5, 0.5), cad=175 * 1.0, p=0.55),
    "cebola": dict(fases=(15, 25, 70, 40), kc=(0.70, 1.05, 0.75), ky=(0.45, 0.45, 0.8, 0.3), cad=125 * 0.4, p=0.30),
}


def balde_controle(pw, cult, plantio):
    c = CULT[cult]
    cad, p = c["cad"], c["p"]
    s = 0.7 * cad
    n = sum(c["fases"])
    lim = np.cumsum((0,) + c["fases"])
    eta_f, etc_f, exc_f = [0.0] * 4, [0.0] * 4, [0.0] * 4
    for i in range(n):
        key = K(plantio + dt.timedelta(i))
        e0 = pw.et0(key)
        if e0 is None or key not in pw.chuva: return None
        etc = kc_curva(c["fases"], c["kc"], i) * e0
        s += pw.chuva[key]
        f = int(np.searchsorted(lim, i, side="right") - 1)
        if s > cad: exc_f[f] += s - cad; s = cad
        ks = min(1.0, s / ((1 - p) * cad))
        eta = etc * ks
        s = max(0.0, s - eta)
        eta_f[f] += eta; etc_f[f] += etc
    isna = [a / b if b else 1.0 for a, b in zip(eta_f, etc_f)]
    y = 1.0
    for f in range(4): y *= max(0.0, 1 - c["ky"][f] * (1 - isna[f]))
    isna_veg = (eta_f[0] + eta_f[1]) / (etc_f[0] + etc_f[1])
    return dict(y=y, isna=isna, isna_veg=isna_veg, exc_f=exc_f, lim=lim)


# ---------- balde da B3 (começa cheio 60 dias antes do plantio): usado nos flags pré-registrados ----------
def balde_b3(pw, plantio, fim, fases, kc, cad, p):
    s = cad
    out = []
    d = plantio - dt.timedelta(60)
    while d <= fim:
        key = K(d)
        e0 = pw.et0(key)
        if e0 is None or key not in pw.chuva: return None
        i = (d - plantio).days
        etc = (0.5 if i < 0 else kc_curva(fases, kc, i)) * e0
        s += pw.chuva[key]
        exc = max(0.0, s - cad); s = min(cad, s)
        eta = etc * min(1.0, s / ((1 - p) * cad))
        s = max(0.0, s - eta)
        if i >= 0: out.append((i, d, etc, eta, exc))
        d += dt.timedelta(1)
    return out


def flag_milho(pw, plantio, dias_dec=112):
    """B3-1: ISNA do plantio até 10/jan (112 dias após 20/set), solo médio, fases 25/40/45/30, p=0,5.
    Para outras datas de plantio, a janela anda junto (mesmos 112 dias)."""
    b = balde_b3(pw, plantio, plantio + dt.timedelta(140), (25, 40, 45, 30), (0.30, 1.20, 0.60), 125.0, 0.5)
    if b is None: return None
    g = [x for x in b if x[0] <= dias_dec]
    return sum(x[3] for x in g) / sum(x[2] for x in g)


def exced_cebola(pw, transplante, ini=31, fim=121):
    """B3-2: excedente de 1/set a 30/nov com transplante em 1/ago (dias 31 a 121), raiz 0,3 m, solo médio, p=0,3.
    Para outras datas de transplante, a janela anda junto (dias 31 a 121)."""
    b = balde_b3(pw, transplante, transplante + dt.timedelta(150), (15, 25, 70, 40), (0.70, 1.05, 0.75), 37.5, 0.3)
    if b is None: return None
    return sum(x[4] for x in b if ini <= x[0] <= fim)


def chuva(pw, a, b):
    return sum(pw.chuva[K(a + dt.timedelta(i))] for i in range((b - a).days + 1))


# ============================ variáveis de uma safra ============================
def safra_milho(pw, ano, mes=9, dia=20):
    pl = dt.date(ano - 1, mes, dia)
    r = balde_controle(pw, "milho", pl)
    if r is None: return None
    fl = flag_milho(pw, pl)
    if fl is None: return None
    n3 = int(r["lim"][3])
    geada = sum(1 for i in range(n3) if pw.tmin[K(pl + dt.timedelta(i))] < 2.0)
    exc4 = r["exc_f"][3]
    f_g = max(0.0, 1 - 0.20 * geada)
    f_e = max(0.5, 1 - 0.10 * exc4 / 100)
    y_d1 = r["y"] * f_g * f_e
    rain = chuva(pw, dt.date(ano - 1, 12, 1), dt.date(ano, 2, 28))
    feats = [r["isna_veg"], r["isna"][2], r["isna"][3], geada, exc4, 1.0 if fl < 0.75 else 0.0]
    return dict(ano=ano, y_agua=r["y"], y_d1=y_d1, chuva=rain, geada=geada, exc=exc4, flag_ind=fl,
                flag=fl < 0.75, X_agua=feats[:3], X=feats,
                falha=(y_d1 < LIM_COLHE) or (fl < 0.75) or (geada > 0), falha_agua=r["y"] < LIM_COLHE)


def safra_cebola(pw, ano, mes=7, dia=15, mes_b3=8, dia_b3=1):
    pl = dt.date(ano, mes, dia)
    r = balde_controle(pw, "cebola", pl)
    if r is None: return None
    # excedente e flag com a configuração exata da B3-2/B3-3 (transplante 1/ago na série principal)
    pl3 = dt.date(ano, mes_b3, dia_b3)
    ex = exced_cebola(pw, pl3)
    if ex is None: return None
    n2 = int(r["lim"][2])
    geada = sum(1 for i in range(n2) if pw.tmin[K(pl + dt.timedelta(i))] < 0.0)
    f_g = max(0.0, 1 - 0.05 * geada)
    f_e = max(0.4, 1 - 0.15 * max(0.0, ex - 200) / 100)
    y_d1 = r["y"] * f_g * f_e
    rain = chuva(pw, dt.date(ano, 9, 1), dt.date(ano, 11, 30))
    feats = [r["isna_veg"], r["isna"][2], r["isna"][3], geada, ex, 1.0 if ex >= 360 else 0.0]
    return dict(ano=ano, y_agua=r["y"], y_d1=y_d1, chuva=rain, geada=geada, exc=ex, flag_ind=ex,
                flag=ex >= 360, X_agua=feats[:3], X=feats,
                falha=(y_d1 < LIM_COLHE) or (ex >= 360), falha_agua=r["y"] < LIM_COLHE)


# ============================ IBGE (conferência) ============================
def pam_mun(caminho, produto, municipio):
    out = {}
    for r in json.load(open(caminho))[1:]:
        if r["D4C"] == produto and r["D1C"] == municipio and r["D2N"].startswith("Rendimento") and r["V"] not in ("-", "...", "X", ".."):
            out[int(r["D3N"])] = float(r["V"])
    return out


def pam_micro(arq):
    out = {}
    for r in json.load(open(B3EXT / arq))[1:]:
        if r["D2N"].startswith("Rendimento") and r["V"] not in ("-", "...", "X", ".."):
            out[int(r["D3N"])] = float(r["V"])
    return out


def sem_tendencia(serie, janela=9):
    """B1-0: rendimento / mediana móvel centrada de 9 anos."""
    anos = sorted(serie)
    return {a: serie[a] / st.median([serie[b] for b in anos if abs(b - a) <= janela // 2]) for a in anos}


def rel_b3(serie, raio=3):
    """B3: rendimento / mediana dos vizinhos ±3 anos, sem o próprio ano (sensibilidade)."""
    out = {}
    for a, y in serie.items():
        viz = [serie[b] for b in range(a - raio, a + raio + 1) if b != a and b in serie]
        if len(viz) >= 3: out[a] = y / st.median(viz)
    return out


# ============================ estatística ============================
def rk(v):
    v = np.asarray(v, float)
    o = np.argsort(v, kind="mergesort")
    r = np.empty(len(v))
    i = 0
    while i < len(v):
        j = i
        while j + 1 < len(v) and v[o[j + 1]] == v[o[i]]: j += 1
        r[o[i:j + 1]] = (i + j) / 2 + 1
        i = j + 1
    return r


def rho(a, b):
    ra, rb = rk(a), rk(b)
    if ra.std() == 0 or rb.std() == 0: return 0.0
    return float(np.corrcoef(ra, rb)[0, 1])


def ridge_fit(X, y, lam=LAMBDA):
    X = np.asarray(X, float); y = np.asarray(y, float)
    mu, sd = X.mean(0), X.std(0)
    sd[sd == 0] = 1.0
    Z = (X - mu) / sd
    Z[:, X.std(0) == 0] = 0.0
    beta = np.linalg.solve(Z.T @ Z + lam * np.eye(Z.shape[1]), Z.T @ (y - y.mean()))
    return dict(mu=mu, sd=sd, beta=beta, b0=y.mean(), const=(X.std(0) == 0))


def ridge_pred(m, X):
    Z = (np.asarray(X, float) - m["mu"]) / m["sd"]
    Z[:, m["const"]] = 0.0
    return m["b0"] + Z @ m["beta"]


def ols1_fit(x, y): return ridge_fit(np.asarray(x, float)[:, None], y, lam=0.0)


def preds_fora(linhas, treino_idx_fn):
    """Para cada ano i, treina nos índices de treino_idx_fn(i) e prevê i. Retorna dict de previsões."""
    n = len(linhas)
    y = np.array([s["obs"] for s in linhas])
    X = np.array([s["X"] for s in linhas]); XA = np.array([s["X_agua"] for s in linhas])
    ch = np.array([s["chuva"] for s in linhas]); ya = np.array([s["y_agua"] for s in linhas])
    y1 = np.array([s["y_d1"] for s in linhas])
    out = {k: np.full(n, np.nan) for k in ("clim", "b", "c1lin", "c2", "d1lin", "d2")}
    for i in range(n):
        tr = treino_idx_fn(i)
        if tr is None: continue
        out["clim"][i] = y[tr].mean()
        out["b"][i] = ridge_pred(ols1_fit(ch[tr], y[tr]), [[ch[i]]])[0]
        out["c1lin"][i] = ridge_pred(ols1_fit(ya[tr], y[tr]), [[ya[i]]])[0]
        out["d1lin"][i] = ridge_pred(ols1_fit(y1[tr], y[tr]), [[y1[i]]])[0]
        out["c2"][i] = ridge_pred(ridge_fit(XA[tr], y[tr]), XA[i:i + 1])[0]
        out["d2"][i] = ridge_pred(ridge_fit(X[tr], y[tr]), X[i:i + 1])[0]
    return out


def metricas(linhas, pr, k8=8):
    y = np.array([s["obs"] for s in linhas])
    ok = ~np.isnan(pr["clim"])
    y = y[ok]
    anos = [s["ano"] for s, o in zip(linhas, ok) if o]
    mse_clim = float(np.mean((y - pr["clim"][ok]) ** 2))
    res = {}
    cru = {"b": np.array([s["chuva"] for s in linhas])[ok], "c1": np.array([s["y_agua"] for s in linhas])[ok],
           "d1": np.array([s["y_d1"] for s in linhas])[ok]}
    for nome, v in cru.items():
        res[nome + "_cru"] = dict(rho=round(rho(v, y), 3))
    piores = set(np.array(anos)[np.argsort(y, kind="mergesort")[:k8]])
    for nome in ("b", "c1lin", "c2", "d1lin", "d2"):
        p = pr[nome][ok]
        res[nome] = dict(rho=round(rho(p, y), 3), SS=round(1 - float(np.mean((y - p) ** 2)) / mse_clim, 3),
                         acerto_piores=len(piores & set(np.array(anos)[np.argsort(p, kind="mergesort")[:k8]])))
    res["clim"] = dict(rho=0.0, SS=0.0, acerto_piores_acaso=round(k8 * k8 / len(y), 1))
    res["n"] = int(ok.sum()); res["piores_obs"] = sorted(int(a) for a in piores)
    res["piores_d2"] = sorted(int(a) for a in np.array(anos)[np.argsort(pr["d2"][ok], kind="mergesort")[:k8]])
    return res


def boot_delta(linhas, pr, base, n=2000, seed=7):
    """Fração de reamostras com rho(d2) - rho(base) > 0, e Δρ mediano."""
    y = np.array([s["obs"] for s in linhas])
    d2 = pr["d2"]
    b = pr[base] if base in pr else np.array([s["y_agua"] if base == "c1" else s["chuva"] for s in linhas])
    rnd = np.random.default_rng(seed)
    ds = []
    for _ in range(n):
        idx = rnd.integers(0, len(y), len(y))
        ds.append(rho(d2[idx], y[idx]) - rho(b[idx], y[idx]))
    ds = np.array(ds)
    return dict(frac_pos=round(float((ds > 0).mean()), 3), delta_med=round(float(np.median(ds)), 3),
                p10=round(float(np.percentile(ds, 10)), 3), p90=round(float(np.percentile(ds, 90)), 3))


def montar(pw, serie_rel, fn, anos):
    ls = []
    for a in anos:
        if a not in serie_rel: continue
        s = fn(pw, a)
        if s is None: continue
        s["obs"] = serie_rel[a]
        ls.append(s)
    return ls


def avaliar(nome, linhas):
    n = len(linhas)
    loo = preds_fora(linhas, lambda i: np.array([j for j in range(n) if j != i]))
    m = metricas(linhas, loo)
    m["boot_d2_vs_b"] = boot_delta(linhas, loo, "b")
    m["boot_d2_vs_c1"] = boot_delta(linhas, loo, "c1")
    # pesos do d2 com todos os anos (só para ler o sinal de cada módulo; não usado na avaliação)
    mod = ridge_fit([s["X"] for s in linhas], [s["obs"] for s in linhas])
    m["pesos_d2_todos_padronizados"] = [round(float(b), 4) for b in mod["beta"]]
    # bloco temporal
    anos = np.array([s["ano"] for s in linhas])
    blocos = {}
    for rot, cond_tr in (("treino<=2004_teste>=2005", lambda a: a <= 2004), ("treino>=2005_teste<=2004", lambda a: a >= 2005)):
        tr = np.array([j for j in range(n) if cond_tr(anos[j])])
        pr = preds_fora(linhas, lambda i, tr=tr: None if cond_tr(anos[i]) else tr)
        te = ~np.isnan(pr["d2"])
        y = np.array([s["obs"] for s in linhas])[te]
        blocos[rot] = {k: round(rho(pr[k][te], y), 3) for k in ("b", "c1lin", "c2", "d2")}
        blocos[rot]["c1_cru"] = round(rho(np.array([s["y_agua"] for s in linhas])[te], y), 3)
        blocos[rot]["n_teste"] = int(te.sum())
        mse_c = float(np.mean((y - pr["clim"][te]) ** 2))
        blocos[rot]["SS_d2"] = round(1 - float(np.mean((y - pr["d2"][te]) ** 2)) / mse_c, 3)
    m["bloco"] = blocos
    m["tabela"] = [dict(ano=s["ano"], obs=round(s["obs"], 3), y_agua=round(s["y_agua"], 3), y_d1=round(s["y_d1"], 3),
                        d2_loo=round(float(p), 3), chuva=round(s["chuva"]), geada=s["geada"], exc=round(s["exc"]),
                        flag=bool(s["flag"])) for s, p in zip(linhas, loo["d2"])]
    m["_loo"] = loo
    return m


def transferir(linhas_tr, linhas_te):
    mod = ridge_fit([s["X"] for s in linhas_tr], [s["obs"] for s in linhas_tr])
    p = ridge_pred(mod, [s["X"] for s in linhas_te])
    y = [s["obs"] for s in linhas_te]
    return dict(n=len(y), rho_d2=round(rho(p, y), 3), rho_c1=round(rho([s["y_agua"] for s in linhas_te], y), 3),
                rho_d1=round(rho([s["y_d1"] for s in linhas_te], y), 3), rho_chuva=round(rho([s["chuva"] for s in linhas_te], y), 3))


def flags_tab(linhas):
    al = [s for s in linhas if s["flag"]]
    return dict(n_flag=len(al), ruins_com_flag=sum(s["obs"] <= LIM_RUIM for s in al),
                freq_ruim=round(sum(s["obs"] <= LIM_RUIM for s in linhas) / len(linhas), 3),
                anos=[(s["ano"], round(s["obs"], 2)) for s in al])


def falha_tab(linhas):
    """'x em 10' do motor d1 contra a frequência real de anos ruins."""
    n = len(linhas)
    f = [s for s in linhas if s["falha"]]
    fa = [s for s in linhas if s["falha_agua"]]
    return dict(n=n, falha_motor_em10=round(10 * len(f) / n, 1), falha_agua_em10=round(10 * len(fa) / n, 1),
                ano_ruim_em10=round(10 * sum(s["obs"] <= LIM_RUIM for s in linhas) / n, 1),
                precisao_motor=round(sum(s["obs"] <= LIM_RUIM for s in f) / len(f), 2) if f else None,
                precisao_agua=round(sum(s["obs"] <= LIM_RUIM for s in fa) / len(fa), 2) if fa else None,
                anos_falha_motor=[(s["ano"], round(s["obs"], 2)) for s in f])


# ============================ ZARC (conferência) ============================
DEC = [(m, d) for m in range(1, 13) for d in (1, 11, 21)]  # dec1 = 01/jan ... dec36 = 21/dez


def zarc(cultura_prefixo, municipio, manejo="Sequeiro", exato=True):
    rows = []
    for arq in ("zarc_2627_smo_itu.csv", "zarc_perene_smo_itu.csv"):
        r = csv.reader(open(ZARC / arq, encoding="utf-8-sig"), delimiter=";")
        next(r)
        for x in r:
            ok_nome = (x[0] == cultura_prefixo) if exato else x[0].startswith(cultura_prefixo)
            if ok_nome and x[8] == municipio and x[12] == manejo:
                rows.append(dict(ciclo=x[4], solo=x[5], risco=[int(v) for v in x[19:55]]))
    return rows


# ============================ execução ============================
if __name__ == "__main__":
    res = {}
    smo = Power(DADOS / "power_sao_miguel_do_oeste.json", alt=533.0)
    itu = Power(DADOS / "power_ituporanga.json", alt=677.0)
    cha = Power(EXTRA / "power_chapeco.json")
    con = Power(EXTRA / "power_concordia.json")
    rds = Power(EXTRA / "power_rio_do_sul.json")
    alw = Power(EXTRA / "power_alfredo_wagner.json")

    G = {}
    G["G1_milho_mun_SMO"] = montar(smo, sem_tendencia(pam_mun(B1EXT / "pam_5457.json", "40122", "4217204")), safra_milho, range(1985, 2026))
    G["G2_milho_micro_42001"] = montar(smo, sem_tendencia(pam_micro("milho_micro_smo.json")), safra_milho, range(1990, 2026))
    G["G3a_milho_micro_42002_Chapeco"] = montar(cha, sem_tendencia(pam_micro("milho_micro_42002.json")), safra_milho, range(1990, 2026))
    G["G3b_milho_micro_42005_Concordia"] = montar(con, sem_tendencia(pam_micro("milho_micro_42005.json")), safra_milho, range(1990, 2026))
    G["G4_cebola_mun_Itu"] = montar(itu, sem_tendencia(pam_mun(B1EXT / "pam_cebola_ituporanga.json", "40107", "4208500")), safra_cebola, range(1984, 2026))
    G["G5_cebola_micro_42014"] = montar(itu, sem_tendencia(pam_micro("cebola_micro_ituporanga.json")), safra_cebola, range(1990, 2026))
    G["G6_cebola_micro_42011_RioDoSul"] = montar(rds, sem_tendencia(pam_micro("cebola_micro_42011.json")), safra_cebola, range(1990, 2026))
    G["G6b_cebola_micro_42017_Tabuleiro_mesma_celula"] = montar(alw, sem_tendencia(pam_micro("cebola_micro_42017.json")), safra_cebola, range(1990, 2026))

    loos = {}
    for nome, ls in G.items():
        m = avaliar(nome, ls)
        loos[nome] = m.pop("_loo")
        m["flag"] = flags_tab(ls)
        m["x_em_10"] = falha_tab(ls)
        res[nome] = m

    # sensibilidade: tendência pela regra da B3 (vizinhos ±3 sem o ano)
    sens = {}
    for nome, (pw, serie, fn, anos) in {
        "G1_milho_mun_SMO": (smo, pam_mun(B1EXT / "pam_5457.json", "40122", "4217204"), safra_milho, range(1985, 2026)),
        "G2_milho_micro_42001": (smo, pam_micro("milho_micro_smo.json"), safra_milho, range(1990, 2026)),
        "G4_cebola_mun_Itu": (itu, pam_mun(B1EXT / "pam_cebola_ituporanga.json", "40107", "4208500"), safra_cebola, range(1984, 2026)),
        "G5_cebola_micro_42014": (itu, pam_micro("cebola_micro_ituporanga.json"), safra_cebola, range(1990, 2026)),
    }.items():
        m = avaliar(nome, montar(pw, rel_b3(serie), fn, anos)); m.pop("_loo")
        sens[nome] = {k: m[k] for k in ("n", "b", "c1_cru", "c1lin", "c2", "d1_cru", "d2")}
    res["sensibilidade_tendencia_B3"] = sens
    # sensibilidade: cebola com transplante 1/ago no balde do controle (igual à B3)
    m = avaliar("G4_1ago", montar(itu, sem_tendencia(pam_mun(B1EXT / "pam_cebola_ituporanga.json", "40107", "4208500")),
                                   lambda pw, a: safra_cebola(pw, a, 8, 1), range(1984, 2026))); m.pop("_loo")
    res["sensibilidade_cebola_transplante_1ago"] = {k: m[k] for k in ("n", "b", "c1_cru", "c2", "d1_cru", "d2")}
    # sensibilidade: d2 sem o flag (o flag é redundante com o ISNA?) e só água + 1 módulo
    def abl(ls, cols):
        L = [dict(s, X=[s["X"][c] for c in cols]) for s in ls]
        n = len(L)
        pr = preds_fora(L, lambda i: np.array([j for j in range(n) if j != i]))
        y = [s["obs"] for s in L]
        mse_c = float(np.mean((np.array(y) - pr["clim"]) ** 2))
        return dict(rho=round(rho(pr["d2"], y), 3), SS=round(1 - float(np.mean((np.array(y) - pr["d2"]) ** 2)) / mse_c, 3))
    res["ablacao"] = {}
    for nome in ("G1_milho_mun_SMO", "G2_milho_micro_42001", "G4_cebola_mun_Itu", "G5_cebola_micro_42014"):
        ls = G[nome]
        res["ablacao"][nome] = {
            "agua(0,1,2)": abl(ls, [0, 1, 2]), "agua+geada": abl(ls, [0, 1, 2, 3]), "agua+excesso": abl(ls, [0, 1, 2, 4]),
            "agua+flag": abl(ls, [0, 1, 2, 5]), "so_flag": abl(ls, [5]), "so_excesso": abl(ls, [4]), "so_geada": abl(ls, [3]),
            "motor_completo": abl(ls, [0, 1, 2, 3, 4, 5])}

    # fora da região: treina em G2 / G5 e aplica sem reajuste
    res["fora_regiao"] = {
        "milho_G2->Chapeco": transferir(G["G2_milho_micro_42001"], G["G3a_milho_micro_42002_Chapeco"]),
        "milho_G2->Concordia": transferir(G["G2_milho_micro_42001"], G["G3b_milho_micro_42005_Concordia"]),
        "cebola_G5->RioDoSul": transferir(G["G5_cebola_micro_42014"], G["G6_cebola_micro_42011_RioDoSul"]),
        "cebola_G5->Tabuleiro(mesma celula)": transferir(G["G5_cebola_micro_42014"], G["G6b_cebola_micro_42017_Tabuleiro_mesma_celula"]),
    }

    # ======= decisões: "x em 10" por decêndio com o motor d1 =======
    jan_m = []
    for mes, dia in [(8, 1), (8, 11), (8, 21), (9, 1), (9, 11), (9, 21), (10, 1), (10, 11), (10, 21), (11, 1), (11, 11), (11, 21), (12, 1), (12, 11), (12, 21)]:
        ls = [s for a in range(1985, 2026) if (s := safra_milho(smo, a, mes, dia))]
        jan_m.append(dict(data=f"{dia:02d}/{mes:02d}", n=len(ls),
                          falha_motor=round(10 * sum(s["falha"] for s in ls) / len(ls), 1),
                          falha_agua=round(10 * sum(s["falha_agua"] for s in ls) / len(ls), 1),
                          geada_em10=round(10 * sum(s["geada"] > 0 for s in ls) / len(ls), 1),
                          flag_em10=round(10 * sum(s["flag"] for s in ls) / len(ls), 1),
                          y_d1_med=round(st.median(s["y_d1"] for s in ls), 2)))
    zm = zarc("Milho 1ª Safra", "São Miguel do Oeste")
    for j in jan_m:
        d, m_ = int(j["data"][:2]), int(j["data"][3:])
        idx = DEC.index((m_, d))
        j["zarc_risco_solos_14_16"] = sorted({r["risco"][idx] for r in zm if r["solo"] in ("14", "15", "16")})
    res["decisao_D1_data_milho_SMO"] = jan_m

    jan_c = []
    for mes, dia in [(6, 1), (6, 11), (6, 21), (7, 1), (7, 11), (7, 21), (8, 1), (8, 11), (8, 21), (9, 1), (9, 11), (9, 21)]:
        ls = [s for a in range(1984, 2026) if (s := safra_cebola(itu, a, mes, dia, mes, dia))]
        jan_c.append(dict(data=f"{dia:02d}/{mes:02d}", n=len(ls),
                          falha_motor=round(10 * sum(s["falha"] for s in ls) / len(ls), 1),
                          falha_agua=round(10 * sum(s["falha_agua"] for s in ls) / len(ls), 1),
                          flag_em10=round(10 * sum(s["flag"] for s in ls) / len(ls), 1),
                          y_d1_med=round(st.median(s["y_d1"] for s in ls), 2)))
    zc = zarc("Cebola", "Ituporanga")
    for j in jan_c:
        d, m_ = int(j["data"][:2]), int(j["data"][3:])
        idx = DEC.index((m_, d))
        v = [r["risco"][idx] for r in zc]
        j["zarc_n_linhas_20pct"] = sum(1 for x in v if x == 20)
        j["zarc_n_linhas_indicado"] = sum(1 for x in v if x > 0)
        j["zarc_n_linhas_total"] = len(v)
    res["decisao_D2_transplante_cebola_Itu"] = jan_c

    json.dump(res, open(AQUI / "v4_resultado.json", "w"), ensure_ascii=False, indent=1, default=lambda o: o.item() if hasattr(o, "item") else str(o))

    # ======= impressão =======
    for nome in G:
        m = res[nome]
        print(f"\n== {nome} (n={m['n']})")
        print(f"  cru: chuva {m['b_cru']['rho']}  agua(c1) {m['c1_cru']['rho']}  d1 {m['d1_cru']['rho']}")
        for k in ("b", "c1lin", "c2", "d1lin", "d2"):
            print(f"  LOO {k:6s} rho {m[k]['rho']:+.3f}  SS {m[k]['SS']:+.3f}  piores8 {m[k]['acerto_piores']}")
        print("  acaso piores8:", m["clim"]["acerto_piores_acaso"], " piores obs", m["piores_obs"], " piores d2", m["piores_d2"])
        print("  boot d2-b", m["boot_d2_vs_b"], " d2-c1", m["boot_d2_vs_c1"])
        print("  pesos d2 (vegISNA, florISNA, matISNA, geada, excesso, flag):", m["pesos_d2_todos_padronizados"])
        print("  bloco", m["bloco"])
        print("  flag", m["flag"])
        print("  x em 10", {k: v for k, v in m["x_em_10"].items() if k != "anos_falha_motor"})
    print("\nsens tendência B3:", json.dumps(res["sensibilidade_tendencia_B3"], ensure_ascii=False))
    print("\nsens cebola 1/ago:", json.dumps(res["sensibilidade_cebola_transplante_1ago"], ensure_ascii=False))
    print("\nablação:", json.dumps(res["ablacao"], ensure_ascii=False, indent=0))
    print("\nfora da região:", json.dumps(res["fora_regiao"], ensure_ascii=False, indent=0))
    print("\nD1 milho:")
    for j in jan_m: print("  ", j)
    print("\nD2 cebola:")
    for j in jan_c: print("  ", j)
