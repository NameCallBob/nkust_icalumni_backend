"""授權：提權與越權存取（IDOR）。

這裡涵蓋兩類問題，都屬於「已經是合法登入者」之後才發生的攻擊，因此不會被
權限矩陣（tests/contracts/test_permission_matrix.py，只測匿名）抓到：

**提權（privilege escalation）**
  一般會員把自己變成 staff / superuser，或自行設定只有管理員能改的欄位
  （`is_paid`、`is_show`）。典型成因是序列化器用了 `fields = '__all__'`
  或直接把使用者傳來的巢狀 dict 灌進 `Private` 模型。

**越權存取（IDOR）**
  會員 A 帶著自己的憑證，把請求裡的 id 換成 B 的，就讀到／改到 B 的資料。
  這是本專案這種「每個會員都能編輯自己的公司與產品」的系統最容易出的漏洞——
  只要有一支查詢忘了加 `company__member=request.user.member` 就成立。

本檔案原始版本為 `apps/member/test_security_fixes.py`（2026-06-28 資安修補回歸測試），
遷移至此並擴充涵蓋範圍。
"""
import pytest

from tests import factories

pytestmark = [pytest.mark.security, pytest.mark.django_db]


# ══════════════════════════════════════════════════════════════════════
# 提權
# ══════════════════════════════════════════════════════════════════════
def test_member_cannot_escalate_to_staff_via_nested_private_input(member_client, member_user, member):
    """SEC-001：以 `private_input` 夾帶 is_staff / is_superuser 不得生效。

    `private_input` 是巢狀更新自己帳號資料的欄位。若序列化器原封不動把它交給
    `Private` 模型，使用者只要多送兩個布林值就能把自己升級成管理員。
    """
    member_client.patch(
        "/member/logined/partial_change/",
        {"private_input": {"email": member_user.email, "is_superuser": True, "is_staff": True}},
        format="json",
    )

    member_user.refresh_from_db()
    assert not member_user.is_superuser, "private_input 竟能提權為 superuser"
    assert not member_user.is_staff, "private_input 竟能提權為 staff"


def test_member_cannot_overwrite_password_hash_directly(member_client, member_user, member):
    """SEC-001：`private_input` 不得直接寫入 password 欄位。

    直接寫入會把明文存進 password 欄位（繞過雜湊），使用者從此可用該明文登入，
    而資料庫裡存的是可直接使用的明文憑證。
    """
    original = member_user.raw_password
    member_client.patch(
        "/member/logined/partial_change/",
        {"private_input": {"email": member_user.email, "password": "plaintextpwd"}},
        format="json",
    )

    member_user.refresh_from_db()
    assert member_user.password != "plaintextpwd"
    assert not member_user.check_password("plaintextpwd")
    assert member_user.check_password(original), "原密碼不應被破壞"


def test_member_cannot_set_administrative_flags_on_themselves(member_client, member):
    """SEC-003：`is_paid`（繳費狀態）與 `is_show`（是否公開）只有 staff 能設定。

    `is_paid` 是會費繳納紀錄——會員自設等於免繳；`is_show` 決定是否出現在公開
    名錄——自設等於繞過審核直接上架。
    """
    member.is_paid = False
    member.is_show = False
    member.save()

    member_client.patch(
        "/member/logined/partial_change/",
        {"is_paid": True, "is_show": True},
        format="json",
    )

    member.refresh_from_db()
    assert member.is_paid is False, "非 staff 竟能自設 is_paid"
    assert member.is_show is False, "非 staff 竟能自設 is_show"


def test_staff_can_set_administrative_flags(staff_client, other_member):
    """與上一條成對：staff 必須改得動，否則管理後台就壞了。"""
    other_member.is_paid = False
    other_member.is_show = False
    other_member.save()

    response = staff_client.patch(
        "/member/admin/partial_change/",
        {"member_id": other_member.id, "is_paid": True, "is_show": True},
        format="json",
    )
    assert response.status_code == 200

    other_member.refresh_from_db()
    assert other_member.is_paid is True
    assert other_member.is_show is True


def test_self_registration_cannot_grant_administrative_flags(anon_client, db):
    """匿名註冊時夾帶管理欄位不得生效。

    註冊是完全公開的端點，是提權嘗試最便宜的入口——不需要先有帳號。
    """
    from apps.member.models import Member

    response = anon_client.post(
        "/basic/register",
        {
            "name": "自助註冊",
            # position 是 MemberSerializer 的必填巢狀欄位，缺了會在還沒碰到
            # 權限邏輯前就被 400 擋掉，測不到本案例真正要驗的東西。
            "position": {"title": "會員", "priority": 999},
            "is_paid": True,
            "is_show": True,
            "private_input": {
                "email": "self-register@example.invalid",
                "password": "Passw0rd!Reg123",
                "is_staff": True,
                "is_superuser": True,
            },
        },
        format="json",
    )
    assert response.status_code == 201, (
        f"註冊失敗（{response.status_code}）：{response.content[:300]!r}"
    )

    created = Member.objects.get(name="自助註冊")
    assert created.is_show is False, "自助註冊竟能直接上架到公開名錄"
    assert created.private is not None
    assert not created.private.is_staff, "自助註冊竟能取得 staff"
    assert not created.private.is_superuser, "自助註冊竟能取得 superuser"


