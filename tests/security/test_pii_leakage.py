"""個資外洩掃描：公開端點回傳的內容裡不得出現任何個資。

做法是「哨兵值」（sentinel）掃描：建立一筆會員，把電話、地址、生日、帳號 email
等欄位塞進獨一無二、不可能自然出現的字串，然後把**每一條匿名可讀的路由**打一遍，
在回應的原始位元組裡搜尋這些哨兵值。

這個做法的好處是它不需要知道任何序列化器的細節，所以：

* 有人在公開的序列化器 `fields` 裡多加一個 `home_phone` → 立刻紅燈
* 有人把某支端點的 `MemberSimpleSerializer` 換成 `MemberSerializer`（全欄位）→ 立刻紅燈
* 有人新增一支公開端點卻忘了過濾欄位 → 立刻紅燈（新路由會自動被納入掃描）

對系友會網站來說這件事特別重要：會員的手機、住家地址與生日一旦被公開端點吐出來，
就會被爬蟲收走，而且無法回收。
"""
import pytest

from tests import factories
from tests.helpers import concrete_url
from tests.route_map import collect_routes

pytestmark = [pytest.mark.security, pytest.mark.django_db]

# 這些字串不可能出現在任何正常回應裡，一旦出現就是從資料庫漏出來的。
SENTINELS = {
    "home_phone": "0287654321",
    "mobile_phone": "0955000111",
    "address": "PII哨兵地址請勿外洩",
    "birth_date": "1990-01-15",
    "account_email": "pii-sentinel@example.invalid",
}

ANONYMOUSLY_READABLE = [r for r in collect_routes() if r.anonymously_readable]


@pytest.fixture
def public_dataset(db):
    """建立一份「已公開」的資料，其中夾帶哨兵個資。

    刻意把每個模型都設成公開狀態（is_show / active / is_featured 都是 True），
    確保公開端點真的會回傳到這筆資料——如果資料根本不會被回傳，這個掃描就
    什麼都測不到，變成假的綠燈。
    """
    user = factories.PrivateFactory(email=SENTINELS["account_email"])
    member = factories.MemberFactory(
        private=user,
        name="公開系友",
        home_phone=SENTINELS["home_phone"],
        mobile_phone=SENTINELS["mobile_phone"],
        address=SENTINELS["address"],
        birth_date=SENTINELS["birth_date"],
        is_show=True,
        is_paid=True,
    )
    company = factories.CompanyFactory(member=member, name="公開公司")
    factories.ProductFactory(company=company)
    factories.OutstandingAlumniFactory(member=member, is_featured=True)
    factories.SchoolOutstandingAlumniFactory(member=member, is_featured=True)
    recruit = factories.RecruitFactory(company=company, active=True)
    # 職缺一定要配一筆 Contact：沒有 Contact 的職缺會讓公開端點直接 500
    # （見 tests/api/test_recruit_api.py::test_public_listing_survives_recruit_without_contact），
    # 那個崩潰會遮蔽掉這裡真正要掃的個資問題。
    factories.RecruitContactFactory(recruit=recruit)
    factories.ArticleFactory(active=True)
    factories.SlideImageFactory(active=True)
    factories.PopupAdFactory(active=True)
    factories.AlumniAssociationFactory()
    factories.OrganizationalStructureFactory()
    factories.MembershipRequirementFactory()
    return {"member": member, "company": company, "user": user}


def _leaks(body: str):
    return {name: value for name, value in SENTINELS.items() if value in body}


@pytest.mark.parametrize("route", ANONYMOUSLY_READABLE, ids=lambda r: r.key)
def test_public_endpoint_does_not_leak_pii(anon_client, public_dataset, route):
    """逐一掃描每條匿名可讀的路由。"""
    member = public_dataset["member"]
    # 多帶幾個常見的查詢參數名，讓需要 id 的端點也能真的取到資料；
    # 端點用不到的參數會被忽略，不影響其他路由。
    params = {"id": member.id, "member_id": member.id, "pk": member.id}

    response = anon_client.get(concrete_url(route.path), params)
    if response.status_code >= 400:
        # 4xx 沒有資料主體可外洩，不是這支測試的守備範圍
        # （「公開端點不得 5xx」由 test_permission_matrix 負責）。
        return

    leaked = _leaks(response.content.decode("utf-8", errors="replace"))
    assert not leaked, (
        f"公開端點 {route.key} 洩漏了個資欄位：{sorted(leaked)}\n"
        f"實際內容片段：{response.content[:400]!r}\n\n"
        "公開端點只能回傳姓名、性別、自介、照片、職位、畢業資訊這類已同意公開的欄位。"
        "需要完整個資請改走需登入且限本人／staff 的端點。"
    )


# Django 各種密碼雜湊的字首，以及序列化器不小心把 password 欄位帶出去時的 JSON key。
PASSWORD_MARKERS = ("pbkdf2_", "argon2$", "bcrypt$", "md5$", '"password"')


