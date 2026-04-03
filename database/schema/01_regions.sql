-- 행정구역 계층 (도→시군구→읍면동→리), 자기 참조 구조
CREATE TABLE regions (
  id         UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  parent_id  UUID        REFERENCES regions(id) ON DELETE SET NULL,
  code       VARCHAR(10) UNIQUE NOT NULL,
  name       VARCHAR(50) NOT NULL,
  level      SMALLINT    NOT NULL CHECK (level BETWEEN 1 AND 4),
  full_path  TEXT        NOT NULL,
  created_at TIMESTAMP   DEFAULT NOW()
);

CREATE INDEX idx_regions_parent_id ON regions(parent_id);
CREATE INDEX idx_regions_level     ON regions(level);
CREATE INDEX idx_regions_code      ON regions(code);
CREATE INDEX idx_regions_full_path ON regions USING gin(full_path gin_trgm_ops);

COMMENT ON COLUMN regions.level     IS '1=도/광역시, 2=시군구, 3=읍면동, 4=리';
COMMENT ON COLUMN regions.full_path IS '"전북 > 군산시 > 나포면" 형태, 검색·표시용';
