@echo off
REM === 농지알리미 Quality Gate ===
REM Agent 태스크 완료 전 자동 실행
REM Exit 0: 통과, Exit 2: 차단 + 피드백

setlocal enabledelayedexpansion
set ERRORS=0

echo === 농지알리미 Quality Gate ===

REM 1. Python 린트 (ruff)
where ruff >nul 2>&1
if %errorlevel% equ 0 (
    echo [1/4] Python 린트 검사...
    ruff check backend\app\ backend\crawler\ --quiet
    if !errorlevel! neq 0 (
        echo [X] Python 린트 실패
        set /a ERRORS+=1
    )
) else (
    echo [1/4] ruff 미설치 — 스킵
)

REM 2. Python 테스트 (pytest)
where pytest >nul 2>&1
if %errorlevel% equ 0 (
    if exist tests\ (
        echo [2/4] Python 테스트...
        pytest tests\ -q --tb=short
        if !errorlevel! neq 0 (
            echo [X] 테스트 실패
            set /a ERRORS+=1
        )
    ) else (
        echo [2/4] tests/ 없음 — 스킵
    )
) else (
    echo [2/4] pytest 미설치 — 스킵
)

REM 3. Frontend 빌드 체크
if exist frontend\package.json (
    echo [3/4] Frontend 타입 체크...
    cd frontend
    call npx tsc --noEmit 2>nul
    if !errorlevel! neq 0 (
        echo [X] TypeScript 타입 체크 실패
        set /a ERRORS+=1
    )
    cd ..
) else (
    echo [3/4] frontend/package.json 없음 — 스킵
)

REM 4. FastAPI import 체크
echo [4/4] FastAPI import 체크...
py -c "from app.main import app; print('OK')" 2>nul
if !errorlevel! neq 0 (
    echo [4/4] FastAPI import 체크 스킵 (backend 디렉토리 아님)
)

echo.
if !ERRORS! gtr 0 (
    echo === [X] Quality Gate 실패: !ERRORS!개 항목 ===
    echo 위 오류를 수정한 후 다시 시도하세요. 1>&2
    exit /b 2
)

echo === [OK] Quality Gate 통과 ===
exit /b 0
