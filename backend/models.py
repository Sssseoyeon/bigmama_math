from sqlalchemy import Column, Integer, String, Date, Time, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func
from backend.database import Base

class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    parent_phone = Column(String, nullable=False)

class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    date = Column(Date, nullable=False)
    status = Column(String, nullable=False)  # present / absent
    check_in = Column(Time, nullable=True)
    check_out = Column(Time, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint("student_id", "date", name="uix_student_date"),
    )
