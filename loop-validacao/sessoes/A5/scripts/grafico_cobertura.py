"""A5-1: gráfico da chance de boa cobertura por data de semeadura (com faixa de sensibilidade dos graus-dia)."""
import json, sys
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
R = json.load(open(sys.argv[1]))
nomes = {"I-MIL": "Ituporanga · milheto (após a cebola) · prazo 30/abr",
         "I-MUC": "Ituporanga · mucuna-preta (após a cebola) · prazo 30/abr",
         "I-AVE": "Ituporanga · aveia-preta (antes da cebola) · prazo 10/jul",
         "S-AVE": "São Miguel do Oeste · aveia-preta (após o milho) · prazo 15/ago"}
fig, axs = plt.subplots(4, 1, figsize=(9, 11))
for ax, (k, r) in zip(axs, R.items()):
    x = range(len(r["datas"]))
    s = r["sensibilidade_gcob"]
    ax.fill_between(x, [100*v for v in s["1.25"]], [100*v for v in s["0.8"]], color="#9ecae1", alpha=.5, label="faixa: graus-dia alvo −20% a +25%")
    ax.plot(x, [100*v for v in r["p_todos"]], color="#08519c", lw=2, label="chance de boa cobertura no prazo (1984–2024)")
    h = r["datas"].index(r["habitual"])
    ax.axvline(h, color="#d94801", ls="--", label=f"data habitual ({r['habitual']})")
    ax.axhline(80, color="grey", lw=.8, ls=":")
    ax.set_title(nomes[k], fontsize=10); ax.set_ylim(-3, 103); ax.set_ylabel("% dos anos")
    step = max(1, len(x)//10)
    ax.set_xticks(list(x)[::step]); ax.set_xticklabels(r["datas"][::step], fontsize=8)
    if k == "I-MIL": ax.legend(fontsize=7, loc="lower left")
axs[-1].set_xlabel("data de semeadura")
fig.suptitle("A5-1 · Chance de cobrir bem o solo antes do prazo, por data de semeadura (NASA POWER)", fontsize=11)
fig.tight_layout(); fig.savefig(sys.argv[2], dpi=110)
