from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import permissions, status
import os
import pandas as pd
from django.conf import settings
from apps.private.models import Private
from apps.notice.email import email
import string
import random
from threading import Thread
from datetime import datetime
import pytz

class UploadExcelPreviewView(APIView):
    """
    (管理員)上傳Excel進行電子郵件擷取並返回資料預覽
    """
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [permissions.IsAdminUser]

    def post(self, request, *args, **kwargs):
        file_obj = request.FILES.get('file')
        if not file_obj:
            return Response({"error": "使用者未上傳檔案，請先上傳！"}, status=status.HTTP_400_BAD_REQUEST)

        # 儲存檔案
        upload_dir = os.path.join(settings.MEDIA_ROOT, 'member_preview')
        os.makedirs(upload_dir, exist_ok=True)

        taipei_tz = pytz.timezone('Asia/Taipei')
        current_time = datetime.now(taipei_tz).strftime('%Y%m%d_%H%M%S')
        preview_file_name = f"預覽上傳_{current_time}.xlsx"

        file_path = os.path.join(upload_dir, preview_file_name)
        with open(file_path, 'wb+') as destination:
            for chunk in file_obj.chunks():
                destination.write(chunk)

        try:
            # 讀取Excel檔案
            df = pd.read_excel(file_path)
            if 'Email' not in df.columns:
                raise KeyError("發現資料欄位沒有名叫做『Email』，請修改Excel後重新上傳！")

            emails = df['Email'].dropna().tolist()

            # 驗證電子郵件格式
            preview_data = []
            for email in emails:
                if not email or '@' not in email:
                    preview_data.append({"email": email, "status": "無效的格式"})
                elif Private.objects.filter(email=email).exists():
                    preview_data.append({"email": email, "status": "已存在"})
                else:
                    preview_data.append({"email": email, "status": "可新增"})

            return Response({"preview": preview_data}, status=status.HTTP_200_OK)

        except KeyError as e:
            return Response(data={"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": f"Failed to process file: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ConfirmAndCreateAccountsView(APIView):
    """
    (管理員)確認資料後批次創建帳號
    """
    permission_classes = [permissions.IsAdminUser]

    def post(self, request, *args, **kwargs):
        emails = request.data.get("emails", [])
        if not emails:
            return Response({"error": "沒有提供有效的電子郵件清單！"}, status=status.HTTP_400_BAD_REQUEST)

        results = {"created": [], "failed": []}

        def generate_random_password(length=8):
            """生成隨機密碼"""
            characters = string.ascii_letters + string.digits
            return ''.join(random.choice(characters) for _ in range(length))

        for email in emails:
            # 檢查電子郵件有效性
            if not email or '@' not in email:
                results["failed"].append({"email": email, "reason": "無效的電子郵件格式"})
                continue

            # 檢查是否已存在
            if Private.objects.filter(email=email).exists():
                results["failed"].append({"email": email, "reason": "使用者已存在"})
                continue

            # 生成隨機密碼
            password = generate_random_password()

            # 創建帳號
            try:
                user = Private.objects.create_user(email=email, password=password)

                # 發送通知信
                Thread(target=email.member_account_created, args=(email, password)).start()

                # 記錄成功創建的帳號
                results["created"].append({"email": email, "password": password})
            except Exception as e:
                results["failed"].append({"email": email, "reason": str(e)})

        return Response(results, status=status.HTTP_200_OK)
