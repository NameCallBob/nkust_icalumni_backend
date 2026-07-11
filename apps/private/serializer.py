from rest_framework import serializers
from apps.private.models import Private,PasswordResetCode

class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        # [資安修補 SEC-017] 不再因「Email 未註冊」回傳可區分的錯誤，避免帳號列舉。
        # 僅驗證 Email 格式（EmailField 已處理），是否存在由 view 端靜默處理。
        return value

    def create_reset_code(self, user):
        reset_code = PasswordResetCode.objects.create(private=user)
        return reset_code
    


# for管理員使用
class PrivateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Private
        fields = ['id', 'email', 'is_active', 'is_staff', 'is_superuser', 'last_login', 'date_joined']
