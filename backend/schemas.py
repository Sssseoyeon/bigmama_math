from pydantic import BaseModel
from datetime import date, time
from typing import Optional

# --------------------
# 학생 관련
# --------------------

class StudentCreate(BaseModel):
    name: str
    parent_phone: str
    grade: str
    expected_time: time

class StudentUpdate(BaseModel):
    name: Optional[str] = None
    parent_phone: Optional[str] = None
    grade: Optional[str] = None
    expected_time: Optional[time] = None

class StudentResponse(BaseModel):
    id: int
    name: str
    parent_phone: str
    grade: str
    expected_time: time

    class Config:
        from_attributes = True


# --------------------
# 출석 관련
# --------------------

class AttendanceCreate(BaseModel):
    student_id: int
    date: date
    status: str
    check_in: Optional[time] = None
    check_out: Optional[time] = None

class AttendanceResponse(BaseModel):
    id: int
    student_id: int
    date: date
    status: str
    check_in: Optional[time]
    check_out: Optional[time]

    class Config:
        from_attributes = True
