import os, sys, html, json
sys.path.insert(0, os.path.dirname(__file__))
from blog_content import GUIDES, A, BOT, L

NL = chr(10)
OUT = os.environ.get("BLOG_OUT") or os.path.join(os.path.dirname(__file__), "out", "blog")
os.makedirs(OUT, exist_ok=True)
BASE = A + "blog/"
CSS = """
:root{--navy:#0B2340;--navy2:#13335A;--sign:#FFCC00;--paper:#fff;--bg:#EEF3F7;--ink:#10202F;--muted:#55677A;--line:#D5DEE7;--link:#1457A8}
@media (prefers-color-scheme:dark){:root{--paper:#122236;--bg:#0A1726;--ink:#E7EEF5;--muted:#9DB0C3;--line:#22384F;--link:#7DB6FF}}
*{box-sizing:border-box}html{scroll-behavior:smooth}
body{margin:0;background:var(--bg);color:var(--ink);font:17px/1.6 "Bricolage Grotesque",system-ui,sans-serif}
a{color:var(--link)}:focus-visible{outline:3px solid var(--sign);outline-offset:2px}
.wrap{max-width:1120px;margin:0 auto;padding:0 16px}
.top{background:var(--navy);color:#fff}
.top .wrap{display:flex;align-items:center;justify-content:space-between;gap:12px;min-height:64px}
.logo{font-weight:800;font-size:21px;color:#fff;text-decoration:none;letter-spacing:-.01em}.logo i{font-style:normal;color:var(--sign)}
nav{display:flex;align-items:center;gap:18px}nav a{color:#C9D6E4;text-decoration:none;font-size:15px}nav a:hover{color:#fff}
nav .tg{background:var(--sign);color:var(--navy);font-weight:700;padding:8px 14px;border-radius:8px}nav .tg:hover{color:var(--navy)}
@media(max-width:560px){nav .hide-s{display:none}}
h1,h2,h3{line-height:1.12;letter-spacing:-.015em}
.board{background:var(--navy);color:#fff;padding:28px 0 40px}
.board h1{font-size:clamp(34px,6.4vw,64px);font-weight:800;margin:6px 0 10px;max-width:14ch}
.board p.sub{color:#B9C9DA;font-size:18px;margin:0 0 22px;max-width:52ch}
.search{width:100%;max-width:560px;font:inherit;font-size:17px;padding:14px 16px;border-radius:10px;border:2px solid transparent;background:#fff;color:#10202F}
.search:focus{outline:0;border-color:var(--sign)}
.rows{margin-top:30px;border-top:1px solid var(--navy2)}
.row{display:grid;grid-template-columns:1.1fr 1fr 2fr auto;gap:16px;align-items:center;padding:13px 4px;border-bottom:1px solid var(--navy2);color:#fff;text-decoration:none}
.row:hover{background:var(--navy2)}
.row .c{color:var(--sign);font-weight:700;font-size:20px;font-variant-numeric:tabular-nums;white-space:nowrap}
.row .k{color:#B9C9DA}.row .t{color:#fff}.row .go{color:var(--sign);font-weight:600;font-size:15px}
.rows .hd{display:grid;grid-template-columns:1.1fr 1fr 2fr auto;gap:16px;padding:10px 4px;color:#7F97B0;font-size:13px}
@media(max-width:700px){.row,.rows .hd{grid-template-columns:1fr auto}.row .k,.rows .hd .k{display:none}.row .t{grid-column:1/-1;grid-row:2;font-size:15px;color:#B9C9DA}.rows .hd{display:none}.row{padding:12px 4px}.row .t{margin-top:-8px}}
.chips{display:flex;gap:8px;overflow-x:auto;padding:18px 0 4px;scrollbar-width:none}.chips::-webkit-scrollbar{display:none}
.chips a{flex:none;background:var(--paper);border:1px solid var(--line);border-radius:999px;padding:7px 14px;font-size:15px;text-decoration:none;color:var(--ink)}
.chips a:hover{border-color:var(--ink)}
.country{margin:44px 0 16px;font-size:clamp(26px,4vw,36px);font-weight:800;text-transform:uppercase;letter-spacing:.02em;display:flex;align-items:baseline;gap:12px;flex-wrap:wrap}
.country small{font-size:15px;font-weight:500;letter-spacing:0;text-transform:none;color:var(--muted)}
.grid{display:grid;gap:14px;grid-template-columns:repeat(2,1fr)}@media(min-width:760px){.grid{grid-template-columns:repeat(3,1fr);gap:20px}}@media(min-width:1040px){.grid{grid-template-columns:repeat(4,1fr)}}
.tile{text-decoration:none;color:var(--ink);display:block}
.ph{position:relative;aspect-ratio:4/5;border-radius:12px;overflow:hidden;background:var(--navy2) center/cover no-repeat}
.ph span{position:absolute;left:14px;right:14px;bottom:12px;color:#fff;font-weight:800;font-size:clamp(19px,2.6vw,26px);line-height:1.05;text-shadow:0 1px 10px rgba(0,0,0,.45)}
.tile b{display:block;padding:10px 2px 0;font-size:15px;font-weight:500;line-height:1.35;color:var(--muted)}
.tile:hover b{color:var(--ink);text-decoration:underline}
.pass{display:grid;grid-template-columns:1fr 150px;margin:56px 0 0;background:var(--paper);border-radius:14px;overflow:hidden;border:1px solid var(--line)}
.pass .m{padding:24px 24px 26px}.pass h2{margin:0 0 6px;font-size:26px}.pass p{margin:0 0 16px;color:var(--muted)}
.pass .stub{background:var(--sign);color:var(--navy);display:flex;flex-direction:column;justify-content:center;align-items:center;font-weight:800;font-size:15px;border-left:2px dashed var(--navy);text-align:center;padding:12px}
.pass .stub span{font-size:40px;line-height:1}
@media(max-width:600px){.pass{grid-template-columns:1fr}.pass .stub{border-left:0;border-top:2px dashed var(--navy);flex-direction:row;gap:10px;padding:14px}}
.btn{display:inline-block;background:var(--navy);color:#fff;text-decoration:none;font-weight:700;padding:12px 18px;border-radius:9px;margin:4px 8px 0 0}
.btn.alt{background:transparent;color:var(--ink);border:2px solid var(--line)}
@media (prefers-color-scheme:dark){.btn{background:var(--sign);color:var(--navy)}}
footer{background:var(--navy);color:#9FB3C8;margin-top:64px;padding:28px 0 36px;font-size:14px}footer a{color:#C9D6E4;margin-right:16px}footer p{margin:0 0 10px}
.hero{position:relative;min-height:340px;display:flex;align-items:flex-end;background:var(--navy2) center/cover no-repeat;color:#fff}
.hero .wrap{width:100%;padding-bottom:28px;padding-top:60px}
.hero h1{font-size:clamp(30px,5.2vw,52px);font-weight:800;margin:6px 0 0;max-width:22ch;text-shadow:0 2px 14px rgba(0,0,0,.35)}
.hero .tag{color:var(--sign);font-weight:700;font-size:15px}
article.guide{max-width:700px;margin:0 auto;padding:28px 16px 0;font:19px/1.72 "Source Serif 4",Georgia,serif}
article.guide h2,article.guide h3,article.guide .note,article.guide .meta,article.guide .pass,article.guide .more{font-family:"Bricolage Grotesque",system-ui,sans-serif}
article.guide h2{font-size:27px;margin:38px 0 10px}article.guide h3{font-size:21px;margin:28px 0 8px}
.lead{font-size:21px;color:var(--ink)}.meta{color:var(--muted);font-size:14px}
.note{background:var(--paper);border:1px solid var(--line);border-radius:10px;padding:12px 14px;font-size:15px;line-height:1.5;color:var(--muted);margin:20px 0}
.more{margin-top:48px}.more .grid{grid-template-columns:repeat(3,1fr);gap:12px}.more .ph{aspect-ratio:1}.more .ph span{font-size:17px}
.page{max-width:700px;margin:0 auto;padding:32px 16px 0}

@media (prefers-reduced-motion:reduce){html{scroll-behavior:auto}}
"""
DISC = ('<div class="note">Some links on this page are affiliate links. If you book through them, Tripwise may earn a small commission '
        'at no extra cost to you. It helps keep our guides and app free. <a href="disclosure.html">Learn more</a>.</div>')
