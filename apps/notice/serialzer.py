from rest_framework import serializers
from apps.notice.models import NotificationSetting

class NotificationSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationSetting
        fields = ['email_notifications', 'sms_notifications', 'news_notifications', 'promo_notifications']
