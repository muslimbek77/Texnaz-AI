from datetime import datetime, timezone
import hashlib
import hmac
import json
import os
import re
import secrets
import sqlite3
import time

from fastapi import Depends, FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

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

DATABASE_PATH = os.getenv("DATABASE_PATH", "/tmp/texnaz-ai.sqlite3")
SETUP_TOKEN = os.getenv("ADMIN_SETUP_TOKEN", "")
COOKIE_SECURE = os.getenv("COOKIE_SECURE", "false").lower() in {"1", "true", "yes"}
SESSION_COOKIE = "texnaz_session"
SESSION_TTL = 7 * 24 * 60 * 60
PASSWORD_ITERATIONS = 310_000
DEFAULT_SETTINGS = {"notifications_enabled": True, "auto_refresh_seconds": 60}


def connect_db():
    os.makedirs(os.path.dirname(DATABASE_PATH) or ".", exist_ok=True)
    connection = sqlite3.connect(DATABASE_PATH, timeout=10)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def initialize_database():
    with connect_db() as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                username TEXT UNIQUE,
                email TEXT NOT NULL UNIQUE,
                password_salt TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS sessions (
                token_hash TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                expires_at REAL NOT NULL
            );
            CREATE TABLE IF NOT EXISTS user_settings (
                user_id INTEGER PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
                preferences TEXT NOT NULL
            );
            """
        )
        columns = {row[1] for row in connection.execute("PRAGMA table_info(users)")}
        if "username" not in columns:
            connection.execute("ALTER TABLE users ADD COLUMN username TEXT")
        connection.execute("CREATE UNIQUE INDEX IF NOT EXISTS users_username_unique ON users(username)")


initialize_database()


def normalize_email(email: str) -> str:
    normalized = email.strip().lower()
    if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", normalized):
        raise HTTPException(status_code=422, detail="Email manzili noto‘g‘ri")
    return normalized


def password_hash(password: str, salt: bytes) -> str:
    return hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, PASSWORD_ITERATIONS
    ).hex()


def user_payload(row):
    return {"id": row["id"], "full_name": row["full_name"], "username": row["username"], "email": row["email"]}


def session_user(token: str | None):
    if not token:
        return None
    now = time.time()
    token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
    with connect_db() as connection:
        row = connection.execute(
            """SELECT users.id, users.full_name, users.username, users.email, sessions.expires_at
               FROM sessions JOIN users ON users.id = sessions.user_id
               WHERE sessions.token_hash = ?""",
            (token_hash,),
        ).fetchone()
        if row and row["expires_at"] <= now:
            connection.execute("DELETE FROM sessions WHERE token_hash = ?", (token_hash,))
            return None
        return user_payload(row) if row else None


def require_user(request: Request):
    user = session_user(request.cookies.get(SESSION_COOKIE))
    if not user:
        raise HTTPException(status_code=401, detail="Tizimga qayta kiring")
    return user


def issue_session(response: Response, user_id: int):
    token = secrets.token_urlsafe(32)
    expires_at = time.time() + SESSION_TTL
    token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
    with connect_db() as connection:
        connection.execute(
            "INSERT INTO sessions(token_hash, user_id, expires_at) VALUES (?, ?, ?)",
            (token_hash, user_id, expires_at),
        )
    response.set_cookie(
        SESSION_COOKIE,
        token,
        max_age=SESSION_TTL,
        httponly=True,
        secure=COOKIE_SECURE,
        samesite="lax",
        path="/",
    )


class SetupPayload(BaseModel):
    full_name: str = Field(min_length=2, max_length=100)
    username: str = Field(min_length=3, max_length=32, pattern=r"^[a-zA-Z0-9_.-]+$")
    email: str = Field(min_length=5, max_length=254)
    password: str = Field(min_length=8, max_length=128)
    setup_token: str = Field(min_length=16, max_length=256)


class LoginPayload(BaseModel):
    identifier: str = Field(min_length=1, max_length=254)
    password: str


class AccountPayload(BaseModel):
    full_name: str = Field(min_length=2, max_length=100)
    email: str = Field(min_length=5, max_length=254)


class PasswordPayload(BaseModel):
    current_password: str
    new_password: str = Field(min_length=8, max_length=128)


class SettingsPayload(BaseModel):
    notifications_enabled: bool = True
    auto_refresh_seconds: int = Field(default=60, ge=0, le=300)


def get_settings(user_id: int):
    with connect_db() as connection:
        row = connection.execute(
            "SELECT preferences FROM user_settings WHERE user_id = ?", (user_id,)
        ).fetchone()
    if not row:
        return DEFAULT_SETTINGS.copy()
    return {**DEFAULT_SETTINGS, **json.loads(row["preferences"])}

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


@app.get("/api/auth/status")
def auth_status(request: Request):
    with connect_db() as connection:
        has_users = connection.execute("SELECT 1 FROM users LIMIT 1").fetchone() is not None
    user = session_user(request.cookies.get(SESSION_COOKIE))
    return {"setup_required": not has_users, "user": user}


@app.post("/api/auth/setup")
def setup_account(payload: SetupPayload, response: Response):
    if not SETUP_TOKEN or not hmac.compare_digest(payload.setup_token, SETUP_TOKEN):
        raise HTTPException(status_code=403, detail="Boshlang‘ich sozlash tokeni noto‘g‘ri")
    email = normalize_email(payload.email)
    salt = secrets.token_bytes(16)
    with connect_db() as connection:
        connection.execute("BEGIN IMMEDIATE")
        if connection.execute("SELECT 1 FROM users LIMIT 1").fetchone():
            raise HTTPException(status_code=409, detail="Hisob avval yaratilgan")
        cursor = connection.execute(
            """INSERT INTO users(full_name, username, email, password_salt, password_hash, created_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (
                payload.full_name.strip(), payload.username.lower(), email, salt.hex(),
                password_hash(payload.password, salt), datetime.now(timezone.utc).isoformat(),
            ),
        )
        user_id = cursor.lastrowid
        connection.execute(
            "INSERT INTO user_settings(user_id, preferences) VALUES (?, ?)",
            (user_id, json.dumps(DEFAULT_SETTINGS)),
        )
    issue_session(response, user_id)
    return {"user": {"id": user_id, "full_name": payload.full_name.strip(), "username": payload.username.lower(), "email": email}}


