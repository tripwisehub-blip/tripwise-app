"""Price-drop alerts for Tripwise.

People subscribe in the Mini App (bell button). The app opens the bot with
/start a_<ORIG>_<DEST>_<YYMMDD>_<YYMMDD>_<PAX>, and the Make scenario saves a record
"a<chat>_<route>" in the Make data store (field "session" = last price in EUR, "0" = new).
/stopalerts saves "x<chat>" - all alerts of that chat are removed here.

This script (GitHub Actions, every 6 hours) checks current prices on Aviasales via the
Travelpayouts API and messages people through the bot when a trip gets cheaper.

Secrets: TP_TOKEN (Travelpayouts), MAKE_TOKEN (Make API, data stores read/write),
TG_BOT_TOKEN (the bot token from @BotFather). Standard library only.
"""
import datetime as dt
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

MAKE_API = "https://eu1.make.com/api/v2"
STORE_ID = 227292
MARKER = "793212"
DROP_MIN = 0.02  # notify only when the price drops by at least 2 %

TP = os.environ.get("TP_TOKEN", "").strip()
MAKE = os.environ.get("MAKE_TOKEN", "").strip()
BOT = os.environ.get("TG_BOT_TOKEN", "").strip()
if not (TP and MAKE and BOT):
    print("Alerts are off: set the TP_TOKEN, MAKE_TOKEN and TG_BOT_TOKEN secrets.")
    sys.exit(0)


