#!/bin/bash
# Busca cenas Sentinel-2 L2A (Earth Search) sobre Ituporanga, 2019-2024
OUT=raw/s2
for Y in 2019 2020 2021 2022 2023 2024; do
  curl -sS -X POST https://earth-search.aws.element84.com/v1/search -H 'Content-Type: application/json' -d "{
   \"collections\":[\"sentinel-2-l2a\"],
   \"intersects\":{\"type\":\"Point\",\"coordinates\":[-49.601,-27.414]},
   \"datetime\":\"${Y}-01-01T00:00:00Z/${Y}-12-31T23:59:59Z\",
   \"query\":{\"eo:cloud_cover\":{\"lt\":80}},
   \"limit\":200}" > $OUT/stac_$Y.json
done
