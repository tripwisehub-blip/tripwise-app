"""Price-drop alerts for Tripwise.

People subscribe in the Mini App (bell button). The app opens the bot with
/start a_<ORIG>_<DEST>_<YYMMDD>_<YYMMDD>_<PAX>, and the Make scenario saves a record
"a<chat>_<route>" in the Make data store (field "session" = last price in EUR, "0" = new).
/stopalerts saves "x<chat>" - all alerts of that chat are removed here.

This script (GitHub Actions, every 6 hours) checks current prices on Aviasales via the
Travelpayouts API and messages people through the bot when a trip gets cheaper.

Secrets: TP_TOKEN (Travelpayouts), MAKE_TOKEN (Make API, data stores read/write),
TG_BOT_TOKEN (the bot token from @BotFather). Standard library only.
"""
import datetime as dt
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

MAKE_API = "https://eu1.make.com/api/v2"
STORE_ID = 227292
MARKER = "793212"
DROP_MIN = 0.02  # notify only when the price drops by at least 2 %

TP = os.environ.get("TP_TOKEN", "").strip()
MAKE = os.environ.get("MAKE_TOKEN", "").strip()
BOT = os.environ.get("TG_BOT_TOKEN", "").strip()
if not (TP and MAKE and BOT):
    print("Alerts are off: set the TP_TOKEN, MAKE_TOKEN and TG_BOT_TOKEN secrets.")
    sys.exit(0)


def call(method, url, body=None, headers=None):
    data = json.dumps(body).encode() if body is not None else None
    h = {"User-Agent": "tripwise-alerts/1.0", **(headers or {})}
    if data is not None:
        h["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=h, method=method)
    with urllib.request.urlopen(req, timeout=40) as resp:
        raw = resp.read()
        return json.loads(raw) if raw else {}


def make(method, path, body=None):
    return call(method, MAKE_API + path, body, {"Authorization": "Token " + MAKE})


def records():
    out, offset = [], 0
    while True:
        page = make("GET", "/data-stores/%d/data?pg%%5Blimit%%5D=100&pg%%5Boffset%%5D=%d" % (STORE_ID, offset))
        rows = page.get("records") or []
        out.extend(rows)
        if len(rows) < 100:
            return out
        offset += 100


def delete(keys):
    if keys:
        make("DELETE", "/data-stores/%d/data" % STORE_ID, {"keys": list(keys)})
        print("deleted", len(keys))


def send(chat, text, url, button):
    body = {"chat_id": chat, "text": text, "disable_web_page_preview": True,
            "reply_markup": {"inline_keyboard": [[{"text": button, "url": url}]]}}
    try:
        call("POST", "https://api.telegram.org/bot%s/sendMessage" % BOT, body)
        return True
    except urllib.error.HTTPError as e:
        print("telegram", chat, e.code)
        return e.code not in (400, 403)  # chat gone or bot blocked -> drop the alert


def cheapest(orig, dest, dep, ret):
    q = urllib.parse.urlencode({"origin": orig, "destination": dest, "departure_at": dep.isoformat(),
                                "return_at": ret.isoformat(), "one_way": "false", "sorting": "price",
                                "limit": 10, "currency": "eur"})
    rows = call("GET", "https://api.travelpayouts.com/aviasales/v3/prices_for_dates?" + q,
                headers={"X-Access-Token": TP}).get("data") or []
    prices = [r["price"] for r in rows if r.get("price")]
    return min(prices) if prices else None


names = {}
try:
    for c in call("GET", "https://api.travelpayouts.com/data/en/cities.json"):
        names[c["code"]] = (c.get("name_translations") or {}).get("en") or c.get("name")
except Exception as e:
    print("cities failed:", e)

today = dt.date.today()
recs = records()
stops = {r["key"][1:] for r in recs if r["key"].startswith("x")}
alerts = [r for r in recs if r["key"].startswith("a")]
remove = {"x" + c for c in stops}
sent = 0

for r in alerts:
    key = r["key"]
    chat, _, route = key[1:].partition("_")
    if chat in stops:
        remove.add(key)
        continue
    try:
        orig, dest, d1, d2, pax = (route.split("_") + ["1"])[:5]
        dep = dt.datetime.strptime(d1, "%y%m%d").date()
        ret = dt.datetime.strptime(d2, "%y%m%d").date()
    except ValueError:
        remove.add(key)
        continue
    if dep <= today:
        remove.add(key)
        continue
    try:
        price = cheapest(orig, dest, dep, ret)
    except Exception as e:
        print(key, "price failed:", e)
        continue
    if price is None:
        continue
    last = float((r.get("data") or {}).get("session") or 0)
    trip = "%s → %s, %s – %s" % (names.get(orig, orig), names.get(dest, dest),
                                 dep.strftime("%d %b"), ret.strftime("%d %b %Y"))
    url = "https://www.aviasales.com/search/%s%s%s%s%s?marker=%s.alert&currency=eur" % (
        orig, dep.strftime("%d%m"), dest, ret.strftime("%d%m"), pax, MARKER)
    if last <= 0:
        text = "📊 Now tracking %s.\nCurrent price: from €%d round trip per person.\nI'll message you when it gets cheaper. Stop alerts: /stopalerts" % (trip, price)
    elif price <= last * (1 - DROP_MIN):
        text = "📉 Price drop! %s\nNow from €%d (was €%d) round trip per person.\nPrices change fast — check it now. Stop alerts: /stopalerts" % (trip, price, last)
    else:
        if price > last:  # remember the new level so the next drop is measured from it
            make("PUT", "/data-stores/%d/data/%s" % (STORE_ID, urllib.parse.quote(key)), {"session": str(price)})
        continue
    if send(chat, text, url, "Show flights"):
        make("PUT", "/data-stores/%d/data/%s" % (STORE_ID, urllib.parse.quote(key)), {"session": str(price)})
        sent += 1
    else:
        remove.add(key)

delete(remove)
print("alerts:", len(alerts), "messages sent:", sent)
