# Agent Teams 실행 가이드 — Phase 2: 1단계 안정화

> 이 가이드를 따라 Claude Code에서 Agent Teams 첫 실행을 합니다.

---

## 사전 확인

```powershell
# PowerShell에서 확인
cd C:\Users\win\Desktop\workspace\test\nongji-alert
claude --version   # 2.1.32 이상 필요 (현재 2.1.89 ✅)
git --version      # 정상 작동 확인 ✅
```

---

## Step 1: Claude Code 실행

```powershell
cd C:\Users\win\Desktop\workspace\test\nongji-alert
claude
```

Claude Code가 열리면 CLAUDE.md를 자동으로 읽습니다.
`.claude/settings.json`의 `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` 설정도 자동 적용됩니다.

---

## Step 2: Plan Mode 진입

Claude Code가 열리면 **Shift+Tab**을 눌러 Plan Mode로 전환하세요.
그리고 아래 프롬프트를 그대로 붙여넣으세요:

```
1단계 안정화 작업을 Agent Teams로 병렬 실행해줘.

3개의 Teammate를 각각 Git Worktree로 격리해서 스폰해줘:

[Backend Agent]
- backend/ 파일들에서 남아있는 datetime.utcnow() 를 모두 찾아서 datetime.now(timezone.utc)로 교체
- from datetime import timezone 임포트 확인
- 대상 파일: backend/app/, backend/crawler/, backend/matcher.py 전체 검색
- matcher.py는 이미 from datetime import UTC 사용 중이므로 건드리지 말 것
- 수정 후 py -c "from app.main import app" 로 import 에러 확인

[Frontend Agent]  
- frontend/dashboard.html에서 조건 추가 폼 제출 시 클라이언트 사이드 빈 조건 방지 검증 강화
- 현재는 거래유형(biz_type)만 체크하는데, 서버와 동일하게 "최소 1개 필터 필수" 검증 추가
- 검증 항목: region_id, land_category, biz_type, area_min, area_max, price_max 중 1개 이상
- 거래유형 미선택이어도 다른 필터가 있으면 통과하도록 로직 수정
- alert()으로 사용자에게 안내 메시지

[Test/QA Agent]
- tests/ 디렉토리에 pytest 테스트 파일 생성
- tests/test_matcher_fields.py: matches_fields() 함수 단위 테스트 (biz_type 매칭, 가격/면적 필터)
- tests/test_conditions_validation.py: 빈 조건 방지 API 테스트 (FastAPI TestClient 사용)
- tests/test_crawler_parser.py: _parse_area(), _parse_deadline(), _resolve_biz_type_code() 단위 테스트

Lead인 너는 위임만 하고 직접 코드를 수정하지 마. Delegate Mode로 운영해.
각 Agent 작업 완료 후 git commit은 각자 하도록 해.
```

---

## Step 3: Plan 확인 후 실행

Claude가 계획을 보여주면 검토하고 **Tab**을 눌러 실행 모드로 전환하세요.
"이 계획대로 진행해줘"라고 입력하면 3개의 Teammate가 스폰됩니다.

---

## Step 4: 진행 확인

작업 중에 확인하고 싶으면:
- 그냥 "진행 상황 알려줘"라고 물어보면 됩니다
- Lead Agent가 각 Teammate의 상태를 확인해서 알려줍니다

---

## Step 5: 완료 후 확인

모든 Teammate가 완료되면:

```powershell
# 커밋 이력 확인
git log --oneline -10

# 변경 파일 확인
git diff --stat HEAD~3

# 테스트 실행
cd backend
py -m pytest tests/ -v
```

---

## 예상 결과

| Agent | 작업 내용 | 예상 시간 |
|-------|----------|----------|
| Backend | datetime 경고 수정 (0~5개 파일) | 2-3분 |
| Frontend | 빈 조건 검증 강화 (1개 파일) | 2-3분 |
| Test/QA | 테스트 3개 파일 생성 | 5-7분 |

---

## 트러블슈팅

### Agent Teams가 활성화 안 될 때
```powershell
# .claude/settings.json 확인
type .claude\settings.json
# CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS이 "1"인지 확인
```

### Git Worktree 에러
```powershell
# worktree 목록 확인
git worktree list
# 남은 worktree 정리
git worktree prune
```

### Teammate가 스폰 안 될 때
Agent Teams 대신 Subagent로 실행해도 됩니다:
```
위 3개 작업을 각각 subagent로 병렬 실행해줘. Git Worktree로 격리해서.
```
