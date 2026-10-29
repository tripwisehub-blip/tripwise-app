"""Daily post with the 3 cheapest upcoming trips to the Tripwise Telegram channel.

Runs inside the "Update prices" workflow. Needs secrets TG_BOT_TOKEN and TG_CHANNEL (e.g. @tripwise_deals);
the channel can also be written in data/channel.txt; skips quietly when neither is set. Posts at most once a day (state in data/channel_last.txt).
Standard library only.
"""
import datetime
import json
import os
import urllib.parse
import urllib.request

TOKEN = os.environ.get("TG_BOT_TOKEN", "").strip()
CHANNEL = os.environ.get("TG_CHANNEL", "").strip() or (open("data/channel.txt").read().strip() if os.path.exists("data/channel.txt") else "")
MARKER = "793212"
APP = "https://tripwisehub-blip.github.io/tripwise-app/"
BOT = "https://t.me/tripwise_hub_bot"
CARS = "https://naiawork.com/g/wqjhitsyjqb09d80c5375ea594bb46/"  # DiscoverCars via Admitad (channel ad space)
ORIGIN_NAMES = {"TLL": "Tallinn", "HEL": "Helsinki", "RIX": "Riga", "VNO": "Vilnius", "LON": "London", "BER": "Berlin",
                "WAW": "Warsaw", "PAR": "Paris", "AMS": "Amsterdam", "STO": "Stockholm"}
ORIGINS = list(ORIGIN_NAMES)
STATE = "data/channel_last.txt"

if not TOKEN or not CHANNEL:
    print("No TG_BOT_TOKEN/TG_CHANNEL, skipping")
    raise SystemExit
today = datetime.date.today()
if os.path.exists(STATE) and open(STATE).read().strip() == today.isoformat():
    print("Already posted today")
    raise SystemExit
if datetime.datetime.now(datetime.timezone.utc).hour < 7:
    print("Too early")
    raise SystemExit

prices = json.load(open("data/prices.json"))
names = prices.get("names") or {}
origin = ORIGINS[today.toordinal() % len(ORIGINS)]
trips = [t for t in (prices.get("origins") or {}).get(origin, []) if t.get("dep", "") > today.isoformat()]
soon = [t for t in trips if t["dep"] <= (today + datetime.timedelta(days=21)).isoformat()]
if len(soon) >= 3:
    trips = soon
best = {}
for t in trips:
    if t["d"] not in best or t["p"] < best[t["d"]]["p"]:
        best[t["d"]] = t
deals = sorted(best.values(), key=lambda t: t["p"])[:3]
if not deals:
    print("No deals for", origin)
    raise SystemExit


def name(code):
    n = names.get(code)
    return (n[0] if n and n[0] else code)


def link(t):
    path = t.get("link") or "/search/%s%s%s%s%s%s1" % (origin, t["dep"][8:10], t["dep"][5:7], t["d"], t["ret"][8:10], t["ret"][5:7])
    return "https://www.aviasales.com" + path + ("&" if "?" in path else "?") + "marker=" + MARKER + ".channel"


def day(s):
    d = datetime.date.fromisoformat(s)
    return d.strftime("%d %b")


lines = ["🔥 <b>Hot deals from %s</b>" % ORIGIN_NAMES.get(origin, name(origin)), ""]
for t in deals:
    lines.append("✈️ <b>%s</b> — from <b>€%d</b> return\n%s – %s · %s\n<a href=\"%s\">See flights</a>" % (
        name(t["d"]), round(t["p"]), day(t["dep"]), day(t["ret"]), "direct" if not t.get("tr") else "with stops", link(t)))
    lines.append("")
lines.append("Prices found on Aviasales recently and may change.")
lines.append("🎡 <a href=\"%s\">Spin the budget wheel</a> · 🤖 <a href=\"%s\">Ask the travel bot</a>" % (APP, BOT))
lines.append('🚗 <a href="%s">Rent a car at your destination</a> (DiscoverCars)' % CARS)
text = "\n".join(lines)

body = {"chat_id": CHANNEL, "text": text, "parse_mode": "HTML", "disable_web_page_preview": True}
req = urllib.request.Request("https://api.telegram.org/bot%s/sendMessage" % TOKEN, data=json.dumps(body).encode(),
                             headers={"Content-Type": "application/json"}, method="POST")
with urllib.request.urlopen(req, timeout=30) as r:
    print("Posted:", json.load(r).get("ok"))
os.makedirs("data", exist_ok=True)
open(STATE, "w").write(today.isoformat())
