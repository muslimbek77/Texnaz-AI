from datetime import datetime, timezone
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Texnaz AI API", version="0.1.0", description="Texnika va yoqilg‘i monitoring API")
cors_origins = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173"
    ).split(",")
    if origin.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1)(:\d+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

VEHICLES = [
    {"id": "TX-001", "plate": "01 A 777 QA", "name": "CAT 320D ekskavator", "site": "Toshkent — A-380", "fuel": 72, "consumption": 18.4, "norm": 20, "status": "ishlamoqda", "driver": "Jasur Karimov", "updated": "1 daqiqa oldin"},
    {"id": "TX-002", "plate": "01 A 214 QA", "name": "HOWO yuk mashinasi", "site": "Samarqand — 4-obyekt", "fuel": 34, "consumption": 31.2, "norm": 28, "status": "ogohlantirish", "driver": "Akmal Rahimov", "updated": "2 daqiqa oldin"},
    {"id": "TX-003", "plate": "10 B 908 PA", "name": "XCMG GR165 greyder", "site": "Jizzax — M-39", "fuel": 58, "consumption": 16.8, "norm": 18, "status": "ishlamoqda", "driver": "Bekzod Aliyev", "updated": "hozir"},
    {"id": "TX-004", "plate": "25 C 441 OA", "name": "KAMAZ 6520 samosval", "site": "Navoiy — 2-obyekt", "fuel": 19, "consumption": 29.4, "norm": 27, "status": "kritik", "driver": "Dilshod Tursunov", "updated": "4 daqiqa oldin"},
    {"id": "TX-005", "plate": "01 D 550 MA", "name": "LiuGong 856H yuklagich", "site": "Toshkent — A-380", "fuel": 86, "consumption": 12.1, "norm": 14, "status": "to‘xtagan", "driver": "Sardor Ergashev", "updated": "8 daqiqa oldin"},
]

ALERTS = [
    {"id": 1, "severity": "kritik", "title": "Yoqilg‘i keskin kamaydi", "vehicle": "KAMAZ 6520 · 25 C 441 OA", "time": "10:42", "detail": "12 daqiqada 18 litr kamayish qayd etildi"},
    {"id": 2, "severity": "warning", "title": "Me’yordan ortiq sarf", "vehicle": "HOWO yuk mashinasi · 01 A 214 QA", "time": "10:28", "detail": "Joriy sarf me’yordan 11% yuqori"},
    {"id": 3, "severity": "info", "title": "Bo‘sh ishlash vaqti oshdi", "vehicle": "CAT 320D · 01 A 777 QA", "time": "09:56", "detail": "Dvigatel 42 daqiqa davomida bo‘sh ishladi"},
]

MAINTENANCE = [
    {"id": "MX-001", "vehicle": "CAT 320D · 01 A 777 QA", "service": "Moy almashtirish", "due_date": "2026-10-24", "workshop": "Toshkent markaziy ustaxonasi", "status": "Rejalashtirilgan"},
    {"id": "MX-002", "vehicle": "HOWO yuk mashinasi · 01 A 214 QA", "service": "Tormoz tizimini tekshirish", "due_date": "2026-10-20", "workshop": "Samarqand ustaxonasi", "status": "Muddati o‘tgan"},
    {"id": "MX-003", "vehicle": "XCMG GR165 · 10 B 908 PA", "service": "Rejali texnik ko‘rik", "due_date": "2026-10-28", "workshop": "Jizzax ustaxonasi", "status": "Rejalashtirilgan"},
]

FUEL_REPORT = [
    {"day": "14 okt", "liters": 2510}, {"day": "15 okt", "liters": 2635},
    {"day": "16 okt", "liters": 2470}, {"day": "17 okt", "liters": 2780},
    {"day": "18 okt", "liters": 2695}, {"day": "19 okt", "liters": 2732},
    {"day": "20 okt", "liters": 2846},
]


@app.get("/api/health")
def health():
    return {"status": "ok", "service": "texnaz-ai-api", "time": datetime.now(timezone.utc).isoformat()}


@app.get("/api/vehicles")
def vehicles(status: str | None = None):
    if status:
        return [vehicle for vehicle in VEHICLES if vehicle["status"] == status]
    return VEHICLES


@app.get("/api/alerts")
def alerts():
    return ALERTS


@app.get("/api/maintenance")
def maintenance():
    return MAINTENANCE


@app.get("/api/reports")
def reports():
    return {"period": "14–20 oktabr 2026", "fuel_by_day": FUEL_REPORT}


@app.get("/api/dashboard")
def dashboard():
    return {
        "fleet_total": len(VEHICLES),
        "active": sum(vehicle["status"] == "ishlamoqda" for vehicle in VEHICLES),
        "fuel_saved_percent": 12.4,
        "open_alerts": len(ALERTS),
        "daily_fuel_liters": FUEL_REPORT[-1]["liters"],
        "demo_data": True,
    }
