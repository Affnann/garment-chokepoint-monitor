"""Download the Eurostat data used in the paper.

Writes three files to data/raw:
  eurostat_eu27_imports_from_BD_hs61_62.csv          EU-27 imports from Bangladesh, HS 61 and 62, all modes
  eurostat_eu_imports_from_BD_by_transport_mode.csv  the same imports split by mode of transport
  eurostat_usd_per_eur_monthly_avg.csv               monthly average US dollars per euro

The paper used data downloaded on October 28, 2026 (Comext updated October 16, 2026).
Eurostat revises recent months, so a later download can differ slightly.
"""
from pathlib import Path
import csv
import requests

RAW = Path(__file__).resolve().parents[1] / "data" / "raw"
RAW.mkdir(parents=True, exist_ok=True)
COMEXT = "https://ec.europa.eu/eurostat/api/comext/dissemination/statistics/1.0/data/"
START = "2022-01"


def get(url):
    r = requests.get(url, timeout=120)
    r.raise_for_status()
    j = r.json()
    if "error" in j:
        raise RuntimeError(j["error"])
    return j


def records(j):
    """Turn a JSON-stat response into a list of dicts, one per value."""
    ids, size = j["id"], j["size"]
    order = {}
    for d in ids:
        idx = j["dimension"][d]["category"]["index"]
        order[d] = sorted(idx, key=idx.get)
    out = []
    for k, v in j["value"].items():
        n, rec = int(k), {}
        for i in range(len(ids) - 1, -1, -1):
            d = ids[i]
            rec[d] = order[d][n % size[i]]
            n //= size[i]
        rec["value"] = v
        out.append(rec)
    return out


# 1. EU-27 imports from Bangladesh, chapters 61 and 62, value in euros and quantity in 100 kg
j = get(COMEXT + "DS-045409?format=JSON&lang=en&freq=M&reporter=EU27_2020&partner=BD"
        "&product=61&product=62&flow=1&indicators=VALUE_IN_EUROS&indicators=QUANTITY_IN_100KG"
        f"&sinceTimePeriod={START}")
rows = {}
for r in records(j):
    rows.setdefault((r["product"], r["time"]), {})[r["indicators"]] = r["value"]
with open(RAW / "eurostat_eu27_imports_from_BD_hs61_62.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["product", "month", "value_eur", "qty_100kg"])
    for (p, m), v in sorted(rows.items()):
        w.writerow([p, m, v.get("VALUE_IN_EUROS", ""), v.get("QUANTITY_IN_100KG", "")])

# 2. The same imports by mode of transport (1 = sea, 4 = air; the total sums every mode)
j = get(COMEXT + "DS-059334?format=JSON&lang=en&freq=M&reporter=EU&partner=BD"
        "&product=61&product=62&flow=1&indicators=VALUE_EUR&indicators=QUANTITY_KG"
        f"&sinceTimePeriod={START}")
agg = {}
for r in records(j):
    a = agg.setdefault((r["product"], r["time"]), {"vs": 0, "va": 0, "vt": 0, "qs": 0, "qa": 0, "qt": 0})
    is_value = r["indicators"] == "VALUE_EUR"
    a["vt" if is_value else "qt"] += r["value"]
    if r["transport_mode"] == "1":
        a["vs" if is_value else "qs"] += r["value"]
    if r["transport_mode"] == "4":
        a["va" if is_value else "qa"] += r["value"]
with open(RAW / "eurostat_eu_imports_from_BD_by_transport_mode.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["product", "month", "val_sea_eur", "val_air_eur", "val_all_eur", "kg_sea", "kg_air", "kg_all"])
    for (p, m), a in sorted(agg.items()):
        w.writerow([p, m, a["vs"], a["va"], a["vt"], a["qs"], a["qa"], a["qt"]])

# 3. Monthly average exchange rate, US dollars per euro
j = get("https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/ert_bil_eur_m"
        f"?format=JSON&lang=en&currency=USD&statinfo=AVG&unit=NAC&sinceTimePeriod={START}")
with open(RAW / "eurostat_usd_per_eur_monthly_avg.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["month", "usd_per_eur"])
    for r in sorted(records(j), key=lambda r: r["time"]):
        w.writerow([r["time"], r["value"]])

print("Eurostat files written to", RAW)
