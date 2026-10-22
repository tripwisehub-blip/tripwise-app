"""Refresh data for the Tripwise Mini App.

Writes two files next to index.html:
  data/rates.json  - exchange rates per 1 EUR (always, no key needed)
  data/prices.json - cheapest short round trips (1-4 days, leaving Thu/Fri/Sat)
                     from popular origins, found on Aviasales in recent days.
                     Needs the Travelpayouts API token in the TP_TOKEN secret.

Runs in GitHub Actions (.github/workflows/prices.yml). Standard library only.
"""
import datetime as dt
import json
import os
import sys
import urllib.parse
import urllib.request

ORIGINS = ["TLL", "HEL", "RIX", "VNO", "STO", "OSL", "CPH", "WAW", "BER", "MUC",
           "FRA", "AMS", "LON", "PAR", "VIE", "PRG", "BCN", "MAD", "ROM", "MIL"]
MAX_PER_ORIGIN = 120
TOKEN = os.environ.get("TP_TOKEN", "").strip()
NOW = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()
os.makedirs("data", exist_ok=True)


def get_json(url, headers=None):
    req = urllib.request.Request(url, headers={"User-Agent": "tripwise-prices/1.0", **(headers or {})})
    with urllib.request.urlopen(req, timeout=40) as resp:
        return json.load(resp)


def save(path, obj):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, separators=(",", ":"))


# 1. Exchange rates (per 1 EUR)
rates = {"EUR": 1.0}
try:
    rates.update(get_json("https://open.er-api.com/v6/latest/EUR").get("rates", {}))
except Exception as e:  # keep going: the app has fallback rates
    print("rates failed:", e)
try:
    c = get_json("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,tether&vs_currencies=eur")
    rates["BTC"] = 1 / c["bitcoin"]["eur"]
    rates["USDT"] = 1 / c["tether"]["eur"]
except Exception as e:
    print("crypto rates failed:", e)
if len(rates) > 5:
    save("data/rates.json", {"updated": NOW, "base": "EUR", "rates": {k: round(v, 8) for k, v in rates.items()}})
    print("rates:", len(rates))

# 2. Flight prices
if not TOKEN:
    print("TP_TOKEN secret is not set - skipping flight prices.")
    sys.exit(0)

auth = {"X-Access-Token": TOKEN}
names = {}
try:
    for c in get_json("https://api.travelpayouts.com/data/en/cities.json"):
        en = (c.get("name_translations") or {}).get("en") or c.get("name")
        names[c["code"]] = [en, (c.get("country_code") or "").lower()]
except Exception as e:
    print("cities failed:", e)

today = dt.date.today()
first_next = (today.replace(day=1) + dt.timedelta(days=32)).replace(day=1)
months = [today.strftime("%Y-%m"), first_next.strftime("%Y-%m")]

origins = {}
errors = 0
for origin in ORIGINS:
    best = {}
    for month in months:
        q = urllib.parse.urlencode({
            "origin": origin, "departure_at": month, "return_at": month,
            "one_way": "false", "direct": "false", "sorting": "price",
            "unique": "false", "limit": 1000, "currency": "eur",
        })
        try:
            rows = get_json("https://api.travelpayouts.com/aviasales/v3/prices_for_dates?" + q, auth).get("data") or []
        except Exception as e:
            errors += 1
            print(origin, month, "failed:", e)
            continue
        for r in rows:
            dep, ret = (r.get("departure_at") or "")[:10], (r.get("return_at") or "")[:10]
            if not dep or not ret:
                continue
            d1, d2 = dt.date.fromisoformat(dep), dt.date.fromisoformat(ret)
            if d1 <= today or not 1 <= (d2 - d1).days <= 4 or d1.weekday() not in (3, 4, 5):
                continue
            dest = r.get("destination")
            price = r.get("price")
            if not dest or not price or dest == origin:
                continue
            if dest not in best or price < best[dest]["p"]:
                best[dest] = {"d": dest, "p": price, "dep": dep, "ret": ret,
                              "tr": int(r.get("transfers") or 0) + int(r.get("return_transfers") or 0),
                              "link": r.get("link") or ""}
    origins[origin] = sorted(best.values(), key=lambda x: x["p"])[:MAX_PER_ORIGIN]
    print(origin, len(origins[origin]))

if not any(origins.values()):
    print("No prices received (errors: %d) - keeping the previous file." % errors)
    sys.exit(1 if errors else 0)

used = {t["d"] for trips in origins.values() for t in trips}
save("data/prices.json", {"updated": NOW, "currency": "EUR", "origins": origins,
                          "names": {c: names[c] for c in sorted(used) if c in names}})
print("prices saved")
