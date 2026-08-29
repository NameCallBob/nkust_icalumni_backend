"""測試專用 Django 設定：**完全離線、零外部依賴、零副作用**。

設計原則
--------
1. **不碰網路**：正式設定會打 Resend API 與 Gmail SMTP。測試改用 locmem 郵件
   後端，並在 ``tests/conftest.py`` 以 autouse fixture 封鎖 socket，確保任何
   新增的程式碼一旦偷連外部服務，測試會立刻失敗而不是安靜地寄出真信。
2. **不碰正式資料庫**：一律 SQLite in-memory，CI 與本機行為一致。
3. **設定不變式可被驗證**：`tests/security/test_settings_hardening.py` 直接讀
   `IC_alumni.settings`（正式設定模組）做斷言，不是讀這份，避免「測試設定放寬了
   所以測試通過」的假象。

使用方式（pytest.ini 已預設指向此模組）::

    pytest
    DJANGO_SETTINGS_MODULE=tests.settings_test python manage.py test
"""
import os
import tempfile

# 正式設定在 import 期就會讀取這些環境變數；先給定值，讓這份設定在任何
# 乾淨環境（CI、新 clone 的機器、沒有 .env 的容器）都能匯入成功。
os.environ.setdefault("SECRET_KEY", "test-only-secret-key-not-used-anywhere-else")
os.environ.setdefault("ENABLE_DEV_ORIGINS", "1")
os.environ.setdefault("RESEND_API_KEY", "test-not-a-real-key")

from IC_alumni.settings import *  # noqa: F401,F403,E402

# ── 資料庫 ───────────────────────────────────────────────────────────────
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
        "TEST": {"NAME": ":memory:"},
    }
}

# ── 執行環境 ─────────────────────────────────────────────────────────────
DEBUG = False
# DEBUG=False 時 Django 需要 ALLOWED_HOSTS 允許測試客戶端的 "testserver"。
ALLOWED_HOSTS = ["testserver", "localhost", "127.0.0.1"]

# ── 郵件：locmem，不出網路，且可用 django.core.mail.outbox 斷言 ────────────
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
DEFAULT_FROM_EMAIL = "test@example.invalid"
EMAIL_HOST_USER = "test@example.invalid"
EMAIL_HOST_PASSWORD = "not-a-real-password"

# ── 密碼雜湊：測試用最快的雜湊，省下大量 PBKDF2 迭代時間 ────────────────────
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
# 保留正式的密碼強度驗證器——`PasswordResetConfirmView` 會呼叫 validate_password，
# 清空驗證器會讓「弱密碼應被拒絕」的測試變成永遠通過的假測試。

# ── 快取：locmem，不需要 Redis ───────────────────────────────────────────
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "test-cache",
    }
}

# ── 檔案上傳：導向暫存目錄，測試不得污染 repo 內的 static/ ────────────────
MEDIA_ROOT = tempfile.mkdtemp(prefix="ic-alumni-test-media-")
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
}

# ── 中介層：拿掉監控中介層 ──────────────────────────────────────────────
# MonitoringMiddleware 會在背景執行緒寫 RequestLog/PerformanceMetric/IPLimit。
# 對 in-memory SQLite 而言那是跨執行緒寫入，會製造隨機的鎖競爭與不可重現的失敗；
# 而且它讓 assertNumQueries 類的查詢預算測試充滿雜訊。
# 監控中介層本身另有專屬測試（tests/api/test_record_monitoring.py）以 override 方式啟用。
MIDDLEWARE = [m for m in MIDDLEWARE if "recordUserMiddleware" not in m]  # noqa: F405

# ── 節流：預設關閉 ──────────────────────────────────────────────────────
# 全域開著會讓「同一支端點呼叫多次」的功能測試在第 N 次被 429 打掛，
# 且失敗與否取決於執行順序。節流本身由 tests/security/test_throttling.py
# 以 override_settings 明確開啟後驗證。
REST_FRAMEWORK = {**REST_FRAMEWORK}  # noqa: F405
REST_FRAMEWORK["DEFAULT_THROTTLE_CLASSES"] = []
REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"] = {}

# ── 日誌：測試期間不要寫檔、不要吵 ───────────────────────────────────────
LOGGING = {
    "version": 1,
    "disable_existing_loggers": True,
    "handlers": {"null": {"class": "logging.NullHandler"}},
    "root": {"handlers": ["null"], "level": "CRITICAL"},
}

# ── 其他 ────────────────────────────────────────────────────────────────
# 讓 migration 期間不做多餘的 collectstatic 檢查
WHITENOISE_AUTOREFRESH = True
