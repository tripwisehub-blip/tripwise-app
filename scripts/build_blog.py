import os, sys, html, json, datetime, urllib.request, urllib.parse
sys.path.insert(0, os.path.dirname(__file__))
from blog_content import GUIDES, A, BOT, L


def tp(url, sub, trs=589578):
    """Wrap an Aviasales URL in a tracked Travelpayouts redirect (clicks show up in the TP report)."""
    return "https://tp.media/r?campaign_id=100&p=4114&trs=%d&marker=793212.%s&u=%s" % (trs, sub, urllib.parse.quote(url, safe=""))

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
.kiwi{background:#EAF6F4;border-radius:10px;padding:12px 14px;margin:0 0 14px}
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
    "weekend-trips-from-tallinn": ("Travel tips", "Weekend trips", "Kraków Old Town"),
    "tallinn-to-stockholm": ("Sweden", "Tallinn – Stockholm", "Gamla stan"),
    "december-trips-from-the-baltics": ("Travel tips", "December trips", "Tenerife"),
    "tokyo-on-a-budget": ("Japan", "Tokyo", "Sensō-ji"),
    "singapore-stopover": ("Singapore", "Singapore", "Gardens by the Bay"),
    "seoul-first-time": ("South Korea", "Seoul", "Gyeongbokgung"),
    "marrakech-guide": ("Morocco", "Marrakech", "Jemaa el-Fnaa"),
    "how-to-find-cheap-flights": ("Travel tips", "Cheap flights", "Airliner"),
    "esim-for-travel": ("Travel tips", "eSIM", "SIM card"),
    "flight-delay-compensation": ("Travel tips", "Flight delays", "Frankfurt Airport"),
}
FLAGS = {"Estonia": "🇪🇪", "Finland": "🇫🇮", "Latvia": "🇱🇻", "Lithuania": "🇱🇹", "Baltic States": "🧭", "Czechia": "🇨🇿", "Spain": "🇪🇸",
         "Italy": "🇮🇹", "Portugal": "🇵🇹", "Türkiye": "🇹🇷", "United Arab Emirates": "🇦🇪", "Thailand": "🇹🇭", "Egypt": "🇪🇬", "Hungary": "🇭🇺", "Poland": "🇵🇱", "France": "🇫🇷", "Austria": "🇦🇹", "Netherlands": "🇳🇱", "United Kingdom": "🇬🇧", "Indonesia": "🇮🇩", "Sweden": "🇸🇪", "Travel tips": "💡"}

PHOTO_JS = """<script>
(function(){var cache={};
function load(t,w){var k=t+w;if(cache[k])return cache[k];cache[k]=fetch('https://en.wikipedia.org/api/rest_v1/page/summary/'+encodeURIComponent(t.replace(/ /g,'_'))).then(function(r){return r.ok?r.json():{}}).then(function(j){var s=(j.thumbnail&&j.thumbnail.source)||'';if(!s)return '';var p=s.split('px-');return p.length>1?p[0].slice(0,p[0].lastIndexOf('/')+1)+w+'px-'+p.slice(1).join('px-')+'"),url("'+s:s;}).catch(function(){return ''});return cache[k];}
document.querySelectorAll('[data-photo]').forEach(function(el){var big=el.classList.contains('hero');load(el.getAttribute('data-photo'),big?1280:500).then(function(u){if(u)el.style.backgroundImage=(big?'linear-gradient(rgba(11,35,64,.1),rgba(11,35,64,.78))':'linear-gradient(transparent 50%,rgba(0,0,0,.6))')+',url("'+u+'")';});});
var q=document.getElementById('q');if(q)q.addEventListener('input',function(){var v=q.value.toLowerCase().trim();document.querySelectorAll('.tile,.row').forEach(function(t){t.style.display=!v||t.textContent.toLowerCase().indexOf(v)>=0?'':'none';});document.querySelectorAll('section.cs').forEach(function(sc){var any=[].some.call(sc.querySelectorAll('.tile'),function(t){return t.style.display!=='none'});sc.style.display=any?'':'none';});});
if(!window.matchMedia('(prefers-reduced-motion: reduce)').matches){var A='ABCDEFGHIJKLMNOPRSTUVWZ';document.querySelectorAll('.rows:not(.deals) .row .c').forEach(function(el,i){var f=el.textContent,n=0,id=setInterval(function(){n++;var k=Math.floor(n/2)-i;el.textContent=f.split('').map(function(ch,j){return j<k||ch===' '?ch:A[Math.floor(Math.random()*A.length)]}).join('');if(k>=f.length){clearInterval(id);el.textContent=f;}},45);});}
})();
</script>"""


OG = {}


def og_img(title):
    """Large Wikipedia photo for social previews (og:image); empty on any error."""
    try:
        req = urllib.request.Request("https://en.wikipedia.org/api/rest_v1/page/summary/" + urllib.parse.quote(title.replace(" ", "_")),
                                     headers={"User-Agent": "TripwiseBlog/1.0 (https://t.me/tripwise_deals)"})
        with urllib.request.urlopen(req, timeout=15) as r:
            src = (json.load(r).get("thumbnail") or {}).get("source", "")
        if "px-" in src:
            head, _, tail = src.partition("px-")
            src = head[:head.rfind("/") + 1] + "1280px-" + tail
        return src.split("?")[0]
    except Exception:
        return ""


def ogmeta(name):
    u = OG.get(name, "")
    return (f'<meta property="og:image" content="{html.escape(u)}"><meta name="twitter:card" content="summary_large_image">') if u else ""


def page(name, title, desc, body, extra_head="", lang="en"):
    doc = f"""<!doctype html><html lang="{lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)}</title><meta name="description" content="{html.escape(desc)}">
<link rel="canonical" href="{BASE}{'' if name == 'index.html' else name}">
<meta property="og:title" content="{html.escape(title)}"><meta property="og:description" content="{html.escape(desc)}"><meta property="og:type" content="article"><meta property="og:url" content="{BASE}{'' if name == 'index.html' else name}"><meta property="og:site_name" content="Tripwise Guides">{ogmeta(name)}
<link rel="alternate" type="application/rss+xml" title="Tripwise Guides" href="{BASE}feed.xml">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,400..800&family=Source+Serif+4:opsz,wght@8..60,400;8..60,600&display=swap" rel="stylesheet">
{extra_head}<style>{CSS}</style></head><body>
<header class="top"><div class="wrap"><a class="logo" href="index.html">Trip<i>wise</i></a><nav><a href="index.html">Guides</a><a class="hide-s" href="https://t.me/tripwise_deals">Deals channel</a><a class="hide-s" href="about.html">About</a><a class="tg" href="{BOT}">Telegram bot</a></nav></div></header>
<main>{body}</main>
<footer><div class="wrap"><p>Independent travel guides by Tripwise, 2026.</p><a href="about.html">About</a><a href="disclosure.html">Affiliate disclosure</a><a href="privacy.html">Privacy</a><a href="mailto:tripwise.hub@gmail.com">Contact</a></div></footer>
{PHOTO_JS}</body></html>"""
    path = os.path.join(OUT, name)
    try:
        if open(path, encoding="utf-8").read() == doc:
            return
    except Exception:
        pass
    with open(path, "w", encoding="utf-8") as f:
        f.write(doc)


