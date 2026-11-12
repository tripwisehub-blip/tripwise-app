"""Pre-publish check for social posts (the "post checker agent").

Every script that sends a post to the Make webhook (FB_HOOK) calls prepare(body, source) first.
The bot worker (/check) then:
  - replaces long links with short pretty ones (go.tripwise-hub.workers.dev/f/tll-bcn-2511-0212, /b/<slug>, /bot, /deals…),
  - opens every link, photo and video and replaces or drops anything broken,
  - builds the Instagram caption ("ig"): no URLs, because Instagram captions are not clickable, only "link in bio",
  - adds the post to the link-in-bio page https://go.tripwise-hub.workers.dev/ig (set it as the Instagram bio link).
Problems are printed in the workflow log and saved to data/precheck_log.json.
If the worker can't be reached, a local fallback still removes URLs from the Instagram caption.
"""
import hashlib, json, os, re, datetime, urllib.request

URL_RE = re.compile(r"https?://[^\s<>()\"']+[^\s<>()\"'.,!?;:]")
LOG = "data/precheck_log.json"


def _worker():
    try:
        return open("data/bot_worker.txt").read().strip() or "https://tripwise-bot.tripwise-hub.workers.dev"
    except OSError:
        return "https://tripwise-bot.tripwise-hub.workers.dev"


def _local_ig(text):
    t = "\n".join(re.sub(r"[:：]\s*$", ": 🔗 link in bio", URL_RE.sub("", l).rstrip()) for l in text.split("\n"))
    t = re.sub(r"\n{3,}", "\n\n", t).strip()
    if "link in bio" not in t:
        t += "\n\n🔗 Links: tap the link in bio"
    return t[:2200]


def prepare(body, source="social", feed=True):
    token = os.environ.get("TG_BOT_TOKEN", "").strip()
    req = dict(body, source=source, feed=feed)
    try:
        if not token:
            raise RuntimeError("no TG_BOT_TOKEN")
        r = urllib.request.Request(_worker() + "/check", data=json.dumps(req).encode(), method="POST",
                                   headers={"Content-Type": "application/json", "X-Key": hashlib.sha256(token.encode()).hexdigest()})
        with urllib.request.urlopen(r, timeout=60) as resp:
            res = json.load(resp)
    except Exception as e:
        print("precheck: worker unavailable (%s), local fallback" % e)
        out = dict(body)
        out["ig"] = _local_ig(body.get("message", ""))
        return out
    out = dict(body)
    out["ig"] = res["ig"]
    if source != "pinterest":  # Pinterest dislikes redirect links: keep the original, only check it
        out["message"] = res["message"]
        if body.get("link"):
            out["link"] = res["link"]
    for k in ("photo", "cover", "video"):
        if k in body and k not in res:
            out.pop(k)
    for p in res.get("problems", []):
        print("precheck PROBLEM:", p)
    print("precheck: %d links/media checked, %d problems" % (len(res.get("checked", [])), len(res.get("problems", []))))
    try:
        log = json.load(open(LOG)) if os.path.exists(LOG) else []
        log.append({"at": datetime.datetime.utcnow().isoformat(timespec="minutes"), "source": source,
                    "problems": res.get("problems", []), "checked": len(res.get("checked", []))})
        os.makedirs("data", exist_ok=True)
        json.dump(log[-60:], open(LOG, "w"), ensure_ascii=False, indent=1)
    except Exception:
        pass
    return out
