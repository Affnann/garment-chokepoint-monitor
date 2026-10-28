"""Checks added after the main results were seen (not in the original plan; reported as such).

1. Placebo: pretend the shock happened in December 2022. Before = Jan-Nov 2022, after = Dec 2022-Nov 2023.
   If EU prices were already falling relative to Japan, this will show a negative estimate too.
2. Month-by-month gap between EU and Japan log unit values, saved to output/tables/gap_by_month.csv
   (the monthly comparisons in Section 5 of the paper come from it).
"""
from pathlib import Path
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

ROOT = Path(__file__).resolve().parents[1]
p = pd.read_csv(ROOT / "data" / "clean" / "panel.csv", dtype={"chapter": str})
g = p.groupby(["dest", "month"], as_index=False)[["value_usd", "kg"]].sum()
g["uv"] = g["value_usd"] / g["kg"]
w = g.pivot(index="month", columns="dest", values="uv").dropna()
w["gap"] = np.log(w["EU"]) - np.log(w["JP"])
w = w.reset_index()


def test(pre, post, label):
    d = w[((w.month >= pre[0]) & (w.month <= pre[1])) | ((w.month >= post[0]) & (w.month <= post[1]))].copy()
    d["post"] = (d.month >= post[0]).astype(int)
    m = smf.ols("gap ~ post", data=d).fit(cov_type="HAC", cov_kwds={"maxlags": 3})
    lo, hi = m.conf_int().loc["post"]
    return {"check": label, "months": len(d), "did_pct": 100 * (np.exp(m.params["post"]) - 1),
            "p": m.pvalues["post"], "ci_low_pct": 100 * (np.exp(lo) - 1), "ci_high_pct": 100 * (np.exp(hi) - 1)}


rows = [test(("2022-01", "2022-11"), ("2022-12", "2023-11"), "placebo: shock in Dec 2022"),
        test(("2022-12", "2023-11"), ("2023-12", "2024-11"), "main (for comparison)")]
out = pd.DataFrame(rows)
out.to_csv(ROOT / "output" / "tables" / "table4_extra_checks.csv", index=False)
w[["month", "gap"]].to_csv(ROOT / "output" / "tables" / "gap_by_month.csv", index=False)
print(out.round(3).to_string(index=False))
print(w.assign(gap_pct=100 * (np.exp(w.gap) - 1))[["month", "gap_pct"]].round(1).to_string(index=False))
