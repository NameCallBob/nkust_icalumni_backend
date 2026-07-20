from django.apps import AppConfig


class RecordConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.record'

    def ready(self):
        import apps.record.signals  # 確保 CRUD 操作記錄的信號檔案被載入
