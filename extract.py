"""Turn Sea's quarterly earnings releases into one tidy table (Q1 2019 - latest).

Sources per number:
- Highlights bullets (rounded, as Sea prints them): gross orders, GMV, Shopee GAAP revenue,
  core marketplace / value-added services revenue, Monee revenue, loan book, NPL ratio.
- Segment tables (US$ thousands, exact): adjusted EBITDA for Shopee and Monee.
Nothing is guessed: a value Sea did not print stays empty, and check.py flags it.
"""
import csv
import html
import json
import re
from pathlib import Path

HERE = Path(__file__).parent
QN = {"First": 1, "Second": 2, "Third": 3, "Fourth": 4}
MONEY = r"US\$\s?(?P<neg>\()?(?P<v>[\d,.]+)\)?\s?(?P<u>billion|million)"


def usd_m(m):
    """'US$(742.8) million' -> -742.8 ; 'US$1.3 billion' -> 1300.0 (US$ millions)."""
    v = float(m.group("v").replace(",", "")) * (1000 if m.group("u") == "billion" else 1)
    return -v if m.group("neg") else v


def section(t, start_pat, end_pat):
    s = re.search(start_pat, t)
    if not s:
        return ""
    e = re.search(end_pat, t[s.end():])
    return t[s.end(): s.end() + (e.start() if e else 4000)]


def first(pat, text, conv=float):
    m = re.search(pat, text)
    return conv(m) if m else None


def table_ebitda(t, names):
    """Current-quarter value from 'Adjusted EBITDA for <segment> (1) prior current yoy%' (US$ thousands)."""
    m = re.search(rf"Adjusted EBITDA for (?:{names}) (?:\(\d\) )?(\(?[\d,]+ ?\)?) (\(?[\d,]+ ?\)?) ", t)
    if not m:
        return None, None
    def num(s):
        v = float(s.strip("() ").replace(",", "")) / 1000
        return -v if "(" in s else v
    return num(m.group(1)), num(m.group(2))  # prior-year quarter, current quarter (US$ millions)


def main():
    rows = []
    for date, title, url, fn in json.loads((HERE / "releases.json").read_text()):
        y = int(re.search(r"(\d{4})", title).group(1))
        q = QN[title.split()[0]]
        if y < 2019:
            continue
        raw = (HERE / "raw" / fn).read_text(encoding="utf-8")
        t = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", raw)))
        hl = t[t.find("Highlights"):]
        shp = section(hl, r"[§◾] (?:E-commerce|Shopee) ", r"[§◾] (?:Digital Financial Services|SeaMoney|Monee|Garena|Digital Entertainment|Full Year)")
        mon = section(hl, r"[§◾] (?:Digital Financial Services|SeaMoney|Monee) ", r"[§◾] (?:Garena|Digital Entertainment|E-commerce|Shopee|Full Year)|Full Year \d{4}")
        r = {"year": y, "quarter": q, "period": f"{y}Q{q}", "release_date": date, "source": url}
        r["gross_orders_bn"] = first(r"[Gg]ross orders (?:for the quarter )?(?:totaled|was|were|reached) ([\d.]+) (billion|million)", shp,
                                     lambda m: float(m.group(1)) / (1000 if m.group(2) == "million" else 1))
        r["orders_yoy_pct"] = first(r"[Gg]ross orders[^%]{0,90}?(?:increase of|increasing by|up|growth of) ([\d.]+)% year-on-year", shp, lambda m: float(m.group(1)))
        gmv = r"GMV\W{0,3} (?:(?:was|for the quarter was) |growth (?:further )?accelerated to ([\d.]+)% year-on-year to reach )"
        r["gmv_usd_bn"] = first(gmv + MONEY, shp, lambda m: usd_m(re.search(MONEY, m.group(0))) / 1000)
        r["gmv_yoy_pct"] = first(gmv + r"(?:US\$[^%]{0,60}?(?:increase of|increasing by|up) ([\d.]+)%)?", shp,
                                 lambda m: float(m.group(1) or m.group(2)) if (m.group(1) or m.group(2)) else None)
        r["shopee_revenue_usd_m"] = first(r"(?:GAAP|[Aa]djusted) [Rr]evenue (?:was|of) " + MONEY, shp, usd_m)
        # marketplace = transaction fees + ads + value-added services (logistics); excludes Shopee's own product sales
        r["marketplace_usd_m"] = first(r"included " + MONEY + r" of (?:GAAP |[Aa]djusted )?marketplace revenue", shp, usd_m)
        r["core_marketplace_usd_m"] = first(r"Core marketplace revenue[^$]{0,200}? to " + MONEY, shp, usd_m)
        r["vas_usd_m"] = first(r"Value-added services revenue[^$]{0,200}? to " + MONEY, shp, usd_m)
        r["shopee_adj_ebitda_prior_usd_m"], r["shopee_adj_ebitda_usd_m"] = table_ebitda(t, "E-commerce|Shopee")
        r["monee_revenue_usd_m"] = first(r"(?:GAAP|[Aa]djusted) revenue (?:was|of) " + MONEY, mon, usd_m)
        r["monee_adj_ebitda_prior_usd_m"], r["monee_adj_ebitda_usd_m"] = table_ebitda(t, "Digital Financial Services|SeaMoney|Monee")
        # Sea changed the loan-book measure twice; keep the basis so series are never mixed silently
        for basis, pat in (("principal outstanding, on- and off-book", r"loans principal outstanding was " + MONEY),
                           ("gross loans receivable, on-book", r"gross loans receivable[^$]{0,60}? to " + MONEY),
                           ("net loans receivable, on-book", r"total loans receivable (?:was|remained stable quarter-on-quarter at) " + MONEY)):
            r["loans_usd_bn"] = first(pat, mon, lambda m: usd_m(m) / 1000)
            r["loans_basis"] = basis if r["loans_usd_bn"] is not None else ""
            if r["loans_basis"]:
                break
        npl = re.search(r"Non-performing loans past due by more than 90 days.*?%[^.%]*?(?:\.\s|$)", mon)
        npl = npl.group(0) if npl else ""
        r["npl_90d_pct"] = first(r"was ([\d.]+)%", npl, lambda m: float(m.group(1)))
        # before 2023Q3 Sea gave only bounds ("less than 4%", "around 2%"); keep them as text, not as exact numbers
        r["npl_note"] = first(r"(?:(?:to |represented )less than|at around) ([\d.]+)%", npl,
                              lambda m: ("~" if "around" in m.group(0) else "<") + m.group(1) + "%") or ""
        rows.append(r)
    out = HERE / "data"
    out.mkdir(exist_ok=True)
    with open(out / "sea_quarterly.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(len(rows), "quarters ->", out / "sea_quarterly.csv")


if __name__ == "__main__":
    main()
