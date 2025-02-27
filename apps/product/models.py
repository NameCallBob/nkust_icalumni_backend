from django.db import models
from apps.company.models import Company
from drf_yasg import openapi
        
# 產品類別的 Swagger Schema
product_cate_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='類別ID'),
        'name': openapi.Schema(type=openapi.TYPE_STRING, description='類別名稱'),
        'created_at': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, description='建立日期'),
        'updated_at': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, description='更新日期'),
    },
    required=['name']
)

# 產品類別模型
class ProductCate(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="product_cate", verbose_name="所屬公司")
    name = models.CharField(max_length=255, verbose_name="類別名稱")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="建立日期")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新日期")

    class Meta:
        verbose_name = "產品類別"
        verbose_name_plural = "產品類別"
        unique_together = ('company', 'name')  # 公司內名稱唯一
        indexes = [models.Index(fields=['company', 'name'])]  # 加速查詢

    def __str__(self):
        return self.name

    

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
    category = models.ForeignKey(
        ProductCate,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="products",
        verbose_name="所屬類別"
    )    
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="product_set", verbose_name="所屬公司")
    name = models.CharField(max_length=255, verbose_name="產品名稱")
    description = models.TextField(verbose_name="產品簡介")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="建立日期")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新日期")

    class Meta:
        verbose_name = "產品"
        verbose_name_plural = "產品"

    def __str__(self):
        return self.name
    

product_image_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='產品圖片ID'),
        'product': openapi.Schema(type=openapi.TYPE_INTEGER, description='所屬產品ID'),
        'image': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_URI, description='圖片URL'),
        'is_primary': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='是否為主要圖片'),
        'created_at': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, description='上傳日期'),
    },
    required=['product', 'image']
)
class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images", verbose_name="所屬產品")
    image = models.ImageField(upload_to='static/product/', verbose_name="產品圖片")
    is_primary = models.BooleanField(default=False, verbose_name="是否為主要圖片")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="上傳日期")

    class Meta:
        verbose_name = "產品圖片"
        verbose_name_plural = "產品圖片"

    def __str__(self):
        return f"{self.product.name} - 圖片 {self.id}"