// Tripwise Telegram bot on Cloudflare Workers (free plan): replaces the Make scenario "СЕТЬ — Диалог Tripwise".
// Bindings: KV namespace BOT, Workers AI binding AI, secret TG_BOT_TOKEN.
// KV keys: c<chat> = {lang, s} (language and session), h<chat> = chat history,
//          a<chat>_<route> = last alert price ("0" = new), x<chat> = stop all alerts.
// /store endpoints are for scripts/price_alerts.py (header X-Key = sha256 of the bot token).

const APP = "https://tripwisehub-blip.github.io/tripwise-app/";
const LANGS = [["en", "🇬🇧 English"], ["ru", "🇷🇺 Русский"], ["uk", "🇺🇦 Українська"], ["et", "🇪🇪 Eesti"], ["fi", "🇫🇮 Suomi"], ["lv", "🇱🇻 Latviešu"],
  ["lt", "🇱🇹 Lietuvių"], ["pl", "🇵🇱 Polski"], ["de", "🇩🇪 Deutsch"], ["fr", "🇫🇷 Français"], ["es", "🇪🇸 Español"], ["it", "🇮🇹 Italiano"],
  ["tr", "🇹🇷 Türkçe"], ["ar", "🇸🇦 العربية"], ["hi", "🇮🇳 हिन्दी"], ["zh", "🇨🇳 中文"], ["ja", "🇯🇵 日本語"], ["ko", "🇰🇷 한국어"],
  ["th", "🇹🇭 ไทย"], ["vi", "🇻🇳 Tiếng Việt"], ["id", "🇮🇩 Indonesia"]];

