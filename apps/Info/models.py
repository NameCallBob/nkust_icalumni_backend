from django.db import models

class AlumniAssociation(models.Model):
    """系友會基本資訊"""
    name = models.CharField(max_length=255, verbose_name="系友會名稱")
    description = models.TextField(verbose_name="簡介", help_text="支援 HTML 標籤的簡介")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="建立時間")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新時間")

    def __str__(self):
        return self.name


class Constitution(models.Model):
    """系友會章程"""
    alumni_association = models.ForeignKey(
        AlumniAssociation, on_delete=models.CASCADE, related_name="constitutions", verbose_name="系友會"
    )
    title = models.CharField(max_length=255, verbose_name="章程標題")
    pdf_file = models.FileField(upload_to="constitutions/", verbose_name="章程 PDF 檔案")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="建立時間")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新時間")

    def __str__(self):
        return self.title


class OrganizationalStructure(models.Model):
    """系友會組織架構"""
    alumni_association = models.ForeignKey(
        AlumniAssociation, on_delete=models.CASCADE, related_name="organization_structures", verbose_name="系友會"
    )
    role_name = models.CharField(max_length=255, verbose_name="角色名稱")
    responsibilities = models.TextField(verbose_name="職責描述", help_text="支援 HTML 標籤")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="建立時間")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新時間")

    def __str__(self):
        return self.role_name


class MembershipRequirement(models.Model):
    """系友會入會條件"""
    alumni_association = models.ForeignKey(
        AlumniAssociation, on_delete=models.CASCADE, related_name="membership_requirements", verbose_name="系友會"
    )
    requirement = models.TextField(verbose_name="入會條件", help_text="支援 HTML 標籤")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="建立時間")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新時間")

    def __str__(self):
        return f"Requirement for {self.alumni_association.name}"


class Attachment(models.Model):
    """系友會相關的附加檔案"""
    alumni_association = models.ForeignKey(
        AlumniAssociation, on_delete=models.CASCADE, related_name="attachments", verbose_name="系友會"
    )
    file_name = models.CharField(max_length=255, verbose_name="檔案名稱")
    file_path = models.FileField(upload_to="attachments/", verbose_name="檔案路徑")
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name="上傳時間")

    def __str__(self):
        return self.file_name