CTA = (f'<div class="pass"><div class="m"><h2>Ask the travel bot</h2><p>Tell it where you want to go, in any language. It finds cheap flights, '
       f'suggests hotels and tours, and sends a message when prices drop.</p><a class="btn" href="{BOT}">Open in Telegram</a>'
       f'<a class="btn alt" href="https://t.me/tripwise_deals">Daily deals: @tripwise_deals</a><a class="btn alt" href="{A}">Open the web app</a></div><div class="stub"><span>✈</span>Free, no sign-up</div></div>')

# Country, city label and Wikipedia photo title for each guide (index layout and hero images)
META = {
    "tallinn-on-a-budget": ("Estonia", "Tallinn", "Tallinn"),
    "tallinn-airport-to-city": ("Estonia", "Tallinn Airport", "Lennart Meri Tallinn Airport"),
    "tallinn-to-helsinki": ("Estonia", "Tallinn – Helsinki ferry", "MS Megastar"),
    "helsinki-city-guide": ("Finland", "Helsinki", "Helsinki"),
    "helsinki-airport-to-city": ("Finland", "Helsinki Airport", "Helsinki Airport"),
    "lapland-rovaniemi-winter": ("Finland", "Rovaniemi, Lapland", "Rovaniemi"),
    "riga-weekend-guide": ("Latvia", "Riga", "Riga"),
    "riga-to-tallinn": ("Latvia", "Riga – Tallinn", "Riga Central Station"),
    "vilnius-weekend": ("Lithuania", "Vilnius", "Vilnius"),
    "baltics-best-time-to-visit": ("Baltic States", "Estonia, Latvia, Lithuania", "Curonian Spit"),
    "prague-on-a-budget": ("Czechia", "Prague", "Prague"),
    "barcelona-first-time": ("Spain", "Barcelona", "Barcelona"),
    "rome-in-three-days": ("Italy", "Rome", "Rome"),
    "lisbon-guide": ("Portugal", "Lisbon", "Lisbon"),
    "istanbul-guide": ("Türkiye", "Istanbul", "Istanbul"),
    "dubai-on-a-budget": ("United Arab Emirates", "Dubai", "Dubai"),
    "bangkok-guide": ("Thailand", "Bangkok", "Bangkok"),
    "tenerife-winter-sun": ("Spain", "Tenerife", "Teide National Park"),
    "antalya-guide": ("Türkiye", "Antalya", "Antalya"),
    "hurghada-guide": ("Egypt", "Hurghada", "Hurghada"),
    "budapest-on-a-budget": ("Hungary", "Budapest", "Budapest"),
    "krakow-weekend": ("Poland", "Kraków", "Kraków"),
    "paris-first-time": ("France", "Paris", "Paris"),
    "christmas-markets-europe": ("Travel tips", "Christmas markets", "Christmas market"),
    "vienna-guide": ("Austria", "Vienna", "Vienna"),
    "amsterdam-on-a-budget": ("Netherlands", "Amsterdam", "Amsterdam"),
    "london-on-a-budget": ("United Kingdom", "London", "London"),
    "madeira-winter": ("Portugal", "Madeira", "Funchal"),
    "bali-guide": ("Indonesia", "Bali", "Pura Ulun Danu Bratan"),
    "how-to-find-cheap-flights": ("Travel tips", "Cheap flights", "Airliner"),
    "esim-for-travel": ("Travel tips", "eSIM", "SIM card"),
    "flight-delay-compensation": ("Travel tips", "Flight delays", "Frankfurt Airport"),
}
FLAGS = {"Estonia": "🇪🇪", "Finland": "🇫🇮", "Latvia": "🇱🇻", "Lithuania": "🇱🇹", "Baltic States": "🧭", "Czechia": "🇨🇿", "Spain": "🇪🇸",
         "Italy": "🇮🇹", "Portugal": "🇵🇹", "Türkiye": "🇹🇷", "United Arab Emirates": "🇦🇪", "Thailand": "🇹🇭", "Egypt": "🇪🇬", "Hungary": "🇭🇺", "Poland": "🇵🇱", "France": "🇫🇷", "Austria": "🇦🇹", "Netherlands": "🇳🇱", "United Kingdom": "🇬🇧", "Indonesia": "🇮🇩", "Travel tips": "💡"}

