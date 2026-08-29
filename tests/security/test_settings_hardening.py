"""設定層的資安不變式。

**刻意直接讀 `IC_alumni.settings`（正式設定模組），不是讀 `tests.settings_test`。**
否則會出現最糟的一種假象：有人為了讓測試好跑而在測試設定裡放寬某項限制，
結果測試依然全綠，但正式環境已經破洞。

這裡驗證的都是「不論誰改、改成什麼，都不該退步」的性質。每一條失敗訊息都寫明
為什麼這條設定重要，讓看到紅燈的人不需要回頭考古。
"""
import importlib
import os
from datetime import timedelta

import pytest
from django.core.management import call_command

import IC_alumni.settings as prod

pytestmark = pytest.mark.security


# ══════════════════════════════════════════════════════════════════════
# 預設拒絕
# ══════════════════════════════════════════════════════════════════════
def test_default_permission_is_deny():
    """DRF 全域預設權限必須是 IsAuthenticated。

    這是整個授權模型的地基：預設拒絕之下，「忘記在新 view 上加權限」的後果是
    該端點無法使用（會馬上被發現），而不是靜悄悄地對全世界開放。
    """
    assert prod.REST_FRAMEWORK["DEFAULT_PERMISSION_CLASSES"] == (
        "rest_framework.permissions.IsAuthenticated",
    ), "DEFAULT_PERMISSION_CLASSES 被改動——這會讓所有未顯式設定權限的端點改變行為。"


def test_browsable_api_renderer_is_disabled():
    """不得啟用 DRF 的 Browsable API。

    它會在正式站上提供一個可互動的 HTML 介面，完整列出可用動作與欄位，
    等同免費送給攻擊者一份 API 說明書，也讓 CSRF 的攻擊面變大。
    """
    renderers = prod.REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"]
    assert "rest_framework.renderers.BrowsableAPIRenderer" not in renderers
    assert renderers == ("rest_framework.renderers.JSONRenderer",)


def test_debug_is_off_by_default():
    assert prod.DEBUG is False, "正式設定模組的 DEBUG 必須硬性為 False。"


# ══════════════════════════════════════════════════════════════════════
# 密鑰
# ══════════════════════════════════════════════════════════════════════
def test_secret_key_is_not_hardcoded():
    """SECRET_KEY 必須來自環境變數，原始碼裡不得有字面值。

    公開 repo 中一旦寫死 SECRET_KEY，任何人都能偽造 session、簽出合法 JWT。
    """
    import inspect

    source = inspect.getsource(prod)
    assert 'SECRET_KEY = os.getenv("SECRET_KEY")' in source, (
        "SECRET_KEY 的取得方式被改動了。它必須是 os.getenv(\"SECRET_KEY\")，"
        "不得出現任何字面值或預設值。"
    )


def test_jwt_signing_key_is_configurable_separately():
    """JWT 簽章金鑰可與 Django SECRET_KEY 分離，才能各自輪換。"""
    assert prod.SIMPLE_JWT["SIGNING_KEY"], "JWT SIGNING_KEY 不得為空。"
    assert prod.SIMPLE_JWT["ALGORITHM"] == "HS256"


def test_access_token_lifetime_is_bounded():
    """存取權杖有效期不得過長。

    本專案的 JWT 沒有主動撤銷機制（沒有比對黑名單的 access token），有效期
    就等於「帳號被盜之後攻擊者還能用多久」的上限。
    """
    lifetime = prod.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"]
    assert lifetime <= timedelta(hours=12), (
        f"ACCESS_TOKEN_LIFETIME 目前為 {lifetime}，超過 12 小時。"
    )


# ══════════════════════════════════════════════════════════════════════
# Cookie 與傳輸安全
# ══════════════════════════════════════════════════════════════════════
def test_jwt_is_delivered_via_httponly_cookie():
    """JWT 以 HttpOnly cookie 交付（SEC-015），前端 JS 讀不到。"""
    assert prod.JWT_COOKIE_NAME == "access_token"


