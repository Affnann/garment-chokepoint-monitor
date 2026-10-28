"""Compare freshly downloaded data with the totals used in the paper.

Run after 00_download_eurostat.py and 00_download_comtrade.py. Small differences can come
from revisions the statistics offices made after October 28, 2026; large ones mean
something went wrong.
"""
from pathlib import Path
import pandas as pd

RAW = Path(__file__).resolve().parents[1] / "data" / "raw"
PAPER = {  # totals for January 2022 to August 2026, as downloaded on October 28, 2026
    ("eurostat_eu27_imports_from_BD_hs61_62.csv", "value_eur"): 89_084_766_180,
    ("eurostat_eu27_imports_from_BD_hs61_62.csv", "qty_100kg"): 59_152_447.48,
    ("eurostat_eu_imports_from_BD_by_transport_mode.csv", "kg_air"): 262_850_634,
    ("eurostat_eu_imports_from_BD_by_transport_mode.csv", "kg_all"): 5_915_244_748,
    ("eurostat_usd_per_eur_monthly_avg.csv", "usd_per_eur"): 62.6164,  # January 2022 to September 2026
    ("comtrade_japan_hs6_aggregated.csv", "value_usd_all"): 5_986_552_463.98,
    ("comtrade_japan_hs6_aggregated.csv", "kg"): 321_464_837.883,
}
for (file, col), expected in PAPER.items():
    path = RAW / file
    if not path.exists():
        print(f"MISSING  {file}")
        continue
    got = pd.read_csv(path)[col].sum()
    diff = 100 * (got - expected) / expected
    flag = "OK      " if abs(diff) < 0.01 else "DIFFERS "
    print(f"{flag}{file} {col}: paper {expected:,.2f}, now {got:,.2f} ({diff:+.3f}%)")
