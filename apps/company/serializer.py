from rest_framework import serializers
from apps.company.models import Company , Industry
from asgiref.sync import sync_to_async
from django.db import transaction

class IndustrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Industry
        fields = ['id', 'title', 'intro']  # 包含所有需要的欄位


class CompanySearchSerializer(serializers.ModelSerializer):
    industry = IndustrySerializer()
    member_name = serializers.SerializerMethodField()
    graduate_grade = serializers.SerializerMethodField()

    class Meta:
        model = Company
        fields = [
            'id', 'member', 'name', 'industry', 'positions', 'products',
            'product_description', 'photo', 'address', 'email',
            'phone_number', 'graduate_grade', 'member_name', 'website'
        ]

    def get_member_name(self, instance):
        return instance.member.name

    def get_graduate_grade(self, instance):
        graduate = instance.member.graduate
        return graduate.grade if graduate else None


import base64
from django.core.files.base import ContentFile

class CompanySerializer(serializers.ModelSerializer):
    industry = serializers.CharField(source='industry.title')  # 只序列化 industry 的 title
    member_name = serializers.SerializerMethodField()
    photo = serializers.CharField(write_only=True)  # Base64 的圖片資料
    photo_url= serializers.ImageField(source="photo",read_only=True)  # Base64 的圖片資料

    class Meta:
        model = Company
        fields = [
            'id', 'name', 'member', 'industry', 'positions', 'description', 'products',
            'product_description', 'photo', 'website', 'address', 'email',
            'clicks', 'phone_number', 'created_at', 'member_name'
        ]

    def get_member_name(self, instance):
        return instance.member.name

    def create(self, validated_data):
        industry = validated_data.pop('industry', None)
        photo_data = validated_data.pop('photo', None)

        photo = None
        if photo_data:
            format, imgstr = photo_data.split(';base64,')
            ext = format.split('/')[-1]
            photo = ContentFile(base64.b64decode(imgstr), name=f"company_photo.{ext}")

        with transaction.atomic():
            industry_instance = Industry.objects.get(title=industry['title'])
            company = Company.objects.create(
                industry=industry_instance, photo=photo, **validated_data
            )
        return company

    def update(self, instance, validated_data):
        industry = validated_data.get('industry', None)
        if industry:
            instance.industry = Industry.objects.get(title=industry['title'])

        photo_data = validated_data.get('photo', None)
        if photo_data:
            format, imgstr = photo_data.split(';base64,')
            ext = format.split('/')[-1]
            instance.photo = ContentFile(base64.b64decode(imgstr), name=f"company_photo.{ext}")

        instance.name = validated_data.get('name', instance.name)
        instance.positions = validated_data.get('positions', instance.positions)
        instance.description = validated_data.get('description', instance.description)
        instance.products = validated_data.get('products', instance.products)
        instance.product_description = validated_data.get('product_description', instance.product_description)
        instance.website = validated_data.get('website', instance.website)
        instance.address = validated_data.get('address', instance.address)
        instance.email = validated_data.get('email', instance.email)
        instance.phone_number = validated_data.get('phone_number', instance.phone_number)

        instance.save()
        return instance

class SimpleCompanySerializer(serializers.ModelSerializer):
    member_name = serializers.SerializerMethodField()
    graduate_grade = serializers.SerializerMethodField()

    class Meta:
        model = Company
        fields = [
            'id', 'name', 'member_name', 'photo', 'member', 'products', 'graduate_grade'
        ]

    def get_member_name(self, obj):
        return obj.member.name

    def get_graduate_grade(self, obj):
        graduate = obj.member.graduate
        return graduate.grade if graduate else None