from rest_framework import status, viewsets, permissions
from rest_framework.response import Response
from rest_framework.decorators import action ,authentication_classes,permission_classes
from rest_framework_simplejwt.authentication import JWTAuthentication
from apps.picture.models import SelfImage, CompanyImage, ProductImage , PopupAd
from apps.picture.serializer import SelfImageSerializer, CompanyImageSerializer, ProductImageSerializer , PopupAdSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class SelfImageViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    @swagger_auto_schema(
        operation_description="取得所有 SelfImage 資料",
        responses={200: SelfImageSerializer(many=True), 401: "未授權的用戶"}
    )
    @action(detail=False, methods=['get'], url_path='all',permission_classes=[permissions.IsAdminUser],authentication_classes=[JWTAuthentication])
    def all(self, request):
        queryset = SelfImage.objects.all()
        serializer = SelfImageSerializer(queryset, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="取得當前使用者的 SelfImage 資料",
        responses={200: SelfImageSerializer(many=True), 401: "未授權的用戶"}
    )
    @action(detail=False, methods=['get'],permission_classes=[permissions.IsAuthenticated],authentication_classes=[JWTAuthentication])
    def selfInfo(self, request):
        queryset = SelfImage.objects.filter(member=request.user.member.id)
        serializer = SelfImageSerializer(queryset, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="創建 SelfImage",
        request_body=SelfImageSerializer,
        responses={201: openapi.Response('成功創建', SelfImageSerializer), 400: '格式錯誤', 401: '未授權'}
    )
    @action(detail=False, methods=['post'], url_path='new', permission_classes=[permissions.IsAuthenticated], authentication_classes=[JWTAuthentication])
    def new(self, request):
        data = request.data.copy()
        data['member'] = request.user.member.id  # 自動抓取 member 的 ID

        serializer = SelfImageSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="更新 SelfImage",
        request_body=SelfImageSerializer,
        responses={200: '成功更新', 400: '格式錯誤', 404: '找不到', 401: '未授權'}
    )
    @action(detail=False, methods=['put'], url_path='change',permission_classes=[permissions.IsAuthenticated],authentication_classes=[JWTAuthentication])
    def change(self, request):
        try:
            image = SelfImage.objects.get(id=request.data.get("id"))
        except SelfImage.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = SelfImageSerializer(image, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="刪除 SelfImage",
        responses={204: '成功刪除', 404: '找不到', 401: '未授權'}
    )
    @action(detail=False, methods=['delete'], url_path='delete',permission_classes=[permissions.IsAuthenticated],authentication_classes=[JWTAuthentication])
    def delete(self, request):
        try:
            image = SelfImage.objects.get(id=request.data.get("id"))
        except SelfImage.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        image.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @swagger_auto_schema(
        operation_description="切換 SelfImage 的 active 狀態",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='Image ID')
            },
            required=['id']
        ),
        responses={200: "切換成功", 404: "找不到", 401: "未授權"}
    )
    @action(detail=False, methods=['post'], url_path='switch_active', permission_classes=[permissions.IsAuthenticated], authentication_classes=[JWTAuthentication])
    def switch_active(self, request):
        image_id = request.data.get("id")
        try:
            image = SelfImage.objects.get(id=image_id)
            image.active = not image.active
            image.save()
            return Response({"status": "active status toggled", "active": image.active}, status=status.HTTP_200_OK)
        except SelfImage.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

class CompanyImageViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    @swagger_auto_schema(
        operation_description="取得所有 CompanyImage 資料",
        responses={200: CompanyImageSerializer(many=True), 401: "未授權"}
    )
    @action(detail=False, methods=['get'], url_path='all',permission_classes=[permissions.IsAdminUser],authentication_classes=[JWTAuthentication])
    def all(self, request):
        queryset = CompanyImage.objects.all()
        serializer = CompanyImageSerializer(queryset, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="取得當前公司成員的 CompanyImage 資料",
        responses={200: CompanyImageSerializer(many=True), 401: "未授權"}
    )
    @action(detail=False, methods=['get'],permission_classes=[permissions.IsAuthenticated],authentication_classes=[JWTAuthentication])
    def selfInfo(self, request):
        from apps.company.models import Company
        queryset = CompanyImage.objects.filter(company=Company.objects.get(member=request.user.member))
        serializer = CompanyImageSerializer(queryset, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="創建 CompanyImage",
        request_body=CompanyImageSerializer,
        responses={201: openapi.Response('成功創建', CompanyImageSerializer), 400: '格式錯誤', 401: '未授權'}
    )
    @action(detail=False, methods=['post'], url_path='new', permission_classes=[permissions.IsAuthenticated], authentication_classes=[JWTAuthentication])
    def new(self, request):
        from apps.company.models import Company
        data = request.data.copy()
        data['company'] = Company.objects.get(member=request.user.member).id  # 自動抓取 company 的 ID
        serializer = CompanyImageSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="更新 CompanyImage",
        request_body=CompanyImageSerializer,
        responses={200: '成功更新', 400: '格式錯誤', 404: '找不到', 401: '未授權'}
    )
    @action(detail=False, methods=['put'], url_path='change',permission_classes=[permissions.IsAuthenticated],authentication_classes=[JWTAuthentication])
    def change(self, request):
        try:
            image = CompanyImage.objects.get(id=request.data.get("id"))
        except CompanyImage.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = CompanyImageSerializer(image, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="刪除 CompanyImage",
        responses={204: '成功刪除', 404: '找不到', 401: '未授權'}
    )
    @action(detail=False, methods=['delete'], url_path='delete',permission_classes=[permissions.IsAuthenticated],authentication_classes=[JWTAuthentication])
    def delete(self, request):
        try:
            image = CompanyImage.objects.get(id=request.data.get("id"))
        except CompanyImage.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        image.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @swagger_auto_schema(
        operation_description="切換 CompanyImage 的 active 狀態",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='Image ID')
            },
            required=['id']
        ),
        responses={200: "切換成功", 404: "找不到", 401: "未授權"}
    )
    @action(detail=False, methods=['post'], url_path='switch_active', permission_classes=[permissions.IsAuthenticated], authentication_classes=[JWTAuthentication])
    def switch_active(self, request):
        image_id = request.data.get("id")
        try:
            image = CompanyImage.objects.get(id=image_id)
            image.active = not image.active
            image.save()
            return Response({"status": "active status toggled", "active": image.active}, status=status.HTTP_200_OK)
        except CompanyImage.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

class ProductImageViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    @swagger_auto_schema(
        operation_description="取得所有 ProductImage 資料",
        responses={200: ProductImageSerializer(many=True), 401: "未授權"}
    )
    @action(detail=False, methods=['get'], url_path='all',permission_classes=[permissions.IsAuthenticated],authentication_classes=[JWTAuthentication])
    def all(self, request):
        queryset = ProductImage.objects.all()
        serializer = ProductImageSerializer(queryset, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="取得當前公司成員的 ProdcutImage 資料",
        responses={200: CompanyImageSerializer(many=True), 401: "未授權"}
    )
    @action(detail=False, methods=['get'],permission_classes=[permissions.IsAuthenticated],authentication_classes=[JWTAuthentication])
    def selfInfo(self, request):
        from apps.company.models import Company
        queryset = ProductImage.objects.filter(company=Company.objects.get(member=request.user.member))
        serializer = ProductImageSerializer(queryset, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="創建 ProductImage",
        request_body=ProductImageSerializer,
        responses={201: openapi.Response('成功創建', ProductImageSerializer), 400: '格式錯誤', 401: '未授權'}
    )
    @action(detail=False, methods=['post'], url_path='new', permission_classes=[permissions.IsAuthenticated], authentication_classes=[JWTAuthentication])
    def new(self, request):
        data = request.data.copy()
        data['product'] = request.data.get('product_id')  # 假設前端傳遞的產品 ID 使用 `product_id`
        print(data['product'])
        serializer = ProductImageSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="更新 ProductImage",
        request_body=ProductImageSerializer,
        responses={200: '成功更新', 400: '格式錯誤', 404: '找不到', 401: '未授權'}
    )
    @action(detail=False, methods=['put'], url_path='change',permission_classes=[permissions.IsAuthenticated],authentication_classes=[JWTAuthentication])
    def change(self, request):
        try:
            image = ProductImage.objects.get(id=request.data.get("id"))
        except ProductImage.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = ProductImageSerializer(image, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="刪除 ProductImage",
        responses={204: '成功刪除', 404: '找不到', 401: '未授權'}
    )
    @action(detail=False, methods=['delete'], url_path='delete',permission_classes=[permissions.IsAuthenticated],authentication_classes=[JWTAuthentication])
    def delete(self, request):
        try:
            image = ProductImage.objects.get(id=request.data.get("id"))
        except ProductImage.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        image.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @swagger_auto_schema(
        operation_description="切換 ProductImage 的 active 狀態",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='Image ID')
            },
            required=['id']
        ),
        responses={200: "切換成功", 404: "找不到", 401: "未授權"}
    )
    @action(detail=False, methods=['post'], url_path='switch_active', permission_classes=[permissions.IsAuthenticated], authentication_classes=[JWTAuthentication])
    def switch_active(self, request):
        image_id = request.data.get("id")
        try:
            image = ProductImage.objects.get(id=image_id)
            image.active = not image.active
            image.save()
            return Response({"status": "active status toggled", "active": image.active}, status=status.HTTP_200_OK)
        except ProductImage.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

class PopupAdViewSet(viewsets.ModelViewSet):
    queryset = PopupAd.objects.all()
    serializer_class = PopupAdSerializer

    # 支援過濾 `active` 狀態的廣告
    def get_queryset(self):
        queryset = super().get_queryset()
        active = self.request.query_params.get('active')  # 從查詢參數中獲取 `active`
        if active is not None:
            queryset = queryset.filter(active=active.lower() == 'true')
        return queryset

    # 自訂操作來啟用/停用廣告
    @action(detail=True, methods=['patch'])
    def toggle_active(self, request, pk=None):
        popup_ad = self.get_object()
        popup_ad.active = not popup_ad.active
        popup_ad.save()
        serializer = self.get_serializer(popup_ad)
        return Response(serializer.data)