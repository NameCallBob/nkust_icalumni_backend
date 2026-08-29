"""全域測試夾具（fixtures）與安全防護。

本檔案定義三類東西：

1. **防護（autouse）**——確保測試不會打網路、不會寄真信、不會被背景執行緒污染。
   這些是 autouse 的，新加的測試自動受保護，不需要作者記得做什麼。
2. **身分夾具**——`anon_client` / `member_client` / `staff_client` / `super_client`，
   對應本專案四種權限層級（匿名 / 一般會員 / staff / superuser）。
3. **資料夾具**——薄薄一層包住 `tests/factories.py`，方便直接注入。

新增測試時的建議：優先用夾具，不要在測試裡自己 `Private.objects.create_user(...)`，
否則權限層級的定義會散落各處，日後權限模型一改就得改幾十個檔案。
"""
import socket

import pytest
from rest_framework.test import APIClient

from tests import factories


# ══════════════════════════════════════════════════════════════════════
# 防護：任何測試都不得對外連線
# ══════════════════════════════════════════════════════════════════════
class OutboundNetworkBlocked(RuntimeError):
    """測試期間嘗試對外連線時拋出。

    看到這個例外代表：某段程式碼在測試中打了真實網路（Resend、SMTP、GeoIP 下載、
    第三方 API…）。正確處理方式是在測試中把它 mock 掉，而不是放寬這道防線——
    會打網路的測試在 CI 上必然變成隨機失敗，而且可能對真實使用者產生副作用。
    """


@pytest.fixture(autouse=True)
def _block_outbound_network(monkeypatch):
    """封鎖所有對外 TCP 連線，但保留 loopback（測試資料庫/測試伺服器需要）。"""
    real_connect = socket.socket.connect
    real_connect_ex = socket.socket.connect_ex

    def _is_loopback(address):
        if not isinstance(address, tuple) or not address:
            return False
        host = address[0]
        return host in ("127.0.0.1", "::1", "localhost", "")

    def guarded_connect(self, address, *args, **kwargs):
        if _is_loopback(address):
            return real_connect(self, address, *args, **kwargs)
        raise OutboundNetworkBlocked(
            f"測試嘗試對外連線 {address!r}。請 mock 掉該外部呼叫；"
            f"詳見 tests/conftest.py 的 OutboundNetworkBlocked 說明。"
        )

    def guarded_connect_ex(self, address, *args, **kwargs):
        if _is_loopback(address):
            return real_connect_ex(self, address, *args, **kwargs)
        raise OutboundNetworkBlocked(f"測試嘗試對外連線 {address!r}")

    monkeypatch.setattr(socket.socket, "connect", guarded_connect)
    monkeypatch.setattr(socket.socket, "connect_ex", guarded_connect_ex)
    yield


# ══════════════════════════════════════════════════════════════════════
# 防護：攔截寄信
# ══════════════════════════════════════════════════════════════════════
@pytest.fixture(autouse=True)
def sent_emails(monkeypatch):
    """攔截 Resend 寄信並記錄下來，回傳一個 list 供測試斷言。

    `apps.notice.email.send_order_email` 是全專案唯一的寄信出口：先試 Resend
    HTTP API，失敗才退回 Django SMTP。這裡把 Resend 那一層換成記錄器並回傳
    True，於是 SMTP 備援不會被觸發，整條寄信路徑都不出網路。

    用法::

        def test_forgot_password_sends_code(anon_client, member_user, sent_emails):
            anon_client.post("/basic/forgot_password", {"email": member_user.email})
            assert len(sent_emails) == 1
            assert sent_emails[0]["to"] == member_user.email
    """
    recorded = []

    def _record(subject, html_content, to_email, text_content=None):
        recorded.append(
            {
                "subject": subject,
                "to": to_email,
                "html": html_content,
                "text": text_content,
            }
        )
        return True

    monkeypatch.setattr("apps.notice.email.send_email_resend", _record)
    return recorded


