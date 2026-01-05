from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date, datetime
from typing import List, Optional

from backend.database import get_db
from backend.models import Consultation, Student
from backend.schemas import ConsultationCreate, ConsultationUpdate, ConsultationResponse

router = APIRouter(
    prefix="/consultations",
    tags=["Consultations"]
)

@router.post("/", response_model=ConsultationResponse)
def create_consultation(
    consultation: ConsultationCreate,
    db: Session = Depends(get_db)
):
    try:
        # student_id가 제공된 경우 학생 존재 확인 (선택사항)
        if consultation.student_id:
            student = db.query(Student).filter(Student.id == consultation.student_id).first()
            if not student:
                raise HTTPException(status_code=404, detail="학생 없음")

        # Consultation 객체 생성
        consultation_data = consultation.dict()
        new_consultation = Consultation(**consultation_data)
        db.add(new_consultation)
        db.commit()
        db.refresh(new_consultation)

        # 반환
        result = ConsultationResponse(
            id=new_consultation.id,
            student_id=new_consultation.student_id,
            student_name=new_consultation.student_name,
            student_grade=new_consultation.student_grade,
            date=new_consultation.date,
            time=new_consultation.time,
            parent_name=new_consultation.parent_name,
            content=new_consultation.content,
            notes=new_consultation.notes,
            status=new_consultation.status,
            created_at=new_consultation.created_at,
            updated_at=new_consultation.updated_at
        )
        return result
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"상담 저장 중 오류 발생: {str(e)}")

@router.get("/", response_model=List[ConsultationResponse])
def get_consultations(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Consultation)
    
    if start_date:
        query = query.filter(Consultation.date >= start_date)
    if end_date:
        query = query.filter(Consultation.date <= end_date)
    
    consultations = query.order_by(Consultation.date, Consultation.time).all()
    
    result = []
    for c in consultations:
        result.append(ConsultationResponse(
            id=c.id,
            student_id=c.student_id,
            student_name=c.student_name,
            student_grade=c.student_grade,
            date=c.date,
            time=c.time,
            parent_name=c.parent_name,
            content=c.content,
            notes=c.notes,
            status=c.status,
            created_at=c.created_at,
            updated_at=c.updated_at
        ))
    
    return result

@router.get("/date/{target_date}", response_model=List[ConsultationResponse])
def get_consultations_by_date(
    target_date: date,
    db: Session = Depends(get_db)
):
    consultations = db.query(Consultation).filter(
        Consultation.date == target_date
    ).order_by(Consultation.time).all()
    
    result = []
    for c in consultations:
        result.append(ConsultationResponse(
            id=c.id,
            student_id=c.student_id,
            student_name=c.student_name,
            student_grade=c.student_grade,
            date=c.date,
            time=c.time,
            parent_name=c.parent_name,
            content=c.content,
            notes=c.notes,
            status=c.status,
            created_at=c.created_at,
            updated_at=c.updated_at
        ))
    
    return result

@router.get("/{consultation_id}", response_model=ConsultationResponse)
def get_consultation(
    consultation_id: int,
    db: Session = Depends(get_db)
):
    consultation = db.query(Consultation).filter(
        Consultation.id == consultation_id
    ).first()
    
    if not consultation:
        raise HTTPException(status_code=404, detail="상담 없음")
    
    return ConsultationResponse(
        id=consultation.id,
        student_id=consultation.student_id,
        student_name=consultation.student_name,
        student_grade=consultation.student_grade,
        date=consultation.date,
        time=consultation.time,
        parent_name=consultation.parent_name,
        content=consultation.content,
        notes=consultation.notes,
        status=consultation.status,
        created_at=consultation.created_at,
        updated_at=consultation.updated_at
    )

@router.put("/{consultation_id}", response_model=ConsultationResponse)
def update_consultation(
    consultation_id: int,
    consultation: ConsultationUpdate,
    db: Session = Depends(get_db)
):
    db_consultation = db.query(Consultation).filter(Consultation.id == consultation_id).first()
    
    if not db_consultation:
        raise HTTPException(status_code=404, detail="상담 없음")
    
    if consultation.student_id is not None:
        db_consultation.student_id = consultation.student_id
    if consultation.student_name is not None:
        db_consultation.student_name = consultation.student_name
    if consultation.student_grade is not None:
        db_consultation.student_grade = consultation.student_grade
    if consultation.date is not None:
        db_consultation.date = consultation.date
    if consultation.time is not None:
        db_consultation.time = consultation.time
    if consultation.parent_name is not None:
        db_consultation.parent_name = consultation.parent_name
    if consultation.content is not None:
        db_consultation.content = consultation.content
    if consultation.notes is not None:
        db_consultation.notes = consultation.notes
    if consultation.status is not None:
        db_consultation.status = consultation.status
    
    db.commit()
    db.refresh(db_consultation)
    
    return ConsultationResponse(
        id=db_consultation.id,
        student_id=db_consultation.student_id,
        student_name=db_consultation.student_name,
        student_grade=db_consultation.student_grade,
        date=db_consultation.date,
        time=db_consultation.time,
        parent_name=db_consultation.parent_name,
        content=db_consultation.content,
        notes=db_consultation.notes,
        status=db_consultation.status,
        created_at=db_consultation.created_at,
        updated_at=db_consultation.updated_at
    )

@router.delete("/{consultation_id}")
def delete_consultation(
    consultation_id: int,
    db: Session = Depends(get_db)
):
    db_consultation = db.query(Consultation).filter(Consultation.id == consultation_id).first()
    
    if not db_consultation:
        raise HTTPException(status_code=404, detail="상담 없음")
    
    db.delete(db_consultation)
    db.commit()
    
    return {"message": "상담이 삭제되었습니다"}

