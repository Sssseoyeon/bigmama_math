@echo off
echo 빅마마 관리 시스템 서버 시작...
cd backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000
pause

