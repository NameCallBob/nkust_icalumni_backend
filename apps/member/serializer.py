from rest_framework import serializers
from apps.member.models import Member, Position, Graduate , OutstandingAlumni
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
from asgiref.sync import sync_to_async

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
    position = PositionSerializer(required=False)
    graduate = GraduateSerializer(required=False)
    photo = Base64ImageField(required=False)

    # 用於序列化輸出的 private 資料
    private = serializers.SerializerMethodField()
    # 用於接收反序列化資料（支援 id 或嵌套資料）
    private_input = serializers.DictField(write_only=True, required=False)

    class Meta:
        model = Member
        fields = '__all__'

    def get_email(self, instance):
        private = getattr(instance, 'private', None)
        return private.email if private else None

    def get_private(self, obj):
        """
        序列化時返回 private 資料
        """
        if obj.private:
            return {
                "email": obj.private.email
            }
        return None

    def to_internal_value(self, data):
        """
        重寫以支援嵌套處理 `private_input` 資料
        """
        private_data = data.pop('private_input', None)
        if private_data:
            if isinstance(private_data, dict):
                # 檢查嵌套資料的完整性
                email = private_data.get('email')
                password = private_data.get('password')
                if not email:
                    raise serializers.ValidationError({
                        "private_input": "沒有提供電子郵件作為帳號，無法建立"
                    })
            elif isinstance(private_data, int):
                # 如果是主鍵，檢查是否存在
                if not Private.objects.filter(pk=private_data).exists():
                    raise serializers.ValidationError({
                        "private_input": "無此會員"
                    })

            # 將處理後的 private 資料放回 data
            data['private_input'] = private_data

        return super().to_internal_value(data)

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
        if position_instance and (position_instance.title == "管理員" or (position_instance.priority and position_instance.priority <= 3)):
            member_instance.private.is_superuser = True
        else:
            member_instance.private.is_superuser = False
        member_instance.private.save()  # 保存更改到 private 模型

    def create(self, validated_data):
        position_data = validated_data.pop('position', None)
        graduate_data = validated_data.pop('graduate', None)
        private_data = validated_data.pop('private_input', None)  # 處理 private_input 資料

        private_instance = None  # 初始化 private_instance
        try:
            # 驗證 Private 輸入資料
            if not private_data or not isinstance(private_data, (dict, int)):
                raise serializers.ValidationError({"private_input": "缺少帳號密碼的資料，請確認是否填寫"})

            graduate_instance = Graduate.objects.create(**graduate_data) if graduate_data else None
            position_instance = None
            if position_data:
                position_title = position_data.get('title')
                if position_title:
                    position_instance = Position.objects.filter(title=position_title).first()
                if not position_instance:
                    position_instance = Position.objects.create(**position_data)

            photo = None
            photo_data = validated_data.get('photo')
            if photo_data and isinstance(photo_data, str):
                try:
                    format, imgstr = photo_data.split(';base64,')
                    ext = format.split('/')[-1]
                    photo = ContentFile(base64.b64decode(imgstr), name=f'{uuid.uuid4()}.{ext}')
                except Exception as e:
                    raise serializers.ValidationError({"photo": f"照片非可轉為base64的格式: {str(e)}"})

            with transaction.atomic():
                if isinstance(private_data, dict):
                    private_instance = Private.objects.create_user(
                        email=private_data['email'],
                        password=private_data['password'],
                    )
                elif isinstance(private_data, int):
                    private_instance = Private.objects.get(pk=private_data)

                member_instance = Member.objects.create(
                    private=private_instance,
                    graduate=graduate_instance,
                    position=position_instance,
                    photo=photo,
                    **validated_data
                )

                self.check_and_set_superuser(member_instance, position_instance)

                Notice.objects.create(
                    member=member_instance,
                    email_notifications=True,
                    sms_notifications=False,
                    news_notifications=True,
                    promo_notifications=True
                )

                return member_instance

        except serializers.ValidationError as e:
            raise e
        except Exception as e:
            raise serializers.ValidationError({"detail": f"An unexpected error occurred during creation: {str(e)}"})

    def update(self, instance, validated_data):
        validated_data.pop('school', None)
        validated_data.pop('grade', None)

        position_instance = None
        position_data = validated_data.pop('position', None)
        if position_data:
            position_title = position_data.get('title')
            if position_title:
                position_instance = Position.objects.filter(title=position_title).first()
                if position_instance:
                    for attr, value in position_data.items():
                        setattr(position_instance, attr, value)
                    position_instance.save()
                else:
                    position_instance = Position.objects.create(**position_data)
            else:
                raise serializers.ValidationError({"position": "選擇的職位未知，請重整網頁查看職位是否有被修改"})
            self.check_and_set_superuser(instance, position_instance)
            instance.position = position_instance

        graduate_data = validated_data.pop('graduate', None)
        if graduate_data:
            if instance.graduate:
                for attr, value in graduate_data.items():
                    setattr(instance.graduate, attr, value)
                instance.graduate.save()
            else:
                graduate_instance = Graduate.objects.create(**graduate_data)
                instance.graduate = graduate_instance

        private_data = validated_data.pop('private_input', None)
        if private_data:
            for attr, value in private_data.items():
                setattr(instance.private, attr, value)
                instance.private.save()

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance

