from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date
from fastapi.responses import FileResponse
import os

from backend.database import get_db
from backend.models import DailyLog, DailyTask, Student
from backend.schemas import DailyLogCreate, DailyLogResponse
from backend.utils.report_image import generate_report_image

router = APIRouter(
    prefix="/daily-logs",
    tags=["Daily Logs"]
)

#  일지 작성
@router.post("/", response_model=DailyLogResponse)
def create_daily_log(log: DailyLogCreate, db: Session = Depends(get_db)):
    # 1️ 학생 존재 확인
    student = db.query(Student).filter(Student.id == log.student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="학생 없음")

    # 2️ 같은 날짜 일지 중복 방지
    existing = db.query(DailyLog).filter(
        DailyLog.student_id == log.student_id,
        DailyLog.date == log.date
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="이미 오늘 일지가 있음")

    # 3️ DailyLog 생성 (tasks 제외!)
    new_log = DailyLog(
        student_id=log.student_id,
        date=log.date,
        teacher_note=log.teacher_note,
        tasks=[]
    )

    # 4️ Task 하나씩 추가
    for task in log.tasks:
        new_log.tasks.append(
            DailyTask(
                content=task.content
            )
        )

    # 5️ 저장
    db.add(new_log)
    db.commit()
    db.refresh(new_log)
    return new_log


#  학생의 일지 목록 조회
@router.get("/student/{student_id}", response_model=list[DailyLogResponse])
def get_logs_by_student(student_id: int, db: Session = Depends(get_db)):
    return (
        db.query(DailyLog)
        .filter(DailyLog.student_id == student_id)
        .order_by(DailyLog.date.desc())
        .all()
    )

# ✅ 이미지 생성 (POST)
@router.post("/{log_id}/image")
def create_log_image(log_id: int, db: Session = Depends(get_db)):
    log = db.query(DailyLog).filter(DailyLog.id == log_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="일지 없음")

    student = db.query(Student).filter(Student.id == log.student_id).first()

    image_url = generate_report_image(student, log)

    return {
        "image_url": image_url,  # "/static/reports/log_1.png"
        "share_text": f"{student.name} 학생 수업 리포트입니다."
    }


# ✅ 이미지 파일 제공 (GET) ← ⭐ 핵심
@router.get("/{log_id}/image-file")
def get_log_image_file(log_id: int):
    image_path = f"backend/static/reports/log_{log_id}.png"

    if not os.path.exists(image_path):
        raise HTTPException(status_code=404, detail="이미지 없음")

    return FileResponse(
        image_path,
        media_type="image/png"
    )
