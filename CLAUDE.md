# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 서비스 개요

농지은행(fbo.or.kr) 매물을 자동 수집하여, 사용자 조건에 맞는 매물을 이메일로 알려주는 구독형 서비스.
발신 이메일: nongji.alimi@gmail.com / 캐릭터: 알리미 (우렁각시 콘셉트)

## 실행 명령어

```bash
# FastAPI 서버 (backend/ 디렉토리에서)
cd backend && py -m uvicorn app.main:app --reload

# 크롤러 수동 실행
cd backend && py -m crawler.main

# 매칭 엔진 수동 실행 (이메일 발송)
cd backend && py matcher.py

# 의존성 설치
cd backend && pip install -r requirements.txt
playwright install chromium

# DB 마이그레이션
chmod +x database/migrate.sh && ./database/migrate.sh
```

## 아키텍처

### 데이터 파이프라인

크롤러(Playwright) → DB 저장 → 매칭 엔진(조건 비교) → 이메일 발송(Gmail SMTP)

- **크롤러** (`backend/crawler/`): APScheduler로 매일 10:00/17:00 실행. 농지은행 페이지를 Playwright+BeautifulSoup으로 파싱
- **매칭 엔진** (`backend/matcher.py`): SQLAlchemy async(asyncpg)로 DB 조회, 사용자 조건과 매물 비교 후 다이제스트 이메일 발송
- **API 서버** (`backend/app/`): FastAPI + psycopg2 raw SQL. 프론트엔드 정적 파일도 직접 서빙

### DB 접근 방식 (혼합 — 주의)

| 모듈 | 드라이버 | SQL 문법 |
|------|---------|---------|
| `backend/app/routers/` | psycopg2 raw SQL | 일반 PostgreSQL |
| `backend/matcher.py` | SQLAlchemy async + asyncpg | **`CAST(:param AS uuid)` 필수** (`::uuid` 금지) |
| `backend/crawler/db.py` | psycopg2 raw SQL | 일반 PostgreSQL |

### 프론트엔드

정적 HTML 파일 (`frontend/*.html`). FastAPI `main.py`에서 `/login`, `/register`, `/dashboard` + `.html` 확장자 둘 다 서빙.

### 인증

JWT (python-jose) + HTTPBearer. 비밀번호는 hashlib.sha256 + secrets (bcrypt 호환성 문제로 교체됨).

## 핵심 규칙 (반드시 준수)

### DB 설계 원칙
- `listings` — 삭제 금지. `status` 컬럼으로만 비활성화
- `listing_snapshots` — 변동 시에만 저장. 중복 스냅샷 금지 (시계열 분석 자산)
- `chat_messages`, `notifications` — 삭제 금지 (발송 이력)

### 데이터 단위
- **DB 가격은 원(won) 단위** — 표시할 때 `/10000`으로 만원 변환
- **면적은 정수 ㎡** — 크롤러 `_parse_area()`로 float 파싱 후 반올림

### matcher.py asyncpg 호환성
- `::uuid`, `::text` 캐스팅 → `CAST(:param AS uuid)` 형식 필수
- `CURRENT_DATE - :days` → Python date 객체로 계산 후 파라미터 전달

### 크롤러 필수사항
- 농지은행 URL에 `schOk=true` 파라미터 필수 (없으면 0건)
- `schBizclType`으로 거래유형 필터링

### conditions.py update 화이트리스트
- `alert_conditions` 테이블에 새 컬럼 추가 시 `ALLOWED_COLUMNS`에도 추가 필수 (SQL Injection 방어)

### 농지은행 상세보기 URL
- `TrdeDetail.do` 사용 금지 (세션/CSRF 필요)
- 반드시 `TrdeList.do` + 시도/시군구 코드 사용
- fbo 코드 ≠ DB 코드 (fbo: 52=전북, 51=강원 / DB: 45=전북, 42=강원) → `FBO_SIDO_MAP`, `FBO_SIGUN_MAP` 참조

### CORS
- `.env`의 `ALLOWED_ORIGINS` 환경변수로 관리

## 농지은행 거래유형 코드

```
매도: D1(맞춤형) A1(수탁) B1(공공임대) C1(경영회생)
임대: D2(맞춤형) A2(수탁) B2(공공임대) C2(경영회생)
```

## DB 테이블 핵심 컬럼

- `alert_conditions.biz_type` — JSONB 배열 (다중 선택), `trade_type` 체크 제약 제거됨
- `listings.is_new` — 테스트 후 반드시 `UPDATE listings SET is_new = FALSE` 복원
- `regions` — 3단 계층 (시도→시군구→읍면동), `level` 1/2/3

## 환경 설정 (.env 필수 키)

```
DATABASE_URL, GMAIL_USER, GMAIL_APP_PASSWORD, ALERT_FROM_NAME, JWT_SECRET, ALLOWED_ORIGINS
```

## 기술 스택

Python 3.14 + FastAPI, Playwright + BeautifulSoup, APScheduler, PostgreSQL 17, psycopg2 + asyncpg(matcher만), JWT(python-jose), Gmail SMTP, uvicorn

## Agent Teams 파일 경계

| Owner | Directories |
|-------|------------|
| Backend | `backend/app/`, `backend/crawler/`, `database/` |
| Frontend | `frontend/*.html` (정적 HTML) |
| Shared (Lead만) | `scripts/`, `docs/` |

각 에이전트는 자기 경계만 수정. 경계를 넘는 작업은 메시지로 요청.