@app.post("/api/auth/login")
def login(payload: LoginPayload, response: Response):
    identifier = payload.identifier.strip().lower()
    with connect_db() as connection:
        row = connection.execute("SELECT * FROM users WHERE username = ? OR email = ?", (identifier, identifier)).fetchone()
    if not row or not hmac.compare_digest(
        password_hash(payload.password, bytes.fromhex(row["password_salt"])), row["password_hash"]
    ):
        raise HTTPException(status_code=401, detail="Email yoki parol noto‘g‘ri")
    issue_session(response, row["id"])
    return {"user": user_payload(row)}


@app.post("/api/auth/logout")
def logout(request: Request, response: Response):
    token = request.cookies.get(SESSION_COOKIE)
    if token:
        token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
        with connect_db() as connection:
            connection.execute("DELETE FROM sessions WHERE token_hash = ?", (token_hash,))
    response.delete_cookie(SESSION_COOKIE, path="/", secure=COOKIE_SECURE, httponly=True, samesite="lax")
    return {"status": "ok"}


@app.get("/api/auth/me")
def auth_me(user=Depends(require_user)):
    return {"user": user}


@app.put("/api/account")
def update_account(payload: AccountPayload, user=Depends(require_user)):
    email = normalize_email(payload.email)
    full_name = payload.full_name.strip()
    try:
        with connect_db() as connection:
            connection.execute(
                "UPDATE users SET full_name = ?, email = ? WHERE id = ?",
                (full_name, email, user["id"]),
            )
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=409, detail="Bu email boshqa hisobda ishlatilgan")
    return {"user": {**user, "full_name": full_name, "email": email}}


@app.put("/api/account/password")
def update_password(payload: PasswordPayload, user=Depends(require_user)):
    with connect_db() as connection:
        row = connection.execute("SELECT * FROM users WHERE id = ?", (user["id"],)).fetchone()
        if not row or not hmac.compare_digest(
            password_hash(payload.current_password, bytes.fromhex(row["password_salt"])),
            row["password_hash"],
        ):
            raise HTTPException(status_code=400, detail="Joriy parol noto‘g‘ri")
        salt = secrets.token_bytes(16)
        connection.execute(
            "UPDATE users SET password_salt = ?, password_hash = ? WHERE id = ?",
            (salt.hex(), password_hash(payload.new_password, salt), user["id"]),
        )
        connection.execute("DELETE FROM sessions WHERE user_id = ?", (user["id"],))
    return {"status": "ok", "reauthenticate": True}


@app.get("/api/settings")
def read_settings(user=Depends(require_user)):
    return get_settings(user["id"])


@app.put("/api/settings")
def save_settings(payload: SettingsPayload, user=Depends(require_user)):
    preferences = payload.model_dump()
    with connect_db() as connection:
        connection.execute(
            """INSERT INTO user_settings(user_id, preferences) VALUES (?, ?)
               ON CONFLICT(user_id) DO UPDATE SET preferences = excluded.preferences""",
            (user["id"], json.dumps(preferences)),
        )
    return preferences


@app.get("/api/vehicles")
def vehicles(status: str | None = None, user=Depends(require_user)):
    if status:
        return [vehicle for vehicle in VEHICLES if vehicle["status"] == status]
    return VEHICLES


@app.get("/api/alerts")
def alerts(user=Depends(require_user)):
    return ALERTS


@app.get("/api/maintenance")
def maintenance(user=Depends(require_user)):
    return MAINTENANCE


@app.get("/api/reports")
def reports(user=Depends(require_user)):
    return {"period": "14–20 oktabr 2026", "fuel_by_day": FUEL_REPORT}


@app.get("/api/dashboard")
def dashboard(user=Depends(require_user)):
    return {
        "fleet_total": len(VEHICLES),
        "active": sum(vehicle["status"] == "ishlamoqda" for vehicle in VEHICLES),
        "fuel_saved_percent": 12.4,
        "open_alerts": len(ALERTS),
        "daily_fuel_liters": FUEL_REPORT[-1]["liters"],
        "demo_data": True,
    }