PHOTO_JS = """<script>
(function(){var cache={};
function load(t,w){var k=t+w;if(cache[k])return cache[k];cache[k]=fetch('https://en.wikipedia.org/api/rest_v1/page/summary/'+encodeURIComponent(t.replace(/ /g,'_'))).then(function(r){return r.ok?r.json():{}}).then(function(j){var s=(j.thumbnail&&j.thumbnail.source)||'';if(!s)return '';var p=s.split('px-');return p.length>1?p[0].slice(0,p[0].lastIndexOf('/')+1)+w+'px-'+p.slice(1).join('px-')+'"),url("'+s:s;}).catch(function(){return ''});return cache[k];}
document.querySelectorAll('[data-photo]').forEach(function(el){var big=el.classList.contains('hero');load(el.getAttribute('data-photo'),big?1280:500).then(function(u){if(u)el.style.backgroundImage=(big?'linear-gradient(rgba(11,35,64,.1),rgba(11,35,64,.78))':'linear-gradient(transparent 50%,rgba(0,0,0,.6))')+',url("'+u+'")';});});
var q=document.getElementById('q');if(q)q.addEventListener('input',function(){var v=q.value.toLowerCase().trim();document.querySelectorAll('.tile,.row').forEach(function(t){t.style.display=!v||t.textContent.toLowerCase().indexOf(v)>=0?'':'none';});document.querySelectorAll('section.cs').forEach(function(sc){var any=[].some.call(sc.querySelectorAll('.tile'),function(t){return t.style.display!=='none'});sc.style.display=any?'':'none';});});
if(!window.matchMedia('(prefers-reduced-motion: reduce)').matches){var A='ABCDEFGHIJKLMNOPRSTUVWZ';document.querySelectorAll('.row .c').forEach(function(el,i){var f=el.textContent,n=0,id=setInterval(function(){n++;var k=Math.floor(n/2)-i;el.textContent=f.split('').map(function(ch,j){return j<k||ch===' '?ch:A[Math.floor(Math.random()*A.length)]}).join('');if(k>=f.length){clearInterval(id);el.textContent=f;}},45);});}
})();
</script>"""


