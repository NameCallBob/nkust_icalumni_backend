"""公司與產品 API。

這一組的核心規則是「每個會員只能碰自己的公司與商品」。跨會員的越權測試在
`tests/security/test_authorization.py`；這裡驗證正常路徑與查詢／篩選行為。
"""
import pytest

from apps.company.models import Company
from apps.product.models import Product, ProductCate
from tests import factories

pytestmark = pytest.mark.django_db


# ══════════════════════════════════════════════════════════════════════
# 公司：公開查詢
# ══════════════════════════════════════════════════════════════════════
def test_public_company_search_is_open(anon_client, db):
    # 公開的公司查詢會過濾 member__is_show=True 且 member__private__is_active=True，
    # 少了任一個條件這家公司就不會出現在結果裡。
    factories.CompanyFactory(
        name="公開查得到的公司", member=factories.MemberFactory(is_show=True)
    )

    response = anon_client.get("/company/search_any/")

    assert response.status_code == 200
    assert "公開查得到的公司" in response.content.decode()


def test_most_viewed_companies_are_ordered_by_clicks(anon_client, db):
    factories.CompanyFactory(
        name="冷門公司", clicks=1, member=factories.MemberFactory(is_show=True)
    )
    factories.CompanyFactory(
        name="熱門公司", clicks=999, member=factories.MemberFactory(is_show=True)
    )

    body = anon_client.get("/company/data/mostView/").content.decode()
    assert "熱門公司" in body
    if "冷門公司" in body:
        assert body.index("熱門公司") < body.index("冷門公司")


def test_random_companies_endpoint_responds(anon_client, db):
    for _ in range(3):
        factories.CompanyFactory()
    assert anon_client.get("/company/data/randomCompanies/").status_code == 200


def test_industry_list_is_public(anon_client, db):
    factories.IndustryFactory(title="資訊服務業")

    response = anon_client.get("/company/industry/all/")

    assert response.status_code == 200
    assert "資訊服務業" in response.content.decode()


# ══════════════════════════════════════════════════════════════════════
# 公司：會員自助維護
# ══════════════════════════════════════════════════════════════════════
def test_member_reads_their_own_company(member_client, company):
    response = member_client.get("/company/data/selfInfo/")

    assert response.status_code == 200
    assert company.name in response.content.decode()


def test_member_updates_their_own_company(member_client, company):
    response = member_client.post(
        "/company/data/selfChange/", {"name": "更名後的公司"}, format="json"
    )
    assert response.status_code == 200

    company.refresh_from_db()
    assert company.name == "更名後的公司"


def test_member_without_a_company_gets_404(member_client, member):
    assert member_client.get("/company/data/selfInfo/").status_code == 404


@pytest.mark.security
def test_only_staff_can_manage_industries(member_client, db):
    industry = factories.IndustryFactory()

    assert member_client.post(
        "/company/industry/new/", {"title": "自建產業"}, format="json"
    ).status_code in (401, 403)
    assert member_client.put(
        "/company/industry/change/", {"id": industry.id, "title": "竄改"}, format="json"
    ).status_code in (401, 403)


@pytest.mark.security
def test_only_staff_can_delete_companies(member_client, company):
    member_client.delete("/company/data/delete/", {"id": company.id}, format="json")
    assert Company.objects.filter(pk=company.pk).exists()


# ══════════════════════════════════════════════════════════════════════
# 產品
# ══════════════════════════════════════════════════════════════════════
def test_member_creates_a_product_for_their_own_company(member_client, company):
    response = member_client.post(
        "/product/data/new/",
        {"name": "新商品", "description": "商品說明"},
        format="json",
    )
    assert response.status_code in (200, 201), response.content[:300]

    created = Product.objects.get(name="新商品")
    assert created.company_id == company.id, "商品竟被掛到別的公司底下"


def test_member_lists_only_their_own_products(member_client, company, db):
    factories.ProductFactory(company=company, name="我的商品")
    factories.ProductFactory(name="別人的商品")

    body = member_client.get("/product/data/selfCompany/").content.decode()
    assert "我的商品" in body
    assert "別人的商品" not in body


def test_member_updates_their_own_product(member_client, company, db):
    product = factories.ProductFactory(company=company, name="修改前")

    response = member_client.put(
        "/product/data/change/",
        {"id": product.id, "name": "修改後", "description": "說明"},
        format="json",
    )
    assert response.status_code == 200

    product.refresh_from_db()
    assert product.name == "修改後"


def test_member_deletes_their_own_product(member_client, company, db):
    product = factories.ProductFactory(company=company)

    member_client.delete("/product/data/remove/", {"id": product.id}, format="json")
    assert not Product.objects.filter(pk=product.pk).exists()


def test_public_product_listing_by_member_id(anon_client, db):
    member = factories.MemberFactory(is_show=True)
    company = factories.CompanyFactory(member=member)
    factories.ProductFactory(company=company, name="公開商品", is_active=True)

    response = anon_client.get("/product/data/member/", {"member_id": member.id})

    assert response.status_code == 200
    assert "公開商品" in response.content.decode()


def test_public_product_listing_hides_inactive_products(anon_client, db):
    member = factories.MemberFactory(is_show=True)
    company = factories.CompanyFactory(member=member)
    factories.ProductFactory(company=company, name="已下架商品", is_active=False)

    body = anon_client.get(
        "/product/data/member/", {"member_id": member.id}
    ).content.decode()
    assert "已下架商品" not in body


# ══════════════════════════════════════════════════════════════════════
# 產品類別
# ══════════════════════════════════════════════════════════════════════
def test_member_creates_a_category_under_their_own_company(member_client, company):
    response = member_client.post(
        "/product/categories/", {"name": "新類別"}, format="json"
    )
    assert response.status_code in (200, 201), response.content[:300]

    created = ProductCate.objects.get(name="新類別")
    assert created.company_id == company.id


@pytest.mark.xfail(
    strict=True,
    reason=(
        "已知缺陷：ProductCate 的 unique_together=('company','name') 只存在於資料庫層。"
        "`ProductCateViewSet.perform_create` 是在 serializer 驗證**之後**才用 "
        "`serializer.save(company=...)` 補上 company，所以 DRF 的 UniqueTogetherValidator "
        "在驗證階段看不到 company 欄位，無法檢查這個組合是否重複。"
        "結果是重複名稱不會得到 400，而是一路撞到資料庫的 UNIQUE 約束，"
        "拋出未被攔截的 IntegrityError → 500。"
        "修法：在 serializer 的 validate() 內用 request.user 推出 company 後自行檢查，"
        "或把 company 設為 HiddenField(default=...) 讓 UniqueTogetherValidator 能取到值。"
    ),
)
def test_category_names_are_unique_per_company(member_client, company, db):
    """同一家公司底下不得有同名的產品類別，且必須回 400 而非 500。"""
    factories.ProductCateFactory(company=company, name="重複類別")

    response = member_client.post(
        "/product/categories/", {"name": "重複類別"}, format="json"
    )
    assert response.status_code == 400, "同一公司內的重複類別名稱應回 400"


@pytest.mark.security
def test_category_list_is_read_only_for_anonymous(anon_client, db):
    """`IsAuthenticatedOrReadOnly`：匿名可讀，但不得寫入。"""
    assert anon_client.get("/product/categories/").status_code == 200
    assert anon_client.post(
        "/product/categories/", {"name": "匿名新增"}, format="json"
    ).status_code in (401, 403)