const HELLO = {
  en: "Hi! I'm Tripwise — I help you travel for less, anywhere in the world ✈️\n\nWhat I can do:\n\n1️⃣ Find cheap flights. Write your route and dates, for example: \"London to Barcelona on 10 December, one way\". Buttons with prices will appear under my reply — tap one and book. The Kiwi.com button also shows low-cost airlines so you can compare.\n\n2️⃣ Everything for your trip in one place. Tap the ✈️ button under this message:\n✈️ find the cheapest flight and pick the one you like;\n🏨 switch to the \"Hotels\" tab — offers in the same city are already there;\n🚗 next to it: \"Cars\", \"Transfers\", \"Tours\" and \"eSIM\" for mobile internet abroad.\n\n3️⃣ Stingy Traveller wheel 🎡 — for when you haven't decided where to go. Set a budget and spin: the wheel picks a weekend city and shows flight prices. Like it? Tap the flight you want and move on to hotels.\n\n4️⃣ Price alerts 🔔 — tap the bell next to a flight and I'll message you when it gets cheaper.\n\n🎙 Write or send voice messages in any language.\n🔥 Hot deals every day: @tripwise_deals\n\nWhere are we heading?",
  ru: "Привет! Я Tripwise — помогаю путешествовать дешевле по всему миру ✈️\n\nЧто я умею:\n\n1️⃣ Найти дешёвые билеты. Напишите маршрут и даты, например: «из Вильнюса в Таллин 10 декабря, только туда». Под ответом появятся кнопки с ценами — нажали и бронируете. Кнопка Kiwi.com покажет ещё и лоукосты для сравнения.\n\n2️⃣ Всё для поездки в одном месте. Нажмите кнопку ✈️ под этим сообщением:\n✈️ найдите самый дешёвый рейс и выберите подходящий;\n🏨 переключитесь на вкладку «Отели» — там уже предложения в том же городе;\n🚗 рядом «Авто», «Трансферы», «Экскурсии» и «eSIM» для интернета за границей.\n\n3️⃣ Колесо скупого путешественника 🎡 — если ещё не решили, куда ехать. Укажите бюджет и крутите: колесо выберет город на выходные и покажет цены на рейсы. Понравилось — кликните на нужный билет и переходите к отелям.\n\n4️⃣ Слежка за ценой 🔔 — нажмите на колокольчик у рейса, и я напишу, когда билет подешевеет.\n\n🎙 Пишите или отправляйте голосовые на любом языке.\n🔥 Горящие предложения каждый день: @tripwise_deals\n\nКуда отправимся?",
  uk: "Привіт! Я Tripwise — допомагаю подорожувати дешевше по всьому світу ✈️\n\nЩо я вмію:\n\n1️⃣ Знайти дешеві квитки. Напишіть маршрут і дати, наприклад: «з Варшави до Риму 10 грудня, тільки туди». Під відповіддю з'являться кнопки з цінами — натиснули й бронюєте. Кнопка Kiwi.com покаже ще й лоукости для порівняння.\n\n2️⃣ Усе для поїздки в одному місці. Натисніть кнопку ✈️ під цим повідомленням:\n✈️ знайдіть найдешевший рейс і виберіть потрібний;\n🏨 перейдіть на вкладку «Готелі» — там уже пропозиції в тому ж місті;\n🚗 поруч «Авто», «Трансфери», «Екскурсії» та «eSIM» для інтернету за кордоном.\n\n3️⃣ Колесо ощадливого мандрівника 🎡 — якщо ще не вирішили, куди їхати. Вкажіть бюджет і крутіть: колесо вибере місто на вихідні й покаже ціни на рейси. Сподобалося — натисніть на потрібний квиток і переходьте до готелів.\n\n4️⃣ Стеження за ціною 🔔 — натисніть на дзвіночок біля рейсу, і я напишу, коли квиток подешевшає.\n\n🎙 Пишіть або надсилайте голосові будь-якою мовою.\n🔥 Гарячі пропозиції щодня: @tripwise_deals\n\nКуди вирушаємо?",
  et: "Tere! Olen Tripwise — aitan reisida odavamalt üle kogu maailma ✈️\n\nMida ma oskan:\n\n1️⃣ Leida odavaid lennupileteid. Kirjuta marsruut ja kuupäevad, näiteks: „Tallinnast Barcelonasse 10. detsembril, ainult sinna“. Vastuse alla ilmuvad hindadega nupud — vajuta ja broneeri. Kiwi.com nupp näitab võrdluseks ka odavlennufirmasid.\n\n2️⃣ Kõik reisiks ühes kohas. Vajuta selle sõnumi all olevat ✈️ nuppu:\n✈️ leia odavaim lend ja vali sobiv;\n🏨 mine vahekaardile „Hotellid“ — seal on juba pakkumised samas linnas;\n🚗 kõrval „Autod“, „Transfeerid“, „Ekskursioonid“ ja „eSIM“ internetiks välismaal.\n\n3️⃣ Kokkuhoidliku reisija ratas 🎡 — kui sa pole veel otsustanud, kuhu minna. Määra eelarve ja keeruta: ratas valib nädalavahetuse linna ja näitab lennuhindu. Meeldib? Vajuta sobival piletil ja liigu edasi hotellide juurde.\n\n4️⃣ Hinnateavitus 🔔 — vajuta lennu juures kellukest ja ma kirjutan, kui pilet odavneb.\n\n🎙 Kirjuta või saada häälsõnum mis tahes keeles.\n🔥 Kuumad pakkumised iga päev: @tripwise_deals\n\nKuhu läheme?",
  fi: "Hei! Olen Tripwise — autan matkustamaan edullisemmin ympäri maailmaa ✈️\n\nMitä osaan:\n\n1️⃣ Löytää halpoja lentoja. Kirjoita reitti ja päivämäärät, esimerkiksi: ”Helsingistä Barcelonaan 10. joulukuuta, vain meno”. Vastaukseni alle tulee painikkeet hintoineen — napauta ja varaa. Kiwi.com-painike näyttää vertailuksi myös halpalentoyhtiöt.\n\n2️⃣ Kaikki matkaan yhdestä paikasta. Napauta tämän viestin alla olevaa ✈️-painiketta:\n✈️ etsi halvin lento ja valitse sopiva;\n🏨 siirry ”Hotellit”-välilehdelle — siellä on jo tarjoukset samassa kaupungissa;\n🚗 vieressä ”Autot”, ”Kuljetukset”, ”Retket” ja ”eSIM” nettiin ulkomailla.\n\n3️⃣ Säästäväisen matkaajan kiekko 🎡 — kun et ole vielä päättänyt, minne lähteä. Aseta budjetti ja pyöräytä: kiekko valitsee viikonloppukaupungin ja näyttää lentohinnat. Kiinnostaako? Napauta haluamaasi lentoa ja siirry hotelleihin.\n\n4️⃣ Hintahälytys 🔔 — napauta lennon vieressä olevaa kelloa, niin kerron, kun lippu halpenee.\n\n🎙 Kirjoita tai lähetä ääniviesti millä kielellä tahansa.\n🔥 Kuumat tarjoukset joka päivä: @tripwise_deals\n\nMinne mennään?",
  lv: "Sveiki! Esmu Tripwise — palīdzu ceļot lētāk visā pasaulē ✈️\n\nKo es protu:\n\n1️⃣ Atrast lētas aviobiļetes. Uzrakstiet maršrutu un datumus, piemēram: “no Rīgas uz Barselonu 10. decembrī, tikai turp”. Zem atbildes parādīsies pogas ar cenām — nospiediet un rezervējiet. Poga Kiwi.com salīdzināšanai parādīs arī zemo cenu aviokompānijas.\n\n2️⃣ Viss ceļojumam vienuviet. Nospiediet ✈️ pogu zem šīs ziņas:\n✈️ atrodiet lētāko lidojumu un izvēlieties piemērotāko;\n🏨 pārejiet uz cilni “Viesnīcas” — tur jau ir piedāvājumi tajā pašā pilsētā;\n🚗 blakus “Auto”, “Transfēri”, “Ekskursijas” un “eSIM” internetam ārzemēs.\n\n3️⃣ Taupīgā ceļotāja rats 🎡 — ja vēl neesat izlēmuši, kurp doties. Norādiet budžetu un grieziet: rats izvēlēsies pilsētu nedēļas nogalei un parādīs lidojumu cenas. Patīk? Nospiediet vajadzīgo biļeti un pārejiet pie viesnīcām.\n\n4️⃣ Cenu sekošana 🔔 — nospiediet zvaniņu pie lidojuma, un es uzrakstīšu, kad biļete kļūs lētāka.\n\n🎙 Rakstiet vai sūtiet balss ziņas jebkurā valodā.\n🔥 Karstie piedāvājumi katru dienu: @tripwise_deals\n\nKurp dodamies?",
  lt: "Sveiki! Aš Tripwise — padedu keliauti pigiau po visą pasaulį ✈️\n\nKą moku:\n\n1️⃣ Rasti pigius lėktuvo bilietus. Parašykite maršrutą ir datas, pavyzdžiui: „iš Vilniaus į Barseloną gruodžio 10 d., tik į vieną pusę“. Po atsakymu atsiras mygtukai su kainomis — paspaudėte ir užsisakote. Mygtukas Kiwi.com palyginimui parodys ir pigių skrydžių bendroves.\n\n2️⃣ Viskas kelionei vienoje vietoje. Paspauskite ✈️ mygtuką po šia žinute:\n✈️ raskite pigiausią skrydį ir išsirinkite tinkamą;\n🏨 pereikite į skirtuką „Viešbučiai“ — ten jau yra pasiūlymai tame pačiame mieste;\n🚗 šalia „Automobiliai“, „Pervežimai“, „Ekskursijos“ ir „eSIM“ internetui užsienyje.\n\n3️⃣ Taupaus keliautojo ratas 🎡 — jei dar nenusprendėte, kur vykti. Nurodykite biudžetą ir sukite: ratas parinks miestą savaitgaliui ir parodys skrydžių kainas. Patiko? Paspauskite norimą bilietą ir pereikite prie viešbučių.\n\n4️⃣ Kainos stebėjimas 🔔 — paspauskite varpelį prie skrydžio, ir parašysiu, kai bilietas atpigs.\n\n🎙 Rašykite arba siųskite balso žinutes bet kuria kalba.\n🔥 Karšti pasiūlymai kasdien: @tripwise_deals\n\nKur keliaujame?",
  pl: "Cześć! Jestem Tripwise — pomagam podróżować taniej po całym świecie ✈️\n\nCo potrafię:\n\n1️⃣ Znaleźć tanie loty. Napisz trasę i daty, na przykład: „z Warszawy do Barcelony 10 grudnia, tylko w jedną stronę”. Pod odpowiedzią pojawią się przyciski z cenami — klikasz i rezerwujesz. Przycisk Kiwi.com pokaże też tanie linie, żeby porównać.\n\n2️⃣ Wszystko do podróży w jednym miejscu. Kliknij przycisk ✈️ pod tą wiadomością:\n✈️ znajdź najtańszy lot i wybierz odpowiedni;\n🏨 przejdź do zakładki „Hotele” — są tam już oferty w tym samym mieście;\n🚗 obok „Auta”, „Transfery”, „Wycieczki” i „eSIM” do internetu za granicą.\n\n3️⃣ Koło oszczędnego podróżnika 🎡 — gdy jeszcze nie wiesz, dokąd jechać. Ustaw budżet i zakręć: koło wybierze miasto na weekend i pokaże ceny lotów. Podoba się? Kliknij wybrany bilet i przejdź do hoteli.\n\n4️⃣ Alert cenowy 🔔 — kliknij dzwonek przy locie, a napiszę, gdy bilet stanieje.\n\n🎙 Pisz lub wysyłaj wiadomości głosowe w dowolnym języku.\n🔥 Gorące oferty codziennie: @tripwise_deals\n\nDokąd lecimy?",
  de: "Hallo! Ich bin Tripwise — ich helfe dir, günstiger zu reisen, überall auf der Welt ✈️\n\nWas ich kann:\n\n1️⃣ Günstige Flüge finden. Schreib Strecke und Daten, zum Beispiel: „von Berlin nach Barcelona am 10. Dezember, nur hin“. Unter meiner Antwort erscheinen Buttons mit Preisen — antippen und buchen. Der Kiwi.com-Button zeigt zum Vergleich auch Billigairlines.\n\n2️⃣ Alles für die Reise an einem Ort. Tippe auf den ✈️-Button unter dieser Nachricht:\n✈️ finde den günstigsten Flug und wähle den passenden;\n🏨 wechsle zum Tab „Hotels“ — dort warten schon Angebote in derselben Stadt;\n🚗 daneben „Mietwagen“, „Transfers“, „Touren“ und „eSIM“ fürs Internet im Ausland.\n\n3️⃣ Sparfuchs-Glücksrad 🎡 — wenn du noch nicht weißt, wohin. Budget festlegen und drehen: Das Rad wählt eine Stadt fürs Wochenende und zeigt die Flugpreise. Gefällt dir? Tippe auf den gewünschten Flug und weiter geht's zu den Hotels.\n\n4️⃣ Preisalarm 🔔 — tippe auf die Glocke neben einem Flug und ich melde mich, sobald er günstiger wird.\n\n🎙 Schreib oder schick Sprachnachrichten in jeder Sprache.\n🔥 Heiße Angebote jeden Tag: @tripwise_deals\n\nWohin geht's?",
  fr: "Bonjour ! Je suis Tripwise — je vous aide à voyager moins cher partout dans le monde ✈️\n\nCe que je sais faire :\n\n1️⃣ Trouver des vols pas chers. Écrivez l'itinéraire et les dates, par exemple : « de Paris à Barcelone le 10 décembre, aller simple ». Des boutons avec les prix apparaîtront sous ma réponse — touchez et réservez. Le bouton Kiwi.com affiche aussi les compagnies low-cost pour comparer.\n\n2️⃣ Tout pour le voyage au même endroit. Touchez le bouton ✈️ sous ce message :\n✈️ trouvez le vol le moins cher et choisissez celui qui vous convient ;\n🏨 passez à l'onglet « Hôtels » — les offres dans la même ville y sont déjà ;\n🚗 à côté : « Voitures », « Transferts », « Visites » et « eSIM » pour internet à l'étranger.\n\n3️⃣ La roue du voyageur malin 🎡 — si vous ne savez pas encore où partir. Fixez un budget et faites tourner : la roue choisit une ville pour le week-end et affiche les prix des vols. Ça vous plaît ? Touchez le billet voulu et passez aux hôtels.\n\n4️⃣ Alerte prix 🔔 — touchez la cloche à côté d'un vol et je vous écris dès que le prix baisse.\n\n🎙 Écrivez ou envoyez des messages vocaux dans n'importe quelle langue.\n🔥 Bons plans chaque jour : @tripwise_deals\n\nOn part où ?",
  es: "¡Hola! Soy Tripwise — te ayudo a viajar más barato por todo el mundo ✈️\n\nQué puedo hacer:\n\n1️⃣ Encontrar vuelos baratos. Escribe la ruta y las fechas, por ejemplo: «de Madrid a Roma el 10 de diciembre, solo ida». Debajo de mi respuesta aparecerán botones con precios — toca y reserva. El botón Kiwi.com muestra también aerolíneas low cost para comparar.\n\n2️⃣ Todo para el viaje en un solo lugar. Toca el botón ✈️ debajo de este mensaje:\n✈️ encuentra el vuelo más barato y elige el que te convenga;\n🏨 cambia a la pestaña «Hoteles» — ya tienes ofertas en la misma ciudad;\n🚗 al lado: «Coches», «Traslados», «Tours» y «eSIM» para internet en el extranjero.\n\n3️⃣ La ruleta del viajero ahorrador 🎡 — si aún no sabes adónde ir. Fija un presupuesto y gira: la ruleta elige una ciudad para el fin de semana y muestra los precios de los vuelos. ¿Te gusta? Toca el billete que quieras y pasa a los hoteles.\n\n4️⃣ Alerta de precio 🔔 — toca la campana junto a un vuelo y te escribiré cuando baje de precio.\n\n🎙 Escribe o envía mensajes de voz en cualquier idioma.\n🔥 Ofertas cada día: @tripwise_deals\n\n¿Adónde vamos?",
  it: "Ciao! Sono Tripwise — ti aiuto a viaggiare spendendo meno in tutto il mondo ✈️\n\nCosa so fare:\n\n1️⃣ Trovare voli economici. Scrivi tratta e date, per esempio: «da Milano a Barcellona il 10 dicembre, solo andata». Sotto la mia risposta compariranno pulsanti con i prezzi — tocca e prenota. Il pulsante Kiwi.com mostra anche le low cost per confrontare.\n\n2️⃣ Tutto per il viaggio in un unico posto. Tocca il pulsante ✈️ sotto questo messaggio:\n✈️ trova il volo più economico e scegli quello giusto;\n🏨 passa alla scheda «Hotel» — ci sono già le offerte nella stessa città;\n🚗 accanto: «Auto», «Transfer», «Tour» ed «eSIM» per internet all'estero.\n\n3️⃣ La ruota del viaggiatore parsimonioso 🎡 — se non hai ancora deciso dove andare. Imposta un budget e gira: la ruota sceglie una città per il weekend e mostra i prezzi dei voli. Ti piace? Tocca il biglietto che vuoi e passa agli hotel.\n\n4️⃣ Avviso di prezzo 🔔 — tocca la campanella accanto a un volo e ti scrivo quando il prezzo scende.\n\n🎙 Scrivi o invia messaggi vocali in qualsiasi lingua.\n🔥 Offerte ogni giorno: @tripwise_deals\n\nDove andiamo?",
  tr: "Merhaba! Ben Tripwise — dünyanın her yerine daha ucuza seyahat etmene yardım ederim ✈️\n\nNeler yapabilirim:\n\n1️⃣ Ucuz uçak bileti bulmak. Rotayı ve tarihleri yaz, örneğin: \"İstanbul'dan Roma'ya 10 Aralık, tek yön\". Cevabımın altında fiyatlı butonlar çıkar — dokun ve rezervasyon yap. Kiwi.com butonu karşılaştırma için düşük maliyetli havayollarını da gösterir.\n\n2️⃣ Seyahat için her şey tek yerde. Bu mesajın altındaki ✈️ butonuna dokun:\n✈️ en ucuz uçuşu bul ve sana uygun olanı seç;\n🏨 \"Oteller\" sekmesine geç — aynı şehirdeki teklifler orada hazır;\n🚗 yanında \"Araçlar\", \"Transferler\", \"Turlar\" ve yurt dışında internet için \"eSIM\".\n\n3️⃣ Tutumlu gezgin çarkı 🎡 — nereye gideceğine henüz karar vermediysen. Bütçeni belirle ve çevir: çark hafta sonu için bir şehir seçer ve uçuş fiyatlarını gösterir. Beğendin mi? İstediğin bilete dokun ve otellere geç.\n\n4️⃣ Fiyat alarmı 🔔 — uçuşun yanındaki zile dokun, bilet ucuzlayınca sana yazarım.\n\n🎙 Her dilde yazabilir veya sesli mesaj gönderebilirsin.\n🔥 Her gün sıcak fırsatlar: @tripwise_deals\n\nNereye gidiyoruz?",
  ar: "مرحبًا! أنا Tripwise — أساعدك على السفر بتكلفة أقل إلى أي مكان في العالم ✈️\n\nما الذي أستطيع فعله:\n\n1️⃣ إيجاد تذاكر طيران رخيصة. اكتب الوجهة والتواريخ، مثلًا: «من دبي إلى إسطنبول في 10 ديسمبر، ذهاب فقط». ستظهر تحت ردّي أزرار بالأسعار — اضغط واحجز. زر Kiwi.com يعرض أيضًا شركات الطيران الاقتصادية للمقارنة.\n\n2️⃣ كل ما تحتاجه للرحلة في مكان واحد. اضغط زر ✈️ أسفل هذه الرسالة:\n✈️ ابحث عن أرخص رحلة واختر المناسبة لك؛\n🏨 انتقل إلى تبويب «فنادق» — ستجد عروض الفنادق في المدينة نفسها؛\n🚗 وبجانبه «سيارات» و«نقل» و«جولات» و«eSIM» للإنترنت في الخارج.\n\n3️⃣ عجلة المسافر المقتصد 🎡 — إذا لم تقرر بعد إلى أين تسافر. حدّد ميزانيتك وأدِر العجلة: ستختار لك مدينة لعطلة نهاية الأسبوع وتعرض أسعار الرحلات. أعجبتك؟ اضغط على التذكرة المناسبة وانتقل إلى الفنادق.\n\n4️⃣ تنبيه السعر 🔔 — اضغط على الجرس بجانب الرحلة وسأراسلك عندما ينخفض السعر.\n\n🎙 اكتب أو أرسل رسائل صوتية بأي لغة.\n🔥 عروض مميزة كل يوم: @tripwise_deals\n\nإلى أين نسافر؟",
  hi: "नमस्ते! मैं Tripwise हूँ — दुनिया में कहीं भी कम खर्च में यात्रा करने में मदद करता हूँ ✈️\n\nमैं क्या कर सकता हूँ:\n\n1️⃣ सस्ती फ़्लाइट ढूँढना। रूट और तारीख़ लिखें, जैसे: \"दिल्ली से दुबई 10 दिसंबर, सिर्फ़ जाना\"। मेरे जवाब के नीचे कीमतों वाले बटन आएँगे — टैप करें और बुक करें। Kiwi.com बटन तुलना के लिए लो-कॉस्ट एयरलाइंस भी दिखाता है।\n\n2️⃣ यात्रा की हर चीज़ एक जगह। इस संदेश के नीचे ✈️ बटन दबाएँ:\n✈️ सबसे सस्ती फ़्लाइट ढूँढें और अपनी पसंद चुनें;\n🏨 \"होटल\" टैब पर जाएँ — उसी शहर के ऑफ़र वहाँ पहले से मौजूद हैं;\n🚗 साथ में \"कार\", \"ट्रांसफ़र\", \"टूर\" और विदेश में इंटरनेट के लिए \"eSIM\"।\n\n3️⃣ किफ़ायती यात्री का पहिया 🎡 — अगर अभी तय नहीं किया कि कहाँ जाना है। बजट चुनें और घुमाएँ: पहिया वीकेंड के लिए एक शहर चुनेगा और फ़्लाइट की कीमतें दिखाएगा। पसंद आया? अपनी टिकट पर टैप करें और होटल पर जाएँ।\n\n4️⃣ प्राइस अलर्ट 🔔 — फ़्लाइट के पास घंटी दबाएँ, टिकट सस्ता होते ही मैं आपको लिखूँगा।\n\n🎙 किसी भी भाषा में लिखें या वॉइस मैसेज भेजें।\n🔥 हर दिन हॉट डील्स: @tripwise_deals\n\nकहाँ चलें?",
  zh: "你好！我是 Tripwise —— 帮你更省钱地环游世界 ✈️\n\n我能做什么：\n\n1️⃣ 找便宜机票。写下路线和日期，例如：“12月10日从上海到曼谷，单程”。我的回复下方会出现带价格的按钮——点击即可预订。Kiwi.com 按钮还会显示廉价航空，方便比价。\n\n2️⃣ 旅行所需一站搞定。点击这条消息下方的 ✈️ 按钮：\n✈️ 找到最便宜的航班，选择合适的一班；\n🏨 切换到“酒店”标签——同一城市的酒店优惠已经为你准备好；\n🚗 旁边还有“租车”“接送”“游览”和出国上网用的“eSIM”。\n\n3️⃣ 省钱旅行转盘 🎡 —— 还没想好去哪儿？设定预算并转动：转盘会选出一个周末城市并显示机票价格。喜欢吗？点击想要的机票，然后去看酒店。\n\n4️⃣ 降价提醒 🔔 —— 点击航班旁的铃铛，机票降价时我会通知你。\n\n🎙 可以用任何语言打字或发语音。\n🔥 每日特价：@tripwise_deals\n\n我们去哪儿？",
  ja: "こんにちは！Tripwise です —— 世界中どこへでも、もっとお得に旅できるようお手伝いします ✈️\n\nできること：\n\n1️⃣ 格安航空券を探す。ルートと日付を書いてください。例：「12月10日 東京からソウル、片道」。返信の下に料金付きのボタンが表示されます — タップして予約できます。Kiwi.com ボタンでは LCC も比較できます。\n\n2️⃣ 旅の準備がひとつの場所で。このメッセージの下の ✈️ ボタンをタップ：\n✈️ 最安の便を見つけて、好きな便を選ぶ；\n🏨「ホテル」タブに切り替えると、同じ都市のホテルがすでに表示されています；\n🚗 隣には「レンタカー」「送迎」「ツアー」、海外でネットを使う「eSIM」も。\n\n3️⃣ 節約旅ルーレット 🎡 —— 行き先が決まっていないときに。予算を決めて回すと、週末に行ける都市を選んで航空券の料金を表示します。気に入ったら、その航空券をタップしてホテルへ進みましょう。\n\n4️⃣ 値下がり通知 🔔 —— 便の横のベルをタップすると、安くなったときにお知らせします。\n\n🎙 どの言語でも、テキストでも音声でもOKです。\n🔥 毎日お得な情報：@tripwise_deals\n\nどこへ行きましょうか？",
  ko: "안녕하세요! 저는 Tripwise예요 — 전 세계 어디든 더 저렴하게 여행하도록 도와드려요 ✈️\n\n제가 할 수 있는 일:\n\n1️⃣ 저렴한 항공권 찾기. 노선과 날짜를 적어 주세요. 예: \"12월 10일 서울에서 도쿄, 편도\". 답변 아래에 가격이 적힌 버튼이 나타나요 — 누르고 바로 예약하세요. Kiwi.com 버튼으로 저가 항공사도 비교할 수 있어요.\n\n2️⃣ 여행 준비를 한곳에서. 이 메시지 아래의 ✈️ 버튼을 누르세요:\n✈️ 가장 저렴한 항공편을 찾아 원하는 것을 고르고;\n🏨 \"호텔\" 탭으로 이동하면 같은 도시의 호텔 상품이 이미 준비되어 있어요;\n🚗 옆에는 \"렌터카\", \"픽업\", \"투어\", 해외 인터넷용 \"eSIM\"도 있어요.\n\n3️⃣ 알뜰 여행자 룰렛 🎡 — 어디로 갈지 아직 정하지 못했다면. 예산을 정하고 돌리면 주말 여행 도시를 골라 항공권 가격을 보여 드려요. 마음에 드세요? 원하는 항공권을 누르고 호텔로 넘어가세요.\n\n4️⃣ 가격 알림 🔔 — 항공편 옆 종을 누르면 가격이 내려갈 때 알려 드려요.\n\n🎙 어떤 언어로든 글이나 음성 메시지를 보내 주세요.\n🔥 매일 특가: @tripwise_deals\n\n어디로 떠나 볼까요?",
  th: "สวัสดี! ฉันคือ Tripwise — ช่วยให้คุณเที่ยวได้ถูกลงทั่วโลก ✈️\n\nสิ่งที่ฉันทำได้:\n\n1️⃣ หาตั๋วเครื่องบินราคาถูก พิมพ์เส้นทางและวันที่ เช่น \"กรุงเทพฯ ไปโตเกียว 10 ธันวาคม เที่ยวเดียว\" ใต้คำตอบจะมีปุ่มพร้อมราคา — แตะแล้วจองได้เลย ปุ่ม Kiwi.com แสดงสายการบินโลว์คอสต์ให้เปรียบเทียบด้วย\n\n2️⃣ ทุกอย่างสำหรับทริปในที่เดียว แตะปุ่ม ✈️ ใต้ข้อความนี้:\n✈️ หาเที่ยวบินที่ถูกที่สุดแล้วเลือกเที่ยวที่ใช่;\n🏨 สลับไปแท็บ \"โรงแรม\" — มีข้อเสนอโรงแรมในเมืองเดียวกันรออยู่แล้ว;\n🚗 ข้าง ๆ มี \"รถเช่า\" \"รถรับส่ง\" \"ทัวร์\" และ \"eSIM\" สำหรับเน็ตต่างประเทศ\n\n3️⃣ วงล้อนักเดินทางสายประหยัด 🎡 — ถ้ายังไม่รู้ว่าจะไปไหน ตั้งงบแล้วหมุน: วงล้อจะเลือกเมืองสำหรับวันหยุดสุดสัปดาห์และแสดงราคาตั๋ว ชอบไหม? แตะตั๋วที่ต้องการแล้วไปต่อที่โรงแรม\n\n4️⃣ แจ้งเตือนราคา 🔔 — แตะกระดิ่งข้างเที่ยวบิน แล้วฉันจะแจ้งเมื่อตั๋วถูกลง\n\n🎙 พิมพ์หรือส่งข้อความเสียงได้ทุกภาษา\n🔥 ดีลร้อนทุกวัน: @tripwise_deals\n\nไปเที่ยวไหนดี?",
  vi: "Xin chào! Mình là Tripwise — giúp bạn du lịch tiết kiệm hơn khắp thế giới ✈️\n\nMình có thể:\n\n1️⃣ Tìm vé máy bay giá rẻ. Viết hành trình và ngày, ví dụ: \"từ Hà Nội đi Bangkok ngày 10 tháng 12, một chiều\". Dưới câu trả lời sẽ có các nút kèm giá — chạm và đặt vé. Nút Kiwi.com còn hiển thị các hãng giá rẻ để so sánh.\n\n2️⃣ Mọi thứ cho chuyến đi ở cùng một nơi. Chạm nút ✈️ bên dưới tin nhắn này:\n✈️ tìm chuyến bay rẻ nhất và chọn chuyến phù hợp;\n🏨 chuyển sang tab \"Khách sạn\" — ưu đãi ở cùng thành phố đã có sẵn;\n🚗 bên cạnh là \"Thuê xe\", \"Đưa đón\", \"Tour\" và \"eSIM\" để dùng internet ở nước ngoài.\n\n3️⃣ Vòng quay du lịch tiết kiệm 🎡 — khi bạn chưa biết đi đâu. Đặt ngân sách và quay: vòng quay sẽ chọn một thành phố cho cuối tuần và hiện giá vé. Thích không? Chạm vào vé bạn muốn rồi chuyển sang khách sạn.\n\n4️⃣ Báo giá 🔔 — chạm chuông cạnh chuyến bay, mình sẽ nhắn khi vé rẻ hơn.\n\n🎙 Viết hoặc gửi tin nhắn thoại bằng bất kỳ ngôn ngữ nào.\n🔥 Ưu đãi hot mỗi ngày: @tripwise_deals\n\nMình đi đâu nhé?",
  id: "Halo! Aku Tripwise — membantumu jalan-jalan lebih hemat ke seluruh dunia ✈️\n\nYang bisa aku lakukan:\n\n1️⃣ Cari tiket pesawat murah. Tulis rute dan tanggal, misalnya: \"dari Jakarta ke Singapura 10 Desember, sekali jalan\". Di bawah jawabanku akan muncul tombol berisi harga — ketuk dan pesan. Tombol Kiwi.com juga menampilkan maskapai berbiaya rendah untuk dibandingkan.\n\n2️⃣ Semua kebutuhan perjalanan di satu tempat. Ketuk tombol ✈️ di bawah pesan ini:\n✈️ temukan penerbangan termurah dan pilih yang cocok;\n🏨 pindah ke tab \"Hotel\" — penawaran di kota yang sama sudah tersedia;\n🚗 di sebelahnya ada \"Mobil\", \"Antar-jemput\", \"Tur\" dan \"eSIM\" untuk internet di luar negeri.\n\n3️⃣ Roda Pelancong Hemat 🎡 — kalau belum tahu mau ke mana. Atur anggaran dan putar: roda memilih kota untuk akhir pekan dan menampilkan harga tiket. Suka? Ketuk tiket yang kamu mau lalu lanjut ke hotel.\n\n4️⃣ Peringatan harga 🔔 — ketuk lonceng di samping penerbangan, aku akan kabari saat tiket lebih murah.\n\n🎙 Tulis atau kirim pesan suara dalam bahasa apa pun.\n🔥 Promo setiap hari: @tripwise_deals\n\nKita ke mana?",
};