def page(name, title, desc, body, extra_head=""):
    doc = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)}</title><meta name="description" content="{html.escape(desc)}">
<link rel="canonical" href="{BASE}{'' if name == 'index.html' else name}">
<meta property="og:title" content="{html.escape(title)}"><meta property="og:description" content="{html.escape(desc)}"><meta property="og:type" content="article"><meta property="og:url" content="{BASE}{'' if name == 'index.html' else name}"><meta property="og:site_name" content="Tripwise Guides">
<link rel="alternate" type="application/rss+xml" title="Tripwise Guides" href="{BASE}feed.xml">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,400..800&family=Source+Serif+4:opsz,wght@8..60,400;8..60,600&display=swap" rel="stylesheet">
{extra_head}<style>{CSS}</style></head><body>
<header class="top"><div class="wrap"><a class="logo" href="index.html">Trip<i>wise</i></a><nav><a href="index.html">Guides</a><a class="hide-s" href="https://t.me/tripwise_deals">Deals channel</a><a class="hide-s" href="about.html">About</a><a class="tg" href="{BOT}">Telegram bot</a></nav></div></header>
<main>{body}</main>
<footer><div class="wrap"><p>Independent travel guides by Tripwise, 2026.</p><a href="about.html">About</a><a href="disclosure.html">Affiliate disclosure</a><a href="privacy.html">Privacy</a><a href="mailto:tripwise.hub@gmail.com">Contact</a></div></footer>
{PHOTO_JS}</body></html>"""
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(doc)


for g in GUIDES:
    others = [o for o in GUIDES if o is not g][:3]
    more = '<div class="more"><h2>More guides</h2><div class="grid">' + "".join(
        f'<a class="tile" href="{o["slug"]}.html"><div class="ph" data-photo="{html.escape(META[o["slug"]][2])}"><span>{html.escape(META[o["slug"]][1])}</span></div><b>{html.escape(o["title"])}</b></a>' for o in others) + "</div></div>"
    hero = (f'<div class="hero" data-photo="{html.escape(META.get(g["slug"], ("", "", g["tag"]))[2])}"><div class="wrap">'
            f'<span class="tag">{g["tag"]}</span><h1>{html.escape(g["title"])}</h1></div></div>')
    body = (hero + f'<article class="guide"><p class="lead">{html.escape(g["desc"])}</p>'
            f'<p class="meta">Updated October 2026. Prices and schedules change, so check current details before booking.</p>'
            + DISC + g["body"] + CTA + more + '</article>')
    ld = json.dumps({"@context": "https://schema.org", "@type": "Article", "headline": g["title"], "description": g["desc"],
                     "dateModified": "2026-10-28", "author": {"@type": "Organization", "name": "Tripwise"},
                     "publisher": {"@type": "Organization", "name": "Tripwise"}, "mainEntityOfPage": BASE + g["slug"] + ".html"}, ensure_ascii=False)
    page(g["slug"] + ".html", g["title"] + " | Tripwise Guides", g["desc"], body, f'<script type="application/ld+json">{ld}</script>')

order, groups = [], {}
for g in GUIDES:
    c = META.get(g["slug"], ("Travel tips", g["tag"], g["tag"]))[0]
    if c not in groups:
        groups[c] = []
        order.append(c)
    groups[c].append(g)
order = [c for c in order if c != "Travel tips"] + (["Travel tips"] if "Travel tips" in groups else [])


def anchor(c):
    return "c-" + "".join(ch for ch in c.lower() if ch.isalnum())


chips = "".join(f'<a href="#{anchor(c)}">{FLAGS.get(c, "")} {html.escape(c)}</a>' for c in order)
sections = ""
for c in order:
    tiles = "".join(
        f'<a class="tile" href="{g["slug"]}.html"><div class="ph" data-photo="{html.escape(META[g["slug"]][2])}"><span>{html.escape(META[g["slug"]][1])}</span></div><b>{html.escape(g["title"])}</b></a>'
        for g in groups[c])
    n = len(groups[c])
    sections += (f'<section class="cs" id="{anchor(c)}"><h2 class="country">{FLAGS.get(c, "")} {html.escape(c)} <small>{n} guide{"s" if n > 1 else ""}</small></h2>'
                 f'<div class="grid">{tiles}</div></section>')
def short(t):
    for sep in (":", " – "):
        if sep in t:
            return t.split(sep)[0]
    return t


board = [g for g in GUIDES if g["slug"] in ("barcelona-first-time", "rome-in-three-days", "lisbon-guide", "istanbul-guide", "dubai-on-a-budget", "bangkok-guide", "paris-first-time", "tenerife-winter-sun")]
rows = "".join(f'<a class="row" href="{g["slug"]}.html"><span class="c">{html.escape(META[g["slug"]][1].split(",")[0])}</span><span class="k">{html.escape(META[g["slug"]][0])}</span>'
               f'<span class="t">{html.escape(short(g["title"]))}</span><span class="go">Read</span></a>' for g in board)
page("index.html", "Tripwise Guides – practical, budget-friendly travel guides",
     "Honest, practical travel guides by country: the Baltics, Finland and Europe's favourite cities, plus tips on cheap flights, eSIMs and flight compensation.",
     '<section class="board"><div class="wrap"><h1>Where are you going next?</h1><p class="sub">Practical guides to cities in Europe and beyond, written to help you spend less on flights, stays and getting around.</p>'
     '<input id="q" class="search" type="search" placeholder="Search a city or country" aria-label="Search guides">'
     f'<div class="rows"><div class="hd"><span>Destination</span><span class="k">Country</span><span class="t">Guide</span><span></span></div>{rows}</div></div></section>'
     + f'<div class="wrap"><div class="chips">{chips}</div>{sections}' + CTA + '</div>',
     '<meta name="fo-verify" content="ecc3db6a-d085-46d5-a6d7-9ad485111ee6" /><meta name="mitgo-verification" content="cc5d1230-0bb6-43c0-bda7-3593e30d9a80" />')

page("about.html", "About Tripwise", "About Tripwise: a free travel assistant in Telegram and independent travel guides.",
     f"""<div class="page"><h1>About Tripwise</h1>
