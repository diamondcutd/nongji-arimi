-- 사용자가 설정하는 알림 조건
-- notify_channels: JSONB 배열 — 채널 추가돼도 구조 변경 불필요
-- created_via: 챗봇 대화로 설정했는지 웹으로 설정했는지 추적
CREATE TABLE alert_conditions (
  id               UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id          UUID        NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  label            VARCHAR(100),
  region_id        UUID        REFERENCES regions(id) ON DELETE SET NULL,
  include_children BOOLEAN     NOT NULL DEFAULT TRUE,
  land_category    VARCHAR(20) CHECK (land_category IN ('전', '답', '과수원', '기타')),
  trade_type       VARCHAR(20) CHECK (trade_type IN ('매도', '임대')),
  area_min         INTEGER     CHECK (area_min >= 0),
  area_max         INTEGER     CHECK (area_max >= 0),
  price_max        BIGINT      CHECK (price_max >= 0),
  notify_channels  JSONB       NOT NULL DEFAULT '["kakao"]',
  created_via      VARCHAR(20) DEFAULT 'chatbot'
                               CHECK (created_via IN ('chatbot', 'web', 'api')),
  is_active        BOOLEAN     NOT NULL DEFAULT TRUE,
  created_at       TIMESTAMP   NOT NULL DEFAULT NOW(),

  CONSTRAINT area_range_check CHECK (
    area_min IS NULL OR area_max IS NULL OR area_min <= area_max
  )
);

CREATE INDEX idx_conditions_user_id   ON alert_conditions(user_id);
CREATE INDEX idx_conditions_region_id ON alert_conditions(region_id);
CREATE INDEX idx_conditions_active    ON alert_conditions(is_active) WHERE is_active = TRUE;

COMMENT ON COLUMN alert_conditions.include_children IS 'true=하위 읍면동·리 포함';
COMMENT ON COLUMN alert_conditions.notify_channels  IS '["kakao","email","sms"]';
COMMENT ON COLUMN alert_conditions.created_via      IS '챗봇 대화 vs 웹 설정 추적';
