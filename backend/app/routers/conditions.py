import os
import uuid
import json
from datetime import datetime, timezone

import psycopg2
import psycopg2.extras
from fastapi import APIRouter, Depends, HTTPException

from app.schemas import ConditionCreate, ConditionUpdate, ConditionResponse
from app.auth_utils import get_current_user

router = APIRouter()


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

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:1234@localhost:5432/nongji")

# Basic: 최대 5개, Premium: 무제한
PLAN_LIMITS = {"basic": 5, "premium": 999999}


def get_conn():
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=psycopg2.extras.RealDictCursor)
    try:
        yield conn
    finally:
        conn.close()


@router.get("", response_model=list[ConditionResponse])
def list_conditions(
    current_user=Depends(get_current_user),
    conn=Depends(get_conn),
):
    cur = conn.cursor()
    try:
        cur.execute(
            """SELECT id, user_id, label, region_id, include_children,
                      land_category, trade_type, biz_type, area_min, area_max,
                      price_max, notify_channels, created_via, is_active, created_at
               FROM alert_conditions
               WHERE user_id = %s AND is_active = true
               ORDER BY created_at DESC""",
            (current_user["id"],),
        )
        rows = cur.fetchall()
        for r in rows:
            r["id"] = str(r["id"])
            r["user_id"] = str(r["user_id"])
            if r["region_id"]:
                r["region_id"] = str(r["region_id"])
        return rows
    finally:
        cur.close()


@router.post("", response_model=ConditionResponse, status_code=201)
def create_condition(
    data: ConditionCreate,
    current_user=Depends(get_current_user),
    conn=Depends(get_conn),
):
    cur = conn.cursor()
    try:
        # 플랜별 조건 개수 제한 확인
        cur.execute(
            "SELECT COUNT(*) AS cnt FROM alert_conditions WHERE user_id = %s AND is_active = true",
            (current_user["id"],),
        )
        count = cur.fetchone()["cnt"]
        limit = PLAN_LIMITS.get(current_user["plan"], 5)

        if count >= limit:
            raise HTTPException(
                status_code=403,
                detail=f"현재 플랜({current_user['plan']})의 알림 조건 등록 한도({limit}개)를 초과했습니다",
            )

        # 빈 조건 방지 — 최소 1개 필터 필수
        has_filter = any([
            data.region_id,
            data.land_category,
            data.trade_type,
            data.biz_type,
            data.area_min is not None,
            data.area_max is not None,
            data.price_max is not None,
        ])
        if not has_filter:
            raise HTTPException(
                status_code=400,
                detail="최소 1개 이상의 필터 조건을 설정해주세요 (지역, 지목, 거래유형, 면적, 가격 중 택1)",
            )

        condition_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc)
        channels = json.dumps(data.notify_channels) if data.notify_channels else '["email"]'
        biz_type_json = json.dumps(data.biz_type) if data.biz_type else '[]'

        cur.execute(
            """INSERT INTO alert_conditions
               (id, user_id, label, region_id, include_children,
                land_category, trade_type, biz_type, area_min, area_max,
                price_max, notify_channels, created_via, is_active, created_at)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s::jsonb, %s, %s, %s, %s::jsonb, %s, %s, %s)
               RETURNING id, user_id, label, region_id, include_children,
                         land_category, trade_type, biz_type, area_min, area_max,
                         price_max, notify_channels, created_via, is_active, created_at""",
            (
                condition_id, current_user["id"], data.label, data.region_id,
                data.include_children, data.land_category, data.trade_type,
                biz_type_json, data.area_min, data.area_max, data.price_max,
                channels, data.created_via, True, now,
            ),
        )
        row = cur.fetchone()
        conn.commit()
        row["id"] = str(row["id"])
        row["user_id"] = str(row["user_id"])
        if row["region_id"]:
            row["region_id"] = str(row["region_id"])
        return row

    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"알림 조건 등록 중 오류: {e}")
    finally:
        cur.close()


@router.put("/{condition_id}", response_model=ConditionResponse)
def update_condition(
    condition_id: str,
    data: ConditionUpdate,
    current_user=Depends(get_current_user),
    conn=Depends(get_conn),
):
    # UUID 형식 검증
    condition_id = validate_uuid(condition_id, "condition_id")

    cur = conn.cursor()
    try:
        # 소유권 확인
        cur.execute(
            "SELECT id FROM alert_conditions WHERE id = %s AND user_id = %s",
            (condition_id, current_user["id"]),
        )
        if not cur.fetchone():
            raise HTTPException(status_code=404, detail="알림 조건을 찾을 수 없습니다")

        update_data = data.model_dump(exclude_unset=True)
        if not update_data:
            raise HTTPException(status_code=400, detail="수정할 항목이 없습니다")

        # Whitelist 컬럼 검증 (SQL Injection 방어)
        ALLOWED_COLUMNS = {
            "label", "region_id", "include_children", "land_category",
            "trade_type", "biz_type", "area_min", "area_max", "price_max",
            "notify_channels", "is_active"
        }
        for key in update_data.keys():
            if key not in ALLOWED_COLUMNS:
                raise HTTPException(
                    status_code=400,
                    detail=f"허용되지 않은 필드: {key}"
                )

        # jsonb 컬럼 캐스팅
        set_parts = []
        values = []
        jsonb_cols = ("notify_channels", "biz_type")
        for key, val in update_data.items():
            if key in jsonb_cols:
                set_parts.append(f"{key} = %s::jsonb")
                values.append(json.dumps(val))
            else:
                set_parts.append(f"{key} = %s")
                values.append(val)

        values.extend([condition_id, current_user["id"]])

        cur.execute(
            f"""UPDATE alert_conditions SET {', '.join(set_parts)}
                WHERE id = %s AND user_id = %s
                RETURNING id, user_id, label, region_id, include_children,
                          land_category, trade_type, biz_type, area_min, area_max,
                          price_max, notify_channels, created_via, is_active, created_at""",
            values,
        )
        row = cur.fetchone()
        conn.commit()
        row["id"] = str(row["id"])
        row["user_id"] = str(row["user_id"])
        if row["region_id"]:
            row["region_id"] = str(row["region_id"])
        return row

    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"알림 조건 수정 중 오류: {e}")
    finally:
        cur.close()


@router.delete("/{condition_id}", status_code=204)
def delete_condition(
    condition_id: str,
    current_user=Depends(get_current_user),
    conn=Depends(get_conn),
):
    # UUID 형식 검증
    condition_id = validate_uuid(condition_id, "condition_id")

    cur = conn.cursor()
    try:
        cur.execute(
            "DELETE FROM alert_conditions WHERE id = %s AND user_id = %s RETURNING id",
            (condition_id, current_user["id"]),
        )
        if not cur.fetchone():
            raise HTTPException(status_code=404, detail="알림 조건을 찾을 수 없습니다")
        conn.commit()
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"알림 조건 삭제 중 오류: {e}")
    finally:
        cur.close()
