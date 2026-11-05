import os, sys, html, json, datetime, urllib.request, urllib.parse
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
    "weekend-trips-from-tallinn": ("Travel tips", "Weekend trips", "Kraków Old Town"),
    "tallinn-to-stockholm": ("Sweden", "Tallinn – Stockholm", "Gamla stan"),
    "december-trips-from-the-baltics": ("Travel tips", "December trips", "Tenerife"),
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
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
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
                url = "https://www.aviasales.com" + path + ("&" if "?" in path else "?") + "marker=793212.blog"
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

urls = [BASE] + [BASE + p for p in ["about.html", "disclosure.html", "privacy.html"]] + [BASE + fn for k, c, lg, fn in DEAL_ALL] + [BASE + g["slug"] + ".html" for g in GUIDES]
with open(os.path.join(OUT, "sitemap.xml"), "w") as f:
    f.write('<?xml version="1.0" encoding="UTF-8"?>' + NL + '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + NL +
            "".join(f"<url><loc>{u}</loc><lastmod>2026-10-28</lastmod></url>" + NL + "" for u in urls) + "</urlset>" + NL + "")
items = "".join(f"<item><title>{html.escape(g['title'])}</title><link>{BASE}{g['slug']}.html</link><guid>{BASE}{g['slug']}.html</guid><description>{html.escape(g['desc'])}</description></item>" for g in GUIDES)
with open(os.path.join(OUT, "feed.xml"), "w", encoding="utf-8") as f:
    f.write(f'<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel><title>Tripwise Guides</title><link>{BASE}</link><description>Practical, budget-friendly travel guides</description>{items}</channel></rss>')
print(sorted(os.listdir(OUT)))
