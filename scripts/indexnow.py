"""Tell Bing, Yandex, Naver, Seznam (IndexNow) about blog pages when the sitemap changes. Standard library only."""
import hashlib, json, os, re, urllib.request
KEY = "a84a5ac056ae7fd3e679fda8ac17d8c0"
SITE = "https://tripwisehub-blip.github.io/tripwise-app/"
sm = open("blog/sitemap.xml", encoding="utf-8").read()
urls = re.findall(r"<loc>([^<]+)</loc>", sm) + [SITE]
h = hashlib.sha256(sm.encode()).hexdigest()
state = "data/indexnow.txt"
if os.path.exists(state) and open(state).read().strip() == h:
    print("sitemap unchanged"); raise SystemExit
body = {"host": "tripwisehub-blip.github.io", "key": KEY, "keyLocation": SITE + KEY + ".txt", "urlList": urls}
req = urllib.request.Request("https://api.indexnow.org/indexnow", data=json.dumps(body).encode(),
                             headers={"Content-Type": "application/json; charset=utf-8"}, method="POST")
try:
    with urllib.request.urlopen(req, timeout=30) as r:
        print("IndexNow:", r.status, len(urls), "urls")
    os.makedirs("data", exist_ok=True); open(state, "w").write(h)
except Exception as e:
    print("IndexNow failed:", e)