const OPEN = { en: "✈️ Open Tripwise app", ru: "✈️ Открыть приложение", uk: "✈️ Відкрити застосунок", et: "✈️ Ava rakendus", fi: "✈️ Avaa sovellus",
  lv: "✈️ Atvērt lietotni", lt: "✈️ Atidaryti programėlę", pl: "✈️ Otwórz aplikację", de: "✈️ App öffnen", fr: "✈️ Ouvrir l'app", es: "✈️ Abrir la app",
  it: "✈️ Apri l'app", tr: "✈️ Uygulamayı aç", ar: "✈️ افتح التطبيق", hi: "✈️ ऐप खोलें", zh: "✈️ 打开应用", ja: "✈️ アプリを開く", ko: "✈️ 앱 열기",
  th: "✈️ เปิดแอป", vi: "✈️ Mở ứng dụng", id: "✈️ Buka aplikasi" };

const ALERT_ON = {
  en: ["🔔 Price alert is on:", "I check prices every 6 hours and will message you as soon as the trip gets cheaper. The first update will show the current price.\n\nTo stop all price alerts, send /stopalerts"],
  ru: ["🔔 Слежу за ценой:", "Проверяю цены каждые 6 часов и напишу, как только поездка подешевеет. В первом сообщении будет текущая цена.\n\nЧтобы отключить все уведомления, отправьте /stopalerts"],
  uk: ["🔔 Стежу за ціною:", "Перевіряю ціни кожні 6 годин і напишу, щойно поїздка подешевшає. У першому повідомленні буде поточна ціна.\n\nЩоб вимкнути всі сповіщення, надішліть /stopalerts"],
  et: ["🔔 Hinnateavitus on sees:", "Kontrollin hindu iga 6 tunni järel ja annan teada, kui reis odavneb. Esimeses sõnumis näed praegust hinda.\n\nKõigi teavituste peatamiseks saada /stopalerts"],
  fi: ["🔔 Hintahälytys on päällä:", "Tarkistan hinnat 6 tunnin välein ja kerron heti, kun matka halpenee. Ensimmäisessä viestissä näet nykyisen hinnan.\n\nLopeta kaikki hälytykset lähettämällä /stopalerts"],
  lv: ["🔔 Cenu paziņojums ieslēgts:", "Pārbaudu cenas ik pēc 6 stundām un uzrakstīšu, tiklīdz ceļojums kļūs lētāks. Pirmajā ziņā būs pašreizējā cena.\n\nLai izslēgtu visus paziņojumus, nosūti /stopalerts"],
  lt: ["🔔 Kainos pranešimas įjungtas:", "Tikrinu kainas kas 6 valandas ir parašysiu, kai tik kelionė atpigs. Pirmoje žinutėje bus dabartinė kaina.\n\nNorėdamas išjungti visus pranešimus, siųsk /stopalerts"],
  pl: ["🔔 Alert cenowy włączony:", "Sprawdzam ceny co 6 godzin i napiszę, gdy tylko podróż stanieje. W pierwszej wiadomości zobaczysz aktualną cenę.\n\nAby wyłączyć wszystkie alerty, wyślij /stopalerts"],
  de: ["🔔 Preisalarm ist aktiv:", "Ich prüfe die Preise alle 6 Stunden und melde mich, sobald die Reise günstiger wird. In der ersten Nachricht siehst du den aktuellen Preis.\n\nUm alle Preisalarme zu stoppen, sende /stopalerts"],
  fr: ["🔔 Alerte prix activée :", "Je vérifie les prix toutes les 6 heures et je vous écris dès que le voyage baisse. Le premier message indiquera le prix actuel.\n\nPour arrêter toutes les alertes, envoyez /stopalerts"],
  es: ["🔔 Alerta de precio activada:", "Reviso los precios cada 6 horas y te aviso en cuanto el viaje baje. El primer mensaje mostrará el precio actual.\n\nPara detener todas las alertas, envía /stopalerts"],
  it: ["🔔 Avviso di prezzo attivo:", "Controllo i prezzi ogni 6 ore e ti scrivo appena il viaggio costa meno. Il primo messaggio mostrerà il prezzo attuale.\n\nPer disattivare tutti gli avvisi, invia /stopalerts"],
};
const STOPPED = {
  en: "Done — all your price alerts will be removed within a few hours. You can set new ones any time with the bell button in the Tripwise app.",
  ru: "Готово — все уведомления о ценах будут удалены в течение нескольких часов. Новые можно включить в приложении Tripwise кнопкой с колокольчиком.",
  uk: "Готово — усі сповіщення про ціни буде видалено протягом кількох годин. Нові можна увімкнути в застосунку Tripwise кнопкою з дзвіночком.",
  et: "Valmis — kõik hinnateavitused eemaldatakse mõne tunni jooksul. Uusi saad lisada Tripwise'i rakenduses kellukese nupuga.",
  fi: "Valmis — kaikki hintahälytykset poistetaan muutaman tunnin kuluessa. Uusia voit lisätä Tripwise-sovelluksessa kellopainikkeella.",
  lv: "Gatavs — visi cenu paziņojumi tiks dzēsti dažu stundu laikā. Jaunus vari iestatīt Tripwise lietotnē ar zvaniņa pogu.",
  lt: "Atlikta — visi kainų pranešimai bus ištrinti per kelias valandas. Naujus gali nustatyti Tripwise programėlėje varpelio mygtuku.",
  pl: "Gotowe — wszystkie alerty cenowe zostaną usunięte w ciągu kilku godzin. Nowe ustawisz w aplikacji Tripwise przyciskiem z dzwonkiem.",
  de: "Fertig — alle Preisalarme werden in den nächsten Stunden entfernt. Neue kannst du jederzeit in der Tripwise-App mit der Glocke setzen.",
  fr: "C'est fait : toutes vos alertes prix seront supprimées d'ici quelques heures. Vous pouvez en créer de nouvelles dans l'app Tripwise avec la cloche.",
  es: "Listo: todas tus alertas de precio se eliminarán en unas horas. Puedes crear nuevas en la app Tripwise con el botón de la campana.",
  it: "Fatto: tutti gli avvisi di prezzo verranno rimossi entro poche ore. Puoi crearne di nuovi nell'app Tripwise con il pulsante della campanella.",
};
const SORRY = "Sorry, something went wrong on my side. Please try again in a moment.";
const NOVOICE = "Sorry, I couldn't hear that. Please type your question in any language and I'll help right away!";

