"""Pre-specified analysis for Paper 4 (see analysis_plan.md).

Reads data/clean/panel.csv. Writes tables to output/tables and figures to output/figures.
"""
from pathlib import Path
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
TAB, FIG = ROOT / "output" / "tables", ROOT / "output" / "figures"
TAB.mkdir(parents=True, exist_ok=True); FIG.mkdir(parents=True, exist_ok=True)

p = pd.read_csv(ROOT / "data" / "clean" / "panel.csv", dtype={"chapter": str})
p["date"] = pd.to_datetime(p["month"] + "-01")

PRE = ("2022-12", "2023-11")
POST = {"main": ("2023-12", "2024-11"), "start_jan2024": ("2024-01", "2024-11")}


def window(df, start, end):
    return df[(df["month"] >= start) & (df["month"] <= end)]


def combine(df, value_col, kg_col):
    """Sum both chapters, then divide, so the combined unit value is weight-weighted."""
    g = df.groupby(["dest", "month"], as_index=False)[[value_col, kg_col]].sum(min_count=1)
    g["chapter"] = "61+62"
    return g


def uv_series(df, value_col, kg_col):
    parts = [df[["dest", "chapter", "month", value_col, kg_col]], combine(df, value_col, kg_col)]
    s = pd.concat(parts, ignore_index=True)
    s["uv"] = s[value_col] / s[kg_col]
    return s


def did(series, post, outcome="uv"):
    """Difference in differences of mean log outcome, EU minus JP, plus a HAC test on the monthly gap."""
    rows = []
    for ch, g in series.groupby("chapter"):
        pre, pst = window(g, *PRE), window(g, *post)
        if pre["dest"].nunique() < 2:
            continue
        lp = lambda d, dest: np.log(d.loc[d["dest"] == dest, outcome]).mean()
        d_eu, d_jp = lp(pst, "EU") - lp(pre, "EU"), lp(pst, "JP") - lp(pre, "JP")
        both = pd.concat([pre.assign(post=0), pst.assign(post=1)])
        wide = both.pivot_table(index=["month", "post"], columns="dest", values=outcome).dropna().reset_index()
        wide["gap"] = np.log(wide["EU"]) - np.log(wide["JP"])
        m = smf.ols("gap ~ post", data=wide).fit(cov_type="HAC", cov_kwds={"maxlags": 3})
        rows.append({"chapter": ch, "months_used": len(wide),
                     "change_EU_log": d_eu, "change_JP_log": d_jp, "did_log": d_eu - d_jp,
                     "did_pct": 100 * (np.exp(d_eu - d_jp) - 1),
                     "hac_coef": m.params["post"], "hac_se": m.bse["post"], "hac_p": m.pvalues["post"],
                     "ci95_low_pct": 100 * (np.exp(m.conf_int().loc["post", 0]) - 1),
                     "ci95_high_pct": 100 * (np.exp(m.conf_int().loc["post", 1]) - 1)})
    return pd.DataFrame(rows)


uv_all = uv_series(p, "value_usd", "kg")
uv_fixed = uv_series(p, "value_usd_fixedfx", "kg")
results = []
for name, post in POST.items():
    results.append(did(uv_all, post).assign(spec=f"unit value, all modes, {name}"))
results.append(did(uv_fixed, POST["main"]).assign(spec="unit value, fixed 2023 exchange rate, main"))
# Sea-only EU against Japan all modes: the EU side drops air shipments.
sea = p.copy()
sea.loc[sea["dest"] == "EU", "value_usd"] = sea.loc[sea["dest"] == "EU", "value_usd_sea"]
sea.loc[sea["dest"] == "EU", "kg"] = sea.loc[sea["dest"] == "EU", "kg_sea"]
results.append(did(uv_series(sea, "value_usd", "kg"), POST["main"]).assign(spec="unit value, EU sea only, main"))
vol = uv_series(p, "value_usd", "kg").rename(columns={"kg": "kg_total"})
results.append(did(vol.assign(uv=vol["kg_total"]), POST["main"]).assign(spec="volume (kg), main"))
res = pd.concat(results, ignore_index=True)
res.to_csv(TAB / "table2_did.csv", index=False)

# Table 1: means before and after, by destination and chapter.
t1 = []
for (dest, ch), g in uv_all.groupby(["dest", "chapter"]):
    for label, (a, b) in {"pre": PRE, "post": POST["main"]}.items():
        w = window(g, a, b)
        t1.append({"dest": dest, "chapter": ch, "period": label, "months": len(w),
                   "mean_uv_usd_per_kg": w["uv"].mean(), "mean_monthly_tonnes": w["kg"].mean() / 1000,
                   "mean_monthly_value_musd": w["value_usd"].mean() / 1e6})
pd.DataFrame(t1).to_csv(TAB / "table1_summary.csv", index=False)

# EU air share before and after.
eu = p[p["dest"] == "EU"].groupby("month", as_index=False)[["kg_air", "kg_all_modes"]].sum()
air = {k: window(eu, a, b) for k, (a, b) in {"pre": PRE, "post": POST["main"]}.items()}
pd.DataFrame([{"period": k, "air_share_kg_pct": 100 * v["kg_air"].sum() / v["kg_all_modes"].sum()}
              for k, v in air.items()]).to_csv(TAB / "table3_eu_air_share.csv", index=False)

# Figure 1: unit values indexed to the pre-window mean, both chapters combined.
fig, ax = plt.subplots(figsize=(7, 3.6))
comb = uv_all[uv_all["chapter"] == "61+62"].copy()
for dest, style in {"EU": "-", "JP": "--"}.items():
    s = comb[comb["dest"] == dest].sort_values("month")
    if s.empty:
        continue
    base = window(s, *PRE)["uv"].mean()
    ax.plot(pd.to_datetime(s["month"] + "-01"), 100 * s["uv"] / base, style, color="black",
            label={"EU": "European Union", "JP": "Japan"}[dest], linewidth=1.2)
ax.axvline(pd.Timestamp("2023-12-01"), color="grey", linewidth=0.8)
ax.set_ylabel("Unit value (Dec 2022–Nov 2023 = 100)")
ax.legend(frameon=False)
ax.spines[["top", "right"]].set_visible(False)
fig.tight_layout(); fig.savefig(FIG / "figure1_unit_values.png", dpi=300)

# Figure 2: EU share of kilograms arriving by air.
fig, ax = plt.subplots(figsize=(7, 3.2))
ax.plot(pd.to_datetime(eu["month"] + "-01"), 100 * eu["kg_air"] / eu["kg_all_modes"], color="black", linewidth=1.2)
ax.axvline(pd.Timestamp("2023-12-01"), color="grey", linewidth=0.8)
ax.set_ylabel("Share arriving by air (% of kg)")
ax.spines[["top", "right"]].set_visible(False)
fig.tight_layout(); fig.savefig(FIG / "figure2_eu_air_share.png", dpi=300)

pd.set_option("display.width", 200)
print(res.round(3).to_string(index=False))
print(pd.read_csv(TAB / "table3_eu_air_share.csv").round(2).to_string(index=False))
