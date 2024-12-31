from django.apps import AppConfig


class PrivateConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.private'
    label = "Private"

    def ready(self):
        import apps.private.signals  # 確保信號檔案被載入
