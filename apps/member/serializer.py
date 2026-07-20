from rest_framework import serializers
from apps.member.models import Member, Position, Graduate, OutstandingAlumni, SchoolOutstandingAlumni
from apps.notice.models import Notice
from apps.private.models import Private
from django.db import transaction
from django.contrib.auth.hashers import make_password
from apps.deal_base64 import Base64ImageField
# 序列化
from apps.picture.serializer import SelfImageSerializer , CompanyImageSerializer
from apps.company.serializer import CompanySearchSerializer

import base64
from asgiref.sync import sync_to_async

from django.db import transaction, connections

class PositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Position
        fields = '__all__'


class GraduateSerializer(serializers.ModelSerializer):
    # 明確設置字段允許空白，覆蓋模型的blank設置
    school = serializers.CharField(allow_blank=True, required=False)
    grade = serializers.CharField(allow_blank=True, required=False, max_length=20)
    student_id = serializers.CharField(allow_blank=True, required=False)
    
    class Meta:
        model = Graduate
        fields = '__all__'
    
    def validate(self, data):
        """
        驗證畢業資料，處理空字串但不返回None
        """
        # 處理空字串，轉換為模型的默認值
        if not data.get('school', '').strip():
            data['school'] = "國立高雄科技大學智慧商務系"
        if not data.get('grade', '').strip():
            data['grade'] = "000"
        if not data.get('student_id', '').strip():
            data['student_id'] = "尚未填寫"
            
        return data
    
    def create(self, validated_data):
        """
        創建Graduate實例
        """
        return super().create(validated_data)


