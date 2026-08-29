"""節流（rate limiting）是否真的接上了。

`settings.REST_FRAMEWORK['DEFAULT_THROTTLE_RATES']` 裡寫了 `'login': '10/min'`
不代表登入端點真的有節流——還必須在 view 上寫 `throttle_scope = 'login'`。
少了那一行，設定看起來很完整，暴力破解卻毫無阻礙，而且靜態檢查與 code review
都很難發現。這組測試把「scope 有沒有接上」變成會失敗的紅燈。

實作說明：DRF 的 `APIView.throttle_classes` 與 `SimpleRateThrottle.THROTTLE_RATES`
都是在 **class 定義時**就從 `api_settings` 取值綁定的類別屬性，`override_settings`
改不動它們。所以這裡直接 monkeypatch 那兩個類別屬性——測到的仍然是真正的節流機制
與 view 上的 scope 宣告，只是繞過 DRF 的設定快取。
"""
import pytest
from django.core.cache import cache
from rest_framework.test import APIClient
from rest_framework.throttling import ScopedRateThrottle

from tests import factories

pytestmark = [pytest.mark.security, pytest.mark.django_db]


@pytest.fixture
def scoped_throttle(monkeypatch):
    """以極低的額度啟用 ScopedRateThrottle，回傳一個「套用到某個 view」的函式。"""
    cache.clear()

    def apply(view_class, rates):
        monkeypatch.setattr(view_class, "throttle_classes", [ScopedRateThrottle])
        monkeypatch.setattr(ScopedRateThrottle, "THROTTLE_RATES", rates)

    yield apply
    cache.clear()


def _hammer(client, method, url, payload, times):
    """連打同一支端點 N 次，回傳狀態碼序列。"""
    return [
        getattr(client, method)(url, payload, format="json").status_code
        for _ in range(times)
    ]


def test_login_is_rate_limited(scoped_throttle, db):
    """登入端點必須有 'login' scope，否則等於開放密碼暴力破解。"""
    from apps.private.views import LoginView

    assert LoginView.throttle_scope == "login", "LoginView 缺少 throttle_scope = 'login'"
    scoped_throttle(LoginView, {"login": "3/min"})

    user = factories.PrivateFactory(email="brute@example.invalid")
    statuses = _hammer(
        APIClient(), "post", "/basic/login",
        {"email": user.email, "password": "wrong"}, times=5,
    )
    assert 429 in statuses, f"連續 5 次登入失敗未觸發節流：{statuses}"


def test_password_reset_request_is_rate_limited(scoped_throttle, db):
    """忘記密碼端點會寄信，沒有節流就同時是暴力破解入口與寄信轟炸工具。"""
    from apps.private.views import PasswordResetRequestView

    assert PasswordResetRequestView.throttle_scope == "password_reset"
    scoped_throttle(PasswordResetRequestView, {"password_reset": "2/min"})

    statuses = _hammer(
        APIClient(), "post", "/basic/forgot_password",
        {"email": "someone@example.invalid"}, times=4,
    )
    assert 429 in statuses, f"忘記密碼端點未觸發節流：{statuses}"


def test_password_reset_confirm_is_rate_limited(scoped_throttle, db):
    """驗證碼只有 6 位數，沒有節流的話純暴力猜測是可行的攻擊。"""
    from apps.private.views import PasswordResetConfirmView

    assert PasswordResetConfirmView.throttle_scope == "password_reset"
    scoped_throttle(PasswordResetConfirmView, {"password_reset": "2/min"})

    statuses = _hammer(
        APIClient(), "post", "/basic/forgot_verify",
        {"email": "someone@example.invalid", "code": "000000", "new_password": "Whatever1!"},
        times=4,
    )
    assert 429 in statuses, f"驗證碼確認端點未觸發節流：{statuses}"


def test_registration_is_rate_limited(scoped_throttle, db):
    """註冊端點沒有節流，等於開放自動化灌帳號。"""
    from apps.private.views import MemberRegisterView

    assert MemberRegisterView.throttle_scope == "register"
    scoped_throttle(MemberRegisterView, {"register": "2/hour"})

    statuses = _hammer(APIClient(), "post", "/basic/register", {"name": "灌水"}, times=4)
    assert 429 in statuses, f"註冊端點未觸發節流：{statuses}"


def test_contact_form_is_rate_limited(scoped_throttle, db):
    """公開的聯絡表單沒有節流，等於開放垃圾訊息轟炸。"""
    from apps.record.contact_views import ContactCreateView

    assert ContactCreateView.throttle_scope == "contact"
    scoped_throttle(ContactCreateView, {"contact": "2/hour"})

    statuses = _hammer(
        APIClient(), "post", "/record/contact/",
        {"name": "spam", "email": "spam@example.invalid", "message": "spam"}, times=4,
    )
    assert 429 in statuses, f"聯絡表單未觸發節流：{statuses}"
