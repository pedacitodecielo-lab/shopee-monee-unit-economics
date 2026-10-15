"""Download Sea Ltd quarterly earnings releases (6-K, exhibit 99.1) from SEC EDGAR.

SEC requires a User-Agent with a real contact and at most 10 requests/second.
Set it before running:  set SEC_USER_AGENT=Your Name you@example.com
Everything is cached in ./raw, so re-runs only fetch new filings.
"""
import json
import os
import re
import sys
import time
from pathlib import Path

import requests

HERE = Path(__file__).parent
RAW = HERE / "raw"
RAW.mkdir(exist_ok=True)
CIK = 1703399  # Sea Ltd

UA = os.environ.get("SEC_USER_AGENT")
if not UA or "@" not in UA:
    sys.exit("Set SEC_USER_AGENT to 'Name email@domain' (SEC requirement).")
S = requests.Session()
S.headers["User-Agent"] = UA


def get(url, path=None):
    if path and path.exists():
        return path.read_text(encoding="utf-8")
    time.sleep(0.15)
    r = S.get(url, timeout=60)
    r.raise_for_status()
    if path:
        path.write_text(r.text, encoding="utf-8")
    return r.text


def main():
    subs = json.loads(get(f"https://data.sec.gov/submissions/CIK{CIK:010d}.json"))
    r = subs["filings"]["recent"]
    assert not subs["filings"].get("files"), "older filings are paged; extend the loop"
    found = []
    for form, date, acc in zip(r["form"], r["filingDate"], r["accessionNumber"]):
        if form != "6-K":
            continue
        folder = f"https://www.sec.gov/Archives/edgar/data/{CIK}/{acc.replace('-', '')}"
        idx = json.loads(get(f"{folder}/index.json", RAW / f"idx_{acc}.json"))
        ex = [i["name"] for i in idx["directory"]["item"] if re.search(r"ex-?99[-_.]?1\.htm", i["name"], re.I)]
        if not ex:
            continue
        path = RAW / f"ex991_{date}_{acc}.htm"
        html = get(f"{folder}/{ex[0]}", path)
        text = re.sub(r"&#160;|&nbsp;", " ", re.sub(r"<[^>]+>", " ", html[:30000]))
        title = re.search(r"Sea Limited Reports ((?:First|Second|Third|Fourth)[A-Za-z0-9 ]*?Results)", re.sub(r"\s+", " ", text))
        if title:  # other 6-Ks (offerings, AGM notices) stay cached but are skipped
            found.append((date, title.group(1), f"{folder}/{ex[0]}", path.name))
    found.sort()
    (HERE / "releases.json").write_text(json.dumps(found, indent=1), encoding="utf-8")
    for f in found:
        print(*f)
    print(len(found), "earnings releases")


if __name__ == "__main__":
    main()
