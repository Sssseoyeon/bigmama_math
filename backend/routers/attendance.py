from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import date, datetime, time

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
    
    print(f"🔍 [조회 시작] 오늘 날짜: {today}, 요일: {weekday}")

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

        # 디버깅: 조회된 출석 기록 확인
        if attendance:
            print(f"🟡 [조회] 학생 {student.name} (ID: {student.id}) - date: {attendance.date}, check_in: {attendance.check_in} (type: {type(attendance.check_in)}, is None: {attendance.check_in is None})")
        else:
            print(f"🟡 [조회] 학생 {student.name} (ID: {student.id}) - 출석 기록 없음")

        # 출석 기록이 있고 check_in이 있으면 출석으로 간주 (예정 시간과 관계없이)
        # check_in이 None이 아니면 출석으로 처리
        if attendance and attendance.check_in is not None:
            print(f"🟢 [상태 결정] {student.name} -> present (check_in 있음)")
            status = "present"
            present += 1

        # 출석 기록이 있지만 check_in이 없는 경우 (status가 "absent"인 경우)
        elif attendance and attendance.status == "absent":
            status = "late_or_absent"
            late_or_absent += 1

        # 출석 기록이 없고, 예정 시간이 지났으면 지각/결석으로 간주
        elif schedule and now >= schedule.expected_time:
            status = "late_or_absent"
            late_or_absent += 1

        # 그 외의 경우는 미확인
        else:
            status = "unchecked"
            unchecked += 1

        result.append({
            "student_id": student.id,
            "name": student.name,
            "expected_time": schedule.expected_time.strftime("%H:%M") if schedule and schedule.expected_time else None,
            "check_in": attendance.check_in.strftime("%H:%M") if attendance and attendance.check_in else None,
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
    # 디버깅: 받은 데이터 확인
    print(f"🔵 [저장 시도] student_id: {attendance.student_id}, date: {attendance.date}")
    print(f"🔵 [저장 시도] check_in: {attendance.check_in} (type: {type(attendance.check_in)})")
    print(f"🔵 [저장 시도] status: {attendance.status}")
    
    record = db.query(Attendance).filter(
        Attendance.student_id == attendance.student_id,
        Attendance.date == attendance.date
    ).first()

    if record:
        # 기존 레코드 업데이트
        print(f"🔵 [기존 레코드 업데이트] 업데이트 전 check_in: {record.check_in}")
        record.status = attendance.status
        record.check_in = attendance.check_in
        record.check_out = attendance.check_out
        print(f"🔵 [기존 레코드 업데이트] 업데이트 후 check_in: {record.check_in}")
    else:
        # 새 레코드 생성
        print(f"🔵 [새 레코드 생성] check_in: {attendance.check_in}")
        record = Attendance(**attendance.dict())
        db.add(record)
        print(f"🔵 [새 레코드 생성] 생성 후 check_in: {record.check_in}")

    db.commit()
    db.refresh(record)
    
    # 디버깅: 저장된 값 확인
    print(f"🟢 [저장 완료] student_id: {record.student_id}, check_in: {record.check_in} (type: {type(record.check_in)}, is None: {record.check_in is None})")
    
    return record
