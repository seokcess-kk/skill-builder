@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul
title Blog Post Generator

cd /d "%~dp0"

REM 환경변수 로드: .env 파일 → ~/.bashrc → 시스템 환경변수 순서로 탐색
if exist "%~dp0.env" (
    for /f "usebackq tokens=1,* delims==" %%a in ("%~dp0.env") do (
        set "%%a=%%b"
    )
) else (
    where bash >nul 2>nul
    if !ERRORLEVEL!==0 (
        for /f "tokens=1,* delims==" %%a in ('bash -c "source ~/.bashrc 2>/dev/null && env" 2^>nul') do (
            if "%%a"=="NAVER_CLIENT_ID" set "NAVER_CLIENT_ID=%%b"
            if "%%a"=="NAVER_CLIENT_SECRET" set "NAVER_CLIENT_SECRET=%%b"
            if "%%a"=="GOOGLE_API_KEY" set "GOOGLE_API_KEY=%%b"
        )
    )
)

echo.
echo  ===================================
echo   Blog Post Generator 시작 중...
echo  ===================================
echo.

start http://localhost:8501
streamlit run app/main.py --server.headless true
