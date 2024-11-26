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

class UploadExcelView(APIView):
    """
    (管理員)上傳Excel進行電子郵件擷取並添加簡單帳號
    """
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [permissions.IsAdminUser]

    def post(self, request, *args, **kwargs):
        file_obj = request.FILES.get('file')
        if not file_obj:
            return Response({"error": "使用者未上傳檔案，請先上傳！"}, status=status.HTTP_400_BAD_REQUEST)

        # 檔案上傳處理
        upload_dir = os.path.join(settings.MEDIA_ROOT, 'member_history')
        os.makedirs(upload_dir, exist_ok=True)

        # 生成台北時間的檔案名稱
        taipei_tz = pytz.timezone('Asia/Taipei')
        current_time = datetime.now(taipei_tz).strftime('%Y%m%d_%H%M%S')
        new_file_name = f"客戶新增上傳_{current_time}.xlsx"

        file_path = os.path.join(upload_dir, new_file_name)
        with open(file_path, 'wb+') as destination:
            for chunk in file_obj.chunks():
                destination.write(chunk)

        try:
            # 讀取Excel檔案並擷取電子郵件
            df = pd.read_excel(file_path)
            if 'Email' not in df.columns:
                raise KeyError("發現資料欄位沒有名叫做『Email』，請修改Excel後重新上傳！")

            emails = df['Email'].dropna().tolist()
            results = self._create_accounts(emails)

            return Response(data=results, status=status.HTTP_200_OK)

        except KeyError as e:
            return Response(data={"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": f"Failed to process file: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _create_accounts(self, emails):
        """
        批次處理電子郵件清單，為每個電子郵件新增帳號並發送通知信
        """
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

        return results
