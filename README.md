# 빅마마 관리 시스템

학원 선생님들을 위한 학생 출석 관리 및 일지 작성 시스템입니다.

## 주요 기능

- 👨‍🎓 학생 관리 (등록, 조회, 학년별 정렬)
- 📅 출석 관리 (등원/하원 시간 기록, 출석 현황 조회)
- ✅ 할 일 관리 (과제 관리, 채점/오답 체크)
- 📝 일지 작성 (학부모 전송용 이미지 생성)
- 📆 상담 관리 (상담 일정 캘린더, 상담 기록)

## 빠른 시작

### 1. 필수 요구사항
- Python 3.8 이상
- SQLite (Python과 함께 설치됨)

### 2. 설치

```bash
# 가상환경 생성 및 활성화
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# 패키지 설치
pip install -r requirements.txt

# Playwright 브라우저 설치 (이미지 생성용)
playwright install chromium
```

### 3. 서버 실행

#### Windows:
```bash
start_server.bat
```

#### Linux/Mac:
```bash
chmod +x start_server.sh
./start_server.sh
```

#### 또는 직접 실행:
```bash
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000
```

### 4. 접속

브라우저에서 `http://localhost:8000` 접속

- **로그인 정보**:
  - 아이디: `bigmama`
  - 비밀번호: `1234`

## 배포

자세한 배포 가이드는 [DEPLOY.md](DEPLOY.md) 파일을 참고하세요.

## 프로젝트 구조

```
Bigmama/
├── backend/           # FastAPI 백엔드
│   ├── routers/      # API 라우터
│   ├── models.py     # 데이터베이스 모델
│   ├── schemas.py    # Pydantic 스키마
│   └── main.py       # FastAPI 앱 진입점
├── frontend/         # 프론트엔드 (HTML)
│   └── index.html
├── bigmama.db        # SQLite 데이터베이스
├── requirements.txt  # Python 패키지 의존성
└── DEPLOY.md         # 배포 가이드
```

## 주요 API 엔드포인트

- `POST /auth/login` - 로그인
- `GET /students/` - 학생 목록
- `POST /attendance/` - 출석 기록 저장
- `GET /attendance/today` - 오늘 출석 현황
- `POST /daily-logs/` - 일지 생성
- `GET /consultations/` - 상담 목록

자세한 API 문서는 서버 실행 후 `http://localhost:8000/docs`에서 확인할 수 있습니다.

## 라이선스

이 프로젝트는 학원 내부 사용을 위해 개발되었습니다.

