# monitoring/signals.py
import json
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.apps import apps
from django.forms.models import model_to_dict
from django.core.serializers.json import DjangoJSONEncoder
from apps.record.models import CRUDLog


def get_user_from_request():
    """從當前請求中獲取用戶"""
    from threading import local
    _thread_locals = local()
    if hasattr(_thread_locals, 'request'):
        request = _thread_locals.request
        if hasattr(request, 'user') and request.user.is_authenticated:
            return request.user
    return None


def get_request_log_from_request():
    """從當前請求中獲取請求日誌"""
    from threading import local
    _thread_locals = local()
    if hasattr(_thread_locals, 'request_log'):
        return _thread_locals.request_log
    return None


def get_client_ip_from_request():
    """從當前請求中獲取客戶端IP"""
    from threading import local
    _thread_locals = local()
    if hasattr(_thread_locals, 'request'):
        request = _thread_locals.request
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR')
    return None


def model_diff(old_instance, new_instance):
    """比較模型實例的變化"""
    changes = {}
    old_data = model_to_dict(old_instance)
    new_data = model_to_dict(new_instance)
    
    for key, old_value in old_data.items():
        new_value = new_data.get(key)
        if old_value != new_value:
            changes[key] = {
                'old': old_value,
                'new': new_value
            }
    return changes


# 記錄模型清單
MONITORED_MODELS = [
    'auth.User',
    'contenttypes.ContentType',
    # 添加您想監控的其他模型
]

# 儲存實例的原始數據
_pre_save_data = {}

@receiver(pre_save)
def store_pre_save_data(sender, instance, **kwargs):
    """在保存前儲存實例數據"""
    sender_model = f"{sender._meta.app_label}.{sender._meta.model_name}"
    if sender_model in MONITORED_MODELS and instance.pk:
        try:
            original = sender.objects.get(pk=instance.pk)
            _pre_save_data[instance] = original
        except sender.DoesNotExist:
            pass


@receiver(post_save)
def log_create_or_update(sender, instance, created, **kwargs):
    """記錄創建或更新操作"""
    sender_model = f"{sender._meta.app_label}.{sender._meta.model_name}"
    if sender_model in MONITORED_MODELS:
        action_type = "create" if created else "update"
        user = get_user_from_request()
        ip_address = get_client_ip_from_request()
        request_log = get_request_log_from_request()
        
        # 將實例轉換為dict
        try:
            data_snapshot = model_to_dict(instance)
            # 將不可序列化的對象轉換為字符串
            for key, value in data_snapshot.items():
                if not isinstance(value, (str, int, float, bool, list, dict, type(None))):
                    data_snapshot[key] = str(value)
        except Exception:
            data_snapshot = {"error": "無法序列化對象"}
        
        # 計算變更內容
        changes = None
        if not created and instance in _pre_save_data:
            original = _pre_save_data.pop(instance)
            changes = model_diff(original, instance)
        
        # 記錄操作
        CRUDLog.objects.create(
            user=user,
            app_name=sender._meta.app_label,
            model_name=sender._meta.model_name,
            action_type=action_type,
            data_snapshot=data_snapshot,
            object_id=str(instance.pk),
            ip_address=ip_address,
            changes=changes,
            request_log=request_log
        )


@receiver(post_delete)
def log_delete(sender, instance, **kwargs):
    """記錄刪除操作"""
    sender_model = f"{sender._meta.app_label}.{sender._meta.model_name}"
    if sender_model in MONITORED_MODELS:
        user = get_user_from_request()
        ip_address = get_client_ip_from_request()
        request_log = get_request_log_from_request()
        
        # 將實例轉換為dict
        try:
            data_snapshot = model_to_dict(instance)
            # 將不可序列化的對象轉換為字符串
            for key, value in data_snapshot.items():
                if not isinstance(value, (str, int, float, bool, list, dict, type(None))):
                    data_snapshot[key] = str(value)
        except Exception:
            data_snapshot = {"error": "無法序列化對象"}
        
        # 記錄操作
        CRUDLog.objects.create(
            user=user,
            app_name=sender._meta.app_label,
            model_name=sender._meta.model_name,
            action_type="delete",
            data_snapshot=data_snapshot,
            object_id=str(instance.pk),
            ip_address=ip_address,
            request_log=request_log
        )