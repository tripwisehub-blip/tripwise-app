"""Affiliate deep links to tours in each city (Tiqets search page), via the Travelpayouts Links API.

Writes data/tours.json: {"Barcelona": "https://tiqets.tpx.lu/...", ...}. Only cities without a link are
requested, so later runs are cheap. City names come from the app's DATA list and data/prices.json.
Secret: TP_TOKEN. Standard library only.
"""
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request

TOKEN = os.environ.get("TP_TOKEN", "").strip()
MARKER = 793212
TRS = 588570
OUT = "data/tours.json"
if not TOKEN:
    print("No TP_TOKEN, skipping")
    sys.exit(0)

cities = set()
html = open("index.html", encoding="utf-8").read()
for line in re.findall(r'^"([a-z]{2}\|[^"]+)",?$', html, re.M):
    for item in line.split("|")[2].split(","):
        name = item.strip().rsplit(" ", 1)[0]
        if name:
            cities.add(name)
try:
    for n in (json.load(open("data/prices.json")).get("names") or {}).values():
        if n and n[0]:
            cities.add(n[0])
except Exception as e:
    print("prices.json:", e)

try:
    links = json.load(open(OUT))
except Exception:
    links = {}
todo = sorted(c for c in cities if c not in links)[:400]
print("cities:", len(cities), "have:", len(links), "to create:", len(todo))

for i in range(0, len(todo), 10):
    batch = todo[i:i + 10]
    body = {"trs": TRS, "marker": MARKER, "shorten": True,
            "links": [{"url": "https://www.tiqets.com/en/search?q=" + urllib.parse.quote(c), "sub_id": "tours"} for c in batch]}
    req = urllib.request.Request("https://api.travelpayouts.com/links/v1/create", data=json.dumps(body).encode(),
                                 headers={"X-Access-Token": TOKEN, "Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=40) as r:
            res = json.load(r)
    except Exception as e:
        print("request failed:", e)
        break
    for c, l in zip(batch, (res.get("result") or {}).get("links") or []):
        if l.get("code") == "success" and l.get("partner_url"):
            links[c] = l["partner_url"]
        else:
            print("failed:", c, l.get("code"))
    time.sleep(0.8)

os.makedirs("data", exist_ok=True)
json.dump(dict(sorted(links.items())), open(OUT, "w"), ensure_ascii=False, indent=0)
print("saved:", len(links))
