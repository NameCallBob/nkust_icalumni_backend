from django.db import models

class AlumniAssociation(models.Model):
    """系友會基本資料"""
    description = models.TextField(verbose_name="簡介", help_text="支援 HTML 標籤")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="建立時間")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新時間")

    def __str__(self):
        return f"簡介創立於{self.created_at}"


class AlumniAssociationImage(models.Model):
    """系友會相關圖片"""
    IMAGE_TYPE_CHOICES = (
        ('large', '大圖'),
        ('small', '小圖'),
    )
    image_type = models.CharField(
        max_length=10, choices=IMAGE_TYPE_CHOICES, verbose_name="圖片類型"
    )
    file = models.ImageField(upload_to="info/alumni_association_images/", verbose_name="圖片檔案")
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name="上傳時間")
    is_active = models.BooleanField()
    def __str__(self):
        return f"{self.uploaded_at} - {self.get_image_type_display()}"


class Constitution(models.Model):
    """系友會章程（PDF格式）"""
    description = models.TextField()
    pdf_file = models.FileField(upload_to="info/constitutions/", verbose_name="章程 PDF 檔案")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="建立時間")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新時間")

    def __str__(self):
        return f"章程上傳於{self.created_at}"


class ConstitutionImage(models.Model):
    """章程相關圖片"""
    IMAGE_TYPE_CHOICES = (
        ('large', '大圖'),
        ('small', '小圖'),
    )
    image_type = models.CharField(
        max_length=10, choices=IMAGE_TYPE_CHOICES, verbose_name="圖片類型"
    )
    file = models.ImageField(upload_to="info/constitution_images/", verbose_name="圖片檔案")
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name="上傳時間")
    is_active = models.BooleanField()
    def __str__(self):
        return f"{self.constitution.title} - {self.get_image_type_display()}"


class OrganizationalStructure(models.Model):
    """系友會組織架構"""
    description = models.TextField(verbose_name="職責描述", help_text="支援 HTML 標籤")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="建立時間")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新時間")

    def __str__(self):
        return self.role_name


class OrganizationalStructureImage(models.Model):
    """組織架構相關圖片"""
    IMAGE_TYPE_CHOICES = (
        ('large', '大圖'),
        ('small', '小圖'),
    )
    image_type = models.CharField(
        max_length=10, choices=IMAGE_TYPE_CHOICES, verbose_name="圖片類型"
    )
    file = models.ImageField(upload_to="info/organizational_structure_images/", verbose_name="圖片檔案")
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name="上傳時間")
    is_active = models.BooleanField()
    def __str__(self):
        return f"{self.organizational_structure.role_name} - {self.get_image_type_display()}"


# 舊版
class MembershipRequirement(models.Model):
    """系友會入會方式"""
    description = models.TextField(verbose_name="入會條件", help_text="支援 HTML 標籤")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="建立時間")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新時間")

    def __str__(self):
        return f"入會條件 ID: {self.id}"


class MembershipRequirementImage(models.Model):
    """入會條件相關圖片"""
    IMAGE_TYPE_CHOICES = (
        ('large', '大圖'),
        ('small', '小圖'),
    )
    image_type = models.CharField(
        max_length=10, choices=IMAGE_TYPE_CHOICES, verbose_name="圖片類型"
    )
    file = models.ImageField(upload_to="info/membership_requirement_images/", verbose_name="圖片檔案")
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name="上傳時間")
    is_active = models.BooleanField()
    def __str__(self):
        return f"入會條件 {self.membership_requirement.id} - {self.get_image_type_display()}"

#
class MembershipRequirement_v2(models.Model):
    """系友會入會方式"""
    description = models.TextField(verbose_name="入會條件", help_text="支援 HTML 標籤")
    pdf_file = models.FileField(upload_to="info/membership_requirement_v2/", verbose_name="入會條件 PDF 檔案")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="建立時間")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新時間")

    def __str__(self):
        return f"入會條件 ID: {self.id}"
