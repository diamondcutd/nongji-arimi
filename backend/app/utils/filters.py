from app.models import Listing, AlertCondition


def matches_condition(listing: Listing, condition: AlertCondition) -> bool:
    """매물이 알림 조건에 매칭되는지 확인"""

    # 시도 코드
    if condition.sido_cd and listing.sido_cd != condition.sido_cd:
        return False

    # 시군구 코드
    if condition.sigun_cd and listing.sigun_cd != condition.sigun_cd:
        return False

    # 읍면동
    if condition.eupmyeondong and listing.eupmyeondong:
        if condition.eupmyeondong not in listing.eupmyeondong:
            return False

    # 지목
    if condition.land_category and listing.land_category != condition.land_category:
        return False

    # 거래유형
    if condition.trade_type and listing.trade_type:
        if condition.trade_type not in listing.trade_type:
            return False

    # 면적 범위
    if listing.total_area is not None:
        if condition.area_min is not None and listing.total_area < condition.area_min:
            return False
        if condition.area_max is not None and listing.total_area > condition.area_max:
            return False

    # 금액 범위
    if listing.price is not None:
        if condition.price_min is not None and listing.price < condition.price_min:
            return False
        if condition.price_max is not None and listing.price > condition.price_max:
            return False

    return True
