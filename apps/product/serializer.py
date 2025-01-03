from rest_framework import serializers
from apps.product.models import Product, ProductImage , ProductCate
import base64 , mimetypes
from django.core.files.base import ContentFile
from apps.company.models import Company

from concurrent.futures import ThreadPoolExecutor, as_completed
import logging

logger = logging.getLogger(__name__)


class ProductImageSerializer(serializers.ModelSerializer):
    # image = serializers.SerializerMethodField()

    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'is_primary', 'created_at']

    # def get_image(self, obj):
    #     """
    #     將圖片轉換為 Base64 格式後回傳。
    #     """
    #     if obj.image:
    #         try:
    #             with obj.image.open('rb') as image_file:
    #                 encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
                    
    #                 # 使用 mimetypes 根據文件名稱判斷 MIME 類型
    #                 mime_type, _ = mimetypes.guess_type(obj.image.name)
    #                 if not mime_type:
    #                     mime_type = "application/octet-stream"  # 預設 MIME 類型

    #                 return f"data:{mime_type};base64,{encoded_image}"
    #         except Exception as e:
    #             logger.error(f"Error encoding image {obj.id}: {e}")
    #             return None
    #     return None


class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)  # 保持原設計
    new_images = serializers.ListField(
        child=serializers.DictField(), write_only=True, required=False,
        help_text="包含新圖片的字典列表，每個字典包括 `image` 和 `is_primary`"
    )
    category = serializers.PrimaryKeyRelatedField(
        queryset=ProductCate.objects.all(),
        required=False,  
        allow_null=True, 
        help_text="產品分類的ID"
    )
    
    def to_internal_value(self, data):
        if data == "":
            return None
        try:
            return super().to_internal_value(data)
        except serializers.ValidationError:
            return None
        
    class Meta:
        model = Product
        fields = [
            'id', 'company', 'name', 'description', 'is_active',
            'created_at', 'updated_at', 'images', 'new_images', 'category'
        ]

    def create(self, validated_data):
        new_images_data = validated_data.pop('new_images', [])
        product = super().create(validated_data)
        self._handle_new_images(product, new_images_data)  # 處理新圖片
        return product

    def update(self, instance, validated_data):
        new_images_data = validated_data.pop('new_images', [])
        instance = super().update(instance, validated_data)
        self._handle_new_images(instance, new_images_data)  # 處理新圖片
        return instance

    def _handle_new_images(self, product, new_images_data):
        """
        處理前端傳入的 `new_images`。
        """
        for image_data in new_images_data:
            try:
                image_base64 = image_data.get('image')
                is_primary = image_data.get('is_primary', False)

                # 解析 Base64 字串並創建圖片檔案
                format, imgstr = image_base64.split(';base64,')
                ext = format.split('/')[-1]
                image_file = ContentFile(base64.b64decode(imgstr), name=f"product_{product.id}.{ext}")

                # 儲存圖片
                ProductImage.objects.create(product=product, image=image_file, is_primary=is_primary)
            except Exception as e:
                logger.error(f"Error saving image for product {product.id}: {e}")

class ProductCateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCate
        fields = ['id', 'name', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

    def create(self, validated_data):
        """
        自動填充 company 為登入使用者的公司
        """
        request = self.context.get('request')
        if not request or not request.user or not request.user.is_authenticated:
            raise serializers.ValidationError("無法確認使用者登入狀態，無法創建分類。")
        
        member = getattr(request.user, 'member', None)
        if not member:
            raise serializers.ValidationError("無法找到與使用者關聯的公司。")
        
        validated_data['company'] = Company.objects.get(member=member)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data.pop('company', None)
        return super().update(instance, validated_data)