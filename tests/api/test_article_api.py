"""文章（公告）API。

公開端點三支（`all_active` / `tableOutput` / `all`）+ staff 專用的增刪改。
重點在於「未發布的文章不該被看到」——文章常常是先寫好草稿、排定時間再公開的。
"""
import pytest

from apps.article.models import Article
from tests import factories

pytestmark = pytest.mark.django_db


# ══════════════════════════════════════════════════════════════════════
# 公開讀取
# ══════════════════════════════════════════════════════════════════════
def test_all_active_returns_only_published_articles(anon_client, db):
    factories.ArticleFactory(title="已發布文章", active=True)
    factories.ArticleFactory(title="未發布草稿", active=False)

    response = anon_client.get("/article/all/all_active/")

    assert response.status_code == 200
    titles = {item["title"] for item in response.data}
    assert "已發布文章" in titles
    assert "未發布草稿" not in titles


def test_all_active_is_ordered_newest_first(anon_client, db):
    older = factories.ArticleFactory(title="舊文章", active=True)
    newer = factories.ArticleFactory(title="新文章", active=True)

    response = anon_client.get("/article/all/all_active/")
    ids = [item["id"] for item in response.data]
    assert ids.index(newer.id) < ids.index(older.id)


def test_unpublished_articles_are_reachable_through_the_public_all_endpoint(anon_client, db):
    """記錄一項現況：`/article/all/all/` 對匿名開放，且回傳**未發布**的文章。

    `all_active` 有 `active=True` 過濾，`all` 沒有——但兩支的權限同樣是 AllowAny。
    也就是說任何人都能讀到尚未公開的草稿（例如還沒到公布時間的錄取名單、
    尚未定案的公告）。

    這條測試斷言的是**現況**，用意是把它變成明文記錄。修正方式是把 `all`
    改成需要 staff（`IsStaffPermission`），改完之後這條測試會失敗——屆時把它
    改寫成「匿名讀不到草稿」即可。
    """
    factories.ArticleFactory(title="尚未公開的草稿", active=False)

    response = anon_client.get("/article/all/all/")

    assert response.status_code == 200
    titles = {item["title"] for item in response.data}
    assert "尚未公開的草稿" in titles, (
        "`/article/all/all/` 已不再回傳未發布文章——這是好事，請更新這條測試。"
    )


def test_get_one_increments_view_count(anon_client, db):
    article = factories.ArticleFactory(active=True)
    assert article.view_count == 0

    anon_client.get("/article/all/get_one/", {"id": article.id})

    article.refresh_from_db()
    assert article.view_count == 1


def test_get_one_returns_404_for_unknown_id(anon_client, db):
    assert anon_client.get("/article/all/get_one/", {"id": 999999}).status_code == 404


def test_get_one_without_id_returns_400(anon_client, db):
    assert anon_client.get("/article/all/get_one/").status_code == 400


# ══════════════════════════════════════════════════════════════════════
# staff 寫入
# ══════════════════════════════════════════════════════════════════════
def test_staff_can_create_an_article(staff_client, db):
    response = staff_client.post(
        "/article/all/new/",
        {"title": "新公告", "content": "<p>內容</p>", "active": True},
        format="json",
    )
    assert response.status_code == 201
    assert Article.objects.filter(title="新公告").exists()


def test_staff_can_update_an_article(staff_client, db):
    article = factories.ArticleFactory(title="修改前")

    response = staff_client.patch(
        "/article/all/change/", {"id": article.id, "title": "修改後"}, format="json"
    )
    assert response.status_code == 200

    article.refresh_from_db()
    assert article.title == "修改後"


def test_staff_can_delete_an_article(staff_client, db):
    article = factories.ArticleFactory()

    staff_client.delete("/article/all/delete/", {"id": article.id}, format="json")
    assert not Article.objects.filter(pk=article.pk).exists()


def test_change_without_id_returns_400(staff_client, db):
    assert staff_client.patch("/article/all/change/", {}, format="json").status_code == 400


def test_delete_of_unknown_article_returns_404(staff_client, db):
    response = staff_client.delete("/article/all/delete/", {"id": 999999}, format="json")
    assert response.status_code == 404


@pytest.mark.security
@pytest.mark.parametrize("action,method", [("new", "post"), ("change", "patch"), ("delete", "delete")])
def test_regular_member_cannot_write_articles(member_client, action, method, db):
    """一般會員不得新增／修改／刪除站務公告（HIGH-3）。"""
    article = factories.ArticleFactory()
    response = getattr(member_client, method)(
        f"/article/all/{action}/",
        {"id": article.id, "title": "越權竄改", "content": "x", "active": True},
        format="json",
    )
    assert response.status_code in (401, 403)
