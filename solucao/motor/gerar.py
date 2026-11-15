#!/usr/bin/env python3
"""Gera as saídas do motor, uma por local da spec-v2, e valida contra o contrato.

Uso (da raiz do projeto):  python3 solucao/motor/gerar.py
Escreve solucao/saida/<local>.json (contrato v2.1.0) e solucao/saida/calculos/<local>.json
(séries e tabelas intermediárias que o rastro cita). Sai com código 1 se alguma saída falhar
no schema ou nas regras R1-R15.
"""
import sys
import time
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from motor import config as C  # noqa: E402
from motor import documento as D  # noqa: E402
from motor import validador as V  # noqa: E402
from motor.locais import sao_miguel_do_oeste, ituporanga, quixada  # noqa: E402

LOCAIS = [sao_miguel_do_oeste, ituporanga, quixada]


def main():
    schema = V.carregar_schema()
    ok = True
    for mod in LOCAIS:
        t = time.time()
        doc, calc = mod.avaliar()
        D.gravar(doc, calc, mod.SLUG)
        erros = V.validar(doc, checar_arquivos=True, schema=schema)
        ok = ok and not erros
        n_num = sum(len(e["indicadores"]) for e in doc["estrategias"])
        print(f"{C.rel(C.SAIDA / (mod.SLUG + '.json'))}: {'VÁLIDO' if not erros else str(len(erros)) + ' ERRO(S)'} "
              f"| {len(doc['estrategias'])} estratégias, {n_num} indicadores, {len(doc['alertas'])} alertas, "
              f"{len(doc['cartoes'])} cartões, {len(doc['rastro'])} itens de rastro | {time.time() - t:.1f} s")
        for e in erros:
            print("   -", e)
        for c in doc["cartoes"]:
            print(f"   {c['id']} {c['template_id']} [{c['destino']}] {c['texto']}")
    print("OK: todas as saídas válidas contra o contrato e R1-R15." if ok else "FALHOU: ver erros acima.")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
