"""
기존 매물 면적 보정 — 10배 뻥튀기 수정
원인: _parse_int가 '4,000.0' → 40000 으로 파싱 (소수점 무시)
수정: total_area_sqm을 1/10로, price_per_sqm 재계산
"""
import psycopg2

DATABASE_URL = "postgresql://postgres:1234@localhost:5432/nongji"

conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

# 1) listings.total_area_sqm 보정
cur.execute("""
    UPDATE listings
    SET total_area_sqm = ROUND(total_area_sqm / 10.0)
    WHERE total_area_sqm IS NOT NULL
""")
print(f"listings 면적 보정: {cur.rowcount}건")

# 2) listing_snapshots.price_per_sqm 재계산
cur.execute("""
    UPDATE listing_snapshots ls
    SET price_per_sqm = CASE
        WHEN l.total_area_sqm > 0 THEN ls.price / l.total_area_sqm
        ELSE NULL
    END
    FROM listings l
    WHERE ls.listing_id = l.id
      AND ls.price IS NOT NULL
""")
print(f"snapshots price_per_sqm 재계산: {cur.rowcount}건")

conn.commit()
cur.close()
conn.close()
print("완료!")
