from rest_framework import serializers
from apps.recruit.models import Recruit, Contact, RecruitImage
from apps.company.models import Company
from apps.deal_base64 import Base64ImageField
from rest_framework.exceptions import ValidationError

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
    contact = ContactSerializer(required=False)  # 聯絡人為選填
    images = RecruitImageSerializer(many=True, required=False)  # 多張圖片為選填
    isPersonalContact = serializers.BooleanField(required=False, default=False)
    isPersonalCompany = serializers.BooleanField(required=False, default=False)

    class Meta:
        model = Recruit
        fields = [
            'id', 'company', 'title', 'intro', 'info_clicks', 'deadline',
            'release_date', 'active', 'company_name', 'contact', 'images',
            'isPersonalContact', 'isPersonalCompany'
        ]

    def get_company_name(self, obj):
        return obj.company.name if obj.company else None

    def validate_user_and_company(self, user):
        """驗證使用者及公司資料"""
        if not hasattr(user, 'member'):
            raise ValidationError({"user": "使用者沒有關聯的會員資料 (member)！"})
        company = Company.objects.filter(member=user.member).first()
        if not company:
            raise ValidationError({"company": "使用者沒有關聯的公司資料！"})
        return company

    def handle_contact_data(self, user, is_contact_self, contact_data):
        """處理聯絡人資料"""
        if is_contact_self:
            return {
                'name': user.member.name,
                'phone': user.member.mobile_phone,
                'email': user.email,
            }
        return contact_data

    def handle_images(self, images_data, recruit):
        """處理圖片資料"""
        if images_data:
            recruit.images.all().delete()  # 清除舊的圖片
            for image_data in images_data:
                RecruitImage.objects.create(recruit=recruit, **image_data)

    def create(self, validated_data):
        user = self.context['request'].user
        company = self.validate_user_and_company(user)

        contact_data = validated_data.pop('contact', None)
        images_data = validated_data.pop('images', [])
        is_contact_self = validated_data.pop('isPersonalContact', False)
        is_owner_self = validated_data.pop('isPersonalCompany', False)

        try:
            # 處理聯絡人資料
            contact_data = self.handle_contact_data(user, is_contact_self, contact_data)

            if is_owner_self and contact_data is not None:
                contact_data['company_name'] = company.name

            validated_data['company'] = company
            recruit = Recruit.objects.create(**validated_data)

            # 保存聯絡人資料
            if contact_data:
                Contact.objects.create(recruit=recruit, **contact_data)

            # 保存圖片資料
            self.handle_images(images_data, recruit)

            return recruit
        except ValidationError as ve:
            raise ve
        except Exception as e:
            raise ValidationError({"error": f"發生未預期的錯誤: {str(e)}"})

    def update(self, instance, validated_data):
        user = self.context['request'].user
        company = self.validate_user_and_company(user)

        contact_data = validated_data.pop('contact', None)
        images_data = validated_data.pop('images', [])
        is_contact_self = validated_data.pop('isPersonalContact', False)
        is_owner_self = validated_data.pop('isPersonalCompany', False)

        try:
            # 處理聯絡人資料
            contact_data = self.handle_contact_data(user, is_contact_self, contact_data)

            if is_owner_self and contact_data is not None:
                contact_data['company_name'] = company.name

            validated_data['company'] = company

            # 更新 Recruit 的字段
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()

            # 更新聯絡人資料
            if contact_data:
                contact, created = Contact.objects.get_or_create(recruit=instance)
                for attr, value in contact_data.items():
                    setattr(contact, attr, value)
                contact.save()

            # 更新圖片資料
            self.handle_images(images_data, instance)

            return instance
        except ValidationError as ve:
            raise ve
        except Exception as e:
            raise ValidationError({"error": f"發生未預期的錯誤: {str(e)}"})
        
class RecruitSerializer_forTable(serializers.ModelSerializer):
    company_name = serializers.SerializerMethodField()

    class Meta:
        model = Recruit
        fields = ['id', 'company', 'title','release_date', 'deadline','company_name']

    def get_company_name(self , obj):
        return obj.company.name

class RecruitAdminSerializer_forTable(serializers.ModelSerializer):

    class Meta:
        model = Recruit
        fields = ['id', 'title','release_date', 'deadline',]
