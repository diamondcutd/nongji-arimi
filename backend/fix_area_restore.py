"""
면적 1/10 복원 — fix_area.py가 이미 정확한 데이터를 다시 /10 한 문제 수정
DB의 total_area_sqm을 10배로 복원
"""
import psycopg2

DATABASE_URL = "postgresql://postgres:1234@localhost:5432/nongji"

conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

# 1) listings.total_area_sqm 복원 (×10)
cur.execute("""
    UPDATE listings
    SET total_area_sqm = total_area_sqm * 10
    WHERE total_area_sqm IS NOT NULL
""")
print(f"listings 면적 복원 (×10): {cur.rowcount}건")

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

# 3) 검증 — 군산시 매물 면적 확인
cur.execute("""
    SELECT address_full, total_area_sqm
    FROM listings
    WHERE address_full LIKE '%군산시%' AND status = 'active'
    ORDER BY address_full
    LIMIT 5
""")
print("\n검증 (군산시 매물):")
for row in cur.fetchall():
    print(f"  {row[0]}: {row[1]}㎡")

cur.close()
conn.close()
print("\n완료!")
