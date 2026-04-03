CREATE TABLE subscriptions (
  id          UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id     UUID        NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  plan        VARCHAR(20) NOT NULL CHECK (plan IN ('basic', 'premium')),
  status      VARCHAR(20) NOT NULL DEFAULT 'active'
                          CHECK (status IN ('active', 'cancelled', 'expired', 'paused')),
  started_at  TIMESTAMP   NOT NULL,
  expires_at  TIMESTAMP,
  payment_key VARCHAR(255),
  amount      INTEGER,
  created_at  TIMESTAMP   NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_subscriptions_user_id    ON subscriptions(user_id);
CREATE INDEX idx_subscriptions_status     ON subscriptions(status);
CREATE INDEX idx_subscriptions_expires_at ON subscriptions(expires_at);

COMMENT ON COLUMN subscriptions.payment_key IS '토스페이먼츠 빌링키';