class MyListSerializer(serializers.ListSerializer):
    """
    自定義 ListSerializer，過濾掉 null 值
    """
    def to_representation(self, data):
        # 調用原生邏輯，過濾掉 None
        return [item for item in super().to_representation(data) if item is not None]
        

class MemberSimpleSerializer(serializers.ModelSerializer):
    """
    系友會資訊＿一般官網預覽使用
    """
    position = serializers.SerializerMethodField()
    graduate = serializers.SerializerMethodField()

    class Meta:
        model = Member
        fields = ['id','name','gender','intro','photo','position','graduate']
        list_serializer_class = MyListSerializer
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
    def to_representation(self, instance):
        """
        自定義輸出邏輯，當 is_show 為 False 時，過濾該物件
        """
        if not instance.is_show:
            return None  # 如果 is_show 為 False，直接返回 None，表示不輸出該資料

        # 調用原始的序列化過程
        representation = super().to_representation(instance)
        return representation

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
    self_images = SelfImageSerializer(source='selfimage_set', many=True)  # 假設一個會員可以有多個 SelfImage
    company = CompanySearchSerializer(source='member')  # 假設一個會員只關聯一家公司
    company_images = CompanyImageSerializer(source='member.companyimage_set', many=True)

    class Meta:
        model = Member
        fields = ['name', 'gender', 'intro', 'photo', 'position', 'graduate', 'company', 'company_images', 'self_images']

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

    def to_representation(self, instance):
        """
        自定義輸出邏輯，當 is_show 為 False 時，過濾該物件
        """
        if not instance.is_show:
            return None  # 如果 is_show 為 False，直接返回 None，表示不輸出該資料

        # 調用原始的序列化過程
        representation = super().to_representation(instance)
        return representation

class OutstandingAlumniSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='member.name', read_only=True)
    photo = serializers.ImageField(source='member.photo', read_only=True)
    position = serializers.SerializerMethodField()
    graduate = serializers.SerializerMethodField()

    class Meta:
        model = OutstandingAlumni
        fields = [
            'id', 'member', 'name', 'photo',
            'achievements', 'is_featured', 'highlight', 'date_awarded','position','graduate'
        ]
        read_only_fields = ['id', 'member_name', 'photo']

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

from django.db import transaction, connections


class MemberCreateSerializer(serializers.ModelSerializer):
    notice_type = serializers.SerializerMethodField()
    position = PositionSerializer(required=False)
    graduate = GraduateSerializer(required=False)
    photo = Base64ImageField(required=False)
    private_input = serializers.IntegerField(write_only=True, required=False)

    class Meta:
        model = Member
        exclude = ('private', )

    def create(self, validated_data):
        position_data = validated_data.pop('position', None)
        graduate_data = validated_data.pop('graduate', None)
        private_data = validated_data.pop('private_input', None)

        photo = None
        if 'photo' in validated_data:
            photo_data = validated_data.pop('photo')

            # 確保 photo_data 是字串，否則直接使用
            if isinstance(photo_data, str):
                try:
                    format, imgstr = photo_data.split(';base64,')
                    ext = format.split('/')[-1]
                    photo = ContentFile(base64.b64decode(imgstr), name=f'{uuid.uuid4()}.{ext}')
                except (ValueError, TypeError, binascii.Error) as e:
                    raise serializers.ValidationError({"photo": f"Invalid photo format: {str(e)}"})
            elif isinstance(photo_data, ContentFile):
                photo = photo_data
            else:
                raise serializers.ValidationError({"photo": "Unsupported photo format."})

        # 使用同步事務處理
        with transaction.atomic():
            private_instance = None
            if isinstance(private_data, dict):
                private_instance = Private.objects.create_user(
                    email=private_data['email'],
                    password=private_data['password']
                )
            elif isinstance(private_data, int):
                try:
                    private_instance = Private.objects.get(pk=private_data)
                except Private.DoesNotExist:
                    raise serializers.ValidationError({"private_input": "Private instance not found."})

            graduate_instance = None
            if graduate_data:
                graduate_instance = Graduate.objects.create(**graduate_data)

            try:
                position_instance = Position.objects.get(title="會員")
            except Position.DoesNotExist:
                raise serializers.ValidationError({"position": "Default position '會員' not found."})

            member_instance = Member.objects.create(
                private=private_instance,
                graduate=graduate_instance,
                position=position_instance,
                photo=photo,
                **validated_data
            )

            Notice.objects.create(
                member=member_instance,
                email_notifications=True,
                sms_notifications=False,
                news_notifications=True,
                promo_notifications=True
            )

        return member_instance

    def get_notice_type(self, instance):
        notice = getattr(instance, 'notice', None)
        if notice:
            return {
                "email": notice.email_notifications,
                "news": notice.news_notifications,
                "promo": notice.promo_notifications,
            }
        return None