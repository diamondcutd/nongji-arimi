"""
잘못된 notifications 이력 초기화
region_id NULL 버그 시절에 매칭된 오염 데이터 삭제
"""
import psycopg2

DATABASE_URL = "postgresql://postgres:1234@localhost:5432/nongji"

conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

cur.execute("SELECT COUNT(*) FROM notifications")
before = cur.fetchone()[0]
print(f"현재 notifications: {before}건")

cur.execute("DELETE FROM notifications")
deleted = cur.rowcount
conn.commit()

print(f"삭제 완료: {deleted}건 (region_id NULL 버그 시절 오염 데이터)")
print("다음 matcher.py 실행부터 정확한 매칭만 기록됩니다.")

cur.close()
conn.close()
