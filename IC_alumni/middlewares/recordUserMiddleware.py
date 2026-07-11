# monitoring/middleware.py
import time
import json
import hashlib
import user_agents
import threading
from concurrent.futures import ThreadPoolExecutor
from django.utils.deprecation import MiddlewareMixin
from django.utils import timezone
from django.conf import settings
import ipaddress
from apps.record.models import RequestLog, IPLimit, ErrorLog, PerformanceMetric, QueryLog
from utils.get_ip import get_country_from_ip
import traceback

# Module-level thread pool for async logging (max 4 background workers)
_log_executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix='monitoring_log')


def _write_request_log(log_data):
    """Write request log in background thread."""
    from django.db import close_old_connections
    try:
        log = RequestLog.objects.create(**log_data)
        return log
    except Exception:
        pass
    finally:
        close_old_connections()


def _increment_ip_count(hashed_ip):
    """[效能修補] 於背景非阻塞地累加 IP 請求計數，不卡住請求主流程。"""
    from django.db import close_old_connections
    from django.db.models import F
    try:
        updated = IPLimit.objects.filter(hashed_ip=hashed_ip).update(
            request_count=F('request_count') + 1,
            total_request_count=F('total_request_count') + 1,
            last_request=timezone.now(),
        )
        if not updated:
            IPLimit.objects.get_or_create(
                hashed_ip=hashed_ip,
                defaults={'request_count': 1, 'total_request_count': 1},
            )
    except Exception:
        pass
    finally:
        close_old_connections()


def _write_performance_metric(metric_data):
    """Write performance metric in background thread."""
    from django.db import close_old_connections
    try:
        PerformanceMetric.objects.create(**metric_data)
    except Exception:
        pass
    finally:
        close_old_connections()


def _write_query_log(query_log_data, query):
    """Write query log and update popular query in background thread."""
    from django.db import close_old_connections
    from apps.record.models import PopularQuery
    try:
        QueryLog.objects.create(**query_log_data)
        popular_query, created = PopularQuery.objects.get_or_create(query=query)
        popular_query.increment_search()
    except Exception:
        pass
    finally:
        close_old_connections()


