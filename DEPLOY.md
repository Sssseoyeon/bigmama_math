# 빅마마 관리 시스템 배포 가이드

## 배포 방법

### 1. 서버 준비 (Linux/Windows)

#### 필수 요구사항
- Python 3.8 이상
- SQLite (Python과 함께 설치됨)
- (선택) Nginx (프록시 서버로 사용)

### 2. 프로젝트 파일 업로드

서버에 프로젝트 폴더 전체를 업로드합니다:
```
Bigmama/
├── backend/
├── frontend/
├── bigmama.db (데이터베이스 파일)
├── requirements.txt
└── DEPLOY.md
```

### 3. Python 환경 설정

#### Linux/Mac:
```bash
# Python 가상환경 생성
python3 -m venv venv
source venv/bin/activate

# 패키지 설치
pip install -r requirements.txt

# Playwright 브라우저 설치 (이미지 생성용)
playwright install chromium
```

#### Windows:
```powershell
# Python 가상환경 생성
python -m venv venv
venv\Scripts\activate

# 패키지 설치
pip install -r requirements.txt

# Playwright 브라우저 설치 (이미지 생성용)
playwright install chromium
```

### 4. 데이터베이스 확인

`bigmama.db` 파일이 있는지 확인하고, 없으면 실행 시 자동으로 생성됩니다.

### 5. 환경 변수 설정 (선택사항)

`.env` 파일을 생성하여 설정할 수 있습니다:
```env
DATABASE_URL=sqlite:///./bigmama.db
SECRET_KEY=your-secret-key-here
```

### 6. 서버 실행

#### 개발 모드 (직접 실행):
```bash
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

#### 프로덕션 모드 (systemd 서비스로 실행 권장):

**Linux systemd 서비스 파일 생성** (`/etc/systemd/system/bigmama.service`):
```ini
[Unit]
Description=Bigmama Management System
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/path/to/Bigmama/backend
Environment="PATH=/path/to/Bigmama/venv/bin"
ExecStart=/path/to/Bigmama/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

**서비스 시작:**
```bash
sudo systemctl enable bigmama
sudo systemctl start bigmama
sudo systemctl status bigmama
```

### 7. Nginx 설정 (선택사항)

프록시 서버로 Nginx를 사용하려면:

**Nginx 설정 파일** (`/etc/nginx/sites-available/bigmama`):
```nginx
server {
    listen 80;
    server_name your-domain.com;

    # 프론트엔드 정적 파일 서빙
    location / {
        root /path/to/Bigmama/frontend;
        try_files $uri $uri/ /index.html;
        index index.html;
    }

    # 백엔드 API 프록시
    location /api {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # 정적 파일 (이미지 등)
    location /static {
        proxy_pass http://127.0.0.1:8000;
    }
}
```

설정 활성화:
```bash
sudo ln -s /etc/nginx/sites-available/bigmama /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 8. 프론트엔드 API URL 수정

`frontend/index.html` 파일에서 API URL을 수정해야 합니다:

```javascript
// 개발 환경
const API = "http://127.0.0.1:8000";

// 프로덕션 환경 (Nginx 사용 시)
const API = "/api";  // 또는 "https://your-domain.com/api"

// 직접 접근 시
const API = "http://your-server-ip:8000";
```

### 9. 방화벽 설정

서버 방화벽에서 포트를 열어야 합니다:
```bash
# Ubuntu/Debian
sudo ufw allow 8000/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# CentOS/RHEL
sudo firewall-cmd --permanent --add-port=8000/tcp
sudo firewall-cmd --permanent --add-port=80/tcp
sudo firewall-cmd --permanent --add-port=443/tcp
sudo firewall-cmd --reload
```

## 데이터베이스 백업

정기적으로 데이터베이스를 백업하는 것을 권장합니다:

```bash
# 백업
cp bigmama.db bigmama_backup_$(date +%Y%m%d).db

# 또는 SQL 덤프
sqlite3 bigmama.db .dump > bigmama_backup_$(date +%Y%m%d).sql
```

## 로그 확인

서버 로그 확인:
```bash
# systemd 사용 시
sudo journalctl -u bigmama -f

# 직접 실행 시
# 터미널에 출력됨
```

## 문제 해결

### 포트가 이미 사용 중일 때
```bash
# 포트 사용 중인 프로세스 확인
lsof -i :8000  # Linux/Mac
netstat -ano | findstr :8000  # Windows

# 다른 포트 사용
uvicorn main:app --host 0.0.0.0 --port 8001
```

### Playwright 브라우저 오류
```bash
playwright install chromium
playwright install-deps
```

### 데이터베이스 권한 오류
```bash
# 데이터베이스 파일 권한 확인
chmod 644 bigmama.db
chmod 755 backend/static/reports
```

## 업데이트 방법

1. 새 버전의 파일로 교체
2. 패키지 업데이트:
   ```bash
   pip install -r requirements.txt --upgrade
   ```
3. 데이터베이스 마이그레이션 실행 (필요시):
   ```bash
   python backend/migrate_consultation.py
   ```
4. 서비스 재시작:
   ```bash
   sudo systemctl restart bigmama
   ```