const LINKS = `BOOKING LINKS (use ONLY these exact URLs or the links given in LIVE FARES, never invent or change links):
- Car rental: https://localrent.tpx.lu/EfbBHrJ5 (alternative: https://getrentacar.tpx.lu/iwSAxi5F)
- Tickets, museums, tours and activities: https://tiqets.tpx.lu/AT5p2SuI
- Audio guides and self-guided tours: https://wegotrip.tpx.lu/PFwel7W8
- Airport and city transfers: https://kiwitaxi.tpx.lu/Z8An788O
- eSIM / mobile internet abroad: https://airalo.tpx.lu/PfdD9FnS
- Flights: https://aviasales.tpx.lu/sjlt4H8o
- Compensation for a delayed or cancelled flight: https://airhelp.tpx.lu/65MarJSz
- Hotels anywhere in the world (compares Booking.com, Agoda, Expedia, Hotels.com, Vrbo and more): https://www.stay22.com/allez/roam?aid=tripwise&campaign=bot&address=CITY — replace CITY with the destination city name in English (spaces as %20). Add &checkin=YYYY-MM-DD&checkout=YYYY-MM-DD when the user gave dates. Also advise which areas to stay in.
- The Tripwise app (flight search, budget wheel, price-drop alerts): tell the user to tap the Open App button at the bottom of the chat.
COMPARE PARTNERS: for car rental give two links so the user can compare prices (Localrent and GetRentacar); for flights use LIVE FARES when given. Give at most 3 links per message, each on its own line after a short label written in the reply language (the link itself is shown to the user as the partner name, so write e.g. "Rent a car:" then the URL). Only in a message that actually contains a booking link, add once per conversation, in the reply language: "Some links are affiliate links — your price stays the same." Never add this note to a message without a link.`;

