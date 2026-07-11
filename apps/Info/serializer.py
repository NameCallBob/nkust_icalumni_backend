import base64
import uuid
from django.core.files.base import ContentFile
from rest_framework import serializers

from apps.Info.models import (
    AlumniAssociation,
    AlumniAssociationImage,
    Constitution,
    ConstitutionImage,
    OrganizationalStructure,
    OrganizationalStructureImage,
    MembershipRequirement,
    MembershipRequirementImage,
    MembershipRequirement_v2,
)
from rest_framework.exceptions import ValidationError


class Base64ImageField(serializers.ImageField):
    """自定義序列化器欄位，用於處理 Base64 格式的圖片"""

    def to_internal_value(self, data):
        # [資安修補 INFO-2] 加入大小上限與「以內容判斷型別」白名單，不信任前端宣稱的副檔名
        from apps.deal_base64 import ALLOWED_IMAGE_EXTENSIONS, MAX_IMAGE_UPLOAD_SIZE
        import imghdr
        try:
            if isinstance(data, str) and data.startswith("data:image"):
                # 提取圖片內容（忽略前端宣稱的格式，改以實際內容判斷）
                _format, imgstr = data.split(";base64,")
                if not imgstr:
                    raise ValidationError("無效的圖片格式或內容缺失。")

                try:
                    decoded = base64.b64decode(imgstr)
                except (TypeError, base64.binascii.Error) as decode_error:
                    raise ValidationError(f"圖片解碼失敗: {str(decode_error)}")

                if len(decoded) > MAX_IMAGE_UPLOAD_SIZE:
                    raise ValidationError(
                        f"圖片大小不能超過 {MAX_IMAGE_UPLOAD_SIZE // (1024 * 1024)}MB，請壓縮後再上傳"
                    )

                ext = imghdr.what(None, decoded)
                ext = "jpg" if ext == "jpeg" else ext
                if ext is None and decoded[:4] == b'RIFF' and decoded[8:12] == b'WEBP':
                    ext = "webp"
                if ext not in ALLOWED_IMAGE_EXTENSIONS:
                    raise ValidationError("不支援的圖片格式，僅允許 JPG、PNG、GIF、WEBP")

                file_name = f"{uuid.uuid4()}.{ext}"
                data = ContentFile(decoded, name=file_name)

            return super().to_internal_value(data)
        except (ValueError, IndexError) as parse_error:
            raise ValidationError(f"無效的圖片數據: {str(parse_error)}")
        except Exception as e:
            raise ValidationError(f"圖片處理時發生未預期錯誤: {str(e)}")

    def to_representation(self, value):
        try:
            if value:
                with open(value.path, "rb") as image_file:
                    base64_data = base64.b64encode(image_file.read()).decode("utf-8")
                    return f"data:image/{value.name.split('.')[-1]};base64,{base64_data}"
            return None
        except FileNotFoundError:
            raise ValidationError("圖片文件未找到或無法訪問。")
        except Exception as e:
            raise ValidationError(f"圖片轉換 Base64 時發生錯誤: {str(e)}")

# 照片區

class AlumniAssociationImageSerializer(serializers.ModelSerializer):
    file = Base64ImageField()  # 使用自定義 Base64ImageField 處理圖片

    class Meta:
        model = AlumniAssociationImage
        fields = "__all__"

    def create(self, validated_data):
        """處理圖片的新增（Base64 格式）"""
        return AlumniAssociationImage.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """處理圖片的更新（Base64 格式）"""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class ConstitutionImageSerializer(serializers.ModelSerializer):
    file = Base64ImageField()

    class Meta:
        model = ConstitutionImage
        fields = "__all__"

    def create(self, validated_data):
        """處理圖片的新增（Base64 格式）"""
        return ConstitutionImage.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """處理圖片的更新（Base64 格式）"""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class OrganizationalStructureImageSerializer(serializers.ModelSerializer):
    file = Base64ImageField()

    class Meta:
        model = OrganizationalStructureImage
        fields = "__all__"

    def create(self, validated_data):
        """處理圖片的新增（Base64 格式）"""
        return OrganizationalStructureImage.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """處理圖片的更新（Base64 格式）"""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class MembershipRequirementImageSerializer(serializers.ModelSerializer):
    file = Base64ImageField()

    class Meta:
        model = MembershipRequirementImage
        fields = "__all__"

    def create(self, validated_data):
        """處理圖片的新增（Base64 格式）"""
        return MembershipRequirementImage.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """處理圖片的更新（Base64 格式）"""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance



# 資料區

class AlumniAssociationSerializer(serializers.ModelSerializer):
    images = AlumniAssociationImageSerializer(many=True, read_only=True)
    images_data = serializers.ListField(
        child=serializers.DictField(), write_only=True, required=False
    )

    class Meta:
        model = AlumniAssociation
        fields = "__all__"

    def create(self, validated_data):
        images_data = validated_data.pop("images_data", [])
        association = AlumniAssociation.objects.create(**validated_data)
        for image_data in images_data:
            AlumniAssociationImage.objects.create(alumni_association=association, **image_data)
        return association

    def update(self, instance, validated_data):
        images_data = validated_data.pop("images_data", [])
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if images_data:
            AlumniAssociationImage.objects.filter(alumni_association=instance).delete()
            for image_data in images_data:
                AlumniAssociationImage.objects.create(image_data)
        return instance




