"""테스트용: 모든 활성 매물을 is_new = TRUE로 변경"""
import psycopg2

conn = psycopg2.connect("postgresql://postgres:1234@localhost:5432/nongji")
cur = conn.cursor()
cur.execute("UPDATE listings SET is_new = TRUE WHERE status = 'active'")
print(f"is_new 활성화: {cur.rowcount}건")
conn.commit()
cur.close()
conn.close()