// More partners (Travelpayouts). Links are created once through the Links API with TP_TOKEN and cached in KV.
const PARTNERS = [
  ["Car rental worldwide, compare prices", "Economybookings", "https://www.economybookings.com/"],
  ["Car rental worldwide, compare prices", "QEEQ", "https://www.qeeq.com/"],
  ["Car rental in Europe and the UK", "AutoEurope", "https://www.autoeurope.eu/"],
  ["Scooters and motorbikes (Asia, islands, beach towns)", "BikesBooking", "https://bikesbooking.com/"],
  ["Airport and city transfers worldwide", "GetTransfer", "https://gettransfer.com/en"],
  ["Meet-and-greet airport pickups", "Welcome Pickups", "https://www.welcomepickups.com/"],
  ["Transfers", "Intui", "https://intui.travel/"],
  ["Tours and attractions, best in Asia", "Klook", "https://www.klook.com/"],
  ["Tours and attractions, best in Asia", "KKday", "https://www.kkday.com/"],
  ["City passes: many attractions in one ticket", "Go City", "https://gocity.com/"],
  ["eSIM", "Yesim", "https://yesim.app/"],
  ["eSIM", "Saily", "https://saily.com/"],
  ["eSIM", "GigSky", "https://www.gigsky.com/"],
  ["Physical travel SIM card", "Drimsim", "https://drimsim.com/"],
  ["Luggage storage in cities", "Radical Storage", "https://radicalstorage.com/"],
  ["Flight delay compensation, alternative", "Compensair", "https://www.compensair.com/"],
];

