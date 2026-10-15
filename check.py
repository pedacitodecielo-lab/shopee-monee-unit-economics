"""Data-quality checks on data/sea_quarterly.csv, plus the cleaned table used by the model.

1. Reported YoY growth vs YoY computed from our own extracted values (catches wrong numbers).
2. Prior-year adjusted EBITDA in each release vs what Sea first reported a year earlier (catches restatements).
3. Sum of four quarters vs Sea's full-year figure in each Q4 release (catches missing or wrong quarters).
4. Gaps: Q1 and Q2 2023 have no GMV or orders in Sea's releases. They are derived from the YoY growth
   Sea reported a year later (2024Q1/Q2) and flagged as derived, then tested against the FY2023 total.
Writes data/checks.md and data/sea_quarterly_clean.csv.
"""
import html
import json
import re
from pathlib import Path

import pandas as pd

HERE = Path(__file__).parent
D = HERE / "data"
df = pd.read_csv(D / "sea_quarterly.csv").set_index("period")
out = ["# Data checks", ""]

# 4. fill the 2023H1 gap from next year's reported growth (Sea's own numbers, flagged)
df["gmv_source"] = df["gmv_usd_bn"].notna().map({True: "reported", False: ""})
df["orders_source"] = df["gross_orders_bn"].notna().map({True: "reported", False: ""})
for p in df.index:
    nxt = f"{int(p[:4]) + 1}{p[4:]}"
    if nxt not in df.index:
        continue
    for col, yoy, src in (("gmv_usd_bn", "gmv_yoy_pct", "gmv_source"), ("gross_orders_bn", "orders_yoy_pct", "orders_source")):
        if pd.isna(df.at[p, col]) and pd.notna(df.at[nxt, col]) and pd.notna(df.at[nxt, yoy]):
            df.at[p, col] = round(df.at[nxt, col] / (1 + df.at[nxt, yoy] / 100), 3)
            df.at[p, src] = f"derived from {nxt} YoY"

# 1. reported vs computed YoY (values are rounded to 0.1 bn, so allow the rounding band)
out += ["## 1. Reported YoY vs computed YoY", "", "| period | metric | reported % | computed % | allowed gap | ok |", "|---|---|---|---|---|---|"]
bad = 0
for p in df.index:
    prev = f"{int(p[:4]) - 1}{p[4:]}"
    if prev not in df.index:
        continue
    for col, yoy in (("gmv_usd_bn", "gmv_yoy_pct"), ("gross_orders_bn", "orders_yoy_pct")):
        a, b, rep = df.at[p, col], df.at[prev, col], df.at[p, yoy]
        if pd.isna(a) or pd.isna(b) or pd.isna(rep) or "derived" in df.at[p, col.replace("_usd_bn", "_source").replace("gross_orders_bn", "orders_source")]:
            continue
        comp = (a / b - 1) * 100
        step = 0.05 if a >= 1 else 0.00005  # rounding unit of the printed value (0.1 bn or 0.1 m)
        tol = (1 + rep / 100) * (step / a + step / b) * 100 + 0.2
        ok = abs(comp - rep) <= tol
        bad += not ok
        out.append(f"| {p} | {col} | {rep:.1f} | {comp:.1f} | {tol:.1f} | {'yes' if ok else '**NO**'} |")
out += ["", f"Failures: {bad}", ""]

# 2. restatements of segment adjusted EBITDA
out += ["## 2. Adjusted EBITDA: prior-year figure in later release vs first reported", "",
        "| period | segment | first reported (US$ m) | shown a year later | difference |", "|---|---|---|---|---|"]
for p in df.index:
    nxt = f"{int(p[:4]) + 1}{p[4:]}"
    if nxt not in df.index:
        continue
    for seg in ("shopee", "monee"):
        a, b = df.at[p, f"{seg}_adj_ebitda_usd_m"], df.at[nxt, f"{seg}_adj_ebitda_prior_usd_m"]
        if pd.notna(a) and pd.notna(b) and abs(a - b) > 0.05:
            out.append(f"| {p} | {seg} | {a:,.1f} | {b:,.1f} | {b - a:+,.1f} |")
out += ["", "Rows above are restatements by Sea (e.g. segment re-allocations). The model uses first-reported values.", ""]

# 3. sum of quarters vs full-year figures in Q4 releases
out += ["## 3. Sum of quarters vs full-year figure", "", "| year | metric | full year | sum of quarters | gap % |", "|---|---|---|---|---|"]
for date, title, url, fn in json.loads((HERE / "releases.json").read_text()):
    if not title.startswith("Fourth"):
        continue
    y = int(re.search(r"(\d{4})", title).group(1))
    if y < 2019:
        continue
    t = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", (HERE / "raw" / fn).read_text(encoding="utf-8"))))
    h = re.search(rf"Full Year {y} (?:Business )?Highlights", t)
    fy = t[h.start():] if h else ""
    fy = fy[re.search(r"(?:E-commerce|Shopee) ", fy).start():][:1500] if re.search(r"(?:E-commerce|Shopee) ", fy) else ""
    vals = {"gmv_usd_bn": re.search(r"GMV\W{0,3} (?:was|for the full year (?:of \d{4} )?was|reached) US\$\s?([\d.]+) billion", fy),
            "gross_orders_bn": re.search(r"[Gg]ross orders (?:for the full year (?:of \d{4} )?)?totaled ([\d.]+) (billion|million)", fy)}
    for col, m in vals.items():
        if not m:
            out.append(f"| {y} | {col} | not printed | | |")
            continue
        full = float(m.group(1)) / (1000 if col == "gross_orders_bn" and m.group(2) == "million" else 1)
        s = df.loc[[f"{y}Q{q}" for q in range(1, 5)], col].sum()
        note = " (includes derived 2023Q1-Q2)" if y == 2023 else ""
        out.append(f"| {y} | {col} | {full:.1f} | {s:.2f}{note} | {(s / full - 1) * 100:+.1f} |")
out += ["", "Gaps within about 3% come from Sea printing quarters rounded to 0.1 bn.", ""]

# missing values that remain
miss = df[["gmv_usd_bn", "gross_orders_bn", "shopee_revenue_usd_m", "marketplace_usd_m", "shopee_adj_ebitda_usd_m"]].isna()
out += ["## 4. Remaining gaps", ""] + [f"- {p}: {', '.join(c for c in miss.columns if miss.at[p, c])}" for p in miss.index if miss.loc[p].any()] + [""]

(D / "checks.md").write_text("\n".join(out), encoding="utf-8")
df.reset_index().to_csv(D / "sea_quarterly_clean.csv", index=False)
print("\n".join(out))
