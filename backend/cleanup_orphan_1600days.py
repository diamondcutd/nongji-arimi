"""1600dayscom 탈퇴 후 잔여 고아 데이터 정리"""
import psycopg2

DATABASE_URL = "postgresql://postgres:1234@localhost:5432/nongji"
USER_ID = "24803a10-8083-425e-9e25-3294d3baca9e"

conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

cur.execute("DELETE FROM notifications WHERE user_id = %s", (USER_ID,))
print(f"notifications 삭제: {cur.rowcount}건")

cur.execute("DELETE FROM alert_conditions WHERE user_id = %s", (USER_ID,))
print(f"alert_conditions 삭제: {cur.rowcount}건")

conn.commit()
cur.close()
conn.close()
print("고아 데이터 정리 완료!")
