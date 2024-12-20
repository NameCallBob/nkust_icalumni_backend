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

# 會員序列化
class PositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Position
        fields = '__all__'


class GraduateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Graduate
        fields = '__all__'


from asgiref.sync import sync_to_async

class MemberSerializer(serializers.ModelSerializer):
    """
    非同步序列化器，用於處理系友會會員的資料
    """
    email = serializers.SerializerMethodField()
    notice_type = serializers.SerializerMethodField()
    position = PositionSerializer(required=False)
    graduate = GraduateSerializer(required=False)
    photo = Base64ImageField(required=False)

    private = serializers.SerializerMethodField()
    private_input = serializers.DictField(write_only=True, required=False)

    class Meta:
        model = Member
        fields = '__all__'

    async def get_email(self, instance):
        private = getattr(instance, 'private', None)
        return private.email if private else None

    async def get_private(self, obj):
        """
        非同步取得 private 資料
        """
        if obj.private:
            return {
                "email": obj.private.email
            }
        return None
    
    async def get_notice_type(self, instance):
            notice = getattr(instance, 'notice', None)
            if notice:
                return {
                    "email": notice.email_notifications,
                    "news": notice.news_notifications,
                    "promo": notice.promo_notifications,
                }
            return None

    async def to_internal_value(self, data):
        """
        非同步處理嵌套資料
        """
        private_data = data.pop('private_input', None)
        if private_data:
            if isinstance(private_data, dict):
                email = private_data.get('email')
                if not email:
                    raise serializers.ValidationError({
                        "private_input": "沒有提供電子郵件作為帳號，無法建立"
                    })
            elif isinstance(private_data, int):
                exists = await Private.objects.filter(pk=private_data).aexists()
                if not exists:
                    raise serializers.ValidationError({
                        "private_input": "無此會員"
                    })

            data['private_input'] = private_data

        return await sync_to_async(super().to_internal_value)(data)

    async def create(self, validated_data):
        """
        非同步創建會員
        """
        position_data = validated_data.pop('position', None)
        graduate_data = validated_data.pop('graduate', None)
        private_data = validated_data.pop('private_input', None)

        photo = None
        photo_data = validated_data.get('photo')
        if photo_data and isinstance(photo_data, str):
            try:
                format, imgstr = photo_data.split(';base64,')
                ext = format.split('/')[-1]
                photo = ContentFile(base64.b64decode(imgstr), name=f'{uuid.uuid4()}.{ext}')
            except Exception as e:
                raise serializers.ValidationError({"photo": f"Invalid photo format: {str(e)}"})

        async with transaction.atomic():
            private_instance = None
            if isinstance(private_data, dict):
                private_instance = await Private.objects.acreate_user(
                    email=private_data['email'],
                    password=private_data['password'],
                )
            elif isinstance(private_data, int):
                private_instance = await Private.objects.aget(pk=private_data)

            graduate_instance = None
            if graduate_data:
                graduate_instance = await Graduate.objects.acreate(**graduate_data)

            position_instance = None
            if position_data:
                position_instance = await Position.objects.acreate(**position_data)

            member_instance = await Member.objects.acreate(
                private=private_instance,
                graduate=graduate_instance,
                position=position_instance,
                photo=photo,
                **validated_data
            )

            await self.check_and_set_superuser(member_instance, position_instance)

            await Notice.objects.acreate(
                member=member_instance,
                email_notifications=True,
                sms_notifications=False,
                news_notifications=True,
                promo_notifications=True
            )

            return member_instance

    async def update(self, instance, validated_data):
        """
        非同步更新會員
        """
        position_data = validated_data.pop('position', None)
        if position_data:
            position_id = position_data.get('id')
            if position_id:
                position_instance = await Position.objects.aget(id=position_id)
                for attr, value in position_data.items():
                    setattr(position_instance, attr, value)
                await sync_to_async(position_instance.save)()
                instance.position = position_instance
            else:
                position_instance = await Position.objects.acreate(**position_data)
                instance.position = position_instance

        graduate_data = validated_data.pop('graduate', None)
        if graduate_data:
            if instance.graduate:
                graduate_instance = instance.graduate
                for attr, value in graduate_data.items():
                    setattr(graduate_instance, attr, value)
                await sync_to_async(graduate_instance.save)()
            else:
                graduate_instance = await Graduate.objects.acreate(**graduate_data)
                instance.graduate = graduate_instance

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        await sync_to_async(instance.save)()
        await self.check_and_set_superuser(instance, instance.position)

        return instance

    async def check_and_set_superuser(self, member_instance, position_instance):
        """
        檢查並設置 superuser 權限
        """
        if position_instance.title == "管理員" or (position_instance.priority and position_instance.priority <= 3):
            member_instance.private.is_superuser = True
        else:
            member_instance.private.is_superuser = False
        await sync_to_async(member_instance.private.save)()
    
class MyListSerializer(serializers.ListSerializer):
    """
    自定義 ListSerializer，過濾掉 null 值
    """
    def to_representation(self, data):
        # 調用原生邏輯，過濾掉 None
        return [item for item in super().to_representation(data) if item is not None]

