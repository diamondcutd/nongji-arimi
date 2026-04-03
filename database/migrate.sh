#!/bin/bash
set -e

DB_NAME=${DB_NAME:-nongji}
DB_URL=${DATABASE_URL:-postgresql://postgres:password@localhost:5432/$DB_NAME}

echo "🌱 농지알리미 DB 마이그레이션 시작"
echo "→ 대상: $DB_NAME"

createdb $DB_NAME 2>/dev/null || echo "  (DB 이미 존재, 계속)"

for file in database/schema/*.sql; do
  echo "  실행: $file"
  psql $DB_URL -f "$file"
done

echo "  시드: 시도 17개"
psql $DB_URL -f database/seeds/regions_seed.sql

echo ""
echo "✅ 완료! 테이블 목록:"
psql $DB_URL -c "
  SELECT table_name
  FROM information_schema.tables
  WHERE table_schema = 'public'
  ORDER BY table_name;
"
