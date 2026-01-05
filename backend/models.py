from sqlalchemy import Column, Integer, String, Date, Time, DateTime, Boolean, ForeignKey, UniqueConstraint, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from backend.database import Base

class Teacher(Base):
    __tablename__ = "teachers"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False, index=True)
    password = Column(String, nullable=False)  # 해시된 비밀번호
    name = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

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
    
    attendance_status = Column(Text, nullable=True)
    # 예: "출석", "지각", "결석"
    # 👉 자동 저장 (attendance에서 읽어와서 넣을 예정)

    absence_reason = Column(Text, nullable=True)
    # 지각/결석 사유 (선생님 입력)

    follow_up_action = Column(Text, nullable=True)
    # 후속 조치 (전화, 문자, 상담 등)

    makeup_class_note = Column(Text, nullable=True)
    # 보강 관련 메모 (날짜/시간 자유 텍스트)

    exam_result = Column(Text, nullable=True)
    # 시험 결과 요약


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


class Consultation(Base):
    __tablename__ = "consultations"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=True)  # 등록된 학생일 경우만
    student_name = Column(String, nullable=False)  # 학생 이름 (직접 입력)
    student_grade = Column(String, nullable=False)  # 학생 학년 (직접 입력)
    date = Column(Date, nullable=False)
    time = Column(Time, nullable=False)
    parent_name = Column(String, nullable=True)  # 학부모 이름
    content = Column(Text, nullable=True)  # 상담 내용
    notes = Column(Text, nullable=True)  # 추가 메모
    status = Column(String, default="scheduled")  # scheduled, completed, cancelled
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    student = relationship("Student", backref="consultations")
