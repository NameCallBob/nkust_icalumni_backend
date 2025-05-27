from django.db.models import F, Q
from django.utils import timezone
from django.contrib.auth import get_user_model
import json
import traceback

from .models import (
    QueryLog, PopularQuery, IPLimit, CRUDLog, 
    RequestLog, ErrorLog, PerformanceMetric
)

User = get_user_model()

def create_query_log(query, ip, request_log=None, search_type=None, device_type=None, country=None, results_count=0, processing_time=None):
    """
    新增一筆查詢記錄
    
    參數:
    - query: 查詢內容
    - ip: 用戶IP地址
    - request_log: 關聯的RequestLog對象 (可選)
    - search_type: 搜索類型 (可選)
    - device_type: 設備類型 (可選)
    - country: 國家 (可選)
    - results_count: 查詢結果數量 (默認0)
    - processing_time: 處理時間(毫秒) (可選)
    
    返回:
    - 新建的QueryLog對象
    """
    hashed_ip = QueryLog.hash_ip(ip)
    
    return QueryLog.objects.create(
        query=query,
        search_type=search_type,
        hashed_ip=hashed_ip,
        device_type=device_type,
        country=country,
        request_log=request_log,
        results_count=results_count,
        processing_time=processing_time
    )

def increment_query_frequency(query, category=None):
    """
    新增或更新熱門查詢的記錄
    
    參數:
    - query: 查詢內容
    - category: 類別 (可選)
    
    返回:
    - PopularQuery對象
    """
    obj, created = PopularQuery.objects.get_or_create(
        query=query,
        defaults={"frequency": 1, "category": category, "last_searched": timezone.now()}
    )
    
    if not created:
        # 使用F表達式避免競態條件
        obj.frequency = F("frequency") + 1
        obj.last_searched = timezone.now()
        obj.save(update_fields=['frequency', 'last_searched'])
    
    return obj

def increment_click_count(query):
    """
    增加查詢的點擊次數
    
    參數:
    - query: 查詢內容
    
    返回:
    - PopularQuery對象
    """
    obj, created = PopularQuery.objects.get_or_create(
        query=query,
        defaults={"frequency": 0, "click_count": 1}
    )
    
    if not created:
        obj.increment_click()
    
    return obj

def log_ip_request(ip, is_blocked=False, block_reason=None, block_duration_hours=None):
    """
    更新 IP 限制的查詢記錄
    
    參數:
    - ip: 用戶IP地址
    - is_blocked: 是否封鎖 (默認False)
    - block_reason: 封鎖原因 (可選)
    - block_duration_hours: 封鎖時長(小時) (可選)
    
    返回:
    - IPLimit對象
    """
    hashed_ip = IPLimit.hash_ip(ip)
    
    obj, created = IPLimit.objects.get_or_create(
        hashed_ip=hashed_ip,
        defaults={
            "request_count": 1, 
            "total_request_count": 1,
            "last_request": timezone.now(),
            "is_blocked": is_blocked
        }
    )
    
    if not created:
        # 更新請求計數和最後請求時間
        obj.request_count = F("request_count") + 1
        obj.total_request_count = F("total_request_count") + 1
        obj.last_request = timezone.now()
        
        # 如果需要封鎖
        if is_blocked and not obj.is_blocked:
            obj.is_blocked = True
            obj.block_reason = block_reason
            
            if block_duration_hours:
                obj.block_until = timezone.now() + timezone.timedelta(hours=block_duration_hours)
                
        obj.save()
    
    return obj

def log_crud_action(user, app_name, model_name, action_type, data_snapshot, object_id=None, ip_address=None, changes=None, request_log=None):
    """
    新增 CRUD 日誌記錄
    
    參數:
    - user: 用戶對象
    - app_name: 應用名稱
    - model_name: 模型名稱
    - action_type: 操作類型 (create/update/delete/read)
    - data_snapshot: 資料快照
    - object_id: 對象ID (可選)
    - ip_address: IP地址 (可選)
    - changes: 變更內容 (可選)
    - request_log: 關聯的RequestLog對象 (可選)
    
    返回:
    - CRUDLog對象
    """
    # 確保 data_snapshot 是 JSON 可序列化的
    if not isinstance(data_snapshot, (dict, list)):
        if hasattr(data_snapshot, '__dict__'):
            data_snapshot = data_snapshot.__dict__
            # 移除不可序列化的項目
            data_snapshot = {k: v for k, v in data_snapshot.items() if isinstance(v, (str, int, float, bool, list, dict, type(None)))}
        else:
            data_snapshot = {'data': str(data_snapshot)}
    
    # 處理變更內容
    if changes and not isinstance(changes, dict):
        changes = {'changes': str(changes)}
    
    return CRUDLog.objects.create(
        user=user,
        app_name=app_name,
        model_name=model_name,
        action_type=action_type,
        data_snapshot=data_snapshot,
        object_id=str(object_id) if object_id else None,
        ip_address=ip_address,
        changes=changes,
        request_log=request_log
    )

