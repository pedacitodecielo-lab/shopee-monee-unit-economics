"""Write the Power BI report pages and visuals (PBIR format) into shopee_monee_unit_economics.Report.

Visuals sit on the white cards drawn by make_pages.py (same pixel boxes, page = 1280x720).
Close Power BI Desktop before running: it overwrites report files on save.
"""
import hashlib
import json
import shutil
from pathlib import Path

from make_pages import CARDS

HERE = Path(__file__).parent
REP = HERE / "shopee_monee_unit_economics.Report"
DEF = REP / "definition"
SCHEMA = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition"
OR, OR_L, GREY, INK, MUTED, BLUE, BLUE_L = "#EE4D2D", "#F7A58F", "#B9B9B9", "#222222", "#6B6B6B", "#1652F0", "#9DB4F8"


def uid(*parts):
    return hashlib.md5("|".join(parts).encode()).hexdigest()[:20]


def lit(v):
    return {"expr": {"Literal": {"Value": v}}}


def colour(hex_):
    return {"solid": {"color": lit(f"'{hex_}'")}}


def src(entity):
    return {"Expression": {"SourceRef": {"Entity": entity}}}


def column(entity, prop):
    return {"Column": {**src(entity), "Property": prop}}


def measure(entity, prop):
    return {"Measure": {**src(entity), "Property": prop}}


def proj(field, entity, prop, active=False):
    p = {"field": field, "queryRef": f"{entity}.{prop}", "nativeQueryRef": prop}
    if active:
        p["active"] = True
    return p


def off(*names):
    return {n: [{"properties": {"show": lit("false")}}] for n in names}


AXIS = [{"properties": {"showAxisTitle": lit("false"), "labelColor": colour(MUTED), "fontSize": lit("8D"),
                         "preferredCategoryWidth": lit("6D")}}]  # narrow categories so all quarters fit without a scrollbar
VAXIS = [{"properties": {"showAxisTitle": lit("false"), "labelColor": colour(MUTED), "fontSize": lit("8D"),
                         "gridlineColor": colour("#EEEEEE")}}]


def legend(show=True):
    return [{"properties": {"show": lit("true" if show else "false"), "position": lit("'Top'"),
                            "fontSize": lit("8D"), "showTitle": lit("false"), "labelColor": colour(MUTED)}}]


def series_colours(entity, pairs):
    return [{"properties": {"fill": colour(c)}, "selector": {"metadata": f"{entity}.{m}"}} for m, c in pairs]


def container(name, box, visual, z):
    x, y, w, h = box
    return {"$schema": f"{SCHEMA}/visualContainer/2.13.0/schema.json", "name": name,
            "position": {"x": x, "y": y, "z": z, "height": h, "width": w, "tabOrder": z}, "visual": visual}


def chart(vtype, roles, objects, sort_entity="Quarterly", sort_prop="Label"):
    v = {"visualType": vtype, "query": {"queryState": roles,
         "sortDefinition": {"sort": [{"field": column(sort_entity, sort_prop), "direction": "Ascending"}], "isDefaultSort": True}},
         "objects": objects, "drillFilterOtherVisuals": True,
         "visualContainerObjects": {**off("title", "background", "border", "dropShadow"),
                                    "padding": [{"properties": {"top": lit("0D"), "bottom": lit("0D"), "left": lit("4D"), "right": lit("4D")}}]}}
    return v


def inside(box):
    x, y, w, h = box
    return (x + 8, y + 36, w - 16, h - 42)


def kpi(entity, name, accent=False):
    return {"visualType": "card",
            "query": {"queryState": {"Values": {"projections": [proj(measure(entity, name), entity, name)]}}},
            "objects": {"labels": [{"properties": {"color": colour(OR if accent else INK), "fontSize": lit("20D"),
                                                   "fontFamily": lit("'Segoe UI Semibold'")}}],
                        "categoryLabels": [{"properties": {"show": lit("true"), "color": colour(MUTED), "fontSize": lit("8D")}}]},
            "visualContainerObjects": {**off("title", "background", "border", "dropShadow"),
                                       "padding": [{"properties": {k: lit("0D") for k in ("top", "bottom", "left", "right")}}]},
            "drillFilterOtherVisuals": True}


def kbox(box):
    x, y, w, h = box
    return (x + 4, y + 28, w - 8, h - 32)