async function partnerLinks(env) {
  const map = (await env.BOT.get("plinks", "json").catch(() => null)) || {};
  if (PARTNERS.some((p) => !map[p[2]]) && env.TP_TOKEN && !(await env.BOT.get("plinks_try"))) {
    await env.BOT.put("plinks_try", "1", { expirationTtl: 3600 });
    for (const trs of [588570, 589578]) {
      const left = PARTNERS.filter((p) => !map[p[2]]);
      for (let i = 0; i < left.length; i += 10) {
        const part = left.slice(i, i + 10);
        const r = await fetch("https://api.travelpayouts.com/links/v1/create", { method: "POST",
          headers: { "X-Access-Token": env.TP_TOKEN, "Content-Type": "application/json" },
          body: JSON.stringify({ trs, marker: 793212, shorten: true, links: part.map((p) => ({ url: p[2], sub_id: "bot" })) }) });
        const j = await r.json().catch(() => ({}));
        ((j.result || {}).links || []).forEach((l, k) => { if (l.code === "success" && l.partner_url && part[k]) map[part[k][2]] = l.partner_url; });
      }
    }
    await env.BOT.put("plinks", JSON.stringify(map));
  }
  const lines = PARTNERS.filter((p) => map[p[2]]).map((p) => `- ${p[0]}: ${p[1]} ${map[p[2]]}`);
  if (!lines.length) return "";
  return "MORE PARTNERS (same rules; pick what fits the user's destination: in South-East and East Asia prefer Klook or KKday for tours and BikesBooking for scooters; in Europe AutoEurope is a good extra for cars; to compare car rental offer two of Localrent, GetRentacar, Economybookings, QEEQ; for transfers Kiwitaxi, GetTransfer, Welcome Pickups or Intui; for eSIM Airalo, Yesim, Saily or GigSky):\n" + lines.join("\n");
}

function systemPrompt(lang, extra) {
  return `You are Tripwise, a friendly travel assistant in Telegram that helps people anywhere in the world find good-value hotels, tours, car rentals, transfers, flights and travel extras for trips to any country. The user has already seen your greeting.

LANGUAGE (very important): Reply in the language of the user's own words in their latest message. Ignore place names, dates and brand names when deciding the language. If the latest message is short, mixed or only data (dates, cities, numbers), keep the language you have been using in this conversation; if there is no earlier conversation, use the user's chosen language, which has the code: ${lang}. Never switch to a language the user has not written in.

COMMANDS: /hotels, /tours, /car, /transfer, /esim mean the user wants help with that topic — start by asking where and when.

FLOW: 1) Find out destination, dates, number of travellers and budget or wishes — ask at most 3 short questions at once, skip what the user already told you. 2) When you have enough, give 3–5 concrete, practical suggestions: which area to stay in and why, what type of accommodation or tour fits, money-saving tips, when prices are lower. 3) When the user is ready to book or asks where to book, give the matching booking link from the list below. 4) Offer related help (a car, a transfer, a tour, an eSIM) in one short line.

${LINKS}
${extra || ""}

RULES: Never mention the current date or time unless the user asks. Never invent prices, hotel names, addresses or availability. The only prices you may quote are the ones given in a LIVE FARES message; otherwise give general guidance and tell the user to check current prices. Plain text only, no Markdown symbols like ** or #. Keep answers under 150 words. Be warm and concise, and write naturally and correctly in the reply language.`;
}

const pick = (obj, lang) => obj[lang] || obj.en;

