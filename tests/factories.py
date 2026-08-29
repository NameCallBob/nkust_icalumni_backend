"""模型工廠：測試資料的**唯一**建立管道。

為什麼要有這一層
----------------
本專案的模型幾乎所有欄位都 ``null=True``，直接 ``Model.objects.create()`` 很容易
建出「現實中不可能存在」的資料，讓測試通過但正式環境爆炸。工廠替每個模型定義
一組合理的預設值，測試只需要覆寫真正在乎的欄位::

    member = MemberFactory(name="王小明", is_show=True)

另外，`Private.objects.create_user()` 會開一條背景執行緒寄歡迎信；工廠刻意
**不走** 那條路徑（直接建物件 + set_password），使建帳號在測試中是純粹、同步、
無副作用的動作。要驗證「建帳號會寄信」的測試，請自行呼叫 `create_user`。
"""
import io

import factory
from django.core.files.uploadedfile import SimpleUploadedFile

from apps.article.models import Article, ArticleImage
from apps.company.models import Company, Industry
from apps.Info.models import (
    AlumniAssociation,
    Constitution,
    MembershipRequirement,
    MembershipRequirement_v2,
    OrganizationalStructure,
)
from apps.member.models import (
    Graduate,
    Member,
    OutstandingAlumni,
    Position,
    SchoolOutstandingAlumni,
)
from apps.picture.models import PopupAd, SlideImage
from apps.private.models import Private
from apps.product.models import Product, ProductCate
from apps.recruit.models import Contact, Recruit

# 測試中一律使用 .invalid 頂級網域（RFC 2606 保留，保證不會對應到真實信箱），
# 避免任何一次「不小心真的寄出去」。
TEST_EMAIL_DOMAIN = "example.invalid"

# 通過本專案密碼強度驗證器（長度、非純數字、非常見密碼）的測試密碼。
DEFAULT_TEST_PASSWORD = "Passw0rd!Test123"


def tiny_png(name="test.png"):
    """回傳一個最小合法 PNG 的 SimpleUploadedFile，供 ImageField 測試使用。

    Pillow 會實際解析上傳的圖檔，隨便塞 b"x" 會在 ImageField 驗證階段就失敗，
    測到的是「假的失敗」而不是被測邏輯。
    """
    from PIL import Image

    buffer = io.BytesIO()
    Image.new("RGB", (2, 2), color=(0, 82, 155)).save(buffer, format="PNG")
    return SimpleUploadedFile(name, buffer.getvalue(), content_type="image/png")


def tiny_pdf(name="test.pdf"):
    """回傳一個最小合法 PDF 的 SimpleUploadedFile，供 FileField 測試使用。"""
    content = (
        b"%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n"
        b"2 0 obj<</Type/Pages/Kids[]/Count 0>>endobj\n"
        b"trailer<</Root 1 0 R>>\n%%EOF\n"
    )
    return SimpleUploadedFile(name, content, content_type="application/pdf")


# ══════════════════════════════════════════════════════════════════════
# 帳號
# ══════════════════════════════════════════════════════════════════════
class PrivateFactory(factory.django.DjangoModelFactory):
    """使用者帳號。預設為一般會員；`is_staff=True` / `is_superuser=True` 可覆寫。"""

    class Meta:
        model = Private
        skip_postgeneration_save = True

    email = factory.Sequence(lambda n: f"user{n}@{TEST_EMAIL_DOMAIN}")
    is_active = True
    is_staff = False
    is_superuser = False

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        # 刻意不用 CustomUserManager.create_user——它會開背景執行緒寄歡迎信。
        raw_password = kwargs.pop("password", DEFAULT_TEST_PASSWORD)
        user = model_class(*args, **kwargs)
        user.set_password(raw_password)
        user.save()
        # 讓測試可以直接拿明文密碼去打登入端點，不必記在別處。
        user.raw_password = raw_password
        return user


# ══════════════════════════════════════════════════════════════════════
# 會員
# ══════════════════════════════════════════════════════════════════════
class PositionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Position

    title = factory.Sequence(lambda n: f"職位{n}")
    priority = factory.Sequence(lambda n: n)


class GraduateFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Graduate

    school = "國立高雄科技大學智慧商務系"
    grade = "110"
    student_id = factory.Sequence(lambda n: f"C1101{n:05d}")


class MemberFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Member

    private = factory.SubFactory(PrivateFactory)
    name = factory.Sequence(lambda n: f"系友{n}")
    gender = "M"
    position = factory.SubFactory(PositionFactory)
    graduate = factory.SubFactory(GraduateFactory)
    intro = "測試用自我介紹"
    is_paid = True
    # 預設不公開：對應「預設拒絕」原則，需要公開的測試自己標明 is_show=True，
    # 這樣「公開端點外洩非公開資料」的 bug 才會被測出來而不是被預設值蓋掉。
    is_show = False


class OutstandingAlumniFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = OutstandingAlumni

    member = factory.SubFactory(MemberFactory)
    highlight = "傑出事蹟摘要"
    achievements = "詳細成就描述"
    is_featured = False
    sort_order = 0


class SchoolOutstandingAlumniFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = SchoolOutstandingAlumni

    member = factory.SubFactory(MemberFactory)
    highlight = "傑出校友事蹟摘要"
    achievements = "詳細成就描述"
    is_featured = False
    sort_order = 0


# ══════════════════════════════════════════════════════════════════════
# 公司／產品
# ══════════════════════════════════════════════════════════════════════
class IndustryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Industry

    title = factory.Sequence(lambda n: f"產業{n}")
    intro = "產業說明"


class CompanyFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Company

    name = factory.Sequence(lambda n: f"測試公司{n}")
    member = factory.SubFactory(MemberFactory)
    industry = factory.SubFactory(IndustryFactory)
    positions = "工程師"
    description = "公司簡介"
    products = "測試商品"
    product_description = "商品簡介"
    website = "https://example.invalid"
    address = "高雄市三民區建工路415號"
    email = factory.Sequence(lambda n: f"company{n}@{TEST_EMAIL_DOMAIN}")
    phone_number = "07-1234567"


class ProductCateFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ProductCate

    company = factory.SubFactory(CompanyFactory)
    name = factory.Sequence(lambda n: f"類別{n}")


class ProductFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Product

    company = factory.SubFactory(CompanyFactory)
    category = None
    name = factory.Sequence(lambda n: f"產品{n}")
    description = "產品簡介"
    is_active = True


# ══════════════════════════════════════════════════════════════════════
# 徵才
# ══════════════════════════════════════════════════════════════════════
class RecruitFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Recruit

    company = factory.SubFactory(CompanyFactory)
    title = factory.Sequence(lambda n: f"職缺{n}")
    intro = "<p>職缺說明</p>"
    deadline = factory.LazyFunction(
        lambda: __import__("datetime").date.today() + __import__("datetime").timedelta(days=30)
    )
    active = True


class RecruitContactFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Contact

    recruit = factory.SubFactory(RecruitFactory)
    company_name = "測試公司"
    name = "聯絡人"
    phone = "0912345678"
    email = factory.Sequence(lambda n: f"contact{n}@{TEST_EMAIL_DOMAIN}")


# ══════════════════════════════════════════════════════════════════════
# 文章／圖片
# ══════════════════════════════════════════════════════════════════════
class ArticleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Article

    title = factory.Sequence(lambda n: f"文章{n}")
    content = "<p>文章內容</p>"
    # 同 MemberFactory.is_show：預設不公開。
    active = False


class ArticleImageFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ArticleImage

    article = factory.SubFactory(ArticleFactory)
    image = factory.LazyFunction(tiny_png)
    pic_type = "small"
    priority = 0


class SlideImageFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = SlideImage

    type = "main"
    image = factory.LazyFunction(tiny_png)
    title = factory.Sequence(lambda n: f"輪播{n}")
    description = "輪播說明"
    priority = 0
    active = False


class PopupAdFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = PopupAd

    image = factory.LazyFunction(tiny_png)
    priority = 0
    active = False


# ══════════════════════════════════════════════════════════════════════
# 系友會簡介（Info）
# ══════════════════════════════════════════════════════════════════════
class AlumniAssociationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = AlumniAssociation

    description = "<p>系友會簡介</p>"


class ConstitutionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Constitution

    description = "<p>章程說明</p>"
    pdf_file = factory.LazyFunction(tiny_pdf)


class OrganizationalStructureFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = OrganizationalStructure

    description = "<p>組織架構</p>"


class MembershipRequirementFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = MembershipRequirement

    description = "<p>入會條件</p>"


class MembershipRequirementV2Factory(factory.django.DjangoModelFactory):
    class Meta:
        model = MembershipRequirement_v2

    description = "<p>入會條件 v2</p>"
    pdf_file = factory.LazyFunction(tiny_pdf)
