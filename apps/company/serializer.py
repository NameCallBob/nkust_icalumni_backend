from rest_framework import serializers
from apps.company.models import Company , Industry
from asgiref.sync import sync_to_async
from django.db import transaction
from django.core.cache import cache


class IndustrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Industry
        fields = ['id', 'title', 'intro']  # 包含所有需要的欄位


class CompanySearchSerializer(serializers.ModelSerializer):
    industry = IndustrySerializer()
    member_name = serializers.SerializerMethodField()
    graduate_grade = serializers.SerializerMethodField()
    # 新增欄位，不會影響現有前端
    member_position = serializers.SerializerMethodField()
    industry_companies_count = serializers.SerializerMethodField()
    created_at_formatted = serializers.SerializerMethodField()
    
    class Meta:
        model = Company
        fields = [
            'id', 'member', 'name', 'industry', 'positions', 'products',
            'product_description', 'photo', 'address', 'email',
            'phone_number', 'graduate_grade', 'member_name', 'website',
            # 新增欄位，不會影響現有前端
            'member_position', 'industry_companies_count', 'created_at_formatted'
        ]

    def get_member_name(self, instance):
        return instance.member.name

    def get_graduate_grade(self, instance):
        graduate = instance.member.graduate
        return graduate.grade if graduate else None
        
    # 新增方法，不會影響現有前端
    def get_member_position(self, instance):
        if hasattr(instance.member, 'position') and instance.member.position:
            return {
                'title': instance.member.position.title,
                'department': getattr(instance.member.position, 'department', None)
            }
        return None
        
    def get_industry_companies_count(self, instance):
        if instance.industry:
            cache_key = f"industry_count:{instance.industry.id}"
            count = cache.get(cache_key)
            
            if count is None:
                count = Company.objects.filter(industry=instance.industry).count()
                cache.set(cache_key, count, 3600)  # 緩存一小時
                
            return count
        return 0
        
    def get_created_at_formatted(self, instance):
        if instance.created_at:
            return instance.created_at.strftime("%Y-%m-%d")
        return None


import base64
from django.core.files.base import ContentFile

class CompanySerializer(serializers.ModelSerializer):
    industry = serializers.CharField(source='industry.title', required=False, allow_null=True, allow_blank=True)
    member_name = serializers.SerializerMethodField(read_only=True)
    photo = serializers.CharField(write_only=True, required=False, allow_null=True, allow_blank=True)
    photo_url = serializers.ImageField(source="photo", read_only=True)

    class Meta:
        model = Company
        fields = [
            'id', 'name', 'member', 'industry', 'positions', 'description', 'products', 'photo_url',
            'product_description', 'photo', 'website', 'address', 'email',
            'clicks', 'phone_number', 'created_at', 'member_name'
        ]
        # [資安修補 MED-1 / IDOR] clicks、created_at 不可由前端寫入；
        # member 亦設為唯讀，避免使用者於 selfChange 將自己的公司改綁到他人 member。
        # 建立公司時由 view 以 serializer.save(member=...) 於伺服器端綁定。
        read_only_fields = ('clicks', 'created_at', 'member')
        extra_kwargs = {
            'name': {'required': False, 'allow_null': True, 'allow_blank': True},
            'member': {'required': False, 'allow_null': True},
            'positions': {'required': False, 'allow_null': True, 'allow_blank': True},
            'description': {'required': False, 'allow_null': True, 'allow_blank': True},
            'products': {'required': False, 'allow_null': True, 'allow_blank': True},
            'product_description': {'required': False, 'allow_null': True, 'allow_blank': True},
            'website': {'required': False, 'allow_null': True, 'allow_blank': True},
            'address': {'required': False, 'allow_null': True, 'allow_blank': True},
            'email': {'required': False, 'allow_null': True, 'allow_blank': True},
            'phone_number': {'required': False, 'allow_null': True, 'allow_blank': True},
        }

    def get_member_name(self, instance):
        if instance.member:
            return instance.member.name
        return None

    def create(self, validated_data):
        industry_data = validated_data.pop('industry', None)
        photo_data = validated_data.pop('photo', None)

        photo = None
        if photo_data:
            try:
                format, imgstr = photo_data.split(';base64,')
                ext = format.split('/')[-1]
                photo = ContentFile(base64.b64decode(imgstr), name=f"company_photo.{ext}")
            except (ValueError, AttributeError):
                # 如果圖片資料格式不正確，不處理圖片
                pass

        with transaction.atomic():
            industry_instance = None
            if industry_data and 'title' in industry_data and industry_data['title']:
                try:
                    industry_instance = Industry.objects.get(title=industry_data['title'])
                except Industry.DoesNotExist:
                    # 如果找不到對應的產業，使用默認值
                    industry_instance = Industry.objects.get(id=1)
            else:
                # 如果沒有提供產業資訊，使用默認值
                industry_instance = Industry.objects.get(id=1)

            company = Company.objects.create(
                industry=industry_instance, 
                photo=photo, 
                **validated_data
            )
        
        return company

    def update(self, instance, validated_data):
        industry_data = validated_data.pop('industry', None)
        if industry_data and 'title' in industry_data and industry_data['title']:
            try:
                instance.industry = Industry.objects.get(title=industry_data['title'])
            except Industry.DoesNotExist:
                # 如果找不到對應的產業，不更新產業欄位
                pass

        photo_data = validated_data.pop('photo', None)
        if photo_data:
            try:
                format, imgstr = photo_data.split(';base64,')
                ext = format.split('/')[-1]
                instance.photo = ContentFile(base64.b64decode(imgstr), name=f"company_photo.{ext}")
            except (ValueError, AttributeError):
                # 如果圖片資料格式不正確，不更新圖片
                pass

        # 更新其他欄位，只有當值存在時才更新
        for field, value in validated_data.items():
            setattr(instance, field, value)

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