class MemberSerializer(serializers.ModelSerializer):
    """
    系友會會員的序列化器
    將 Member 模型轉換為 JSON 格式，並進行驗證和反序列化。
    """
    email = serializers.SerializerMethodField()
    notice_type = serializers.SerializerMethodField()
    position = PositionSerializer(required=True)  # position 保持必填
    graduate = GraduateSerializer(required=False)
    photo = Base64ImageField(required=False)

    # 用於序列化輸出的 private 資料
    private = serializers.SerializerMethodField()
    # 用於接收反序列化資料（支援 id 或嵌套資料）
    private_input = serializers.DictField(write_only=True, required=False)

    class Meta:
        model = Member
        fields = '__all__'

    # [資安修補 SEC-001/SEC-003] 僅 staff 的請求可寫入管理性欄位（is_paid / is_show）；
    # private_input 一律僅允許安全欄位，權限欄位（is_staff/is_superuser/is_active）與密碼
    # 絕不可經此巢狀序列化器寫入（密碼改用專屬端點、權限改用 PrivateViewSet.adjust-account）。
    PRIVILEGED_MEMBER_FIELDS = ('is_paid', 'is_show')
    ALLOWED_PRIVATE_INPUT_FIELDS = ('email',)

    def _is_privileged(self):
        request = self.context.get('request') if hasattr(self, 'context') else None
        user = getattr(request, 'user', None)
        return bool(user and getattr(user, 'is_authenticated', False) and getattr(user, 'is_staff', False))

    def _strip_privileged_fields(self, validated_data):
        """非 staff 請求移除管理性欄位，避免會員自助竄改繳費/展示狀態。"""
        if not self._is_privileged():
            for field in self.PRIVILEGED_MEMBER_FIELDS:
                validated_data.pop(field, None)

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

    # [資安修補 CRIT-1] 移除依前端 position 自動賦予 superuser 的邏輯。
    # 權限（is_superuser / is_staff）絕不可由使用者可控的 position 資料推導，
    # 否則未驗證者可透過 POST /basic/register 直接提權為 Django 超級使用者。
    # 權限調整僅能經由受管理員保護的後台流程進行。

    def validate_photo(self, value):
        """
        驗證照片格式和大小，但允許空值
        """
        if value:
            if isinstance(value, str):
                try:
                    format, imgstr = value.split(';base64,')
                    ext = format.split('/')[-1]
                    # 檢查檔案格式
                    if ext.lower() not in ['jpg', 'jpeg', 'png', 'gif']:
                        raise serializers.ValidationError("照片格式不正確，請使用 JPG、PNG 或 GIF 格式")
                    # 檢查檔案大小（限制為 5MB）
                    if len(base64.b64decode(imgstr)) > 5 * 1024 * 1024:
                        raise serializers.ValidationError("照片大小不能超過 5MB，請壓縮後再上傳")
                except Exception as e:
                    raise serializers.ValidationError("照片格式錯誤，請確認是否為正確的圖片檔案")
        return value

    def validate_position(self, value):
        """
        驗證職位資料，放寬驗證條件
        """
        # 如果沒有提供position或title為空，不強制要求
        return value

    def validate_graduate(self, value):
        """
        驗證畢業資料，允許空值和空字串
        """
        # 直接返回，讓GraduateSerializer自己處理驗證
        return value

    def validate_private_input(self, value):
        """
        驗證私人資料，允許更靈活的格式
        """
        if value:
            if isinstance(value, dict):
                # 允許空字串或None值
                return value
            elif isinstance(value, int):
                return value
            else:
                # 嘗試轉換為整數（如果是字串格式的數字）
                try:
                    return int(value)
                except (ValueError, TypeError):
                    pass
        return value

    def create(self, validated_data):
        position_data = validated_data.pop('position', None)
        graduate_data = validated_data.pop('graduate', None)
        private_data = validated_data.pop('private_input', None)
        photo_data = validated_data.pop('photo', None)

        private_instance = None
        try:
            # 處理 graduate 資料
            graduate_instance = None
            if graduate_data:
                try:
                    # 使用 GraduateSerializer 來處理空字串情況
                    graduate_serializer = GraduateSerializer(data=graduate_data)
                    if graduate_serializer.is_valid():
                        graduate_instance = graduate_serializer.save()
                except Exception as e:
                    # 如果Graduate創建失敗，不中斷整個過程
                    graduate_instance = None

            # 處理 position 資料，更加寬鬆
            position_instance = None
            if position_data and position_data.get('title'):
                try:
                    position_title = position_data.get('title')
                    position_instance = Position.objects.filter(title=position_title).first()
                    if not position_instance:
                        # 嘗試創建position，如果失敗則使用默認值
                        try:
                            position_instance = Position.objects.create(**position_data)
                        except Exception:
                            position_instance = None
                except Exception as e:
                    position_instance = None
            
            # 如果沒有有效的position，嘗試使用默認的"會員"
            if not position_instance:
                try:
                    position_instance = Position.objects.get(title="會員")
                except Position.DoesNotExist:
                    try:
                        position_instance = Position.objects.create(title="會員", priority=999)
                    except Exception:
                        position_instance = None

            # photo 已由 Base64ImageField.to_internal_value 驗證/壓縮成 WebP，直接使用即可
            # （之前這裡會把它當成原始 base64 字串再 split(';base64,') 一次，
            # 但欄位轉換後 photo_data 早已是 ContentFile/None，isinstance(..., str)
            # 永遠是 False，導致自助註冊上傳的大頭照被靜默丟棄）
            photo = photo_data

            with transaction.atomic():
                # 處理 private 資料，更加寬鬆
                if private_data:
                    try:
                        if isinstance(private_data, dict):
                            email = private_data.get('email', '').strip()
                            password = private_data.get('password', '').strip()
                            if email and password:
                                private_instance = Private.objects.create_user(
                                    email=email,
                                    password=password
                                )
                        elif isinstance(private_data, int):
                            try:
                                private_instance = Private.objects.get(pk=private_data)
                            except Private.DoesNotExist:
                                private_instance = None
                    except Exception as e:
                        # 如果Private創建失敗，不中斷整個過程
                        private_instance = None

                # [資安修補 SEC-003] 非 staff（含匿名註冊）不可自設 is_paid / is_show
                self._strip_privileged_fields(validated_data)

                # 創建會員，移除可能導致錯誤的空值
                create_data = {}
                for key, value in validated_data.items():
                    if value is not None and value != '':
                        create_data[key] = value

                try:
                    member_instance = Member.objects.create(
                        private=private_instance,
                        graduate=graduate_instance,
                        position=position_instance,
                        photo=photo,
                        **create_data
                    )
                except Exception as e:
                    raise serializers.ValidationError({"detail": "會員資料格式不正確，請檢查填寫的資料"})

                # [資安修補 CRIT-1] 不再依 position 設定 superuser 權限。

                # 創建通知設定
                try:
                    Notice.objects.create(
                        member=member_instance,
                        email_notifications=True,
                        sms_notifications=False,
                        news_notifications=True,
                        promo_notifications=True
                    )
                except Exception as e:
                    # 通知設定創建失敗，記錄但不中斷
                    pass

                return member_instance

        except serializers.ValidationError as e:
            raise e
        except Exception as e:
            raise serializers.ValidationError({"detail": "系統發生錯誤，請稍後再試"})

    def update(self, instance, validated_data):
        try:
            validated_data.pop('school', None)
            validated_data.pop('grade', None)

            # 處理 position 資料，更加寬鬆
            position_instance = None
            position_data = validated_data.pop('position', None)
            if position_data and position_data.get('title'):
                try:
                    position_title = position_data.get('title')
                    position_instance = Position.objects.filter(title=position_title).first()
                    if position_instance:
                        for attr, value in position_data.items():
                            setattr(position_instance, attr, value)
                        position_instance.save()
                    else:
                        try:
                            position_instance = Position.objects.create(**position_data)
                        except Exception:
                            position_instance = None
                    
                    # [資安修補 CRIT-1] 不再依 position 設定 superuser 權限。
                    if position_instance:
                        instance.position = position_instance
                except Exception as e:
                    # 如果position更新失敗，記錄但不中斷整個過程
                    pass

            # 處理 graduate 資料，更加寬鬆
            graduate_data = validated_data.pop('graduate', None)
            if graduate_data:
                try:
                    # 使用 GraduateSerializer 來處理空字串情況
                    graduate_serializer = GraduateSerializer(data=graduate_data)
                    if graduate_serializer.is_valid():
                        if instance.graduate:
                            # 更新現有的 Graduate 實例
                            validated_graduate_data = graduate_serializer.validated_data
                            for attr, value in validated_graduate_data.items():
                                setattr(instance.graduate, attr, value)
                            instance.graduate.save()
                        else:
                            # 創建新的 Graduate 實例
                            graduate_instance = graduate_serializer.save()
                            instance.graduate = graduate_instance
                except Exception as e:
                    # 如果graduate更新失敗，記錄但不中斷整個過程
                    pass

            # 處理 private 資料
            # [資安修補 SEC-001] 僅允許白名單欄位（email），禁止經此途徑寫入
            # is_staff / is_superuser / is_active / password 等敏感欄位，根除自助提權。
            private_data = validated_data.pop('private_input', None)
            if private_data and instance.private:
                try:
                    for attr, value in private_data.items():
                        if attr not in self.ALLOWED_PRIVATE_INPUT_FIELDS:
                            continue
                        if value is not None and value != '':
                            setattr(instance.private, attr, value)
                    instance.private.save()
                except Exception as e:
                    # 如果private更新失敗，記錄但不中斷整個過程
                    pass

            # [資安修補 SEC-003] 非 staff 不可竄改 is_paid / is_show
            self._strip_privileged_fields(validated_data)

            # 更新其他欄位，過濾空值
            for attr, value in validated_data.items():
                if value is not None and value != '':
                    setattr(instance, attr, value)

            instance.save()
            return instance

        except serializers.ValidationError as e:
            raise e
        except Exception as e:
            raise serializers.ValidationError({"detail": "系統發生錯誤，請稍後再試"})

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
    self_images = SelfImageSerializer(source='selfimage_set', many=True, read_only=True)  # 假設一個會員可以有多個 SelfImage
    company = CompanySearchSerializer(read_only=True)  # 不需要指定 source，因為欄位名稱就是 company
    company_images = CompanyImageSerializer(source='company.companyimage_set', many=True, read_only=True)

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
            'achievements', 'is_featured', 'highlight', 'date_awarded',
            'position', 'graduate', 'sort_order'
        ]
        read_only_fields = ['id', 'member_name', 'photo']

    def get_position(self, instance):
            position = getattr(instance.member, 'position', None)
            if position:
                return {
                    "title": position.title,
                }
            return None

    def get_graduate(self, instance):
            graduate = getattr(instance.member, 'graduate', None)
            if graduate:
                return {
                    "school": graduate.school,
                    "grade": graduate.grade
                }
            return None


class SchoolOutstandingAlumniSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='member.name', read_only=True)
    photo = serializers.ImageField(source='member.photo', read_only=True)
    position = serializers.SerializerMethodField()
    graduate = serializers.SerializerMethodField()

    class Meta:
        model = SchoolOutstandingAlumni
        fields = [
            'id', 'member', 'name', 'photo',
            'achievements', 'is_featured', 'highlight', 'date_awarded',
            'position', 'graduate', 'sort_order'
        ]
        read_only_fields = ['id', 'member_name', 'photo']

    def get_position(self, instance):
            position = getattr(instance.member, 'position', None)
            if position:
                return {
                    "title": position.title,
                }
            return None

    def get_graduate(self, instance):
            graduate = getattr(instance.member, 'graduate', None)
            if graduate:
                return {
                    "school": graduate.school,
                    "grade": graduate.grade
                }
            return None


class MemberCreateSerializer(serializers.ModelSerializer):
    notice_type = serializers.SerializerMethodField()
    position = PositionSerializer(required=False)
    graduate = GraduateSerializer(required=False)
    photo = Base64ImageField(required=False)
    # 改為更靈活的字段類型，可以接受字典或整數
    private_input = serializers.JSONField(write_only=True, required=False)

    class Meta:
        model = Member
        exclude = ('private', )

    def validate_private_input(self, value):
        """
        驗證私人資料，允許更靈活的格式
        """
        if value:
            if isinstance(value, dict):
                # 允許空字串或None值
                return value
            elif isinstance(value, int):
                return value
            else:
                # 嘗試轉換為整數（如果是字串格式的數字）
                try:
                    return int(value)
                except (ValueError, TypeError):
                    pass
        return value

    def validate_graduate(self, value):
        """
        驗證畢業資料，允許空值和空字串
        """
        # 直接返回，讓GraduateSerializer自己處理驗證
        return value

    def validate_position(self, value):
        """
        驗證職位資料，允許空值
        """
        # 如果沒有提供position，使用默認值
        return value

    def create(self, validated_data):
        position_data = validated_data.pop('position', None)
        graduate_data = validated_data.pop('graduate', None)
        private_data = validated_data.pop('private_input', None)

        # photo 已由 Base64ImageField.to_internal_value 驗證/壓縮成 WebP，直接使用即可
        photo = validated_data.pop('photo', None)

        # 使用同步事務處理
        with transaction.atomic():
            private_instance = None
            if private_data:
                try:
                    if isinstance(private_data, dict):
                        email = private_data.get('email', '').strip()
                        password = private_data.get('password', '').strip()
                        if email and password:
                            private_instance = Private.objects.create_user(
                                email=email,
                                password=password
                            )
                    elif isinstance(private_data, int):
                        try:
                            private_instance = Private.objects.get(pk=private_data)
                        except Private.DoesNotExist:
                            # 如果找不到Private實例，不中斷創建過程
                            private_instance = None
                except Exception as e:
                    # 如果Private創建失敗，不中斷整個過程
                    private_instance = None

            graduate_instance = None
            if graduate_data:
                try:
                    # 使用 GraduateSerializer 來處理空字串情況
                    graduate_serializer = GraduateSerializer(data=graduate_data)
                    if graduate_serializer.is_valid():
                        graduate_instance = graduate_serializer.save()
                except Exception as e:
                    # 如果Graduate創建失敗，不中斷整個過程
                    graduate_instance = None

            # 嘗試獲取默認position，如果不存在則創建
            try:
                position_instance = Position.objects.get(title="會員")
            except Position.DoesNotExist:
                try:
                    position_instance = Position.objects.create(title="會員", priority=10)
                except Exception:
                    # 如果無法創建默認position，使用None
                    position_instance = None

            # 創建會員實例，移除可能導致錯誤的空值
            create_data = {}
            for key, value in validated_data.items():
                if value is not None and value != '':
                    create_data[key] = value

            member_instance = Member.objects.create(
                private=private_instance,
                graduate=graduate_instance,
                position=position_instance,
                photo=photo,
                **create_data
            )

            # 嘗試創建通知設定，如果失敗也不中斷
            try:
                Notice.objects.create(
                    member=member_instance,
                    email_notifications=True,
                    sms_notifications=False,
                    news_notifications=True,
                    promo_notifications=True
                )
            except Exception:
                # 如果通知設定創建失敗，繼續執行
                pass

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
