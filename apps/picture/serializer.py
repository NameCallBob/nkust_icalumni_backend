from rest_framework import serializers
from apps.picture.models import SelfImage, CompanyImage, ProductImage, SlideImage
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
