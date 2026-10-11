"""Reproduces trend_results.csv from gw_tidy.csv and rainfall.csv.

Per well (post-monsoon depth to water, 2015-2023, wells with >=6 readings):
  - Theil-Sen slope (m/year) and Mann-Kendall-style p-value (Kendall tau vs year)
  - the same after removing the linear effect of monsoon rainfall (residual trend)
  - Spearman correlation of depth with monsoon rainfall
"""
import numpy as np
import pandas as pd
from scipy import stats

gw = pd.read_csv("gw_tidy.csv")
rain = pd.read_csv("rainfall.csv")[["Year", "Actual_Monsoon_mm"]]
post = gw[gw.season == "post"].merge(rain, on="Year")

rows = []
for site, g in post.groupby("Site"):
    g = g.dropna(subset=["Depth"]).sort_values("Year")
    if len(g) < 6:
        rows.append((site, len(g), None, None, None, None, None))
        continue
    slope = stats.theilslopes(g.Depth, g.Year)[0]
    p = stats.kendalltau(g.Year, g.Depth)[1]
    fit = np.polyfit(g.Actual_Monsoon_mm, g.Depth, 1)
    resid = g.Depth - np.polyval(fit, g.Actual_Monsoon_mm)
    slope_adj = stats.theilslopes(resid, g.Year)[0]
    p_adj = stats.kendalltau(g.Year, resid)[1]
    rho = stats.spearmanr(g.Actual_Monsoon_mm, g.Depth)[0]
    rows.append((site, len(g), round(slope, 3), round(p, 3), round(slope_adj, 3), round(p_adj, 3), round(rho, 2)))

out = pd.DataFrame(rows, columns=["Site", "n", "slope_m_yr", "p", "slope_rainadj", "p_adj", "rho_rain"])
out.to_csv("trend_results_reproduced.csv", index=False)
print(out.dropna().sort_values("slope_m_yr").to_string(index=False))
