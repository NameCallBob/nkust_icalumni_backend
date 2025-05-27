# monitoring/utils.py
import hashlib
import geoip2.database
from datetime import datetime, timedelta
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone
from apps.record.models import ErrorLog, IPLimit

def get_country_from_ip(ip_address):
    """使用 GeoIP2 從 IP 獲取國家信息"""
    try:
        reader = geoip2.database.Reader(settings.GEOIP_PATH)
        response = reader.country(ip_address)
        reader.close()
        return response.country.name
    except Exception:
        return None

def rate_limit_check(ip_address, window_seconds=60, max_requests=100):
    """速率限制檢查"""
    hashed_ip = hashlib.sha256(f"{ip_address}{settings.SECRET_KEY}".encode()).hexdigest()
    
    try:
        ip_limit = IPLimit.objects.get(hashed_ip=hashed_ip)
        
        # 如果已被封鎖，直接返回 True
        if ip_limit.is_blocked:
            return True
            
        # 檢查時間窗口
        time_window = timezone.now() - timedelta(seconds=window_seconds)
        if ip_limit.last_request < time_window:
            # 重置計數器
            ip_limit.request_count = 1
            ip_limit.save(update_fields=['request_count', 'last_request'])
            return False
            
        # 檢查請求數量
        if ip_limit.request_count > max_requests:
            # 超出限制，標記為封鎖
            ip_limit.is_blocked = True
            ip_limit.block_reason = f"60秒內超過{max_requests}次請求"
            ip_limit.block_until = timezone.now() + timedelta(minutes=30)
            ip_limit.save()
            
            # 發送警報
            send_rate_limit_alert(ip_address, ip_limit.request_count)
            return True
            
        # 增加計數器
        ip_limit.request_count += 1
        ip_limit.save(update_fields=['request_count', 'last_request'])
        return False
        
    except IPLimit.DoesNotExist:
        # 首次請求，創建記錄
        IPLimit.objects.create(
            hashed_ip=hashed_ip,
            request_count=1,
        )
        return False

def send_rate_limit_alert(ip_address, request_count):
    """發送速率限制警報"""
    subject = f"安全警報：IP地址 {ip_address} 已被封鎖"
    message = f"""
    系統檢測到可能的惡意流量：
    
    IP地址: {ip_address}
    請求次數: {request_count} 次/分鐘
    時間: {timezone.now()}
    
    該IP已被自動封鎖30分鐘。
    """
    
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = settings.ADMIN_EMAILS
    
    send_mail(
        subject,
        message,
        from_email,
        recipient_list,
        fail_silently=True,
    )

def log_error(level, message, traceback=None, request=None):
    """記錄錯誤"""
    from apps.record.models import ErrorLog, RequestLog
    
    # 檢查是否有對應的請求日誌
    request_log = None
    if request and hasattr(request, 'id'):
        try:
            request_log = RequestLog.objects.get(id=request.id)
        except RequestLog.DoesNotExist:
            pass
    
    # 建立錯誤日誌
    error_log = ErrorLog.objects.create(
        level=level,
        message=message,
        traceback=traceback,
        request_log=request_log,
    )
    
    # 嚴重錯誤發送警報
    if level in ['error', 'critical']:
        send_error_alert(error_log)
    
    return error_log

def send_error_alert(error_log):
    """發送錯誤警報"""
    subject = f"系統錯誤警報：{error_log.get_level_display()}"
    message = f"""
    系統檢測到一個嚴重錯誤：
    
    錯誤等級: {error_log.get_level_display()}
    錯誤訊息: {error_log.message}
    發生時間: {error_log.timestamp}
    
    
    請盡快檢查系統。
    """
    
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = settings.ADMIN_EMAILS
    
    send_mail(
        subject,
        message,
        from_email,
        recipient_list,
        fail_silently=True,
    )

def cleanup_old_logs(days=30):
    """清理舊日誌數據"""
    from apps.record.models import RequestLog, QueryLog, ErrorLog
    
    cutoff_date = timezone.now() - timedelta(days=days)
    
    # 刪除老舊請求日誌
    RequestLog.objects.filter(timestamp__lt=cutoff_date).delete()
    
    # 刪除老舊查詢日誌
    QueryLog.objects.filter(timestamp__lt=cutoff_date).delete()
    
    # 刪除已處理的錯誤日誌
    ErrorLog.objects.filter(
        handled=True, 
        timestamp__lt=cutoff_date
    ).delete()