from django.db import models
from apps.member.models import Member
from apps.company.models import Company
from apps.product.models import Product

class SelfImage(models.Model):
    member = models.ForeignKey(Member ,on_delete=models.CASCADE)
    image = models.ImageField(upload_to='self_image/')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    priority = models.IntegerField("優先度",default=0)
    active = models.BooleanField("是否使用")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

class CompanyImage(models.Model):
    company = models.ForeignKey(Company,on_delete=models.CASCADE)
    image = models.ImageField(upload_to='company_image/')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    priority = models.IntegerField("優先度",default=0)
    active = models.BooleanField("是否使用")
    created_at = models.DateTimeField(auto_now_add=True)

class ProductImage(models.Model):
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    image = models.ImageField(upload_to='product_image/')
    title = models.CharField(max_length=255,null=True)
    description = models.TextField(blank=True, null=True)
    priority = models.IntegerField("優先度",default=0)
    active = models.BooleanField("是否使用")
    created_at = models.DateTimeField(auto_now_add=True)

class SlideImage(models.Model):
    type = models.TextField(default="None", null=False)
    image = models.ImageField(upload_to='slide/')
    title = models.CharField(max_length=255,null=True)
    description = models.TextField(blank=True, null=True)
    link_url = models.URLField("超連結", blank=True, null=True, help_text="點擊輪播圖片時要導向的網址")
    priority = models.IntegerField("優先度",default=0)
    active = models.BooleanField("是否使用")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # [效能修補 M1] 前台輪播以 active 篩選並依 priority 排序
        indexes = [
            models.Index(fields=['active', 'priority'], name='slide_active_priority_idx'),
        ]

class PopupAd(models.Model):
    image =  models.ImageField(upload_to='popup/')
    priority = models.IntegerField("優先度",default=0)
    active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        # [效能修補 M1] 前台彈窗以 active 篩選
        indexes = [
            models.Index(fields=['active'], name='popupad_active_idx'),
        ]

    def __str__(self):
        return f"PopupAd (Active: {self.active})"