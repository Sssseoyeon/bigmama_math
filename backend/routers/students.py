from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import Student
from backend.schemas import StudentCreate, StudentResponse, StudentUpdate

router = APIRouter(
    prefix="/students",
    tags=["Students"]
)

# 학생 수정
@router.put("/{student_id}", response_model=StudentResponse)
def update_student(
    student_id: int,
    student: StudentUpdate,
    db: Session = Depends(get_db)
):
    db_student = db.query(Student).filter(Student.id == student_id).first()

    if not db_student:
        raise HTTPException(status_code=404, detail="학생 없음")

    if student.name is not None:
        db_student.name = student.name
    if student.grade is not None:
        db_student.grade = student.grade
    if student.parent_phone is not None:
        db_student.parent_phone = student.parent_phone

    db.commit()
    db.refresh(db_student)
    return db_student


# 학생 등록
@router.post("/", response_model=StudentResponse)
def create_student(student: StudentCreate, db: Session = Depends(get_db)):
    new_student = Student(**student.dict())
    db.add(new_student)
    db.commit()
    db.refresh(new_student)
    return new_student


# 학생 목록 조회
@router.get("/", response_model=list[StudentResponse])
def get_students(db: Session = Depends(get_db)):
    return db.query(Student).all()
