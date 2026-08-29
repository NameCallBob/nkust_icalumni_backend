"""徵才（職缺）API。

這一支的公開端點是全站流量最高的地方之一（求職者不會登入就想看職缺），
所以它同時是「最需要穩」和「最容易被掃描」的端點。
"""
import pytest

from tests import factories

pytestmark = pytest.mark.django_db


# ══════════════════════════════════════════════════════════════════════
# 公開讀取
# ══════════════════════════════════════════════════════════════════════
def test_all_active_returns_only_published_positions(anon_client, db):
    published = factories.RecruitFactory(title="刊登中的職缺", active=True)
    factories.RecruitContactFactory(recruit=published)
    hidden = factories.RecruitFactory(title="已下架的職缺", active=False)
    factories.RecruitContactFactory(recruit=hidden)

    response = anon_client.get("/recruit/data/all_active/")

    assert response.status_code == 200
    body = response.content.decode()
    assert "刊登中的職缺" in body
    assert "已下架的職缺" not in body


def test_get_one_returns_the_requested_position(anon_client, db):
    recruit = factories.RecruitFactory(title="資料工程師")
    factories.RecruitContactFactory(recruit=recruit)

    response = anon_client.get("/recruit/data/getOne/", {"id": recruit.id})

    assert response.status_code == 200
    assert response.data["title"] == "資料工程師"


def test_get_one_without_id_returns_400(anon_client, db):
    assert anon_client.get("/recruit/data/getOne/").status_code == 400


# ══════════════════════════════════════════════════════════════════════
# 已知缺陷：沒有聯絡人的職缺會讓公開端點 500
# ══════════════════════════════════════════════════════════════════════
@pytest.mark.xfail(
    strict=True,
    reason=(
        "已知缺陷：RecruitSerializer.get__company_name 與 "
        "RecruitSerializer_forTable.get_company_name 寫成 "
        "`obj.contact.company_name if obj.contact else None`。"
        "Recruit.contact 是反向 OneToOne，沒有對應資料時存取它會丟出 "
        "RelatedObjectDoesNotExist（同時繼承 AttributeError），"
        "而不是回傳 None，所以 `if obj.contact` 這個寫法擋不住。"
        "由於 ContactSerializer 是 required=False，沒有聯絡人的職缺是可以被建立的，"
        "一旦存在就會讓 /recruit/data/all_active/、getOne/、tableOutput/ 這三支"
        "「匿名可存取」的端點全部 500——連 staff 的職缺管理列表也一起壞掉，"
        "也就是說一筆沒有聯絡人的資料就能讓整個徵才模組（前台與後台）無法使用。"
        "修法：改用 `getattr(obj, 'contact', None)` 或 "
        "`obj.contact.company_name if hasattr(obj, 'contact') else None`。"
    ),
)
@pytest.mark.parametrize(
    "url,client_fixture",
    [
        ("/recruit/data/all_active/", "anon_client"),
        ("/recruit/data/tableOutput/", "anon_client"),
        ("/recruit/data/all/", "staff_client"),
        ("/recruit/admin/admin/all_recruits/", "staff_client"),
    ],
)
def test_listings_survive_recruit_without_contact(request, db, url, client_fixture):
    """沒有聯絡人的職缺不得讓任何一支列表端點崩潰。

    這條測試標記為 `xfail(strict=True)`：目前**預期會失敗**（因為 bug 還在）。
    修好之後它會變成 XPASS，而 strict 模式下 XPASS 會讓 CI 失敗——那正是提醒
    「bug 修好了，把這個 xfail 標記拿掉」的機制，避免修好的問題被無聲遺忘。
    """
    factories.RecruitFactory(title="沒有聯絡人的職缺", active=True)

    client = request.getfixturevalue(client_fixture)
    response = client.get(url)
    assert response.status_code == 200, (
        f"{url} 因為職缺缺少 Contact 而回應 {response.status_code}"
    )


# ══════════════════════════════════════════════════════════════════════
# 公開端點會揭露聯絡人資訊
# ══════════════════════════════════════════════════════════════════════
def test_public_listing_exposes_contact_person_details(anon_client, db):
    """記錄一項現況：公開職缺列表包含聯絡人的姓名、電話與 email。

    這對徵才而言是合理的（求職者需要知道找誰），但要意識到兩件事：

    1. 這些欄位對**全世界匿名可讀**，會被爬蟲收走，是垃圾郵件與詐騙電話的來源。
    2. `RecruitSerializer.handle_contact_data` 在 `isPersonalContact=True` 時，
       會把刊登者本人的手機與帳號 email 複製進 Contact——也就是說會員的個人
       手機可能因為勾了一個選項而變成公開資料。

    這條測試斷言現況，讓「公開」這件事是明文寫下來、review 得到的決定。
    """
    recruit = factories.RecruitFactory(active=True)
    factories.RecruitContactFactory(
        recruit=recruit, name="人資小姐", phone="0912000111", email="hr@example.invalid"
    )

    body = anon_client.get("/recruit/data/all_active/").content.decode()

    assert "人資小姐" in body
    assert "0912000111" in body
    assert "hr@example.invalid" in body


# ══════════════════════════════════════════════════════════════════════
# 權限
# ══════════════════════════════════════════════════════════════════════
@pytest.mark.security
def test_anonymous_cannot_list_all_positions_including_unpublished(anon_client, db):
    """`/recruit/data/all/`（含未發布）必須要登入。"""
    assert anon_client.get("/recruit/data/all/").status_code in (401, 403)


@pytest.mark.security
def test_regular_member_cannot_use_admin_recruit_endpoints(member_client, db):
    for url in (
        "/recruit/admin/admin/all_recruits/",
        "/recruit/admin/admin/companies/",
        "/recruit/admin/admin/users/",
        "/recruit/admin/admin/export/",
    ):
        assert member_client.get(url).status_code in (401, 403), f"{url} 未擋下一般會員"


def test_staff_can_list_all_recruits(staff_client, db):
    recruit = factories.RecruitFactory(active=False)
    # 必須配 Contact，否則會踩到上面那個 xfail 記錄的缺陷。
    factories.RecruitContactFactory(recruit=recruit)

    response = staff_client.get("/recruit/admin/admin/all_recruits/")
    assert response.status_code == 200
