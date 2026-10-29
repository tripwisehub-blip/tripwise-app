"""Daily "hot package holidays" post to the Tripwise Telegram channel from data/hot_offers.json.

Posts once a day after 14 UTC (state in data/channel_tours_last.txt). Needs TG_BOT_TOKEN;
the channel comes from TG_CHANNEL or data/channel.txt. Standard library only.
"""
import datetime
import html
import json
import os
import urllib.request

TOKEN = os.environ.get("TG_BOT_TOKEN", "").strip()
CHANNEL = os.environ.get("TG_CHANNEL", "").strip() or (open("data/channel.txt").read().strip() if os.path.exists("data/channel.txt") else "")
STATE = "data/channel_tours_last.txt"
APP = "https://tripwisehub-blip.github.io/tripwise-app/"
SYM = {"EUR": "€", "PLN": "zł ", "USD": "$", "GBP": "£"}

if not TOKEN or not CHANNEL or not os.path.exists("data/hot_offers.json"):
    print("Nothing to post (token/channel/offers missing)")
    raise SystemExit
today = datetime.date.today()
if os.path.exists(STATE) and open(STATE).read().strip() == today.isoformat():
    print("Already posted today")
    raise SystemExit
if datetime.datetime.now(datetime.timezone.utc).hour < 14:
    print("Too early")
    raise SystemExit

offers = [o for o in json.load(open("data/hot_offers.json")) if not o.get("date") or o["date"] >= today.isoformat()]
if not offers:
    print("No offers")
    raise SystemExit
# Rotate through the cheapest offers so posts differ day to day; one offer per country/place
start = (today.toordinal() * 3) % max(1, min(len(offers), 30))
seen, picks = set(), []
for o in offers[start:] + offers[:start]:
    key = (o.get("country") or o.get("place") or o["name"]).lower()
    if key in seen:
        continue
    seen.add(key)
    picks.append(o)
    if len(picks) == 3:
        break


def money(o):
    s = SYM.get(o.get("currency", "EUR"), o.get("currency", "") + " ")
    return ("%s%d" % (s, o["price"])) if s in ("€", "$", "£") else ("%d %s" % (o["price"], o.get("currency", "")))


lines = ["🌴 <b>Hot package holidays</b> — flight + hotel", ""]
for o in picks:
    where = ", ".join(x for x in [o.get("place"), o.get("country")] if x) or o["name"]
    extra = " · ".join(x for x in [
        datetime.date.fromisoformat(o["date"]).strftime("%d %b") if o.get("date") else "",
        (o["days"] + " days") if o.get("days") and o["days"].isdigit() else o.get("days", ""),
        o.get("board", ""), ("★" * int(o["stars"][0])) if o.get("stars", "")[:1].isdigit() else ""] if x)
    lines.append("🏝 <b>%s</b> — from <b>%s</b>\n%s%s\n<a href=\"%s\">See the offer (%s, departures from %s)</a>" % (
        html.escape(where), money(o), html.escape(o["name"][:80]), ("\n" + html.escape(extra)) if extra else "",
        html.escape(o["url"], quote=True), html.escape(o["partner"]), html.escape(o.get("market", ""))))
    lines.append("")
lines.append("Prices per person from the tour operator; availability changes quickly.")
lines.append("🎡 <a href=\"%s\">More deals in the Tripwise app</a>" % APP)
text = "\n".join(lines)

photo = next((o["photo"] for o in picks if o.get("photo")), "")
method, body = ("sendPhoto", {"chat_id": CHANNEL, "photo": photo, "caption": text, "parse_mode": "HTML"}) if photo and len(text) <= 1024 \
    else ("sendMessage", {"chat_id": CHANNEL, "text": text, "parse_mode": "HTML", "disable_web_page_preview": True})
req = urllib.request.Request("https://api.telegram.org/bot%s/%s" % (TOKEN, method), data=json.dumps(body).encode(),
                             headers={"Content-Type": "application/json"}, method="POST")
with urllib.request.urlopen(req, timeout=30) as r:
    print("Posted:", json.load(r).get("ok"))
open(STATE, "w").write(today.isoformat())
