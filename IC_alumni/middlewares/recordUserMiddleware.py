# monitoring/middleware.py
import time
import json
import re
import hashlib
import user_agents
from django.utils.deprecation import MiddlewareMixin
from django.utils import timezone
from apps.record.models import RequestLog, IPLimit, ErrorLog, PerformanceMetric, QueryLog
from utils.get_ip import get_country_from_ip
import traceback

class MonitoringMiddleware(MiddlewareMixin):
    """整合監控中間件"""
    
    def process_request(self, request):
        # 儲存請求開始時間
        request.start_time = time.time()
        
        # 檢查IP限制
        client_ip = self.get_client_ip(request)
        hashed_ip = IPLimit.hash_ip(client_ip)
        
        # 檢查是否被封鎖
        try:
            ip_limit = IPLimit.objects.get(hashed_ip=hashed_ip)
            
            if ip_limit.is_blocked:
                # 檢查是否超過封鎖時間
                if ip_limit.block_until and ip_limit.block_until < timezone.now():
                    # 解除封鎖
                    ip_limit.is_blocked = False
                    ip_limit.save(update_fields=['is_blocked'])
                else:
                    # 返回封鎖響應
                    from django.http import HttpResponseForbidden
                    return HttpResponseForbidden("您的IP暫時被限制訪問，請稍後再試。")
            
            # 更新請求計數
            ip_limit.request_count += 1
            ip_limit.total_request_count += 1
            ip_limit.save(update_fields=['request_count', 'total_request_count', 'last_request'])
            
        except IPLimit.DoesNotExist:
            # 首次請求，創建記錄
            IPLimit.objects.create(
                hashed_ip=hashed_ip,
                request_count=1,
                total_request_count=1
            )   
        except Exception as e:
            return None
        
        return None

    def process_response(self, request, response):
        # 若沒有開始時間（某些請求可能被其他中間件短路）
        if not hasattr(request, 'start_time'):
            return response
            
        # 計算處理時間（毫秒）
        processing_time = (time.time() - request.start_time) * 1000
        
        # 排除靜態文件和監控自身的API請求
        path = request.path
        if path.startswith('/static/') or path.startswith('/media/') or path.startswith('/api/monitoring/'):
            return response
        
        # 獲取使用者ID（若已認證）
        user_id = None
        if hasattr(request, 'user') and request.user.is_authenticated:
            user_id = str(request.user.id)
            
        # 解析用戶代理
        user_agent_string = request.META.get('HTTP_USER_AGENT', '')
        device_type = "unknown"
        if user_agent_string:
            user_agent = user_agents.parse(user_agent_string)
            if user_agent.is_mobile:
                device_type = "mobile"
            elif user_agent.is_tablet:
                device_type = "tablet"
            elif user_agent.is_pc:
                device_type = "desktop"
        
        # 獲取IP和國家
        ip_address = self.get_client_ip(request)
        country = get_country_from_ip(ip_address)
        
        # 判斷是否為API調用
        is_api_call = path.startswith('/api/')
        
        # 獲取會話ID
        session_id = request.session.session_key if hasattr(request, 'session') else None
        
        # 獲取請求內容（根據內容類型處理）
        request_body = None
        if request.method in ['POST', 'PUT', 'PATCH']:
            try:
                if request.content_type == 'application/json':
                    # 請求內容已被讀取，需從request._body取得
                    if hasattr(request, '_body'):
                        request_body = json.loads(request._body.decode('utf-8'))
                    else:
                        request_body = request.body.decode('utf-8')
                else:
                    # 表單數據
                    request_body = dict(request.POST)
            except Exception:
                request_body = "無法解析請求內容"
                
        # 獲取響應大小
        response_size = len(response.content) if hasattr(response, 'content') else 0
        
        # 記錄請求日誌
        log = RequestLog.objects.create(
            user_id=user_id,
            ip_address=ip_address,
            method=request.method,
            path=path,
            query_params=json.dumps(dict(request.GET)) if request.GET else None,
            request_body=json.dumps(request_body) if request_body else None,
            response_status=response.status_code,
            response_size=response_size,
            processing_time=processing_time,
            user_agent=user_agent_string,
            referer=request.META.get('HTTP_REFERER'),
            device_type=device_type,
            country=country,
            is_api_call=is_api_call,
            user_session=session_id,
        )
        
        # 記錄性能指標
        if processing_time > 1000:  # 請求超過1秒
            PerformanceMetric.objects.create(
                metric_type="api_response",
                name=f"{request.method} {path}",
                value=processing_time,
                unit="ms",
                details={
                    "endpoint": path,
                    "method": request.method,
                    "params": dict(request.GET),
                },
                request_log=log
            )
            
        # 檢查是否為搜索查詢
        if 'search' in request.GET or 'query' in request.GET or 'q' in request.GET:
            query = request.GET.get('search') or request.GET.get('query') or request.GET.get('q')
            if query:
                # 建立查詢日誌
                hashed_ip = QueryLog.hash_ip(ip_address)
                QueryLog.objects.create(
                    query=query,
                    search_type=self.determine_search_type(path),
                    hashed_ip=hashed_ip,
                    device_type=device_type,
                    country=country,
                    request_log=log,
                    results_count=self.get_response_result_count(response),
                    processing_time=processing_time,
                )
                
                # 更新熱門查詢統計
                from apps.record.models import PopularQuery
                popular_query, created = PopularQuery.objects.get_or_create(query=query)
                popular_query.increment_search()
                
        return response
        
    def process_exception(self, request, exception):
        """處理請求異常"""
        # 記錄錯誤日誌
        ErrorLog.objects.create(
            level="error",
            message=str(exception),
            traceback=traceback.format_exc(),
        )
        return None
        
    def get_client_ip(self, request):
        """獲取客戶端真實 IP 地址"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            # 取得實際客戶端IP
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
        
    def determine_search_type(self, path):
        """根據路徑確定搜索類型"""
        if '/products/' in path:
            return 'product_search'
        elif '/articles/' in path:
            return 'article_search'
        elif '/users/' in path:
            return 'user_search'
        else:
            return 'general_search'
            
    def get_response_result_count(self, response):
        """嘗試從響應中獲取結果計數"""
        if hasattr(response, 'data') and isinstance(response.data, dict):
            # DRF 響應
            if 'count' in response.data:
                return response.data['count']
            elif 'results' in response.data and isinstance(response.data['results'], list):
                return len(response.data['results'])
        return 0