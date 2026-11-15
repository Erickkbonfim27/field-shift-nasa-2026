#!/bin/bash
# Baixa as folhas SRTM 1" (tiles públicos "skadi", NASA/USGS) que cobrem o Oeste de SC.
# Uso: bash safra-segura/scripts/baixar_srtm.sh   (pula as folhas já baixadas)
cd "$(dirname "$0")/../dados/bruto" || exit 1
mkdir -p srtm && cd srtm || exit 1
for t in S27W054 S27W053 S27W052 S27W051 S28W054 S28W053 S28W052 S28W051; do
  [ -s "$t.hgt.gz" ] && continue
  curl -s -m 280 -o "$t.hgt.gz" "https://s3.amazonaws.com/elevation-tiles-prod/skadi/${t:0:3}/$t.hgt.gz" && echo "$t $(wc -c < "$t.hgt.gz")" &
done
wait
