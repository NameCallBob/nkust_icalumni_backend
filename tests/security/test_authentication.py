"""登入／登出／身分驗證的行為契約。

本專案的認證是「HttpOnly cookie 型 JWT + CSRF double-submit」（SEC-015），
比單純的 Bearer header 多了幾個容易改壞的接縫：

* token 絕不能出現在 JSON body（否則前端又會存回 localStorage，XSS 就能偷）
* cookie 分支必須驗 CSRF，header 分支不驗（header 天生免疫 CSRF）
* 登入失敗的回應不得洩漏「這個 email 有沒有註冊」

這些都不是靠讀程式碼能穩住的性質，必須用實際請求釘死。
"""
import pytest
from rest_framework.test import APIClient

from tests import factories

pytestmark = [pytest.mark.security, pytest.mark.django_db]

LOGIN_URL = "/basic/login"
LOGOUT_URL = "/basic/logout"
WHOAMI_URL = "/basic/whoami"


@pytest.fixture
def credentials(db):
    user = factories.PrivateFactory(email="login-test@example.invalid")
    return user, {"email": user.email, "password": user.raw_password}


# ══════════════════════════════════════════════════════════════════════
# 登入成功路徑
# ══════════════════════════════════════════════════════════════════════
def test_login_succeeds_and_sets_httponly_cookie(anon_client, credentials):
    user, payload = credentials
    response = anon_client.post(LOGIN_URL, payload, format="json")

    assert response.status_code == 200
    cookie = response.cookies.get("access_token")
    assert cookie is not None, "登入成功必須以 Set-Cookie 交付 access token。"
    assert cookie["httponly"], "access_token cookie 必須是 HttpOnly，否則 XSS 可竊取。"
    assert cookie["path"] == "/"


def test_login_response_body_never_contains_the_token(anon_client, credentials):
    """token 不得出現在回應 body——這是 SEC-015 的整個重點。

    只要 body 裡還有 token，前端就會（或遲早會）把它存進 localStorage，
    HttpOnly cookie 提供的防護就白做了。
    """
    _, payload = credentials
    response = anon_client.post(LOGIN_URL, payload, format="json")

    body = response.content.decode()
    assert "token" not in body.lower(), f"登入回應 body 疑似含有 token：{body}"
    assert set(response.data) == {"message", "is_super"}


def test_login_normalizes_email_case(anon_client, credentials):
    """email 是登入帳號，大小寫不得造成登入失敗。"""
    user, payload = credentials
    response = anon_client.post(
        LOGIN_URL, {**payload, "email": user.email.upper()}, format="json"
    )
    assert response.status_code == 200


def test_login_reports_superuser_status(anon_client, db):
    admin = factories.PrivateFactory(
        email="admin-login@example.invalid", is_staff=True, is_superuser=True
    )
    response = anon_client.post(
        LOGIN_URL, {"email": admin.email, "password": admin.raw_password}, format="json"
    )
    assert response.status_code == 200
    assert response.data["is_super"] is True


# ══════════════════════════════════════════════════════════════════════
# 登入失敗路徑：不得洩漏帳號是否存在
# ══════════════════════════════════════════════════════════════════════
def test_wrong_password_and_unknown_account_are_indistinguishable(anon_client, credentials):
    """帳號列舉防護（MED-3）：兩種失敗必須回完全相同的狀態碼與內容。

    只要兩者有任何差異，攻擊者就能拿一份 email 名單掃出「哪些人是本站會員」——
    對系友會這種成員身分本身就是個資的網站，這件事比密碼外洩更難補救。
    """
    user, payload = credentials

    wrong_password = anon_client.post(
        LOGIN_URL, {"email": user.email, "password": "definitely-not-the-password"},
        format="json",
    )
    unknown_account = anon_client.post(
        LOGIN_URL, {"email": "nobody-here@example.invalid", "password": payload["password"]},
        format="json",
    )

    assert wrong_password.status_code == unknown_account.status_code == 400
    assert wrong_password.content == unknown_account.content


def test_failed_login_sets_no_cookie(anon_client, credentials):
    user, _ = credentials
    response = anon_client.post(
        LOGIN_URL, {"email": user.email, "password": "wrong"}, format="json"
    )
    assert response.status_code == 400
    assert "access_token" not in response.cookies


def test_disabled_account_with_correct_password_gets_403(anon_client, db):
    """停用帳號 + 正確密碼 → 403，讓前端能顯示「帳號已停用」。

    這是刻意保留的資訊差異：能觸發它的人本來就已經知道正確密碼，
    不構成額外的列舉風險。
    """
    user = factories.PrivateFactory(email="disabled@example.invalid", is_active=False)
    response = anon_client.post(
        LOGIN_URL, {"email": user.email, "password": user.raw_password}, format="json"
    )
    assert response.status_code == 403


def test_disabled_account_with_wrong_password_looks_like_any_other_failure(anon_client, db):
    """停用帳號 + 錯誤密碼 → 與一般失敗無異，不得洩漏帳號存在。"""
    user = factories.PrivateFactory(email="disabled2@example.invalid", is_active=False)
    response = anon_client.post(
        LOGIN_URL, {"email": user.email, "password": "wrong"}, format="json"
    )
    assert response.status_code == 400


