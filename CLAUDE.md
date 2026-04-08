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

### UI 디자인 시스템

- **브랜드 컬러**: 청초록 `#10B981` (라이트), `#34D399` (다크)
- **다크모드**: `@media (prefers-color-scheme: dark)` — OS 설정 자동 감지, 전체 페이지 적용
- **폰트**: `'Pretendard', -apple-system, BlinkMacSystemFont, sans-serif` (CDN: jsdelivr)
- **디자인 원칙**: Apple-style 단순함 — 넓은 여백과 호흡, 타이포그래피 중심 계층
- **CTA 버튼**: 카카오 노란색 `#FEE500` 유지 (랜딩), 그린 `var(--green)` (앱 내부)
- **배경**: 라이트 `#FFFFFF` / 다크 `#111827`
- **CSS 변수 체계** (라이트 / 다크):
  - `--green`: `#10B981` / `#34D399`
  - `--green-dark`: `#059669` / `#10B981`
  - `--green-bg`: `#ECFDF5` / `rgba(52,211,153,0.1)`
  - `--bg`: `#FFFFFF` / `#111827`
  - `--card`: `#F9FAFB` / `#1F2937`
  - `--text`: `#111827` / `#F9FAFB`
  - `--sub`: `#6B7280` / `#9CA3AF`
  - `--border`: `#F3F4F6` / `#374151`
  - `--input-border`: `#E5E7EB` / `#374151`

### 인증

- **카카오 로그인 단일** — 이메일/비밀번호 로그인 없음. 카카오 OAuth만 사용
- JWT (python-jose) + HTTPBearer
- 비밀번호 로그인은 필요 시 추가 (현재 미사용)

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
- **놓친 매물 쿼리**: `LATERAL JOIN`으로 최신 스냅샷 사용 (is_first가 아님). deadline 지난 매물은 자동 제외 (`ls.deadline >= :today`)

### 크롤러 필수사항
- 농지은행 URL에 `schOk=true` 파라미터 필수 (없으면 0건)
- `schBizclType`으로 거래유형 필터링
- **100건 제한**: 농지은행은 한 페이지 최대 100건 반환. 시도 총 건수 ≥100이면 시군구별 분할 크롤링 (`scraper.py`에 구현됨)
- **매물 만료 처리**: 크롤링 후 `expire_unseen_listings()`가 DB에서 사라진 매물을 `status='expired'`로 변경 (deadline 경과 즉시, 상시 매물은 3일 미발견 시). `upsert_listing()`이 재발견 시 `active`로 자동 복원

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

## 2026-04-07 작업 이력

### 완료
- **UI 테마 통일**: login.html, register.html, dashboard.html을 오렌지(#F59E0B)→청초록(#10B981)으로 변경. index.html은 유지
- **다크모드 추가**: 4개 전체 페이지에 `@media (prefers-color-scheme: dark)` 적용. CSS 변수 체계 통일
- **이메일 템플릿 그린 테마**: `matcher.py` `build_digest_html()` — 헤더 흰색 배경+로고, 배경 #F9FAFB, 요약배너 #ECFDF5, Pretendard 폰트, 필지수/신청자수 표시 추가, "농지은행에서 보기" 링크
- **매물 만료 처리 시스템 구축**:
  - `crawler/db.py`: `expire_unseen_listings()` 추가 — 크롤링 시 미발견 매물 자동 만료
  - `crawler/main.py`: 크롤링 완료 후 만료 처리 호출
  - `matcher.py`: 놓친 매물 쿼리를 최신 스냅샷 LATERAL JOIN으로 변경 + deadline 필터 추가
  - `expire_stale.py`: DB 일괄 정리 일회성 스크립트 (실행 완료, 삭제 가능)
- **크롤러 100건 제한 해결**: `scraper.py` — 시도별 총 건수 확인 후 ≥100이면 시군구별 분할 크롤링. `_build_url()`에 `sigun_cd` 파라미터 추가, `_parse_page_listings()` 헬퍼 분리

### 미완료 / 확인 필요
- (없음 — 오늘 작업 전부 완료)

## 2026-04-07 추가 작업 이력

### 완료
- **분할 크롤링 테스트 완료**: 100건 이상 시도 6개(경기·충북·충남·전북·전남·경북) 모두 시군구 분할 크롤링 정상 동작 확인
  - 경기(41): 54개 시군구 → 156건
  - 충북(43): 15개 시군구 → 331건
  - 충남(44): 17개 시군구 → 239건
  - 전북(52): 16개 시군구 → 157건
  - 전남(46): 22개 시군구 → 254건
  - 경북(47): 24개 시군구 → 수집 완료
- **matcher 주석 복원**: 크롤링 테스트 후 `crawler/main.py` 87~91번 줄 매칭 엔진 호출 재활성화
- **카카오 로그인 구현 완료**:
  - `backend/app/routers/auth.py` — 이메일/비번 제거, 카카오 OAuth 엔드포인트 2개 추가 (`/kakao/login`, `/kakao/callback`)
  - `frontend/login.html` — 카카오 버튼 전용 페이지로 교체
  - `frontend/dashboard.html` — URL 토큰 자동 저장 처리 추가
  - `backend/requirements.txt` — httpx 추가
  - `.env` — `KAKAO_REST_API_KEY`, `KAKAO_CLIENT_SECRET`, `KAKAO_REDIRECT_URI`, `FRONTEND_URL` 추가
  - 카카오 콘솔: 리다이렉트 URI 등록, 활성화 ON, Client Secret 활성화 확인
  - 로그인 → 동의 → 대시보드 진입까지 전체 플로우 테스트 완료
  - 남은 작업: 동의항목에서 닉네임 필수 설정 (현재 '사용자님'으로 표시)
