"""圖片 API：個人照片、公司照片、輪播、彈窗廣告。

圖片端點的共同重點：

* **上傳**必須真的存進 MEDIA_ROOT（測試設定已導向暫存目錄，不會污染 repo）
* **擁有者檢查**——`SelfImage.objects.get(id=..., member=request.user.member)`
  這種帶著擁有者條件的查詢是唯一的防線，少了它就是越權刪改（見
  `tests/security/test_authorization.py`）
* **前台顯示用的端點只回傳 active 的圖片**——否則已下架的輪播圖仍會出現在首頁
"""
import pytest

from apps.picture.models import PopupAd, SelfImage, SlideImage
from tests import factories

pytestmark = pytest.mark.django_db


# ══════════════════════════════════════════════════════════════════════
# 輪播圖（前台首頁）
# ══════════════════════════════════════════════════════════════════════
def test_active_slides_are_public(anon_client, db):
    factories.SlideImageFactory(title="上架中的輪播", active=True)
    factories.SlideImageFactory(title="已下架的輪播", active=False)

    response = anon_client.get("/picture/slide-images/active/")

    assert response.status_code == 200
    body = response.content.decode()
    assert "上架中的輪播" in body
    assert "已下架的輪播" not in body, "已下架的輪播圖仍出現在前台"


def test_active_slides_respect_priority_order(anon_client, db):
    """排序是 `-priority`（數字大的排前面），不是由小到大。"""
    factories.SlideImageFactory(title="優先度低", active=True, priority=1)
    factories.SlideImageFactory(title="優先度高", active=True, priority=9)

    body = anon_client.get("/picture/slide-images/active/").content.decode()
    assert body.index("優先度高") < body.index("優先度低")


def test_slide_cache_is_invalidated_when_slides_change(anon_client, staff_client, db):
    """輪播列表有 300 秒快取，任何寫入都必須清掉它。

    少了 invalidation，管理員上架新輪播後最長要等五分鐘才會出現在首頁，
    而且下架的圖同樣會繼續顯示——對「臨時撤下錯誤公告」這種需求是致命的。
    這條測試把 invalidation 釘死；哪天有人加了新的寫入動作卻忘記清快取，
    只要順手在這裡加一個案例就能抓到。
    """
    slide = factories.SlideImageFactory(title="會被下架的輪播", active=True)

    # 先讀一次，讓快取被填滿
    assert "會被下架的輪播" in anon_client.get("/picture/slide-images/active/").content.decode()

    staff_client.post(
        "/picture/slide-images/switch_active/", {"id": slide.id}, format="json"
    )

    after = anon_client.get("/picture/slide-images/active/").content.decode()
    assert "會被下架的輪播" not in after, "下架後仍從快取讀到舊資料"


def test_staff_can_add_a_slide(staff_client, db):
    response = staff_client.post(
        "/picture/slide-images/add/",
        {"image": factories.tiny_png(), "title": "新輪播", "type": "main", "active": True},
        format="multipart",
    )
    assert response.status_code in (200, 201), response.content[:300]
    assert SlideImage.objects.filter(title="新輪播").exists()


def test_staff_can_toggle_a_slide(staff_client, db):
    slide = factories.SlideImageFactory(active=False)

    response = staff_client.post(
        "/picture/slide-images/switch_active/", {"id": slide.id}, format="json"
    )
    assert response.status_code == 200

    slide.refresh_from_db()
    assert slide.active is True


def test_staff_can_remove_a_slide(staff_client, db):
    slide = factories.SlideImageFactory()

    staff_client.delete("/picture/slide-images/remove/", {"id": slide.id}, format="json")
    assert not SlideImage.objects.filter(pk=slide.pk).exists()


@pytest.mark.security
def test_regular_member_cannot_manage_slides(member_client, db):
    """輪播圖是首頁最顯眼的位置，只有 staff 能動。"""
    slide = factories.SlideImageFactory()

    assert member_client.post(
        "/picture/slide-images/add/", {"title": "越權新增"}, format="json"
    ).status_code in (401, 403)
    assert member_client.delete(
        "/picture/slide-images/remove/", {"id": slide.id}, format="json"
    ).status_code in (401, 403)
    assert SlideImage.objects.filter(pk=slide.pk).exists()


# ══════════════════════════════════════════════════════════════════════
# 彈窗廣告
# ══════════════════════════════════════════════════════════════════════
def test_popup_ads_are_readable_by_anyone(anon_client, db):
    factories.PopupAdFactory(active=True)
    assert anon_client.get("/picture/popup-ads/").status_code == 200


@pytest.mark.security
def test_only_staff_can_create_popup_ads(member_client, anon_client, db):
    """`IsAdminOrReadOnly`：所有人可讀，只有管理員能寫。"""
    for client in (anon_client, member_client):
        response = client.post(
            "/picture/popup-ads/", {"image": factories.tiny_png()}, format="multipart"
        )
        assert response.status_code in (401, 403)
    assert PopupAd.objects.count() == 0


def test_staff_can_toggle_a_popup_ad(staff_client, db):
    ad = factories.PopupAdFactory(active=False)

    response = staff_client.patch(f"/picture/popup-ads/{ad.id}/toggle_active/")
    assert response.status_code == 200

    ad.refresh_from_db()
    assert ad.active is True


# ══════════════════════════════════════════════════════════════════════
# 個人照片
# ══════════════════════════════════════════════════════════════════════
def test_member_uploads_their_own_photo(member_client, member):
    response = member_client.post(
        "/picture/self-images/new/",
        {"image": factories.tiny_png(), "title": "我的照片", "active": True},
        format="multipart",
    )
    assert response.status_code in (200, 201), response.content[:300]

    created = SelfImage.objects.get(title="我的照片")
    assert created.member_id == member.id, "照片竟被掛到別的會員底下"


def test_member_lists_only_their_own_photos(member_client, member, db):
    SelfImage.objects.create(
        member=member, image=factories.tiny_png(), title="我的照片", active=True
    )
    SelfImage.objects.create(
        member=factories.MemberFactory(),
        image=factories.tiny_png(),
        title="別人的照片",
        active=True,
    )

    body = member_client.get("/picture/self-images/selfInfo/").content.decode()
    assert "我的照片" in body
    assert "別人的照片" not in body


def test_member_deletes_their_own_photo(member_client, member):
    image = SelfImage.objects.create(
        member=member, image=factories.tiny_png(), title="待刪除", active=True
    )

    member_client.delete("/picture/self-images/delete/", {"id": image.id}, format="json")
    assert not SelfImage.objects.filter(pk=image.pk).exists()


@pytest.mark.security
def test_only_staff_can_list_every_members_photos(member_client, staff_client, db):
    assert member_client.get("/picture/self-images/all/").status_code in (401, 403)
    assert staff_client.get("/picture/self-images/all/").status_code == 200
