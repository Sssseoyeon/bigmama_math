from pydantic import BaseModel
from datetime import date, time
from typing import Optional
from datetime import date, time

class StudentUpdate(BaseModel):
    name: str | None = None
    parent_phone: str | None = None

class AttendanceResponse(BaseModel):
    id: int
    student_id: int
    date: date
    status: str
    check_in: time | None
    check_out: time | None

    class Config:
        from_attributes = True


# 학생 생성 요청용
class StudentCreate(BaseModel):
    name: str
    parent_phone: str

# 학생 응답용
class StudentResponse(BaseModel):
    id: int
    name: str
    parent_phone: str

    class Config:
        from_attributes = True

class AttendanceCreate(BaseModel):
    student_id: int
    date: date
    status: str
    check_in: Optional[time] = None
    check_out: Optional[time] = None

class AttendanceResponse(AttendanceCreate):
    id: int

    class Config:
        from_attributes = True