<p>Tripwise helps travellers plan good-value trips. We publish practical travel guides and run a free travel assistant in Telegram, <a href="{BOT}">@tripwise_hub_bot</a>, that answers questions in any language – including voice messages – and suggests areas to stay, tours, transport and money-saving tips.</p>
<p>The <a href="{A}">Tripwise web app</a> lets you search flights in many currencies, find weekend destinations that fit your budget with the budget wheel, and get price-drop alerts for a chosen route.</p>
<h2>Our principles</h2>
<ul><li>Useful first: every guide should help you make a real decision.</li><li>No invented prices or fake reviews – we tell you to check current prices with the provider.</li><li>Clear disclosure of affiliate links.</li></ul>
<h2>Contact</h2><p>Questions, corrections or partnership requests: <a href="mailto:tripwise.hub@gmail.com">tripwise.hub@gmail.com</a>.</p></div>""")

page("disclosure.html", "Affiliate disclosure | Tripwise", "How Tripwise earns money: affiliate links explained.",
     f"""<div class="page"><h1>Affiliate disclosure</h1>
<p>Tripwise is free to use. Some links in our guides, the Telegram bot and the web app are affiliate links. When you book a flight, tour, transfer, car rental, eSIM or other service through such a link, the provider may pay us a commission.</p>
<p><b>You never pay more</b> because you used our link. Commissions do not change which options we recommend: our suggestions are based on usefulness and value for travellers.</p>
<p>We work with partner networks such as Travelpayouts and with providers including Aviasales, Tiqets, WeGoTrip, Kiwitaxi, Localrent, Airalo and AirHelp.</p>
<p>Questions? Write to <a href="mailto:tripwise.hub@gmail.com">tripwise.hub@gmail.com</a>.</p></div>""")

page("privacy.html", "Privacy policy | Tripwise", "Tripwise privacy policy.",
     """<div class="page"><h1>Privacy policy</h1><p>Last updated: October 2026.</p>
