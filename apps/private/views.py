# REST ful
from rest_framework.decorators import action ,permission_classes ,authentication_classes
from rest_framework import viewsets, permissions , status
from rest_framework.views import APIView

from rest_framework.response import Response
# check
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
# inner
from apps.private.serializer import PasswordResetRequestSerializer
from apps.member.serializer import MemberSerializer

from django.utils import timezone
from apps.notice.email import email
# model
from apps.private.models import PasswordResetCode,Private

import threading ; 

class LoginView(APIView):
    """
    使用者使用基本功能
    """
    authentication_classes=[]
    permission_classes=[permissions.AllowAny]

    def post(self,request):
        """登入"""
        userEmail = request.data.get('email')
        password = request.data.get('password')
        user = authenticate(email=userEmail, password=password)
        if user:
            refresh = RefreshToken.for_user(user)
            # 獲取登入時間
            login_time = timezone.now().strftime('%Y-%m-%d %H:%M:%S')

            # 獲取IP位址
            ip_address = request.META.get('REMOTE_ADDR')

            # 獲取裝置資訊
            device_info = request.META.get('HTTP_USER_AGENT', 'Unknown Device')
            context = {
                'login_time': login_time,
                'ip_address': ip_address,
                'device_info': device_info,
            }
            
            threading.Thread(target=email.login,
                             args=(userEmail,context,)
                             ).start()
            
            return Response({'message': "OK", 'token': str(refresh.access_token)}, status=200)
        else:
            return Response({'error': 'failed'}, status=400)

class PasswordResetRequestView(APIView):
    """程式碼重置需求"""
    authentication_classes=[]
    permission_classes=[permissions.AllowAny]

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        if serializer.is_valid():
            userEmail = serializer.validated_data['email']
            user = Private.objects.get(email=userEmail)
            reset_code = serializer.create_reset_code(user)

            context = {"verification_code":reset_code.code}

            threading.Thread(target=email.forgot_password,
                             args=(userEmail,context,)).start()
            
            return Response({'message': '驗證碼已發送至您的電子郵件'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PasswordResetConfirmView(APIView):
    """密碼確認後重置"""
    authentication_classes=[]
    permission_classes=[permissions.AllowAny]

    def post(self, request):
        code = request.data.get('code')
        new_password = request.data.get('new_password')

        try:
            reset_code = PasswordResetCode.objects.get(code=code)
            if reset_code.is_expired():
                return Response({'error': '驗證碼已過期'}, status=status.HTTP_400_BAD_REQUEST)
        except PasswordResetCode.DoesNotExist:
            return Response({'error': '無效的驗證碼'}, status=status.HTTP_400_BAD_REQUEST)

        user = reset_code.private
        user.set_password(new_password)
        user.save()

        # 刪除使用過的驗證碼
        reset_code.delete()

        return Response({'message': '密碼已重設成功'}, status=status.HTTP_200_OK)
    

class MemberRegisterView(APIView):
    permission_classes=[permissions.AllowAny]
    authentication_classes=[]
    serializer = MemberSerializer

    def post(self,request):
        serializer = MemberSerializer(
            data=request.data
            )
        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data, 
                status=status.HTTP_201_CREATED
                )
        return Response(
                serializer.errors, 
                status=status.HTTP_400_BAD_REQUEST
                )
