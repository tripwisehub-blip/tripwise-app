"""Daily vertical "cheap flights" video (Reels / Shorts / TikTok) for Tripwise.

Builds a 15-second 1080x1920 MP4 from data/prices.json: a hook slide, the 3 cheapest return trips from one city
(photos from Wikipedia) and a call-to-action slide. Saves it to blog/videos/<date>.mp4 plus blog/videos/latest.json
with the caption. Posting happens later (video_post.py) once GitHub Pages serves the file.
Needs Pillow and ffmpeg. Runs once a day (state in data/video_last.txt).
"""
import datetime
import glob
import io
import json
import os
import subprocess
import tempfile
import urllib.parse
import urllib.request

from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1080, 1920
NAVY, YELLOW, WHITE = (11, 27, 58), (255, 205, 0), (255, 255, 255)
ORIGIN_NAMES = {"TLL": "Tallinn", "HEL": "Helsinki", "RIX": "Riga", "VNO": "Vilnius", "LON": "London", "BER": "Berlin",
                "WAW": "Warsaw", "PAR": "Paris", "AMS": "Amsterdam", "STO": "Stockholm"}
OUT_DIR = "blog/videos"
STATE = "data/video_last.txt"
FONT_DIRS = ["/usr/share/fonts/truetype/dejavu/", "/usr/share/fonts/dejavu/"]
SLIDE_SEC, FADE = 3.4, 0.5


def font(size, bold=True):
    name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    for d in FONT_DIRS:
        if os.path.exists(d + name):
            return ImageFont.truetype(d + name, size)
    return ImageFont.load_default()


