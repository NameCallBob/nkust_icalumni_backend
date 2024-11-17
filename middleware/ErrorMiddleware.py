import traceback
from django.core.mail import mail_admins
from django.utils.deprecation import MiddlewareMixin

class ExceptionEmailMiddleware(MiddlewareMixin):
    def process_exception(self, request, exception):
        # 組裝錯誤訊息
        subject = f"『伺服器錯誤』智慧商務系友會網站＿{request.path}"
        message = (
            f"HTTP方法: {request.method}\n"
            f"網址或路徑: {request.build_absolute_uri()}\n\n"
            f"錯誤訊息:\n\n{traceback.format_exc()}"
        )

        # 寄送給管理員
        mail_admins(subject, message)
