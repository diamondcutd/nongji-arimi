-- 매물 원장: 최초 정보 보존, 절대 수정 금지
-- 변하는 정보(가격·신청자)는 listing_snapshots에 저장
CREATE TABLE listings (
  id             UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
  listing_key    VARCHAR(200) UNIQUE NOT NULL,
  region_id      UUID         REFERENCES regions(id) ON DELETE SET NULL,
  trade_type     VARCHAR(20)  NOT NULL CHECK (trade_type IN ('매도', '임대')),
  biz_type       VARCHAR(30),
  land_category  VARCHAR(20)  CHECK (land_category IN ('전', '답', '과수원', '기타')),
  address_full   TEXT,
  parcel_count   SMALLINT,
  total_area_sqm INTEGER      CHECK (total_area_sqm > 0),
  detail_url     TEXT,
  first_seen_at  TIMESTAMP    NOT NULL DEFAULT NOW(),
  last_seen_at   TIMESTAMP    NOT NULL DEFAULT NOW(),
  status         VARCHAR(20)  NOT NULL DEFAULT 'active'
                              CHECK (status IN ('active', 'closed', 'expired')),
  is_new         BOOLEAN      NOT NULL DEFAULT TRUE
);

CREATE INDEX idx_listings_region_id   ON listings(region_id);
CREATE INDEX idx_listings_trade_type  ON listings(trade_type);
CREATE INDEX idx_listings_land_cat    ON listings(land_category);
CREATE INDEX idx_listings_status      ON listings(status);
CREATE INDEX idx_listings_first_seen  ON listings(first_seen_at);
CREATE INDEX idx_listings_last_seen   ON listings(last_seen_at);
CREATE INDEX idx_listings_is_new      ON listings(is_new) WHERE is_new = TRUE;
CREATE INDEX idx_listings_address     ON listings USING gin(address_full gin_trgm_ops);

COMMENT ON COLUMN listings.listing_key   IS '농지은행 reqFlndid 파라미터값';
COMMENT ON COLUMN listings.first_seen_at IS '공급 패턴 분석의 핵심';
COMMENT ON COLUMN listings.status        IS '삭제 금지, 상태만 변경';
COMMENT ON COLUMN listings.is_new        IS 'true=알림 미발송';