def call(method, url, body=None, headers=None):
    data = json.dumps(body).encode() if body is not None else None
    h = {"User-Agent": "tripwise-alerts/1.0", **(headers or {})}
    if data is not None:
        h["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=h, method=method)
    with urllib.request.urlopen(req, timeout=40) as resp:
        raw = resp.read()
        return json.loads(raw) if raw else {}


def make(method, path, body=None):
    return call(method, MAKE_API + path, body, {"Authorization": "Token " + MAKE})


def records():
    out, offset = [], 0
    while True:
        page = make("GET", "/data-stores/%d/data?pg%%5Blimit%%5D=100&pg%%5Boffset%%5D=%d" % (STORE_ID, offset))
        rows = page.get("records") or []
        out.extend(rows)
        if len(rows) < 100:
            return out
        offset += 100


def delete(keys):
    if keys:
        make("DELETE", "/data-stores/%d/data" % STORE_ID, {"keys": list(keys)})
        print("deleted", len(keys))


def send(chat, text, url, button):
    body = {"chat_id": chat, "text": text, "disable_web_page_preview": True,
            "reply_markup": {"inline_keyboard": [[{"text": button, "url": url}]]}}
    try:
        call("POST", "https://api.telegram.org/bot%s/sendMessage" % BOT, body)
        return True
    except urllib.error.HTTPError as e:
        print("telegram", chat, e.code)
        return e.code not in (400, 403)  # chat gone or bot blocked -> drop the alert


def cheapest(orig, dest, dep, ret):
    q = urllib.parse.urlencode({"origin": orig, "destination": dest, "departure_at": dep.isoformat(),
                                "return_at": ret.isoformat(), "one_way": "false", "sorting": "price",
                                "limit": 10, "currency": "eur"})
    rows = call("GET", "https://api.travelpayouts.com/aviasales/v3/prices_for_dates?" + q,
                headers={"X-Access-Token": TP}).get("data") or []
    prices = [r["price"] for r in rows if r.get("price")]
    return min(prices) if prices else None


# Messages in the language the user had in the app (last part of the alert key, "en" if missing)
MSG = {
    "en": ("📊 Now tracking {trip}.\nCurrent price: from €{p} round trip per person.\nI'll message you when it gets cheaper.",
           "📉 Price drop! {trip}\nNow from €{p} (was €{old}) round trip per person.\nPrices change fast — check it now.",
           "Stop alerts: /stopalerts", "Show flights"),
    "ru": ("📊 Слежу за ценой: {trip}.\nСейчас: от €{p} туда-обратно на человека.\nНапишу, когда станет дешевле.",
           "📉 Цена снизилась! {trip}\nСейчас от €{p} (было €{old}) туда-обратно на человека.\nЦены быстро меняются — проверьте сейчас.",
           "Отключить уведомления: /stopalerts", "Смотреть билеты"),
    "uk": ("📊 Стежу за ціною: {trip}.\nЗараз: від €{p} туди й назад на людину.\nНапишу, коли стане дешевше.",
           "📉 Ціна знизилася! {trip}\nЗараз від €{p} (було €{old}) туди й назад на людину.\nЦіни швидко змінюються — перевірте зараз.",
           "Вимкнути сповіщення: /stopalerts", "Дивитися квитки"),
    "et": ("📊 Jälgin hinda: {trip}.\nPraegu: alates €{p} edasi-tagasi inimese kohta.\nAnnan teada, kui läheb odavamaks.",
           "📉 Hind langes! {trip}\nNüüd alates €{p} (oli €{old}) edasi-tagasi inimese kohta.\nHinnad muutuvad kiiresti — vaata kohe.",
           "Peata teavitused: /stopalerts", "Vaata lende"),
    "fi": ("📊 Seuraan hintaa: {trip}.\nNyt: alkaen €{p} meno-paluu per henkilö.\nKerron, kun hinta laskee.",
           "📉 Hinta laski! {trip}\nNyt alkaen €{p} (oli €{old}) meno-paluu per henkilö.\nHinnat muuttuvat nopeasti — tarkista nyt.",
           "Lopeta hälytykset: /stopalerts", "Näytä lennot"),
    "lv": ("📊 Sekoju cenai: {trip}.\nPašlaik: no €{p} turp un atpakaļ vienai personai.\nUzrakstīšu, kad kļūs lētāk.",
           "📉 Cena samazinājās! {trip}\nTagad no €{p} (bija €{old}) turp un atpakaļ vienai personai.\nCenas mainās ātri — pārbaudi tagad.",
           "Izslēgt paziņojumus: /stopalerts", "Skatīt lidojumus"),
    "lt": ("📊 Stebiu kainą: {trip}.\nDabar: nuo €{p} į abi puses vienam asmeniui.\nParašysiu, kai atpigs.",
           "📉 Kaina sumažėjo! {trip}\nDabar nuo €{p} (buvo €{old}) į abi puses vienam asmeniui.\nKainos keičiasi greitai — patikrink dabar.",
           "Išjungti pranešimus: /stopalerts", "Žiūrėti skrydžius"),
    "pl": ("📊 Śledzę cenę: {trip}.\nTeraz: od €{p} w obie strony za osobę.\nNapiszę, gdy stanieje.",
           "📉 Cena spadła! {trip}\nTeraz od €{p} (było €{old}) w obie strony za osobę.\nCeny szybko się zmieniają — sprawdź teraz.",
           "Wyłącz alerty: /stopalerts", "Pokaż loty"),
    "de": ("📊 Ich beobachte den Preis: {trip}.\nAktuell: ab €{p} hin und zurück pro Person.\nIch melde mich, wenn es günstiger wird.",
           "📉 Preis gesunken! {trip}\nJetzt ab €{p} (vorher €{old}) hin und zurück pro Person.\nPreise ändern sich schnell — jetzt prüfen.",
           "Preisalarme stoppen: /stopalerts", "Flüge anzeigen"),
    "fr": ("📊 Je surveille le prix : {trip}.\nActuellement : à partir de {p} € aller-retour par personne.\nJe vous écris dès qu'il baisse.",
           "📉 Le prix a baissé ! {trip}\nMaintenant à partir de {p} € (avant {old} €) aller-retour par personne.\nLes prix changent vite — vérifiez maintenant.",
           "Arrêter les alertes : /stopalerts", "Voir les vols"),
    "es": ("📊 Sigo el precio: {trip}.\nAhora: desde {p} € ida y vuelta por persona.\nTe aviso cuando baje.",
           "📉 ¡Bajó el precio! {trip}\nAhora desde {p} € (antes {old} €) ida y vuelta por persona.\nLos precios cambian rápido: compruébalo ya.",
           "Detener alertas: /stopalerts", "Ver vuelos"),
    "it": ("📊 Seguo il prezzo: {trip}.\nOra: da {p} € andata e ritorno a persona.\nTi scrivo quando scende.",
           "📉 Il prezzo è sceso! {trip}\nOra da {p} € (prima {old} €) andata e ritorno a persona.\nI prezzi cambiano in fretta: controlla ora.",
           "Disattiva gli avvisi: /stopalerts", "Vedi i voli"),
    "tr": ("📊 Fiyatı takip ediyorum: {trip}.\nŞu an: kişi başı gidiş-dönüş €{p}'dan başlayan fiyatlarla.\nUcuzladığında yazacağım.",
           "📉 Fiyat düştü! {trip}\nŞimdi kişi başı gidiş-dönüş €{p}'dan başlıyor (önce €{old}).\nFiyatlar hızla değişir — hemen kontrol et.",
           "Alarmları durdur: /stopalerts", "Uçuşları göster"),
    "ar": ("📊 أتابع السعر: {trip}.\nالآن: من {p} يورو ذهابًا وإيابًا للشخص.\nسأراسلك عندما ينخفض السعر.",
           "📉 انخفض السعر! {trip}\nالآن من {p} يورو (كان {old} يورو) ذهابًا وإيابًا للشخص.\nالأسعار تتغير بسرعة — تحقق الآن.",
           "إيقاف التنبيهات: /stopalerts", "عرض الرحلات"),
    "zh": ("📊 正在关注价格：{trip}。\n当前：每人往返 €{p} 起。\n降价时我会通知你。",
           "📉 降价了！{trip}\n现在每人往返 €{p} 起（之前 €{old}）。\n价格变化很快，现在就看看吧。",
           "停止提醒：/stopalerts", "查看航班"),
    "ja": ("📊 価格を追跡中：{trip}\n現在：1人往復 €{p} から\n安くなったらお知らせします。",
           "📉 値下がりしました！{trip}\n現在 1人往復 €{p} から（以前 €{old}）\n価格はすぐ変わります。今すぐ確認を。",
           "通知を停止：/stopalerts", "フライトを見る"),
    "ko": ("📊 가격을 추적 중: {trip}\n현재: 1인 왕복 €{p}부터\n더 저렴해지면 알려드릴게요.",
           "📉 가격이 내려갔어요! {trip}\n지금 1인 왕복 €{p}부터 (이전 €{old})\n가격은 빠르게 바뀌어요. 지금 확인하세요.",
           "알림 중지: /stopalerts", "항공편 보기"),
    "th": ("📊 กำลังติดตามราคา: {trip}\nตอนนี้: ไป-กลับเริ่มต้น €{p} ต่อคน\nจะแจ้งเมื่อราคาถูกลง",
           "📉 ราคาลดลง! {trip}\nตอนนี้ไป-กลับเริ่มต้น €{p} ต่อคน (เดิม €{old})\nราคาเปลี่ยนเร็ว รีบเช็กเลย",
           "หยุดการแจ้งเตือน: /stopalerts", "ดูเที่ยวบิน"),
    "vi": ("📊 Đang theo dõi giá: {trip}.\nHiện tại: khứ hồi từ €{p} mỗi người.\nMình sẽ báo khi giá giảm.",
           "📉 Giá đã giảm! {trip}\nHiện từ €{p} (trước đó €{old}) khứ hồi mỗi người.\nGiá thay đổi nhanh — kiểm tra ngay.",
           "Tắt cảnh báo: /stopalerts", "Xem chuyến bay"),
    "hi": ("📊 कीमत पर नज़र रख रहा हूँ: {trip}.\nअभी: प्रति व्यक्ति आने-जाने का किराया €{p} से।\nसस्ता होने पर बताऊँगा।",
           "📉 कीमत घटी! {trip}\nअब प्रति व्यक्ति आने-जाने का किराया €{p} से (पहले €{old})।\nकीमतें जल्दी बदलती हैं — अभी देखें।",
           "अलर्ट बंद करें: /stopalerts", "फ़्लाइट देखें"),
    "id": ("📊 Memantau harga: {trip}.\nSaat ini: pulang-pergi mulai €{p} per orang.\nSaya kabari saat lebih murah.",
           "📉 Harga turun! {trip}\nSekarang mulai €{p} (sebelumnya €{old}) pulang-pergi per orang.\nHarga cepat berubah — cek sekarang.",
           "Hentikan peringatan: /stopalerts", "Lihat penerbangan"),
}

names = {}
try:
    for c in call("GET", "https://api.travelpayouts.com/data/en/cities.json"):
        tr = c.get("name_translations") or {}
        names[c["code"]] = {k: v for k, v in tr.items() if v}
        names[c["code"]].setdefault("en", c.get("name") or c["code"])
except Exception as e:
    print("cities failed:", e)


def city(code, lang):
    n = names.get(code) or {}
    return n.get(lang) or n.get("en") or code

today = dt.date.today()
recs = records()
stops = {r["key"][1:] for r in recs if r["key"].startswith("x")}
alerts = [r for r in recs if r["key"].startswith("a")]
remove = {"x" + c for c in stops}
sent = 0

for r in alerts:
    key = r["key"]
    chat, _, route = key[1:].partition("_")
    if chat in stops:
        remove.add(key)
        continue
    try:
        parts = route.split("_")
        orig, dest, d1, d2 = parts[:4]
        pax = parts[4] if len(parts) > 4 else "1"
        lang = parts[5] if len(parts) > 5 and parts[5] in MSG else "en"
        dep = dt.datetime.strptime(d1, "%y%m%d").date()
        ret = dt.datetime.strptime(d2, "%y%m%d").date()
    except ValueError:
        remove.add(key)
        continue
    if dep <= today:
        remove.add(key)
        continue
    try:
        price = cheapest(orig, dest, dep, ret)
    except Exception as e:
        print(key, "price failed:", e)
        continue
    if price is None:
        continue
    last = float((r.get("data") or {}).get("session") or 0)
    trip = "%s → %s, %s–%s" % (city(orig, lang), city(dest, lang), dep.strftime("%d.%m"), ret.strftime("%d.%m.%Y"))
    m = MSG[lang]
    url = "https://www.aviasales.com/search/%s%s%s%s%s?marker=%s.alert&currency=eur" % (
        orig, dep.strftime("%d%m"), dest, ret.strftime("%d%m"), pax, MARKER)
    if last <= 0:
        text = m[0].format(trip=trip, p=int(price)) + "\n" + m[2]
    elif price <= last * (1 - DROP_MIN):
        text = m[1].format(trip=trip, p=int(price), old=int(last)) + "\n" + m[2]
    else:
        if price > last:  # remember the new level so the next drop is measured from it
            make("PUT", "/data-stores/%d/data/%s" % (STORE_ID, urllib.parse.quote(key)), {"session": str(price)})
        continue
    if send(chat, text, url, m[3]):
        make("PUT", "/data-stores/%d/data/%s" % (STORE_ID, urllib.parse.quote(key)), {"session": str(price)})
        sent += 1
    else:
        remove.add(key)

delete(remove)
print("alerts:", len(alerts), "messages sent:", sent)
