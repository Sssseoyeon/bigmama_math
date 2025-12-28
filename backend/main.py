from fastapi import FastAPI
from backend.database import Base, engine
from backend import models
from backend.routers import attendance, student_schedules, students
from fastapi.middleware.cors import CORSMiddleware
from backend.routers import daily_logs, daily_tasks
from fastapi.staticfiles import StaticFiles

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 개발용이라 전부 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


Base.metadata.create_all(bind=engine)

app.include_router(attendance.router)
app.include_router(students.router)
app.include_router(daily_logs.router)
app.include_router(daily_tasks.router)
app.include_router(student_schedules.router)
app.mount("/static", StaticFiles(directory="backend/static"), name="static")
