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

def send_order_email(user_email, context, subject_template, html_template):
    """
    通用的訂單通知郵件發送函數。

    param:
        user_email: 接收者的電子郵件地址
        context: 用於渲染模板的上下文資料
        subject_template: 主題模板，包含需要格式化的部分
        html_template: HTML內容模板名稱

    return: 
        Boolean 是否寄送成功
    """

    try:
        subject = subject_template.format(**context)
        html_content = render_to_string(html_template, context)
        text_content = strip_tags(html_content)
    except Exception as e:
        logger = logging.getLogger('django')
        logger.error(f"An error occurred-模板問題: {e}")
        return False

    try:
        email = EmailMultiAlternatives(subject, text_content, 'noreply@4timeMei.com', [user_email])
        email.attach_alternative(html_content, "text/html")
        email.send()
        return True
    except Exception as e:
        logger = logging.getLogger('django')
        logger.error(f"An error occurred-寄信問題: {e}")
        return False


class email:
    
    def member_account_created(user_email):
        """帳號已被創造通知"""
        subject_template = f"『 歡迎加入智慧商務系 系友會！ 』帳號已創建"
        context ={
            "current_year":datetime.now().year
        }
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
    


print()

if __name__ == "__main__":
    # 測試使用
    # 範例context的格式
    context = {
        'member_name' : "彬彬",
        'order_number': '123456',
        'order_status': '已處理',
        'order_amount': 'NT$1000',
        'order_time': '2024-07-28 12:34',
        'payment_status': '已付款',
        'order_note': '請盡快處理',
        'store_name': '範例店家',
        'store_phone': '02-12345678',
        'store_address': '台北市範例路123號',
        "takeOrder_number":'123213'
    }
    # 測試腳本
    import django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Mei_four.settings')
    django.setup()
    # 發送郵件
    send_order_email_forCustomer('C110156220@nkust.edu.tw', context)