def test_csrf_cookie_must_stay_readable_by_javascript():
    """CSRF token cookie 必須可被 JS 讀取——這是刻意的，不是漏設。

    cookie 型 JWT 認證需要前端把 csrftoken 值放進 X-CSRFToken header 才能通過
    `CookieJWTAuthentication._enforce_csrf`。把它設成 HttpOnly 會讓所有寫入請求
    直接壞掉。這條測試存在的目的是防止有人「順手加強安全性」而弄壞登入流程。
    """
    assert prod.CSRF_COOKIE_HTTPONLY is False


def test_https_security_flags_turn_on_together():
    """`ENABLE_HTTPS_SECURITY=1` 時，HSTS 與 Secure cookie 必須一起生效。

    這些旗標是綁在一起的：只開 SECURE_SSL_REDIRECT 而沒開 SESSION_COOKIE_SECURE，
    等於重導到 HTTPS 之後 cookie 仍可經明文通道外洩。
    """
    previous = os.environ.get("ENABLE_HTTPS_SECURITY")
    os.environ["ENABLE_HTTPS_SECURITY"] = "1"
    try:
        hardened = importlib.reload(prod)
        assert hardened.SECURE_SSL_REDIRECT is True
        assert hardened.SESSION_COOKIE_SECURE is True
        assert hardened.CSRF_COOKIE_SECURE is True
        assert hardened.SECURE_HSTS_SECONDS >= 31_536_000
        assert hardened.SECURE_HSTS_INCLUDE_SUBDOMAINS is True
        assert hardened.JWT_COOKIE_SECURE is True
        # 跨網域部署（前端與 API 不同網域）下 cookie 必須 SameSite=None，
        # 而瀏覽器規範要求 SameSite=None 一定要搭配 Secure。
        assert hardened.JWT_COOKIE_SAMESITE == "None"
    finally:
        if previous is None:
            os.environ.pop("ENABLE_HTTPS_SECURITY", None)
        else:
            os.environ["ENABLE_HTTPS_SECURITY"] = previous
        importlib.reload(prod)


def test_clickjacking_and_mime_sniffing_protections_are_on():
    assert prod.X_FRAME_OPTIONS == "DENY"
    assert prod.SECURE_CONTENT_TYPE_NOSNIFF is True


# ══════════════════════════════════════════════════════════════════════
# CORS / CSRF 來源
# ══════════════════════════════════════════════════════════════════════
def test_cors_is_a_whitelist_not_a_wildcard():
    """允許帶憑證的 CORS 絕不可搭配萬用來源。

    `CORS_ALLOW_CREDENTIALS=True` + 萬用來源 = 任何網站都能用受害者的 cookie
    呼叫本 API。瀏覽器其實會擋掉這個組合，但別依賴瀏覽器來守這條線。
    """
    assert prod.CORS_ALLOW_ALL_ORIGINS is False
    assert "*" not in prod.CORS_ALLOWED_ORIGINS
    assert prod.CORS_ALLOW_CREDENTIALS is True


def test_dev_origins_are_off_unless_explicitly_enabled():
    """localhost 任意 port 的 CORS 放行預設必須關閉（fail-safe）。"""
    previous = os.environ.get("ENABLE_DEV_ORIGINS")
    os.environ["ENABLE_DEV_ORIGINS"] = "0"
    try:
        strict = importlib.reload(prod)
        assert strict.CORS_ALLOWED_ORIGIN_REGEXES == [], (
            "未設定 ENABLE_DEV_ORIGINS 時不得放行任意 localhost port。"
        )
        # 關閉時，CSRF 信任來源不得比 CORS 白名單多出任何項目。
        assert set(strict.CSRF_TRUSTED_ORIGINS) == set(strict.CORS_ALLOWED_ORIGINS)
    finally:
        if previous is None:
            os.environ.pop("ENABLE_DEV_ORIGINS", None)
        else:
            os.environ["ENABLE_DEV_ORIGINS"] = previous
        importlib.reload(prod)


