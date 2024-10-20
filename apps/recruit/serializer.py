from rest_framework import serializers
from apps.recruit.models import Recruit,Contact,RecruitImage
from apps.deal_base64 import Base64ImageField

class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ['name', 'phone', 'email']

# RecruitImageSerializer for handling images
class RecruitImageSerializer(serializers.ModelSerializer):
    image = Base64ImageField()  # 使用 Base64ImageField 來處理 base64 上傳

    class Meta:
        model = RecruitImage
        fields = ['image', 'image_type']

class RecruitSerializer(serializers.ModelSerializer):
    company_name = serializers.SerializerMethodField()
    contact = ContactSerializer()  # 使用嵌套序列化器來處理 Contact
    images = RecruitImageSerializer(many=True, required=False)  # 多張圖片的嵌套序列化器

    class Meta:
        model = Recruit
        fields = ['id', 'company', 'title', 'intro', 'info_clicks', 'deadline', 'release_date', 'active', 'company_name', 'contact', 'images']

    def get_company_name(self, obj):
        return obj.company.name

    def create(self, validated_data):
        contact_data = validated_data.pop('contact')
        images_data = validated_data.pop('images', [])  # 預設為空列表處理圖片
        recruit = Recruit.objects.create(**validated_data)

        if contact_data:
            Contact.objects.create(recruit=recruit, **contact_data)

        # 保存 RecruitImage 信息
        for image_data in images_data:
            RecruitImage.objects.create(recruit=recruit, **image_data)

        return recruit

    def update(self, instance, validated_data):
        contact_data = validated_data.pop('contact',None)
        images_data = validated_data.pop('images', [])  # 預設為空列表處理圖片
        contact = instance.contact

        # 更新 Recruit 的字段
        instance.company = validated_data.get('company', instance.company)
        instance.title = validated_data.get('title', instance.title)
        instance.intro = validated_data.get('intro', instance.intro)
        instance.info_clicks = validated_data.get('info_clicks', instance.click)
        instance.deadline = validated_data.get('deadline', instance.deadline)
        instance.release_date = validated_data.get('release_date', instance.release_date)
        instance.active = validated_data.get('active', instance.active)
        instance.save()

        if contact_data:
            contact.name = contact_data.get('name', contact.name)
            contact.phone = contact_data.get('phone', contact.phone)
            contact.email = contact_data.get('email', contact.email)
            contact.save()

        # 更新 RecruitImage 信息
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