def test_public_endpoints_never_expose_password_hashes(anon_client, public_dataset):
    """密碼欄位與雜湊不得出現在任何公開回應中。

    雜湊外洩等同離線暴力破解的起點。最常見的成因是某個序列化器寫了
    `fields = '__all__'` 而該模型剛好有 password 欄位。
    """
    offenders = []
    for route in ANONYMOUSLY_READABLE:
        body = anon_client.get(concrete_url(route.path)).content.decode(
            "utf-8", errors="replace"
        )
        hits = [m for m in PASSWORD_MARKERS if m in body]
        if hits:
            offenders.append(f"{route.key} → {hits}")

    assert not offenders, "公開端點回應含有密碼相關內容：\n" + "\n".join(offenders)


# ══════════════════════════════════════════════════════════════════════
# 針對性檢查：公開會員端點的欄位白名單
# ══════════════════════════════════════════════════════════════════════
PUBLIC_MEMBER_FIELDS = {
    "id", "name", "gender", "intro", "photo", "position", "graduate",
    "company", "company_images", "self_images",
}


def test_public_member_detail_returns_only_whitelisted_fields(anon_client, public_dataset):
    """`/member/any/getOne/` 的欄位集合被釘死。

    這是全站最敏感的公開端點——它以 id 取單一會員，天然可被列舉。欄位白名單
    寫死在測試裡，任何新增欄位都必須先修改這份清單，強迫作者停下來想一次
    「這個欄位真的可以對全世界公開嗎」。
    """
    member = public_dataset["member"]
    response = anon_client.get("/member/any/getOne/", {"id": member.id})

    assert response.status_code == 200
    assert set(response.data) <= PUBLIC_MEMBER_FIELDS, (
        f"公開會員端點多回傳了未經審核的欄位："
        f"{sorted(set(response.data) - PUBLIC_MEMBER_FIELDS)}"
    )


def test_public_member_detail_hides_members_who_opted_out(anon_client, db):
    """`is_show=False` 的會員不得從公開端點取得。

    這是會員對「要不要公開自己」的選擇，必須被端點尊重；漏掉這個過濾條件
    等同把全部會員名冊公開。
    """
    hidden = factories.MemberFactory(name="不公開的系友", is_show=False)
    response = anon_client.get("/member/any/getOne/", {"id": hidden.id})
    assert response.status_code == 404


def test_public_member_search_hides_members_who_opted_out(anon_client, db):
    """公開搜尋端點同樣必須套用 is_show 過濾。"""
    factories.MemberFactory(name="不公開的系友XYZ", is_show=False)
    factories.MemberFactory(name="公開的系友ABC", is_show=True)

    body = anon_client.get("/member/search_user/").content.decode()
    assert "不公開的系友XYZ" not in body, "公開搜尋回傳了 is_show=False 的會員。"


def test_logged_in_member_cannot_read_another_members_pii(
    member_client, other_member
):
    """一般會員不得以 id 讀取他人完整個資（SEC-002）。

    沒有這道檢查，任何一個註冊帳號就能靠 id 逐一列舉，把整份會員名冊連同
    電話地址下載下來——比端點公開更隱蔽，因為存取記錄看起來都是「合法登入者」。
    """
    response = member_client.get("/member/logined/getOne/", {"id": other_member.id})
    assert response.status_code == 403


def test_member_can_read_own_pii(member_client, member):
    response = member_client.get("/member/logined/getOne/", {"id": member.id})
    assert response.status_code == 200


def test_staff_can_read_any_member_pii(staff_client, other_member):
    response = staff_client.get("/member/logined/getOne/", {"id": other_member.id})
    assert response.status_code == 200


# ══════════════════════════════════════════════════════════════════════
# 已知的個資「可驗證性」問題
# ══════════════════════════════════════════════════════════════════════
def test_public_alumni_search_matches_against_private_phone_and_address(anon_client, db):
    """記錄一項現況：公開搜尋會拿關鍵字去比對電話與住址欄位。

    這不是「外洩」——回應只含公開欄位，電話本身不會被吐出來。但它構成一個
    **驗證預言機（oracle）**：任何人都能輸入一支手機號碼，從「有沒有搜到人」
    判斷這支號碼是不是某位系友的。對已知號碼做反查，或拿外流名單做交叉比對，
    都因此變得可行。

    這條測試刻意寫成「斷言現況」而不是「斷言修好了」，用意是把這個行為變成
    **明文記錄且會被 review 看到**的決定。若日後把電話／住址從搜尋條件移除
    （建議如此），這條測試會失敗，屆時直接刪掉它即可。
    """
    factories.MemberFactory(
        name="可被反查的系友",
        mobile_phone="0987654321",
        address="某條不公開的路100號",
        is_show=True,
    )

    by_phone = anon_client.get("/member/any/alumni-search/", {"q": "0987654321"})
    by_address = anon_client.get("/member/any/alumni-search/", {"q": "某條不公開的路"})

    def _hit_count(response):
        data = response.data
        return data.get("count", len(data)) if isinstance(data, dict) else len(data)

    assert _hit_count(by_phone) > 0, (
        "電話已不再是搜尋條件——這是好事，請刪除這條記錄用的測試。"
    )
    assert _hit_count(by_address) > 0, (
        "住址已不再是搜尋條件——這是好事，請刪除這條記錄用的測試。"
    )

    # 但無論如何，回應本身都不得含有電話或住址原始值。
    for response in (by_phone, by_address):
        body = response.content.decode()
        assert "0987654321" not in body
        assert "某條不公開的路100號" not in body
