"""忘記密碼流程的資安契約。

這條流程是所有網站最常被攻破的地方：它必須在「不需要任何憑證」的前提下，
讓真正的帳號持有者換掉密碼。任何一個環節鬆掉，就是完整的帳號接管。

本專案的驗證碼只有 6 位數（10^6 種組合），所以以下每一條防線都是必要的，
少任何一條都會讓暴力猜碼變成可行的攻擊：

* 驗證碼必須綁定 email（不能只憑 code 全域查詢）
* 驗證碼必須會過期
* 用過即失效（且該帳號的其他碼一併作廢）
* 新密碼必須通過強度驗證
* 端點必須節流（見 tests/security/test_throttling.py）
* 回應不得洩漏該 email 是否已註冊
"""
import pytest
from django.utils import timezone

from apps.private.models import PasswordResetCode
from tests import factories
from tests.helpers import join_background_threads

pytestmark = [pytest.mark.security, pytest.mark.django_db]

REQUEST_URL = "/basic/forgot_password"
CONFIRM_URL = "/basic/forgot_verify"
NEW_PASSWORD = "BrandNewPassw0rd!"


@pytest.fixture
def account(db):
    return factories.PrivateFactory(email="reset-target@example.invalid")


def _issue_code(client, user):
    response = client.post(REQUEST_URL, {"email": user.email}, format="json")
    assert response.status_code == 200
    # 寄信是背景執行緒，等它結束才能對 sent_emails 做斷言。
    join_background_threads()
    return PasswordResetCode.objects.get(private=user)


# ══════════════════════════════════════════════════════════════════════
# 索取驗證碼
# ══════════════════════════════════════════════════════════════════════
def test_requesting_a_code_sends_exactly_one_email(anon_client, account, sent_emails):
    _issue_code(anon_client, account)
    assert len(sent_emails) == 1
    assert sent_emails[0]["to"] == account.email


def test_response_is_identical_for_unknown_emails(anon_client, account):
    """帳號列舉防護（SEC-017）：不論 email 有沒有註冊，回應必須完全相同。"""
    known = anon_client.post(REQUEST_URL, {"email": account.email}, format="json")
    unknown = anon_client.post(
        REQUEST_URL, {"email": "not-registered@example.invalid"}, format="json"
    )
    assert known.status_code == unknown.status_code == 200
    assert known.content == unknown.content


def test_no_code_is_created_for_unknown_emails(anon_client, sent_emails):
    """未註冊的 email 不得產生驗證碼，也不得寄信。

    沒有這道檢查，這支端點就變成一個免費的、可被任意指定收件人的寄信管道。
    """
    anon_client.post(REQUEST_URL, {"email": "nobody@example.invalid"}, format="json")
    join_background_threads()
    assert PasswordResetCode.objects.count() == 0
    assert sent_emails == []


def test_reset_code_is_six_digits(anon_client, account):
    code = _issue_code(anon_client, account)
    assert len(code.code) == 6 and code.code.isdigit()


def test_reset_code_expires(anon_client, account):
    code = _issue_code(anon_client, account)
    assert code.expires_at > timezone.now()
    assert not code.is_expired()


# ══════════════════════════════════════════════════════════════════════
# 使用驗證碼
# ══════════════════════════════════════════════════════════════════════
def test_valid_code_resets_the_password(anon_client, account):
    code = _issue_code(anon_client, account)

    response = anon_client.post(
        CONFIRM_URL,
        {"email": account.email, "code": code.code, "new_password": NEW_PASSWORD},
        format="json",
    )
    assert response.status_code == 200

    account.refresh_from_db()
    assert account.check_password(NEW_PASSWORD)


def test_code_is_bound_to_its_owner_email(anon_client, account, db):
    """A 的驗證碼不得用來重設 B 的密碼（HIGH-1）。

    這是本流程最致命的一條：若驗證碼只用 `code` 全域查詢而不綁 email，
    攻擊者只要猜中「系統中任何一個尚未過期的驗證碼」，就能拿它重設**自己指定**
    的帳號——搜尋空間從「猜中某個特定帳號的碼」塌縮成「猜中任何人的碼」，
    在有一定使用量的站台上是幾分鐘內可完成的攻擊。
    """
    victim = factories.PrivateFactory(email="victim@example.invalid")
    original_hash = victim.password
    code = _issue_code(anon_client, account)

    response = anon_client.post(
        CONFIRM_URL,
        {"email": victim.email, "code": code.code, "new_password": NEW_PASSWORD},
        format="json",
    )
    assert response.status_code == 400

    victim.refresh_from_db()
    assert victim.password == original_hash, "他人的驗證碼竟然改掉了受害者的密碼。"


def test_expired_code_is_rejected_and_deleted(anon_client, account):
    code = _issue_code(anon_client, account)
    code.expires_at = timezone.now() - timezone.timedelta(minutes=1)
    code.save()

    response = anon_client.post(
        CONFIRM_URL,
        {"email": account.email, "code": code.code, "new_password": NEW_PASSWORD},
        format="json",
    )
    assert response.status_code == 400
    assert not PasswordResetCode.objects.filter(pk=code.pk).exists()


def test_code_cannot_be_reused(anon_client, account):
    """單次使用：用過的碼（以及該帳號其他未使用的碼）必須一併作廢。"""
    code = _issue_code(anon_client, account)
    anon_client.post(
        CONFIRM_URL,
        {"email": account.email, "code": code.code, "new_password": NEW_PASSWORD},
        format="json",
    )

    assert PasswordResetCode.objects.filter(private=account).count() == 0

    second = anon_client.post(
        CONFIRM_URL,
        {"email": account.email, "code": code.code, "new_password": "AnotherPassw0rd!"},
        format="json",
    )
    assert second.status_code == 400
    account.refresh_from_db()
    assert account.check_password(NEW_PASSWORD), "已使用的驗證碼竟然還能再改一次密碼。"


def test_wrong_code_is_rejected(anon_client, account):
    _issue_code(anon_client, account)
    original_hash = account.password

    response = anon_client.post(
        CONFIRM_URL,
        {"email": account.email, "code": "000000", "new_password": NEW_PASSWORD},
        format="json",
    )
    assert response.status_code == 400
    account.refresh_from_db()
    assert account.password == original_hash


@pytest.mark.parametrize(
    "weak_password",
    [
        "123456",       # 常見密碼
        "12345678",     # 純數字
        "abc",          # 太短
    ],
)
def test_weak_new_passwords_are_rejected(anon_client, account, weak_password):
    """重設密碼時必須套用與註冊時相同的強度規則。

    重設流程是最容易漏掉密碼驗證的地方——註冊表單有驗證，重設卻直接
    `set_password(request.data['new_password'])`，等於留了一個把所有帳號
    降級成弱密碼的後門。
    """
    code = _issue_code(anon_client, account)
    response = anon_client.post(
        CONFIRM_URL,
        {"email": account.email, "code": code.code, "new_password": weak_password},
        format="json",
    )
    assert response.status_code == 400, f"弱密碼 {weak_password!r} 竟被接受"

    account.refresh_from_db()
    assert not account.check_password(weak_password)


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"email": "reset-target@example.invalid"},
        {"code": "123456"},
        {"new_password": "Something1!"},
        {"email": "", "code": "", "new_password": ""},
    ],
)
def test_incomplete_payloads_are_rejected_cleanly(anon_client, account, payload):
    """缺欄位必須回 400，不能是未處理例外。"""
    response = anon_client.post(CONFIRM_URL, payload, format="json")
    assert response.status_code == 400
