# apps/record/threadlocals.py
"""執行緒本地儲存目前請求物件，供 signals.py 的 CRUD 操作記錄取得操作者/IP 使用。

必須是模組層級的單一 threading.local() 實例；若在每次讀取時才建立新的
local()，等同於永遠拿不到任何資料（先前 bug）。
"""
import threading

_thread_locals = threading.local()


def set_current_request(request):
    _thread_locals.request = request


def get_current_request():
    return getattr(_thread_locals, 'request', None)


def clear_current_request():
    if hasattr(_thread_locals, 'request'):
        del _thread_locals.request
