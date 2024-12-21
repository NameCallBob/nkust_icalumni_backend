from rest_framework import serializers
from apps.picture.models import SelfImage, CompanyImage, ProductImage, SlideImage , PopupAd
from apps.deal_base64 import Base64ImageField
class SelfImageSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = SelfImage
        fields = '__all__'

class CompanyImageSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = CompanyImage
        fields = ['id', 'image', 'title', 'description', 'priority', 'active', 'created_at' ,'company']

class ProductImageSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = ProductImage
        fields = '__all__'

class SlideImageSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = SlideImage
        fields = '__all__'
        extra_kwargs = {
            'image': {'required': True},  # 設定 `image` 為必填
        }

class PopupAdSerializer(serializers.ModelSerializer):
    image = Base64ImageField()
    
    class Meta:
        model = PopupAd
        fields = ['id', 'image', 'active', 'created_at', 'updated_at']  # 允許的字段
        read_only_fields = ['created_at', 'updated_at']  # 僅供讀取的字段
