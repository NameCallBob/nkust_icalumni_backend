from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
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


# 系友會圖片 ViewSet
class AlumniAssociationImageViewSet(viewsets.ViewSet):
    """系友會圖片 ViewSet"""

    def query_images(self, request):
        """查詢所有圖片或啟用圖片"""
        queryset = AlumniAssociationImage.objects.all()
        filters = request.query_params
        if "is_active" in filters and filters["is_active"].lower() == "true":
            queryset = queryset.filter(is_active=True)
        serializer = AlumniAssociationImageSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["post"], permission_classes=[IsAdminUser])
    def create_image(self, request):
        """新增系友會圖片（限管理員）"""
        serializer = AlumniAssociationImageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["put"], permission_classes=[IsAdminUser])
    def update_image(self, request):
        """更新系友會圖片（限管理員）"""
        image_id = request.data.get("id")
        if not image_id:
            return Response({"detail": "缺少 id"}, status=status.HTTP_400_BAD_REQUEST)
        instance = get_object_or_404(AlumniAssociationImage, id=image_id)
        serializer = AlumniAssociationImageSerializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["delete"], permission_classes=[IsAdminUser])
    def delete_image(self, request):
        """刪除系友會圖片（限管理員）"""
        image_id = request.data.get("id")
        if not image_id:
            return Response({"detail": "缺少 id"}, status=status.HTTP_400_BAD_REQUEST)
        instance = get_object_or_404(AlumniAssociationImage, id=image_id)
        instance.delete()
        return Response({"detail": "圖片已刪除"}, status=status.HTTP_204_NO_CONTENT)

# 系友會圖片 ViewSet
class ConstitutionImageViewSet(viewsets.ViewSet):
    """系友會圖片 ViewSet"""

    def query_images(self, request):
        """查詢所有圖片或啟用圖片"""
        queryset = ConstitutionImage.objects.all()
        filters = request.query_params
        if "is_active" in filters and filters["is_active"].lower() == "true":
            queryset = queryset.filter(is_active=True)
        serializer = ConstitutionImageSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["post"], permission_classes=[IsAdminUser])
    def create_image(self, request):
        """新增系友會圖片（限管理員）"""
        serializer = ConstitutionImageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["put"], permission_classes=[IsAdminUser])
    def update_image(self, request):
        """更新系友會圖片（限管理員）"""
        image_id = request.data.get("id")
        if not image_id:
            return Response({"detail": "缺少 id"}, status=status.HTTP_400_BAD_REQUEST)
        instance = get_object_or_404(ConstitutionImage, id=image_id)
        serializer = ConstitutionImageSerializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["delete"], permission_classes=[IsAdminUser])
    def delete_image(self, request):
        """刪除系友會圖片（限管理員）"""
        image_id = request.data.get("id")
        if not image_id:
            return Response({"detail": "缺少 id"}, status=status.HTTP_400_BAD_REQUEST)
        instance = get_object_or_404(ConstitutionImage, id=image_id)
        instance.delete()
        return Response({"detail": "圖片已刪除"}, status=status.HTTP_204_NO_CONTENT)


# 系友會圖片 ViewSet
class OrganizationalStructureImageViewSet(viewsets.ViewSet):
    """系友會圖片 ViewSet"""

    def query_images(self, request):
        """查詢所有圖片或啟用圖片"""
        queryset = OrganizationalStructureImage.objects.all()
        filters = request.query_params
        if "is_active" in filters and filters["is_active"].lower() == "true":
            queryset = queryset.filter(is_active=True)
        serializer = OrganizationalStructureImageSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["post"], permission_classes=[IsAdminUser])
    def create_image(self, request):
        """新增系友會圖片（限管理員）"""
        serializer = OrganizationalStructureImageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["put"], permission_classes=[IsAdminUser])
    def update_image(self, request):
        """更新系友會圖片（限管理員）"""
        image_id = request.data.get("id")
        if not image_id:
            return Response({"detail": "缺少 id"}, status=status.HTTP_400_BAD_REQUEST)
        instance = get_object_or_404(OrganizationalStructureImage, id=image_id)
        serializer = OrganizationalStructureImageSerializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["delete"], permission_classes=[IsAdminUser])
    def delete_image(self, request):
        """刪除系友會圖片（限管理員）"""
        image_id = request.data.get("id")
        if not image_id:
            return Response({"detail": "缺少 id"}, status=status.HTTP_400_BAD_REQUEST)
        instance = get_object_or_404(OrganizationalStructureImage, id=image_id)
        instance.delete()
        return Response({"detail": "圖片已刪除"}, status=status.HTTP_204_NO_CONTENT)


# 系友會圖片 ViewSet
class MembershipRequirementImageViewSet(viewsets.ViewSet):
    """系友會圖片 ViewSet"""

    def query_images(self, request):
        """查詢所有圖片或啟用圖片"""
        queryset = MembershipRequirementImage.objects.all()
        filters = request.query_params
        if "is_active" in filters and filters["is_active"].lower() == "true":
            queryset = queryset.filter(is_active=True)
        serializer = MembershipRequirementImageSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["post"], permission_classes=[IsAdminUser])
    def create_image(self, request):
        """新增系友會圖片（限管理員）"""
        serializer = MembershipRequirementImageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["put"], permission_classes=[IsAdminUser])
    def update_image(self, request):
        """更新系友會圖片（限管理員）"""
        image_id = request.data.get("id")
        if not image_id:
            return Response({"detail": "缺少 id"}, status=status.HTTP_400_BAD_REQUEST)
        instance = get_object_or_404(MembershipRequirementImage, id=image_id)
        serializer = MembershipRequirementImageSerializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["delete"], permission_classes=[IsAdminUser])
    def delete_image(self, request):
        """刪除系友會圖片（限管理員）"""
        image_id = request.data.get("id")
        if not image_id:
            return Response({"detail": "缺少 id"}, status=status.HTTP_400_BAD_REQUEST)
        instance = get_object_or_404(MembershipRequirementImage, id=image_id)
        instance.delete()
        return Response({"detail": "圖片已刪除"}, status=status.HTTP_204_NO_CONTENT)
