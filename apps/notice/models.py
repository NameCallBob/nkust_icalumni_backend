from django.db import models
from apps.member.models import Member

class Notice(models.Model):
    member = models.OneToOneField(Member, on_delete=models.CASCADE, related_name='notification_setting')
    email_notifications = models.BooleanField(default=True)
    sms_notifications = models.BooleanField(default=False)
    news_notifications = models.BooleanField(default=True)
    promo_notifications = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.username}'s Notification Settings"