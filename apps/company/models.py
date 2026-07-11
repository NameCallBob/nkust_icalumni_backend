
from apps.member.models import Member
from django.db import models
from django.db.models import Q


class Industry(models.Model):
    title = models.CharField(max_length=50, null=False)
    intro = models.TextField(null=True)

    class Meta:
        verbose_name = "產業列"
        verbose_name_plural = "產業列"

    def __str__(self):
        return self.title

class Company(models.Model):
    name = models.CharField(max_length=255, verbose_name="公司名稱", null=True, blank=True)
    # 關聯欄位也需要允許為空
    member = models.OneToOneField(Member, related_name="company", on_delete=models.CASCADE, null=True, blank=True)
    industry = models.ForeignKey(Industry, related_name="industry", on_delete=models.SET_DEFAULT, default=1, null=True, blank=True)
    positions = models.CharField(max_length=255, verbose_name="公司在職職位", null=True, blank=True)
    description = models.TextField(verbose_name="公司簡介", null=True, blank=True)
    products = models.CharField(max_length=255, verbose_name="販售商品", null=True, blank=True)
    product_description = models.TextField(verbose_name="販售商品簡介", null=True, blank=True)
    photo = models.ImageField(upload_to='company/', verbose_name="照片", null=True, blank=True)
    website = models.URLField(max_length=500, verbose_name="公司網站連結", null=True, blank=True)
    address = models.TextField(verbose_name="公司地點", null=True, blank=True)
    email = models.EmailField(verbose_name="聯絡信箱", null=True, blank=True)
    clicks = models.BigIntegerField("點擊次數", default=0)
    phone_number = models.CharField(max_length=100, verbose_name="聯絡電話", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "公司"
        verbose_name_plural = "公司"
        # [效能修補 M1] 將先前 migration 加入但模型未宣告的索引補回模型，保持狀態一致。
        indexes = [
            models.Index(fields=['clicks'], name='company_clicks_idx'),
            models.Index(fields=['created_at'], name='company_created_at_idx'),
        ]

    def __str__(self):
        return self.name

    @classmethod
    def search_companies(
        cls,
        name=None,
        industry=None,
        positions=None,
        products=None,
        product_description=None,
        member=None,
        email=None,
        phone_number=None
    ):
        query = Q()

        if name:
            query &= Q(name__icontains=name)
        if industry:
            query &= Q(industry__title__icontains=industry)
        if positions:
            query &= Q(positions__icontains=positions)
        if products:
            query &= Q(products__icontains=products)
        if product_description:
            query &= Q(product_description__icontains=product_description)
        if member:
            query &= Q(member__name__icontains=member)
        if email:
            query &= Q(email__icontains=email)
        if phone_number:
            query &= Q(phone_number__icontains=phone_number)

        return cls.objects.filter(query)

    @classmethod
    def search_in_all_fields(cls, keyword):
        """
        在所有欄位搜尋包含指定單詞的公司
        """
        query = (
            Q(name__icontains=keyword) |
            Q(industry__title__icontains=keyword) |
            Q(positions__icontains=keyword) |
            Q(description__icontains=keyword) |
            Q(products__icontains=keyword) |
            Q(product_description__icontains=keyword) |
            Q(member__name__icontains=keyword) |
            Q(email__icontains=keyword) |
            Q(phone_number__icontains=keyword) |
            Q(website__icontains=keyword) |
            Q(address__icontains=keyword)
        )

        return cls.objects.filter(query)
