from rest_framework import serializers
from apps.product.models import Product, ProductImage , ProductCate
import base64
from django.core.files.base import ContentFile
from apps.company.models import Company

from concurrent.futures import ThreadPoolExecutor, as_completed
import logging

logger = logging.getLogger(__name__)


class ProductImageSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'is_primary', 'created_at']

    def get_image(self, obj):
        if obj.image:
            try:
                with obj.image.open('rb') as image_file:
                    encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
                    return f"data:{obj.image.file.content_type};base64,{encoded_image}"
            except Exception as e:
                logger.error(f"Error encoding image {obj.id}: {e}")
                return None
        return None


class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True)
    new_images = serializers.ListField(
        child=serializers.CharField(), write_only=True, required=False,
        help_text="Base64編碼的圖片列表"
    )
    category = serializers.PrimaryKeyRelatedField(
        queryset=ProductCate.objects.all(),
        required=True,
        help_text="產品分類的ID"
    )

    class Meta:
        model = Product
        fields = [
            'id', 'company', 'name', 'description', 'is_active',
            'created_at', 'updated_at', 'images', 'new_images', 'category'
        ]

    def create(self, validated_data):
        category = validated_data.pop('category', None)
        validated_data['category'] = category
        new_images = validated_data.pop('new_images', [])
        product = super().create(validated_data)
        self._handle_new_images(product, new_images)
        return product

    def update(self, instance, validated_data):
        category = validated_data.pop('category', None)
        if category:
            validated_data['category'] = category
        new_images = validated_data.pop('new_images', [])
        instance = super().update(instance, validated_data)
        self._handle_new_images(instance, new_images)
        return instance

    def _handle_new_images(self, product, new_images):
        """
        使用多執行緒處理多張圖片的 Base64 字串。
        """
        def process_image(image_data, product):
            try:
                # 解析 Base64 字串並創建圖片檔案
                format, imgstr = image_data.split(';base64,')
                ext = format.split('/')[-1]
                image_file = ContentFile(base64.b64decode(imgstr), name=f"product_{product.id}.{ext}")
                ProductImage.objects.create(product=product, image=image_file)
            except Exception as e:
                # 記錄錯誤
                logger.error(f"Error saving image for product {product.id}: {e}")

        # 使用多執行緒加速圖片處理
        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(process_image, image_data, product) for image_data in new_images]
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    logger.error(f"Unhandled exception in image saving thread: {e}")

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