# ══════════════════════════════════════════════════════════════════════
# 防護：背景執行緒
# ══════════════════════════════════════════════════════════════════════
@pytest.fixture(autouse=True)
def _synchronous_background_work(monkeypatch):
    """把寄信用的背景 thread 改為同步 no-op，並讓 CRUDLog 的 executor 不落 DB。

    專案在多處用 `threading.Thread(target=寄信).start()` 與 ThreadPoolExecutor
    寫入操作記錄。對 in-memory SQLite 而言，背景執行緒的 DB 寫入是另一條連線，
    會造成隨機的鎖競爭；而且它會污染 `assertNumQueries` 的查詢計數。

    `apps.record.signals` 的行為另有專屬測試（tests/api/test_record_monitoring.py）
    以 `crud_logging_enabled` 夾具明確開啟後驗證。
    """
    import apps.record.signals as record_signals

    monkeypatch.setattr(
        record_signals._crud_log_executor,
        "submit",
        lambda fn, *a, **kw: None,
    )
    yield


@pytest.fixture(autouse=True)
def _clear_cache():
    """每個測試前後清空 Django 快取。

    專案有多處用 `cache.set(...)` 快取公開列表（例如首頁輪播 `slides_active_v1`，
    TTL 300 秒）。locmem 快取活在整個 pytest 行程裡，不清就會跨測試汙染——
    A 測試建立的資料會透過快取出現在 B 測試的回應中，症狀是「單獨跑會過、
    整批跑就掛」，而且會隨 pytest-randomly 的隨機順序時好時壞。
    """
    from django.core.cache import cache

    cache.clear()
    yield
    cache.clear()


@pytest.fixture
def crud_logging_enabled(monkeypatch):
    """讓 CRUDLog 改為同步寫入，供監控功能自身的測試使用。"""
    import apps.record.signals as record_signals

    class _Immediate:
        @staticmethod
        def submit(fn, *args, **kwargs):
            fn(*args, **kwargs)

    monkeypatch.setattr(record_signals, "_crud_log_executor", _Immediate)
    monkeypatch.setattr(record_signals._crud_log_executor, "submit", _Immediate.submit)
    yield


# ══════════════════════════════════════════════════════════════════════
# 身分：四種權限層級
# ══════════════════════════════════════════════════════════════════════
@pytest.fixture
def anon_client():
    """未登入的 API 客戶端。"""
    return APIClient()


@pytest.fixture
def member_user(db):
    """一般會員帳號（is_staff=False, is_superuser=False）。"""
    return factories.PrivateFactory(email="member@example.invalid")


@pytest.fixture
def other_member_user(db):
    """另一個一般會員，用於驗證「不得存取他人資料」。"""
    return factories.PrivateFactory(email="other@example.invalid")


@pytest.fixture
def staff_user(db):
    """staff 帳號（is_staff=True，非 superuser）。"""
    return factories.PrivateFactory(email="staff@example.invalid", is_staff=True)


@pytest.fixture
def super_user(db):
    """superuser 帳號。"""
    return factories.PrivateFactory(
        email="super@example.invalid", is_staff=True, is_superuser=True
    )


def _authenticated(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def member_client(member_user):
    return _authenticated(member_user)


@pytest.fixture
def other_member_client(other_member_user):
    return _authenticated(other_member_user)


@pytest.fixture
def staff_client(staff_user):
    return _authenticated(staff_user)


@pytest.fixture
def super_client(super_user):
    return _authenticated(super_user)


@pytest.fixture
def clients(anon_client, member_client, staff_client, super_client):
    """四種身分的對照表，方便寫權限矩陣測試。"""
    return {
        "anon": anon_client,
        "member": member_client,
        "staff": staff_client,
        "super": super_client,
    }


# ══════════════════════════════════════════════════════════════════════
# 資料
# ══════════════════════════════════════════════════════════════════════
@pytest.fixture
def position(db):
    return factories.PositionFactory()


@pytest.fixture
def member(db, member_user):
    """綁定 `member_user` 帳號的會員資料。"""
    return factories.MemberFactory(private=member_user, name="測試會員")


@pytest.fixture
def other_member(db, other_member_user):
    return factories.MemberFactory(
        private=other_member_user,
        name="他人會員",
        home_phone="0212345678",
        mobile_phone="0912345678",
        address="高雄市三民區建工路415號",
        is_show=True,
    )


@pytest.fixture
def industry(db):
    return factories.IndustryFactory()


@pytest.fixture
def company(db, member, industry):
    return factories.CompanyFactory(member=member, industry=industry)
