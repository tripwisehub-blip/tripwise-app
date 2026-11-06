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
  en: "Hi! I'm Tripwise, your travel assistant for good-value trips anywhere in the world.\n\nTell me where you want to go, when, and how many people are travelling, and I'll suggest the best areas to stay, money-saving tips, tours, car rentals, transfers and more.\n\nYou can write or send a voice message in any language.\n\nWhere are you heading?",
  ru: "Привет! Я Tripwise — помощник для выгодных путешествий по всему миру.\n\nНапишите, куда и когда хотите поехать и сколько вас, — подскажу, где лучше остановиться и как сэкономить, а также экскурсии, аренду авто, трансферы и многое другое.\n\nМожно писать или отправлять голосовые на любом языке.\n\nКуда отправимся?",
  uk: "Привіт! Я Tripwise — помічник для вигідних подорожей по всьому світу.\n\nНапишіть, куди й коли хочете поїхати і скільки вас, — підкажу, де краще зупинитися і як заощадити, а також екскурсії, оренду авто, трансфери та інше.\n\nМожна писати або надсилати голосові будь-якою мовою.\n\nКуди вирушаємо?",
  et: "Tere! Olen Tripwise — sinu abiline soodsateks reisideks üle kogu maailma.\n\nKirjuta, kuhu ja millal soovid minna ning kui palju teid on, ja ma soovitan parimaid piirkondi ööbimiseks, säästunippe, ekskursioone, autorenti, transfeere ja muud.\n\nVõid kirjutada või saata häälsõnumi mis tahes keeles.\n\nKuhu me läheme?",
  fi: "Hei! Olen Tripwise — avustajasi edullisille matkoille ympäri maailmaa.\n\nKerro, minne ja milloin haluat matkustaa ja montako teitä on, niin ehdotan parhaat alueet majoittua, säästövinkit, retket, autonvuokrauksen, kuljetukset ja paljon muuta.\n\nVoit kirjoittaa tai lähettää ääniviestin millä kielellä tahansa.\n\nMinne mennään?",
  lv: "Sveiki! Esmu Tripwise — tavs palīgs izdevīgiem ceļojumiem visā pasaulē.\n\nUzraksti, kurp un kad vēlies doties un cik jūs būsiet, — ieteikšu labākās vietas, kur apmesties, kā ietaupīt, kā arī ekskursijas, auto nomu, transfērus un vairāk.\n\nVari rakstīt vai sūtīt balss ziņas jebkurā valodā.\n\nKurp dodamies?",
  lt: "Sveiki! Aš Tripwise — tavo pagalbininkas naudingoms kelionėms visame pasaulyje.\n\nParašyk, kur ir kada nori keliauti ir kiek jūsų bus, — patarsiu, kur geriausia apsistoti, kaip sutaupyti, taip pat ekskursijas, automobilių nuomą, pervežimus ir daugiau.\n\nGali rašyti ar siųsti balso žinutes bet kuria kalba.\n\nKur keliaujame?",
  pl: "Cześć! Jestem Tripwise — asystent tanich podróży po całym świecie.\n\nNapisz, dokąd i kiedy chcesz jechać i ile osób jedzie, a podpowiem, gdzie najlepiej się zatrzymać i jak zaoszczędzić, a także wycieczki, wynajem auta, transfery i więcej.\n\nMożesz pisać lub wysyłać wiadomości głosowe w dowolnym języku.\n\nDokąd jedziemy?",
  de: "Hallo! Ich bin Tripwise — dein Assistent für günstige Reisen weltweit.\n\nSchreib mir, wohin und wann du reisen möchtest und wie viele ihr seid, und ich empfehle die besten Gegenden zum Übernachten, Spartipps, Touren, Mietwagen, Transfers und mehr.\n\nDu kannst in jeder Sprache schreiben oder Sprachnachrichten senden.\n\nWohin geht's?",
  fr: "Bonjour ! Je suis Tripwise, votre assistant pour voyager malin partout dans le monde.\n\nDites-moi où et quand vous voulez partir et combien vous êtes, et je vous conseille les meilleurs quartiers, des astuces pour économiser, des visites, des voitures de location, des transferts et plus encore.\n\nÉcrivez ou envoyez un vocal dans n'importe quelle langue.\n\nOn part où ?",
  es: "¡Hola! Soy Tripwise, tu asistente para viajar barato por todo el mundo.\n\nDime adónde y cuándo quieres ir y cuántos sois, y te recomendaré las mejores zonas para alojarte, trucos para ahorrar, tours, alquiler de coches, traslados y más.\n\nPuedes escribir o enviar audios en cualquier idioma.\n\n¿A dónde vamos?",
  it: "Ciao! Sono Tripwise, il tuo assistente per viaggi convenienti in tutto il mondo.\n\nDimmi dove e quando vuoi andare e quanti siete, e ti consiglierò le zone migliori dove alloggiare, trucchi per risparmiare, tour, noleggio auto, transfer e altro.\n\nPuoi scrivere o mandare vocali in qualsiasi lingua.\n\nDove andiamo?",
  tr: "Merhaba! Ben Tripwise, dünyanın her yerinde uygun fiyatlı seyahatler için asistanınım.\n\nNereye, ne zaman ve kaç kişi gitmek istediğinizi yazın, kalmak için en iyi bölgeleri, tasarruf ipuçlarını, turları, araç kiralamayı, transferleri ve daha fazlasını önereyim.\n\nHerhangi bir dilde yazabilir veya sesli mesaj gönderebilirsiniz.\n\nNereye gidiyoruz?",
  ar: "مرحبًا! أنا Tripwise، مساعدك للسفر بأفضل الأسعار حول العالم.\n\nأخبرني إلى أين ومتى تريد السفر وكم عددكم، وسأقترح أفضل المناطق للإقامة ونصائح للتوفير والجولات وتأجير السيارات والتنقلات وغير ذلك.\n\nيمكنك الكتابة أو إرسال رسالة صوتية بأي لغة.\n\nإلى أين نذهب؟",
  hi: "नमस्ते! मैं Tripwise हूँ — दुनिया भर में किफ़ायती यात्रा के लिए आपका सहायक।\n\nबताइए आप कहाँ, कब और कितने लोग जाना चाहते हैं — मैं ठहरने के सबसे अच्छे इलाके, पैसे बचाने के टिप्स, टूर, कार रेंटल, ट्रांसफ़र और बहुत कुछ सुझाऊँगा।\n\nआप किसी भी भाषा में लिख सकते हैं या वॉइस मैसेज भेज सकते हैं।\n\nकहाँ चलें?",
  zh: "你好！我是 Tripwise，你的全球高性价比旅行助手。\n\n告诉我你想去哪里、什么时候去、一共几个人，我会推荐最佳住宿区域、省钱技巧、旅游项目、租车、接送服务等。\n\n你可以用任何语言打字或发送语音消息。\n\n我们去哪儿？",
  ja: "こんにちは！Tripwiseです。世界中のお得な旅をサポートするアシスタントです。\n\n行き先、日程、人数を教えてください。おすすめの宿泊エリア、節約のコツ、ツアー、レンタカー、送迎などをご提案します。\n\nどの言語でも、文字でも音声メッセージでもOKです。\n\nどこへ行きますか？",
  ko: "안녕하세요! 저는 Tripwise, 전 세계 가성비 여행을 돕는 여행 도우미예요.\n\n어디로, 언제, 몇 명이 여행하는지 알려주시면 숙소 추천 지역, 절약 팁, 투어, 렌터카, 공항 픽업 등을 추천해 드릴게요.\n\n어떤 언어로든 글이나 음성 메시지로 보내셔도 돼요.\n\n어디로 떠나볼까요?",
  th: "สวัสดี! ฉันคือ Tripwise ผู้ช่วยวางแผนเที่ยวแบบคุ้มค่าทั่วโลก\n\nบอกฉันว่าอยากไปที่ไหน เมื่อไร และไปกี่คน แล้วฉันจะแนะนำย่านที่พักที่ดีที่สุด เคล็ดลับประหยัดเงิน ทัวร์ รถเช่า รถรับส่ง และอื่น ๆ\n\nพิมพ์หรือส่งข้อความเสียงได้ทุกภาษา\n\nเราจะไปไหนกันดี?",
  vi: "Xin chào! Mình là Tripwise, trợ lý du lịch giúp bạn đi khắp thế giới với giá tốt.\n\nHãy cho mình biết bạn muốn đi đâu, khi nào và đi mấy người — mình sẽ gợi ý khu lưu trú tốt nhất, mẹo tiết kiệm, tour, thuê xe, đưa đón và nhiều hơn nữa.\n\nBạn có thể nhắn tin hoặc gửi tin nhắn thoại bằng bất kỳ ngôn ngữ nào.\n\nMình đi đâu nhỉ?",
  id: "Halo! Saya Tripwise, asisten perjalanan hemat ke seluruh dunia.\n\nBeri tahu saya ke mana dan kapan Anda ingin pergi serta berapa orang, dan saya akan menyarankan area menginap terbaik, tips hemat, tur, sewa mobil, transfer, dan lainnya.\n\nAnda bisa menulis atau mengirim pesan suara dalam bahasa apa pun.\n\nMau ke mana kita?",
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

