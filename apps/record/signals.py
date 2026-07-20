# monitoring/signals.py
"""CRUD 操作記錄（CRUDLog）：監控 MONITORED_MODELS 內模型的 create/update/delete。

安全原則：這裡的任何例外都不可以往外傳，否則會讓「記錄操作」這件事
反過來搞壞被監控模型本身的 save()/delete()。所以每個 receiver 最外層
都包 try/except，且實際寫入 CRUDLog 走背景執行緒（同 recordUserMiddleware
的做法），避免拖慢原本的請求處理路徑。
"""
import logging
from concurrent.futures import ThreadPoolExecutor

from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.forms.models import model_to_dict

from apps.record.models import CRUDLog
from apps.record.threadlocals import get_current_request
from utils.get_ip import get_client_ip

logger = logging.getLogger('nkust_ic_alumni')

# 背景寫入 CRUDLog，避免每次業務模型 save()/delete() 都多一次同步 DB 寫入
_crud_log_executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix='crud_log')

# 記錄資料快照時要遮罩的欄位（避免密碼雜湊等敏感值寫入操作記錄）
SENSITIVE_SNAPSHOT_KEYS = {'password', 'new_password', 'old_password', 'confirm_password'}


def get_user_from_request():
    """從當前請求（thread-local）取得操作者"""
    request = get_current_request()
    if request is not None and hasattr(request, 'user') and request.user.is_authenticated:
        return request.user
    return None


def get_client_ip_from_request():
    """從當前請求（thread-local）取得來源 IP（沿用 SEC-012 修補後的信任邏輯）"""
    request = get_current_request()
    if request is not None:
        return get_client_ip(request)
    return None


def _redact_snapshot(data):
    """遮罩資料快照中的敏感欄位"""
    if not isinstance(data, dict):
        return data
    redacted = {}
    for key, value in data.items():
        if isinstance(key, str) and key.lower() in SENSITIVE_SNAPSHOT_KEYS:
            redacted[key] = '***REDACTED***'
        else:
            redacted[key] = value
    return redacted


def _to_json_safe_dict(instance):
    """將模型實例轉為可 JSON 序列化的 dict，並遮罩敏感欄位"""
    try:
        data = model_to_dict(instance)
        for key, value in data.items():
            if not isinstance(value, (str, int, float, bool, list, dict, type(None))):
                data[key] = str(value)
        return _redact_snapshot(data)
    except Exception:
        return {"error": "無法序列化對象"}


def model_diff(old_instance, new_instance):
    """比較模型實例的變化（回傳前已遮罩敏感欄位）"""
    changes = {}
    old_data = _redact_snapshot(model_to_dict(old_instance))
    new_data = _redact_snapshot(model_to_dict(new_instance))

    for key, old_value in old_data.items():
        new_value = new_data.get(key)
        if old_value != new_value:
            changes[key] = {
                'old': old_value,
                'new': new_value,
            }
    return changes


# 記錄模型清單（app_label.model_name，model_name 皆為小寫；app_label 依各 AppConfig 實際設定）
MONITORED_MODELS = [
    'Private.private',              # 帳號主檔（is_staff/is_superuser/password），CRIT 提權事故後重點監控對象
    'member.member',
    'member.position',
    'member.graduate',
    'member.outstandingalumni',
    'member.schooloutstandingalumni',
    'company.company',
    'company.industry',
    'product.product',
    'product.productcate',
    'article.article',
    'notice.notice',
    'recruit.recruit',
    'Info.alumniassociation',
    'Info.constitution',
    'Info.organizationalstructure',
    'Info.membershiprequirement',
    'Info.membershiprequirement_v2',
]

# 儲存實例的原始數據（save 前 -> save 後比對用）
_pre_save_data = {}


def _write_crud_log(kwargs):
    """背景執行緒寫入 CRUDLog"""
    from django.db import close_old_connections
    try:
        CRUDLog.objects.create(**kwargs)
    except Exception:
        logger.exception("寫入 CRUDLog 失敗")
    finally:
        close_old_connections()


@receiver(pre_save)
def store_pre_save_data(sender, instance, **kwargs):
    """在保存前儲存實例數據，供 update 時計算 diff"""
    try:
        sender_model = f"{sender._meta.app_label}.{sender._meta.model_name}"
        if sender_model not in MONITORED_MODELS or not instance.pk:
            return
        try:
            original = sender.objects.get(pk=instance.pk)
            _pre_save_data[instance] = original
        except sender.DoesNotExist:
            pass
    except Exception:
        logger.exception("CRUD 操作記錄：pre_save 處理失敗（不影響原始儲存）")


@receiver(post_save)
def log_create_or_update(sender, instance, created, **kwargs):
    """記錄創建或更新操作"""
    try:
        sender_model = f"{sender._meta.app_label}.{sender._meta.model_name}"
        if sender_model not in MONITORED_MODELS:
            return

        action_type = "create" if created else "update"
        user = get_user_from_request()
        ip_address = get_client_ip_from_request()

        data_snapshot = _to_json_safe_dict(instance)

        changes = None
        if not created and instance in _pre_save_data:
            original = _pre_save_data.pop(instance, None)
            if original is not None:
                changes = model_diff(original, instance)
        else:
            # 避免同一 instance 物件在其他分支殘留於 _pre_save_data，造成記憶體累積
            _pre_save_data.pop(instance, None)

        _crud_log_executor.submit(_write_crud_log, {
            'user': user,
            'app_name': sender._meta.app_label,
            'model_name': sender._meta.model_name,
            'action_type': action_type,
            'data_snapshot': data_snapshot,
            'object_id': str(instance.pk),
            'ip_address': ip_address,
            'changes': changes,
            'request_log': None,
        })
    except Exception:
        logger.exception("CRUD 操作記錄：post_save 處理失敗（不影響原始儲存）")


@receiver(post_delete)
def log_delete(sender, instance, **kwargs):
    """記錄刪除操作"""
    try:
        sender_model = f"{sender._meta.app_label}.{sender._meta.model_name}"
        if sender_model not in MONITORED_MODELS:
            return

        user = get_user_from_request()
        ip_address = get_client_ip_from_request()
        data_snapshot = _to_json_safe_dict(instance)

        _crud_log_executor.submit(_write_crud_log, {
            'user': user,
            'app_name': sender._meta.app_label,
            'model_name': sender._meta.model_name,
            'action_type': 'delete',
            'data_snapshot': data_snapshot,
            'object_id': str(instance.pk),
            'ip_address': ip_address,
            'request_log': None,
        })
    except Exception:
        logger.exception("CRUD 操作記錄：post_delete 處理失敗（不影響原始刪除）")
