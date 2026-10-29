# Garment Chokepoint Monitor

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23734645.svg)](https://doi.org/10.5281/zenodo.23734645)

How shipping chokepoints change the prices and routes of Bangladesh's garment exports.

## What this project does

The European Union is the largest market for Bangladeshi garments, and the ships that carry them normally pass through the Red Sea. When shipping lines began diverting ships away from the Red Sea in December 2023, the question was who would pay for the longer trip. This project builds a monthly dataset of Bangladeshi garment imports (HS chapters 61 and 62) into two destinations and compares them:

- **European Union (EU-27):** its shipments used the Red Sea route.
- **Japan:** its shipments do not pass through the Red Sea.

For each month it computes the price per kilo (unit value = import value / weight) and the quantity, and, for the EU, the share of kilograms arriving by air instead of by sea. The code downloads the public data, builds the clean monthly table, and produces the summary tables, a difference-in-differences comparison, and two figures.

Main result: over the year after the diversions began (December 2023 to November 2024, compared with the same months a year earlier), EU-bound garments became 5.5 percent cheaper per kilo relative to Japan-bound garments (95 percent confidence interval: 2.9 to 8.0 percent). The EU's air share rose from 3.5 to 6.2 percent of kilograms.

## Research paper

Release v1.0.0 is the replication package for Kazi Affnann Azom (2026), "Who Paid for the Red Sea Crisis? Bangladeshi Garment Prices in the EU and Japan," preprint, Zenodo, [https://doi.org/10.5281/zenodo.23770054](https://doi.org/10.5281/zenodo.23770054). The tables and figures in the paper are the files produced by the code here (see the table below).

## What is here

| Folder or file | Contents |
|---|---|
| `analysis_plan.md` | The analysis plan, written before the main comparison was computed, with every later change listed and dated |
| `data/raw/` | The Eurostat data used in the paper (the Japan data must be downloaded; see below) |
| `data/README.md` | Sources, download dates, licenses and variable definitions |
| `code/` | Numbered scripts, run in order |
| `output/tables/`, `output/figures/` | The summary tables and figures, as produced by the code (see below) |

Which output file goes with which part of the paper (v1.0.0):

| File | In the paper |
|---|---|
| `output/tables/table1_summary.csv` | Table 1 |
| `output/tables/table2_did.csv` | Table 2, every row except the placebo |
| `output/tables/table4_extra_checks.csv` | Table 2, placebo row |
| `output/tables/table3_eu_air_share.csv` | Air shares in Section 5 |
| `output/tables/gap_by_month.csv` | Monthly EU minus Japan gap behind the month counts in Section 5 |
| `output/figures/figure1_unit_values.png` | Figure 1 |
| `output/figures/figure2_eu_air_share.png` | Figure 2 |

## How to reproduce the results

The results were produced with Python 3.13 and the package versions pinned in `requirements.txt`.

```
pip install -r requirements.txt
python code/00_download_comtrade.py     # Japan data from UN Comtrade, about an hour
python code/00_download_eurostat.py     # optional: refreshes the Eurostat files already in data/raw
python code/04_check_downloads.py       # compares your downloads with the totals used in the paper
python code/01_build_panel.py           # builds data/clean/panel.csv
python code/02_analysis.py              # Tables 1 and 2, Figures 1 and 2
python code/03_extra_checks.py          # placebo test (added after the main results were seen)
```

Statistics offices revise recent months, so a download made after October 28, 2026 can differ slightly from the one used in the paper. `04_check_downloads.py` shows by how much.

## Licenses

The code is released under the MIT License (see `LICENSE`). The data keep the terms of their sources: Eurostat data may be reused with acknowledgment of the source; UN Comtrade data may not be republished without the United Nations' permission, which is why this repository includes the download script instead of the Japan data. See `data/README.md`.

## How to cite

Azom, Kazi Affnann (2026). *Garment Chokepoint Monitor (v1.0.0: replication package for 'Who Paid for the Red Sea Crisis?')* (Version v1.0.0) [Software]. Zenodo. https://doi.org/10.5281/zenodo.23734646

- This version (v1.0.0): [10.5281/zenodo.23734646](https://doi.org/10.5281/zenodo.23734646)
- All versions (always points to the latest): [10.5281/zenodo.23734645](https://doi.org/10.5281/zenodo.23734645)

See also `CITATION.cff`.
