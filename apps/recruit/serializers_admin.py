from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from apps.recruit.models import Recruit, Contact, RecruitImage
from apps.company.models import Company
# from django.contrib.auth.models import User
from apps.deal_base64 import Base64ImageField
from apps.private.models import Private

class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ['name', 'phone', 'email', 'company_name']

class RecruitImageSerializer(serializers.ModelSerializer):
    image = Base64ImageField()
    
    class Meta:
        model = RecruitImage
        fields = ['image', 'image_type']

class RecruitSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()
    user_id = serializers.SerializerMethodField()
    company_name = serializers.CharField(required=False, write_only=True)  # 允許寫入但不會出現在輸出中
    _company_name = serializers.SerializerMethodField(required=False)  # 用於輸出顯示
    contact = ContactSerializer(required=False)  # 聯絡人為選填
    images = RecruitImageSerializer(many=True, required=False)  # 多張圖片為選填
    isPersonalContact = serializers.BooleanField(required=False, default=False)
    isPersonalCompany = serializers.BooleanField(required=False, default=False)

    class Meta:
        model = Recruit
        fields = [
            'id', 'company', 'title', 'intro', 'info_clicks', 'deadline',
            'release_date', 'active', '_company_name', 'company_name', 'contact', 'images',
            'isPersonalContact', 'isPersonalCompany', 'user_name', 'user_id'
        ]
        read_only_fields = ['id']  # 確保在任何操作中ID是只讀的
        extra_kwargs = {
            'id': {'required': False}  # 明確指定ID不是必需的
        }
    
    def get_user_name(self, obj):
        return obj.company.member.name if obj.company and hasattr(obj.company, 'member') else None

    def get_user_id(self, obj):
        return obj.company.member.private.id if obj.company and hasattr(obj.company, 'member') and hasattr(obj.company.member, 'private') else None
    
    def get__company_name(self, obj):
        return obj.contact.company_name if obj.contact else None

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

    def to_internal_value(self, data):
        """
        重寫此方法以處理前端發送的 company_name
        這將允許前端發送 company_name 作為可寫欄位，即使實際上它是一個只讀欄位
        """
        # 保存 company_name 值以便後續使用
        company_name_value = data.get('company_name', None)
        
        # 首先讓標準驗證流程運行
        ret = super().to_internal_value(data)
        
        # 如果前端提供了 company_name，保存在一個臨時屬性中
        if company_name_value is not None:
            ret['_company_name_to_update'] = company_name_value
            
        return ret

    def create(self, validated_data):
        # 提取並移除臨時的 company_name 值
        validated_data.pop('_company_name_to_update', None)
            
        # 確保在創建時排除ID字段
        if 'id' in validated_data:
            validated_data.pop('id')  # 明確移除任何可能的ID值
            
        user = self.context['request'].user
        # company = self.validate_user_and_company(user)
        
        contact_data = validated_data.pop('contact', None)
        images_data = validated_data.pop('images', [])
        is_contact_self = validated_data.pop('isPersonalContact', False)
        is_owner_self = validated_data.pop('isPersonalCompany', False)

        try:
            # 處理聯絡人資料
            contact_data = self.handle_contact_data(user, is_contact_self, contact_data)

            # 取出 company_name 並設置到 contact_data
            company_name = validated_data.pop('company_name')
            contact_data['company_name'] = company_name
            
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
        
        # 處理直接提供的 company_name
        company_name = validated_data.pop('company_name', None)
        print(f"直接提供的 company_name: {company_name}")  # 調試輸出
        
        # 處理 contact 資料
        contact_data = validated_data.pop('contact', None) or {}
        print(f"聯絡人資料: {contact_data}")  # 調試輸出
        
        images_data = validated_data.pop('images', [])
        is_contact_self = validated_data.pop('isPersonalContact', False)
        is_owner_self = validated_data.pop('isPersonalCompany', False)

        try:
            # 更新 Recruit 的字段
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()

            # 獲取或創建聯絡人
            contact, created = Contact.objects.get_or_create(recruit=instance)
            
            # 如果直接提供了 company_name，優先使用它
            if company_name is not None:
                contact.company_name = company_name
                print(f"正在設置 company_name 為: {company_name}")  # 調試輸出
            # 否則使用 contact_data 中的 company_name
            elif 'company_name' in contact_data:
                contact.company_name = contact_data['company_name']
                print(f"從 contact_data 設置 company_name 為: {contact_data['company_name']}")  # 調試輸出
                
            # 更新其他聯絡人資料
            for attr, value in contact_data.items():
                if attr != 'company_name':  # company_name 已經處理過了
                    setattr(contact, attr, value)
            
            # 確保保存聯絡人資料
            contact.save()
            print(f"保存後的 company_name: {contact.company_name}")  # 調試輸出

            # 更新圖片資料
            if images_data:
                self.handle_images(images_data, instance)

            return instance
        except ValidationError as ve:
            raise ve
        except Exception as e:
            print(f"發生錯誤: {str(e)}")  # 調試輸出
            raise ValidationError({"error": f"發生未預期的錯誤: {str(e)}"})


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ['id', 'name']

class UserListSerializer(serializers.ListSerializer):
    def to_representation(self, data):
        iterable = data.all() if hasattr(data, 'all') else data
        result = []
        for item in iterable:
            representation = self.child.to_representation(item)
            if representation and representation['name'] is not None:
                result.append(representation)
        return result

class UserSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    
    class Meta:
        model = Private
        fields = ['id', 'name']
        list_serializer_class = UserListSerializer
    
    def get_name(self, obj):
        return obj.member.name if hasattr(obj, 'member') else None

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if representation['name'] is None:
            return None
        return representation