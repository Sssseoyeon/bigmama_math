from pydantic import BaseModel
from datetime import date, time
from typing import List, Optional

# --------------------
# 학생 관련
# --------------------

class StudentCreate(BaseModel):
    name: str
    grade: str
    parent_phone: Optional[str] = None

class StudentUpdate(BaseModel):
    name: Optional[str] = None
    grade: Optional[str] = None
    parent_phone: Optional[str] = None

class StudentResponse(BaseModel):
    id: int
    name: str
    grade: str
    parent_phone: Optional[str] = None

    class Config:
        from_attributes = True

class StudentScheduleCreate(BaseModel):
    weekday: int
    expected_time: time


class StudentScheduleResponse(BaseModel):
    id: int
    weekday: int
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


# --------------------
# 학생 일지
# --------------------
class DailyTaskCreate(BaseModel):
    content: str

class DailyLogCreate(BaseModel):
    student_id: int
    date: date
    tasks: List[DailyTaskCreate]
    teacher_note: Optional[str] = None
    

class DailyLogResponse(BaseModel):
    id: int
    student_id: int
    date: date
    tasks: List[DailyTaskResponse]
    teacher_note: Optional[str]
    is_completed: bool

    class Config:
        from_attributes = True


class DailyTaskResponse(DailyTaskCreate):
    id: int
    content: str
    grading_done: bool
    review_done: bool
    is_done: bool

    class Config:
        from_attributes = True


class DailyTaskUpdate(BaseModel):
    grading_done: Optional[bool] = None
    review_done: Optional[bool] = None