#!/bin/bash
# Baixa o NASA POWER diário (1981–2025) para cada ponto da grade do Oeste de SC.
# Uso: bash safra-segura/scripts/baixar_power.sh   (pula os pontos já baixados)
cd "$(dirname "$0")/../dados/bruto/power" || exit 1
P="PRECTOTCORR,T2M,T2M_MIN,T2M_MAX,RH2M,WS2M,ALLSKY_SFC_SW_DWN"
baixa() {
  lat=$1; lon=$2; f="p_${lat}_${lon}.json"
  [ -s "$f" ] && grep -q '"19810101"' "$f" && grep -q '"RH2M"' "$f" && return   # já tem 1981–2025 e o conjunto completo
  curl -s -m 280 "https://power.larc.nasa.gov/api/temporal/daily/point?parameters=$P&community=AG&longitude=$lon&latitude=$lat&start=19810101&end=20251231&format=JSON" -o "$f"
  echo "$f $(wc -c < "$f")"
}
export -f baixa; export P
xargs -P 5 -L 1 bash -c 'baixa "$0" "$1"' < pontos.txt
