"""
읍면동(level 3) 데이터 수집 스크립트 v2
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DB 시군구 코드가 표준 법정동코드와 다르므로
'이름 매칭' 방식으로 읍면동을 올바른 시군구에 연결합니다.

실행 방법:
  cd C:\\Users\\win\\Desktop\\workspace\\test\\nongji-alert\\backend
  py seed_eupmyeon.py
"""

import json
import os
import time
import urllib.request

import psycopg2
import psycopg2.extras
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:1234@localhost:5432/nongji")

# 공공 법정동코드 프록시 API (인증 불필요)
API_BASE = "https://grpc-proxy-server-mkvo6j4wsq-du.a.run.app/v1/regcodes"


def fetch_all_under_sido(sido_code: str) -> list[dict]:
    """시도 코드(2자리)로 하위 모든 코드 조회 (시군구 + 읍면동 + 리)"""
    url = f"{API_BASE}?regcode_pattern={sido_code}*&is_ignore_zero=true"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read())
            return data.get("regcodes", [])
    except Exception as e:
        print(f"  ⚠ API 오류 (시도 {sido_code}): {e}")
        return []


def parse_regions(api_results: list[dict]) -> dict:
    """
    API 결과를 시군구 → 읍면동 구조로 파싱
    
    법정동코드 10자리 구조:
      시도(2) + 시군구(3) + 읍면동(3) + 리(2) = 10자리
    
    시군구: XX YYY 00000 (뒤 5자리 모두 0)
    읍면동: XX YYY ZZZ 00 (ZZZ ≠ 000, 뒤 2자리 0)
    리:     XX YYY ZZZ WW (WW ≠ 00)
    """
    sigun_map = {}  # { 시군구이름: { code: ..., eupmyeon: [{code, name}, ...] } }
    
    # 1단계: 시군구 식별 (뒤 5자리가 00000)
    for item in api_results:
        code = item["code"]       # 10자리
        name = item["name"]       # "서울특별시 종로구"
        
        if code[5:] == "00000":
            # 시군구 레벨
            name_parts = name.strip().split()
            sigun_name = name_parts[-1] if len(name_parts) >= 2 else name
            sigun_code_5 = code[:5]
            sigun_map[sigun_code_5] = {
                "name": sigun_name,
                "code": sigun_code_5,
                "eupmyeon": []
            }
    
    # 2단계: 읍면동 식별 (뒤 2자리가 00, 읍면동 부분이 000이 아닌 것)
    for item in api_results:
        code = item["code"]
        name = item["name"]
        
        eup_part = code[5:8]   # 읍면동 코드 (3자리)
        ri_part = code[8:]     # 리 코드 (2자리)
        
        if eup_part != "000" and ri_part == "00":
            # 읍면동 레벨
            sigun_code_5 = code[:5]
            name_parts = name.strip().split()
            eup_name = name_parts[-1] if name_parts else name
            eup_code_8 = code[:8]
            
            if sigun_code_5 in sigun_map:
                sigun_map[sigun_code_5]["eupmyeon"].append({
                    "code": eup_code_8,
                    "name": eup_name,
                })
    
    return sigun_map


def normalize_name(name: str) -> str:
    """시군구 이름 정규화 (비교용)"""
    return name.strip().replace(" ", "")


def main():
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=psycopg2.extras.RealDictCursor)
    cur = conn.cursor()

    try:
        # 1. 기존 읍면동 데이터 삭제
        cur.execute("DELETE FROM regions WHERE level = 3")
        deleted = cur.rowcount
        if deleted > 0:
            print(f"기존 읍면동 {deleted}건 삭제\n")

        # 2. DB의 시도 목록 조회
        cur.execute("SELECT id, code, name FROM regions WHERE level = 1 ORDER BY code")
        sido_list = cur.fetchall()
        print(f"시도 {len(sido_list)}개에서 읍면동 수집 시작...\n")

        # 3. DB의 시군구 전체 조회 (이름 매칭용)
        cur.execute("""
            SELECT r2.id, r2.code as db_code, r2.name, r1.code as sido_code, r1.name as sido_name
            FROM regions r2
            JOIN regions r1 ON r2.parent_id = r1.id
            WHERE r2.level = 2
            ORDER BY r2.code
        """)
        db_sigun_list = cur.fetchall()

        # 시도코드 + 시군구이름 → DB 레코드 매핑
        db_sigun_by_name = {}
        for s in db_sigun_list:
            key = (s["sido_code"], normalize_name(s["name"]))
            db_sigun_by_name[key] = s

        total_inserted = 0
        total_matched = 0
        total_unmatched = 0
        unmatched_list = []

        for sido in sido_list:
            sido_code = sido["code"]
            sido_name = sido["name"]
            print(f"━━━ {sido_name} ({sido_code}) ━━━")

            # API에서 해당 시도의 모든 하위 코드 조회
            api_results = fetch_all_under_sido(sido_code)
            if not api_results:
                print(f"  ⚠ API 데이터 없음, 건너뜀\n")
                continue

            # 시군구 → 읍면동 구조로 파싱
            sigun_map = parse_regions(api_results)
            print(f"  API: 시군구 {len(sigun_map)}개 발견")

            # 각 시군구를 DB와 이름 매칭
            sido_inserted = 0
            for api_sigun_code, api_sigun in sigun_map.items():
                api_name = normalize_name(api_sigun["name"])
                lookup_key = (sido_code, api_name)

                db_record = db_sigun_by_name.get(lookup_key)
                if not db_record:
                    total_unmatched += 1
                    unmatched_list.append(f"  {sido_name} {api_sigun['name']}")
                    continue

                total_matched += 1
                db_sigun_id = str(db_record["id"])
                db_sigun_name = db_record["name"]
                eup_list = api_sigun["eupmyeon"]

                for eup in eup_list:
                    full_path = f"{sido_name} > {db_sigun_name} > {eup['name']}"
                    cur.execute("""
                        INSERT INTO regions (parent_id, code, name, level, full_path)
                        VALUES (%s, %s, %s, 3, %s)
                        ON CONFLICT (code) DO NOTHING
                    """, (db_sigun_id, eup["code"], eup["name"], full_path))
                    sido_inserted += 1

                if eup_list:
                    print(f"  ✓ {db_sigun_name}: {len(eup_list)}건")

            total_inserted += sido_inserted
            print(f"  소계: {sido_inserted}건 삽입\n")
            time.sleep(0.5)  # API 부하 방지

        conn.commit()

        print(f"\n{'='*50}")
        print(f"✅ 완료!")
        print(f"   읍면동 삽입: {total_inserted}건")
        print(f"   시군구 매칭 성공: {total_matched}개")
        if total_unmatched > 0:
            print(f"   시군구 매칭 실패: {total_unmatched}개")
            print(f"   (API에만 있고 DB에 없는 시군구)")
            for name in unmatched_list[:10]:
                print(name)
            if len(unmatched_list) > 10:
                print(f"   ... 외 {len(unmatched_list) - 10}개")
        print(f"{'='*50}")

        # 최종 확인
        cur.execute("SELECT level, count(*) as cnt FROM regions GROUP BY level ORDER BY level")
        for row in cur.fetchall():
            level_name = {1: "시도", 2: "시군구", 3: "읍면동"}[row["level"]]
            print(f"  level {row['level']} ({level_name}): {row['cnt']}건")

    except Exception as e:
        conn.rollback()
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    main()
