# apps/picture/serializer.py
from rest_framework import serializers
from apps.picture.models import SelfImage, CompanyImage, ProductImage, SlideImage, PopupAd
from apps.deal_base64 import Base64ImageField

class SelfImageSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = SelfImage
        fields = '__all__'
        
    def update(self, instance, validated_data):
        # 如果沒有提供新圖片，保留原有圖片
        if 'image' not in validated_data:
            validated_data['image'] = instance.image
        return super().update(instance, validated_data)

class CompanyImageSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = CompanyImage
        fields = ['id', 'image', 'title', 'description', 'priority', 'active', 'created_at' ,'company']
        
    def update(self, instance, validated_data):
        # 如果沒有提供新圖片，保留原有圖片
        if 'image' not in validated_data:
            validated_data['image'] = instance.image
        return super().update(instance, validated_data)

class ProductImageSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = ProductImage
        fields = '__all__'
        
    def update(self, instance, validated_data):
        # 如果沒有提供新圖片，保留原有圖片
        if 'image' not in validated_data:
            validated_data['image'] = instance.image
        return super().update(instance, validated_data)

class SlideImageSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = SlideImage
        fields = '__all__'
        extra_kwargs = {
            'image': {'required': True},  # 設定 `image` 為必填
        }
        
    def update(self, instance, validated_data):
        # 如果沒有提供新圖片，保留原有圖片
        if 'image' not in validated_data:
            validated_data['image'] = instance.image
        return super().update(instance, validated_data)

class PopupAdSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = PopupAd
        fields = ['id', 'image', 'priority', 'active', 'created_at', 'updated_at']  # 允許的字段
        read_only_fields = ['created_at', 'updated_at']  # 僅供讀取的字段
        
    def update(self, instance, validated_data):
        # 如果沒有提供新圖片，保留原有圖片
        if 'image' not in validated_data:
            validated_data['image'] = instance.image
        return super().update(instance, validated_data)