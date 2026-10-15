"""Tables for the Power BI report (CSV, one per visual family). Values come from data/sea_quarterly_clean.csv;
ratios are computed the same way as in the Excel model.

Quarterly.csv  one row per quarter, Shopee and Monee measures
Drivers.csv    YoY marketplace-revenue growth split into orders / order value / take rate (last 8 quarters)
Scenarios.csv  FY2026 Shopee adjusted EBITDA: H1 actual + H2 scenario (same assumptions as Target_2026 sheet)
"""
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).parent
OUT = HERE / "data"
OUT.mkdir(exist_ok=True)
d = pd.read_csv(HERE.parent / "data" / "sea_quarterly_clean.csv")

q = pd.DataFrame({
    "Period": d.period,
    "Label": d.period.str[2:4] + "Q" + d.period.str[-1],
    "Sort": range(1, len(d) + 1),
    "Half": np.where(d.quarter <= 2, "H1", "H2"),
    "QuarterEnd": (pd.PeriodIndex(d.period, freq="Q").end_time.normalize()).strftime("%Y-%m-%d"),  # date axis fits 30 quarters without scrolling
    "GMV_bn": d.gmv_usd_bn,
    "Orders_bn": d.gross_orders_bn,
    "AOV": d.gmv_usd_bn / d.gross_orders_bn,
    "CoreTake": d.core_marketplace_usd_m / (d.gmv_usd_bn * 1000),
    "VASTake": d.vas_usd_m / (d.gmv_usd_bn * 1000),
    "MarketplaceTake": d.marketplace_usd_m / (d.gmv_usd_bn * 1000),
    "EBITDA_m": d.shopee_adj_ebitda_usd_m,
    "EBITDA_GMV": d.shopee_adj_ebitda_usd_m / (d.gmv_usd_bn * 1000),
    "EBITDA_per_order": d.shopee_adj_ebitda_usd_m / (d.gross_orders_bn * 1000),
    "Loans_bn": d.loans_usd_bn,
    "LoanBasis": d.loans_basis.fillna(""),
    "NPL": d.npl_90d_pct / 100,
    "MoneeRevenue_m": d.monee_revenue_usd_m,
    "MoneeEBITDA_m": d.monee_adj_ebitda_usd_m,
})
q["MoneeMargin"] = q.MoneeEBITDA_m / q.MoneeRevenue_m
prev = q.shift(4)
same = q.LoanBasis.eq(prev.LoanBasis) & q.LoanBasis.ne("")
q["LoanYoY"] = np.where(same, q.Loans_bn / prev.Loans_bn - 1, np.nan)
q["NPL_Seasoned"] = np.where(same & q.NPL.notna(), q.NPL * q.Loans_bn / prev.Loans_bn, np.nan)
q["CurrentLoanBasis"] = q.LoanBasis.str.startswith("principal")
q["GMV_YoY"] = q.GMV_bn / prev.GMV_bn - 1
assert abs(q.CoreTake.iloc[-1] - 0.1111) < 0.0005 and abs(q.EBITDA_GMV.iloc[-1] - 0.00667) < 0.00005  # matches Excel
q.to_csv(OUT / "Quarterly.csv", index=False, float_format="%.6f")

# growth drivers (same log decomposition as the Growth_Drivers sheet), in percentage points of YoY growth
rows = []
for i in range(len(q) - 8, len(q)):
    o = np.log(q.Orders_bn[i] / q.Orders_bn[i - 4])
    a = np.log(q.AOV[i] / q.AOV[i - 4])
    t = np.log(q.MarketplaceTake[i] / q.MarketplaceTake[i - 4])
    total = np.exp(o + a + t) - 1
    for k, (name, part) in enumerate((("More orders", o), ("Order value", a), ("Higher take rate", t))):
        rows.append({"Label": q.Label[i], "Sort": q.Sort[i], "Component": name, "ComponentSort": k + 1,
                     "Contribution": part / (o + a + t) * total})
pd.DataFrame(rows).to_csv(OUT / "Drivers.csv", index=False, float_format="%.6f")

# FY2026 scenarios (mirror of Target_2026 sheet)
by = q.set_index("Period")
h1 = by.loc[["2026Q1", "2026Q2"], "EBITDA_m"].sum()
g = by.loc[["2026Q1", "2026Q2"], "GMV_bn"].sum() / by.loc[["2025Q1", "2025Q2"], "GMV_bn"].sum() - 1
h2gmv25 = by.loc[["2025Q3", "2025Q4"], "GMV_bn"].sum()
m_h2_25 = by.loc[["2025Q3", "2025Q4"], "EBITDA_m"].sum() / (h2gmv25 * 1000)
m_h1_26 = h1 / (by.loc[["2026Q1", "2026Q2"], "GMV_bn"].sum() * 1000)
m_q2_26 = by.at["2026Q2", "EBITDA_m"] / (by.at["2026Q2", "GMV_bn"] * 1000)
season = by.loc[["2025Q3", "2025Q4"], "EBITDA_m"].sum() / by.loc[["2025Q1", "2025Q2"], "EBITDA_m"].sum()
sc = [("2025 H2 dip", 1, h1 * season), ("Bear", 2, h2gmv25 * (1 + g - 0.05) * 1000 * m_h2_25),
      ("Base", 3, h2gmv25 * (1 + g) * 1000 * m_h1_26), ("Bull", 4, h2gmv25 * (1 + g + 0.03) * 1000 * m_q2_26)]
s = pd.DataFrame([{"Scenario": n, "Sort": k, "H1_actual": h1, "H2": h2, "FY": h1 + h2, "Target": 1000.0} for n, k, h2 in sc])
assert round(s.FY[2], 1) == 1043.2 and round(s.FY[1], 1) == 962.1 and round(s.FY[0], 1) == 856.4  # matches Excel
s.to_csv(OUT / "Scenarios.csv", index=False, float_format="%.4f")
print(s[["Scenario", "FY"]].round(1).to_string(index=False))
