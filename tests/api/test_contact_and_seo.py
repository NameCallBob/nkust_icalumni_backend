"""公開的「聯絡我們」表單與 SEO 端點。

這兩組都是完全匿名可用的端點，也就是攻擊面的最前緣：
聯絡表單是寫入端點（垃圾訊息、注入），SEO 端點會把資料庫內容組成 XML 輸出
（很容易在不經意間把不該公開的資料寫進 sitemap）。
"""
import pytest

from apps.record.models import ContactMessage
from tests import factories

pytestmark = pytest.mark.django_db

CONTACT_URL = "/record/contact/"


# ══════════════════════════════════════════════════════════════════════
# 聯絡我們
# ══════════════════════════════════════════════════════════════════════
def test_anyone_can_submit_the_contact_form(anon_client, db):
    response = anon_client.post(
        CONTACT_URL,
        {"name": "訪客", "email": "visitor@example.invalid", "message": "請問入會方式？"},
        format="json",
    )
    assert response.status_code == 201
    assert ContactMessage.objects.count() == 1


def test_contact_form_validates_its_input(anon_client, db):
    """缺欄位／格式錯誤必須回 400，而且不得寫進資料庫。"""
    for payload in (
        {},
        {"name": "只有名字"},
        {"name": "格式錯誤", "email": "not-an-email", "message": "x"},
    ):
        response = anon_client.post(CONTACT_URL, payload, format="json")
        assert response.status_code == 400, f"{payload} 竟被接受"

    assert ContactMessage.objects.count() == 0


def test_contact_endpoint_never_returns_existing_messages(anon_client, db):
    """這支端點只寫不讀——回傳既有訊息等於把所有人的來信公開。"""
    ContactMessage.objects.create(
        name="先前的來信", email="earlier@example.invalid", message="機密內容"
    )

    response = anon_client.post(
        CONTACT_URL,
        {"name": "訪客", "email": "visitor@example.invalid", "message": "新訊息"},
        format="json",
    )
    body = response.content.decode()
    assert "機密內容" not in body
    assert "earlier@example.invalid" not in body


@pytest.mark.security
def test_contact_form_does_not_allow_get(anon_client, db):
    """只開放 POST。GET 若被實作成列表，等同公開所有來信。"""
    assert anon_client.get(CONTACT_URL).status_code == 405


# ══════════════════════════════════════════════════════════════════════
# SEO
# ══════════════════════════════════════════════════════════════════════
def test_sitemap_is_served_to_anonymous_visitors(anon_client, db):
    """sitemap 必須匿名可讀——搜尋引擎不會登入。"""
    response = anon_client.get("/api/seo/sitemap.xml")
    assert response.status_code == 200
    assert b"<urlset" in response.content or b"<url>" in response.content


def test_sitemap_lists_published_content_only(anon_client, db):
    """未發布的文章與已下架的職缺不得出現在 sitemap。

    sitemap 會被搜尋引擎主動抓取並索引——把草稿的網址寫進去，等於主動請
    Google 來收錄還沒公開的內容。
    """
    published_article = factories.ArticleFactory(title="published-article", active=True)
    draft_article = factories.ArticleFactory(title="draft-article", active=False)
    live_recruit = factories.RecruitFactory(title="live-position", active=True)
    closed_recruit = factories.RecruitFactory(title="closed-position", active=False)

    body = anon_client.get("/api/seo/sitemap.xml").content.decode()

    assert f"/article/{published_article.id}/" in body
    assert f"/article/{draft_article.id}/" not in body, "sitemap 收錄了未發布文章"
    assert f"/recruit/{live_recruit.id}/" in body
    assert f"/recruit/{closed_recruit.id}/" not in body, "sitemap 收錄了已下架職缺"


@pytest.mark.security
def test_sitemap_does_not_leak_member_personal_data(anon_client, db):
    """sitemap 不得含有任何會員個資。"""
    factories.MemberFactory(
        name="系友姓名",
        mobile_phone="0911222333",
        address="不該出現在 sitemap 的地址",
        is_show=True,
    )

    body = anon_client.get("/api/seo/sitemap.xml").content.decode()
    assert "0911222333" not in body
    assert "不該出現在 sitemap 的地址" not in body


def test_robots_txt_is_served(anon_client, db):
    response = anon_client.get("/api/seo/robots.txt")
    assert response.status_code == 200
    assert b"User-agent" in response.content


@pytest.mark.security
def test_robots_txt_disallows_the_admin_area(anon_client, db):
    """robots.txt 至少要把後台路徑排除在索引之外。

    這不是安全機制（robots.txt 擋不住任何攻擊者），但把 `/database/admin/`
    交給搜尋引擎索引會讓後台入口變得很容易被找到。
    """
    body = anon_client.get("/api/seo/robots.txt").content.decode()
    assert "Disallow" in body