class MemberSimpleSerializer(serializers.ModelSerializer):
    position = serializers.SerializerMethodField()
    graduate = serializers.SerializerMethodField()

    class Meta:
        model = Member
        fields = ['id', 'name', 'gender', 'intro', 'photo', 'position', 'graduate']
        list_serializer_class = MyListSerializer

    async def get_position(self, instance):
        position = getattr(instance, 'position', None)
        if position:
            return {"title": position.title}
        return None

    async def get_graduate(self, instance):
        graduate = getattr(instance, 'graduate', None)
        if graduate:
            return {"school": graduate.school, "grade": graduate.grade}
        return None

    async def to_representation(self, instance):
        if not instance.is_show:
            return None
        representation = await sync_to_async(super().to_representation)(instance)
        return representation


class MemberSimpleAdminSerializer(serializers.ModelSerializer):
    position = serializers.SerializerMethodField()
    graduate = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    isActive = serializers.SerializerMethodField()

    class Meta:
        model = Member
        fields = ['id', 'name', 'gender', 'photo', 'position', 'graduate', 'email', 'is_paid', 'isActive']

    async def get_email(self, obj):
        return obj.private.email

    async def get_isActive(self, obj):
        return obj.private.is_active

    async def get_position(self, instance):
        position = getattr(instance, 'position', None)
        if position:
            return {"title": position.title}
        return None

    async def get_graduate(self, instance):
        graduate = getattr(instance, 'graduate', None)
        if graduate:
            return {"school": graduate.school, "grade": graduate.grade}
        return None

class MemberSimpleDetailSerializer(serializers.ModelSerializer):
    position = serializers.SerializerMethodField()
    graduate = serializers.SerializerMethodField()
    self_images = SelfImageSerializer(source='selfimage_set', many=True)
    company = CompanySearchSerializer(source='member')
    company_images = CompanyImageSerializer(source='member.companyimage_set', many=True)

    class Meta:
        model = Member
        fields = ['name', 'gender', 'intro', 'photo', 'position', 'graduate', 'company', 'company_images', 'self_images']

    async def get_position(self, instance):
        position = getattr(instance, 'position', None)
        if position:
            return {"title": position.title}
        return None

    async def get_graduate(self, instance):
        graduate = getattr(instance, 'graduate', None)
        if graduate:
            return {"school": graduate.school, "grade": graduate.grade}
        return None

    async def to_representation(self, instance):
        if not instance.is_show:
            return None
        representation = await sync_to_async(super().to_representation)(instance)
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
            'achievements', 'is_featured', 'highlight', 'date_awarded', 'position', 'graduate'
        ]
        read_only_fields = ['id', 'member_name', 'photo']

    async def get_position(self, instance):
        position = getattr(instance, 'position', None)
        if position:
            return {"title": position.title}
        return None

    async def get_graduate(self, instance):
        graduate = getattr(instance, 'graduate', None)
        if graduate:
            return {"school": graduate.school, "grade": graduate.grade}
        return None

    

class MemberCreateSerializer(serializers.ModelSerializer):
    notice_type = serializers.SerializerMethodField()
    position = PositionSerializer(required=False)
    graduate = GraduateSerializer(required=False)
    photo = Base64ImageField(required=False)
    private_input = serializers.IntegerField(write_only=True, required=False)

    class Meta:
        model = Member
        exclude = ('private', )

    async def create(self, validated_data):
        position_data = validated_data.pop('position', None)
        graduate_data = validated_data.pop('graduate', None)
        private_data = validated_data.pop('private_input', None)

        photo = None
        if 'photo' in validated_data:
            photo_data = validated_data.pop('photo')
            try:
                format, imgstr = photo_data.split(';base64,')
                ext = format.split('/')[-1]
                photo = ContentFile(base64.b64decode(imgstr), name=f'{uuid.uuid4()}.{ext}')
            except Exception as e:
                raise serializers.ValidationError({"photo": f"Invalid photo format: {str(e)}"})

        async with transaction.atomic():
            private_instance = None
            if isinstance(private_data, dict):
                private_instance = await Private.objects.acreate_user(
                    email=private_data['email'],
                    password=private_data['password']
                )
            elif isinstance(private_data, int):
                private_instance = await Private.objects.aget(pk=private_data)

            graduate_instance = None
            if graduate_data:
                graduate_instance = await Graduate.objects.acreate(**graduate_data)

            position_instance = await Position.objects.aget(title="會員")

            member_instance = await Member.objects.acreate(
                private=private_instance,
                graduate=graduate_instance,
                position=position_instance,
                photo=photo,
                **validated_data
            )

            await Notice.objects.acreate(
                member=member_instance,
                email_notifications=True,
                sms_notifications=False,
                news_notifications=True,
                promo_notifications=True
            )

            return member_instance

    async def get_notice_type(self, instance):
        notice = getattr(instance, 'notice', None)
        if notice:
            return {
                "email": notice.email_notifications,
                "news": notice.news_notifications,
                "promo": notice.promo_notifications,
            }
        return None
