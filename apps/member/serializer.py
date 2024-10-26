from rest_framework import serializers
from apps.member.models import Member, Position, Graduate
from apps.notice.models import Notice
from apps.private.models import Private
from django.db import transaction
from django.contrib.auth.hashers import make_password
from apps.deal_base64 import Base64ImageField
# 序列化
from apps.picture.serializer import SelfImageSerializer , CompanyImageSerializer
from apps.company.serializer import CompanySearchSerializer

from django.core.files.base import ContentFile
import base64
import uuid

# 會員序列化
class PositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Position
        fields = '__all__'


class GraduateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Graduate
        fields = '__all__'


class MemberSerializer(serializers.ModelSerializer):
    """
    系友會會員的序列化器
    將 Member 模型轉換為 JSON 格式，並進行驗證和反序列化。
    """
    email = serializers.SerializerMethodField()
    notice_type = serializers.SerializerMethodField()
    position = PositionSerializer()  # 嵌套序列化器，支援查詢和寫入
    graduate = GraduateSerializer()  # 同樣使用嵌套序列化器
    photo = Base64ImageField()

    class Meta:
        model = Member
        fields = '__all__'

    def get_email(self, instance):
        private = getattr(instance, 'private', None)
        return private.email if private else None

    def get_notice_type(self, instance):
        notice = getattr(instance, 'notice', None)
        if notice:
            return {
                "email": notice.email_notifications,
                "news": notice.news_notifications,
                "promo": notice.promo_notifications,
            }
        return None

    def check_and_set_superuser(self, member_instance, position_instance):
        """
        檢查 position 條件並設置/取消 superuser 權限
        """
        if position_instance.title == "管理員" or (position_instance.priority and position_instance.priority < 3):
            member_instance.private.is_superuser = True
        else:
            member_instance.private.is_superuser = False
        member_instance.private.save()  # 保存更改到 private 模型

    def create(self, validated_data):
        position_data = validated_data.pop('position', None)
        graduate_data = validated_data.pop('graduate', None)

        try:
            with transaction.atomic():
                # 創建 Private 和 Graduate 實例
                private_instance = Private.objects.create(
                    email=validated_data['email'],
                    password=make_password(validated_data['password']),
                    is_active=False
                )

                graduate_instance = Graduate.objects.create(**graduate_data) if graduate_data else None
                position_instance = Position.objects.create(**position_data) if position_data else None

                # 處理 base64 照片
                photo_data = validated_data.get('photo')
                if photo_data:
                    format, imgstr = photo_data.split(';base64,')  # 提取圖片格式和 base64 資料
                    ext = format.split('/')[-1]  # 獲取圖片的擴展名
                    photo = ContentFile(base64.b64decode(imgstr), name=f'{uuid.uuid4()}.{ext}')  # 解碼並創建 ContentFile
                else:
                    photo = None

                # 創建 Member 實例
                member_instance = Member.objects.create(
                    private=private_instance,
                    graduate=graduate_instance,
                    position=position_instance,
                    photo=photo,
                    **validated_data
                )
                # 設置 superuser 權限
                self.check_and_set_superuser(member_instance, position_instance)

                # 創建 Notice
                Notice.objects.create(
                    member=member_instance,
                    email_notifications=True,
                    sms_notifications=False,
                    news_notifications=True,
                    promo_notifications=True
                )

                return member_instance

        except Exception as e:
            raise serializers.ValidationError(f"An error occurred during creation: {str(e)}")

    def update(self, instance, validated_data):
        # 移除根層的 school 和 grade，避免衝突
        validated_data.pop('school', None)
        validated_data.pop('grade', None)

        # 處理 position 更新或創建
        position_data = validated_data.pop('position', None)
        if position_data:
            position_id = position_data.get('id')
            if position_id:
                # 獲取特定的 Position 實例並逐一更新字段
                position_instance = Position.objects.get(id=position_id)
                for attr, value in position_data.items():
                    setattr(position_instance, attr, value)
                position_instance.save()
                instance.position = position_instance
            else:
                # 創建新的 Position 實例並關聯
                position_instance = Position.objects.create(**position_data)
                instance.position = position_instance
        else:
            position_instance = instance.position  # 若未傳入 position，使用當前 position

        # 處理 graduate 更新或創建，避免批量影響
        graduate_data = validated_data.pop('graduate', None)
        if graduate_data:
            if instance.graduate:
                # 檢查是否需要更新或創建新 graduate
                if instance.graduate.school != graduate_data.get("school") or instance.graduate.grade != graduate_data.get("grade"):
                    # 如果現有 graduate 被多個成員共享，則創建新的實例
                    graduate_instance = Graduate.objects.create(**graduate_data)
                    instance.graduate = graduate_instance
                else:
                    # 更新當前成員的 Graduate 屬性
                    for attr, value in graduate_data.items():
                        setattr(instance.graduate, attr, value)
                    instance.graduate.save()
            else:
                # 如果沒有關聯的 graduate，則創建新的 Graduate 並關聯
                graduate_instance = Graduate.objects.create(**graduate_data)
                instance.graduate = graduate_instance

        # 更新其他非嵌套字段
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()  # 保存所有變更

        # 更新 superuser 權限
        self.check_and_set_superuser(instance, position_instance)

        return instance  # 返回更新後的實例

class MemberSimpleSerializer(serializers.ModelSerializer):
    """
    系友會資訊＿一般官網預覽使用
    """
    position = serializers.SerializerMethodField()
    graduate = serializers.SerializerMethodField()

    class Meta:
        model = Member
        fields = ['id','name','gender','intro','photo','position','graduate']

    def get_position(self, instance):
            position = getattr(instance, 'position', None)
            if position:
                return {
                    "title": position.title,
                }
            return None

    def get_graduate(self, instance):
            graduate = getattr(instance, 'graduate', None)
            if graduate:
                return {
                    "school": graduate.school,
                    "grade": graduate.grade
                }
            return None

class MemberSimpleAdminSerializer(serializers.ModelSerializer):
    """
    給予管理端的預覽輸出
    """
    position = serializers.SerializerMethodField()
    graduate = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    isActive = serializers.SerializerMethodField()

    class Meta:
        model = Member
        fields = ['id','name','gender','photo','position','graduate','email','is_paid','isActive']

    def get_email(self,obj):
        return obj.private.email
    def get_isActive(self,obj):
        return obj.private.is_active

    def get_position(self, instance):
            position = getattr(instance, 'position', None)
            if position:
                return {
                    "title": position.title,
                }
            return None

    def get_graduate(self, instance):
            graduate = getattr(instance, 'graduate', None)
            if graduate:
                return {
                    "school": graduate.school,
                    "grade": graduate.grade
                }
            return None

class MemberSimpleDetailSerializer(serializers.ModelSerializer):
    """
    一般官網可看到的詳細頁面
    """
    position = serializers.SerializerMethodField()
    graduate = serializers.SerializerMethodField()
    self_images = SelfImageSerializer(source='selfimage_set',many=True)  # 假設一個會員可以有多個 SelfImage
    company = CompanySearchSerializer(source='member')  # 假設一個會員只關聯一家公司
    company_images = CompanyImageSerializer(source='member.companyimage_set', many=True)

    class Meta:
        model = Member
        fields = ['name','gender','intro','photo','position','graduate','company','company_images','self_images']

    def get_position(self, instance):
            position = getattr(instance, 'position', None)
            if position:
                return {
                    "title": position.title,
                }
            return None

    def get_graduate(self, instance):
            graduate = getattr(instance, 'graduate', None)
            if graduate:
                return {
                    "school": graduate.school,
                    "grade": graduate.grade
                }
            return None