def test_cors_whitelist_is_pinned():
    """CORS 白名單的內容被釘死，任何新增都必須是刻意修改這份測試才做得到。

    白名單上的每個網域都能帶著使用者的 cookie 呼叫本 API，等同完全信任該網域
    上的所有 JavaScript。清單長大是攻擊面長大，不該在 review 中被一行 diff 蓋過去。

    註：`http://localhost:3000` 目前**常駐**在正式白名單裡（不受
    `ENABLE_DEV_ORIGINS` 控制）。實務風險低（攻擊者得先能在受害者機器的
    3000 port 上供應內容），但這是可以清掉的殘留；清掉時記得同步改這份清單。
    """
    assert set(prod.CORS_ALLOWED_ORIGINS) == {
        "http://localhost:3000",
        "https://nkusticalumni.org",
        "https://aaic.nkust.edu.tw",
        "https://nkust_alumni_api.binbinbob.work",
    }


def test_csrf_trusted_origins_stay_in_sync_with_cors():
    """CSRF 信任來源沿用 CORS 白名單，避免兩份清單各自漂移。"""
    assert set(prod.CORS_ALLOWED_ORIGINS) <= set(prod.CSRF_TRUSTED_ORIGINS)


# ══════════════════════════════════════════════════════════════════════
# 節流
# ══════════════════════════════════════════════════════════════════════
@pytest.mark.parametrize(
    "scope,max_per_window",
    [
        ("login", 30),
        ("password_reset", 20),
        ("register", 60),
        ("contact", 60),
    ],
)
def test_auth_endpoints_are_throttled(scope, max_per_window):
    """認證相關端點必須有嚴格節流，否則等於開放暴力破解。"""
    rates = prod.REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"]
    assert scope in rates, f"缺少 '{scope}' 節流設定。"

    count = int(rates[scope].split("/")[0])
    assert count <= max_per_window, (
        f"'{scope}' 節流放寬到 {rates[scope]}，超過建議上限 {max_per_window}。"
    )


def test_throttling_uses_trusted_proxy_count():
    """節流取 client IP 時必須只信任固定層數的代理。

    沒有 NUM_PROXIES，DRF 會直接採信 X-Forwarded-For 的最左側值——那是攻擊者
    完全可控的字串，改一下就能無限繞過節流。
    """
    assert "NUM_PROXIES" in prod.REST_FRAMEWORK
    assert isinstance(prod.REST_FRAMEWORK["NUM_PROXIES"], int)


# ══════════════════════════════════════════════════════════════════════
# 密碼政策
# ══════════════════════════════════════════════════════════════════════
def test_password_validators_are_enabled():
    """密碼強度驗證器不得被清空。

    `PasswordResetConfirmView` 直接呼叫 `validate_password`；清空驗證器會讓
    使用者能把密碼重設成 "123456"，而相關測試依然全綠。
    """
    names = {v["NAME"].rsplit(".", 1)[-1] for v in prod.AUTH_PASSWORD_VALIDATORS}
    assert {
        "MinimumLengthValidator",
        "CommonPasswordValidator",
        "NumericPasswordValidator",
    } <= names


# ══════════════════════════════════════════════════════════════════════
# API 文件揭露
# ══════════════════════════════════════════════════════════════════════
def test_api_docs_are_not_exposed_by_default(client):
    """Swagger / Redoc 預設不對外開放（SEC-020）。

    它會完整列出所有端點、參數與資料模型，大幅降低攻擊門檻。
    需要時以 `EXPOSE_API_DOCS=1` 明確開啟。
    """
    for path in ("/server/api/swagger/", "/server/api/redoc/"):
        assert client.get(path).status_code == 404, (
            f"{path} 不應在預設設定下可存取。"
        )


# ══════════════════════════════════════════════════════════════════════
# Django 內建部署檢查
# ══════════════════════════════════════════════════════════════════════
def test_django_system_check_reports_no_errors():
    """`manage.py check` 不得有任何 ERROR 級別問題。"""
    call_command("check", fail_level="ERROR")