async function tg(env, method, body) {
  const r = await fetch(`https://api.telegram.org/bot${env.TG_BOT_TOKEN}/${method}`, {
    method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
  return r.json().catch(() => ({}));
}

const send = (env, chat, text, markup) => tg(env, "sendMessage", { chat_id: chat, text, disable_web_page_preview: true, ...(markup ? { reply_markup: markup } : {}) });

// Turn long affiliate URLs into short clickable names ("Aviasales ↗") and send as HTML.
const BRANDS = [["stay22", "Hotels"], ["aviasales", "Aviasales"], ["kiwitaxi", "Kiwitaxi"], ["kiwi", "Kiwi.com"], ["localrent", "Localrent"], ["getrentacar", "GetRentacar"],
  ["tiqets", "Tiqets"], ["wegotrip", "WeGoTrip"], ["airalo", "Airalo"], ["airhelp", "AirHelp"], ["klook", "Klook"], ["kkday", "KKday"],
  ["economybookings", "Economybookings"], ["qeeq", "QEEQ"], ["yesim", "Yesim"], ["t.me/tripwise_deals", "@tripwise_deals"], ["tripwise-app", "Tripwise"],
  ["gettransfer", "GetTransfer"], ["welcomepickups", "Welcome Pickups"], ["intui", "Intui"], ["gigsky", "GigSky"], ["saily", "Saily"], ["drimsim", "Drimsim"],
  ["gocity", "Go City"], ["bikesbooking", "BikesBooking"], ["autoeurope", "AutoEurope"], ["radicalstorage", "Radical Storage"], ["compensair", "Compensair"]];
const esc = (t) => t.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
function brand(url) {
  let u = url;
  try { const p = new URL(url); u = (p.searchParams.get("u") || "") + " " + p.hostname + p.pathname; } catch (e) {}
  u = u.toLowerCase();
  const b = BRANDS.find(([k]) => u.includes(k));
  return b ? b[1] : "Link";
}
function pretty(text) {
  const parts = text.split(/(https?:\/\/[^\s)\]]+)/g);
  return parts.map((p, i) => {
    if (i % 2 === 0) return esc(p);
    const url = p.replace(/[.,;:!?]+$/, "");
    const tail = p.slice(url.length);
    return `<a href="${esc(url)}">${brand(url)} ↗</a>${esc(tail)}`;
  }).join("");
}
const sendPretty = (env, chat, text, buttons) => tg(env, "sendMessage", { chat_id: chat, text: pretty(text), parse_mode: "HTML", disable_web_page_preview: true,
  ...(buttons && buttons.length ? { reply_markup: { inline_keyboard: buttons } } : {}) })
  .then((r) => (r && r.ok ? r : send(env, chat, text, buttons && buttons.length ? { inline_keyboard: buttons } : null)));
const appButton = (lang) => ({ inline_keyboard: [[{ text: pick(OPEN, lang), web_app: { url: APP + "?lang=" + lang } }]] });

async function getUser(env, chat, from) {
  const u = await env.BOT.get("c" + chat, "json");
  if (u && u.lang) return u;
  const code = ((from && from.language_code) || "en").slice(0, 2);
  return { lang: HELLO[code] ? code : "en", s: (u && u.s) || "0" };
}

async function ask(env, chat, user, text) {
  const hist = (await env.BOT.get("h" + chat, "json")) || [];
  const extra = await partnerLinks(env).catch((e) => { console.log("partners", String(e)); return ""; });
  const messages = [{ role: "system", content: systemPrompt(user.lang, extra) }, ...hist, { role: "user", content: text }];
  let buttons = null;
  try {
    const fares = await liveFares(env, hist, text);
    if (fares && fares.text) {
      messages.splice(messages.length - 1, 0, { role: "system", content: fares.text });
      buttons = fares.buttons;
    }
  } catch (e) { console.log("fares", String(e)); }
  let answer = "";
  for (const model of ["@cf/meta/llama-3.3-70b-instruct-fp8-fast", "@cf/meta/llama-3.1-8b-instruct-fast"]) {
    try {
      const out = await env.AI.run(model, { messages, max_tokens: 500 });
      answer = (out && (out.response || "")).trim();
      if (answer) break;
    } catch (e) { console.log("ai", model, String(e)); }
  }
  if (!answer) return send(env, chat, SORRY);
  answer = answer.replace(/\*\*|__|^#+\s*/gm, "");
  const next = [...hist, { role: "user", content: text }, { role: "assistant", content: answer }].slice(-20);
  await env.BOT.put("h" + chat, JSON.stringify(next), { expirationTtl: 60 * 60 * 24 * 30 });
  return sendPretty(env, chat, answer, buttons);
}

// ---------- Live flight prices (Travelpayouts Data API) ----------
const hotelLink = (city, ci, co) => "https://www.stay22.com/allez/roam?aid=tripwise&campaign=bot&address=" + encodeURIComponent(city) + (ci && co ? "&checkin=" + ci + "&checkout=" + co : "");
const tpKiwi = () => "https://kiwi.tpx.lu/mSYPrCCe"; // Kiwi.com affiliate link (Website project)
const tpUrl = (u) => "https://tp.media/r?campaign_id=100&p=4114&trs=588570&marker=793212.bot&u=" + encodeURIComponent(u);

async function iata(term) {
  if (!term) return null;
  if (/^[A-Z]{3}$/.test(term)) return { code: term, name: term };
  const r = await fetch("https://autocomplete.travelpayouts.com/places2?locale=en&types[]=city&types[]=airport&term=" + encodeURIComponent(term));
  const list = await r.json().catch(() => []);
  const p = list && list[0];
  return p ? { code: p.city_code || p.code, name: p.city_name || p.name } : null;
}

async function liveFares(env, hist, text, log = () => {}) {
  if (!env.TP_TOKEN) { log("no TP_TOKEN"); return ""; }
  const recent = hist.slice(-4).map((m) => m.role + ": " + m.content).join("\n") + "\nuser: " + text;
  const ex = await env.AI.run("@cf/meta/llama-3.3-70b-instruct-fp8-fast", { max_tokens: 150, messages: [
    { role: "system", content: 'Extract the flight trip the user is planning from the conversation (any language; convert city names to their English nominative form, e.g. "из Вильнюса" -> "Vilnius"). Today is ' + new Date().toISOString().slice(0, 10) + '. Answer ONLY with JSON: {"from":"departure city in English or empty","to":"destination city in English or empty","month":"YYYY-MM or empty","depart":"YYYY-MM-DD or empty","return":"YYYY-MM-DD or empty","oneway":true or false (true if the user wants only one direction)}. If the user does not talk about a trip, answer {}.' },
    { role: "user", content: recent }] });
  const raw = ex && ex.response;
  let q = raw && typeof raw === "object" ? raw : null;
  if (!q) {
    const m = String(raw || "").match(/\{[\s\S]*\}/);
    try { q = m ? JSON.parse(m[0].replace(/:\s*true if[^,}]*/g, ":true")) : null; } catch { q = null; }
  }
  log("extract", raw, q);
  if (!q || !q.from || !q.to) return "";
  const [o, d] = await Promise.all([iata(q.from), iata(q.to)]);
  log("iata", o, d);
  if (!o || !d || o.code === d.code) return "";
  const dep = q.depart || q.month || "";
  const ret = q.return || (q.month && !q.depart ? q.month : "");
  // Try the exact dates first, then the month, then any date; return trips first, then one-way.
  const tries = [];
  const oneWayFirst = q.oneway === true || q.oneway === "true";
  for (const ow of oneWayFirst ? ["true", "false"] : ["false", "true"]) {
    if (dep) tries.push([ow, dep, ow === "false" ? ret : ""]);
    if (dep && dep.length > 7) tries.push([ow, dep.slice(0, 7), ow === "false" && ret ? ret.slice(0, 7) : ""]);
    tries.push([ow, "", ""]);
  }
  let rows = [], used = null;
  for (const [ow, a, b] of tries) {
    const params = new URLSearchParams({ origin: o.code, destination: d.code, currency: "eur", sorting: "price", limit: "5", one_way: ow, token: env.TP_TOKEN });
    if (a) params.set("departure_at", a);
    if (b) params.set("return_at", b);
    const res = await fetch("https://api.travelpayouts.com/aviasales/v3/prices_for_dates?" + params);
    const js = await res.json().catch(() => ({}));
    rows = (js.data || []).filter((x) => x.price).slice(0, 3);
    log("prices", ow, a, b, res.status, rows.length, js.error || "");
    if (rows.length) { used = { ow, a }; break; }
  }
  const kiwi = tpKiwi(o.code, d.code);
  const search = tpUrl(`https://www.aviasales.com/search/${o.code}${d.code}1`);
  if (!rows.length) return { text: `LIVE FARES: no recent fares found for ${o.name} → ${d.name}. Say so honestly in one sentence and say the search buttons below show today's prices. Do not paste any flight links.`,
    buttons: [[{ text: "🔎 Aviasales", url: search }, { text: "🔎 Kiwi.com", url: kiwi }]] };
  const note = used.a === dep ? "" : (dep ? " (no fares cached for the exact dates the user asked; these are the closest cheapest dates found — say so)" : "");
  const buttons = [];
  const lines = rows.map((x) => {
    const a = (x.departure_at || "").slice(0, 10), b = (x.return_at || "").slice(0, 10);
    const link = tpUrl("https://www.aviasales.com" + (x.link || `/search/${o.code}${a.slice(8, 10)}${a.slice(5, 7)}${d.code}${b.slice(8, 10)}${b.slice(5, 7)}1`));
    const way = used.ow === "true" ? "one-way" : "return, back " + b;
    buttons.push([{ text: `✈️ ${a.slice(8, 10)}.${a.slice(5, 7)}${b && used.ow !== "true" ? "–" + b.slice(8, 10) + "." + b.slice(5, 7) : ""} · €${x.price} · ${x.transfers ? x.transfers + "×🔄" : "direct"}`, url: link }]);
    return `- ${a}, ${way}, ${x.transfers ? x.transfers + " stop(s)" : "direct"}, ${x.airline || ""}: €${x.price} per person`;
  });
  buttons.push([{ text: "🔎 Kiwi.com", url: kiwi }, { text: "🔎 Aviasales", url: search }]);
  const r0 = rows[0], ci = (r0.departure_at || "").slice(0, 10);
  let co = (r0.return_at || "").slice(0, 10);
  if (!co && ci) { const t = new Date(ci + "T12:00:00Z"); t.setUTCDate(t.getUTCDate() + 3); co = t.toISOString().slice(0, 10); }
  buttons.push([{ text: `🏨 ${d.name}: hotels`, url: hotelLink(d.name, ci, co) }]);
  return { buttons, text: `LIVE FARES (real prices from our partner search, per person, may change)${note}. Briefly list the best 2–3 with price and dates, and say that booking buttons and a Kiwi.com comparison are attached below. Do NOT paste any flight links yourself:\n${o.name} → ${d.name}\n` + lines.join("\n") };
}