# Live deal pages: cheapest return flights from each origin city, rebuilt with every price update.
# Every city gets an English page, a Russian page and a page in the local language (better local search reach).
DEAL_CITIES = [("TLL", "Tallinn"), ("RIX", "Riga"), ("HEL", "Helsinki"), ("VNO", "Vilnius"), ("STO", "Stockholm"),
               ("WAW", "Warsaw"), ("BER", "Berlin"), ("LON", "London"), ("PAR", "Paris"), ("AMS", "Amsterdam")]
PRICES_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "prices.json")
RU_FROM = {"TLL": ("Таллинна", "tallinna"), "RIX": ("Риги", "rigi"), "HEL": ("Хельсинки", "helsinki"), "VNO": ("Вильнюса", "vilnyusa"),
           "STO": ("Стокгольма", "stokgolma"), "WAW": ("Варшавы", "varshavy"), "BER": ("Берлина", "berlina"), "LON": ("Лондона", "londona"),
           "PAR": ("Парижа", "parizha"), "AMS": ("Амстердама", "amsterdama")}
LOCAL = {"TLL": ("et", "Odavad lennupiletid Tallinnast", "odavad-lennupiletid-tallinnast.html"),
         "RIX": ("lv", "Lēti lidojumi no Rīgas", "leti-lidojumi-no-rigas.html"),
         "HEL": ("fi", "Halvat lennot Helsingistä", "halvat-lennot-helsingista.html"),
         "VNO": ("lt", "Pigūs skrydžiai iš Vilniaus", "pigus-skrydziai-is-vilniaus.html"),
         "STO": ("sv", "Billiga flyg från Stockholm", "billiga-flyg-fran-stockholm.html"),
         "WAW": ("pl", "Tanie loty z Warszawy", "tanie-loty-z-warszawy.html"),
         "BER": ("de", "Billigflüge ab Berlin", "billigfluege-ab-berlin.html"),
         "PAR": ("fr", "Vols pas chers au départ de Paris", "vols-pas-chers-depuis-paris.html"),
         "AMS": ("nl", "Goedkope vluchten vanaf Amsterdam", "goedkope-vluchten-vanaf-amsterdam.html")}
# sub, Destination, Flight, Dates, Price, Direct, With stops, return, note, tip, channel line, other cities
TXT = {
    "en": ("The cheapest return flights we found recently, sorted by price. Updated several times a day.", "Destination", "Flight", "Dates", "Price",
           "Direct", "With stops", "return", "Prices are per person for a return economy ticket, found on Aviasales recently. Fares change quickly, so check the final price before booking. Updated",
           "Be flexible with dates – moving a trip by a day or two often saves more than any discount code. The lowest fares sell out first, and the cheapest often include only a small bag.",
           "Get the 3 best deals from a different city every day in our Telegram channel", "Flights from other cities"),
    "ru": ("Самые дешёвые билеты туда-обратно, которые мы нашли за последние дни. Отсортировано по цене, обновляется несколько раз в день.", "Куда", "Рейс", "Даты", "Цена",
           "Прямой", "С пересадкой", "туда-обратно", "Цена за одного человека, билет туда-обратно, эконом, найдено на Aviasales. Цены быстро меняются — проверяйте итоговую цену перед покупкой. Обновлено",
           "Будьте гибки с датами: сдвиг на день-два часто экономит больше любого промокода. Самые дешёвые билеты раскупают первыми, и в них обычно входит только ручная кладь.",
           "Каждый день 3 лучших предложения из разных городов — в нашем Telegram-канале", "Билеты из других городов"),
    "et": ("Odavaimad edasi-tagasi lennud, mis viimastel päevadel leidsime, hinna järgi sorteeritud. Uuendatakse mitu korda päevas.", "Sihtkoht", "Lend", "Kuupäevad", "Hind",
           "Otselend", "Ümberistumisega", "edasi-tagasi", "Hind ühe inimese kohta, edasi-tagasi turistiklassis, leitud Aviasalesist. Hinnad muutuvad kiiresti, kontrolli lõpphinda enne ostu. Uuendatud",
           "Ole kuupäevadega paindlik – päeva-kahe võrra nihutamine säästab sageli rohkem kui sooduskood. Odavaimad piletid müüakse esimesena läbi ja neis on tavaliselt ainult käsipagas.",
           "Iga päev 3 parimat pakkumist meie Telegrami kanalis", "Lennud teistest linnadest"),
    "lv": ("Lētākie lidojumi turp un atpakaļ, ko atradām pēdējās dienās, sakārtoti pēc cenas. Atjaunots vairākas reizes dienā.", "Galamērķis", "Lidojums", "Datumi", "Cena",
           "Tiešais", "Ar pārsēšanos", "turp un atpakaļ", "Cena vienai personai par biļeti turp un atpakaļ ekonomiskajā klasē, atrasta Aviasales. Cenas strauji mainās, pirms pirkuma pārbaudiet gala cenu. Atjaunots",
           "Esiet elastīgi ar datumiem – pārcelšana par dienu vai divām bieži ietaupa vairāk nekā atlaides kods. Lētākās biļetes izpērk pirmās, un tajās parasti ir tikai rokas bagāža.",
           "Katru dienu 3 labākie piedāvājumi mūsu Telegram kanālā", "Lidojumi no citām pilsētām"),
    "lt": ("Pigiausi skrydžiai pirmyn ir atgal, kuriuos radome per pastarąsias dienas, surūšiuoti pagal kainą. Atnaujinama kelis kartus per dieną.", "Kryptis", "Skrydis", "Datos", "Kaina",
           "Tiesioginis", "Su persėdimu", "pirmyn ir atgal", "Kaina vienam asmeniui už bilietą pirmyn ir atgal ekonomine klase, rasta Aviasales. Kainos greitai keičiasi, prieš pirkdami patikrinkite galutinę kainą. Atnaujinta",
           "Būkite lankstūs su datomis – kelionės perkėlimas diena ar dviem dažnai sutaupo daugiau nei nuolaidos kodas. Pigiausi bilietai išperkami pirmiausia, juose dažniausiai tik rankinis bagažas.",
           "Kasdien 3 geriausi pasiūlymai mūsų Telegram kanale", "Skrydžiai iš kitų miestų"),
    "fi": ("Halvimmat meno-paluulennot, jotka löysimme viime päivinä, hinnan mukaan järjestettynä. Päivittyy useita kertoja päivässä.", "Kohde", "Lento", "Päivät", "Hinta",
           "Suora", "Vaihdollinen", "meno-paluu", "Hinta per henkilö meno-paluulipusta turistiluokassa, löydetty Aviasalesista. Hinnat muuttuvat nopeasti, tarkista lopullinen hinta ennen ostoa. Päivitetty",
           "Ole joustava päivien kanssa – matkan siirtäminen päivällä tai kahdella säästää usein enemmän kuin alennuskoodi. Halvimmat liput myydään ensin loppuun, ja niihin kuuluu yleensä vain käsimatkatavara.",
           "Joka päivä 3 parasta tarjousta Telegram-kanavallamme", "Lennot muista kaupungeista"),
    "sv": ("De billigaste tur och retur-flygen vi hittat de senaste dagarna, sorterade efter pris. Uppdateras flera gånger om dagen.", "Resmål", "Flyg", "Datum", "Pris",
           "Direkt", "Med byte", "tur och retur", "Pris per person för en tur och retur-biljett i ekonomiklass, hittat på Aviasales. Priserna ändras snabbt, kontrollera slutpriset innan du bokar. Uppdaterat",
           "Var flexibel med datum – att flytta resan en dag eller två sparar ofta mer än en rabattkod. De billigaste biljetterna tar slut först och har oftast bara handbagage.",
           "Varje dag de 3 bästa erbjudandena i vår Telegram-kanal", "Flyg från andra städer"),
    "pl": ("Najtańsze loty w obie strony, które znaleźliśmy w ostatnich dniach, posortowane według ceny. Aktualizowane kilka razy dziennie.", "Kierunek", "Lot", "Daty", "Cena",
           "Bezpośredni", "Z przesiadką", "w obie strony", "Cena za osobę za bilet w obie strony w klasie ekonomicznej, znaleziona na Aviasales. Ceny szybko się zmieniają, sprawdź cenę końcową przed zakupem. Aktualizacja",
           "Bądź elastyczny z datami – przesunięcie podróży o dzień lub dwa często daje więcej niż kod rabatowy. Najtańsze bilety wyprzedają się najszybciej i zwykle obejmują tylko bagaż podręczny.",
           "Codziennie 3 najlepsze oferty na naszym kanale Telegram", "Loty z innych miast"),
    "de": ("Die günstigsten Hin- und Rückflüge, die wir in den letzten Tagen gefunden haben, nach Preis sortiert. Mehrmals täglich aktualisiert.", "Ziel", "Flug", "Daten", "Preis",
           "Direkt", "Mit Umstieg", "hin und zurück", "Preis pro Person für ein Hin- und Rückflugticket in der Economy, gefunden bei Aviasales. Preise ändern sich schnell, prüfe den Endpreis vor der Buchung. Aktualisiert",
           "Sei flexibel bei den Daten – ein oder zwei Tage Verschiebung sparen oft mehr als jeder Rabattcode. Die günstigsten Tarife sind zuerst weg und enthalten meist nur Handgepäck.",
           "Jeden Tag die 3 besten Angebote in unserem Telegram-Kanal", "Flüge aus anderen Städten"),
    "fr": ("Les vols aller-retour les moins chers trouvés ces derniers jours, triés par prix. Mis à jour plusieurs fois par jour.", "Destination", "Vol", "Dates", "Prix",
           "Direct", "Avec escale", "aller-retour", "Prix par personne pour un billet aller-retour en classe économique, trouvé sur Aviasales. Les prix changent vite, vérifiez le prix final avant de réserver. Mis à jour",
           "Soyez flexible sur les dates : décaler le voyage d'un ou deux jours fait souvent économiser plus qu'un code promo. Les tarifs les plus bas partent en premier et n'incluent souvent qu'un bagage cabine.",
           "Chaque jour les 3 meilleures offres sur notre chaîne Telegram", "Vols depuis d'autres villes"),
    "nl": ("De goedkoopste retourvluchten die we de afgelopen dagen vonden, gesorteerd op prijs. Meerdere keren per dag bijgewerkt.", "Bestemming", "Vlucht", "Data", "Prijs",
           "Direct", "Met overstap", "retour", "Prijs per persoon voor een retourticket in economy, gevonden op Aviasales. Prijzen veranderen snel, controleer de eindprijs voor je boekt. Bijgewerkt",
           "Wees flexibel met data – een dag of twee schuiven bespaart vaak meer dan een kortingscode. De goedkoopste tickets zijn het eerst weg en hebben meestal alleen handbagage.",
           "Elke dag de 3 beste deals in ons Telegram-kanaal", "Vluchten vanuit andere steden"),
}


