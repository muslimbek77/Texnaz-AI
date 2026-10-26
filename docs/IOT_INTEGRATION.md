# Texnaz AI — IoT integratsiya yo‘riqnomasi

## Hozirgi holat

Dashboard va FastAPI backend demo ma’lumotlar bilan ishlaydi. GPS lokatsiyasi, yoqilg‘i sensori, qurilma autentifikatsiyasi va telemetriya qabul qilish endpointi hozircha ulanmagan. Quyidagi yo‘riqnoma pilot integratsiyani kelishish va amalga oshirish uchun mo‘ljallangan.

## Tavsiya etilgan ma’lumot oqimi

`GPS/yoqilg‘i qurilmasi → ishlab chiqaruvchi platformasi yoki MQTT broker → Texnaz AI ingest API → ma’lumotlar bazasi → dashboard`

Qurilma to‘g‘ridan-to‘g‘ri HTTP yubora olsa, broker o‘rniga HTTPS ingest endpoint ishlatilishi mumkin. Qurilma mobil tarmoq vaqtincha uzilganda o‘lchovlarni navbatda saqlab, aloqa qaytgach qayta yuborishi kerak.

## Pilot boshlanishidan oldin olinadigan ma’lumotlar

1. Qurilma va tracker ishlab chiqaruvchisi, modeli, firmware versiyasi.
2. Protokol: HTTP(S), MQTT yoki vendor API; endpoint/broker, TLS talabi va payload namunasi.
3. Har bir qurilmaning barqaror identifikatori, SIM/operator va ulanish davriyligi.
4. GPS aniqligi va koordinata formati; yoqilg‘i datchigi turi, birliklari, kalibrlash jadvali va o‘lchash xatosi.
5. Dvigatel holati, odometr/soat hisoblagich, yoqilg‘i quyish yoki keskin kamayishni ajratish qoidalari.
6. Pilot texnikalari ro‘yxati: ichki ID, davlat raqami, obyekt, haydovchi va sarf me’yori.
7. Vendor sandbox yoki test qurilma, API kalitlarini xavfsiz uzatish kanali va mas’ul aloqa shaxsi.

API kaliti, parol yoki broker secret'larini chatga yoki Git repozitoriyga yubormang. Deploy vaqtida serverdagi environment/secrets boshqaruvida saqlang.

## Taklif etilayotgan telemetriya payloadi

Bu hozirgi endpoint shartnomasi emas; qurilma namunasi bilan kelishilgach yakuniy schema belgilanadi.

```json
{
  "device_id": "tracker-001",
  "vehicle_id": "TX-001",
  "observed_at": "2026-10-26T08:15:30Z",
  "latitude": 41.3111,
  "longitude": 69.2797,
  "speed_kph": 12.5,
  "ignition": true,
  "fuel_percent": 72.0,
  "fuel_liters": 180.5,
  "odometer_km": 25431.2,
  "engine_hours": 1832.7,
  "sequence": 18422
}
```

`vehicle_id` yoki `device_id` tashqi jadval orqali Texnaz AI texnikasiga bog‘lanishi kerak. Har bir yozuvda UTC vaqt, aniq birliklar va takror yuborishni topishga yordam beruvchi sequence/event ID bo‘lsin. Sensor bermaydigan maydonlarni yubormang.

## Ingest API uchun qabul mezonlari

- HTTPS majburiy; qurilma yoki vendor uchun alohida token/credential va bekor qilish imkoniyati.
- Payload schema va chegaralarni tekshirish; noto‘g‘ri yozuvga tushunarli 4xx javob.
- Takroriy eventni idempotent qabul qilish; kechikkan/offline eventlarni `observed_at` bilan saqlash.
- Server qabul vaqtini alohida yozish, UTC vaqtni normalizatsiya qilish.
- Telemetriyani saqlashdan dashboard KPI hisoblashni ajratish; so‘nggi holat va tarixiy yozuvlarni saqlash.
- Rate limit, audit log, qurilma holati/last-seen, xatolik metrikalari va zaxira nusxa.
- Yoqilg‘i keskin o‘zgarishida darhol hukm chiqarmasdan sensor shovqini, texnika qiyaligi va kalibrlashni hisobga olish.

## Amalga oshirish bosqichlari

1. Vendor hujjati va 1–2 ta haqiqiy payloadni olib schema/protokolni tasdiqlash.
2. 5–10 texnikani ichki ID va datchik kalibrlashi bilan ro‘yxatdan o‘tkazish.
3. Ingest adapter, autentifikatsiya va telemetriya saqlash qatlamini qo‘shish.
4. Bitta test qurilmada GPS, yoqilg‘i, ignition va offline qayta yuborishni solishtirish.
5. Dashboarddagi demo belgilarini olib tashlashdan oldin real ma’lumot bilan qabul sinovini o‘tkazish.
6. Pilotni kengaytirish, ogohlantirish chegaralari va operator jarayonini kelishish.

## Demo deploy

Loyiha ildizida Docker va Docker Compose plugin o‘rnatilgan serverda:

```bash
docker compose up -d --build
docker compose ps
curl http://127.0.0.1:8080/api/health
```

Dashboard `http://SERVER_IP:8080/` manzilida, API health tekshiruvi `/api/health` da bo‘ladi. Portni `WEB_PORT` environment qiymati bilan o‘zgartirish mumkin. Internetga ochiq demo `https://texnaz.kuprikqurilish.uz` manzilida HTTPS reverse proxy orqali beriladi. Dashboard API’lari login sessiyasi bilan himoyalangan; sog‘liq tekshiruvi ochiq. Demo ma’lumotlar real IoT telemetriyasi emas. Haqiqiy qurilmalarni ulashdan oldin ingest API va qurilma autentifikatsiyasini amalga oshiring.
