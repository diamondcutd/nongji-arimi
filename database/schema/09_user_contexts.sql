-- 챗봇 단기 기억 — 사용자당 1행, 대화마다 덮어씀
-- chat_messages에 이력이 있으니 초기화 가능
CREATE TABLE user_contexts (
  user_id         UUID        PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
  current_step    VARCHAR(50) NOT NULL DEFAULT 'idle',
  -- 단계 값:
  -- idle           → 대기 중
  -- greeting       → 첫 인사
  -- setting_region → 지역 입력 받는 중
  -- setting_type   → 거래유형 입력 받는 중
  -- confirming     → 조건 최종 확인 중
  -- saving_journal → 일지 내용 받는 중
  temp_data       JSONB,
  -- 확정 전 임시 데이터
  -- 예: {"region_name":"군산시","category":null,"trade":"임대"}
  waiting_for     VARCHAR(50),
  -- 다음에 받아야 할 입력:
  -- region / category / trade_type / area / price / memo / confirmation
  last_listing_id UUID        REFERENCES listings(id) ON DELETE SET NULL,
  last_message_at TIMESTAMP,
  updated_at      TIMESTAMP   NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_contexts_step        ON user_contexts(current_step);
CREATE INDEX idx_contexts_waiting_for ON user_contexts(waiting_for);

COMMENT ON TABLE  user_contexts             IS '챗봇 단기 기억 — 초기화 가능';
COMMENT ON COLUMN user_contexts.temp_data   IS '확정 전 임시 입력값';
COMMENT ON COLUMN user_contexts.waiting_for IS '다음에 받아야 할 입력값 종류';