class ConstitutionSerializer(serializers.ModelSerializer):
    images = ConstitutionImageSerializer(many=True, read_only=True)
    images_data = serializers.ListField(
        child=serializers.DictField(), required=False
    )

    class Meta:
        model = Constitution
        fields = "__all__"

    def create(self, validated_data):
        images_data = validated_data.pop("images_data", [])
        constitution = Constitution.objects.create(**validated_data)
        for image_data in images_data:
            ConstitutionImage.objects.create(constitution=constitution, **image_data)
        return constitution

    def update(self, instance, validated_data):
        images_data = validated_data.pop("images_data", [])
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if images_data:
            instance.images.all().delete()
            for image_data in images_data:
                ConstitutionImage.objects.create(constitution=instance, **image_data)
        return instance

    def to_representation(self, instance):
        """自定義輸出格式"""
        data = super().to_representation(instance)
        
        # 只返回檔案路徑，不包含網域
        if instance.pdf_file:
            data['pdf_file'] = instance.pdf_file.name
        else:
            data['pdf_file'] = None
            
        return data



class OrganizationalStructureSerializer(serializers.ModelSerializer):
    images = OrganizationalStructureImageSerializer(many=True, read_only=True)
    images_data = serializers.ListField(
        child=serializers.DictField(), write_only=True, required=False
    )

    class Meta:
        model = OrganizationalStructure
        fields = "__all__"

    def create(self, validated_data):
        images_data = validated_data.pop("images_data", [])
        structure = OrganizationalStructure.objects.create(**validated_data)
        for image_data in images_data:
            OrganizationalStructureImage.objects.create(
                organizational_structure=structure, **image_data
            )
        return structure

    def update(self, instance, validated_data):
        images_data = validated_data.pop("images_data", [])
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if images_data:
            instance.images.all().delete()
            for image_data in images_data:
                OrganizationalStructureImage.objects.create(
                    organizational_structure=instance, **image_data
                )
        return instance

class MembershipRequirementSerializer(serializers.ModelSerializer):
    images = MembershipRequirementImageSerializer(many=True, read_only=True)
    images_data = serializers.ListField(
        child=serializers.DictField(), write_only=True, required=False
    )

    class Meta:
        model = MembershipRequirement
        fields = "__all__"

    def create(self, validated_data):
        images_data = validated_data.pop("images_data", [])
        requirement = MembershipRequirement.objects.create(**validated_data)
        for image_data in images_data:
            MembershipRequirementImage.objects.create(
                membership_requirement=requirement, **image_data
            )
        return requirement

    def update(self, instance, validated_data):
        images_data = validated_data.pop("images_data", [])
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if images_data:
            instance.images.all().delete()
            for image_data in images_data:
                MembershipRequirementImage.objects.create(
                    membership_requirement=instance, **image_data
                )
        return instance


class MembershipRequirementSerializer_v2(serializers.ModelSerializer):
    """入會條件v2序列化器"""

    class Meta:
        model = MembershipRequirement_v2
        fields = ['id', 'description', 'pdf_file', 'created_at', 'updated_at']
        extra_kwargs = {
            'description': {
                'required': False,
                'allow_blank': True,
                'help_text': '入會條件描述，支援 HTML 標籤'
            },
            'pdf_file': {
                'required': False,
                'allow_null': True,
                'help_text': '入會條件 PDF 檔案'
            }
        }

    def validate_description(self, value):
        """驗證描述欄位"""
        if value and len(value.strip()) > 10000:
            raise serializers.ValidationError("描述內容過長，請控制在 10000 字以內")
        return value

    def validate_pdf_file(self, value):
        """驗證 PDF 檔案"""
        if value:
            # 檢查檔案大小 (限制 10MB)
            if value.size > 10 * 1024 * 1024:
                raise serializers.ValidationError("PDF 檔案大小不能超過 10MB")

            # 檢查檔案類型
            if not value.name.lower().endswith('.pdf'):
                raise serializers.ValidationError("請上傳 PDF 格式的檔案")

        return value

    def validate(self, attrs):
        """整體驗證"""
        # 新增時至少要有一個欄位有內容
        if not self.instance:  # 新增時
            description = attrs.get('description', '').strip()
            pdf_file = attrs.get('pdf_file')

            if not description and not pdf_file:
                raise serializers.ValidationError("請至少填寫入會條件描述或上傳 PDF 檔案")

        return attrs

    def to_representation(self, instance):
        """自定義輸出格式"""
        data = super().to_representation(instance)

        # 格式化時間顯示
        if instance.created_at:
            data['created_at'] = instance.created_at.strftime('%Y-%m-%d %H:%M:%S')
        if instance.updated_at:
            data['updated_at'] = instance.updated_at.strftime('%Y-%m-%d %H:%M:%S')
        
        # 只返回檔案路徑，不包含網域
        if instance.pdf_file:
            data['pdf_file'] = instance.pdf_file.name
        else:
            data['pdf_file'] = None
            
        return data