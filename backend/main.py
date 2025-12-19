from fastapi import FastAPI
from backend.database import Base, engine
from backend import models
from backend.routers import attendance
from backend.routers import students

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(attendance.router)
app.include_router(students.router)
