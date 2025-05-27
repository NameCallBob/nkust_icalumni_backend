from django.db.models.signals import pre_save, pre_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model

User = get_user_model()

# 定義受保護的電子郵件清單
PROTECTED_EMAILS = ["kuasmis@gmail.com", "robin92062574@gmail.com","c110156220@nkust.edu.tw"]

@receiver(pre_save, sender=User)
def prevent_protected_user_modification(sender, instance, **kwargs):
    """
    防止修改特定電子郵件的使用者屬性。
    """
    # 如果是受保護的電子郵件，檢查屬性變更
    if instance.email in PROTECTED_EMAILS:
        # 查找原始資料
        try:
            original = sender.objects.get(pk=instance.pk)
        except sender.DoesNotExist:
            # 如果是新建操作，允許繼續
            return

        # 檢查是否嘗試修改受保護屬性
        if (original.is_staff != instance.is_staff or
            original.is_superuser != instance.is_superuser or
            original.is_active != instance.is_active):
            raise PermissionError("此使用者以受保護，無法作任何更改，如有問題請聯絡管理員！")

@receiver(pre_delete, sender=User)
def prevent_protected_user_deletion(sender, instance, **kwargs):
    """
    防止刪除特定電子郵件的使用者。
    """
    # 禁止刪除受保護的電子郵件
    if instance.email in PROTECTED_EMAILS:
        raise PermissionError("此使用者以受保護，無法刪除")