def deal_slug(city):
    return "cheap-flights-from-" + city.lower() + ".html"


def flag_emoji(iso):
    iso = (iso or "").upper()
    return "".join(chr(0x1F1E6 + ord(c) - 65) for c in iso) if len(iso) == 2 and iso.isalpha() else ""


def deal_versions(code, city):
    """(lang, h1 title, file name) for every language version of one city's deal page."""
    out = [("en", "Cheap flights from " + city, deal_slug(city)),
           ("ru", "Дешёвые авиабилеты из " + RU_FROM[code][0], "deshevye-aviabilety-iz-" + RU_FROM[code][1] + ".html")]
    if code in LOCAL:
        out.append(LOCAL[code])
    return out


def deal_pages():
    try:
        prices = json.load(open(PRICES_FILE, encoding="utf-8"))
    except Exception:
        return []
    names = prices.get("names") or {}
    today = datetime.date.today().isoformat()
    made = []
    for code, city in DEAL_CITIES:
        best = {}
        for t in (prices.get("origins") or {}).get(code, []):
            if t.get("dep", "") <= today:
                continue
            if t["d"] not in best or t["p"] < best[t["d"]]["p"]:
                best[t["d"]] = t
        deals = sorted(best.values(), key=lambda t: t["p"])[:15]
        if not deals:
            continue
        versions = deal_versions(code, city)
        alt = "".join(f'<link rel="alternate" hreflang="{lg}" href="{BASE}{fn}">' for lg, _, fn in versions)
        for lang, h1, fname in versions:
            T = TXT[lang]
            rows = ""
            for t in deals:
                n = names.get(t["d"]) or [t["d"], ""]
                path = t.get("link") or "/search/%s%s%s%s%s%s1" % (code, t["dep"][8:10], t["dep"][5:7], t["d"], t["ret"][8:10], t["ret"][5:7])
                url = tp("https://www.aviasales.com" + path, "blog")
                x1, x2 = datetime.date.fromisoformat(t["dep"]), datetime.date.fromisoformat(t["ret"])
                dates = (x1.strftime("%d %b") + " – " + x2.strftime("%d %b")) if lang == "en" else (x1.strftime("%d.%m") + " – " + x2.strftime("%d.%m"))
                kind = T[5] if not t.get("tr") else T[6]
                label = (flag_emoji(n[1] if len(n) > 1 else "") + " " + (n[0] or t["d"])).strip()
                rows += (f'<a class="row" href="{html.escape(url)}" rel="sponsored noopener" target="_blank"><span class="c">{html.escape(label)}</span>'
                         f'<span class="k">{kind}</span><span class="t">{dates} · {T[7]}</span><span class="go">€{round(t["p"])}</span></a>')
            others = " · ".join(f'<a href="{deal_versions(k, n)[1 if lang == "ru" else 0][2]}">{html.escape(RU_FROM[k][0] if lang == "ru" else n)}</a>' for k, n in DEAL_CITIES if k != code)
            langs = " · ".join(f'<a href="{fn}">{lg.upper()}</a>' for lg, _, fn in versions if fn != fname)
            body = (f'<section class="board"><div class="wrap"><h1>{html.escape(h1)}</h1><p class="sub">{html.escape(T[0])}</p>'
                    f'<div class="rows deals"><div class="hd"><span>{T[1]}</span><span class="k">{T[2]}</span><span class="t">{T[3]}</span><span>{T[4]}</span></div>{rows}</div></div></section>'
                    f'<div class="wrap"><div class="page"><p class="meta">{html.escape(T[8])} {today}. {langs}</p><p>{html.escape(T[9])}</p>'
                    f'<p>{html.escape(T[10])}: <a href="https://t.me/tripwise_deals">@tripwise_deals</a> · <a href="{A}">Tripwise app</a></p>'
                    f'<h2>{html.escape(T[11])}</h2><p>{others}</p>' + CTA + '</div></div>')
            page(fname, h1 + " | Tripwise", h1 + ": " + T[0], body, alt, lang)
            made.append((code, city, lang, fname))
    return made


