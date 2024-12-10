from rest_framework import viewsets, status
from rest_framework.decorators import action,authentication_classes,permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser , AllowAny
from django.shortcuts import get_object_or_404
from apps.Info.models import (
    AlumniAssociationImage,
    ConstitutionImage,
    OrganizationalStructureImage,
    MembershipRequirementImage,
)
from apps.Info.serializer import (
    AlumniAssociationImageSerializer,
    ConstitutionImageSerializer,
    OrganizationalStructureImageSerializer,
    MembershipRequirementImageSerializer,
)

class BaseImageViewSet(viewsets.ViewSet):
    """基礎圖片 ViewSet"""
    model = None
    serializer_class = None

    def get_queryset(self):
        return self.model.objects.all()

    @action(detail=False, methods=["get"], permission_classes=[IsAdminUser])
    def query_all_images(self, request):
        """查詢所有圖片（僅管理員）"""
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], permission_classes=[AllowAny], authentication_classes=[])
    def query_active_images(self, request):
        """查詢啟用圖片（任何人）"""
        queryset = self.get_queryset().filter(is_active=True)
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["post"], permission_classes=[IsAdminUser])
    def create_image(self, request):
        """新增圖片（僅管理員）"""
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["put"], permission_classes=[IsAdminUser])
    def update_image(self, request):
        """更新圖片（僅管理員）"""
        image_id = request.data.get("id")
        if not image_id:
            return Response({"detail": "缺少 id"}, status=status.HTTP_400_BAD_REQUEST)
        instance = get_object_or_404(self.model, id=image_id)
        serializer = self.serializer_class(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["put"], permission_classes=[IsAdminUser])
    def toggle_status(self, request):
        """更新圖片（僅管理員）"""
        image_id = request.data.get("id")
        if not image_id:
            return Response({"detail": "缺少 id"}, status=status.HTTP_400_BAD_REQUEST)
        instance = get_object_or_404(self.model, id=image_id)
        instance.is_active = not instance.is_active
        instance.save()
        return Response(status=200,data="ok")

    @action(detail=False, methods=["delete"], permission_classes=[IsAdminUser])
    def delete_image(self, request):
        """刪除圖片（僅管理員）"""
        image_id = request.data.get("id")
        if not image_id:
            return Response({"detail": "缺少 id"}, status=status.HTTP_400_BAD_REQUEST)
        instance = get_object_or_404(self.model, id=image_id)
        instance.delete()
        return Response({"detail": "圖片已刪除"}, status=status.HTTP_204_NO_CONTENT)


class AlumniAssociationImageViewSet(BaseImageViewSet):
    """系友會圖片 ViewSet"""
    model = AlumniAssociationImage
    serializer_class = AlumniAssociationImageSerializer


class ConstitutionImageViewSet(BaseImageViewSet):
    """章程圖片 ViewSet"""
    model = ConstitutionImage
    serializer_class = ConstitutionImageSerializer


class OrganizationalStructureImageViewSet(BaseImageViewSet):
    """組織架構圖片 ViewSet"""
    model = OrganizationalStructureImage
    serializer_class = OrganizationalStructureImageSerializer


class MembershipRequirementImageViewSet(BaseImageViewSet):
    """會員資格圖片 ViewSet"""
    model = MembershipRequirementImage
    serializer_class = MembershipRequirementImageSerializer