const LINKS = `BOOKING LINKS (use ONLY these exact URLs, never invent or change links):
- Car rental: https://localrent.tpx.lu/EfbBHrJ5 (alternative: https://getrentacar.tpx.lu/iwSAxi5F)
- Tickets, museums, tours and activities: https://tiqets.tpx.lu/AT5p2SuI
- Audio guides and self-guided tours: https://wegotrip.tpx.lu/PFwel7W8
- Airport and city transfers: https://kiwitaxi.tpx.lu/Z8An788O
- eSIM / mobile internet abroad: https://airalo.tpx.lu/PfdD9FnS
- Flights: https://aviasales.tpx.lu/sjlt4H8o
- Compensation for a delayed or cancelled flight: https://airhelp.tpx.lu/65MarJSz
- Hotels: no booking link yet — give advice on areas and what to look for, and suggest comparing prices on the big booking sites.
- The Tripwise app (flight search, budget wheel, price-drop alerts): tell the user to tap the Open App button at the bottom of the chat.
Give at most 2 links per message, each on its own line with a short label written in the reply language. When you share a link, add once per conversation, in the reply language: "Some links are affiliate links — your price stays the same."`;

function systemPrompt(lang) {
  return `You are Tripwise, a friendly travel assistant in Telegram that helps people anywhere in the world find good-value hotels, tours, car rentals, transfers, flights and travel extras for trips to any country. The user has already seen your greeting.

LANGUAGE (very important): Reply in the language of the user's own words in their latest message. Ignore place names, dates and brand names when deciding the language. If the latest message is short, mixed or only data (dates, cities, numbers), keep the language you have been using in this conversation; if there is no earlier conversation, use the user's chosen language, which has the code: ${lang}. Never switch to a language the user has not written in.

COMMANDS: /hotels, /tours, /car, /transfer, /esim mean the user wants help with that topic — start by asking where and when.

FLOW: 1) Find out destination, dates, number of travellers and budget or wishes — ask at most 3 short questions at once, skip what the user already told you. 2) When you have enough, give 3–5 concrete, practical suggestions: which area to stay in and why, what type of accommodation or tour fits, money-saving tips, when prices are lower. 3) When the user is ready to book or asks where to book, give the matching booking link from the list below. 4) Offer related help (a car, a transfer, a tour, an eSIM) in one short line.

${LINKS}

RULES: Never mention the current date or time unless the user asks. Never invent exact prices, hotel names, addresses or availability — give general guidance and tell the user to check current prices. Plain text only, no Markdown symbols like ** or #. Keep answers under 150 words. Be warm and concise, and write naturally and correctly in the reply language.`;
}

const pick = (obj, lang) => obj[lang] || obj.en;

async function tg(env, method, body) {
  const r = await fetch(`https://api.telegram.org/bot${env.TG_BOT_TOKEN}/${method}`, {
    method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
  return r.json().catch(() => ({}));
}

const send = (env, chat, text, markup) => tg(env, "sendMessage", { chat_id: chat, text, disable_web_page_preview: true, ...(markup ? { reply_markup: markup } : {}) });
const appButton = (lang) => ({ inline_keyboard: [[{ text: pick(OPEN, lang), web_app: { url: APP + "?lang=" + lang } }]] });

async function getUser(env, chat, from) {
  const u = await env.BOT.get("c" + chat, "json");
  if (u && u.lang) return u;
  const code = ((from && from.language_code) || "en").slice(0, 2);
  return { lang: HELLO[code] ? code : "en", s: (u && u.s) || "0" };
}

async function ask(env, chat, user, text) {
  const hist = (await env.BOT.get("h" + chat, "json")) || [];
  const messages = [{ role: "system", content: systemPrompt(user.lang) }, ...hist, { role: "user", content: text }];
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
  return send(env, chat, answer);
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