class MonitoringMiddleware(MiddlewareMixin):
    """整合監控中間件 - 使用背景執行緒處理日誌寫入以降低延遲"""

    def process_request(self, request):
        # 儲存請求開始時間
        request.start_time = time.time()

        # 檢查IP限制（必須阻擋被封鎖的IP）
        client_ip = self.get_client_ip(request)
        hashed_ip = IPLimit.hash_ip(client_ip)

        # [效能修補] 封鎖狀態快取 60 秒，避免每個請求都對 DB 做一次同步查詢。
        # 管理員手動封鎖最遲 60 秒內生效。
        from django.core.cache import cache
        block_key = f'ip_blocked:{hashed_ip}'
        is_blocked = cache.get(block_key)
        if is_blocked is None:
            try:
                ip_limit = IPLimit.objects.get(hashed_ip=hashed_ip)
                if ip_limit.is_blocked and ip_limit.block_until and ip_limit.block_until < timezone.now():
                    # 封鎖到期，解除
                    ip_limit.is_blocked = False
                    ip_limit.save(update_fields=['is_blocked'])
                    is_blocked = False
                else:
                    is_blocked = bool(ip_limit.is_blocked)
            except IPLimit.DoesNotExist:
                is_blocked = False
            except Exception:
                is_blocked = False
            try:
                cache.set(block_key, is_blocked, 60)
            except Exception:
                pass

        if is_blocked:
            from django.http import HttpResponseForbidden
            return HttpResponseForbidden("您的IP暫時被限制訪問，請稍後再試。")

        # [效能修補] 請求計數改為背景非阻塞更新，移出請求關鍵路徑
        try:
            _log_executor.submit(_increment_ip_count, hashed_ip)
        except Exception:
            pass

        return None

    def process_response(self, request, response):
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
            ua = user_agents.parse(user_agent_string)
            if ua.is_mobile:
                device_type = "mobile"
            elif ua.is_tablet:
                device_type = "tablet"
            elif ua.is_pc:
                device_type = "desktop"

        # 獲取IP和國家
        ip_address = self.get_client_ip(request)
        country = get_country_from_ip(ip_address)

        # 判斷是否為API調用
        is_api_call = path.startswith('/api/')

        # 獲取會話ID
        session_id = request.session.session_key if hasattr(request, 'session') else None

        # 獲取請求內容
        request_body = None
        if request.method in ['POST', 'PUT', 'PATCH']:
            try:
                if request.content_type == 'application/json':
                    if hasattr(request, '_body'):
                        request_body = json.loads(request._body.decode('utf-8'))
                    else:
                        request_body = request.body.decode('utf-8')
                else:
                    request_body = dict(request.POST)
            except Exception:
                request_body = "無法解析請求內容"
            # [資安修補 HIGH-5] 遮罩敏感欄位，避免明文密碼/重設碼/Token 寫入 RequestLog 資料庫
            request_body = self._redact_sensitive(request_body)

        # 獲取響應大小
        # [效能修補] 優先使用 Content-Length 標頭，避免存取 response.content 觸發整體渲染/破壞串流
        response_size = 0
        content_length = response.get('Content-Length') if hasattr(response, 'get') else None
        if content_length is not None:
            try:
                response_size = int(content_length)
            except (TypeError, ValueError):
                response_size = 0
        elif hasattr(response, 'content') and not getattr(response, 'streaming', False):
            response_size = len(response.content)

        # 準備日誌資料（在主執行緒收集，傳給背景執行緒寫入）
        log_data = {
            'user_id': user_id,
            'ip_address': ip_address,
            'method': request.method,
            'path': path,
            # [資安修補 SEC-011] query string 同樣可能帶 token/code 等敏感值，寫入前一併遮罩。
            'query_params': json.dumps(self._redact_sensitive(dict(request.GET))) if request.GET else None,
            'request_body': json.dumps(request_body) if request_body else None,
            'response_status': response.status_code,
            'response_size': response_size,
            'processing_time': processing_time,
            'user_agent': user_agent_string,
            'referer': request.META.get('HTTP_REFERER'),
            'device_type': device_type,
            'country': country,
            'is_api_call': is_api_call,
            'user_session': session_id,
        }

        # 異步寫入 RequestLog
        log_future = _log_executor.submit(_write_request_log, log_data)

        # 異步寫入 PerformanceMetric（僅在超過1秒時）
        if processing_time > 1000:
            metric_data = {
                'metric_type': "api_response",
                'name': f"{request.method} {path}",
                'value': processing_time,
                'unit': "ms",
                'details': {
                    'endpoint': path,
                    'method': request.method,
                    'params': dict(request.GET),
                },
            }
            _log_executor.submit(_write_performance_metric, metric_data)

        # 異步寫入 QueryLog 和更新 PopularQuery
        if 'search' in request.GET or 'query' in request.GET or 'q' in request.GET:
            query = request.GET.get('search') or request.GET.get('query') or request.GET.get('q')
            if query:
                hashed_ip = QueryLog.hash_ip(ip_address)
                query_log_data = {
                    'query': query,
                    'search_type': self.determine_search_type(path),
                    'hashed_ip': hashed_ip,
                    'device_type': device_type,
                    'country': country,
                    'request_log': None,
                    'results_count': self.get_response_result_count(response),
                    'processing_time': processing_time,
                }
                _log_executor.submit(_write_query_log, query_log_data, query)

        return response

    def process_exception(self, request, exception):
        """處理請求異常（背景寫入）"""
        tb = traceback.format_exc()
        exc_str = str(exception)

        def _write_error():
            from django.db import close_old_connections
            try:
                ErrorLog.objects.create(
                    level="error",
                    message=exc_str,
                    traceback=tb,
                )
            except Exception:
                pass
            finally:
                close_old_connections()

        _log_executor.submit(_write_error)
        return None

    # [資安修補 HIGH-5] 敏感欄位遮罩名單
    SENSITIVE_KEYS = {
        'password', 'new_password', 'old_password', 'confirm_password',
        'code', 'token', 'access', 'refresh', 'secret', 'authorization',
    }

    def _redact_sensitive(self, body):
        """遞迴遮罩請求內容中的敏感欄位，避免明文寫入日誌資料庫。"""
        try:
            if isinstance(body, dict):
                redacted = {}
                for k, v in body.items():
                    if isinstance(k, str) and k.lower() in self.SENSITIVE_KEYS:
                        redacted[k] = '***REDACTED***'
                    else:
                        redacted[k] = self._redact_sensitive(v)
                return redacted
            if isinstance(body, list):
                return [self._redact_sensitive(v) for v in body]
        except Exception:
            return body
        return body

    def get_client_ip(self, request):
        """獲取客戶端真實 IP 地址。

        [資安修補 SEC-012] 不再盲信用戶端可控的 X-Forwarded-For 第一個值
        （否則攻擊者可偽造 IP 規避封鎖/限流，並於 log 注入任意字串）。
        僅信任反向代理附加的最後 N 個 hop（N=settings.TRUSTED_PROXY_COUNT，預設 1），
        取最右側可信 IP；無 XFF 或格式無效時退回 REMOTE_ADDR。
        """
        remote_addr = request.META.get('REMOTE_ADDR')
        num_trusted = getattr(settings, 'TRUSTED_PROXY_COUNT', 1)
        ip = remote_addr
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for and num_trusted > 0:
            parts = [p.strip() for p in x_forwarded_for.split(',') if p.strip()]
            if len(parts) >= num_trusted:
                ip = parts[-num_trusted]
        # 驗證 IP 格式，避免被注入非法字串
        try:
            ipaddress.ip_address(ip)
        except (ValueError, TypeError):
            ip = remote_addr
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
            if 'count' in response.data:
                return response.data['count']
            elif 'results' in response.data and isinstance(response.data['results'], list):
                return len(response.data['results'])
        return 0
