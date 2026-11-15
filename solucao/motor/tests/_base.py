"""Prepara o sys.path para os testes: `python3 -m unittest discover solucao/motor/tests`."""
import sys
from pathlib import Path

sys.dont_write_bytecode = True
SOLUCAO = Path(__file__).resolve().parents[2]
if str(SOLUCAO) not in sys.path:
    sys.path.insert(0, str(SOLUCAO))
