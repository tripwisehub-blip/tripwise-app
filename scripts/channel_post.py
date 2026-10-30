"""Daily post with the 3 cheapest upcoming trips to the Tripwise Telegram channel.

Runs inside the "Update prices" workflow. Needs secrets TG_BOT_TOKEN and TG_CHANNEL (e.g. @tripwise_deals);
the channel can also be written in data/channel.txt; skips quietly when neither is set. Posts at most once a day (state in data/channel_last.txt).
The post is a photo of the cheapest destination (from Wikipedia) with a short caption and booking buttons.
Standard library only.
"""
import datetime
import json
import os
import urllib.parse
import urllib.request

NL = chr(10)
TOKEN = os.environ.get("TG_BOT_TOKEN", "").strip()
CHANNEL = os.environ.get("TG_CHANNEL", "").strip() or (open("data/channel.txt").read().strip() if os.path.exists("data/channel.txt") else "")
MARKER = "793212"
APP = "https://tripwisehub-blip.github.io/tripwise-app/"
BOT = "https://t.me/tripwise_hub_bot"
CHAN_LINK = "https://t.me/tripwise_deals"
CARS = "https://naiawork.com/g/wqjhitsyjqb09d80c5375ea594bb46/"  # DiscoverCars via Admitad (channel ad space)
ORIGIN_NAMES = {"TLL": "Tallinn", "HEL": "Helsinki", "RIX": "Riga", "VNO": "Vilnius", "LON": "London", "BER": "Berlin",
                "WAW": "Warsaw", "PAR": "Paris", "AMS": "Amsterdam", "STO": "Stockholm"}
ORIGINS = list(ORIGIN_NAMES)
STATE = "data/channel_last.txt"
MEDALS = ["🥇", "🥈", "🥉"]
HOOKS = ["Fares like these disappear fast ⚡", "Pack a bag, it's cheaper than staying home 🧳", "Weekend plans, sorted 😎",
         "Spontaneous trip? Why not ✨", "Your next story starts here 🌍"]

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


def flag(code):
    n = names.get(code)
    iso = (n[1] if n and len(n) > 1 and n[1] else "").upper()
    return "".join(chr(0x1F1E6 + ord(c) - 65) for c in iso) if len(iso) == 2 and iso.isalpha() else "📍"


def link(t):
    path = t.get("link") or "/search/%s%s%s%s%s%s1" % (origin, t["dep"][8:10], t["dep"][5:7], t["d"], t["ret"][8:10], t["ret"][5:7])
    return "https://www.aviasales.com" + path + ("&" if "?" in path else "?") + "marker=" + MARKER + ".channel"


def span(a, b):
    x, y = datetime.date.fromisoformat(a), datetime.date.fromisoformat(b)
    if x.month == y.month:
        return "%d–%d %s" % (x.day, y.day, y.strftime("%b"))
    return "%d %s – %d %s" % (x.day, x.strftime("%b"), y.day, y.strftime("%b"))


def photo_for(title):
    try:
        url = "https://en.wikipedia.org/api/rest_v1/page/summary/" + urllib.parse.quote(title.replace(" ", "_"))
        req = urllib.request.Request(url, headers={"User-Agent": "TripwiseBot/1.0 (https://t.me/tripwise_deals)"})
        with urllib.request.urlopen(req, timeout=20) as r:
            j = json.load(r)
        src = (j.get("thumbnail") or {}).get("source", "")
        if "px-" in src:
            head, _, tail = src.partition("px-")
            return head[:head.rfind("/") + 1] + "960px-" + tail, src
        return src, src
    except Exception as e:
        print("photo lookup failed:", e)
        return "", ""


city = ORIGIN_NAMES.get(origin, name(origin))
top = deals[0]
lines = ["🔥 <b>Cheap flights from %s</b>" % city, "<i>Return tickets for the next few weeks</i>", ""]
for i, t in enumerate(deals):
    lines.append("%s <b>%s</b> %s — <b>€%d</b>" % (MEDALS[i], name(t["d"]), flag(t["d"]), round(t["p"])))
    lines.append("      🗓 %s · %s" % (span(t["dep"], t["ret"]), "✈️ direct" if not t.get("tr") else "🔁 with stops"))
lines += ["", HOOKS[today.toordinal() % len(HOOKS)], "👇 Tap a destination to see the flights",
          "", "<i>Prices found on Aviasales recently and may change.</i>", "#cheapflights #%s" % city.replace(" ", "")]
caption = NL.join(lines)

buttons = [[{"text": "✈️ %s from €%d" % (name(t["d"]), round(t["p"])), "url": link(t)}] for t in deals]
buttons.append([{"text": "🎡 Budget wheel", "url": APP}, {"text": "🤖 Travel bot", "url": BOT}])
buttons.append([{"text": "🚗 Rent a car", "url": CARS},
                {"text": "📣 Share", "url": "https://t.me/share/url?url=" + urllib.parse.quote(CHAN_LINK) + "&text=" + urllib.parse.quote("Cheap flights every day 👉")}])
markup = {"inline_keyboard": buttons}


def call(method, body):
    req = urllib.request.Request("https://api.telegram.org/bot%s/%s" % (TOKEN, method), data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r).get("ok")


ok = False
for pic in photo_for(name(top["d"])):
    if not pic or ok:
        continue
    try:
        ok = call("sendPhoto", {"chat_id": CHANNEL, "photo": pic, "caption": caption, "parse_mode": "HTML", "reply_markup": markup})
    except Exception as e:
        print("sendPhoto failed:", e)
if not ok:
    ok = call("sendMessage", {"chat_id": CHANNEL, "text": caption, "parse_mode": "HTML", "disable_web_page_preview": True, "reply_markup": markup})
print("Posted:", ok)
os.makedirs("data", exist_ok=True)
open(STATE, "w").write(today.isoformat())
