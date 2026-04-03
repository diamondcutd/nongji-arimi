import logging
import os
import uuid

import psycopg2
import psycopg2.extras
from fastapi import APIRouter, Depends, HTTPException, Query

logger = logging.getLogger(__name__)
router = APIRouter()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:1234@localhost:5432/nongji")


def validate_uuid(value: str, field_name: str = "id") -> str:
    """UUID 형식 검증. 유효하지 않으면 HTTPException 발생"""
    try:
        uuid.UUID(value)
        return value
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=400,
            detail=f"유효하지 않은 {field_name} 형식입니다 (UUID 예상)"
        )


def get_conn():
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=psycopg2.extras.RealDictCursor)
    try:
        yield conn
    finally:
        conn.close()


@router.get("/sido")
def get_sido(conn=Depends(get_conn)):
    """시도 목록 반환 (level=1)"""
    cur = conn.cursor()
    try:
        cur.execute(
            "SELECT id::text, code, name FROM regions WHERE level = 1 ORDER BY code"
        )
        rows = cur.fetchall()
        logger.info("sido 조회: %d건", len(rows))
        return [dict(r) for r in rows]
    except Exception as e:
        logger.error("sido 조회 실패: %s", e)
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()


@router.get("/sigun")
def get_sigun(sido_id: str = Query(..., description="시도 UUID"), conn=Depends(get_conn)):
    """해당 시도의 시군구 목록 반환 (level=2)"""
    # UUID 형식 검증
    sido_id = validate_uuid(sido_id, "sido_id")

    cur = conn.cursor()
    try:
        cur.execute(
            "SELECT id::text, code, name FROM regions WHERE parent_id = %s::uuid AND level = 2 ORDER BY name",
            (sido_id,),
        )
        rows = cur.fetchall()
        logger.info("sigun 조회 (sido_id=%s): %d건", sido_id, len(rows))
        return [dict(r) for r in rows]
    except Exception as e:
        logger.error("sigun 조회 실패 (sido_id=%s): %s", sido_id, e)
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()


@router.get("/eupmyeon")
def get_eupmyeon(sigun_id: str = Query(..., description="시군구 UUID"), conn=Depends(get_conn)):
    """해당 시군구의 읍면동 목록 반환 (level=3)"""
    # UUID 형식 검증
    sigun_id = validate_uuid(sigun_id, "sigun_id")

    cur = conn.cursor()
    try:
        cur.execute(
            "SELECT id::text, code, name FROM regions WHERE parent_id = %s::uuid AND level = 3 ORDER BY name",
            (sigun_id,),
        )
        rows = cur.fetchall()
        logger.info("eupmyeon 조회 (sigun_id=%s): %d건", sigun_id, len(rows))
        return [dict(r) for r in rows]
    except Exception as e:
        logger.error("eupmyeon 조회 실패 (sigun_id=%s): %s", sigun_id, e)
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()


@router.get("/ancestors")
def get_ancestors(region_id: str = Query(..., description="지역 UUID"), conn=Depends(get_conn)):
    """region_id의 계층 정보 반환 (시도/시군구/읍면동 UUID)
    편집 모달에서 드롭다운 프리필용"""
    # UUID 형식 검증
    region_id = validate_uuid(region_id, "region_id")

    cur = conn.cursor()
    try:
        cur.execute(
            "SELECT id::text, parent_id::text, name, level FROM regions WHERE id = %s::uuid",
            (region_id,),
        )
        region = cur.fetchone()
        if not region:
            raise HTTPException(status_code=404, detail="지역을 찾을 수 없습니다")

        result = {"sido_id": None, "sigun_id": None, "eupmyeon_id": None}

        if region["level"] == 1:
            result["sido_id"] = region["id"]
        elif region["level"] == 2:
            result["sigun_id"] = region["id"]
            result["sido_id"] = region["parent_id"]
        elif region["level"] == 3:
            result["eupmyeon_id"] = region["id"]
            result["sigun_id"] = region["parent_id"]
            # 시군구의 parent → 시도
            cur.execute(
                "SELECT parent_id::text FROM regions WHERE id = %s::uuid",
                (region["parent_id"],),
            )
            sigun = cur.fetchone()
            if sigun:
                result["sido_id"] = sigun["parent_id"]

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error("ancestors 조회 실패 (region_id=%s): %s", region_id, e)
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
