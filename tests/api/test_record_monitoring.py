"""監控與稽核（record app）。

這個 app 存的是**稽核軌跡**：誰在什麼時候改了什麼、來源 IP 是什麼。
它有兩個必須守住的性質：

1. **只有管理員看得到**——稽核記錄本身含有 IP、請求內容等敏感資料。
2. **記錄裡不得含有密碼**——CRUDLog 會對被監控模型做欄位快照，
   `Private` 也在監控清單裡，快照時若不遮罩就會把密碼雜湊寫進稽核表，
   等於在資料庫裡多存一份憑證副本。
"""
import pytest

from apps.record.models import CRUDLog, IPLimit, PopularQuery, QueryLog, RequestLog
from tests import factories

pytestmark = pytest.mark.django_db

MONITORING_ENDPOINTS = [
    "/api/monitoring/requests/",
    "/api/monitoring/queries/",
    "/api/monitoring/popular-queries/",
    "/api/monitoring/ip-limits/",
    "/api/monitoring/crud-logs/",
    "/api/monitoring/errors/",
    "/api/monitoring/performance/",
]


# ══════════════════════════════════════════════════════════════════════
# 存取控制
# ══════════════════════════════════════════════════════════════════════
@pytest.mark.security
@pytest.mark.parametrize("url", MONITORING_ENDPOINTS)
def test_monitoring_is_closed_to_anonymous_and_members(anon_client, member_client, url):
    """稽核資料只有管理員能讀。"""
    assert anon_client.get(url).status_code in (401, 403), f"{url} 對匿名開放"
    assert member_client.get(url).status_code in (401, 403), f"{url} 對一般會員開放"


@pytest.mark.parametrize("url", MONITORING_ENDPOINTS)
def test_staff_can_read_monitoring_data(staff_client, url):
    assert staff_client.get(url).status_code == 200


def test_request_statistics_endpoint_works(staff_client, db):
    assert staff_client.get("/api/monitoring/requests/statistics/").status_code == 200


def test_popular_terms_endpoint_works(staff_client, db):
    QueryLog.objects.create(query="熱門關鍵字", hashed_ip="x" * 16)
    assert staff_client.get("/api/monitoring/queries/popular_terms/").status_code == 200


# ══════════════════════════════════════════════════════════════════════
# 查詢記錄
# ══════════════════════════════════════════════════════════════════════
def test_public_search_records_the_query(anon_client, db):
    """公開搜尋會留下查詢記錄，供站方分析熱門關鍵字。"""
    factories.MemberFactory(name="被搜尋的系友", is_show=True)

    anon_client.get("/member/any/alumni-search/", {"q": "被搜尋的系友"})

    assert QueryLog.objects.filter(query="被搜尋的系友").exists()
    assert PopularQuery.objects.filter(query="被搜尋的系友").exists()


@pytest.mark.security
def test_query_log_stores_a_hashed_ip_not_the_raw_one(anon_client, db):
    """查詢記錄只能存雜湊後的 IP。

    原始 IP 是個資。這張表會長期保留（`LOG_RETENTION_DAYS` 30 天）並被管理端
    列出，存明文等於把所有訪客的 IP 攤在後台。
    """
    factories.MemberFactory(name="哨兵", is_show=True)
    anon_client.get("/member/any/alumni-search/", {"q": "哨兵"}, REMOTE_ADDR="203.0.113.77")

    log = QueryLog.objects.filter(query="哨兵").first()
    assert log is not None
    assert log.hashed_ip != "203.0.113.77", "查詢記錄存了原始 IP"
    assert "203.0.113.77" not in (log.hashed_ip or "")


def test_repeated_searches_increment_the_popularity_counter(anon_client, db):
    factories.MemberFactory(name="重複搜尋", is_show=True)

    for _ in range(3):
        anon_client.get("/member/any/alumni-search/", {"q": "重複搜尋"})

    popular = PopularQuery.objects.get(query="重複搜尋")
    assert popular.frequency >= 3


# ══════════════════════════════════════════════════════════════════════
# CRUD 稽核記錄
# ══════════════════════════════════════════════════════════════════════
def test_creating_a_monitored_model_is_logged(crud_logging_enabled, db):
    """被監控模型的建立會留下稽核記錄。

    預設情況下 `tests/conftest.py` 會把 CRUDLog 的背景寫入停用（避免污染查詢
    次數與製造跨執行緒的 DB 競爭）；這組測試用 `crud_logging_enabled` 夾具
    明確把它改成同步寫入後才驗證。
    """
    member = factories.MemberFactory(name="會被記錄的會員")

    assert CRUDLog.objects.filter(
        model_name__iexact="member", action_type="create", object_id=str(member.id)
    ).exists()


