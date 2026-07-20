# IC_alumni/middlewares/currentRequestMiddleware.py
"""將目前請求存進 thread-local，供 apps/record/signals.py 的 CRUD 操作記錄
取得操作者（request.user）與來源 IP。

所有動作都包在 try/except 內：這支 middleware 只是輔助記錄用途，
發生任何例外都不應該影響原本的請求處理流程。
"""
from django.utils.deprecation import MiddlewareMixin
from apps.record.threadlocals import set_current_request, clear_current_request


class CurrentRequestMiddleware(MiddlewareMixin):

    def process_request(self, request):
        try:
            set_current_request(request)
        except Exception:
            pass
        return None

    def process_response(self, request, response):
        try:
            clear_current_request()
        except Exception:
            pass
        return response

    def process_exception(self, request, exception):
        try:
            clear_current_request()
        except Exception:
            pass
        return None
