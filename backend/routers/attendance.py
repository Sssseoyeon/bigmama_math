from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date, datetime
from backend.database import get_db
from backend.models import Attendance, Student
from backend.schemas import AttendanceCreate, AttendanceResponse
from backend.utils.sms import send_sms


router = APIRouter(prefix="/attendance", tags=["Attendance"])

@router.get("/student/{student_id}", response_model=list[AttendanceResponse])
def get_attendance_by_student(student_id: int, db: Session = Depends(get_db)):
    return (
        db.query(Attendance)
        .filter(Attendance.student_id == student_id)
        .order_by(Attendance.date.desc())
        .all()
    )

@router.get("/date/{target_date}", response_model=list[AttendanceResponse])
def get_attendance_by_date(target_date: date, db: Session = Depends(get_db)):
    return (
        db.query(Attendance)
        .filter(Attendance.date == target_date)
        .all()
    )

@router.get("/absent/today")
def get_today_absent_students(db: Session = Depends(get_db)):
    today = date.today()

    # 오늘 출석 기록이 있는 학생 id
    present_student_ids = (
        db.query(Attendance.student_id)
        .filter(Attendance.date == today, Attendance.status == "present")
        .subquery()
    )

    # 오늘 결석 처리된 학생
    absent_records = (
        db.query(Student)
        .outerjoin(
            Attendance,
            (Attendance.student_id == Student.id) &
            (Attendance.date == today)
        )
        .filter(
            (Attendance.status == "absent") | (Attendance.id == None)
        )
        .all()
    )

    return [
        {
            "student_id": s.id,
            "name": s.name,
            "message": f"[학원 알림] {s.name} 학생이 오늘 출석하지 않았습니다."
        }
        for s in absent_records
    ]


@router.get("/today")
def get_today_attendance(db: Session = Depends(get_db)):
    today = date.today()
    now = datetime.now().time()

    students = db.query(Student).all()
    result = []

    present = late_or_absent = unchecked = 0

    for student in students:
        attendance = db.query(Attendance).filter(
            Attendance.student_id == student.id,
            Attendance.date == today
        ).first()

        if attendance and attendance.check_in:
            status = "present"
            present += 1
        else:
            if now >= student.expected_time:
                status = "late_or_absent"
                late_or_absent += 1
            else:
                status = "unchecked"
                unchecked += 1

        result.append({
            "student_id": student.id,
            "name": student.name,
            "expected_time": student.expected_time,
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

    # 결석 시 문자 발송 로그 (지금은 콘솔)
    if attendance.status == "absent":
        print(f"[문자 예정] 학생 {attendance.student_id} 결석")

    return record


@router.post("/absent/today/send-sms")
def send_absent_sms(db: Session = Depends(get_db)):
    today = date.today()

    absent_students = (
        db.query(Student)
        .outerjoin(
            Attendance,
            (Attendance.student_id == Student.id) &
            (Attendance.date == today)
        )
        .filter(
            (Attendance.status == "absent") | (Attendance.id == None)
        )
        .all()
    )

    for s in absent_students:
        message = f"[학원 알림] {s.name} 학생이 오늘 출석하지 않았습니다."
        send_sms(s.parent_phone, message)  # 나중에 학부모 번호로 교체

    return {
        "count": len(absent_students),
        "result": "문자 발송 완료 (콘솔 로그)"
    }
