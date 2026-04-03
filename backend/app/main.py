import logging
import os
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.database import init_db
from app.routers import auth, conditions, listings, regions, subscriptions
from app.services.scheduler import start_scheduler, stop_scheduler

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    start_scheduler()
    yield
    # Shutdown
    stop_scheduler()


app = FastAPI(
    title="농지알리미 API",
    description="농지은행 매물 알림 서비스",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS 설정: 환경변수 기반 (프로덕션 안전성 + 개발 편의성)
ALLOWED_ORIGINS_STR = os.getenv(
    "ALLOWED_ORIGINS",
    "http://127.0.0.1:5500,http://localhost:5500,http://127.0.0.1:8000,http://localhost:8000"
)
ALLOWED_ORIGINS = [origin.strip() for origin in ALLOWED_ORIGINS_STR.split(",") if origin.strip()]

# 프로덕션에서 "null" 제거 (브라우저에서 origin을 인식할 수 없을 때 "null" 전송되므로 명시적 제거)
ALLOWED_ORIGINS = [origin for origin in ALLOWED_ORIGINS if origin != "null"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(conditions.router, prefix="/conditions", tags=["conditions"])
app.include_router(listings.router, prefix="/listings", tags=["listings"])
app.include_router(regions.router, prefix="/regions", tags=["regions"])
app.include_router(subscriptions.router, prefix="/subscriptions", tags=["subscriptions"])


# ── 프론트엔드 정적 파일 서빙 ──
FRONTEND_DIR = Path(__file__).resolve().parent.parent.parent / "frontend"

if FRONTEND_DIR.exists():
    @app.get("/")
    async def serve_index():
        return FileResponse(FRONTEND_DIR / "index.html")

    # /register, /register.html 둘 다 지원 (기존 프론트엔드 호환)
    @app.get("/register")
    @app.get("/register.html")
    async def serve_register():
        return FileResponse(FRONTEND_DIR / "register.html")

    @app.get("/login")
    @app.get("/login.html")
    async def serve_login():
        return FileResponse(FRONTEND_DIR / "login.html")

    @app.get("/dashboard")
    @app.get("/dashboard.html")
    async def serve_dashboard():
        return FileResponse(FRONTEND_DIR / "dashboard.html")

    @app.get("/index.html")
    async def serve_index_html():
        return FileResponse(FRONTEND_DIR / "index.html")

    # 정적 파일 (CSS, JS, 이미지 등) — 가장 마지막에 마운트
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")
else:
    @app.get("/")
    async def root():
        return {"message": "농지알리미 API 서버 가동 중"}