def fetch(url, timeout=20):
    req = urllib.request.Request(url, headers={"User-Agent": "TripwiseBot/1.0 (https://t.me/tripwise_deals)"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def wiki_photo(title):
    try:
        j = json.loads(fetch("https://en.wikipedia.org/api/rest_v1/page/summary/" + urllib.parse.quote(title.replace(" ", "_"))))
        src = (j.get("thumbnail") or {}).get("source", "")
        cands = []
        if "px-" in src:
            head, _, tail = src.partition("px-")
            cands = [head[:head.rfind("/") + 1] + w + "px-" + tail for w in ("1280", "960")]
        cands.append(src)
        for u in cands:
            try:
                return Image.open(io.BytesIO(fetch(u))).convert("RGB")
            except Exception:
                continue
    except Exception as e:
        print("photo failed", title, e)
    return None


def cover(img):
    """Crop/scale an image to fill 1080x1920, or make a gradient when there is no photo."""
    if img is None:
        img = Image.new("RGB", (W, H), NAVY)
        d = ImageDraw.Draw(img)
        for y in range(H):
            t = y / H
            d.line([(0, y), (W, y)], fill=(int(11 + 40 * t), int(27 + 30 * t), int(58 + 60 * t)))
        return img
    r = max(W / img.width, H / img.height)
    img = img.resize((int(img.width * r) + 1, int(img.height * r) + 1), Image.LANCZOS)
    x, y = (img.width - W) // 2, (img.height - H) // 2
    return img.crop((x, y, x + W, y + H))


def shade(img, top=0.35, bottom=0.85):
    """Darken the image towards the bottom so white text is readable."""
    over = Image.new("L", (1, H))
    for y in range(H):
        t = y / H
        over.putpixel((0, y), int(255 * (top + (bottom - top) * t) * 0.8))
    over = over.resize((W, H))
    black = Image.new("RGB", (W, H), (0, 0, 0))
    return Image.composite(black, img, over)


def text_c(d, y, s, f, fill=WHITE, maxw=W - 120):
    while d.textlength(s, font=f) > maxw and f.size > 30:
        f = font(f.size - 4)
    x = (W - d.textlength(s, font=f)) / 2
    d.text((x + 3, y + 3), s, font=f, fill=(0, 0, 0))
    d.text((x, y), s, font=f, fill=fill)
    return y + f.size + 20


def pill(d, y, s, f, bg=YELLOW, fg=NAVY):
    tw = d.textlength(s, font=f)
    pad = 36
    x0 = (W - tw) / 2 - pad
    d.rounded_rectangle([x0, y, x0 + tw + 2 * pad, y + f.size + 44], radius=40, fill=bg)
    d.text((x0 + pad, y + 18), s, font=f, fill=fg)
    return y + f.size + 80


def brand(d):
    f = font(40)
    s = "TRIPWISE"
    d.text(((W - d.textlength(s, font=f)) / 2, 110), s, font=f, fill=YELLOW)


def span(a, b):
    x, y = datetime.date.fromisoformat(a), datetime.date.fromisoformat(b)
    if x.month == y.month:
        return "%d-%d %s" % (x.day, y.day, y.strftime("%b"))
    return "%d %s - %d %s" % (x.day, x.strftime("%b"), y.day, y.strftime("%b"))


SITE = "https://tripwisehub-blip.github.io/tripwise-app/blog/"


def post_pending():
    """Send the last made video to the Make webhook (Instagram Reels, Facebook, YouTube) once Pages serves it."""
    hook = os.environ.get("FB_HOOK", "").strip()
    meta_path = OUT_DIR + "/latest.json"
    if not hook or not os.path.exists(meta_path):
        return
    meta = json.load(open(meta_path))
    if meta.get("posted"):
        return
    url = SITE + meta["file"]
    try:
        urllib.request.urlopen(urllib.request.Request(url, method="HEAD"), timeout=20)
    except Exception as e:
        print("Video not live yet:", e)
        return
    body = {"video": url, "cover": SITE + meta.get("cover", ""), "title": meta["title"], "message": meta["caption"], "link": SITE}
    try:
        urllib.request.urlopen(urllib.request.Request(hook, data=json.dumps(body).encode(),
                                                      headers={"Content-Type": "application/json"}), timeout=30)
        meta["posted"] = True
        json.dump(meta, open(meta_path, "w"), ensure_ascii=False, indent=1)
        print("Video sent to social networks:", url)
    except Exception as e:
        print("Video post failed:", e)



# ---------- background music: synthesized here, so it is 100% original and copyright-free ----------
def make_music(path, seconds, seed):
    """Upbeat lo-fi/pop loop: chords (soft pad), bass, plucked melody, kick and hi-hat. Key and tempo change by day."""
    import array, math, random, wave
    rnd = random.Random(seed)
    sr = 44100
    bpm = rnd.choice([96, 100, 104, 108, 112])
    beat = 60.0 / bpm
    root = rnd.choice([0, 2, 3, 5, 7, 8, 10])  # semitones above A2
    progs = [[0, 7, 9, 5], [0, 5, 9, 7], [9, 5, 0, 7], [0, 9, 5, 7]]  # I-V-vi-IV and friends
    prog = rnd.choice(progs)
    major = {0: [0, 4, 7], 5: [0, 4, 7], 7: [0, 4, 7], 9: [0, 3, 7]}
    scale = [0, 2, 4, 7, 9, 12, 14, 16]
    n = int(sr * seconds)
    buf = [0.0] * n
    def f(semi):
        return 110.0 * 2 ** ((semi + root) / 12.0)
    def add(start, dur, freq, amp, kind="sine", decay=3.0):
        a, b = int(start * sr), min(n, int((start + dur) * sr))
        w = 2 * math.pi * freq / sr
        att = int(0.01 * sr)
        for i in range(a, b):
            t = (i - a) / sr
            env = math.exp(-decay * t) * min(1.0, (i - a) / att if att else 1.0)
            ph = w * (i - a)
            if kind == "pad":
                v = math.sin(ph) + 0.3 * math.sin(2 * ph) + 0.15 * math.sin(3 * ph)
            elif kind == "pluck":
                v = math.sin(ph) + 0.5 * math.sin(2 * ph) * math.exp(-8 * t)
            else:
                v = math.sin(ph)
            buf[i] += amp * env * v
    bar = 4 * beat
    t, k = 0.0, 0
    while t < seconds:
        ch = prog[k % 4]
        for iv in major[ch]:
            add(t, bar, f(ch + iv + 12), 0.05, "pad", 0.6)
        for q in range(4):  # bass on every beat
            add(t + q * beat, beat * 0.9, f(ch - 12 + (7 if q == 2 else 0)), 0.16, "sine", 2.5)
        for q in range(8):  # melody on eighth notes, sparse
            if rnd.random() < 0.55:
                add(t + q * beat / 2, beat / 2, f(ch + 24 + rnd.choice(scale)), 0.07, "pluck", 6.0)
        for q in range(4):  # kick on 1 and 3, hat on eighths
            if q % 2 == 0:
                a = int((t + q * beat) * sr)
                for i in range(a, min(n, a + int(0.18 * sr))):
                    tt = (i - a) / sr
                    buf[i] += 0.5 * math.exp(-18 * tt) * math.sin(2 * math.pi * (50 + 90 * math.exp(-30 * tt)) * tt)
            for h in range(2):
                a = int((t + q * beat + h * beat / 2) * sr)
                for i in range(a, min(n, a + int(0.03 * sr))):
                    buf[i] += 0.04 * math.exp(-120 * (i - a) / sr) * (rnd.random() * 2 - 1)
        t += bar
        k += 1
    fade = int(1.5 * sr)
    peak = max(1e-6, max(abs(x) for x in buf))
    out = array.array("h")
    for i, x in enumerate(buf):
        g = min(1.0, i / (0.3 * sr), (n - i) / fade)
        v = int(26000 * g * x / peak)
        out.append(v)
        out.append(v)
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(out.tobytes())

def main():
    post_pending()
    today = datetime.date.today()
    if os.path.exists(STATE) and open(STATE).read().strip() == today.isoformat():
        print("Video already made today")
        return
    prices = json.load(open("data/prices.json"))
    names = prices.get("names") or {}
    origins = list(ORIGIN_NAMES)
    deals = []
    for k in range(len(origins)):
        origin = origins[(today.toordinal() * 3 + k) % len(origins)]
        trips = [t for t in (prices.get("origins") or {}).get(origin, []) if t.get("dep", "") > today.isoformat()]
        best = {}
        for t in trips:
            if t["d"] not in best or t["p"] < best[t["d"]]["p"]:
                best[t["d"]] = t
        deals = sorted(best.values(), key=lambda t: t["p"])[:3]
        if len(deals) == 3:
            break
    if len(deals) < 3:
        print("Not enough deals")
        return
    city = ORIGIN_NAMES[origin]

    def nm(code):
        n = names.get(code)
        return n[0] if n and n[0] else code

    photos = [wiki_photo(nm(t["d"])) for t in deals]
    slides = []
    # 1. hook
    img = shade(cover(photos[0]), 0.45, 0.8)
    d = ImageDraw.Draw(img)
    brand(d)
    y = 640
    y = text_c(d, y, "CHEAP FLIGHTS", font(104))
    y = text_c(d, y, "from %s" % city, font(84), YELLOW)
    y += 40
    pill(d, y, "from EUR %d return" % round(deals[0]["p"]), font(56))
    text_c(d, 1620, "Wait for the prices...", font(44, False))
    slides.append(img)
    # 2-4. deals
    for i, t in enumerate(deals):
        img = shade(cover(photos[i]), 0.25, 0.85)
        d = ImageDraw.Draw(img)
        brand(d)
        text_c(d, 1080, "#%d" % (i + 1), font(70), YELLOW)
        text_c(d, 1170, nm(t["d"]).upper(), font(110))
        pill(d, 1320, "EUR %d" % round(t["p"]), font(96))
        text_c(d, 1520, "%s -> %s  |  %s" % (city, nm(t["d"]), span(t["dep"], t["ret"])), font(42, False))
        text_c(d, 1590, "direct flight" if not t.get("tr") else "with stops", font(42, False))
        slides.append(img)
    # 5. call to action
    img = cover(None)
    d = ImageDraw.Draw(img)
    brand(d)
    y = 620
    y = text_c(d, y, "New deals", font(100))
    y = text_c(d, y, "every day", font(100), YELLOW)
    y += 60
    y = pill(d, y, "Link in bio", font(64))
    y = text_c(d, y + 20, "Telegram: @tripwise_deals", font(52, False))
    text_c(d, y + 10, "Follow so you don't miss them", font(44, False))
    slides.append(img)

    os.makedirs(OUT_DIR, exist_ok=True)
    out = "%s/%s.mp4" % (OUT_DIR, today.isoformat())
    with tempfile.TemporaryDirectory() as tmp:
        cmd = ["ffmpeg", "-y", "-loglevel", "error"]
        for i, s in enumerate(slides):
            p = "%s/s%d.jpg" % (tmp, i)
            s.save(p, quality=92)
            cmd += ["-loop", "1", "-t", str(SLIDE_SEC), "-i", p]
        song = tmp + "/music.wav"
        make_music(song, len(slides) * SLIDE_SEC, today.toordinal())
        cmd += ["-i", song]
        parts, prev = [], None
        for i in range(len(slides)):
            # slow zoom-in on every slide
            parts.append("[%d:v]scale=1188:2112,zoompan=z='min(zoom+0.0009,1.1)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=%d:s=%dx%d:fps=30,setsar=1[v%d]"
                         % (i, int(SLIDE_SEC * 30), W, H, i))
        prev = "v0"
        for i in range(1, len(slides)):
            off = i * (SLIDE_SEC - FADE)
            parts.append("[%s][v%d]xfade=transition=slideleft:duration=%s:offset=%.2f[x%d]" % (prev, i, FADE, off, i))
            prev = "x%d" % i
        cmd += ["-filter_complex", ";".join(parts), "-map", "[%s]" % prev, "-map", "%d:a" % len(slides),
                "-shortest", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-profile:v", "high", "-crf", "23",
                "-c:a", "aac", "-b:a", "96k", "-movflags", "+faststart", out]
        subprocess.run(cmd, check=True)
        slides[0].save("%s/%s.jpg" % (OUT_DIR, today.isoformat()), quality=88)

    for old in sorted(glob.glob(OUT_DIR + "/*.mp4"))[:-3] + sorted(glob.glob(OUT_DIR + "/*.jpg"))[:-3]:
        os.remove(old)
    lines = ["Cheap flights from %s this week ✈️" % city, ""]
    for i, t in enumerate(deals):
        lines.append("%s %s — €%d return (%s)" % (["🥇", "🥈", "🥉"][i], nm(t["d"]), round(t["p"]), span(t["dep"], t["ret"])))
    lines += ["", "Fresh deals every day 👉 link in bio / Telegram @tripwise_deals",
              "", "#cheapflights #travel #traveltips #%s #budgettravel #travelhacks" % city.lower()]
    meta = {"date": today.isoformat(), "file": out.replace("blog/", ""), "cover": "videos/%s.jpg" % today.isoformat(),
            "title": "Cheap flights from %s from €%d ✈️ #shorts" % (city, round(deals[0]["p"])),
            "caption": "\n".join(lines), "posted": False}
    json.dump(meta, open(OUT_DIR + "/latest.json", "w"), ensure_ascii=False, indent=1)
    os.makedirs("data", exist_ok=True)
    open(STATE, "w").write(today.isoformat())
    print("Video saved", out)


if __name__ == "__main__":
    main()
