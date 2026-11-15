#!/bin/bash
# Baixa NDVI MOD13Q1 (250 m, 16 dias) de dez a fev de cada safra, 9x9 km em volta do ponto.
# Uso: baixar_modis.sh <lat> <lon> <prefixo> <mes_ini_doy_ano_anterior> <doy_fim>
LAT=$1; LON=$2; PRE=$3; D0=$4; D1=$5
OUT=$(dirname "$0")/modis
for Y in $(seq ${6:-2001} ${7:-2025}); do
  P=$((Y-1)); F="$OUT/${PRE}_${Y}.json"
  [ -s "$F" ] && grep -q subset "$F" && continue
  for t in 1 2 3; do
    curl -s -m 400 -H "Accept: application/json" "https://modis.ornl.gov/rst/api/v1/MOD13Q1/subset?latitude=$LAT&longitude=$LON&band=250m_16_days_NDVI&startDate=A${P}${D0}&endDate=A${Y}${D1}&kmAboveBelow=4&kmLeftRight=4" -o "$F"
    grep -q subset "$F" && break
    sleep 5
  done
  echo "$Y $(wc -c < "$F")"
done
