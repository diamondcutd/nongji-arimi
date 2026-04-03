-- 매물 시계열: 크롤링마다 1행 추가, 절대 삭제 금지
-- price_per_sqm: ㎡당 가격 미리 계산 저장 (나중에 백만 건에서 매번 나누면 DB 죽음)
CREATE TABLE listing_snapshots (
  id              UUID      PRIMARY KEY DEFAULT gen_random_uuid(),
  listing_id      UUID      NOT NULL REFERENCES listings(id) ON DELETE CASCADE,
  price           BIGINT    CHECK (price >= 0),
  price_per_sqm   INTEGER   CHECK (price_per_sqm >= 0),
  applicant_count SMALLINT  DEFAULT 0 CHECK (applicant_count >= 0),
  deadline        DATE,
  is_first        BOOLEAN   NOT NULL DEFAULT FALSE,
  crawled_at      TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_snapshots_listing_id ON listing_snapshots(listing_id);
CREATE INDEX idx_snapshots_crawled_at ON listing_snapshots(crawled_at);
CREATE INDEX idx_snapshots_price_sqm  ON listing_snapshots(price_per_sqm);
CREATE INDEX idx_snapshots_is_first   ON listing_snapshots(is_first) WHERE is_first = TRUE;

COMMENT ON TABLE  listing_snapshots             IS '시계열 스냅샷 — 삭제 금지';
COMMENT ON COLUMN listing_snapshots.price_per_sqm IS '㎡당 가격, 크롤링 시 미리 계산';
