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

        # [資安修補 MED-6] 基本檔案檢查：副檔名與大小
        if not file_obj.name.lower().endswith(('.xlsx', '.xls')):
            return Response({"error": "僅接受 .xlsx 或 .xls 檔案"}, status=status.HTTP_400_BAD_REQUEST)
        if file_obj.size > 5 * 1024 * 1024:
            return Response({"error": "檔案大小不能超過 5MB"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # [資安修補 MED-6] 直接以記憶體解析，不再把含會員 Email 的 Excel 寫入
            # web 可服務的 MEDIA_ROOT（原本檔名可預測、且永久殘留造成個資外洩）。
            df = pd.read_excel(file_obj)
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
            # [資安修補 SEC-022] 不外洩缺漏欄位等內部細節
            return Response(data={"error": "檔案格式不正確或缺少必要欄位"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": "檔案處理失敗，請確認檔案格式"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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

        from django.core.validators import validate_email as dj_validate_email
        from django.core.exceptions import ValidationError as DjValidationError

        for email in emails:
            # [資安修補 SEC-023] 以 Django EmailValidator 嚴格驗證，取代僅檢查 '@'。
            try:
                dj_validate_email(email)
            except (DjValidationError, TypeError):
                results["failed"].append({"email": email, "reason": "無效的電子郵件格式"})
                continue

            # 檢查是否已存在
            if Private.objects.filter(email=email).exists():
                results["failed"].append({"email": email, "reason": "使用者已存在"})
                continue

            # [資安修補 CRIT-3] 不可使用空密碼建立帳號（authenticate(password="") 會成功 → 認證繞過）。
            # 一律產生高強度隨機密碼，使用者須透過「忘記密碼」流程設定自己的密碼。
            password = generate_random_password(12)

            # 創建帳號
            try:
                user = Private.objects.create_user(email=email, password=password)
                from apps.notice.email import email as notice_email
                # 發送通知信
                Thread(target=notice_email.member_account_created, args=(email, password)).start()

                # 記錄成功創建的帳號
                results["created"].append({"email": email})
            except Exception as e:
                results["failed"].append({"email": email, "reason": str(e)})

        return Response(results, status=status.HTTP_200_OK)