async function transcribe(env, fileId) {
  const f = await tg(env, "getFile", { file_id: fileId });
  if (!f.ok) return "";
  const buf = await (await fetch(`https://api.telegram.org/file/bot${env.TG_BOT_TOKEN}/${f.result.file_path}`)).arrayBuffer();
  let bin = "";
  const bytes = new Uint8Array(buf);
  for (let i = 0; i < bytes.length; i += 0x8000) bin += String.fromCharCode(...bytes.subarray(i, i + 0x8000));
  const out = await env.AI.run("@cf/openai/whisper-large-v3-turbo", { audio: btoa(bin) });
  return ((out && out.text) || "").trim();
}

async function handle(env, upd) {
  const cb = upd.callback_query;
  if (cb) {
    tg(env, "answerCallbackQuery", { callback_query_id: cb.id });
    const chat = cb.message && cb.message.chat.id;
    if (!chat || !(cb.data || "").startsWith("lang:")) return;
    const lang = HELLO[cb.data.slice(5)] ? cb.data.slice(5) : "en";
    await env.BOT.put("c" + chat, JSON.stringify({ lang, s: String(Date.now()) }));
    await env.BOT.delete("h" + chat);
    await send(env, chat, HELLO[lang], appButton(lang));
    await tg(env, "setChatMenuButton", { chat_id: chat, menu_button: { type: "web_app", text: "Open App", web_app: { url: APP + "?lang=" + lang } } });
    return;
  }
  const m = upd.message;
  if (!m || !m.chat) return;
  const chat = m.chat.id;
  const text = (m.text || "").trim();
  const user = await getUser(env, chat, m.from);

  if (text.startsWith("/start a_")) {
    const route = text.slice(9, 70);
    await env.BOT.put("a" + chat + "_" + route, "0");
    await env.BOT.delete("x" + chat);
    const p = text.split("_");
    const d = (s) => s && s.length === 6 ? `${s.slice(4, 6)}.${s.slice(2, 4)}` : s;
    const t = pick(ALERT_ON, user.lang);
    return send(env, chat, `${t[0]} ${p[1]} → ${p[2]}, ${d(p[3])}–${d(p[4])}.20${(p[4] || "").slice(0, 2)}\n\n${t[1]}`, appButton(user.lang));
  }
  if (text.startsWith("/start")) {
    const rows = [];
    for (let i = 0; i < LANGS.length; i += 3) rows.push(LANGS.slice(i, i + 3).map(([c, n]) => ({ text: n, callback_data: "lang:" + c })));
    await env.BOT.put("c" + chat, JSON.stringify({ lang: user.lang, s: String(Date.now()) }));
    await env.BOT.delete("h" + chat);
    return send(env, chat, "🌍 Choose your language\nВыберите язык · اختر لغتك · 选择语言 · 言語を選択", { inline_keyboard: rows });
  }
  if (text.startsWith("/stopalerts")) {
    await env.BOT.put("x" + chat, "stop");
    return send(env, chat, pick(STOPPED, user.lang));
  }
  if (text) {
    tg(env, "sendChatAction", { chat_id: chat, action: "typing" });
    return ask(env, chat, user, text);
  }
  const fileId = (m.voice && m.voice.file_id) || (m.video_note && m.video_note.file_id) || (m.audio && m.audio.file_id);
  if (fileId) {
    tg(env, "sendChatAction", { chat_id: chat, action: "typing" });
    let heard = "";
    try { heard = await transcribe(env, fileId); } catch (e) { console.log("whisper", String(e)); }
    if (!heard) return send(env, chat, NOVOICE);
    return ask(env, chat, user, heard);
  }
}

async function sha(s) {
  const h = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(s));
  return [...new Uint8Array(h)].map((b) => b.toString(16).padStart(2, "0")).join("");
}

// Price-alert storage for scripts/price_alerts.py
async function store(req, env, url) {
  if (req.headers.get("X-Key") !== await sha(env.TG_BOT_TOKEN)) return new Response("forbidden", { status: 403 });
  if (req.method === "GET") {
    const out = [];
    for (const prefix of ["a", "x"]) {
      let cursor;
      do {
        const page = await env.BOT.list({ prefix, cursor });
        for (const k of page.keys) out.push({ key: k.name, data: { session: (await env.BOT.get(k.name)) || "0" } });
        cursor = page.list_complete ? null : page.cursor;
      } while (cursor);
    }
    return Response.json({ records: out });
  }
  const body = await req.json();
  for (const [k, v] of Object.entries(body.put || {})) await env.BOT.put(k, String(v));
  for (const k of body.delete || []) await env.BOT.delete(k);
  return Response.json({ ok: true });
}

export default {
  async fetch(req, env, ctx) {
    const url = new URL(req.url);
    if (url.pathname === "/store") return store(req, env, url);
    if (url.pathname === "/debug-partners") return new Response(await partnerLinks(env).catch((e) => "ERR " + e));
    if (url.pathname === "/debug-fares") { // diagnostics only: shows how a message is turned into a fare search (no secrets)
      const q = (url.searchParams.get("q") || "").slice(0, 200);
      const trace = [];
      const out = await liveFares(env, [], q, (...a) => trace.push(a)).catch((e) => "ERR " + e);
      if (out && out.buttons) out.buttons = out.buttons.map((r) => r.map((b) => b.text));
      return Response.json({ trace, out });
    }
    if (url.pathname === "/tg" && req.method === "POST") {
      const secret = (await sha(env.TG_BOT_TOKEN)).slice(0, 32);
      if (req.headers.get("X-Telegram-Bot-Api-Secret-Token") !== secret) return new Response("forbidden", { status: 403 });
      const upd = await req.json();
      ctx.waitUntil(handle(env, upd).catch((e) => console.log("handle", String(e))));
      return new Response("ok");
    }
    return new Response("Tripwise bot is running.");
  },
};
