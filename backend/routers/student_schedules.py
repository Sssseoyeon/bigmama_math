from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import Student, StudentSchedule
from backend.schemas import StudentScheduleCreate, StudentScheduleResponse

router = APIRouter(
    prefix="/students/{student_id}/schedules",
    tags=["Student Schedules"]
)

# 요일별 스케줄 조회
@router.get("/", response_model=list[StudentScheduleResponse])
def get_schedules(student_id: int, db: Session = Depends(get_db)):
    return db.query(StudentSchedule).filter(
        StudentSchedule.student_id == student_id
    ).all()


# 요일별 스케줄 생성/수정
@router.post("/", response_model=StudentScheduleResponse)
def create_or_update_schedule(
    student_id: int,
    schedule: StudentScheduleCreate,
    db: Session = Depends(get_db)
):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="학생 없음")

    existing = db.query(StudentSchedule).filter(
        StudentSchedule.student_id == student_id,
        StudentSchedule.weekday == schedule.weekday
    ).first()

    if existing:
        existing.expected_time = schedule.expected_time
        db.commit()
        db.refresh(existing)
        return existing

    new_schedule = StudentSchedule(
        student_id=student_id,
        weekday=schedule.weekday,
        expected_time=schedule.expected_time
    )
    db.add(new_schedule)
    db.commit()
    db.refresh(new_schedule)
    return new_schedule
