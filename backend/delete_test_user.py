"""1600dayscom@gmail.com 테스트 계정 삭제"""
import psycopg2

DATABASE_URL = "postgresql://postgres:1234@localhost:5432/nongji"
TARGET_EMAIL = "1600dayscom@gmail.com"

conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

# 유저 ID 조회
cur.execute("SELECT id FROM users WHERE email = %s", (TARGET_EMAIL,))
row = cur.fetchone()
if not row:
    print(f"{TARGET_EMAIL} 계정이 없습니다.")
    cur.close()
    conn.close()
    exit()

user_id = row[0]
print(f"삭제 대상: {TARGET_EMAIL} (id: {user_id})")

# 관련 데이터 삭제 (순서: FK 의존성 고려)
cur.execute("DELETE FROM notifications WHERE user_id = %s", (user_id,))
print(f"  notifications 삭제: {cur.rowcount}건")

cur.execute("DELETE FROM alert_conditions WHERE user_id = %s", (user_id,))
print(f"  alert_conditions 삭제: {cur.rowcount}건")

cur.execute("DELETE FROM users WHERE id = %s", (user_id,))
print(f"  users 삭제: {cur.rowcount}건")

conn.commit()
cur.close()
conn.close()
print("완료!")
