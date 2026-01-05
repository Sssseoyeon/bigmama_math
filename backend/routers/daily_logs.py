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

    # 3️ 일지가 이미 있으면 할 일만 추가 (업데이트)
    if existing:
        # 기존 일지에 할 일 추가 (중복 방지)
        existing_task_contents = {t.content for t in existing.tasks}  # 기존 할 일 내용 집합
        for task in log.tasks:
            # 같은 내용의 할 일이 이미 있으면 건너뛰기
            if task.content not in existing_task_contents:
                existing.tasks.append(
                    DailyTask(
                        content=task.content
                    )
                )
                existing_task_contents.add(task.content)  # 추가한 내용도 집합에 추가
        # 기타 필드가 있고 빈 문자열이 아니면 업데이트 (할 일만 추가하는 경우는 빈 문자열이므로 업데이트 안함)
        if log.teacher_note is not None and log.teacher_note != "":
            existing.teacher_note = log.teacher_note
        if log.attendance_status is not None and log.attendance_status != "":
            existing.attendance_status = log.attendance_status
        if log.absence_reason is not None and log.absence_reason != "":
            existing.absence_reason = log.absence_reason
        if log.follow_up_action is not None and log.follow_up_action != "":
            existing.follow_up_action = log.follow_up_action
        if log.makeup_class_note is not None and log.makeup_class_note != "":
            existing.makeup_class_note = log.makeup_class_note
        if log.exam_result is not None and log.exam_result != "":
            existing.exam_result = log.exam_result
        
        db.commit()
        db.refresh(existing)
        return existing

    # 4️ DailyLog 생성 (tasks 제외!)
    new_log = DailyLog(
        student_id=log.student_id,
        date=log.date,
        teacher_note=log.teacher_note,

        attendance_status=log.attendance_status,
        absence_reason=log.absence_reason,
        follow_up_action=log.follow_up_action,
        makeup_class_note=log.makeup_class_note,
        exam_result=log.exam_result,

        tasks=[]
    )

    # 5️ Task 하나씩 추가
    for task in log.tasks:
        new_log.tasks.append(
            DailyTask(
                content=task.content
            )
        )

    # 6️ 저장
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
