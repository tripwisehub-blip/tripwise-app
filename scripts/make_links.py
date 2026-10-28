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

# City tours in other languages: data/tours_<lang>.json (the app falls back to English)
for lang in ["de", "es", "fr", "it", "ru", "pl", "ja", "ko", "zh"]:
    path = "data/tours_%s.json" % lang
    try:
        tl = json.load(open(path))
    except Exception:
        tl = {}
    todo_l = sorted(c for c in cities if c not in tl)
    for i in range(0, len(todo_l), 10):
        batch = todo_l[i:i + 10]
        body = {"trs": TRS, "marker": MARKER, "shorten": True,
                "links": [{"url": "https://www.tiqets.com/%s/search?q=%s" % (lang, urllib.parse.quote(c)), "sub_id": "tours_" + lang} for c in batch]}
        req = urllib.request.Request("https://api.travelpayouts.com/links/v1/create", data=json.dumps(body).encode(),
                                     headers={"X-Access-Token": TOKEN, "Content-Type": "application/json"}, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=40) as r:
                res = json.load(r)
        except Exception as e:
            print(lang, "request failed:", e)
            break
        for c, l in zip(batch, (res.get("result") or {}).get("links") or []):
            if l.get("code") == "success" and l.get("partner_url"):
                tl[c] = l["partner_url"]
        time.sleep(0.7)
    json.dump(dict(sorted(tl.items())), open(path, "w"), ensure_ascii=False, indent=0)
    print("tours", lang, len(tl))


# ---------- Partner home pages in the user's language (English when the site has no such language) ----------
LR = {"en": "https://www.localrent.com/en/", "de": "https://localrent.de/", "es": "https://localrent.es/", "fr": "https://localrent.fr/",
      "it": "https://localrent.it/", "pl": "https://localrent.pl/"}
for l in ["fi", "ja", "ko", "ru", "th", "tr", "vi", "zh"]:
    LR[l] = "https://www.localrent.com/%s/" % l
GRC = {"en": "https://getrentacar.com/en-US", "zh": "https://getrentacar.com/zh-CN"}
for l in ["ru", "de", "fr", "es", "it", "pl", "tr", "ar", "th"]:
    GRC[l] = "https://getrentacar.com/" + l
KT = {"en": "https://kiwitaxi.com/en", "uk": "https://kiwitaxi.com/ua"}
for l in ["fr", "de", "es", "pl", "it"]:
    KT[l] = "https://kiwitaxi.com/" + l
TQ = {l: "https://www.tiqets.com/%s/" % l for l in ["en", "de", "es", "fr", "ko", "it", "ja", "pl", "ru", "zh"]}
PAGES = {
    "car": LR, "car2": GRC, "transfer": KT, "tours": TQ,
    "audio": {"en": "https://wegotrip.com/en/"},
    "delay": {"en": "https://www.airhelp.com/en/"},
    "tours3": {"en": "https://www.kkday.com/en-us"},
    "transfer3": {"en": "https://gettransfer.com/en"},
}
OUT2 = "data/links.json"
try:
    plinks = json.load(open(OUT2))
except Exception:
    plinks = {}
need = [(k, l, u) for k, m in PAGES.items() for l, u in m.items() if (plinks.get(k) or {}).get(l) is None]
print("partner pages to create:", len(need))
for i in range(0, len(need), 10):
    batch = need[i:i + 10]
    body = {"trs": TRS, "marker": MARKER, "shorten": True, "links": [{"url": u, "sub_id": k + "_" + l} for k, l, u in batch]}
    req = urllib.request.Request("https://api.travelpayouts.com/links/v1/create", data=json.dumps(body).encode(),
                                 headers={"X-Access-Token": TOKEN, "Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=40) as r:
            res = json.load(r)
    except Exception as e:
        print("request failed:", e)
        break
    for (k, l, u), x in zip(batch, (res.get("result") or {}).get("links") or []):
        if x.get("code") == "success" and x.get("partner_url"):
            plinks.setdefault(k, {})[l] = x["partner_url"]
        else:
            print("failed:", k, l, x.get("code"))
    time.sleep(0.8)
json.dump(plinks, open(OUT2, "w"), ensure_ascii=False, indent=0, sort_keys=True)
print("partner pages saved:", sum(len(v) for v in plinks.values()))