DEAL_ALL = deal_pages()
DEAL_MADE = [c for k, c, lg, fn in DEAL_ALL if lg == "en"]
DEALS_BLOCK = ('<section class="cs"><h2 class="country">✈️ Cheap flights from your city</h2><div class="chips">'
               + "".join(f'<a href="{fn}">{html.escape(c if lg == "en" else lg.upper() + " · " + c)}</a>' for k, c, lg, fn in DEAL_ALL) + '</div></section>') if DEAL_ALL else ""

# Route pages: one page per origin -> destination pair and language ("Cheap flights from Tallinn to Barcelona").
# Every route gets English, Russian and the language of the departure city. A registry (routes.json in the blog folder)
# keeps routes we have seen, so pages stay online with the last known fare even when today's feed has no data for them.
RT = {
    "en": dict(h1="Cheap flights from {o} to {d}", intro="Return flights from {o} to {d} from €{p}. The cheapest dates we found recently – tap a date to see the live fare and book. Updated several times a day.",
               intro0="Return flights from {o} to {d} with live prices. Updated several times a day.", cols=("Departure", "Flight", "Return", "Price"),
               direct="Direct", stops="With stops", back="back", nights="nights", note="Prices are per person, return, economy, found recently on Aviasales and may change. Updated",
               tipsh="Tips for cheap {o} – {d} flights", tips=("Midweek departures (Tuesday–Thursday) are usually cheaper than Fridays and Sundays.", "The lowest fares usually include only a small cabin bag – add luggage before comparing.", "Check {month}: moving the trip by a day or two often saves more than any discount code."),
               month="the whole month", chan="Best deals every day in our Telegram channel", more_o="More cheap flights from {o}", more_d="Flights to {d} from other cities",
               guide="Planning what to do there? Read our guide", any="Any dates", nof="No fresh fares right now – check live prices", srch="Search", all="All routes"),
    "ru": dict(h1="Дешёвые авиабилеты {o} — {d}", intro="Билеты туда-обратно {o} — {d} от €{p}. Самые дешёвые даты, которые мы нашли за последние дни, — нажмите на дату, чтобы увидеть актуальную цену. Обновляется несколько раз в день.",
               intro0="Билеты туда-обратно {o} — {d} с актуальными ценами. Обновляется несколько раз в день.", cols=("Туда", "Рейс", "Обратно", "Цена"),
               direct="Прямой", stops="С пересадкой", back="обратно", nights="ноч.", note="Цена за одного человека, туда-обратно, эконом, найдено на Aviasales, может измениться. Обновлено",
               tipsh="Как купить дешёвый билет {o} — {d}", tips=("Вылеты в середине недели (вт–чт) обычно дешевле, чем в пятницу и воскресенье.", "В самых дешёвых тарифах обычно только ручная кладь — учитывайте багаж при сравнении.", "Смотрите {month}: сдвиг поездки на день-два часто экономит больше любого промокода."),
               month="цены на весь месяц", chan="Лучшие предложения каждый день в нашем Telegram-канале", more_o="Ещё дешёвые билеты из города {o}", more_d="Билеты в {d} из других городов",
               guide="Что посмотреть на месте? Наш гид (англ.)", any="Любые даты", nof="Свежих цен сейчас нет — смотрите актуальные", srch="Найти", all="Все маршруты"),
    "et": dict(h1="Odavad lennupiletid {o} – {d}", intro="Edasi-tagasi lennud {o} – {d} alates €{p}. Odavaimad kuupäevad, mis viimati leidsime – vajuta kuupäevale, et näha hetkehinda. Uuendatakse mitu korda päevas.",
               intro0="Edasi-tagasi lennud {o} – {d} hetkehindadega. Uuendatakse mitu korda päevas.", cols=("Minek", "Lend", "Tagasi", "Hind"),
               direct="Otselend", stops="Ümberistumisega", back="tagasi", nights="ööd", note="Hind ühe inimese kohta, edasi-tagasi, turistiklass, leitud Aviasalesist, võib muutuda. Uuendatud",
               tipsh="Nõuanded odavateks lendudeks {o} – {d}", tips=("Nädala keskel (T–N) väljumised on tavaliselt odavamad kui reedel ja pühapäeval.", "Odavaimates piletites on tavaliselt ainult käsipagas.", "Vaata {month}: päeva-kahe võrra nihutamine säästab sageli kõige rohkem."),
               month="kogu kuu hindu", chan="Parimad pakkumised iga päev meie Telegrami kanalis", more_o="Veel odavaid lende: {o}", more_d="Lennud sihtkohta {d} teistest linnadest",
               guide="Mida seal teha? Meie juhend (inglise k.)", any="Kõik kuupäevad", nof="Värskeid hindu praegu pole – vaata hetkehindu", srch="Otsi", all="Kõik marsruudid"),
    "lv": dict(h1="Lēti lidojumi {o} – {d}", intro="Lidojumi turp un atpakaļ {o} – {d} no €{p}. Lētākie datumi, ko nesen atradām – nospiediet datumu, lai redzētu aktuālo cenu. Atjaunots vairākas reizes dienā.",
               intro0="Lidojumi turp un atpakaļ {o} – {d} ar aktuālām cenām. Atjaunots vairākas reizes dienā.", cols=("Turp", "Lidojums", "Atpakaļ", "Cena"),
               direct="Tiešais", stops="Ar pārsēšanos", back="atpakaļ", nights="naktis", note="Cena vienai personai, turp un atpakaļ, ekonomiskā klase, atrasta Aviasales, var mainīties. Atjaunots",
               tipsh="Padomi lētiem lidojumiem {o} – {d}", tips=("Izlidošana nedēļas vidū (O–C) parasti ir lētāka nekā piektdienās un svētdienās.", "Lētākajās biļetēs parasti ir tikai rokas bagāža.", "Skatiet {month}: pārcelšana par dienu vai divām bieži ietaupa visvairāk."),
               month="visa mēneša cenas", chan="Labākie piedāvājumi katru dienu mūsu Telegram kanālā", more_o="Vēl lēti lidojumi: {o}", more_d="Lidojumi uz {d} no citām pilsētām",
               guide="Ko tur darīt? Mūsu ceļvedis (angļu val.)", any="Jebkuri datumi", nof="Pašlaik nav svaigu cenu – skatiet aktuālās", srch="Meklēt", all="Visi maršruti"),
    "lt": dict(h1="Pigūs skrydžiai {o} – {d}", intro="Skrydžiai pirmyn ir atgal {o} – {d} nuo €{p}. Pigiausios neseniai rastos datos – spustelėkite datą ir pamatysite dabartinę kainą. Atnaujinama kelis kartus per dieną.",
               intro0="Skrydžiai pirmyn ir atgal {o} – {d} su dabartinėmis kainomis. Atnaujinama kelis kartus per dieną.", cols=("Išvykimas", "Skrydis", "Grįžimas", "Kaina"),
               direct="Tiesioginis", stops="Su persėdimu", back="atgal", nights="naktys", note="Kaina vienam asmeniui, pirmyn ir atgal, ekonominė klasė, rasta Aviasales, gali keistis. Atnaujinta",
               tipsh="Patarimai pigiems skrydžiams {o} – {d}", tips=("Skrydžiai savaitės viduryje (A–K) dažniausiai pigesni nei penktadienį ir sekmadienį.", "Pigiausiuose bilietuose dažniausiai tik rankinis bagažas.", "Žiūrėkite {month}: kelionės perkėlimas diena ar dviem dažnai sutaupo daugiausia."),
               month="viso mėnesio kainas", chan="Geriausi pasiūlymai kasdien mūsų Telegram kanale", more_o="Daugiau pigių skrydžių: {o}", more_d="Skrydžiai į {d} iš kitų miestų",
               guide="Ką ten veikti? Mūsų gidas (anglų k.)", any="Bet kokios datos", nof="Šiuo metu naujų kainų nėra – žiūrėkite dabartines", srch="Ieškoti", all="Visi maršrutai"),
    "fi": dict(h1="Halvat lennot {o} – {d}", intro="Meno-paluulennot {o} – {d} alkaen €{p}. Halvimmat äskettäin löytämämme päivät – napauta päivää nähdäksesi hinnan. Päivittyy useita kertoja päivässä.",
               intro0="Meno-paluulennot {o} – {d} ajantasaisin hinnoin. Päivittyy useita kertoja päivässä.", cols=("Meno", "Lento", "Paluu", "Hinta"),
               direct="Suora", stops="Vaihdollinen", back="paluu", nights="yötä", note="Hinta per henkilö, meno-paluu, turistiluokka, löydetty Aviasalesista, voi muuttua. Päivitetty",
               tipsh="Vinkit halpoihin lentoihin {o} – {d}", tips=("Keskiviikon lähdöt (ti–to) ovat yleensä halvempia kuin perjantaina ja sunnuntaina.", "Halvimpiin lippuihin kuuluu yleensä vain käsimatkatavara.", "Katso {month}: päivän tai kahden siirto säästää usein eniten."),
               month="koko kuukauden hinnat", chan="Parhaat tarjoukset joka päivä Telegram-kanavallamme", more_o="Lisää halpoja lentoja: {o}", more_d="Lennot kohteeseen {d} muista kaupungeista",
               guide="Mitä siellä tehdä? Oppaamme (englanniksi)", any="Mitkä tahansa päivät", nof="Tuoreita hintoja ei nyt ole – katso ajantasaiset", srch="Hae", all="Kaikki reitit"),
    "sv": dict(h1="Billiga flyg {o} – {d}", intro="Tur och retur {o} – {d} från €{p}. De billigaste datumen vi hittat nyligen – tryck på ett datum för aktuellt pris. Uppdateras flera gånger om dagen.",
               intro0="Tur och retur {o} – {d} med aktuella priser. Uppdateras flera gånger om dagen.", cols=("Utresa", "Flyg", "Hemresa", "Pris"),
               direct="Direkt", stops="Med byte", back="hem", nights="nätter", note="Pris per person, tur och retur, ekonomi, hittat på Aviasales, kan ändras. Uppdaterat",
               tipsh="Tips för billiga flyg {o} – {d}", tips=("Avgångar mitt i veckan (tis–tor) är oftast billigare än fredag och söndag.", "De billigaste biljetterna har oftast bara handbagage.", "Kolla {month}: att flytta resan en dag eller två sparar ofta mest."),
               month="hela månadens priser", chan="Bästa erbjudandena varje dag i vår Telegram-kanal", more_o="Fler billiga flyg från {o}", more_d="Flyg till {d} från andra städer",
               guide="Vad göra där? Vår guide (engelska)", any="Alla datum", nof="Inga färska priser just nu – se aktuella", srch="Sök", all="Alla rutter"),
    "nb": dict(h1="Billige flybilletter {o} – {d}", intro="Tur-retur {o} – {d} fra €{p}. De billigste datoene vi fant nylig – trykk på en dato for aktuell pris. Oppdateres flere ganger om dagen.",
               intro0="Tur-retur {o} – {d} med aktuelle priser. Oppdateres flere ganger om dagen.", cols=("Utreise", "Fly", "Hjemreise", "Pris"),
               direct="Direkte", stops="Med bytte", back="hjem", nights="netter", note="Pris per person, tur-retur, økonomi, funnet på Aviasales, kan endres. Oppdatert",
               tipsh="Tips for billige fly {o} – {d}", tips=("Avganger midt i uka (tir–tor) er ofte billigere enn fredag og søndag.", "De billigste billettene har som regel bare håndbagasje.", "Se {month}: å flytte turen en dag eller to sparer ofte mest."),
               month="hele månedens priser", chan="Beste tilbud hver dag i vår Telegram-kanal", more_o="Flere billige fly fra {o}", more_d="Fly til {d} fra andre byer",
               guide="Hva gjøre der? Vår guide (engelsk)", any="Alle datoer", nof="Ingen ferske priser nå – se aktuelle", srch="Søk", all="Alle ruter"),
    "da": dict(h1="Billige flybilletter {o} – {d}", intro="Returrejser {o} – {d} fra €{p}. De billigste datoer, vi har fundet for nylig – tryk på en dato for aktuel pris. Opdateres flere gange dagligt.",
               intro0="Returrejser {o} – {d} med aktuelle priser. Opdateres flere gange dagligt.", cols=("Udrejse", "Fly", "Hjemrejse", "Pris"),
               direct="Direkte", stops="Med skift", back="hjem", nights="nætter", note="Pris pr. person, retur, økonomi, fundet på Aviasales, kan ændre sig. Opdateret",
               tipsh="Tips til billige fly {o} – {d}", tips=("Afgange midt på ugen (tir–tor) er ofte billigere end fredag og søndag.", "De billigste billetter har som regel kun håndbagage.", "Se {month}: at flytte rejsen en dag eller to sparer ofte mest."),
               month="hele månedens priser", chan="Bedste tilbud hver dag på vores Telegram-kanal", more_o="Flere billige fly fra {o}", more_d="Fly til {d} fra andre byer",
               guide="Hvad skal man lave der? Vores guide (engelsk)", any="Alle datoer", nof="Ingen friske priser lige nu – se aktuelle", srch="Søg", all="Alle ruter"),
    "pl": dict(h1="Tanie loty {o} – {d}", intro="Loty w obie strony {o} – {d} od €{p}. Najtańsze daty znalezione ostatnio – kliknij datę, by zobaczyć aktualną cenę. Aktualizowane kilka razy dziennie.",
               intro0="Loty w obie strony {o} – {d} z aktualnymi cenami. Aktualizowane kilka razy dziennie.", cols=("Wylot", "Lot", "Powrót", "Cena"),
               direct="Bezpośredni", stops="Z przesiadką", back="powrót", nights="noce", note="Cena za osobę, w obie strony, ekonomiczna, znaleziona na Aviasales, może się zmienić. Aktualizacja",
               tipsh="Jak tanio polecieć {o} – {d}", tips=("Wyloty w środku tygodnia (wt–czw) są zwykle tańsze niż w piątek i niedzielę.", "Najtańsze bilety zwykle obejmują tylko bagaż podręczny.", "Sprawdź {month}: przesunięcie podróży o dzień lub dwa często oszczędza najwięcej."),
               month="ceny w całym miesiącu", chan="Najlepsze oferty codziennie na naszym kanale Telegram", more_o="Więcej tanich lotów z {o}", more_d="Loty do {d} z innych miast",
               guide="Co tam robić? Nasz przewodnik (ang.)", any="Dowolne daty", nof="Brak świeżych cen – sprawdź aktualne", srch="Szukaj", all="Wszystkie trasy"),
    "de": dict(h1="Günstige Flüge {o} – {d}", intro="Hin- und Rückflüge {o} – {d} ab €{p}. Die günstigsten Termine, die wir zuletzt gefunden haben – tippe auf ein Datum für den aktuellen Preis. Mehrmals täglich aktualisiert.",
               intro0="Hin- und Rückflüge {o} – {d} mit aktuellen Preisen. Mehrmals täglich aktualisiert.", cols=("Hinflug", "Flug", "Rückflug", "Preis"),
               direct="Direkt", stops="Mit Umstieg", back="zurück", nights="Nächte", note="Preis pro Person, hin und zurück, Economy, gefunden bei Aviasales, kann sich ändern. Aktualisiert",
               tipsh="Tipps für günstige Flüge {o} – {d}", tips=("Abflüge unter der Woche (Di–Do) sind meist günstiger als Freitag und Sonntag.", "Die günstigsten Tarife enthalten meist nur Handgepäck.", "Prüfe {month}: ein oder zwei Tage Verschiebung sparen oft am meisten."),
               month="die Preise im ganzen Monat", chan="Die besten Angebote täglich in unserem Telegram-Kanal", more_o="Weitere günstige Flüge ab {o}", more_d="Flüge nach {d} aus anderen Städten",
               guide="Was dort unternehmen? Unser Guide (Englisch)", any="Beliebige Daten", nof="Gerade keine aktuellen Preise – Live-Preise prüfen", srch="Suchen", all="Alle Strecken"),
    "nl": dict(h1="Goedkope vluchten {o} – {d}", intro="Retourvluchten {o} – {d} vanaf €{p}. De goedkoopste data die we onlangs vonden – tik op een datum voor de actuele prijs. Meerdere keren per dag bijgewerkt.",
               intro0="Retourvluchten {o} – {d} met actuele prijzen. Meerdere keren per dag bijgewerkt.", cols=("Heen", "Vlucht", "Terug", "Prijs"),
               direct="Direct", stops="Met overstap", back="terug", nights="nachten", note="Prijs per persoon, retour, economy, gevonden op Aviasales, kan veranderen. Bijgewerkt",
               tipsh="Tips voor goedkope vluchten {o} – {d}", tips=("Vertrek midden in de week (di–do) is meestal goedkoper dan vrijdag en zondag.", "De goedkoopste tickets hebben meestal alleen handbagage.", "Bekijk {month}: een dag of twee schuiven bespaart vaak het meest."),
               month="de prijzen van de hele maand", chan="Elke dag de beste deals in ons Telegram-kanaal", more_o="Meer goedkope vluchten vanaf {o}", more_d="Vluchten naar {d} vanuit andere steden",
               guide="Wat te doen? Onze gids (Engels)", any="Alle data", nof="Nu geen verse prijzen – bekijk actuele", srch="Zoeken", all="Alle routes"),
    "fr": dict(h1="Vols pas chers {o} – {d}", intro="Vols aller-retour {o} – {d} dès €{p}. Les dates les moins chères trouvées récemment – touchez une date pour voir le prix actuel. Mis à jour plusieurs fois par jour.",
               intro0="Vols aller-retour {o} – {d} avec prix actuels. Mis à jour plusieurs fois par jour.", cols=("Aller", "Vol", "Retour", "Prix"),
               direct="Direct", stops="Avec escale", back="retour", nights="nuits", note="Prix par personne, aller-retour, économie, trouvé sur Aviasales, peut changer. Mis à jour",
               tipsh="Conseils pour des vols pas chers {o} – {d}", tips=("Les départs en milieu de semaine (mar–jeu) sont souvent moins chers que le vendredi et le dimanche.", "Les tarifs les plus bas n'incluent souvent qu'un bagage cabine.", "Consultez {month} : décaler d'un ou deux jours fait souvent économiser le plus."),
               month="les prix du mois entier", chan="Les meilleures offres chaque jour sur notre chaîne Telegram", more_o="Plus de vols pas chers depuis {o}", more_d="Vols vers {d} depuis d'autres villes",
               guide="Que faire sur place ? Notre guide (anglais)", any="Toutes dates", nof="Pas de prix récents – voir les prix actuels", srch="Rechercher", all="Toutes les routes"),
    "cs": dict(h1="Levné letenky {o} – {d}", intro="Zpáteční lety {o} – {d} od €{p}. Nejlevnější termíny, které jsme nedávno našli – klepněte na datum pro aktuální cenu. Aktualizováno několikrát denně.",
               intro0="Zpáteční lety {o} – {d} s aktuálními cenami. Aktualizováno několikrát denně.", cols=("Odlet", "Let", "Návrat", "Cena"),
               direct="Přímý", stops="S přestupem", back="zpět", nights="nocí", note="Cena za osobu, zpáteční, ekonomická třída, nalezeno na Aviasales, může se změnit. Aktualizováno",
               tipsh="Tipy na levné lety {o} – {d}", tips=("Odlety uprostřed týdne (út–čt) bývají levnější než v pátek a v neděli.", "Nejlevnější letenky obvykle zahrnují jen příruční zavazadlo.", "Podívejte se na {month}: posun o den či dva často ušetří nejvíc."),
               month="ceny celého měsíce", chan="Nejlepší nabídky každý den na našem Telegram kanálu", more_o="Další levné lety z {o}", more_d="Lety do {d} z jiných měst",
               guide="Co tam dělat? Náš průvodce (anglicky)", any="Libovolné datum", nof="Teď nejsou čerstvé ceny – podívejte se na aktuální", srch="Hledat", all="Všechny trasy"),
    "es": dict(h1="Vuelos baratos {o} – {d}", intro="Vuelos de ida y vuelta {o} – {d} desde €{p}. Las fechas más baratas que encontramos recientemente: toca una fecha para ver el precio actual. Se actualiza varias veces al día.",
               intro0="Vuelos de ida y vuelta {o} – {d} con precios actuales. Se actualiza varias veces al día.", cols=("Ida", "Vuelo", "Vuelta", "Precio"),
               direct="Directo", stops="Con escala", back="vuelta", nights="noches", note="Precio por persona, ida y vuelta, turista, encontrado en Aviasales, puede cambiar. Actualizado",
               tipsh="Consejos para vuelos baratos {o} – {d}", tips=("Las salidas entre semana (mar–jue) suelen ser más baratas que viernes y domingo.", "Las tarifas más bajas suelen incluir solo equipaje de mano.", "Mira {month}: mover el viaje uno o dos días suele ahorrar más."),
               month="los precios de todo el mes", chan="Las mejores ofertas cada día en nuestro canal de Telegram", more_o="Más vuelos baratos desde {o}", more_d="Vuelos a {d} desde otras ciudades",
               guide="¿Qué hacer allí? Nuestra guía (inglés)", any="Cualquier fecha", nof="No hay precios recientes – mira los actuales", srch="Buscar", all="Todas las rutas"),
    "it": dict(h1="Voli economici {o} – {d}", intro="Voli andata e ritorno {o} – {d} da €{p}. Le date più economiche trovate di recente: tocca una data per il prezzo attuale. Aggiornato più volte al giorno.",
               intro0="Voli andata e ritorno {o} – {d} con prezzi aggiornati. Aggiornato più volte al giorno.", cols=("Andata", "Volo", "Ritorno", "Prezzo"),
               direct="Diretto", stops="Con scalo", back="ritorno", nights="notti", note="Prezzo a persona, andata e ritorno, economy, trovato su Aviasales, può cambiare. Aggiornato",
               tipsh="Consigli per voli economici {o} – {d}", tips=("Le partenze a metà settimana (mar–gio) costano di solito meno di venerdì e domenica.", "Le tariffe più basse includono di solito solo il bagaglio a mano.", "Guarda {month}: spostare il viaggio di un giorno o due spesso fa risparmiare di più."),
               month="i prezzi di tutto il mese", chan="Le migliori offerte ogni giorno sul nostro canale Telegram", more_o="Altri voli economici da {o}", more_d="Voli per {d} da altre città",
               guide="Cosa fare lì? La nostra guida (inglese)", any="Qualsiasi data", nof="Nessun prezzo recente – guarda i prezzi attuali", srch="Cerca", all="Tutte le rotte"),
}
ORIGIN_LANG = {"TLL": "et", "RIX": "lv", "VNO": "lt", "HEL": "fi", "STO": "sv", "OSL": "nb", "CPH": "da", "WAW": "pl", "BER": "de", "MUC": "de",
               "FRA": "de", "VIE": "de", "AMS": "nl", "PAR": "fr", "PRG": "cs", "BCN": "es", "MAD": "es", "ROM": "it", "MIL": "it"}
