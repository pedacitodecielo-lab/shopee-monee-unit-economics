"""Draw the Power BI page backgrounds (1280x720) and full mockups with the charts drawn in.

backgrounds/page{1,2}.png  -> set as Power BI page background; visuals sit on the white cards
mockups/page{1,2}.png      -> same pages with the charts drawn by matplotlib, for design review
Card positions are in CARDS so the Power BI visuals can be placed on the same pixel boxes.
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import FancyBboxPatch
from PIL import Image

HERE = Path(__file__).parent
ROOT = HERE.parent
W, H = 1280, 720
OR, OR_D, OR_L, INK, MUTED, BG = "#EE4D2D", "#C93A1E", "#FFE9E3", "#222222", "#6B6B6B", "#FFF7F4"
BLUE = "#1652F0"
plt.rcParams["font.family"] = "Segoe UI"
plt.rcParams["text.parse_math"] = False  # "US$" pairs must not turn into math text

d = pd.read_csv(ROOT / "data" / "sea_quarterly_clean.csv")
d["aov"] = d.gmv_usd_bn / d.gross_orders_bn
d["core_take"] = d.core_marketplace_usd_m / (d.gmv_usd_bn * 1000) * 100
d["vas_take"] = d.vas_usd_m / (d.gmv_usd_bn * 1000) * 100
d["mkt_take"] = d.marketplace_usd_m / (d.gmv_usd_bn * 1000) * 100
d["ebitda_gmv"] = d.shopee_adj_ebitda_usd_m / (d.gmv_usd_bn * 1000) * 100
d["label"] = d.period.str[2:4] + "Q" + d.period.str[-1]

# pixel boxes (x, y, w, h) shared with the Power BI build
CARDS = {
    1: {"side": (16, 92, 284, 612), "k1": (316, 92, 181, 92), "k2": (507, 92, 181, 92), "k3": (698, 92, 181, 92),
        "k4": (889, 92, 181, 92), "k5": (1080, 92, 184, 92),
        "c1": (316, 196, 468, 250), "c2": (796, 196, 468, 250), "c3": (316, 458, 468, 246), "c4": (796, 458, 468, 246)},
}
CARDS[2] = CARDS[1]
TITLES = {
    1: {"k1": "GMV, last 4 quarters", "k2": "Gross orders, last 4 quarters", "k3": "Core take rate (fees + ads)",
        "k4": "Adj. EBITDA % of GMV", "k5": "Adj. EBITDA per order",
        "c1": "GMV and orders keep compounding", "c2": "Shopee takes more in fees and ads, less from logistics",
        "c3": "...but profit per dollar sold stays thin", "c4": "Where marketplace revenue growth comes from (YoY)"},
    2: {"k1": "Monee loans outstanding", "k2": "Loan growth, YoY", "k3": "NPL 90+ days, reported",
        "k4": "NPL vs book a year earlier", "k5": "Monee adj. EBITDA margin",
        "c1": "Monee's loan book has more than tripled", "c2": "Reported NPL falls; the seasoned ratio does not",
        "c3": "FY2026 Shopee adj. EBITDA vs the US$1 bn goal", "c4": "Shopee adj. EBITDA by quarter: the H2 dip"},
}
HEAD = {1: ("Shopee Unit Economics", "Is Shopee's growth becoming more profitable?  |  Sea Ltd 6-K filings, Q1 2019 - Q2 2026, US$"),
        2: ("Monee Credit & the FY2026 Target", "Is fast loan growth healthy, and can Shopee reach US$1 bn adj. EBITDA in 2026?  |  US$")}
SIDE = {
    1: ("Key findings", [
        ("Take rate doubled", "Fees + ads rose from 5.2% of GMV (Q3 22) to 11.2% (Q2 26). Logistics fell to 1.8%."),
        ("Growth mix is shifting", "37% of Q2 26 marketplace revenue growth came from a higher take rate, up from 11% a year earlier."),
        ("Profit stays thin", "Adj. EBITDA is 0.67% of GMV, about US$0.06 an order, below Q1 23's 1.2%. Sales & marketing grew 57% YoY."),
        ("Profit can be switched off", "Shopee went back to losses in Q3 23 - Q2 24 when Sea chose to reinvest."),
    ]),
    2: ("Key findings", [
        ("Loan book x3.6", "US$3.1 bn (Q4 23) to US$11.1 bn (Q2 26), incl. off-book loans."),
        ("Margin traded for growth", "Monee adj. EBITDA margin fell from 31% to 21% over the same period."),
        ("Seasoning check", "Reported NPL 1.0%. Divided by the book a year earlier it is about 1.6-2.0%, flat, not improving."),
        ("US$1 bn is tight", "H1 26 gave US$479 m. Base case US$1,043 m; bear US$962 m; if H2 repeats 2025's dip, US$856 m."),
    ]),
}
FOOT = "Source: Sea Limited earnings releases (SEC Form 6-K, ex. 99.1). Q1-Q2 2023 GMV/orders derived from YoY growth Sea reported a year later. Independent analysis, not affiliated with Sea Ltd."


def card(ax, box, fill="white"):
    x, y, w, h = box
    ax.add_patch(FancyBboxPatch((x + 2, y + 3), w, h, boxstyle="round,pad=0,rounding_size=12", fc="#00000012", ec="none"))
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=12", fc=fill, ec="#F1D5CC", lw=0.8))


def logo(fig, path, cx, cy, height, pill_w):
    ax = fig.add_axes([0, 0, 1, 1], zorder=5)
    ax.set_xlim(0, W); ax.set_ylim(H, 0); ax.axis("off")
    ax.add_patch(FancyBboxPatch((cx - pill_w / 2, cy - 22), pill_w, 44, boxstyle="round,pad=0,rounding_size=22", fc="white", ec="none"))
    im = Image.open(path).convert("RGBA")
    r = height / im.height
    w = im.width * r
    ax.imshow(im, extent=(cx - w / 2, cx + w / 2, cy + height / 2, cy - height / 2), zorder=6)


def background(page):
    fig = plt.figure(figsize=(W / 100, H / 100), dpi=100)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, W); ax.set_ylim(H, 0); ax.axis("off")
    ax.add_patch(plt.Rectangle((0, 0), W, H, fc=BG))
    grad = np.linspace(0, 1, 256).reshape(1, -1)
    ax.imshow(grad, extent=(0, W, 78, 0), cmap=matplotlib.colors.LinearSegmentedColormap.from_list("g", [OR, "#F7663F"]), aspect="auto", zorder=1)
    t, s = HEAD[page]
    ax.text(24, 34, t, color="white", fontsize=22, fontweight="bold", va="center")
    ax.text(24, 60, s, color="#FFE3DA", fontsize=10.5, va="center")
    cards = CARDS[page]
    for k, box in cards.items():
        card(ax, box)
    # sidebar
    x, y, w, h = cards["side"]
    title, items = SIDE[page]
    ax.text(x + 18, y + 30, title, color=OR, fontsize=15, fontweight="bold", va="center")
    yy = y + 70
    for i, (head, body) in enumerate(items, 1):
        ax.add_patch(plt.Circle((x + 30, yy), 13, fc=OR, ec="none"))
        ax.text(x + 30, yy, str(i), color="white", fontsize=11, fontweight="bold", ha="center", va="center")
        ax.text(x + 52, yy, head, color=INK, fontsize=11.5, fontweight="bold", va="center")
        import textwrap
        for j, line in enumerate(textwrap.wrap(body, 34)):
            ax.text(x + 52, yy + 22 + j * 17, line, color=MUTED, fontsize=9.5, va="center")
        yy += 40 + 17 * len(textwrap.wrap(body, 34)) + 18
    # card titles
    for k, title in TITLES[page].items():
        bx, by, bw, bh = cards[k]
        if k.startswith("k"):
            ax.text(bx + bw / 2, by + 18, title, color=MUTED, fontsize=9, va="center", ha="center")  # Power BI cards centre their value
        else:
            ax.add_patch(FancyBboxPatch((bx + 14, by + 14), 6, 18, boxstyle="round,pad=0,rounding_size=3", fc=OR, ec="none"))
            ax.text(bx + 28, by + 23, title, color=INK, fontsize=11.5, fontweight="bold", va="center")
    ax.text(W / 2, 714, FOOT, color="#9A9A9A", fontsize=7, ha="center", va="center")
    logo(fig, HERE / "assets" / "shopee_mark.png", 1072, 39, 28, 150)
    logo(fig, HERE / "assets" / "monee_logo.png", 1196, 39, 22, 128)
    return fig


def place(fig, box, pad=(14, 38, 12, 10)):
    x, y, w, h = box
    l, t, r, b = pad
    return fig.add_axes([(x + l) / W, 1 - (y + h - b) / H, (w - l - r) / W, (h - t - b) / H], zorder=3)


def style(ax):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color("#DDDDDD")
    ax.tick_params(colors=MUTED, labelsize=7.5, length=0)
    ax.grid(axis="y", color="#EEEEEE", lw=0.8)
    ax.set_axisbelow(True)


def kpi(fig, box, value, sub, color=INK):
    x, y, w, h = box
    ax = fig.add_axes([0, 0, 1, 1], zorder=4)
    ax.set_xlim(0, W); ax.set_ylim(H, 0); ax.axis("off")
    ax.text(x + 14, y + 52, value, color=color, fontsize=21, fontweight="bold", va="center")
    ax.text(x + 14, y + 78, sub, color=MUTED, fontsize=8.5, va="center")


def ticks(ax, labels, every=4):
    idx = range(0, len(labels), every)
    ax.set_xticks(list(idx)); ax.set_xticklabels([labels[i] for i in idx])


def mock(page):
    fig = background(page)
    c = CARDS[page]
    last, yr = d.iloc[-1], d.iloc[-5]
    if page == 1:
        ttm = d.iloc[-4:]
        kpi(fig, c["k1"], f"US${ttm.gmv_usd_bn.sum():.1f} bn", f"+{(ttm.gmv_usd_bn.sum() / d.iloc[-8:-4].gmv_usd_bn.sum() - 1) * 100:.0f}% vs prior 4Q")
        kpi(fig, c["k2"], f"{ttm.gross_orders_bn.sum():.1f} bn", f"AOV US${last.aov:.2f}")
        kpi(fig, c["k3"], f"{last.core_take:.1f}%", f"Q2 26, was {d.loc[d.period == '2022Q3', 'core_take'].item():.1f}% in Q3 22", OR)
        kpi(fig, c["k4"], f"{last.ebitda_gmv:.2f}%", "Q2 26, peak 1.20% in Q1 23")
        kpi(fig, c["k5"], f"US${last.shopee_adj_ebitda_usd_m / (last.gross_orders_bn * 1000):.3f}", "Q2 26 adjusted EBITDA / orders")
        a = place(fig, c["c1"]); style(a)
        a.bar(range(len(d)), d.gmv_usd_bn, color=OR, width=0.7)
        a.set_ylabel("GMV, US$ bn", color=MUTED, fontsize=7.5)
        b = a.twinx(); b.plot(range(len(d)), d.gross_orders_bn, color=INK, lw=1.6); b.tick_params(colors=MUTED, labelsize=7.5, length=0)
        for s in b.spines.values(): s.set_visible(False)
        b.set_ylabel("Orders, bn", color=MUTED, fontsize=7.5); ticks(a, list(d.label))
        a = place(fig, c["c2"]); style(a)
        s = d[d.core_take.notna()]
        a.plot(s.label, s.core_take, color=OR, lw=2.2, marker="o", ms=3, label="Fees + ads")
        a.plot(s.label, s.vas_take, color="#999999", lw=2, marker="o", ms=3, label="Logistics (VAS)")
        a.legend(frameon=False, fontsize=7.5, loc="upper left"); ticks(a, list(s.label), 3); a.yaxis.set_major_formatter(lambda v, _: f"{v:.0f}%")
        a = place(fig, c["c3"]); style(a)
        cols = [OR if v >= 0 else "#B9B9B9" for v in d.ebitda_gmv]
        a.bar(range(len(d)), d.ebitda_gmv, color=cols, width=0.7); a.axhline(0, color="#999999", lw=0.8)
        ticks(a, list(d.label)); a.yaxis.set_major_formatter(lambda v, _: f"{v:.0f}%")
        a = place(fig, c["c4"]); style(a)
        rows = d.iloc[-8:].reset_index(drop=True)
        prev = d.iloc[-12:-4].reset_index(drop=True)
        o = np.log(rows.gross_orders_bn / prev.gross_orders_bn); v = np.log(rows.aov / prev.aov); t = np.log(rows.mkt_take / prev.mkt_take)
        tot = np.exp(o + v + t) - 1
        so, sv, st = (o / (o + v + t) * tot * 100, v / (o + v + t) * tot * 100, t / (o + v + t) * tot * 100)
        x = range(len(rows))
        a.bar(x, so, color="#F7A58F", label="More orders", width=0.65)
        a.bar(x, st, bottom=np.where(st >= 0, so.clip(lower=0), 0), color=OR, label="Higher take rate", width=0.65)
        a.bar(x, sv, bottom=np.where(sv < 0, 0, so + st), color="#BBBBBB", label="Order value", width=0.65)
        a.set_xticks(list(x)); a.set_xticklabels(list(rows.label)); a.legend(frameon=False, fontsize=7, ncol=3, loc="upper left")
        a.yaxis.set_major_formatter(lambda v, _: f"{v:.0f}%")
    else:
        m = d[d.loans_usd_bn.notna()]
        kpi(fig, c["k1"], f"US${last.loans_usd_bn:.1f} bn", "Q2 26, incl. off-book")
        kpi(fig, c["k2"], f"+{(last.loans_usd_bn / yr.loans_usd_bn - 1) * 100:.0f}%", "vs Q2 25, same basis")
        kpi(fig, c["k3"], f"{last.npl_90d_pct:.1f}%", "past due 90+ days")
        kpi(fig, c["k4"], f"{last.npl_90d_pct / 100 * last.loans_usd_bn / yr.loans_usd_bn * 100:.1f}%", "seasoning view, Q2 26", OR)
        kpi(fig, c["k5"], f"{last.monee_adj_ebitda_usd_m / last.monee_revenue_usd_m * 100:.1f}%", "Q2 26, was 31.4% in Q4 23")
        a = place(fig, c["c1"]); style(a)
        cols = [BLUE if "principal" in str(b) else "#9DB4F8" for b in m.loans_basis]
        a.bar(m.label, m.loans_usd_bn, color=cols, width=0.65); a.tick_params(axis="x", labelsize=7)
        ticks(a, list(m.label), 3); a.set_ylabel("US$ bn", color=MUTED, fontsize=7.5)
        a.text(0.01, 0.95, "light bars: older on-book measures", transform=a.transAxes, fontsize=7, color=MUTED, va="top")
        a = place(fig, c["c2"]); style(a)
        s = d[d.npl_90d_pct.notna()].copy()
        s["seasoned"] = [r.npl_90d_pct * r.loans_usd_bn / d.loc[i - 4, "loans_usd_bn"] if i - 4 >= 0 and d.loc[i - 4, "loans_basis"] == r.loans_basis else np.nan
                         for i, r in s.iterrows()]
        a.plot(s.label, s.npl_90d_pct, color=BLUE, lw=2.2, marker="o", ms=3, label="Reported NPL 90+")
        a.plot(s.label, s.seasoned, color=OR, lw=2.2, marker="o", ms=3, label="NPL / loans a year earlier")
        a.set_ylim(0, 2.5); a.legend(frameon=False, fontsize=7.5, loc="lower left"); a.yaxis.set_major_formatter(lambda v, _: f"{v:.1f}%")
        ticks(a, list(s.label), 2)
        a = place(fig, c["c3"]); style(a)
        h1 = d.loc[d.period.isin(["2026Q1", "2026Q2"]), "shopee_adj_ebitda_usd_m"].sum()
        sc = {"2025 H2 dip": 856.4, "Bear": 962.1, "Base": 1043.2, "Bull": 1087.2}
        a.barh(list(sc), [h1] * 4, color="#F7A58F", label="H1 2026 actual")
        a.barh(list(sc), [v - h1 for v in sc.values()], left=h1, color=OR, label="H2 2026 scenario")
        a.axvline(1000, color=INK, lw=1.4, ls="--"); a.text(1003, 3.45, "US$1 bn", fontsize=7.5, color=INK)
        for i, v in enumerate(sc.values()):
            a.text(v + 8, i, f"{v:,.0f}", va="center", fontsize=8, color=INK)
        a.set_xlim(0, 1250); a.legend(frameon=True, framealpha=0.9, edgecolor="none", fontsize=7, loc="lower right"); a.grid(axis="x", color="#EEEEEE"); a.grid(axis="y", visible=False)
        a = place(fig, c["c4"]); style(a)
        s = d[d.period >= "2024Q1"]
        cols = [OR if p[-1] in "12" else "#F7A58F" for p in s.period]
        a.bar(s.label, s.shopee_adj_ebitda_usd_m, color=cols, width=0.65); a.axhline(0, color="#999999", lw=0.8)
        a.text(0.01, 0.95, "dark = H1 quarters, light = H2 quarters", transform=a.transAxes, fontsize=7, color=MUTED, va="top")
        a.set_ylabel("US$ m", color=MUTED, fontsize=7.5)
    return fig


if __name__ == "__main__":
    for folder in ("backgrounds", "mockups"):
        (HERE / folder).mkdir(exist_ok=True)
    for p in (1, 2):
        background(p).savefig(HERE / "backgrounds" / f"page{p}.png", dpi=100); plt.close("all")
        mock(p).savefig(HERE / "mockups" / f"page{p}.png", dpi=100); plt.close("all")
    print("ok")
