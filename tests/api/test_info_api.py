"""系友會簡介（Info）API：簡介、章程、組織架構、入會條件。

這四組的結構完全一樣（`latest` 公開 / `all` 限管理員 / `new`、`change`、`remove`
限管理員），因此用參數化一次涵蓋，避免四份幾乎相同的複製貼上程式碼——
日後新增第五組時只要在表格裡多一列。
"""
import pytest

pytestmark = pytest.mark.django_db

# (資源名稱, 對外的 latest 端點, 管理端前綴, 建立用的 factory)
RESOURCES = [
    ("系友會簡介", "/info/associations/latest/", "/info/associations", "AlumniAssociationFactory"),
    ("章程", "/info/constitutions/latest/", "/info/constitutions", "ConstitutionFactory"),
    ("組織架構", "/info/structures/latest/", "/info/structures", "OrganizationalStructureFactory"),
    ("入會條件", "/info/requirement/latest/", "/info/requirement", "MembershipRequirementFactory"),
    ("入會條件 v2", "/info/requirement-v2/latest/", "/info/requirement-v2", "MembershipRequirementV2Factory"),
]

IDS = [r[0] for r in RESOURCES]


@pytest.mark.parametrize("name,latest_url,admin_prefix,factory_name", RESOURCES, ids=IDS)
def test_latest_is_public(anon_client, db, name, latest_url, admin_prefix, factory_name):
    """前台頁面要能在未登入的情況下顯示這些內容。"""
    from tests import factories

    getattr(factories, factory_name)()

    response = anon_client.get(latest_url)
    assert response.status_code == 200, f"{name} 的 latest 端點回應 {response.status_code}"


@pytest.mark.parametrize("name,latest_url,admin_prefix,factory_name", RESOURCES, ids=IDS)
def test_latest_returns_the_most_recent_entry(anon_client, db, name, latest_url, admin_prefix, factory_name):
    """`latest` 必須回傳最新的一筆，否則改了內容前台也不會更新。"""
    from tests import factories

    factory = getattr(factories, factory_name)
    factory(description="<p>舊版內容</p>")
    factory(description="<p>最新版內容</p>")

    body = anon_client.get(latest_url).content.decode()
    assert "最新版內容" in body, f"{name} 的 latest 沒有回傳最新的一筆"


@pytest.mark.security
@pytest.mark.parametrize("name,latest_url,admin_prefix,factory_name", RESOURCES, ids=IDS)
def test_management_endpoints_require_staff(member_client, db, name, latest_url, admin_prefix, factory_name):
    """一般會員不得新增／修改／刪除系友會的官方內容。"""
    checks = [
        ("get", f"{admin_prefix}/all/"),
        ("post", f"{admin_prefix}/new/"),
        ("put", f"{admin_prefix}/change/"),
        ("delete", f"{admin_prefix}/remove/"),
    ]
    for method, url in checks:
        response = getattr(member_client, method)(url, {}, format="json")
        assert response.status_code in (401, 403), f"{name} 的 {method.upper()} {url} 未擋下一般會員"


@pytest.mark.parametrize("name,latest_url,admin_prefix,factory_name", RESOURCES, ids=IDS)
def test_staff_can_list_all_entries(staff_client, db, name, latest_url, admin_prefix, factory_name):
    from tests import factories

    getattr(factories, factory_name)()

    response = staff_client.get(f"{admin_prefix}/all/")
    assert response.status_code == 200


def test_latest_returns_a_clean_response_when_there_is_no_content(anon_client, db):
    """尚未建立任何內容時不得 5xx——新站台剛上線時就是這個狀態。"""
    for _, latest_url, _, _ in RESOURCES:
        response = anon_client.get(latest_url)
        assert response.status_code < 500, f"{latest_url} 在無資料時回應 {response.status_code}"


def test_membership_requirement_v2_pdf_download_is_public(anon_client, db):
    """入會申請書 PDF 必須讓未登入者也能下載。"""
    from tests import factories

    factories.MembershipRequirementV2Factory()

    response = anon_client.get("/info/requirement-v2/download_pdf/")
    assert response.status_code < 500
