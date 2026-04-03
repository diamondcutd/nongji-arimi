-- ============================================================
-- users 테이블 마이그레이션: 이메일 로그인 지원 추가
-- pgAdmin에서 실행 — 기존 데이터 유지
-- ============================================================

BEGIN;

-- 1) kakao_id를 nullable로 변경 (이메일 전용 사용자도 가입 가능하게)
ALTER TABLE users ALTER COLUMN kakao_id DROP NOT NULL;

-- 2) 이메일 로그인용 컬럼 추가
--    email 컬럼은 이미 존재하므로 UNIQUE 제약만 추가
DO $$
BEGIN
    -- email에 UNIQUE가 없으면 추가
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conrelid = 'users'::regclass AND conname = 'users_email_key'
    ) THEN
        ALTER TABLE users ADD CONSTRAINT users_email_key UNIQUE (email);
    END IF;
END $$;

-- password_hash 컬럼 추가 (이미 존재하면 무시)
ALTER TABLE users ADD COLUMN IF NOT EXISTS password_hash VARCHAR(255);

-- 3) 카카오 또는 이메일 중 하나는 반드시 존재하도록 CHECK 제약 추가
ALTER TABLE users ADD CONSTRAINT chk_login_method
    CHECK (kakao_id IS NOT NULL OR email IS NOT NULL);

-- 4) email 인덱스 추가 (이미 존재하면 무시)
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

-- 5) 코멘트 업데이트
COMMENT ON COLUMN users.kakao_id      IS '카카오 OAuth ID (로그인용, 카카오 가입 시 필수)';
COMMENT ON COLUMN users.email         IS '이메일 (이메일 로그인용, 알림 수신용)';
COMMENT ON COLUMN users.password_hash IS 'bcrypt 해시 (이메일 로그인 시 필수)';

COMMIT;
