from rest_framework import serializers
from apps.recruit.models import Recruit, Contact, RecruitImage
from apps.company.models import Company
from apps.deal_base64 import Base64ImageField
from rest_framework.exceptions import ValidationError
from asgiref.sync import sync_to_async
from django.db import transaction

class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ['name', 'phone', 'email']

# RecruitImageSerializer using Base64ImageField
class RecruitImageSerializer(serializers.ModelSerializer):
    image = Base64ImageField()  # 使用 Base64ImageField 來處理 base64 上傳

    class Meta:
        model = RecruitImage
        fields = ['image', 'image_type']

class RecruitSerializer(serializers.ModelSerializer):
    company_name = serializers.SerializerMethodField(required=False)
    contact = ContactSerializer(required=False)
    images = RecruitImageSerializer(many=True, required=False)
    isPersonalContact = serializers.BooleanField(required=False, default=False)
    isPersonalCompany = serializers.BooleanField(required=False, default=False)

    class Meta:
        model = Recruit
        fields = [
            'id', 'company', 'title', 'intro', 'info_clicks', 'deadline',
            'release_date', 'active', 'company_name', 'contact', 'images',
            'isPersonalContact', 'isPersonalCompany'
        ]

    async def get_company_name(self, obj):
        return obj.company.name if obj.company else None

    async def validate_user_and_company(self, user):
        """非同步驗證使用者及公司資料"""
        if not hasattr(user, 'member'):
            raise ValidationError({"user": "使用者沒有關聯的會員資料 (member)！"})
        company = await Company.objects.filter(member=user.member).afirst()
        if not company:
            raise ValidationError({"company": "使用者沒有關聯的公司資料！"})
        return company

    async def handle_contact_data(self, user, is_contact_self, contact_data):
        """非同步處理聯絡人資料"""
        if is_contact_self:
            return {
                'name': user.member.name,
                'phone': user.member.mobile_phone,
                'email': user.email,
            }
        return contact_data

    async def handle_images(self, images_data, recruit):
        """非同步處理圖片資料"""
        if images_data:
            await sync_to_async(recruit.images.all().delete)()
            for image_data in images_data:
                await RecruitImage.objects.acreate(recruit=recruit, **image_data)

    async def create(self, validated_data):
        user = self.context['request'].user
        company = await self.validate_user_and_company(user)

        contact_data = validated_data.pop('contact', None)
        images_data = validated_data.pop('images', [])
        is_contact_self = validated_data.pop('isPersonalContact', False)
        is_owner_self = validated_data.pop('isPersonalCompany', False)

        try:
            async with transaction.atomic():
                # 處理聯絡人資料
                contact_data = await self.handle_contact_data(user, is_contact_self, contact_data)

                if is_owner_self and contact_data is not None:
                    contact_data['company_name'] = company.name

                validated_data['company'] = company
                recruit = await Recruit.objects.acreate(**validated_data)

                # 保存聯絡人資料
                if contact_data:
                    await Contact.objects.acreate(recruit=recruit, **contact_data)

                # 保存圖片資料
                await self.handle_images(images_data, recruit)

            return recruit
        except ValidationError as ve:
            raise ve
        except Exception as e:
            raise ValidationError({"error": f"發生未預期的錯誤: {str(e)}"})

    async def update(self, instance, validated_data):
        user = self.context['request'].user
        company = await self.validate_user_and_company(user)

        contact_data = validated_data.pop('contact', None)
        images_data = validated_data.pop('images', [])
        is_contact_self = validated_data.pop('isPersonalContact', False)
        is_owner_self = validated_data.pop('isPersonalCompany', False)

        try:
            async with transaction.atomic():
                # 處理聯絡人資料
                contact_data = await self.handle_contact_data(user, is_contact_self, contact_data)

                if is_owner_self and contact_data is not None:
                    contact_data['company_name'] = company.name

                validated_data['company'] = company

                # 更新 Recruit 的字段
                for attr, value in validated_data.items():
                    setattr(instance, attr, value)
                await sync_to_async(instance.save)()

                # 更新聯絡人資料
                if contact_data:
                    contact, created = await Contact.objects.aget_or_create(recruit=instance)
                    for attr, value in contact_data.items():
                        setattr(contact, attr, value)
                    await sync_to_async(contact.save)()

                # 更新圖片資料
                await self.handle_images(images_data, instance)

            return instance
        except ValidationError as ve:
            raise ve
        except Exception as e:
            raise ValidationError({"error": f"發生未預期的錯誤: {str(e)}"})
                
class RecruitSerializer_forTable(serializers.ModelSerializer):
    company_name = serializers.SerializerMethodField()

    class Meta:
        model = Recruit
        fields = ['id', 'company', 'title', 'release_date', 'deadline', 'company_name']

    async def get_company_name(self, obj):
        return obj.company.name if obj.company else None

class RecruitAdminSerializer_forTable(serializers.ModelSerializer):

    class Meta:
        model = Recruit
        fields = ['id', 'title','release_date', 'deadline',]