TP_LANGS = ("ru", "de", "fr", "es", "it", "pl")  # city names in these languages come from the Travelpayouts directory


def slugify(s):
    s = "".join(ch if ch.isalnum() and ch.isascii() else "-" for ch in s.lower().replace("'", ""))
    while "--" in s:
        s = s.replace("--", "-")
    return s.strip("-")


def city_names():
    """{lang: {IATA: name}} cached in the blog folder; filled from the public Travelpayouts directory."""
    path = os.path.join(OUT, "city_names.json")
    try:
        cache = json.load(open(path, encoding="utf-8"))
    except Exception:
        cache = {}
    changed = False
    for lg in TP_LANGS:
        if cache.get(lg):
            continue
        try:
            req = urllib.request.Request("https://api.travelpayouts.com/data/%s/cities.json" % lg, headers={"User-Agent": "TripwiseBot/1.0"})
            with urllib.request.urlopen(req, timeout=60) as r:
                cache[lg] = {c["code"]: c["name"] for c in json.load(r) if c.get("code") and c.get("name")}
            changed = True
        except Exception as e:
            print("city names", lg, e)
    if changed:
        json.dump(cache, open(path, "w", encoding="utf-8"), ensure_ascii=False)
    return cache


# Second flight partner on route pages: Kiwi.com deep links made by scripts/make_links.py (data/kiwi_routes.json)
try:
    KIWI = json.load(open("data/kiwi_routes.json"))
