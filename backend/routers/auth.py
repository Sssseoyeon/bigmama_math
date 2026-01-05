from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from datetime import datetime, timedelta
import secrets

router = APIRouter(prefix="/auth", tags=["Authentication"])

# 고정된 계정 정보
FIXED_USERNAME = "bigmama"
FIXED_PASSWORD = "1234"
FIXED_TEACHER_NAME = "선생님"

# 간단한 세션 저장 (실제 운영환경에서는 Redis 등 사용 권장)
active_sessions = {}

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    token: str
    teacher_name: str
    username: str

@router.post("/login", response_model=LoginResponse)
def login(login_data: LoginRequest):
    # 고정된 계정 정보로 확인
    if login_data.username != FIXED_USERNAME or login_data.password != FIXED_PASSWORD:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="아이디 또는 비밀번호가 잘못되었습니다"
        )
    
    # 토큰 생성
    token = secrets.token_urlsafe(32)
    active_sessions[token] = {
        "teacher_id": 1,
        "teacher_name": FIXED_TEACHER_NAME,
        "username": FIXED_USERNAME,
        "expires_at": datetime.now() + timedelta(days=30)  # 30일 유효
    }
    
    return {
        "token": token,
        "teacher_name": FIXED_TEACHER_NAME,
        "username": FIXED_USERNAME
    }

@router.get("/me")
def get_current_user(token: str = None):
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="인증이 필요합니다"
        )
    
    if token not in active_sessions:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="인증이 필요합니다"
        )
    
    session = active_sessions[token]
    if datetime.now() > session["expires_at"]:
        del active_sessions[token]
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="세션이 만료되었습니다"
        )
    
    return {
        "teacher_id": session["teacher_id"],
        "teacher_name": session["teacher_name"],
        "username": session["username"]
    }

@router.post("/logout")
def logout(token: str = None):
    if token and token in active_sessions:
        del active_sessions[token]
    return {"message": "로그아웃되었습니다"}

