"""Apply the Telegram bot's name, short description and description from data/bot_profile.json.

Run by .github/workflows/bot_profile.yml when that file changes. Needs TG_BOT_TOKEN. Standard library only.
Prints only Telegram's ok/description answers, never the token.
"""
import json, os, sys, time, urllib.parse, urllib.request

TOKEN = os.environ.get("TG_BOT_TOKEN", "").strip()
if not TOKEN:
    sys.exit("TG_BOT_TOKEN is not set")
LIMITS = {"name": 64, "short": 120, "description": 512}
CALLS = {"name": ("setMyName", "name"), "short": ("setMyShortDescription", "short_description"),
         "description": ("setMyDescription", "description")}


def call(method, params):
    data = urllib.parse.urlencode(params).encode()
    req = urllib.request.Request(f"https://api.telegram.org/bot{TOKEN}/{method}", data=data)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        try:
            return json.load(e)
        except Exception:
            return {"ok": False, "description": str(e)}


profile = json.load(open(os.path.join(os.path.dirname(__file__), "..", "data", "bot_profile.json"), encoding="utf-8"))
failed = 0
for lang, texts in profile.items():
    if lang.startswith("_"):
        continue
    for key, (method, field) in CALLS.items():
        text = texts.get(key)
        if not text:
            continue
        if len(text) > LIMITS[key]:
            print(f"[{lang or 'default'}] {key}: too long ({len(text)} > {LIMITS[key]}), skipped"); failed += 1
            continue
        params = {field: text}
        if lang:
            params["language_code"] = lang
        for attempt in range(3):
            res = call(method, params)
            retry = (res.get("parameters") or {}).get("retry_after")
            if res.get("ok") or not retry:
                break
            print(f"[{lang or 'default'}] {key}: rate limited, waiting {retry}s")
            time.sleep(min(int(retry), 120) + 1)
        print(f"[{lang or 'default'}] {key}: {'ok' if res.get('ok') else res.get('description')}")
        failed += 0 if res.get("ok") else 1
        time.sleep(1)
print("current default name:", (call("getMyName", {}).get("result") or {}).get("name"))
sys.exit(1 if failed else 0)
