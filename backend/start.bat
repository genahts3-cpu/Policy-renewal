@echo off
echo ============================================
echo  Policy Renewal Agent - Backend Startup
echo ============================================
cd /d "%~dp0"

echo [1/3] Creating data directories...
if not exist "data" mkdir data
if not exist "data\chroma" mkdir data\chroma
if not exist "data\pdfs" mkdir data\pdfs

echo [2/3] Seeding policy knowledge base...
python scripts\seed_policies.py

echo [3/3] Starting FastAPI server...
echo Backend running at: http://localhost:8000
echo API Docs at:        http://localhost:8000/docs
echo.
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
