"""Daily "guide of the day" post to the Tripwise Telegram channel.

Picks one blog guide (rotating, newest first), takes its hero photo from Wikipedia and posts a photo with a short
caption and buttons. Runs in the "Update prices" workflow; posts once a day in the morning run (04-12 UTC).
State in data/channel_guide_last.txt. Needs TG_BOT_TOKEN and TG_CHANNEL. Standard library only.
"""
import datetime
import html
import json
import os
import re
import urllib.parse
import urllib.request

NL = chr(10)
TOKEN = os.environ.get("TG_BOT_TOKEN", "").strip()
CHANNEL = os.environ.get("TG_CHANNEL", "").strip() or (open("data/channel.txt").read().strip() if os.path.exists("data/channel.txt") else "")
STATE = "data/channel_guide_last.txt"
BLOG = "https://tripwisehub-blip.github.io/tripwise-app/blog/"
FLIGHTS = "https://aviasales.tpx.lu/sjlt4H8o"
BOT = "https://t.me/tripwise_hub_bot"
OPENERS = ["📖 <b>Guide of the day</b>", "🧭 <b>Planning a trip?</b>", "🗺 <b>Travel guide</b>", "✨ <b>Trip idea of the day</b>"]

if not TOKEN or not CHANNEL:
    print("No TG_BOT_TOKEN/TG_CHANNEL, skipping")
    raise SystemExit
today = datetime.date.today()
if os.path.exists(STATE) and open(STATE).read().strip() == today.isoformat():
    print("Already posted today")
    raise SystemExit
hour = datetime.datetime.now(datetime.timezone.utc).hour
if not 4 <= hour < 11:
    print("Not the morning run")
    raise SystemExit

guides = json.load(open("scripts/blog_guides.json", encoding="utf-8"))
guides = [g for g in guides if g.get("slug")][::-1]
g = guides[today.toordinal() % len(guides)]
page = "blog/%s.html" % g["slug"]
photo_title = ""
if os.path.exists(page):
    m = re.search('class="hero" data-photo="([^"]+)"', open(page, encoding="utf-8").read())
    photo_title = html.unescape(m.group(1)) if m else ""
heads = [html.unescape(re.sub("<[^>]+>", "", h)).strip() for h in re.findall("<h2>(.*?)</h2>", g["body"])][:4]


def photo_for(title):
    if not title:
        return []
    try:
        url = "https://en.wikipedia.org/api/rest_v1/page/summary/" + urllib.parse.quote(title.replace(" ", "_"))
        req = urllib.request.Request(url, headers={"User-Agent": "TripwiseBot/1.0 (https://t.me/tripwise_deals)"})
        with urllib.request.urlopen(req, timeout=20) as r:
            src = (json.load(r).get("thumbnail") or {}).get("source", "")
        if "px-" in src:
            head, _, tail = src.partition("px-")
            return [head[:head.rfind("/") + 1] + "960px-" + tail, src]
        return [src] if src else []
    except Exception as e:
        print("photo lookup failed:", e)
        return []


url = BLOG + g["slug"] + ".html?utm_source=telegram&utm_medium=channel"
lines = [OPENERS[today.toordinal() % len(OPENERS)] + " · " + html.escape(g["tag"]), "",
         "<b>%s</b>" % html.escape(g["title"]), "", html.escape(g["desc"])]
if heads:
    lines += ["", "Inside:"] + ["▫️ " + html.escape(h) for h in heads]
lines += ["", "👇 Read it in 3 minutes", "#travelguide #" + (re.sub("[^A-Za-z]", "", g["tag"].split("·")[0]) or "travel")]
caption = NL.join(lines)
if len(caption) > 1000:
    caption = NL.join(lines[:5] + lines[-2:])

markup = {"inline_keyboard": [[{"text": "📖 Read the guide", "url": url}],
                              [{"text": "✈️ Find cheap flights", "url": FLIGHTS}, {"text": "🤖 Ask the bot", "url": BOT}],
                              [{"text": "📣 Share", "url": "https://t.me/share/url?url=" + urllib.parse.quote(url)}]]}


def call(method, body):
    req = urllib.request.Request("https://api.telegram.org/bot%s/%s" % (TOKEN, method), data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r).get("ok")


ok = False
for pic in photo_for(photo_title):
    if ok:
        break
    try:
        ok = call("sendPhoto", {"chat_id": CHANNEL, "photo": pic, "caption": caption, "parse_mode": "HTML", "reply_markup": markup})
    except Exception as e:
        print("sendPhoto failed:", e)
if not ok:
    ok = call("sendMessage", {"chat_id": CHANNEL, "text": caption, "parse_mode": "HTML", "reply_markup": markup})
print("Posted guide", g["slug"], ok)
os.makedirs("data", exist_ok=True)
open(STATE, "w").write(today.isoformat())
