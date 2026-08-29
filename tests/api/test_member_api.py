"""會員 API：自助維護、公開查詢、管理端。

會員資料是本站的核心資產，同一份資料有三種存取路徑，每一種能看到的欄位都不同：

===================  ============  ==========================================
路徑                 身分          可見範圍
===================  ============  ==========================================
`/member/any/*`      匿名          僅 `is_show=True` 的會員，且僅公開欄位
`/member/logined/*`  會員本人      自己的完整資料（含個資）
`/member/admin/*`    staff         所有人的完整資料
===================  ============  ==========================================

這三條界線一旦模糊，就是個資外洩。跨界線的測試放在
`tests/security/test_pii_leakage.py` 與 `tests/security/test_authorization.py`；
本檔案專注在每條路徑「自己該做對的事」。
"""
import pytest

from apps.member.models import Member
from tests import factories

pytestmark = pytest.mark.django_db


# ══════════════════════════════════════════════════════════════════════
# 公開查詢
# ══════════════════════════════════════════════════════════════════════
def test_public_detail_returns_a_visible_member(anon_client, db):
    member = factories.MemberFactory(name="公開系友", is_show=True)

    response = anon_client.get("/member/any/getOne/", {"id": member.id})

    assert response.status_code == 200
    assert response.data["name"] == "公開系友"


def test_public_detail_without_id_returns_404(anon_client, db):
    assert anon_client.get("/member/any/getOne/").status_code == 404


def test_get_by_grade_filters_by_graduation_year(anon_client, db):
    factories.MemberFactory(
        name="110級系友", graduate=factories.GraduateFactory(grade="110"), is_show=True
    )
    factories.MemberFactory(
        name="112級系友", graduate=factories.GraduateFactory(grade="112"), is_show=True
    )

    body = anon_client.get("/member/any/get-by-grade/", {"grade": "110"}).content.decode()
    assert "110級系友" in body
    assert "112級系友" not in body


def test_get_by_grade_all_returns_every_visible_member(anon_client, db):
    factories.MemberFactory(name="甲系友", is_show=True)
    factories.MemberFactory(name="乙系友", is_show=True)
    factories.MemberFactory(name="隱藏系友", is_show=False)

    body = anon_client.get("/member/any/get-by-grade/", {"grade": "全部"}).content.decode()
    assert "甲系友" in body and "乙系友" in body
    assert "隱藏系友" not in body


def test_get_by_position_filters_by_position_id(anon_client, db):
    chairman = factories.PositionFactory(title="會長")
    factories.MemberFactory(name="會長本人", position=chairman, is_show=True)
    factories.MemberFactory(name="一般會員", is_show=True)

    body = anon_client.get(
        "/member/any/get-by-position/", {"position": chairman.id}
    ).content.decode()
    assert "會長本人" in body
    assert "一般會員" not in body


def test_alumni_search_requires_a_keyword(anon_client, db):
    assert anon_client.get("/member/any/alumni-search/").status_code == 400


def test_alumni_search_finds_members_by_name(anon_client, db):
    factories.MemberFactory(name="陳大文", is_show=True)
    factories.MemberFactory(name="林小美", is_show=True)

    body = anon_client.get("/member/any/alumni-search/", {"q": "陳大文"}).content.decode()
    assert "陳大文" in body
    assert "林小美" not in body


def test_public_position_and_graduate_lists_are_readable(anon_client, db):
    factories.PositionFactory(title="理事長")
    factories.GraduateFactory(grade="108")

    assert anon_client.get("/member/position/get-all/").status_code == 200
    assert anon_client.get("/member/graduate/get-all/").status_code == 200
    assert anon_client.get("/member/graduate/unique-grades/").status_code == 200


# ══════════════════════════════════════════════════════════════════════
# 會員自助維護
# ══════════════════════════════════════════════════════════════════════
def test_member_can_read_their_own_profile(member_client, member):
    response = member_client.get("/member/logined/selfInfo/")

    assert response.status_code == 200
    assert response.data["name"] == member.name


def test_member_can_update_their_own_profile(member_client, member):
    response = member_client.patch(
        "/member/logined/partial_change/",
        {"name": "更新後的名字", "intro": "更新後的自介"},
        format="json",
    )
    assert response.status_code == 200

    member.refresh_from_db()
    assert member.name == "更新後的名字"
    assert member.intro == "更新後的自介"


def test_member_without_a_profile_gets_404(member_client, member_user):
    """帳號存在但還沒建立會員資料時，selfInfo 應回 404 而不是崩潰。"""
    assert member_client.get("/member/logined/selfInfo/").status_code == 404


# ══════════════════════════════════════════════════════════════════════
# 修改密碼
# ══════════════════════════════════════════════════════════════════════
def test_member_can_change_their_password(member_client, member_user):
    response = member_client.post(
        "/member/logined/update_password/",
        {"old_password": member_user.raw_password, "new_password": "N3wPassw0rd!ok"},
        format="json",
    )
    assert response.status_code == 200

    member_user.refresh_from_db()
    assert member_user.check_password("N3wPassw0rd!ok")


@pytest.mark.security
def test_changing_password_requires_the_current_one(member_client, member_user):
    """不驗舊密碼的話，只要偷到一次 token 就能永久接管帳號。"""
    original = member_user.password

    response = member_client.post(
        "/member/logined/update_password/",
        {"old_password": "wrong-old-password", "new_password": "N3wPassw0rd!ok"},
        format="json",
    )
    assert response.status_code == 403

    member_user.refresh_from_db()
    assert member_user.password == original


