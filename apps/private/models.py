from django.db import models
from django.contrib.auth.models import BaseUserManager,AbstractBaseUser
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import PermissionsMixin
from apps.notice.email import email as notice_email
#  自定義使用者之相關設定
class CustomUserManager(BaseUserManager):
    def create_user(self,email,password,**extra_fields):
        """建立一般使用者"""
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        extra_fields.setdefault("is_active", True)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()

        from threading import Thread
        Thread(target=notice_email.member_account_created,args=(email,password,)).start()

        return user

    def create_superuser(self,email,password,**extra_fields):
        """建立管理員或特別權限者"""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        if extra_fields.get("is_staff") is not True:
            raise ValueError(("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(("Superuser must have is_superuser=True."))
        
        from threading import Thread
        Thread(target=notice_email.member_account_created,args=(email,password,)).start()

        return self.create_user(email, password,**extra_fields)

# 實際 自定義 Model

class Private(AbstractBaseUser , PermissionsMixin):
    """
    使用者最高隱私之儲存內容
    """
    id = models.AutoField("id",primary_key=True)
    email = models.CharField("電子郵件", max_length=50 ,null=False,unique=True)
    password = models.CharField("密碼",max_length=100,null=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False) # a admin user; non super-user
    is_superuser = models.BooleanField(default=False) # a superuser
    last_login = models.DateTimeField(auto_now=True,null=True, blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ['password']
    objects = CustomUserManager()
    @property
    def is_anonymous(self):
        return False



import random
from datetime import  timedelta
from django.utils import timezone

class PasswordResetCode(models.Model):
    private = models.ForeignKey(Private, on_delete=models.CASCADE)
    code = models.CharField(max_length=6, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    expires_at = models.DateTimeField()
    def save(self, *args, **kwargs):
        if not self.code:
            self.code = self.generate_code()
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(hours=1)
        super().save(*args, **kwargs)

    def generate_code(self):
        return ''.join(random.choices('0123456789', k=6))

    def is_expired(self):
        return timezone.now() > self.expires_at