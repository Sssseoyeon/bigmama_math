from fastapi import FastAPI
from backend.database import Base, engine
from backend import models
from backend.routers import attendance, students
from fastapi.middleware.cors import CORSMiddleware


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
