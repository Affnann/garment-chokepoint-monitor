# Garment Chokepoint Monitor

How shipping chokepoints change the prices and routes of Bangladesh's garment exports.

Release v1.0.0 is the replication package for Kazi Affnann Azom (2026), "Who Paid for the Red Sea Crisis? Bangladeshi Garment Prices in the EU and Japan," preprint.

The paper compares the price per kilo (unit value) of Bangladeshi garments imported by the European Union, whose shipments used the Red Sea route, with the same goods imported by Japan, whose shipments did not, before and after the shipping diversions that began in December 2023. Over the following year, EU-bound garments became 5.5 percent cheaper per kilo relative to Japan-bound garments (95 percent confidence interval: 2.9 to 8.0 percent).

## What is here

| Folder or file | Contents |
|---|---|
| `analysis_plan.md` | The analysis plan, written before the main comparison was computed, with every later change listed and dated |
| `data/raw/` | The Eurostat data used in the paper (the Japan data must be downloaded; see below) |
| `data/README.md` | Sources, download dates, licenses and variable definitions |
| `code/` | Numbered scripts, run in order |
| `output/tables/`, `output/figures/` | The tables and figures in the paper, as produced by the code |

## How to reproduce the results

You need Python 3.10 or later.

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

## AI use

As stated in the paper, the author used Claude (Anthropic), an AI assistant, to write the code, search for and check sources, and draft and edit text. The author approved the research question, data sources and analysis plan, and checked the results.

## How to cite

See `CITATION.cff`, or use the DOI on this repository's Zenodo record.
