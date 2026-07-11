"""聯絡我們（公開）端點。"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions

from apps.record.serializer import ContactMessageSerializer


class ContactCreateView(APIView):
    """
    公開的「聯絡我們」表單送出端點。
    - 任何人可送出（AllowAny），但以節流限制濫用（settings: 'contact' 範圍）。
    - 僅寫入 ContactMessage，不回傳既有資料，避免資訊外洩。
    """
    authentication_classes = []
    permission_classes = [permissions.AllowAny]
    throttle_scope = 'contact'

    def post(self, request):
        serializer = ContactMessageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "已收到您的訊息，我們會盡快與您聯繫。"},
                            status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
