from rest_framework import serializers
from apps.member.models import Member, Position, Graduate
from apps.notice.models import Notice
from apps.private.models import Private
from django.db import transaction
from django.contrib.auth.hashers import make_password
# 序列化
from apps.picture.serializer import SelfImageSerializer , CompanyImageSerializer
from apps.company.serializer import CompanySearchSerializer

class MemberSerializer(serializers.ModelSerializer):
    """
    系友會會員的序列化器
    將 Member 模型轉換為 JSON 格式，並進行驗證和反序列化。
    """
    email = serializers.SerializerMethodField()
    notice_type = serializers.SerializerMethodField()
    position = serializers.SerializerMethodField()
    graduate = serializers.SerializerMethodField()

    class Meta:
        model = Member
        fields = '__all__'

    def get_email(self,instance):
        private = getattr(instance, 'private', None)
        return private.email

    def get_notice_type(self, instance):
        notice = getattr(instance, 'notice', None)
        if notice:
            return {
                "email": notice.email_notifications,
                "news": notice.news_notifications,
                "promo": notice.promo_notifications,
            }
        return None

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

    def create(self, validated_data):
        try:
            with transaction.atomic():
                private_instance = Private.objects.create(
                    email=validated_data['email'],
                    password=make_password(validated_data['password']),
                    is_active=False
                )

                graduate_instance = Graduate.objects.create(
                    school=validated_data.get('school'),
                    grade=validated_data.get('grade')
                )

                member_instance = Member.objects.create(
                    private=private_instance,
                    name=validated_data['name'],
                    home_phone=validated_data.get('home_phone'),
                    mobile_phone=validated_data.get('mobile_phone'),
                    gender=validated_data.get('gender'),
                    address=validated_data.get('address'),
                    is_paid=False,
                    intro=validated_data.get('intro'),
                    birth_date=validated_data.get('birth_date'),
                    photo=None,
                    position=Position.objects.get(id=1),
                    graduate=graduate_instance,
                )

                notice_instance = Notice.objects.create(
                    member = member_instance,
                    email_notifications=True,
                    sms_notifications=False,
                    news_notifications=True,
                    promo_notifications=True
                )

                return member_instance

        except Exception as e:
            raise serializers.ValidationError(f"An error occurred during creation: {str(e)}")


class MemberSimpleSerializer(serializers.ModelSerializer):
    """
    一般官網預覽使用
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


class PositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Position
        fields = '__all__'

class GraduateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Graduate
        fields = '__all__'