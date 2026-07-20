# REST ful
from rest_framework.decorators import action ,permission_classes ,authentication_classes
from rest_framework import viewsets, permissions , status
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from rest_framework.response import Response
from django.conf import settings
# check
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
# inner
from apps.private.serializer import PasswordResetRequestSerializer
from apps.member.serializer import MemberSerializer
from apps.member.views import _parse_multipart_json_fields

# time
from django.utils import timezone
import pytz

from apps.notice.email import email
# model
from apps.private.models import PasswordResetCode,Private

import threading ;

# drf_yasg
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class LoginView(APIView):
    """
    使用者使用基本功能
    """
    authentication_classes = []
    permission_classes = [permissions.AllowAny]
    # [資安修補 MED-4] 登入端點嚴格節流，抑制暴力破解
    throttle_scope = 'login'

    @swagger_auto_schema(
        operation_description="使用者登入",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, description='使用者電子郵件'),
                'password': openapi.Schema(type=openapi.TYPE_STRING, description='使用者密碼'),
            },
            required=['email', 'password'],
        ),
        responses={
            200: openapi.Response('登入成功', openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING),
                    'token': openapi.Schema(type=openapi.TYPE_STRING),
                }
            )),
            400: '登入失敗'
        }
    )
    def post(self, request):
        """登入"""
        # [資安修補 MED-3] 防帳號列舉：
        #   - 原本先檢查 is_active 再驗密碼，未驗證者可藉 403/400 差異探測帳號是否存在/停用。
        #   - 改為先驗證密碼；唯有「密碼正確但帳號停用」才回 403（維持前端既有 UX），
        #     其餘（帳號不存在、密碼錯誤）一律回相同的 400，無法區分。
        from django.contrib.auth.hashers import check_password
        userEmail = (request.data.get('email') or '').strip().lower()
        password = request.data.get('password')

        user = authenticate(email=userEmail, password=password)
        if user is not None:
            # authenticate 對停用帳號預設回 None，故此處 user 必為啟用中
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            # [資安修補 SEC-015] token 不再放進 JSON body（避免前端存 localStorage 或任何
            # JS 可讀取的地方），只透過 HttpOnly Set-Cookie 交付——即使頁面被 XSS 也讀不到。
            # 同時用 get_token() 順便讓 Django 在這次回應把 csrftoken cookie 設好，前端才有
            # 值可以讀出來塞進後續寫入請求的 X-CSRFToken header（CookieJWTAuthentication 會檢查）。
            from django.middleware.csrf import get_token
            get_token(request)
            response = Response(
                {'message': "OK", 'is_super': user.is_superuser},
                status=200,
            )
            response.set_cookie(
                settings.JWT_COOKIE_NAME,
                access_token,
                max_age=int(settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'].total_seconds()),
                httponly=True,
                secure=settings.JWT_COOKIE_SECURE,
                samesite=settings.JWT_COOKIE_SAMESITE,
                path='/',
            )
            return response

        # 認證失敗：僅在「密碼正確但帳號停用」時回 403，避免外部列舉
        try:
            u = Private.objects.get(email=userEmail)
            if (not u.is_active) and password and check_password(password, u.password):
                return Response({'msg': "已被停用"}, status=403)
        except Private.DoesNotExist:
            pass
        return Response({'error': 'failed'}, status=400)


class LogoutView(APIView):
    """[資安修補 SEC-015] 清除 HttpOnly JWT cookie——前端 JS 無法直接刪除 HttpOnly cookie，
    必須靠後端這支端點用 Set-Cookie 覆蓋成過期狀態。允許未登入狀態呼叫（冪等，方便前端直接呼叫不用先判斷）。"""
    authentication_classes = []
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        response = Response({'message': 'logged out'}, status=200)
        response.delete_cookie(settings.JWT_COOKIE_NAME, path='/')
        return response


class WhoAmIView(APIView):
    """[資安修補 SEC-015] 取代前端原本用 api/token/verify/ + localStorage 裡的 token 驗證登入狀態的
    方式（cookie 是 HttpOnly，前端已經沒有 token 可以放進 verify 請求的 body 了）。
    前端只要打這支、看是 200 還是 401 就知道目前的 cookie 還有沒有效，不用自己保管 token。"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        # 頁面重新整理後前端會靠這支確認登入狀態，順便補發一次 csrftoken cookie
        # （例如瀏覽器清過 cookie 只剩 access_token，或使用者是從別的分頁帶著 session 過來）。
        from django.middleware.csrf import get_token
        get_token(request)
        return Response({'is_super': request.user.is_superuser}, status=200)
            

class PasswordResetRequestView(APIView):
    """程式碼重置需求"""
    throttle_scope = 'password_reset'
    authentication_classes = []
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_description="請求重置密碼驗證碼",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, description='使用者電子郵件'),
            },
            required=['email'],
        ),
        responses={
            200: '驗證碼已發送',
            400: '資料格式錯誤'
        }
    )
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        if serializer.is_valid():
            userEmail = serializer.validated_data['email']
            # [資安修補 SEC-017] 僅當帳號存在時才產碼寄信；無論存在與否一律回相同 200 與相同訊息，
            # 避免攻擊者依回應差異列舉已註冊帳號。
            try:
                user = Private.objects.get(email=userEmail)
            except Private.DoesNotExist:
                user = None
            if user is not None:
                reset_code = serializer.create_reset_code(user)
                context = {"verification_code": reset_code.code}
                threading.Thread(target=email.forgot_password, args=(userEmail, context,)).start()
            return Response({'message': '若該電子郵件已註冊，驗證碼將寄送至您的信箱'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PasswordResetConfirmView(APIView):
    """密碼確認後重置"""
    authentication_classes = []
    permission_classes = [permissions.AllowAny]
    throttle_scope = 'password_reset'

    @swagger_auto_schema(
        operation_description="確認驗證碼並重置密碼",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'code': openapi.Schema(type=openapi.TYPE_STRING, description='重置密碼的驗證碼'),
                'new_password': openapi.Schema(type=openapi.TYPE_STRING, description='新密碼'),
            },
            required=['code', 'new_password'],
        ),
        responses={
            200: '密碼已重設成功',
            400: '驗證碼無效或已過期'
        }
    )
    def post(self, request):
        # [資安修補 HIGH-1] 重設碼僅 6 位數，原本只用 code 全域查詢、未綁定 email、
        # 無嘗試次數限制，等同對所有未過期重設碼進行暴力猜測即可接管任意帳號。
        # 修補：必須同時提供 email，將驗證碼綁定至該帳號；並對新密碼做強度驗證。
        from django.contrib.auth.password_validation import validate_password
        from django.core.exceptions import ValidationError as DjangoValidationError

        email_input = (request.data.get('email') or '').strip().lower()
        code = request.data.get('code')
        new_password = request.data.get('new_password')

        if not email_input or not code or not new_password:
            return Response({'error': '請提供 email、驗證碼與新密碼'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            reset_code = PasswordResetCode.objects.get(code=code, private__email=email_input)
            if reset_code.is_expired():
                reset_code.delete()
                return Response({'error': '驗證碼已過期'}, status=status.HTTP_400_BAD_REQUEST)
        except PasswordResetCode.DoesNotExist:
            return Response({'error': '無效的驗證碼'}, status=status.HTTP_400_BAD_REQUEST)

        user = reset_code.private
        try:
            validate_password(new_password, user=user)
        except DjangoValidationError as e:
            return Response({'error': list(e.messages)}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()

        # 單次使用：用完即刪除該帳號所有未使用的重設碼
        PasswordResetCode.objects.filter(private=user).delete()
        return Response({'message': '密碼已重設成功'}, status=status.HTTP_200_OK)

class MemberRegisterView(APIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = []
    throttle_scope = 'register'
    # 前端大頭照改用 multipart/form-data 送出，global DEFAULT_PARSER_CLASSES 只有
    # JSONParser，不加這行會直接 415，還沒進到 serializer 就擋掉了整個註冊流程。
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    @swagger_auto_schema(
        operation_description="註冊新的會員",
        request_body=MemberSerializer,
        responses={
            201: '註冊成功',
            400: '資料格式錯誤'
        }
    )
    def post(self, request):
        # [資安修補 SEC-003] 帶 context 讓序列化器判定請求者非 staff（匿名註冊），
        # 自動移除 is_paid / is_show 等管理性欄位，禁止自助設定。
        # multipart 表單無法原生表達巢狀物件，position/graduate/private_input
        # 若以 JSON 字串送出，這裡還原成 dict 再交給 serializer。
        data = _parse_multipart_json_fields(request.data.copy(), ['position', 'graduate', 'private_input'])
        serializer = MemberSerializer(data=data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
