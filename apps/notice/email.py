"""
在使用本服務之前，請先確認是否在settings.py設定有關於SMTP服務的設定
e.g. settings.py如下（請記得用環境變數儲存敏感資訊：Ｄ)

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your_gmail_address@gmail.com'
EMAIL_HOST_PASSWORD = 'your_gmail_password'
DEFAULT_FROM_EMAIL = 'your_gmail_address@gmail.com'

若無，此服務會出現錯誤．
"""
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import logging
from datetime import datetime

import requests
import os

def send_email_resend(subject, html_content, to_email, text_content=None):
    try:
        response = requests.post(
            "https://api.resend.com/emails",
            headers={
                "Authorization": f"Bearer {os.getenv('RESEND_API_KEY')}",
                "Content-Type": "application/json"
            },
            json={
                # [資安修補 SEC-025] 寄件人網域改由環境變數設定（預設沿用既有值）。
                "from": os.getenv("RESEND_FROM_EMAIL", "noreply@binbinbob.work"),
                "to": [to_email],
                "subject": subject,
                "html": html_content,
                "text": text_content or ""
            }
        )
        if response.status_code == 200:
            return True
        else:
            logging.getLogger('django').error(f"Resend 發信失敗: {response.status_code}, {response.text}")
            return False
    except Exception as e:
        logging.getLogger('django').error(f"Resend API 錯誤: {e}")
        return False


def send_order_email(user_email, context, subject_template, html_template):
    logger = logging.getLogger('django')
    try:
        subject = subject_template.format(**context)
        html_content = render_to_string(html_template, context)
        text_content = strip_tags(html_content)
    except Exception as e:
        logger.error(f"模板處理錯誤: {e}")
        return False

    # Step 1: 優先使用 Resend API
    if send_email_resend(subject, html_content, user_email, text_content):
        return True

    # Step 2: 若 Resend 發信失敗，嘗試使用 Django SMTP 發信
    try:
        # [資安修補 SEC-025] 修正他專案殘留的寄件人網域（4timeMei.com），改用本專案設定。
        from django.conf import settings as _settings
        smtp_from = getattr(_settings, 'DEFAULT_FROM_EMAIL', None) or os.getenv('EMAIL_HOST_USER')
        email = EmailMultiAlternatives(subject, text_content, smtp_from, [user_email])
        email.attach_alternative(html_content, "text/html")
        email.send()
        return True
    except Exception as e:
        logger.error(f"SMTP 備援寄信錯誤: {e}")
        return False


class email:

    def member_account_created(user_email, password=None):
        """帳號已被創造通知。

        [資安修補 MED-5] 不再於郵件中寄送明文密碼。保留 password 參數僅為相容既有呼叫，
        實際不放入信件內容；使用者改以「忘記密碼」流程自行設定密碼。
        """
        subject_template = f"『 歡迎加入智慧商務系 系友會！ 』帳號已創建"
        context = {}
        context['current_year'] = datetime.now().year
        html_template = "welcome.html"
        return send_order_email(user_email, context, subject_template, html_template)

    def forgot_password(user_email, context):
        """忘記密碼寄送驗證碼"""
        subject_template = f"『 智慧商務系系友會 』忘記密碼驗證碼"

        context['current_year'] = datetime.now().year

        html_template = "forgotPasswordCode.html"
        return send_order_email(user_email, context, subject_template, html_template)

    def login(user_email, context):
        """登入"""
        subject_template = f"『 智慧商務系系友會 』帳號已登入"
        context['current_year'] = datetime.now().year

        html_template = "loginNotice.html"
        return send_order_email(user_email, context, subject_template, html_template)

# if __name__ == "__main__":
#     # 測試使用
#     # 範例context的格式
#     context = {
#         'member_name' : "彬彬",
#         'order_number': '123456',
#         'order_status': '已處理',
#         'order_amount': 'NT$1000',
#         'order_time': '2024-07-28 12:34',
#         'payment_status': '已付款',
#         'order_note': '請盡快處理',
#         'store_name': '範例店家',
#         'store_phone': '02-12345678',
#         'store_address': '台北市範例路123號',
#         "takeOrder_number":'123213'
#     }
#     # 測試腳本
#     import django
#     os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Mei_four.settings')
#     django.setup()
#     # 發送郵件
#     send_order_email_forCustomer('C110156220@nkust.edu.tw', context)