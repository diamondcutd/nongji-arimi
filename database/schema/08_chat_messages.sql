-- 카카오톡 대화 이력 전체 저장
-- 절대 삭제 금지 — 3년 후 일지 모듈의 원재료
-- intent='save_journal'인 행들이 나중에 journal_entries로 이관됨
CREATE TABLE chat_messages (
  id             UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id        UUID         REFERENCES users(id) ON DELETE SET NULL,
  kakao_user_key VARCHAR(100) NOT NULL,
  session_id     VARCHAR(100),
  direction      VARCHAR(10)  NOT NULL CHECK (direction IN ('inbound', 'outbound')),
  message_type   VARCHAR(20)  NOT NULL DEFAULT 'text'
                              CHECK (message_type IN ('text', 'button', 'image', 'location', 'system')),
  content        TEXT         NOT NULL,
  intent         VARCHAR(50),
  -- intent 값:
  -- set_condition  → 알림 조건 설정 중
  -- save_journal   → 일지 저장 요청 ← 나중에 이 행들이 journal로 이관됨
  -- request_info   → 매물 정보 요청
  -- chitchat       → 일상 대화
  -- confirm        → 확인 응답
  extracted_data JSONB,
  -- 자연어에서 추출한 구조화 데이터
  -- 예: {"region_name":"나포면","category":"답","trade":"임대","area_min":1653}
  listing_id     UUID         REFERENCES listings(id) ON DELETE SET NULL,
  sent_at        TIMESTAMP    NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_chat_user_id       ON chat_messages(user_id);
CREATE INDEX idx_chat_kakao_key     ON chat_messages(kakao_user_key);
CREATE INDEX idx_chat_session_id    ON chat_messages(session_id);
CREATE INDEX idx_chat_direction     ON chat_messages(direction);
CREATE INDEX idx_chat_intent        ON chat_messages(intent);
CREATE INDEX idx_chat_listing_id    ON chat_messages(listing_id);
CREATE INDEX idx_chat_sent_at       ON chat_messages(sent_at);

COMMENT ON TABLE  chat_messages                IS '카카오톡 대화 이력 — 삭제 금지, 일지 원재료';
COMMENT ON COLUMN chat_messages.direction      IS 'inbound=사용자→챗봇, outbound=챗봇→사용자';
COMMENT ON COLUMN chat_messages.intent         IS '서버가 파악한 사용자 의도';
COMMENT ON COLUMN chat_messages.extracted_data IS '자연어 → 구조화 데이터 (JSONB)';
