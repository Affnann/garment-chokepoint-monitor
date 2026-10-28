"""Download Japan's imports from Bangladesh (HS 61 and 62) from UN Comtrade.

UN Comtrade's terms do not allow its data to be republished without permission, so this
repository contains this script instead of the data. Running it writes
data/raw/comtrade_japan_hs6_aggregated.csv.

Comtrade's chapter-level records for Japan carry no weights, so the script downloads every
six-digit line (cmdCode=AG6) and adds up the lines in chapters 61 and 62. The free public
endpoint returns one month per request and limits how fast you can ask, so a full run takes
about an hour.

The paper used data downloaded on October 28, 2026.
"""
from pathlib import Path
import csv
import time
import requests

RAW = Path(__file__).resolve().parents[1] / "data" / "raw"
RAW.mkdir(parents=True, exist_ok=True)
URL = ("https://comtradeapi.un.org/public/v1/preview/C/M/HS"
       "?reporterCode=392&partnerCode=50&flowCode=M&cmdCode=AG6&period={p}")  # 392 = Japan, 50 = Bangladesh

months = [f"{y}{m:02d}" for y in range(2022, 2027) for m in range(1, 13) if (y, m) <= (2026, 8)]
rows = []
for p in months:
    for attempt in range(6):
        r = requests.get(URL.format(p=p), timeout=120)
        if r.status_code != 429:
            break
        time.sleep(8)  # rate limited: wait and try again
    r.raise_for_status()
    data = r.json().get("data") or []
    if len(data) >= 500:
        raise RuntimeError(f"{p}: response may be truncated at the preview limit")
    for ch in ("61", "62"):
        lines = [d for d in data if d["cmdCode"].startswith(ch) and len(d["cmdCode"]) == 6
                 and d["partner2Code"] == 0 and d["customsCode"] == "C00" and d["motCode"] == 0]
        if not lines:
            continue  # Comtrade has no record for this month
        rows.append([ch, f"{p[:4]}-{p[4:]}",
                     sum(d["primaryValue"] for d in lines),
                     sum(d["primaryValue"] for d in lines if (d["netWgt"] or 0) > 0),
                     sum(d["netWgt"] or 0 for d in lines),
                     len(lines),
                     sum(1 for d in lines if d["isNetWgtEstimated"])])
    print(p, "done")
    time.sleep(3)

rows.sort()
with open(RAW / "comtrade_japan_hs6_aggregated.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["chapter", "month", "value_usd_all", "value_usd_with_weight", "kg", "rows", "est_weight_rows"])
    w.writerows(rows)
print("Comtrade file written to", RAW)
