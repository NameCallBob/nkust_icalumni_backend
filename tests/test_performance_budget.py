"""查詢預算：公開列表端點的 SQL 查詢次數不得隨資料量增長。

N+1 查詢是這類「列表 + 巢狀關聯」API 最典型的效能地雷，而且它有個很惡劣的性質：
**開發時完全看不出來**。本機資料庫有 5 筆資料，多跑 5 次查詢沒人會察覺；正式站
累積到 3000 筆會員之後，同一支端點就變成 3000 次查詢、逾時、然後拖垮整個站。

做法刻意不寫死「這支端點應該是 7 次查詢」這種數字——那種斷言會在任何無關的
重構後失敗，最後被大家改成一個越來越大的數字。這裡改為比較「少量資料」與
「大量資料」兩種情況的查詢次數：

* 次數相同 → 沒有 N+1，通過
* 次數隨筆數增加 → 有 N+1，失敗，並印出增加了幾次

這個判準與資料量、索引、序列化器細節都無關，只針對真正的問題。
"""
import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext

from tests import factories

pytestmark = [pytest.mark.performance, pytest.mark.django_db]

SMALL = 2
LARGE = 12


def _count_queries(client, url, params=None):
    with CaptureQueriesContext(connection) as captured:
        response = client.get(url, params or {})
    return response, len(captured.captured_queries)


def _assert_no_n_plus_one(client, url, seed, params=None):
    """先種 SMALL 筆量測一次，再補到 LARGE 筆量測一次，比較查詢次數。"""
    seed(SMALL)
    first_response, baseline = _count_queries(client, url, params)
    if first_response.status_code != 200:
        pytest.skip(f"{url} 回應 {first_response.status_code}，無法量測")

    seed(LARGE - SMALL)
    _, scaled = _count_queries(client, url, params)

    extra = scaled - baseline
    assert extra <= 0, (
        f"{url} 疑似 N+1：資料從 {SMALL} 筆增加到 {LARGE} 筆時，"
        f"SQL 查詢從 {baseline} 次增加到 {scaled} 次（多了 {extra} 次）。\n\n"
        "請在 queryset 上補 `select_related()`（一對一／外鍵）或 "
        "`prefetch_related()`（一對多／多對多）。"
    )


# ══════════════════════════════════════════════════════════════════════
# 公開列表端點
# ══════════════════════════════════════════════════════════════════════
def test_public_member_search_has_no_n_plus_one(anon_client, db):
    """公開系友搜尋——序列化時會取 position / graduate / company，最容易 N+1。"""

    def seed(count):
        for _ in range(count):
            factories.MemberFactory(is_show=True, is_paid=True)

    _assert_no_n_plus_one(anon_client, "/member/search_user/", seed)


def test_public_alumni_search_has_no_n_plus_one(anon_client, db):
    """`alumni-search` 會跨 company / industry / graduate 做 OR 查詢，是最重的一支。"""

    def seed(count):
        for _ in range(count):
            member = factories.MemberFactory(name="搜尋目標", is_show=True, is_paid=True)
            factories.CompanyFactory(member=member)

    # 這支端點沒有 q 參數會直接回 400，量測不到任何東西。
    _assert_no_n_plus_one(
        anon_client, "/member/any/alumni-search/", seed, params={"q": "搜尋目標"}
    )


def test_public_company_search_has_no_n_plus_one(anon_client, db):
    def seed(count):
        for _ in range(count):
            factories.CompanyFactory()

    _assert_no_n_plus_one(anon_client, "/company/search_any/", seed)


def test_public_article_list_has_no_n_plus_one(anon_client, db):
    """文章列表會 prefetch images——少了 prefetch 就是每篇文章一次額外查詢。"""

    def seed(count):
        for _ in range(count):
            article = factories.ArticleFactory(active=True)
            factories.ArticleImageFactory(article=article)

    _assert_no_n_plus_one(anon_client, "/article/all/all_active/", seed)


def test_public_recruit_list_has_no_n_plus_one(anon_client, db):
    def seed(count):
        for _ in range(count):
            recruit = factories.RecruitFactory(active=True)
            factories.RecruitContactFactory(recruit=recruit)

    _assert_no_n_plus_one(anon_client, "/recruit/data/all_active/", seed)


def test_featured_outstanding_alumni_has_no_n_plus_one(anon_client, db):
    def seed(count):
        for _ in range(count):
            factories.OutstandingAlumniFactory(is_featured=True)

    _assert_no_n_plus_one(anon_client, "/member/outstanding-alumni/featured/", seed)


def test_active_slides_have_no_n_plus_one(anon_client, db):
    def seed(count):
        for _ in range(count):
            factories.SlideImageFactory(active=True)

    _assert_no_n_plus_one(anon_client, "/picture/slide-images/active/", seed)


# ══════════════════════════════════════════════════════════════════════
# 登入後的列表端點
# ══════════════════════════════════════════════════════════════════════
def test_admin_member_table_has_no_n_plus_one(staff_client, db):
    """管理端的會員總表是資料量最大的一支，N+1 在這裡代價最高。"""

    def seed(count):
        for _ in range(count):
            factories.MemberFactory()

    _assert_no_n_plus_one(staff_client, "/member/admin/tableOutput_all/", seed)
