"""Hot package holidays from partner product feeds (Admitad YML/XML) -> data/hot_offers.json.

Feed URLs are personal, so they live in GitHub secrets (one per partner), e.g. ADMITAD_FEED_TRAVELKING.
Skips quietly when no secret is set. Standard library only.
"""
import datetime
import json
import os
import re
import urllib.request
import xml.etree.ElementTree as ET

FEEDS = [  # (secret name, partner name, departure market)
    ("ADMITAD_FEED_TRAVELKING", "Travelking", "Poland"),
]
OUT = "data/hot_offers.json"


def text(el, tag):
    x = el.find(tag)
    return (x.text or "").strip() if x is not None and x.text else ""


def pick(params, *keys):
    for name, value in params.items():
        n = name.lower()
        if any(k in n for k in keys):
            return value
    return ""


def parse_date(s):
    m = re.search(r"(\d{4})-(\d{2})-(\d{2})", s) or re.search(r"(\d{2})[./](\d{2})[./](\d{4})", s)
    if not m:
        return ""
    g = m.groups()
    return "%s-%s-%s" % ((g[0], g[1], g[2]) if len(g[0]) == 4 else (g[2], g[1], g[0]))


offers = []
today = datetime.date.today().isoformat()
for secret, partner, market in FEEDS:
    url = os.environ.get(secret, "").strip()
    if not url:
        print("No", secret, "- skipping", partner)
        continue
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "tripwise"}), timeout=120) as r:
            root = ET.fromstring(r.read())
    except Exception as e:
        print(partner, "feed failed:", e)
        continue
    n = 0
    for o in root.iter("offer"):
        params = {p.get("name", ""): (p.text or "").strip() for p in o.findall("param")}
        try:
            price = float(text(o, "price") or 0)
        except ValueError:
            continue
        link = text(o, "url")
        if not price or not link:
            continue
        date = parse_date(pick(params, "data", "date", "wyjazd", "departure", "termin") or text(o, "description"))
        if date and date < today:
            continue
        offers.append({
            "partner": partner, "market": market, "name": text(o, "name")[:120], "price": round(price),
            "currency": text(o, "currencyId") or "EUR", "url": link, "photo": text(o, "picture"),
            "country": pick(params, "kraj", "country", "państwo")[:40], "place": pick(params, "miasto", "city", "region", "miejsc")[:40],
            "date": date, "days": pick(params, "dni", "days", "noc", "night", "długość")[:20],
            "board": pick(params, "wyżyw", "board", "meal", "food")[:30], "stars": pick(params, "standard", "star", "gwiazd", "kategor")[:10],
        })
        n += 1
    print(partner, "offers:", n)

if offers:
    offers.sort(key=lambda x: x["price"])
    os.makedirs("data", exist_ok=True)
    json.dump(offers[:60], open(OUT, "w"), ensure_ascii=False, indent=0)
    print("saved", min(60, len(offers)))
