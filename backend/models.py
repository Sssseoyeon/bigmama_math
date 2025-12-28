from sqlalchemy import Column, Integer, String, Date, Time, DateTime, Boolean, ForeignKey, UniqueConstraint, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from backend.database import Base

class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    grade = Column(String, nullable=False)
    parent_phone = Column(String, nullable=True)

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

class DailyLog(Base):
    __tablename__ = "daily_logs"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    date = Column(Date, nullable=False)
    teacher_note = Column(Text, nullable=True)
    

    tasks = relationship(
        "DailyTask",
        back_populates="daily_log",
        cascade="all, delete-orphan"
    )

    @property
    def is_completed(self):
        # 모든 task가 완료되었을 때만 True
        return all(task.is_done for task in self.tasks)


class DailyTask(Base):
    __tablename__ = "daily_tasks"

    id = Column(Integer, primary_key=True, index=True)
    daily_log_id = Column(Integer, ForeignKey("daily_logs.id"), nullable=False)

    content = Column(String, nullable=False)

    grading_done = Column(Boolean, default=False)   # 채점 완료
    review_done = Column(Boolean, default=False)    # 오답 완료
    
    daily_log = relationship(
        "DailyLog",
        back_populates="tasks"
    )
    
    @property
    def is_done(self):
        return self.grading_done and self.review_done      # 최종 완료 여부
    

class StudentSchedule(Base):
    __tablename__ = "student_schedules"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)

    weekday = Column(Integer, nullable=False)
    # 0=월, 1=화, 2=수, 3=목, 4=금, 5=토, 6=일

    expected_time = Column(Time, nullable=False)

    student = relationship("Student", backref="schedules")

    __table_args__ = (
        UniqueConstraint("student_id", "weekday", name="uix_student_weekday"),
    )


class DailyReport(Base):
    __tablename__ = "daily_reports"

    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    date = Column(Date, nullable=False)

    attendance_status = Column(String)
    attendance_reason = Column(Text, nullable=True)

    class_content = Column(Text)
    homework = Column(Text)
    test_type = Column(String, nullable=True)
    score = Column(Integer, nullable=True)

    teacher_comment = Column(Text)

    pdf_path = Column(String, nullable=True)
