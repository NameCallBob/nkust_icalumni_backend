import threading
from datetime import datetime
from django.db import transaction
from apps.record.models import QueryLogs, PopularQueries, IPLimits, ClickCount

def save_query_log(data):
    """
    保存查詢記錄到 QueryLogs 表。
    """
    def save():
        try:
            hashed_ip = QueryLogs.hash_ip(data.get("ip", ""))
            QueryLogs.objects.create(
                query=data.get("query", ""),
                search_type=data.get("search_type", None),
                hashed_ip=hashed_ip,
                device_type=data.get("device_type", None),
                country=data.get("country", None),
            )
        except Exception as e:
            print(f"Error while saving query log: {e}")

    thread = threading.Thread(target=save)
    thread.start()

def update_popular_queries(data):
    """
    更新 PopularQueries 表的數據。
    """
    def update():
        try:
            with transaction.atomic():
                popular_query, created = PopularQueries.objects.get_or_create(
                    query=data.get("query", ""),
                    defaults={"frequency": 1},
                )
                if not created:
                    popular_query.frequency += 1
                    popular_query.save()
        except Exception as e:
            print(f"Error while updating popular queries: {e}")

    thread = threading.Thread(target=update)
    thread.start()

def update_ip_limits(data):
    """
    更新 IPLimits 表的數據。
    """
    def update():
        try:
            hashed_ip = QueryLogs.hash_ip(data.get("ip", ""))
            with transaction.atomic():
                ip_limit, _ = IPLimits.objects.get_or_create(
                    hashed_ip=hashed_ip,
                    defaults={"request_count": 1},
                )
                if not ip_limit.is_blocked:
                    ip_limit.request_count += 1
                    ip_limit.last_request = datetime.now()
                    ip_limit.save()
        except Exception as e:
            print(f"Error while updating IP limits: {e}")

    thread = threading.Thread(target=update)
    thread.start()

def update_click_count(data):
    """
    更新 ClickCount 表的點擊數。
    """
    def update():
        try:
            if data.get("click", False):
                with transaction.atomic():
                    click_count, _ = ClickCount.objects.get_or_create(
                        query=data.get("query", ""),
                        defaults={"click_count": 1},
                    )
                    if not _:
                        click_count.increment()
        except Exception as e:
            print(f"Error while updating click count: {e}")

    thread = threading.Thread(target=update)
    thread.start()