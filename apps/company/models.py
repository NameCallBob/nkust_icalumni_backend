from django.db import models
from apps.member.models import Member

class Industry(models.Model):
    title = models.CharField(max_length=50,null=False)
    intro = models.TextField()

class Company(models.Model):
    name = models.CharField(max_length=255, verbose_name="公司名稱")
    member = models.ForeignKey(Member , on_delete=models.CASCADE)
    industry = models.ForeignKey(Industry , on_delete=models.CASCADE)
    positions = models.CharField(max_length=255, verbose_name="公司在職職位")
    description = models.TextField(verbose_name="公司簡介")
    products = models.CharField(max_length=255, verbose_name="販售商品")
    product_description = models.TextField(verbose_name="販售商品簡介")
    photo = models.ImageField(upload_to='static/company/', verbose_name="照片", null=True, blank=True)
    website = models.URLField(max_length=500, verbose_name="公司網站連結")
    address = models.TextField(verbose_name="公司地點", null=True, blank=True)
    email = models.EmailField(verbose_name="聯絡信箱", null=True, blank=True)
    phone_number = models.CharField(max_length=20, verbose_name="聯絡電話", null=True, blank=True)
    
    class Meta:
        verbose_name = "公司"
        verbose_name_plural = "公司"

    def __str__(self):
        return self.name