<h2>Website and web app</h2><p>These guides do not use advertising cookies or user accounts. The web app stores your settings (language, currency, departure city) only in your own browser. Partner websites you open through our links have their own privacy policies and may use cookies to track bookings.</p>
<h2>Telegram bot</h2><p>When you message @tripwise_hub_bot, we process your messages to answer them, using an AI service. We store your Telegram chat ID and, if you turn on a price alert, the route and dates you chose, so that we can send you updates. Send /stopalerts to remove your alerts. We do not sell personal data.</p>
<h2>Contact</h2><p>To ask about or delete your data, write to <a href="mailto:tripwise.hub@gmail.com">tripwise.hub@gmail.com</a>.</p></div>""")

urls = [BASE] + [BASE + p for p in ["about.html", "disclosure.html", "privacy.html"]] + [BASE + g["slug"] + ".html" for g in GUIDES]
with open(os.path.join(OUT, "sitemap.xml"), "w") as f:
    f.write('<?xml version="1.0" encoding="UTF-8"?>' + NL + '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + NL +
            "".join(f"<url><loc>{u}</loc><lastmod>2026-10-28</lastmod></url>" + NL + "" for u in urls) + "</urlset>" + NL + "")
items = "".join(f"<item><title>{html.escape(g['title'])}</title><link>{BASE}{g['slug']}.html</link><guid>{BASE}{g['slug']}.html</guid><description>{html.escape(g['desc'])}</description></item>" for g in GUIDES)
with open(os.path.join(OUT, "feed.xml"), "w", encoding="utf-8") as f:
    f.write(f'<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel><title>Tripwise Guides</title><link>{BASE}</link><description>Practical, budget-friendly travel guides</description>{items}</channel></rss>')
print(sorted(os.listdir(OUT)))
