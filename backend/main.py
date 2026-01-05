from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path

from backend.database import Base, engine
from backend import models
from backend.routers import attendance, student_schedules, students
from backend.routers import daily_logs, daily_tasks, auth, consultations

app = FastAPI()

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프로덕션에서는 특정 도메인으로 제한하는 것을 권장
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 데이터베이스 테이블 생성
Base.metadata.create_all(bind=engine)

# API 라우터 등록 (모든 API는 /api prefix로 등록)
app.include_router(auth.router, prefix="/api")
app.include_router(attendance.router, prefix="/api")
app.include_router(students.router, prefix="/api")
app.include_router(daily_logs.router, prefix="/api")
app.include_router(daily_tasks.router, prefix="/api")
app.include_router(student_schedules.router, prefix="/api")
app.include_router(consultations.router, prefix="/api")

# 정적 파일 서빙 (이미지 등)
app.mount("/static", StaticFiles(directory="backend/static"), name="static")

# 프론트엔드 파일 경로
FRONTEND_DIR = Path(__file__).parent.parent / "frontend"
FRONTEND_INDEX = FRONTEND_DIR / "index.html"

# 루트 경로에서 프론트엔드 HTML 서빙 (API 경로가 아닌 경우)
@app.get("/", response_class=FileResponse)
async def serve_frontend_root():
    """루트 경로에서는 프론트엔드 HTML을 서빙"""
    if FRONTEND_INDEX.exists():
        return FileResponse(FRONTEND_INDEX)
    from fastapi import HTTPException
    raise HTTPException(status_code=404, detail="Frontend file not found")