Q, LBL = "Quarterly", column("Quarterly", "Label")
cat = {"Category": {"projections": [proj(LBL, Q, "Label", active=True)]}}
# 30 quarters do not fit as categories (Power BI adds a scrollbar); a continuous date axis does
datecat = {"Category": {"projections": [proj(column(Q, "QuarterEnd"), Q, "QuarterEnd", active=True)]}}
DATEAXIS = [{"properties": {**AXIS[0]["properties"], "axisType": lit("'Scalar'")}}]


def ys(*names, entity=Q, role="Y"):
    return {role: {"projections": [proj(measure(entity, n), entity, n) for n in names]}}


PAGES = {
    1: ("Shopee", [
        ("k1", kpi(Q, "+29% vs prior 4 quarters")), ("k2", kpi(Q, "AOV US$9.12 per order")),
        ("k3", kpi(Q, "Q2 26, was 5.2% in Q3 22", accent=True)), ("k4", kpi(Q, "Q2 26, peak 1.20% in Q1 23")),
        ("k5", kpi(Q, "Q2 26 adj. EBITDA / gross orders")),
        ("c1", chart("lineClusteredColumnComboChart", {**datecat, **ys("GMV (US$ bn)"), **ys("Gross orders (bn)", role="Y2")},
                     {"categoryAxis": DATEAXIS, "valueAxis": [{"properties": {**VAXIS[0]["properties"], "secShow": lit("true"),
                                                                           "secLabelColor": colour(MUTED), "secFontSize": lit("8D")}}],
                      "legend": legend(),
                      "dataPoint": [{"properties": {"fill": colour(OR)}}] + series_colours(Q, [("GMV (US$ bn)", OR), ("Gross orders (bn)", INK)])},
                     sort_prop="QuarterEnd")),
        ("c2", chart("lineChart", {**cat, **ys("Fees + ads", "Logistics (VAS)")},
                     {"categoryAxis": AXIS, "valueAxis": VAXIS, "legend": legend(),
                      "dataPoint": series_colours(Q, [("Fees + ads", OR), ("Logistics (VAS)", "#999999")]),
                      "lineStyles": [{"properties": {"strokeWidth": lit("3D"), "showMarker": lit("true")}}]})),
        ("c3", chart("columnChart", {**datecat, **ys("Profit quarter", "Loss quarter")},
                     {"categoryAxis": DATEAXIS, "valueAxis": VAXIS, "legend": legend(),
                      "dataPoint": series_colours(Q, [("Profit quarter", OR), ("Loss quarter", GREY)])},
                     sort_prop="QuarterEnd")),
        ("c4", chart("columnChart", {"Category": {"projections": [proj(column("Drivers", "Label"), "Drivers", "Label", active=True)]},
                                     "Series": {"projections": [proj(column("Drivers", "Component"), "Drivers", "Component")]},
                                     **ys("Contribution to YoY growth", entity="Drivers")},
                     {"categoryAxis": AXIS, "valueAxis": VAXIS, "legend": legend(),
                      "dataPoint": [{"properties": {"fill": colour(c)}, "selector": {"data": [{"scopeId": {"Comparison": {
                          "ComparisonKind": 0, "Left": column("Drivers", "Component"), "Right": {"Literal": {"Value": f"'{n}'"}}}}}]}}
                          for n, c in (("More orders", OR_L), ("Higher take rate", OR), ("Order value", GREY))]},
                     sort_entity="Drivers")),
    ]),
    2: ("Monee & FY2026 nowcast", [
        ("k1", kpi(Q, "Q2 26, incl. off-book loans")), ("k2", kpi(Q, "vs Q2 25, same loan measure")),
        ("k3", kpi(Q, "past due 90+ days, Q2 26")), ("k4", kpi(Q, "NPL / loan book a year earlier", accent=True)),
        ("k5", kpi(Q, "Q2 26, was 31.4% in Q4 23")),
        ("c1", chart("columnChart", {**cat, **ys("Loans (current measure)", "Loans (older on-book measures)")},
                     {"categoryAxis": AXIS, "valueAxis": VAXIS, "legend": legend(),
                      "dataPoint": series_colours(Q, [("Loans (current measure)", BLUE), ("Loans (older on-book measures)", BLUE_L)])})),
        ("c2", chart("lineChart", {**cat, **ys("Reported NPL 90+", "NPL / loans a year earlier")},
                     {"categoryAxis": AXIS, "valueAxis": [{"properties": {**VAXIS[0]["properties"], "start": lit("0D")}}],
                      "legend": legend(),
                      "dataPoint": series_colours(Q, [("Reported NPL 90+", BLUE), ("NPL / loans a year earlier", OR)]),
                      "lineStyles": [{"properties": {"strokeWidth": lit("3D"), "showMarker": lit("true")}}]})),
        ("c3", chart("barChart", {"Category": {"projections": [proj(column("Scenarios", "Scenario"), "Scenarios", "Scenario", active=True)]},
                                  **ys("H1 2026 actual", "H2 2026 scenario", entity="Scenarios")},
                     {"categoryAxis": AXIS, "valueAxis": [{"properties": {**VAXIS[0]["properties"], "labelDisplayUnits": lit("1D")}}],
                      "legend": legend(),
                      "dataPoint": series_colours("Scenarios", [("H1 2026 actual", OR_L), ("H2 2026 scenario", OR)]),
                      "totals": [{"properties": {"show": lit("true"), "fontSize": lit("9D"), "labelDisplayUnits": lit("1D")}}],
                      "y1AxisReferenceLine": [{"properties": {"show": lit("true"), "value": lit("1000D"),
                                                              "lineColor": colour(INK), "style": lit("'dashed'"),
                                                              "displayName": lit("'US$1 bn goal'"), "dataLabelShow": lit("false")},
                                               "selector": {"id": "1"}}]},
                     sort_entity="Scenarios", sort_prop="Scenario")),
        ("c4", chart("columnChart", {**cat, **ys("H1 quarter", "H2 quarter")},
                     {"categoryAxis": AXIS, "valueAxis": VAXIS, "legend": legend(),
                      "dataPoint": series_colours(Q, [("H1 quarter", OR), ("H2 quarter", OR_L)])})),
    ]),
}


