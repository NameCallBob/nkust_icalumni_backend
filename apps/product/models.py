from django.db import models
from apps.company.models import Company
from drf_yasg import openapi

product_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='產品ID'),
        'company': openapi.Schema(type=openapi.TYPE_INTEGER, description='所屬公司ID'),
        'name': openapi.Schema(type=openapi.TYPE_STRING, description='產品名稱'),
        'description': openapi.Schema(type=openapi.TYPE_STRING, description='產品簡介'),
        'photo': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_URI, description='產品照片URL'),
        'created_at': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, description='建立日期'),
        'updated_at': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, description='更新日期'),
    },
    required=['company', 'name', 'description'],
)
class Product(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="product_set", verbose_name="所屬公司")
    name = models.CharField(max_length=255, verbose_name="產品名稱")
    description = models.TextField(verbose_name="產品簡介")
    photo = models.ImageField(upload_to='static/product/', verbose_name="產品照片", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="建立日期")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新日期")

    class Meta:
        verbose_name = "產品"
        verbose_name_plural = "產品"

    def __str__(self):
        return self.name