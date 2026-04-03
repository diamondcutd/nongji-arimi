# 의사결정 기록 (Second Brain)

> 프로젝트의 모든 중요 의사결정을 기록합니다.
> Agent가 "왜 이렇게 했는지" 맥락을 잃지 않도록 합니다.

---

## 작성 규칙

각 결정은 아래 형식을 따릅니다:

```
### [YYYY-MM-DD] 결정 제목
- **상태:** 채택 | 검토중 | 폐기
- **맥락:** 왜 이 결정이 필요했는가
- **결정:** 무엇을 결정했는가
- **대안:** 고려했지만 선택하지 않은 것들
- **결과:** 이 결정으로 인한 영향
```

---

## 결정 목록

### [2026-04-01] 기술 스택 선정
- **상태:** 채택
- **맥락:** 1인 개발자가 농지 정보 알림 서비스를 구축하는데 적합한 스택 필요
- **결정:** Backend: Python 3.14 (FastAPI), Frontend: Next.js (React), DB: PostgreSQL 17, Crawler: Playwright + BeautifulSoup
- **대안:** Django (풀스택이지만 무거움), Go (빠르지만 크롤링 생태계 약함)
- **결과:** FastAPI의 빠른 개발 속도 + Playwright의 안정적 크롤링 확보

### [2026-04-01] psycopg2 raw SQL 채택 (SQLAlchemy ORM 폐기)
- **상태:** 채택
- **맥락:** SQLAlchemy ORM에서 UUID 타입 불일치 에러 반복 발생 (auth/register 500 에러)
- **결정:** 라우터에서 psycopg2 raw SQL 사용, matcher.py에서만 SQLAlchemy async(asyncpg) 유지
- **대안:** SQLAlchemy 타입 매핑 수정 시도 (불안정)
- **결과:** 안정적 DB 접근, 단 matcher.py는 반드시 CAST() 문법 사용 필수

### [2026-04-01] hashlib.sha256 비밀번호 해싱 (bcrypt 폐기)
- **상태:** 채택
- **맥락:** bcrypt Windows 호환성 문제 (설치 실패, 버전 충돌)
- **결정:** hashlib.sha256 + secrets.token_hex(16) 솔트
- **대안:** bcrypt 재시도, argon2
- **결과:** 크로스 플랫폼 호환, 프로덕션 전환 시 argon2 업그레이드 검토 필요

### [2026-04-01] 매칭 엔진 v3 누적 다이제스트
- **상태:** 채택
- **맥락:** 사용자가 매물을 놓치지 않도록 하면서도 이메일 피로감 최소화
- **결정:** 3섹션 구성 (마감 임박 / 새 매물 / 놓친 매물) + 인지심리학 적용
- **대안:** 단순 새 매물 알림 (놓친 매물 재확인 불가)
- **결과:** 손실 회피, 자이가르닉 효과 활용한 행동 유도 이메일

### [2026-04-01] Agent Teams 도입
- **상태:** 채택
- **맥락:** 1인 개발이지만 팀급 생산성이 필요. Frontend/Backend/Test를 병렬로 진행하고 싶음
- **결정:** Claude Code Agent Teams (3명 구성: Backend, Frontend, Test/QA)
- **대안:** 순차 개발 (느림), 외주 (비용), GitHub Copilot Workspace (아직 제한적)
- **결과:** 파일 경계 분리 + Quality Gate Hook으로 품질 유지하며 병렬 개발 가능

### [2026-04-01] Antigravity + Claude Code 이중 IDE 전략
- **상태:** 채택
- **맥락:** Antigravity(Google IDE)와 Claude Code를 함께 사용하여 시너지 극대화
- **결정:** Antigravity에서 Gemini 기반 Plan Review, Claude Code에서 Agent Teams 실행
- **대안:** VS Code + Claude Code만 사용 (Gemini 활용 못함)
- **결과:** 두 AI의 장점을 결합한 멀티 AI 개발 환경

---

## 패턴 라이브러리

> 반복적으로 사용되는 패턴을 기록합니다.

### 농지은행 크롤링 패턴
```
- schOk=true 파라미터 필수
- schBizclType으로 거래유형 필터링
- deadline "상시" → NULL 처리
- _parse_area()로 소수점 면적 파싱
- 변동 시에만 스냅샷 저장 (price/applicant_count/deadline 비교)
```

### DB 가격 처리 패턴
```
- DB 저장: 원(won) 단위 정수
- 화면 표시: price / 10000 → 만원 단위
- _format_price() 함수 사용 필수
```

### matcher.py SQL 패턴
```
- asyncpg 사용 → ::uuid 캐스팅 금지
- 반드시 CAST(:param AS uuid) 형식
- Python date 객체로 날짜 계산 후 전달
```

### Agent 간 통신 패턴
```
1. Agent가 다른 Agent의 영역 작업이 필요할 때:
   → 메시지로 요청 (직접 수정 금지)
2. 인터페이스(타입/스키마)만 공유 파일에 정의
3. 구현은 각자 영역에서 수행
```
