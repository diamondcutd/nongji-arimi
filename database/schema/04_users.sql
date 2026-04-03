-- 카카오 로그인 + 이메일 로그인 둘 다 지원
-- kakao_id: 카카오 OAuth 로그인용 (nullable — 이메일 가입 사용자는 없음)
-- email + password_hash: 이메일 로그인용 (nullable — 카카오 가입 사용자는 없음)
CREATE TABLE users (
  id                     UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
  kakao_id               VARCHAR(50)  UNIQUE,
  kakao_channel_user_key VARCHAR(100),
  chatbot_activated_at   TIMESTAMP,
  email                  VARCHAR(255) UNIQUE,
  password_hash          VARCHAR(255),
  nickname               VARCHAR(100),
  phone                  VARCHAR(20),
  plan                   VARCHAR(20)  NOT NULL DEFAULT 'free'
                                      CHECK (plan IN ('free', 'basic', 'premium')),
  is_active              BOOLEAN      NOT NULL DEFAULT TRUE,
  created_at             TIMESTAMP    NOT NULL DEFAULT NOW(),
  last_login             TIMESTAMP,

  -- 카카오 또는 이메일 중 하나는 반드시 존재
  CONSTRAINT chk_login_method CHECK (kakao_id IS NOT NULL OR email IS NOT NULL)
);

CREATE INDEX idx_users_kakao_id               ON users(kakao_id);
CREATE INDEX idx_users_kakao_channel_user_key ON users(kakao_channel_user_key);
CREATE INDEX idx_users_email                  ON users(email);
CREATE INDEX idx_users_plan                   ON users(plan);

COMMENT ON COLUMN users.kakao_id               IS '카카오 OAuth ID (로그인용, 카카오 가입 시 필수)';
COMMENT ON COLUMN users.kakao_channel_user_key IS '카카오 채널 챗봇 사용자 키 (알림톡 발송용)';
COMMENT ON COLUMN users.chatbot_activated_at   IS '카카오 채널 추가 시각';
COMMENT ON COLUMN users.email                  IS '이메일 (이메일 로그인용, 알림 수신용)';
COMMENT ON COLUMN users.password_hash          IS 'bcrypt 해시 (이메일 로그인 시 필수)';
