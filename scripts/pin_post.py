"""Pinterest drip: send one pin per run (guide pages first, then the cheapest flight routes) to the Make webhook.

The webhook routes payloads with "pin" set to Pinterest only. State in data/pins_done.json. Needs FB_HOOK. Standard library only.
"""
import html
import json
import os
import re
import urllib.parse
import urllib.request

HOOK = os.environ.get("FB_HOOK", "").strip()
BLOG = "https://tripwisehub-blip.github.io/tripwise-app/blog/"
STATE = "data/pins_done.json"
PER_RUN = 1


def photo(title):
    try:
        req = urllib.request.Request("https://en.wikipedia.org/api/rest_v1/page/summary/" + urllib.parse.quote(title.replace(" ", "_")),
                                     headers={"User-Agent": "TripwiseBot/1.0 (https://t.me/tripwise_deals)"})
        with urllib.request.urlopen(req, timeout=20) as r:
            src = (json.load(r).get("thumbnail") or {}).get("source", "")
        if "px-" in src:
            head, _, tail = src.partition("px-")
            return head[:head.rfind("/") + 1] + "1280px-" + tail
        return src
    except Exception as e:
        print("photo failed", title, e)
        return ""


def candidates():
    for g in json.load(open("scripts/blog_guides.json", encoding="utf-8")):
        page = "blog/%s.html" % g["slug"]
        if not os.path.exists(page):
            continue
        m = re.search('class="hero" data-photo="([^"]+)"', open(page, encoding="utf-8").read())
        if m:
            yield ("guide:" + g["slug"], html.unescape(m.group(1)), g["title"], g["desc"], BLOG + g["slug"] + ".html")
    try:
        reg = json.load(open("blog/routes.json", encoding="utf-8"))
        names = json.load(open("data/prices.json", encoding="utf-8")).get("names") or {}
    except Exception:
        return
    for key, r in sorted(reg.items(), key=lambda kv: kv[1].get("low") or 9999):
        o, d = key.split("-")
        on, dn = (names.get(o) or [o])[0], (names.get(d) or [d])[0]
        slug = "flights-" + re.sub("-+", "-", re.sub("[^a-z0-9]", "-", on.lower())).strip("-") + "-to-" + re.sub("-+", "-", re.sub("[^a-z0-9]", "-", dn.lower())).strip("-") + ".html"
        if not os.path.exists("blog/" + slug) or not r.get("low"):
            continue
        yield ("route:" + key, dn, "Cheap flights %s to %s from €%d return" % (on, dn, r["low"]),
               "Return flights from %s to %s from €%d. See the cheapest dates, tips for booking and live prices updated every day." % (on, dn, r["low"]),
               BLOG + slug)


def main():
    if not HOOK:
        print("No FB_HOOK, skipping")
        return
    done = set(json.load(open(STATE))) if os.path.exists(STATE) else set()
    sent = 0
    for key, ptitle, title, desc, link in candidates():
        if key in done:
            continue
        img = photo(ptitle)
        if not img:
            done.add(key)
            continue
        body = {"pin": "1", "photo": img, "title": title[:99], "message": desc + "\n\n#travel #cheapflights #budgettravel #europetravel", "link": link + "?utm_source=pinterest"}
        from precheck import prepare
        body = prepare(body, "pinterest", feed=False)
        if "photo" not in body:
            print("pin skipped, photo broken:", key)
            done.add(key)
            continue
        try:
            urllib.request.urlopen(urllib.request.Request(HOOK, data=json.dumps(body).encode(), headers={"Content-Type": "application/json"}), timeout=30)
            print("Pinned", key)
        except Exception as e:
            print("pin failed", key, e)
            break
        done.add(key)
        sent += 1
        if sent >= PER_RUN:
            break
    os.makedirs("data", exist_ok=True)
    json.dump(sorted(done), open(STATE, "w"))


if __name__ == "__main__":
    main()
