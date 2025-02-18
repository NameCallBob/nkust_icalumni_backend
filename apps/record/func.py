from django.db.models import F
from django.utils.timezone import now

from apps.record.models import QueryLogs,PopularQueries,IPLimits,ClickCount,CRUDLog

def create_query_log(query, ip, search_type=None, device_type=None, country=None):
    """新增一筆查詢記錄"""
    hashed_ip = QueryLogs.hash_ip(ip)
    return QueryLogs.objects.create(
        query=query,
        search_type=search_type,
        hashed_ip=hashed_ip,
        device_type=device_type,
        country=country
    )

def increment_query_frequency(query, category=None):
    """新增或更新熱門查詢的記錄"""
    obj, created = PopularQueries.objects.get_or_create(
        query=query,
        defaults={"frequency": 1, "category": category, "last_searched": now()}
    )
    if not created:
        obj.frequency = F("frequency") + 1
        obj.last_searched = now()
        obj.save()
    return obj

def log_ip_request(ip):
    """更新 IP 限制的查詢記錄"""
    hashed_ip = QueryLogs.hash_ip(ip)
    obj, created = IPLimits.objects.get_or_create(
        hashed_ip=hashed_ip,
        defaults={"request_count": 1, "last_request": now()}
    )
    if not created:
        obj.request_count = F("request_count") + 1
        obj.last_request = now()
        obj.save()
    return obj

def increment_click_count(query):
    """增加查詢的點擊次數"""
    obj, created = ClickCount.objects.get_or_create(
        query=query,
        defaults={"click_count": 1}
    )
    if not created:
        obj.increment()
    return obj

def log_crud_action(user, app_name, model_name, action_type, data_snapshot):
    """新增 CRUD 日誌記錄"""
    return CRUDLog.objects.create(
        user=user,
        app_name=app_name,
        model_name=model_name,
        action_type=action_type,
        data_snapshot=data_snapshot
    )

def get_popular_queries(limit=10):
    """查詢熱門的查詢記錄"""
    return PopularQueries.objects.order_by("-frequency")[:limit]

def is_ip_blocked(ip):
    """檢查 IP 是否被封鎖"""
    hashed_ip = QueryLogs.hash_ip(ip)
    ip_limit = IPLimits.objects.filter(hashed_ip=hashed_ip).first()
    return ip_limit.is_blocked if ip_limit else False
