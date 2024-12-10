from django.db import models
from apps.member.models import Member
from apps.company.models import Company
from apps.product.models import Product

class SelfImage(models.Model):
    member = models.ForeignKey(Member ,on_delete=models.CASCADE)
    image = models.ImageField(upload_to='static/self_image/')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    priority = models.IntegerField("優先度",default=0)
    active = models.BooleanField("是否使用")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

class CompanyImage(models.Model):
    company = models.ForeignKey(Company,on_delete=models.CASCADE)
    image = models.ImageField(upload_to='static/company_image/')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    priority = models.IntegerField("優先度",default=0)
    active = models.BooleanField("是否使用")
    created_at = models.DateTimeField(auto_now_add=True)

class ProductImage(models.Model):
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    image = models.ImageField(upload_to='static/product_image/')
    title = models.CharField(max_length=255,null=True)
    description = models.TextField(blank=True, null=True)
    priority = models.IntegerField("優先度",default=0)
    active = models.BooleanField("是否使用")
    created_at = models.DateTimeField(auto_now_add=True)

class SlideImage(models.Model):
    type = models.TextField(default="None", null=False)
    image = models.ImageField(upload_to='static/slide/')
    title = models.CharField(max_length=255,null=True)
    description = models.TextField(blank=True, null=True)
    active = models.BooleanField("是否使用")
    created_at = models.DateTimeField(auto_now_add=True)
