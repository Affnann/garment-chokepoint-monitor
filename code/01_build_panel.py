"""Build the monthly panel of Bangladeshi garment imports into the EU and Japan.

Inputs (data/raw):
  eurostat_eu27_imports_from_BD_hs61_62.csv      EU-27, all transport modes, EUR and 100 kg
  eurostat_eu_imports_from_BD_by_transport_mode.csv  EU, sea / air / all, EUR and kg
  eurostat_usd_per_eur_monthly_avg.csv           monthly average USD per EUR
  comtrade_japan_hs6_aggregated.csv              Japan, HS 61 / 62, USD (CIF) and kg

Output (data/clean/panel.csv): one row per destination x chapter x month.
"""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW, CLEAN = ROOT / "data" / "raw", ROOT / "data" / "clean"
CLEAN.mkdir(parents=True, exist_ok=True)

fx = pd.read_csv(RAW / "eurostat_usd_per_eur_monthly_avg.csv")

eu = pd.read_csv(RAW / "eurostat_eu27_imports_from_BD_hs61_62.csv", dtype={"product": str})
eu = eu.merge(fx, on="month", how="left", validate="many_to_one")
assert eu["usd_per_eur"].notna().all(), "missing exchange rate"
eu = pd.DataFrame({
    "dest": "EU", "chapter": eu["product"], "month": eu["month"],
    "value_usd": eu["value_eur"] * eu["usd_per_eur"],
    "value_usd_fixedfx": eu["value_eur"] * fx.loc[fx["month"].str.startswith("2023"), "usd_per_eur"].mean(),
    "kg": eu["qty_100kg"] * 100,
})

mode = pd.read_csv(RAW / "eurostat_eu_imports_from_BD_by_transport_mode.csv", dtype={"product": str})
mode = mode.merge(fx, on="month", how="left", validate="many_to_one")
mode = pd.DataFrame({
    "dest": "EU", "chapter": mode["product"], "month": mode["month"],
    "value_usd_sea": mode["val_sea_eur"] * mode["usd_per_eur"],
    "kg_sea": mode["kg_sea"], "kg_air": mode["kg_air"], "kg_all_modes": mode["kg_all"],
})
eu = eu.merge(mode, on=["dest", "chapter", "month"], how="left", validate="one_to_one")
assert (eu["kg"].round() == eu["kg_all_modes"].round()).all(), "EU weight differs between datasets"

frames = [eu]
jp_path = RAW / "comtrade_japan_hs6_aggregated.csv"
if jp_path.exists():
    jp = pd.read_csv(jp_path, dtype={"chapter": str})
    frames.append(pd.DataFrame({
        "dest": "JP", "chapter": jp["chapter"], "month": jp["month"],
        "value_usd": jp["value_usd_with_weight"], "value_usd_fixedfx": jp["value_usd_with_weight"],
        "kg": jp["kg"],
    }))
else:
    print("Japan file not found yet: panel has EU only")

panel = pd.concat(frames, ignore_index=True)
panel["uv_usd_per_kg"] = panel["value_usd"] / panel["kg"]
panel["uv_usd_per_kg_fixedfx"] = panel["value_usd_fixedfx"] / panel["kg"]
panel["uv_sea_usd_per_kg"] = panel["value_usd_sea"] / panel["kg_sea"]
panel["air_share_kg"] = panel["kg_air"] / panel["kg_all_modes"]
panel = panel.sort_values(["dest", "chapter", "month"])
panel.to_csv(CLEAN / "panel.csv", index=False)
print(panel.groupby(["dest", "chapter"]).agg(months=("month", "count"), first=("month", "min"), last=("month", "max")))
