from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import date, datetime

from backend.database import get_db
from backend.models import Attendance, Student, StudentSchedule
from backend.schemas import AttendanceCreate, AttendanceResponse

router = APIRouter(prefix="/attendance", tags=["Attendance"])


# -------------------------
# 학생별 출석 기록
# -------------------------
@router.get("/student/{student_id}", response_model=list[AttendanceResponse])
def get_attendance_by_student(student_id: int, db: Session = Depends(get_db)):
    return (
        db.query(Attendance)
        .filter(Attendance.student_id == student_id)
        .order_by(Attendance.date.desc())
        .all()
    )


# -------------------------
# 오늘 아직 안 온 학생 (문자 대상)
# -------------------------
@router.get("/absent/today")
def get_today_absent_students(db: Session = Depends(get_db)):
    today = date.today()
    now = datetime.now().time()
    weekday = today.weekday()

    result = []

    students = db.query(Student).all()

    for student in students:
        # 오늘 요일 스케줄
        schedule = db.query(StudentSchedule).filter(
            StudentSchedule.student_id == student.id,
            StudentSchedule.weekday == weekday
        ).first()

        if not schedule:
            continue  # 오늘 안 오는 학생

        attendance = db.query(Attendance).filter(
            Attendance.student_id == student.id,
            Attendance.date == today
        ).first()

        if attendance and attendance.check_in:
            continue  # 이미 출석

        if now >= schedule.expected_time:
            result.append({
                "student_id": student.id,
                "name": student.name,
                "parent_phone": student.parent_phone
            })

    return result


# -------------------------
# 오늘 출석 현황
# -------------------------
@router.get("/today")
def get_today_attendance(db: Session = Depends(get_db)):
    today = date.today()
    now = datetime.now().time()
    weekday = today.weekday()

    students = db.query(Student).all()
    result = []

    present = late_or_absent = unchecked = 0

    for student in students:
        attendance = db.query(Attendance).filter(
            Attendance.student_id == student.id,
            Attendance.date == today
        ).first()

        schedule = db.query(StudentSchedule).filter(
            StudentSchedule.student_id == student.id,
            StudentSchedule.weekday == weekday
        ).first()

        if attendance and attendance.check_in:
            status = "present"
            present += 1

        elif schedule and now >= schedule.expected_time:
            status = "late_or_absent"
            late_or_absent += 1

        else:
            status = "unchecked"
            unchecked += 1

        result.append({
            "student_id": student.id,
            "name": student.name,
            "expected_time": schedule.expected_time if schedule else None,
            "check_in": attendance.check_in if attendance else None,
            "status": status
        })

    return {
        "date": today,
        "now": now,
        "summary": {
            "present": present,
            "late_or_absent": late_or_absent,
            "unchecked": unchecked
        },
        "students": result
    }


# -------------------------
# 출석 저장
# -------------------------
@router.post("/", response_model=AttendanceResponse)
def create_or_update_attendance(
    attendance: AttendanceCreate,
    db: Session = Depends(get_db)
):
    record = db.query(Attendance).filter(
        Attendance.student_id == attendance.student_id,
        Attendance.date == attendance.date
    ).first()

    if record:
        record.status = attendance.status
        record.check_in = attendance.check_in
        record.check_out = attendance.check_out
    else:
        record = Attendance(**attendance.dict())
        db.add(record)

    db.commit()
    db.refresh(record)
    return record
