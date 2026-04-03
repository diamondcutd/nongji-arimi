# 농지알리미 데이터베이스

## 실행 방법

```bash
# 1. PostgreSQL 실행 중인지 확인
# 2. 마이그레이션 실행
chmod +x database/migrate.sh
./database/migrate.sh
```

## 환경변수

| 변수 | 기본값 | 설명 |
|------|--------|------|
| `DB_NAME` | `nongji` | 데이터베이스 이름 |
| `DATABASE_URL` | `postgresql://postgres:password@localhost:5432/nongji` | 전체 연결 URL |

## 테이블 구조

### 농지 데이터
- `regions` — 행정구역 계층 (도→시군구→읍면동→리)
- `listings` — 매물 원장 (불변)
- `listing_snapshots` — 매물 시계열 (가격·경쟁자 변화 추적)

### 사용자·알림
- `users` — 카카오 로그인 사용자
- `alert_conditions` — 알림 조건
- `notifications` — 알림 발송 이력
- `subscriptions` — 구독 결제

### 카카오 챗봇
- `chat_messages` — 대화 이력 (일지 원재료)
- `user_contexts` — 챗봇 단기 기억

## 삭제 금지 테이블

`listings`, `listing_snapshots`, `notifications`, `chat_messages`는 절대 삭제하지 않습니다.
비활성화는 `status` 컬럼 변경으로만 처리합니다.
