from rest_framework import serializers
from apps.product.models import Product, ProductImage
import base64
from django.core.files.base import ContentFile

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
                return None
        return None


class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)

    new_images = serializers.ListField(
        child=serializers.CharField(), write_only=True, required=False,
        help_text="Base64編碼的圖片列表"
    )

    class Meta:
        model = Product
        fields = ['id', 'company', 'name', 'description', 'is_active', 'created_at', 'updated_at', 'images', 'new_images']

    def create(self, validated_data):
        new_images = validated_data.pop('new_images', [])
        product = super().create(validated_data)
        self._handle_new_images(product, new_images)
        return product

    def update(self, instance, validated_data):
        new_images = validated_data.pop('new_images', [])
        instance = super().update(instance, validated_data)
        self._handle_new_images(instance, new_images)
        return instance

    def _handle_new_images(self, product, new_images):
        for image_data in new_images:
            try:
                format, imgstr = image_data.split(';base64,')
                ext = format.split('/')[-1]
                image_file = ContentFile(base64.b64decode(imgstr), name=f"product_{product.id}.{ext}")
                ProductImage.objects.create(product=product, image=image_file)
            except Exception as e:
                continue
