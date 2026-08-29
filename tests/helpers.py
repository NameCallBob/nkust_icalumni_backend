"""測試共用工具。"""
import re

# router 產生的 pk 佔位符：`(?P<pk>[^/.]+)`。做逐條路由的黑箱請求時要換成具體值。
_NAMED_GROUP = re.compile(r"\(\?P<(?P<name>\w+)>[^)]*\)")

_PLACEHOLDER_VALUES = {
    "pk": "1",
    "id": "1",
    "path": "example.png",
    "format": "json",
}


def concrete_url(path: str) -> str:
    """把含 regex 群組的路由 pattern 轉成一個可以真的發出請求的 URL。

    權限檢查發生在 DRF 的 `initial()`，早於 view handler 取用 pk，所以就算 pk=1
    對應的物件不存在，也不影響「匿名應被擋下」這件事的驗證。
    """

    def replace(match):
        return _PLACEHOLDER_VALUES.get(match.group("name"), "1")

    return "/" + _NAMED_GROUP.sub(replace, path)


# HTTP 安全動詞——不改變伺服器狀態，唯讀公開的權限類別對這些放行匿名。
SAFE_METHODS = ("GET", "HEAD", "OPTIONS")

# 全部 HTTP 動詞——APIView 路由沒有 router 的 actions 對照表，只能逐一嘗試。
ALL_METHODS = ("get", "post", "put", "patch", "delete")

# 「被擋下來」的合法回應：
#   401 有認證機制但未提供憑證（CookieJWTAuthentication 會帶 WWW-Authenticate）
#   403 已判定為匿名且權限不足（authentication_classes=[] 時 DRF 回這個）
DENIED_STATUSES = (401, 403)

# 「這個動詞這條路由不支援」——不算通過也不算失敗，跳過即可。
NOT_APPLICABLE_STATUSES = (405,)


def join_background_threads(timeout=5.0):
    """等待專案自行 spawn 的背景執行緒跑完。

    寄信在多處是 `threading.Thread(target=...).start()` 後就不管了（不 join），
    所以「有沒有寄信」這件事在測試裡天生是個競態。這個函式把它變成確定性的：
    先等執行緒結束，再做斷言。

    刻意跳過 ThreadPoolExecutor 的常駐 worker——它們會一直活著等新任務，
    join 下去只會白等到逾時。
    """
    import threading

    persistent_prefixes = ("crud_log", "monitoring_log", "ThreadPoolExecutor")
    main = threading.main_thread()
    for thread in list(threading.enumerate()):
        if thread is main or not thread.is_alive() or thread.daemon:
            continue
        if thread.name.startswith(persistent_prefixes):
            continue
        thread.join(timeout)
