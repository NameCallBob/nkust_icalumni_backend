from rest_framework import serializers
from apps.company.models import Company , Industry

class IndustrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Industry
        fields = ['id', 'title', 'intro']  # 包含所有需要的欄位


class CompanySearchSerializer(serializers.ModelSerializer):
    industry = IndustrySerializer()
    class Meta:
        model = Company
        fields = ['id', 'name', 'industry', 'positions', 'description', 'products',
                  'product_description', 'photo', 'website', 'address', 'email',
                  'clicks', 'phone_number', 'created_at']

import base64
from django.core.files.base import ContentFile

class CompanySerializer(serializers.ModelSerializer):
    industry = serializers.CharField(source='industry.title')  # 只序列化 industry 的 title
    member_name = serializers.SerializerMethodField()
    photo = serializers.CharField(write_only=True)  # 改為處理 Base64 的圖片資料

    def get_member_name(self, instance):
        return instance.member.name

    class Meta:
        model = Company
        fields = ['id', 'name', 'member', 'industry', 'positions', 'description', 'products',
                  'product_description', 'photo', 'website', 'address', 'email',
                  'clicks', 'phone_number', 'created_at', 'member_name']

    def create(self, validated_data):
        # 處理 industry 關聯
        industry = validated_data.pop('industry')

        # 處理圖片的 Base64 解碼
        photo_data = validated_data.pop('photo', None)
        if photo_data:
            format, imgstr = photo_data.split(';base64,')
            ext = format.split('/')[-1]
            photo = ContentFile(base64.b64decode(imgstr), name=f"company_photo.{ext}")
        else:
            photo = None

        # 建立公司
        # NOTE:由於只序列化 industry 的 title，所以industry型態會為{'title':'1'}
        company = Company.objects.create(industry=Industry.objects.get(id=industry['title']), photo=photo, **validated_data)
        return company

    def update(self, instance, validated_data):
        # 處理 industry 的修改
        industry = validated_data.get('industry', None)
        if industry:
            instance.industry = industry['title']

        # 處理圖片的 Base64 解碼更新
        photo_data = validated_data.get('photo', None)
        if photo_data:
            format, imgstr = photo_data.split(';base64,')
            ext = format.split('/')[-1]
            instance.photo = ContentFile(base64.b64decode(imgstr), name=f"company_photo.{ext}")

        # 逐步處理其他欄位，使用 get 方法來支援部分更新
        instance.name = validated_data.get('name', instance.name)
        instance.positions = validated_data.get('positions', instance.positions)
        instance.description = validated_data.get('description', instance.description)
        instance.products = validated_data.get('products', instance.products)
        instance.product_description = validated_data.get('product_description', instance.product_description)
        instance.website = validated_data.get('website', instance.website)
        instance.address = validated_data.get('address', instance.address)
        instance.email = validated_data.get('email', instance.email)
        instance.phone_number = validated_data.get('phone_number', instance.phone_number)

        # 保存修改
        instance.save()
        return instance

class SimpleCompanySerializer(serializers.ModelSerializer):
    member_name = serializers.SerializerMethodField()

    class Meta:
        model = Company
        fields = [
            'id', 'name', 'member_name','photo','member'
        ]

    def get_member_name(self,obj):
        return obj.member.name