def get_popular_queries(limit=10, category=None, min_frequency=None, time_period_days=None):
    """
    查詢熱門的查詢記錄
    
    參數:
    - limit: 返回結果數量限制 (默認10)
    - category: 過濾特定類別 (可選)
    - min_frequency: 最小頻率閾值 (可選)
    - time_period_days: 最近天數 (可選)
    
    返回:
    - QuerySet of PopularQuery
    """
    query = PopularQuery.objects.all()
    
    # 應用過濾條件
    if category:
        query = query.filter(category=category)
    
    if min_frequency:
        query = query.filter(frequency__gte=min_frequency)
    
    if time_period_days:
        cutoff_date = timezone.now() - timezone.timedelta(days=time_period_days)
        query = query.filter(last_searched__gte=cutoff_date)
    
    return query.order_by("-frequency")[:limit]

def is_ip_blocked(ip):
    """
    檢查 IP 是否被封鎖
    
    參數:
    - ip: 用戶IP地址
    
    返回:
    - boolean: 是否被封鎖
    """
    hashed_ip = IPLimit.hash_ip(ip)
    
    try:
        ip_limit = IPLimit.objects.get(hashed_ip=hashed_ip)
        
        # 如果已封鎖，檢查是否超過封鎖時間
        if ip_limit.is_blocked and ip_limit.block_until:
            if ip_limit.block_until < timezone.now():
                # 超過封鎖時間，自動解除
                ip_limit.is_blocked = False
                ip_limit.save(update_fields=['is_blocked'])
                return False
                
        return ip_limit.is_blocked
        
    except IPLimit.DoesNotExist:
        # 找不到記錄，表示未封鎖
        return False

def log_error(level, message, traceback_info=None, request=None, request_log=None):
    """
    記錄系統錯誤
    
    參數:
    - level: 錯誤等級 ('debug', 'info', 'warning', 'error', 'critical')
    - message: 錯誤訊息
    - traceback_info: 堆疊追蹤 (可選)
    - request: HttpRequest對象 (可選)
    - request_log: RequestLog對象 (可選)
    
    返回:
    - ErrorLog對象
    """
    # 如果提供了追蹤但不是字符串，格式化它
    if traceback_info is None and sys.exc_info()[0] is not None:
        traceback_info = traceback.format_exc()
        
    # 如果提供了請求但沒有提供請求日誌
    if request_log is None and request is not None:
        from .middleware import MonitoringMiddleware
        request_log = MonitoringMiddleware.get_request_log()
    
    return ErrorLog.objects.create(
        level=level,
        message=message,
        traceback=traceback_info,
        request_log=request_log,
        handled=False
    )

def record_performance_metric(metric_type, name, value, unit, details=None, request_log=None):
    """
    記錄性能指標
    
    參數:
    - metric_type: 指標類型
    - name: 指標名稱
    - value: 指標值
    - unit: 單位
    - details: 詳細資訊 (可選)
    - request_log: RequestLog對象 (可選)
    
    返回:
    - PerformanceMetric對象
    """
    # 確保詳細資訊是JSON可序列化的
    if details and not isinstance(details, dict):
        details = {'data': str(details)}
    
    return PerformanceMetric.objects.create(
        metric_type=metric_type,
        name=name,
        value=value,
        unit=unit,
        details=details,
        request_log=request_log
    )

def get_request_stats(days=7, path_pattern=None):
    """
    獲取請求統計數據
    
    參數:
    - days: 天數範圍 (默認7天)
    - path_pattern: 路徑模式過濾 (可選)
    
    返回:
    - dict: 統計數據
    """
    from django.db.models import Count, Avg, Min, Max
    
    start_date = timezone.now() - timezone.timedelta(days=days)
    
    # 基礎查詢集
    queryset = RequestLog.objects.filter(timestamp__gte=start_date)
    
    # 應用路徑過濾
    if path_pattern:
        queryset = queryset.filter(path__icontains=path_pattern)
    
    # 計算統計資料
    stats = {
        'total_requests': queryset.count(),
        'average_time': queryset.aggregate(avg_time=Avg('processing_time'))['avg_time'],
        'by_status': list(queryset.values('response_status').annotate(count=Count('id')).order_by('-count')),
        'by_method': list(queryset.values('method').annotate(count=Count('id')).order_by('-count')),
        'by_path': list(queryset.values('path').annotate(
            count=Count('id'),
            avg_time=Avg('processing_time')
        ).order_by('-count')[:10]),
        'by_device': list(queryset.values('device_type').annotate(count=Count('id')).order_by('-count')),
        'by_country': list(queryset.values('country').annotate(count=Count('id')).order_by('-count')[:10]),
    }
    
    return stats

def cleanup_old_logs(days=30):
    """
    清理老舊日誌數據
    
    參數:
    - days: 保留天數 (默認30天)
    
    返回:
    - dict: 清理結果統計
    """
    cutoff_date = timezone.now() - timezone.timedelta(days=days)
    
    # 刪除老舊請求日誌
    req_count, _ = RequestLog.objects.filter(timestamp__lt=cutoff_date).delete()
    
    # 刪除老舊查詢日誌
    query_count, _ = QueryLog.objects.filter(timestamp__lt=cutoff_date).delete()
    
    # 刪除已處理的錯誤日誌
    error_count, _ = ErrorLog.objects.filter(
        handled=True, 
        timestamp__lt=cutoff_date
    ).delete()
    
    # 刪除老舊性能指標
    perf_count, _ = PerformanceMetric.objects.filter(timestamp__lt=cutoff_date).delete()
    
    return {
        'request_logs': req_count,
        'query_logs': query_count,
        'error_logs': error_count,
        'performance_metrics': perf_count,
        'total': req_count + query_count + error_count + perf_count
    }