except Exception:
    KIWI = {}
KIWI_TXT = {"en": "Also compare this route on Kiwi.com — it combines low-cost airlines into one trip:",
            "ru": "Сравните этот маршрут и на Kiwi.com — он собирает поездку из рейсов разных лоукостеров:",
            "uk": "Порівняйте цей маршрут і на Kiwi.com — він поєднує рейси різних лоукостерів:",
            "et": "Võrdle seda marsruuti ka Kiwi.com-is — see ühendab odavlennufirmade lende:",
            "fi": "Vertaa reittiä myös Kiwi.comissa — se yhdistää halpalentoyhtiöiden lentoja:",
            "lv": "Salīdziniet šo maršrutu arī Kiwi.com — tas apvieno lētās aviokompanijas:",
            "lt": "Palyginkite šį maršrutą ir Kiwi.com — jis sujungia pigių skrydžių bendroves:",
            "pl": "Porównaj tę trasę także na Kiwi.com — łączy loty tanich linii w jedną podróż:",
            "de": "Vergleiche die Strecke auch auf Kiwi.com — dort werden Billigflüge kombiniert:",
            "fr": "Comparez aussi ce trajet sur Kiwi.com, qui combine les vols low-cost :",
            "es": "Compara también esta ruta en Kiwi.com, que combina vuelos low-cost:",
            "it": "Confronta questa tratta anche su Kiwi.com, che combina voli low cost:",
            "sv": "Jämför även rutten på Kiwi.com — den kombinerar lågprisflyg:",
            "no": "Sammenlign ruten også på Kiwi.com — den kombinerer lavprisfly:",
            "da": "Sammenlign ruten på Kiwi.com — den kombinerer lavprisfly:",
            "nl": "Vergelijk deze route ook op Kiwi.com — het combineert prijsvechters:"}


