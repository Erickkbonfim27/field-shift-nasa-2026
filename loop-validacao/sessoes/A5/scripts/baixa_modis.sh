#!/bin/bash
# A5-3: baixa MOD13Q1 (NDVI e confiabilidade do pixel) da ORNL DAAC, bloco de 33 x 33 km em Ituporanga,
# composições de 30/set, 16/out e 1º/nov de cada ano (dias 273, 289 e 305; 274/290/306 em ano bissexto).
# Uso: baixa_modis.sh <pasta_saida>
cd "$1"
for y in $(seq 2000 2025); do for b in 250m_16_days_NDVI 250m_16_days_pixel_reliability; do echo "$y $b"; done; done | \
xargs -P 1 -n 2 sh -c 'f="mod13q1_$0_$1.json"; for t in 1 2 3; do [ -s "$f" ] && [ $(wc -c < "$f") -gt 5000 ] && break; curl -s --max-time 400 -H "Accept: application/json" "https://modis.ornl.gov/rst/api/v1/MOD13Q1/subset?latitude=-27.445&longitude=-49.538&band=$1&startDate=A${0}270&endDate=A${0}310&kmAboveBelow=16&kmLeftRight=16" -o "$f"; sleep 5; done; echo "$f $(wc -c < $f)"'