def main():
    pages_dir = DEF / "pages"
    shutil.rmtree(pages_dir)
    pages_dir.mkdir()
    res = REP / "StaticResources" / "RegisteredResources"
    res.mkdir(parents=True, exist_ok=True)
    order = []
    for p, (title, visuals) in PAGES.items():
        pid = uid("page", str(p))
        order.append(pid)
        img = f"page{p}.png"
        shutil.copy(HERE / "backgrounds" / img, res / img)
        page = {"$schema": f"{SCHEMA}/page/2.1.0/schema.json", "name": pid, "displayName": title,
                "displayOption": "FitToPage", "height": 720, "width": 1280,
                "objects": {"background": [{"properties": {
                    "image": {"image": {"name": lit(f"'{img}'"),
                                        "url": {"expr": {"ResourcePackageItem": {"PackageName": "RegisteredResources", "PackageType": 1, "ItemName": img}}},
                                        "scaling": lit("'Fit'")}},
                    "transparency": lit("0D")}}],
                    "outspace": [{"properties": {"color": colour("#FFF7F4")}}]}}
        vdir = pages_dir / pid / "visuals"
        vdir.mkdir(parents=True)
        (pages_dir / pid / "page.json").write_text(json.dumps(page, indent=2), encoding="utf-8")
        for z, (key, vis) in enumerate(visuals):
            box = CARDS[p][key]
            vid = uid(str(p), key)
            (vdir / vid).mkdir()
            c = container(vid, kbox(box) if key.startswith("k") else inside(box), vis, z * 1000)
            (vdir / vid / "visual.json").write_text(json.dumps(c, indent=2), encoding="utf-8")
    (pages_dir / "pages.json").write_text(json.dumps({"$schema": f"{SCHEMA}/pagesMetadata/1.1.0/schema.json",
                                                       "pageOrder": order, "activePageName": order[0]}, indent=2), encoding="utf-8")
    rj = json.loads((DEF / "report.json").read_text(encoding="utf-8"))
    pk = [r for r in rj["resourcePackages"] if r["name"] != "RegisteredResources"]
    pk.append({"name": "RegisteredResources", "type": "RegisteredResources",
               "items": [{"name": f"page{p}.png", "path": f"page{p}.png", "type": "Image"} for p in PAGES]})
    rj["resourcePackages"] = pk
    (DEF / "report.json").write_text(json.dumps(rj, indent=2), encoding="utf-8")
    print("pages:", order)


if __name__ == "__main__":
    main()
