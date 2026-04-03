-- 알림 발송 이력 — 삭제 금지
CREATE TABLE notifications (
  id           UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id      UUID        NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  listing_id   UUID        NOT NULL REFERENCES listings(id) ON DELETE CASCADE,
  condition_id UUID        REFERENCES alert_conditions(id) ON DELETE SET NULL,
  channel      VARCHAR(20) NOT NULL CHECK (channel IN ('email', 'kakao', 'sms')),
  status       VARCHAR(20) NOT NULL DEFAULT 'sent'
                           CHECK (status IN ('sent', 'failed', 'pending')),
  failed_reason TEXT,
  sent_at      TIMESTAMP   NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_notifications_user_id    ON notifications(user_id);
CREATE INDEX idx_notifications_listing_id ON notifications(listing_id);
CREATE INDEX idx_notifications_sent_at    ON notifications(sent_at);
CREATE INDEX idx_notifications_status     ON notifications(status);

COMMENT ON TABLE notifications IS '알림 발송 이력 — 삭제 금지';