def test_login_with_missing_fields_does_not_crash(anon_client):
    for payload in ({}, {"email": ""}, {"password": "x"}, {"email": None, "password": None}):
        response = anon_client.post(LOGIN_URL, payload, format="json")
        assert response.status_code < 500, f"payload={payload} 造成伺服器錯誤"


# ══════════════════════════════════════════════════════════════════════
# whoami / logout
# ══════════════════════════════════════════════════════════════════════
def test_whoami_requires_authentication(anon_client):
    assert anon_client.get(WHOAMI_URL).status_code == 401


def test_whoami_identifies_the_current_user(member_client, staff_client, super_client):
    assert member_client.get(WHOAMI_URL).data["is_super"] is False
    assert staff_client.get(WHOAMI_URL).data["is_super"] is False
    assert super_client.get(WHOAMI_URL).data["is_super"] is True


def test_logout_expires_the_cookie(anon_client, credentials):
    _, payload = credentials
    anon_client.post(LOGIN_URL, payload, format="json")

    response = anon_client.post(LOGOUT_URL)
    assert response.status_code == 200
    assert response.cookies["access_token"].value == ""


def test_logout_is_idempotent_for_anonymous_callers(anon_client):
    """未登入呼叫 logout 也必須是 200。

    前端在各種狀態下都會直接打這支（例如 token 已過期後點登出），
    回 401 會讓使用者卡在「登不出去」的狀態。
    """
    assert anon_client.post(LOGOUT_URL).status_code == 200


# ══════════════════════════════════════════════════════════════════════
# Cookie 認證的 CSRF 防護
# ══════════════════════════════════════════════════════════════════════
def test_cookie_auth_rejects_write_without_csrf_token(credentials):
    """帶著有效 cookie 但沒有 X-CSRFToken 的寫入請求必須被拒絕。

    cookie 是瀏覽器自動附帶的，沒有這道檢查，任何網站都能誘導已登入的使用者
    對本 API 發出寫入請求。這正是 `CookieJWTAuthentication._enforce_csrf` 的職責。
    """
    client = APIClient(enforce_csrf_checks=True)
    _, payload = credentials
    login = client.post(LOGIN_URL, payload, format="json")
    assert login.status_code == 200

    response = client.patch(
        "/member/logined/partial_change/", {"name": "改名"}, format="json"
    )
    assert response.status_code == 403, (
        "cookie 認證的寫入請求在缺少 CSRF token 時必須被擋下。"
    )


def test_cookie_auth_accepts_write_with_csrf_token(credentials, member):
    """附上 csrftoken 之後，同一個寫入請求要能成功通過認證。

    與上一條成對存在：只驗證「擋得住」而沒驗證「放得行」，很容易寫出一個
    把所有寫入都擋死、但測試全綠的 CSRF 實作。
    """
    client = APIClient(enforce_csrf_checks=True)
    user = member.private
    login = client.post(
        LOGIN_URL, {"email": user.email, "password": user.raw_password}, format="json"
    )
    assert login.status_code == 200

    csrf_token = login.cookies["csrftoken"].value
    response = client.patch(
        "/member/logined/partial_change/",
        {"name": "新名字"},
        format="json",
        HTTP_X_CSRFTOKEN=csrf_token,
    )
    assert response.status_code != 403, (
        f"帶了 CSRF token 仍被拒絕：{response.status_code} {response.content[:200]}"
    )


def test_read_requests_do_not_require_csrf_token(credentials):
    """GET 不需要 CSRF token——它不改變狀態，強制檢查只會讓前端無法讀資料。"""
    client = APIClient(enforce_csrf_checks=True)
    _, payload = credentials
    client.post(LOGIN_URL, payload, format="json")

    assert client.get(WHOAMI_URL).status_code == 200


def test_bearer_header_auth_still_works(credentials):
    """向下相容：Authorization: Bearer <token> 仍可通過認證，且不需要 CSRF。

    header 分支天生免疫 CSRF（攻擊者無法讓瀏覽器自動附上自訂 header），
    所以刻意不對它做 CSRF 檢查。
    """
    from rest_framework_simplejwt.tokens import RefreshToken

    user, _ = credentials
    token = str(RefreshToken.for_user(user).access_token)

    client = APIClient(enforce_csrf_checks=True)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    assert client.get(WHOAMI_URL).status_code == 200


def test_invalid_token_is_rejected(anon_client):
    anon_client.credentials(HTTP_AUTHORIZATION="Bearer not-a-real-jwt")
    assert anon_client.get(WHOAMI_URL).status_code == 401


def test_token_signed_with_a_different_key_is_rejected(credentials):
    """用別的金鑰簽出來的 JWT 必須被拒絕——避免簽章驗證被繞過。"""
    import jwt as pyjwt

    user, _ = credentials
    forged = pyjwt.encode(
        {"user_id": user.id, "token_type": "access", "exp": 9_999_999_999, "jti": "x"},
        "an-entirely-different-secret-of-sufficient-length",
        algorithm="HS256",
    )
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {forged}")
    assert client.get(WHOAMI_URL).status_code == 401
