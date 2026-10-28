# Data

All files cover January 2022 to August 2026 (exchange rates to September 2026). They were downloaded on October 28, 2026.

## Files in `data/raw/`

### `eurostat_eu27_imports_from_BD_hs61_62.csv`
EU-27 imports from Bangladesh in HS chapters 61 (knitted apparel) and 62 (woven apparel), all modes of transport.
- Source: Eurostat, Comext dataset DS-045409, "EU trade since 1988 by HS2-4-6 and CN8" (data updated October 16, 2026).
- Columns: `product` (HS chapter), `month`, `value_eur` (import value in euros, CIF), `qty_100kg` (net weight in units of 100 kg).

### `eurostat_eu_imports_from_BD_by_transport_mode.csv`
The same imports split by the mode of transport at the EU border.
- Source: Eurostat, Comext dataset DS-059334, "Extra-EU trade since 2002 by mode of transport, by HS2-4-6".
- Columns: `val_sea_eur`, `val_air_eur`, `val_all_eur` (values in euros by sea, by air, all modes); `kg_sea`, `kg_air`, `kg_all` (net weight in kg).
- Totals agree with DS-045409: weights match exactly; values differ by €137 out of €89.1 billion.

### `eurostat_usd_per_eur_monthly_avg.csv`
- Source: Eurostat, series ert_bil_eur_m, "Euro/ECU exchange rates: monthly data" (updated October 7, 2026), monthly average, US dollars per euro.

### `comtrade_japan_hs6_aggregated.csv` (not included: created by `code/00_download_comtrade.py`)
Japan's imports from Bangladesh in HS chapters 61 and 62, built by adding up the six-digit product lines in each chapter, because Comtrade's chapter-level records for Japan carry no weights.
- Source: United Nations, UN Comtrade Database, monthly HS data, reporter Japan (392), partner Bangladesh (50), flow imports.
- Columns: `chapter`, `month`, `value_usd_all` (import value in US dollars, CIF), `value_usd_with_weight` (value of the lines that report a weight), `kg` (net weight), `rows` (number of six-digit lines), `est_weight_rows` (lines whose weight Comtrade marks as estimated; 43 of 5,545 in total).
- Comtrade has no record for Japan in April 2026.

## Why Bangladesh's own export statistics are not used
In July 2024, Bangladesh Bank found that export figures for FY2022 to FY2024 reported by the Export Promotion Bureau were overstated, mainly because of accounting errors in garment exports. The paper therefore uses the importers' records.

## Licenses and terms
- **Eurostat:** reuse is free for commercial and non-commercial purposes, with acknowledgment of the source and of any changes made (Eurostat copyright notice). Changes made here: euro values converted to US dollars, and transport modes summed into sea, air and total.
- **UN Comtrade:** the UN Comtrade license agreement does not allow redistribution or publication of its data without the prior written permission of the United Nations Statistics Division (comtrade@un.org). The data are therefore not included; the download script is.
