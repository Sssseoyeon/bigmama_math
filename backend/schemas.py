from pydantic import BaseModel
from datetime import date, time, datetime
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

class DailyTaskUpdate(BaseModel):
    content: Optional[str] = None
    grading_done: Optional[bool] = None
    review_done: Optional[bool] = None


# --------------------
# 상담 관련
# --------------------

class ConsultationCreate(BaseModel):
    student_id: Optional[int] = None  # 등록된 학생일 경우만
    student_name: str  # 학생 이름 (직접 입력)
    student_grade: str  # 학생 학년 (직접 입력)
    date: date
    time: time
    parent_name: Optional[str] = None
    content: Optional[str] = None
    notes: Optional[str] = None
    status: str = "scheduled"

class ConsultationUpdate(BaseModel):
    student_id: Optional[int] = None
    student_name: Optional[str] = None
    student_grade: Optional[str] = None
    date: Optional[date] = None
    time: Optional[time] = None
    parent_name: Optional[str] = None
    content: Optional[str] = None
    notes: Optional[str] = None
    status: Optional[str] = None

class ConsultationResponse(BaseModel):
    id: int
    student_id: Optional[int] = None
    student_name: str
    student_grade: str
    date: date
    time: time
    parent_name: Optional[str] = None
    content: Optional[str] = None
    notes: Optional[str] = None
    status: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class DailyLogCreate(BaseModel):
    student_id: int
    date: date
    tasks: List[DailyTaskCreate]
    teacher_note: Optional[str] = None

    attendance_status: Optional[str] = None
    # "출석" | "지각" | "결석"
    # 👉 나중에 attendance에서 복사해서 넣을 값

    absence_reason: Optional[str] = None
    # 지각 / 결석 사유 (선생님 입력)

    follow_up_action: Optional[str] = None
    # 후속 조치 (전화, 문자, 상담 등)

    makeup_class_note: Optional[str] = None
    # 보강 메모 (날짜/시간 자유 텍스트)

    exam_result: Optional[str] = None
    # 시험 결과 요약
    

class DailyTaskResponse(DailyTaskCreate):
    id: int
    content: str
    grading_done: bool
    review_done: bool
    is_done: bool

    class Config:
        from_attributes = True


class DailyLogResponse(BaseModel):
    id: int
    student_id: int
    date: date
    tasks: List[DailyTaskResponse]
    teacher_note: Optional[str]
    is_completed: bool

    attendance_status: Optional[str] = None
    # "출석" | "지각" | "결석"
    # 👉 나중에 attendance에서 복사해서 넣을 값

    absence_reason: Optional[str] = None
    # 지각 / 결석 사유 (선생님 입력)

    follow_up_action: Optional[str] = None
    # 후속 조치 (전화, 문자, 상담 등)

    makeup_class_note: Optional[str] = None
    # 보강 메모 (날짜/시간 자유 텍스트)

    exam_result: Optional[str] = None

    class Config:
        from_attributes = True
