# Texnaz AI

Texnaz AI — Ko‘prikqurilish AJ texnikasi va yoqilg‘i sarfini kuzatish uchun loyiha. Ushbu boshlang‘ich bosqich TZ hamda taqdimot asosida tuzilgan interaktiv dashboard va FastAPI backend skeletini o‘z ichiga oladi.

## Ishga tushirish

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend so‘rovlarni `/api` orqali yuboradi; Vite bu yo‘lni lokalda `http://127.0.0.1:8000` backendiga yo‘naltiradi. Alohida joylashtirilgan backend uchun frontendni build qilishdan oldin `VITE_API_URL` qiymatini backend manziliga o‘rnating (masalan, `https://api.example.com`).

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

API hujjatlari: http://localhost:8000/docs. Boshqa domenlardan foydalanilganda backendda `CORS_ORIGINS` ni vergul bilan ajratilgan frontend originlari bilan sozlang, masalan `https://dashboard.example.com`.

API tekshiruvi: `http://localhost:8000/api/health`. Dashboard, texnikalar, ogohlantirishlar, texnik xizmat va hisobotlar `/api/dashboard`, `/api/vehicles`, `/api/alerts`, `/api/maintenance` va `/api/reports` endpointlaridan olinadi.

Hozirgi dashboard demo ma’lumotlardan foydalanadi. IoT qurilmalar, xarita provayderi, Telegram/SMS, 1C va E-Ombor integratsiyalari keyingi bosqichlarda ulanadi.

## Demo hisob va sozlamalar

Yangi deployda birinchi administrator hisobi yaratiladi. Serverdagi `.env` faylidan `ADMIN_SETUP_TOKEN` qiymatini olib, boshlang‘ich sozlash formasiga kiriting. Tokenni maxfiy saqlang. Ism, login, email va kamida 8 belgili parol tanlang; undan keyin login va parol bilan kirasiz. Demo serverda `texnaz` hisobi oldindan sozlangan.

Dashboard, texnika, ogohlantirishlar, xizmat va hisobot API’lari sessiya cookie’si orqali himoyalangan. `Sozlamalar` sahifasi bildirishnomalar hamda yangilanish oralig‘ini saqlaydi; `Hisob` sahifasida profilni o‘zgartirish, parolni yangilash va chiqish mumkin. Foydalanuvchi va sozlamalar SQLite bazasida Docker volume’da saqlanadi.

## Tuzilma

- `frontend/` — React + Vite web dashboard
- `backend/` — FastAPI API
- `docs/` — loyiha hujjatlari
- `docs/source/` — boshlang‘ich TZ va taqdimot nusxalari

## Boshlang‘ich reja

1. MVP dashboard, texnika parki va ogohlantirishlar
2. PostgreSQL ma’lumotlar modeli va autentifikatsiya/RBAC
3. GPS/yoqilg‘i telemetriyasi ingest API va offline sync
4. Hisobotlar, anomaliya aniqlash va prognoz
5. Tashqi tizimlar hamda Telegram integratsiyalari
