# Sessão A5 · Cobertura e oferta

Fichas: `../../fichas/A5-1-janela-cobertura.md`, `A5-2-area-cebola-satelite.md` e `A5-3-vigor-cebola-modis.md`.

## Como reproduzir
Precisa de um Python com numpy, scipy, matplotlib, rasterio, shapely e pyproj (`python -m venv venv && venv/bin/pip install numpy scipy matplotlib rasterio shapely pyproj`).

### A5-1 (só a biblioteca padrão e numpy)
```
cd scripts && python3 cobertura.py ../../../dados ../resultados && python3 sensibilidade_cobertura.py ../../../dados ../resultados
python grafico_cobertura.py ../resultados/resultado_cobertura.json ../A5-1_chance_cobertura.png
```

### A5-2 (Sentinel-2; ~115 cenas, ~700 MB intermediários: use uma pasta fora do repositório)
```
python scripts/baixa_ndvi_s2.py $PWD/dados <pasta_s2> 97 2022,2023,2024,2025
python scripts/compostos_s2.py <pasta_s2> <ano>                 # para cada ano
python scripts/classifica_cebola.py <pasta_s2> dados/pam_cebola_ituporanga.json 2024 2022,2024,2025 resultados/resultado_cebola_s2.json
python scripts/grafico_cebola.py <pasta_s2> resultados/resultado_cebola_s2.json A5-2_area_cebola_s2.png
```
As máscaras finais de cebola (`cebola_<ano>.npz`) e do município estão em `dados/s2/`.

### A5-3 (MODIS pela ORNL, já baixado em `dados/modis/`)
```
python scripts/base_chuva_b41.py ../../dados/power_ituporanga.json dados/pam_cebola_ituporanga_2000.json resultados/base_chuva_b41.json
python scripts/analisa_modis.py dados/modis dados/s2 2022,2024,2025 dados/pam_cebola_ituporanga_2000.json resultados/base_chuva_b41.json resultados/resultado_modis_vigor.json A5-3_vigor_modis.png
python scripts/sensibilidade_modis.py resultados/resultado_modis_vigor.json
```

## Avisos
- O código IBGE de Ituporanga é 4208500. O 4208401 do protocolo é Itapiranga.
- No Earth Search, o deslocamento BOA já vem aplicado (`earthsearch:boa_offset_applied`); não subtraia 1000.
- A máscara SCL deixa passar névoa; `compostos_s2.py` tem um filtro extra.