def test_new_password_must_differ_from_the_old_one(member_client, member_user):
    response = member_client.post(
        "/member/logined/update_password/",
        {"old_password": member_user.raw_password, "new_password": member_user.raw_password},
        format="json",
    )
    assert response.status_code == 400


@pytest.mark.security
@pytest.mark.xfail(
    strict=True,
    reason=(
        "已知缺陷：`MemberViewSet.update_password` 直接 `user.set_password(new_password)`，"
        "沒有呼叫 `django.contrib.auth.password_validation.validate_password`。"
        "同一個專案裡的忘記密碼流程（PasswordResetConfirmView）有驗，登入後自行修改卻沒驗，"
        "等於留了一條把帳號降級成弱密碼的路徑，`AUTH_PASSWORD_VALIDATORS` 形同虛設。"
        "`MemberAdminViewSet.update_password` 與 `PrivateViewSet.update_password` 也有同樣問題。"
        "修法：在 set_password 之前補上 validate_password(new_password, user=user)，"
        "並把 ValidationError 轉成 400。"
    ),
)
@pytest.mark.parametrize("weak_password", ["123456", "12345678", "abc"])
def test_password_change_rejects_weak_passwords(member_client, member_user, weak_password):
    """登入後自行修改密碼，也必須套用密碼強度規則。"""
    response = member_client.post(
        "/member/logined/update_password/",
        {"old_password": member_user.raw_password, "new_password": weak_password},
        format="json",
    )
    assert response.status_code == 400, f"弱密碼 {weak_password!r} 竟被接受"


# ══════════════════════════════════════════════════════════════════════
# 管理端
# ══════════════════════════════════════════════════════════════════════
def test_staff_can_list_every_member(staff_client, db):
    factories.MemberFactory(name="會員甲")
    factories.MemberFactory(name="會員乙", is_show=False)

    response = staff_client.get("/member/admin/tableOutput_all/")

    assert response.status_code == 200
    names = {row["name"] for row in response.data}
    assert {"會員甲", "會員乙"} <= names


def test_staff_can_read_any_member_detail(staff_client, other_member):
    """注意參數名不一致：管理端用 `member_id`，會員端 `/member/logined/getOne/` 用 `id`。

    這是既有的介面不一致，前端兩邊都要記得用對；此處把它釘死，
    哪天有人統一了參數名，這條測試會失敗並提醒同步更新前端。
    """
    response = staff_client.get("/member/admin/getOne/", {"member_id": other_member.id})
    assert response.status_code == 200
    assert response.data["name"] == other_member.name


def test_staff_can_toggle_paid_status(staff_client, other_member):
    other_member.is_paid = False
    other_member.save()

    response = staff_client.patch(
        "/member/admin/switch_paid/", {"member_id": other_member.id}, format="json"
    )
    assert response.status_code == 200

    other_member.refresh_from_db()
    assert other_member.is_paid is True


def test_staff_can_deactivate_an_account(staff_client, other_member):
    response = staff_client.patch(
        "/member/admin/switch_active/", {"member_id": other_member.id}, format="json"
    )
    assert response.status_code == 200

    other_member.private.refresh_from_db()
    assert other_member.private.is_active is False


def test_staff_can_delete_a_member(staff_client, other_member):
    member_id = other_member.id
    response = staff_client.delete(
        "/member/admin/delete/", {"member_id": member_id}, format="json"
    )
    assert response.status_code in (200, 204)
    assert not Member.objects.filter(pk=member_id).exists()


# ══════════════════════════════════════════════════════════════════════
# 傑出系友／校友
# ══════════════════════════════════════════════════════════════════════
@pytest.mark.parametrize(
    "url,factory_name",
    [
        ("/member/outstanding-alumni/featured/", "OutstandingAlumniFactory"),
        ("/member/school-outstanding-alumni/featured/", "SchoolOutstandingAlumniFactory"),
    ],
)
def test_featured_endpoints_return_only_featured_entries(anon_client, db, url, factory_name):
    factory = getattr(factories, factory_name)
    featured_member = factories.MemberFactory(name="被選上的系友", is_show=True)
    hidden_member = factories.MemberFactory(name="未被選上的系友", is_show=True)
    factory(member=featured_member, is_featured=True)
    factory(member=hidden_member, is_featured=False)

    body = anon_client.get(url).content.decode()
    assert "被選上的系友" in body
    assert "未被選上的系友" not in body


def test_featured_entries_respect_sort_order(anon_client, db):
    first = factories.MemberFactory(name="排第一", is_show=True)
    second = factories.MemberFactory(name="排第二", is_show=True)
    factories.OutstandingAlumniFactory(member=second, is_featured=True, sort_order=2)
    factories.OutstandingAlumniFactory(member=first, is_featured=True, sort_order=1)

    body = anon_client.get("/member/outstanding-alumni/featured/").content.decode()
    assert body.index("排第一") < body.index("排第二")


@pytest.mark.security
def test_only_staff_can_manage_outstanding_alumni(member_client, db):
    member = factories.MemberFactory()
    response = member_client.post(
        "/member/outstanding-alumni/",
        {"member": member.id, "highlight": "自封傑出系友"},
        format="json",
    )
    assert response.status_code in (401, 403)