def route_pages():
    try:
        prices = json.load(open(PRICES_FILE, encoding="utf-8"))
    except Exception:
        return []
    names = prices.get("names") or {}
    today = datetime.date.today().isoformat()
    reg_path = os.path.join(OUT, "routes.json")
    try:
        reg = json.load(open(reg_path, encoding="utf-8"))
    except Exception:
        reg = {}
    city_of = dict(DEAL_CITIES)
    loc = city_names()

    def nm(code, lg="en"):
        n = names.get(code)
        en = n[0] if n and n[0] else city_of.get(code, code)
        return (loc.get(lg) or {}).get(code) or en

    def iso(code):
        n = names.get(code)
        return n[1] if n and len(n) > 1 else ""

    for o, trips in (prices.get("origins") or {}).items():
        for t in trips:
            if t.get("dep", "") <= today:
                continue
            key = o + "-" + t["d"]
            r = reg.setdefault(key, {"fares": [], "low": None})
            fares = [f for f in r["fares"] if f["dep"] > today and not (f["dep"] == t["dep"] and f["ret"] == t["ret"])]
            fares.append({"p": round(t["p"]), "dep": t["dep"], "ret": t["ret"], "tr": t.get("tr", 0), "link": t.get("link", "")})
            r["fares"] = sorted(fares, key=lambda f: f["p"])[:6]
            r["low"] = min([x for x in [r.get("low"), round(t["p"])] if x is not None])
            r["seen"] = today
    for r in reg.values():
        r["fares"] = [f for f in r["fares"] if f["dep"] > today]
    json.dump(reg, open(reg_path, "w", encoding="utf-8"), ensure_ascii=False)

    guide_for = {}
    for g in GUIDES:
        c = META.get(g["slug"], ("", "", ""))[1].split(",")[0].strip().lower()
        if c:
            guide_for.setdefault(c, g)
    by_origin, by_dest = {}, {}
    keys = [k for k in reg if nm(k.split("-")[0]) != nm(k.split("-")[1])]
    for key in keys:
        o, d = key.split("-")
        by_origin.setdefault(o, []).append(key)
        by_dest.setdefault(d, []).append(key)

    def langs(key):
        lg = ORIGIN_LANG.get(key.split("-")[0])
        return ["en", "ru"] + ([lg] if lg and lg not in ("en", "ru") else [])

    def fname(key, lg="en"):
        o, d = key.split("-")
        base = "flights-" + slugify(nm(o)) + "-to-" + slugify(nm(d)) + ".html"
        return base if lg == "en" else lg + "-" + base

    made = []
    for key in keys:
        o, d = key.split("-")
        r = reg[key]
        fares = r["fares"]
        best = fares[0]["p"] if fares else r.get("low")
        search = tp("https://www.aviasales.com/search/%s%s1" % (o, d), "route")
        versions = langs(key)
        alt = "".join(f'<link rel="alternate" hreflang="{lg}" href="{BASE}{fname(key, lg)}">' for lg in versions)
        g = guide_for.get(nm(d).lower())
        for lg in versions:
            T = RT[lg]
            of, dn = nm(o, lg), nm(d, lg)
            rows = ""
            for f in fares:
                path = f.get("link") or "/search/%s%s%s%s%s%s1" % (o, f["dep"][8:10], f["dep"][5:7], d, f["ret"][8:10], f["ret"][5:7])
                url = tp("https://www.aviasales.com" + path, "route")
                x1, x2 = datetime.date.fromisoformat(f["dep"]), datetime.date.fromisoformat(f["ret"])
                rows += (f'<a class="row" href="{html.escape(url)}" rel="sponsored noopener" target="_blank"><span class="c">{x1.strftime("%d.%m.%Y")}</span>'
                         f'<span class="k">{T["direct"] if not f.get("tr") else T["stops"]}</span><span class="t">{T["back"]} {x2.strftime("%d.%m")} · {(x2 - x1).days} {T["nights"]}</span><span class="go">€{f["p"]}</span></a>')
            if not rows:
                rows = (f'<a class="row" href="{search}" rel="sponsored noopener" target="_blank"><span class="c">{T["any"]}</span><span class="k">–</span>'
                        f'<span class="t">{T["nof"]}</span><span class="go">{T["srch"]}</span></a>')
            h1 = (T["h1"].format(o=of, d=dn) + " " + flag_emoji(iso(d))).strip()
            intro = T["intro"].format(o=of, d=dn, p=best) if best else T["intro0"].format(o=of, d=dn)
            same_o = sorted([k for k in by_origin.get(o, []) if k != key and reg[k].get("low")], key=lambda k: reg[k]["low"])[:12]
            same_d = sorted([k for k in by_dest.get(d, []) if k != key and reg[k].get("low")], key=lambda k: reg[k]["low"])[:12]
            more_o = " · ".join(f'<a href="{fname(k, lg if lg in langs(k) else "en")}">{html.escape(nm(k.split("-")[1], lg))} €{reg[k]["low"]}</a>' for k in same_o)
            more_d = " · ".join(f'<a href="{fname(k, lg if lg in langs(k) else "en")}">{html.escape(nm(k.split("-")[0], lg))} €{reg[k]["low"]}</a>' for k in same_d)
            other = " · ".join(f'<a href="{fname(key, x)}">{x.upper()}</a>' for x in versions if x != lg)
            tips = "".join("<li>" + html.escape(t).replace("{month}", f'<a href="{search}" rel="sponsored noopener" target="_blank">{html.escape(T["month"])}</a>') + "</li>" for t in T["tips"])
            kw = KIWI.get(key)
            kiwi = (f'<p class="kiwi">{html.escape(KIWI_TXT.get(lg, KIWI_TXT["en"]))} <a href="{html.escape(kw)}" rel="sponsored noopener" target="_blank">Kiwi.com →</a></p>' if kw else "")
            body = (f'<section class="board"><div class="wrap"><h1>{html.escape(h1)}</h1><p class="sub">{html.escape(intro)}</p>'
                    f'<div class="rows deals"><div class="hd">' + "".join(f'<span{c}>{x}</span>' for x, c in zip(T["cols"], ("", ' class="k"', ' class="t"', ""))) + f'</div>{rows}</div></div></section>'
                    f'<div class="wrap"><div class="page">{kiwi}<p class="meta">{html.escape(T["note"])} {r.get("seen", today)}. {other} · <a href="flight-routes.html">{T["all"]}</a></p>'
                    f'<h2>{html.escape(T["tipsh"].format(o=of, d=dn))}</h2><ul>{tips}<li>{html.escape(T["chan"])}: <a href="https://t.me/tripwise_deals">@tripwise_deals</a></li></ul>'
                    + (f'<p>{html.escape(T["guide"])}: <a href="{g["slug"]}.html">{html.escape(g["title"])}</a>.</p>' if g else "")
                    + (f'<h2>{html.escape(T["more_o"].format(o=of))}</h2><p>{more_o}</p>' if more_o else "")
                    + (f'<h2>{html.escape(T["more_d"].format(d=dn))}</h2><p>{more_d}</p>' if more_d else "")
                    + CTA + '</div></div>')
            ld = json.dumps({"@context": "https://schema.org", "@type": "Product", "name": f"{of} – {dn}",
                             "offers": {"@type": "AggregateOffer", "priceCurrency": "EUR", "lowPrice": best, "offerCount": max(len(fares), 1)}}, ensure_ascii=False) if best else ""
            title = T["h1"].format(o=of, d=dn) + (f" · €{best}" if best else "") + " | Tripwise"
            page(fname(key, lg), title, intro, body, alt + (f'<script type="application/ld+json">{ld}</script>' if ld else ""), lg)
            made.append(fname(key, lg))
    groups = ""
    for o in sorted(by_origin, key=lambda c: nm(c)):
        ks = sorted([k for k in by_origin[o] if reg[k].get("low")], key=lambda k: reg[k]["low"])
        if ks:
            groups += f'<h2>From {html.escape(nm(o))}</h2><p>' + " · ".join(f'<a href="{fname(k)}">{html.escape(nm(k.split("-")[1]))} €{reg[k]["low"]}</a>' for k in ks) + "</p>"
    page("flight-routes.html", "Cheap flight routes from 20 European cities | Tripwise",
         "All cheap flight routes we track: lowest return fares from Tallinn, Riga, Vilnius, Helsinki, Stockholm, London, Berlin, Paris and more.",
         f'<div class="wrap"><div class="page"><h1>Cheap flight routes</h1><p>The lowest return fares we have seen on each route, in English, Russian and the language of the departure city. Prices update several times a day.</p>{groups}</div></div>')
    return made + ["flight-routes.html"]