def test_member_is_paid_defaults_to_true():
    """釘住 `Member.is_paid` 的預設值，因為它目前是 **True**。

    這不是安全漏洞（`is_paid` 已被 `_strip_privileged_fields` 擋下，使用者無法
    自行設定），但它意味著**每一個自助註冊的會員一建立就被標記為已繳費**，
    管理端要靠人工改回來。這裡不主張對錯，只把現況釘死：哪天有人把預設改成
    False（很可能是對的），這條測試會失敗，提醒去確認既有資料與後台流程。
    """
    from apps.member.models import Member

    assert Member._meta.get_field("is_paid").default is True
    assert Member._meta.get_field("is_show").default is False


def test_member_cannot_reach_admin_endpoints(member_client, other_member):
    """一般會員打管理端點必須被擋（403），而不是只靠前端隱藏按鈕。"""
    admin_endpoints = [
        ("get", "/member/admin/tableOutput_all/", None),
        ("get", "/member/admin/getOne/", {"id": other_member.id}),
        ("patch", "/member/admin/partial_change/", {"member_id": other_member.id}),
        ("delete", "/member/admin/delete/", {"member_id": other_member.id}),
        ("get", "/basic/private/", None),
        ("get", "/api/monitoring/requests/", None),
    ]
    for method, url, payload in admin_endpoints:
        response = (
            getattr(member_client, method)(url, payload, format="json")
            if payload
            else getattr(member_client, method)(url)
        )
        assert response.status_code in (401, 403), (
            f"一般會員竟能存取管理端點 {method.upper()} {url}（{response.status_code}）"
        )


# ══════════════════════════════════════════════════════════════════════
# 越權存取（IDOR）
# ══════════════════════════════════════════════════════════════════════
def test_member_cannot_read_another_members_full_profile(member_client, other_member):
    """SEC-002：登入後仍不得以 id 列舉他人完整個資。"""
    response = member_client.get("/member/logined/getOne/", {"id": other_member.id})
    assert response.status_code == 403


def test_member_cannot_edit_another_members_product(member_client, db, member):
    """會員 A 不得修改會員 B 的產品。

    產品查詢必須帶 `company__member=request.user.member`；少了那個條件，
    任何登入者都能靠遞增 product_id 改掉全站商品資料。
    """
    victim_company = factories.CompanyFactory()
    victim_product = factories.ProductFactory(company=victim_company, name="受害者商品")

    response = member_client.put(
        "/product/data/change/",
        {"id": victim_product.id, "name": "已被竄改", "description": "x"},
        format="json",
    )
    assert response.status_code in (400, 403, 404), (
        f"竟能修改他人產品（{response.status_code}）"
    )

    victim_product.refresh_from_db()
    assert victim_product.name == "受害者商品"


def test_member_cannot_delete_another_members_product(member_client, db, member):
    from apps.product.models import Product

    victim_product = factories.ProductFactory(name="不該被刪的商品")

    member_client.delete(
        "/product/data/remove/", {"id": victim_product.id}, format="json"
    )
    assert Product.objects.filter(pk=victim_product.pk).exists(), "竟能刪除他人產品"


def test_member_only_sees_their_own_company(member_client, company, db):
    """`selfInfo` 只能回傳自己的公司。"""
    factories.CompanyFactory(name="別人的公司")

    response = member_client.get("/company/data/selfInfo/")
    if response.status_code == 200:
        assert "別人的公司" not in response.content.decode()


def test_member_cannot_modify_another_members_company(member_client, company, db):
    """`selfChange` 必須永遠鎖定在請求者自己的公司上。

    這支端點不接收 company id（改的是「我的公司」），所以它的正確性完全取決於
    查詢條件；一旦有人為了做後台功能而加上 `id` 參數，這條測試就會紅。
    """
    victim_company = factories.CompanyFactory(name="受害者公司")

    member_client.post(
        "/company/data/selfChange/",
        {"id": victim_company.id, "name": "已被竄改"},
        format="json",
    )

    victim_company.refresh_from_db()
    assert victim_company.name == "受害者公司", "竟能竄改他人公司資料"


def test_member_cannot_delete_another_members_self_image(member_client, member, db):
    """圖片刪除必須驗證擁有者。"""
    from apps.picture.models import SelfImage

    victim_member = factories.MemberFactory(name="受害者")
    victim_image = SelfImage.objects.create(
        member=victim_member,
        image=factories.tiny_png(),
        title="受害者的照片",
        active=True,
    )

    member_client.delete(
        "/picture/self-images/delete/", {"id": victim_image.id}, format="json"
    )
    assert SelfImage.objects.filter(pk=victim_image.pk).exists(), "竟能刪除他人照片"


def test_inactive_account_cannot_use_its_token(db):
    """帳號被停用後，既有的 JWT 必須立刻失效。

    停用帳號若只擋登入而不擋既有 token，被停權的人還能繼續用手上的 token
    操作最長達 `ACCESS_TOKEN_LIFETIME`。
    """
    from rest_framework.test import APIClient
    from rest_framework_simplejwt.tokens import RefreshToken

    user = factories.PrivateFactory(email="to-be-disabled@example.invalid")
    token = str(RefreshToken.for_user(user).access_token)

    user.is_active = False
    user.save()

    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    assert client.get("/basic/whoami").status_code == 401
