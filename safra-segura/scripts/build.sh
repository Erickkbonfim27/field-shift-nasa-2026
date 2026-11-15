#!/bin/bash
# Build completo do Safra Segura.
#   bash safra-segura/scripts/build.sh            -> só monta a página (rápido, usa dados já gerados)
#   bash safra-segura/scripts/build.sh --dados    -> recalcula clima e relevo e depois monta
#   bash safra-segura/scripts/build.sh --baixar   -> baixa o NASA POWER e o SRTM que faltarem, recalcula e monta
set -e
cd "$(dirname "$0")"
if [ "$1" = "--baixar" ]; then bash baixar_power.sh; bash baixar_srtm.sh; fi
if [ "$1" = "--dados" ] || [ "$1" = "--baixar" ]; then
  python3 gerar_clima.py
  python3 gerar_relevo.py
fi
case "$1" in --dados|--baixar) shift ;; esac
python3 montar.py "$@"
