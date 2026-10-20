# Texnaz AI

Texnaz AI — Ko‘prikqurilish AJ texnikasi va yoqilg‘i sarfini kuzatish uchun loyiha. Ushbu boshlang‘ich bosqich TZ hamda taqdimot asosida tuzilgan interaktiv dashboard va FastAPI backend skeletini o‘z ichiga oladi.

## Ishga tushirish

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

API hujjatlari: http://localhost:8000/docs

Hozirgi dashboard demo ma’lumotlardan foydalanadi. IoT qurilmalar, xarita provayderi, Telegram/SMS, 1C va E-Ombor integratsiyalari keyingi bosqichlarda ulanadi.

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
