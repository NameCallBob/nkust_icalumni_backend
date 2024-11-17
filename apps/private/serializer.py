from rest_framework import serializers
from apps.private.models import Private,PasswordResetCode

class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        try:
            user = Private.objects.get(email=value)
        except Private.DoesNotExist:
            raise serializers.ValidationError("此電子郵件未註冊")
        return value

    def create_reset_code(self, user):
        reset_code = PasswordResetCode.objects.create(private=user)
        return reset_code
    


# for管理員使用
class PrivateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Private
        fields = ['id', 'email', 'is_active', 'is_staff', 'is_superuser', 'last_login', 'date_joined']
