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
)
from rest_framework.exceptions import ValidationError


class Base64ImageField(serializers.ImageField):
    """自定義序列化器欄位，用於處理 Base64 格式的圖片"""

    def to_internal_value(self, data):
        try:
            if isinstance(data, str) and data.startswith("data:image"):
                # 提取圖片格式和內容
                format, imgstr = data.split(";base64,")
                ext = format.split("/")[-1]

                if not ext or not imgstr:
                    raise ValidationError("無效的圖片格式或內容缺失。")

                # 解碼圖片並生成文件名
                try:
                    file_name = f"{uuid.uuid4()}.{ext}"
                    data = ContentFile(base64.b64decode(imgstr), name=file_name)
                except (TypeError, base64.binascii.Error) as decode_error:
                    raise ValidationError(f"圖片解碼失敗: {str(decode_error)}")

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