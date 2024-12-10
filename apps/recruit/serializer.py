from rest_framework import serializers
from apps.recruit.models import Recruit, Contact, RecruitImage
from apps.deal_base64 import Base64ImageField

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
    company_name = serializers.SerializerMethodField()
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

    def create(self, validated_data):
        # 提取聯絡人及圖片資料
        from apps.company.models import Company
        contact_data = validated_data.pop('contact', None)
        images_data = validated_data.pop('images', [])
        is_contact_self = validated_data.pop('isPersonalContact', False)
        is_owner_self = validated_data.pop('isPersonalCompany', False)
        
        # 設置聯絡人及公司資料
        user = self.context['request'].user  # 從 context 中獲取使用者
        company_ob = Company.objects.get(member = user.member)

        if is_contact_self:
            contact_data = {
                'name': user.member.name,
                'phone': user.member.mobile_phone,
                'email': user.email,
            }
            print(contact_data)
        
        if is_owner_self:
            contact_data['company_name'] = company_ob.name

        elif 'company_name' not in validated_data:
            raise serializers.ValidationError({"company_name": ["請輸入公司名稱!"]})

        validated_data['company'] = company_ob
        # 建立 Recruit
        recruit = Recruit.objects.create(**validated_data)

        # 保存聯絡人資料
        if contact_data:
            Contact.objects.create(recruit=recruit, **contact_data)

        # 保存 RecruitImage 資訊
        for image_data in images_data:
            RecruitImage.objects.create(recruit=recruit, **image_data)

        return recruit

    def update(self, instance, validated_data):
        # 提取聯絡人及圖片資料
        contact_data = validated_data.pop('contact', None)
        images_data = validated_data.pop('images', [])
        is_contact_self = validated_data.pop('isPersonalContact', False)
        is_owner_self = validated_data.pop('isPersonalCompany', False)

        # 設置聯絡人為本人和公司為本人公司邏輯
        user = self.context['request'].user  # 從 context 中獲取使用者
        if is_contact_self:
            contact_data = {
                'name': user.member.name,
                'phone': user.member.mobile_phone,
                'email': user.email,
            }
        if is_owner_self:
            contact_data['company_name'] = user.member.company.name

        validated_data['company'] = user.member.company

        # 更新 Recruit 的字段
        instance.company = validated_data.get('company', instance.company)
        instance.title = validated_data.get('title', instance.title)
        instance.intro = validated_data.get('intro', instance.intro)
        instance.info_clicks = validated_data.get('info_clicks', instance.info_clicks)
        instance.deadline = validated_data.get('deadline', instance.deadline)
        instance.release_date = validated_data.get('release_date', instance.release_date)
        instance.active = validated_data.get('active', instance.active)
        instance.save()

        # 更新聯絡人資料
        if contact_data:
            contact, created = Contact.objects.get_or_create(recruit=instance)
            contact.name = contact_data.get('name', contact.name)
            contact.phone = contact_data.get('phone', contact.phone)
            contact.email = contact_data.get('email', contact.email)
            contact.company_name = contact_data.get('company_name', contact.company_name)
            contact.save()

        # 清除並重新建立 RecruitImage 信息
        instance.images.all().delete()  # 清除舊的圖片
        for image_data in images_data:
            RecruitImage.objects.create(recruit=instance, **image_data)

        return instance

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
