from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# SQLite DB 파일 경로
SQLALCHEMY_DATABASE_URL = "sqlite:///./bigmama.db"

# DB 엔진 생성
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}  # SQLite 필수 옵션
)

# 세션 생성기
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# 모델들이 상속받을 Base
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
