#!/bin/bash
# Baixa NASA POWER diário (comunidade AG) para os pontos novos da V1. Uso: bash baixa_power.sh
cd "$(dirname "$0")/power"
P="PRECTOTCORR,T2M,T2M_MAX,T2M_MIN,RH2M,WS2M,ALLSKY_SFC_SW_DWN,GWETROOT"
while read nome lat lon; do
  [ -s "power_$nome.json" ] && continue
  curl -s -m 300 -o "power_$nome.json" "https://power.larc.nasa.gov/api/temporal/daily/point?parameters=$P&community=AG&longitude=$lon&latitude=$lat&start=19840101&end=20251231&format=JSON"
  echo "$nome $(wc -c < power_$nome.json)"
done <<PTS
abelardo_luz -26.5624 -52.2557
fraiburgo -27.0378 -50.8724
itaiopolis -26.4721 -49.8912
campos_novos -27.413 -51.2446
sao_jose_do_cerrito -27.5983 -50.6503
treze_de_maio -28.5662 -49.1542
icara -28.7516 -49.2773
turvo -28.9031 -49.7034
quilombo -26.7292 -52.718
ipuacu -26.6787 -52.476
lebon_regis -26.8584 -50.7026
irineopolis -26.3571 -50.7607
campo_alegre -26.1206 -49.2175
curitibanos -27.2929 -50.6175
bom_retiro -27.7854 -49.563
sao_pedro_de_alcantara -27.5916 -48.8371
pedras_grandes -28.4794 -49.2045
PTS