ROUTES = route_pages()
DEALS_BLOCK += ('<section class="cs"><h2 class="country">🗺 All flight routes</h2><div class="chips"><a href="flight-routes.html">'
                f'Browse {len([r for r in ROUTES if r.startswith("flights-")])} routes with prices</a></div></section>') if ROUTES else ""

OG["index.html"] = og_img("Barcelona")
for g in GUIDES:
    OG[g["slug"] + ".html"] = og_img(META.get(g["slug"], ("", "", g["tag"]))[2])
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
     + f'<div class="wrap"><div class="chips">{chips}</div>{DEALS_BLOCK}{sections}' + CTA + '</div>',
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

urls = [BASE] + [BASE + p for p in ["about.html", "disclosure.html", "privacy.html"]] + [BASE + fn for k, c, lg, fn in DEAL_ALL] + [BASE + g["slug"] + ".html" for g in GUIDES] + [BASE + r for r in ROUTES]
with open(os.path.join(OUT, "sitemap.xml"), "w") as f:
    f.write('<?xml version="1.0" encoding="UTF-8"?>' + NL + '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + NL +
            "".join(f"<url><loc>{u}</loc><lastmod>{datetime.date.today().isoformat()}</lastmod></url>" + NL + "" for u in urls) + "</urlset>" + NL + "")
items = "".join(f"<item><title>{html.escape(g['title'])}</title><link>{BASE}{g['slug']}.html</link><guid>{BASE}{g['slug']}.html</guid><description>{html.escape(g['desc'])}</description></item>" for g in GUIDES)
with open(os.path.join(OUT, "feed.xml"), "w", encoding="utf-8") as f:
    f.write(f'<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel><title>Tripwise Guides</title><link>{BASE}</link><description>Practical, budget-friendly travel guides</description>{items}</channel></rss>')
print(sorted(os.listdir(OUT)))