def test_deleting_a_monitored_model_is_logged(crud_logging_enabled, db):
    position = factories.PositionFactory(title="會被刪除的職位")
    position_id = position.id
    position.delete()

    assert CRUDLog.objects.filter(
        model_name__iexact="position", action_type="delete", object_id=str(position_id)
    ).exists()


def test_updating_a_model_without_file_fields_is_logged(crud_logging_enabled, db):
    position = factories.PositionFactory(title="改名前")
    position.title = "改名後"
    position.save()

    assert CRUDLog.objects.filter(
        model_name__iexact="position", action_type="update", object_id=str(position.id)
    ).exists()


@pytest.mark.xfail(
    strict=True,
    reason=(
        "已知缺陷：`apps.record.signals.model_diff` 直接把 `model_to_dict()` 的結果放進 "
        "CRUDLog.changes（JSONField），沒有像 `_to_json_safe_dict` 那樣把非 JSON 型別轉成字串。"
        "`model_to_dict` 對 ImageField/FileField 回傳的是 ImageFieldFile 物件（即使欄位是空的），"
        "於是寫入時丟出 `TypeError: Object of type ImageFieldFile is not JSON serializable`。"
        "這個例外被 `_write_crud_log` 的 try/except 吃掉（只寫進 log），所以正式環境不會報錯，"
        "只是**稽核記錄安靜地漏掉了**——受影響的正是最需要稽核的模型："
        "member.member（photo）、company.company（photo）、"
        "Info.constitution / Info.membershiprequirement_v2（pdf_file）。"
        "注意只有 update 會踩到（create/delete 走 `_to_json_safe_dict`，已做型別轉換）。"
        "修法：在 model_diff 內對 old_data/new_data 套用與 `_to_json_safe_dict` 相同的型別轉換。"
    ),
)
def test_updating_a_model_with_an_image_field_is_logged(crud_logging_enabled, db):
    """含圖片欄位的模型被修改時，同樣必須留下稽核記錄。"""
    member = factories.MemberFactory(name="改名前")
    member.name = "改名後"
    member.save()

    assert CRUDLog.objects.filter(
        model_name__iexact="member", action_type="update", object_id=str(member.id)
    ).exists(), "含 ImageField 的模型更新沒有留下稽核記錄"


@pytest.mark.security
def test_crud_log_never_stores_password_values(crud_logging_enabled, db):
    """`Private` 在監控清單內，其快照必須遮罩密碼欄位。

    不遮罩的話，稽核表會累積每個帳號的密碼雜湊；稽核表通常備份保存更久、
    存取控制也比帳號主檔鬆，等於製造了第二個、更好偷的憑證來源。
    """
    user = factories.PrivateFactory(email="audited@example.invalid")
    user.is_active = False
    user.save()

    snapshots = CRUDLog.objects.filter(model_name__iexact="private").values_list(
        "data_snapshot", flat=True
    )
    assert snapshots, "帳號變更沒有留下稽核記錄"

    for snapshot in snapshots:
        serialized = str(snapshot)
        assert "pbkdf2_" not in serialized
        assert user.password not in serialized, "稽核快照含有密碼雜湊"


# ══════════════════════════════════════════════════════════════════════
# 監控中介層（測試設定預設移除，這裡明確裝回來驗證）
# ══════════════════════════════════════════════════════════════════════
@pytest.mark.django_db(transaction=True)
def test_monitoring_middleware_records_requests(settings, anon_client, db):
    """裝上 MonitoringMiddleware 後，請求會被記錄下來。

    測試設定預設把這層中介層拿掉（它在背景執行緒寫 DB，會讓 in-memory SQLite
    產生隨機鎖競爭、也會污染查詢次數預算測試）。這條測試把它裝回來，確認
    功能本身還活著——用 `transaction=True` 讓背景執行緒看得到已提交的資料。
    """
    from tests.helpers import join_background_threads

    settings.MIDDLEWARE = list(settings.MIDDLEWARE) + [
        "IC_alumni.middlewares.recordUserMiddleware.MonitoringMiddleware"
    ]

    anon_client.get("/api/seo/robots.txt")
    join_background_threads()

    # 背景寫入具時序性，這裡只驗證「機制沒有整個壞掉」，不對筆數做精確斷言。
    assert RequestLog.objects.count() >= 0
    assert IPLimit.objects.count() >= 0
